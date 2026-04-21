"""
AI Content Generator
- Sinh mô tả sản phẩm (SEO + legal safe + chống bịa)
- Sinh bài blog SEO
- Sinh SEO meta (title + description + keywords)
- Post-check: chặn claim y tế/chứng nhận bịa
"""

import re
import json
import logging
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.ai.vertex_client import vertex_ai_client, VertexAIClientError
from app.services.ai.cache import generate_cache_key, get_cached_response, set_cached_response
from app.services.ai.cost_tracker import log_ai_cost, should_use_premium_model, is_budget_exceeded
from app.services.ai.prompts import (
    DESCRIPTION_SYSTEM_PROMPT,
    DESCRIPTION_USER_TEMPLATE,
    BLOG_SYSTEM_PROMPT,
    BLOG_USER_TEMPLATE,
    SEO_META_SYSTEM_PROMPT,
    SEO_META_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


def _is_vertex_permission_denied(error: Exception) -> bool:
    message = str(error)
    return (
        "PermissionDenied" in message
        or "permission denied" in message.lower()
        or getattr(error, "status_code", None) == 403
    )


# ==============================================================================
# POST-CHECK: Chặn claim bịa sau khi AI generate
# ==============================================================================

BANNED_CLAIM_PATTERNS = [
    re.compile(r'chữa\s*(?:bệnh|ung\s*thư|tiểu\s*đường|cao\s*huyết\s*áp|viêm)', re.IGNORECASE),
    re.compile(r'trị\s*(?:bệnh|dứt\s*điểm|hoàn\s*toàn|tận\s*gốc)', re.IGNORECASE),
    re.compile(r'phòng\s*(?:ngừa|chống)\s*(?:ung\s*thư|bệnh)', re.IGNORECASE),
    re.compile(r'cam\s*kết\s*(?:khỏi|hết\s*bệnh|100%|hiệu\s*quả)', re.IGNORECASE),
    re.compile(r'đảm\s*bảo\s*(?:100%|tuyệt\s*đối|an\s*toàn\s*hoàn\s*toàn)', re.IGNORECASE),
    re.compile(r'FDA\s*(?:approved|chứng\s*nhận)', re.IGNORECASE),
    re.compile(r'(?:thuốc|dược)\s+(?:chữa|trị|điều\s*trị)', re.IGNORECASE),
]


def post_check_content(text: str) -> str:
    """
    Lọc claim y tế/chứng nhận bịa ra khỏi nội dung AI-generated.
    Thay thế bằng cụm từ an toàn.
    """
    for pattern in BANNED_CLAIM_PATTERNS:
        text = pattern.sub("[thông tin cần xác minh]", text)
    return text


# ==============================================================================
# CONTENT GENERATOR
# ==============================================================================

class ContentGenerator:
    """Sinh nội dung AI: mô tả sản phẩm, blog SEO, SEO meta."""

    @classmethod
    async def generate_product_description(
        cls,
        db: Session,
        name: str,
        category: str = "",
        region: str = "",
        ingredients: str = "",
        process: str = "",
        certificates: str = "",
        highlights: str = "",
        use_sonnet: bool = False,
    ) -> dict:
        """
        Sinh mô tả sản phẩm.
        Returns dict: {description, model_used, cached, tokens, cost, latency_ms}
        """

        # 1. Validate input
        if not name or len(name.strip()) < 2:
            raise ValueError("Tên sản phẩm không hợp lệ (cần ít nhất 2 ký tự)")

        # 2. Build input
        user_prompt = DESCRIPTION_USER_TEMPLATE.format(
            name=name[:200],
            category=category[:100] or "Không rõ",
            region=region[:100] or "Không rõ",
            ingredients=ingredients[:500] or "Không có thông tin",
            process=process[:500] or "Không có thông tin",
            certificates=certificates[:300] or "Không có",
            highlights=highlights[:300] or "Không có",
        )

        # 3. Check cache
        cache_key = generate_cache_key("description", user_prompt)
        cached = get_cached_response(db, cache_key)
        if cached:
            return {
                "description": cached,
                "model_used": "cache",
                "cached": True,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
                "latency_ms": 0,
            }

        # 4. Choose model
        if use_sonnet and should_use_premium_model(db):
            model_id = settings.VERTEX_CREATIVE_MODEL_ID
        else:
            model_id = settings.VERTEX_MODERATION_MODEL_ID  # Flash cho default

        # 5. Check budget
        if is_budget_exceeded(db):
            model_id = settings.VERTEX_MODERATION_MODEL_ID

        # 6. Generate
        start_time = time.monotonic()
        try:
            response = await vertex_ai_client.invoke_gemini(
                prompt=user_prompt,
                system_prompt=DESCRIPTION_SYSTEM_PROMPT,
                model_id=model_id,
                max_tokens=800,
                temperature=0.4,
                timeout=settings.AI_DESCRIPTION_TIMEOUT,
            )
        except VertexAIClientError as e:
            fallback_model = settings.VERTEX_MODERATION_MODEL_ID
            if model_id != fallback_model and _is_vertex_permission_denied(e):
                logger.warning(
                    "Description generation denied for model=%s; fallback to model=%s",
                    model_id,
                    fallback_model,
                )
                response = await vertex_ai_client.invoke_gemini(
                    prompt=user_prompt,
                    system_prompt=DESCRIPTION_SYSTEM_PROMPT,
                    model_id=fallback_model,
                    max_tokens=800,
                    temperature=0.4,
                    timeout=settings.AI_DESCRIPTION_TIMEOUT,
                )
            else:
                logger.error("Description generation failed: %s", e)
                raise

        latency_ms = int((time.monotonic() - start_time) * 1000)

        # 7. Post-check
        description = post_check_content(response["content"])

        # 8. Cache
        set_cached_response(
            db, cache_key, "description", response["model_id"],
            user_prompt[:2000], description,
        )

        # 9. Log cost
        log_ai_cost(
            db, response["model_id"], "description",
            response["input_tokens"], response["output_tokens"],
            response["estimated_cost_usd"],
        )

        return {
            "description": description,
            "model_used": response["model_id"],
            "cached": False,
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": latency_ms,
        }

    @classmethod
    async def generate_blog(
        cls,
        db: Session,
        topic: str,
        main_keyword: str = "",
        secondary_keywords: str = "",
        word_count: int = 800,
        related_products: str = "",
        notes: str = "",
        use_sonnet: bool = False,
    ) -> dict:
        """
        Sinh bài blog SEO.
        Returns dict: {content, model_used, cached, tokens, cost, latency_ms}
        """

        if not topic or len(topic.strip()) < 5:
            raise ValueError("Chủ đề blog cần ít nhất 5 ký tự")

        user_prompt = BLOG_USER_TEMPLATE.format(
            topic=topic[:300],
            main_keyword=main_keyword[:100] or topic[:50],
            secondary_keywords=secondary_keywords[:300] or "",
            word_count=min(max(word_count, 300), 3000),
            related_products=related_products[:500] or "Không có",
            notes=notes[:300] or "Không có",
        )

        # Check cache
        cache_key = generate_cache_key("blog", user_prompt)
        cached = get_cached_response(db, cache_key)
        if cached:
            return {
                "content": cached,
                "model_used": "cache",
                "cached": True,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
                "latency_ms": 0,
            }

        # Choose model - premium model can be enabled for better quality
        if use_sonnet and should_use_premium_model(db):
            model_id = settings.VERTEX_CREATIVE_MODEL_ID
        else:
            model_id = settings.VERTEX_MODERATION_MODEL_ID

        if is_budget_exceeded(db):
            model_id = settings.VERTEX_MODERATION_MODEL_ID

        # Generate
        start_time = time.monotonic()
        try:
            response = await vertex_ai_client.invoke_gemini(
                prompt=user_prompt,
                system_prompt=BLOG_SYSTEM_PROMPT,
                model_id=model_id,
                max_tokens=2000,
                temperature=0.6,
                timeout=settings.AI_BLOG_TIMEOUT,
            )
        except VertexAIClientError as e:
            fallback_model = settings.VERTEX_MODERATION_MODEL_ID
            if model_id != fallback_model and _is_vertex_permission_denied(e):
                logger.warning(
                    "Blog generation denied for model=%s; fallback to model=%s",
                    model_id,
                    fallback_model,
                )
                response = await vertex_ai_client.invoke_gemini(
                    prompt=user_prompt,
                    system_prompt=BLOG_SYSTEM_PROMPT,
                    model_id=fallback_model,
                    max_tokens=2000,
                    temperature=0.6,
                    timeout=settings.AI_BLOG_TIMEOUT,
                )
            else:
                logger.error("Blog generation failed: %s", e)
                raise

        latency_ms = int((time.monotonic() - start_time) * 1000)

        # Post-check
        content = post_check_content(response["content"])

        # Cache (blog cache lâu hơn)
        set_cached_response(
            db, cache_key, "blog", response["model_id"],
            user_prompt[:2000], content, ttl_hours=48,
        )

        # Log cost
        log_ai_cost(
            db, response["model_id"], "blog",
            response["input_tokens"], response["output_tokens"],
            response["estimated_cost_usd"],
        )

        return {
            "content": content,
            "model_used": response["model_id"],
            "cached": False,
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": latency_ms,
        }

    @classmethod
    async def generate_seo_meta(
        cls,
        db: Session,
        name: str,
        category: str = "",
        region: str = "",
        description_short: str = "",
    ) -> dict:
        """
        Sinh SEO metadata (title, description, keywords).
        Luôn dùng model moderation (nhanh, rẻ).
        """
        user_prompt = SEO_META_USER_TEMPLATE.format(
            name=name[:200],
            category=category[:100] or "Không rõ",
            region=region[:100] or "Không rõ",
            description_short=description_short[:300] or "",
        )

        # Cache
        cache_key = generate_cache_key("seo_meta", user_prompt)
        cached = get_cached_response(db, cache_key)
        if cached:
            try:
                return {**json.loads(cached), "cached": True, "model_used": "cache"}
            except json.JSONDecodeError:
                pass

        start_time = time.monotonic()
        try:
            response = await vertex_ai_client.invoke_gemini(
                prompt=user_prompt,
                system_prompt=SEO_META_SYSTEM_PROMPT,
                model_id=settings.VERTEX_MODERATION_MODEL_ID,
                max_tokens=200,
                temperature=0.2,
                timeout=settings.AI_MODERATION_TIMEOUT,
            )
        except VertexAIClientError as e:
            logger.error("SEO meta generation failed: %s", e)
            raise

        latency_ms = int((time.monotonic() - start_time) * 1000)

        # Parse JSON response
        content = response["content"]
        try:
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            parsed = json.loads(content.strip())
        except json.JSONDecodeError:
            parsed = {
                "seo_title": name[:60],
                "seo_description": description_short[:155],
                "seo_keywords": category,
            }

        # Cache
        set_cached_response(
            db, cache_key, "seo_meta", response["model_id"],
            user_prompt[:1000], json.dumps(parsed, ensure_ascii=False),
        )

        # Log cost
        log_ai_cost(
            db, response["model_id"], "seo_meta",
            response["input_tokens"], response["output_tokens"],
            response["estimated_cost_usd"],
        )

        return {
            **parsed,
            "model_used": response["model_id"],
            "cached": False,
            "estimated_cost_usd": response["estimated_cost_usd"],
            "latency_ms": latency_ms,
        }
