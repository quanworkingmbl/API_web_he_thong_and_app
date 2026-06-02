"""
AI Moderation Service
Pipeline: Rule Engine -> Gemini Flash (multimodal) -> (Escalate premium model nếu cần)
Dùng cho cả Product và Content moderation.

v2: Hỗ trợ multimodal — phân tích cả text lẫn ảnh sản phẩm/bài viết.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.ai.vertex_client import vertex_ai_client, VertexAIClientError
from app.services.ai.rule_engine import RuleEngine
from app.services.ai.cost_tracker import log_ai_cost, is_budget_exceeded
from app.services.ai.prompts import (
    MODERATION_SYSTEM_PROMPT,
    MODERATION_USER_TEMPLATE,
    CONTENT_MODERATION_SYSTEM_PROMPT,
    CONTENT_MODERATION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)

# Giới hạn text gửi lên AI (tăng từ 2000 → 8000 để bắt nội dung cuối bài)
TEXT_LIMIT = 8000
# Số ảnh tối đa gửi lên Gemini mỗi lần (5 ảnh để balance cost vs coverage)
MAX_IMAGES_PER_REQUEST = 5


def _is_vertex_permission_denied(error: Exception) -> bool:
    message = str(error)
    return (
        "PermissionDenied" in message
        or "permission denied" in message.lower()
        or getattr(error, "status_code", None) == 403
    )


@dataclass
class ModerationResult:
    decision: str                   # APPROVE / REVIEW / REJECT
    confidence: float = 0.0
    reasons: List[str] = None
    flags: List[str] = None
    image_issues: List[str] = None  # Vấn đề phát hiện qua phân tích ảnh
    source: str = ""                # "rule_engine" | "flash" | "creative_model"
    model_used: str = ""
    escalated: bool = False
    processing_time_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    images_analyzed: int = 0        # Số ảnh đã phân tích
    raw_response: str = ""

    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
        if self.flags is None:
            self.flags = []
        if self.image_issues is None:
            self.image_issues = []

    def to_dict(self) -> dict:
        return asdict(self)


# ==============================================================================
# IMAGE URL EXTRACTION HELPERS
# ==============================================================================

def _extract_image_urls_from_product(db: Session, product_id: int) -> List[str]:
    """
    Lấy tất cả URL ảnh của sản phẩm từ:
    1. Bảng product_media (ưu tiên — structured)
    2. products.images (JSON fallback — legacy)
    """
    from app.models.product_media import ProductMedia, MediaType
    from app.models.product import Product

    urls: List[str] = []

    # Source 1: product_media table (sắp xếp theo is_primary DESC, sort_order ASC)
    media_rows = (
        db.query(ProductMedia)
        .filter(
            ProductMedia.product_id == product_id,
            ProductMedia.media_type == MediaType.IMAGE,
        )
        .order_by(ProductMedia.is_primary.desc(), ProductMedia.sort_order.asc())
        .limit(MAX_IMAGES_PER_REQUEST)
        .all()
    )
    for m in media_rows:
        if m.url and m.url.startswith("http"):
            urls.append(m.url)

    # Source 2: products.images JSON (nếu chưa đủ ảnh)
    if len(urls) < MAX_IMAGES_PER_REQUEST:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product and product.images:
            try:
                legacy = json.loads(product.images)
                if isinstance(legacy, list):
                    for u in legacy:
                        if isinstance(u, str) and u.startswith("http") and u not in urls:
                            urls.append(u)
                            if len(urls) >= MAX_IMAGES_PER_REQUEST:
                                break
            except (json.JSONDecodeError, TypeError):
                pass

    logger.info("[Moderation] product_id=%d — image URLs found: %d", product_id, len(urls))
    return urls[:MAX_IMAGES_PER_REQUEST]


def _extract_image_urls_from_content(db: Session, content_id: int) -> List[str]:
    """
    Lấy URL ảnh của bài viết từ contents.images (JSON array).
    """
    from app.models.content import Content

    content = db.query(Content).filter(Content.id == content_id).first()
    if not content or not content.images:
        return []

    urls: List[str] = []
    try:
        images = json.loads(content.images)
        if isinstance(images, list):
            for item in images:
                if isinstance(item, str) and item.startswith("http"):
                    urls.append(item)
                elif isinstance(item, dict):
                    # Support {url: "...", alt: "..."} format
                    u = item.get("url") or item.get("src") or item.get("href", "")
                    if u and u.startswith("http"):
                        urls.append(u)
    except (json.JSONDecodeError, TypeError):
        pass

    logger.info("[Moderation] content_id=%d — image URLs found: %d", content_id, len(urls))
    return urls[:MAX_IMAGES_PER_REQUEST]


# ==============================================================================
# MODERATION SERVICE
# ==============================================================================

class ModerationService:
    """
    Kiểm duyệt product/content theo pipeline:
    1. Rule Engine (regex + blacklist) → REJECT ngay nếu vi phạm rõ
    2. Gemini Flash multimodal (text + ảnh, temperature=0) → APPROVE/REVIEW/REJECT
    3. Escalate premium model nếu: REVIEW + sản phẩm ưu tiên doanh thu
    """

    @classmethod
    async def moderate_product(
        cls,
        db: Session,
        product_id: int,
        name: str,
        description: str = "",
        category: str = "",
        category_id: Optional[int] = None,
        price: float = 0,
        label: str = "",
        region: str = "",
        is_high_value: bool = False,
    ) -> ModerationResult:
        """Kiểm duyệt sản phẩm (text + ảnh). Returns ModerationResult."""
        start_time = time.monotonic()

        # Step 1: Rule Engine (KHÔNG giới hạn text — kiểm tra toàn bộ)
        rule_result = RuleEngine.check_product(
            name=name,
            description=description,
            category_id=category_id,
            price=price,
            label=label,
        )

        if rule_result.decision == "REJECT":
            result = ModerationResult(
                decision="REJECT",
                confidence=1.0,
                reasons=rule_result.reasons,
                source="rule_engine",
                processing_time_ms=int((time.monotonic() - start_time) * 1000),
            )
            cls._save_log(db, result, product_id=product_id, rule_engine_result="REJECT")
            return result

        # Step 2: Fetch ảnh từ DB
        image_urls = _extract_image_urls_from_product(db, product_id)

        # Step 3: Gọi Gemini Flash multimodal
        try:
            flash_result = await cls._call_product_moderation_llm(
                name=name,
                description=description,
                category=category,
                price=price,
                label=label,
                region=region,
                image_urls=image_urls,
                model_id=settings.VERTEX_MODERATION_MODEL_ID,
                timeout=settings.AI_MODERATION_TIMEOUT + (5 if image_urls else 0),
            )
        except VertexAIClientError as e:
            logger.error("Moderation LLM failed: %s", e)
            if _is_vertex_permission_denied(e):
                raise
            result = ModerationResult(
                decision="REVIEW",
                confidence=0.0,
                reasons=[f"AI moderation failed: {str(e)}"],
                flags=rule_result.reasons,
                source="fallback",
                processing_time_ms=int((time.monotonic() - start_time) * 1000),
            )
            cls._save_log(db, result, product_id=product_id, rule_engine_result=rule_result.decision)
            return result

        # Merge flags từ rule engine
        if rule_result.decision == "FLAG":
            flash_result.flags.extend(rule_result.reasons)

        # Step 4: Escalate to creative model nếu cần
        if flash_result.decision == "REVIEW" and is_high_value:
            if not is_budget_exceeded(db):
                try:
                    creative_result = await cls._call_product_moderation_llm(
                        name=name,
                        description=description,
                        category=category,
                        price=price,
                        label=label,
                        region=region,
                        image_urls=image_urls,
                        model_id=settings.VERTEX_CREATIVE_MODEL_ID,
                        timeout=settings.AI_MODERATION_TIMEOUT + 10,
                    )
                    creative_result.escalated = True
                    creative_result.source = "creative_model"
                    creative_result.processing_time_ms = int((time.monotonic() - start_time) * 1000)

                    log_ai_cost(
                        db, settings.VERTEX_CREATIVE_MODEL_ID, "moderation",
                        creative_result.input_tokens, creative_result.output_tokens,
                        creative_result.estimated_cost_usd,
                    )
                    cls._save_log(db, creative_result, product_id=product_id, rule_engine_result=rule_result.decision)
                    return creative_result

                except VertexAIClientError:
                    logger.warning("Creative escalation failed, keeping flash result")

        flash_result.processing_time_ms = int((time.monotonic() - start_time) * 1000)

        log_ai_cost(
            db, settings.VERTEX_MODERATION_MODEL_ID, "moderation",
            flash_result.input_tokens, flash_result.output_tokens,
            flash_result.estimated_cost_usd,
        )

        cls._save_log(db, flash_result, product_id=product_id, rule_engine_result=rule_result.decision)
        return flash_result

    @classmethod
    async def moderate_content(
        cls,
        db: Session,
        content_id: int,
        title: str,
        content_text: str = "",
        content_type: str = "",
    ) -> ModerationResult:
        """Kiểm duyệt content/blog (text + ảnh)."""
        start_time = time.monotonic()

        # Step 1: Rule Engine (toàn bộ text, không giới hạn)
        rule_result = RuleEngine.check_content(
            title=title,
            content_text=content_text,
            content_type=content_type,
        )

        if rule_result.decision == "REJECT":
            result = ModerationResult(
                decision="REJECT",
                confidence=1.0,
                reasons=rule_result.reasons,
                source="rule_engine",
                processing_time_ms=int((time.monotonic() - start_time) * 1000),
            )
            cls._save_log(db, result, content_id=content_id, rule_engine_result="REJECT")
            return result

        # Step 2: Fetch ảnh từ DB
        image_urls = _extract_image_urls_from_content(db, content_id)

        # Step 3: Build prompt với giới hạn TEXT_LIMIT (8000 ký tự)
        try:
            prompt = CONTENT_MODERATION_USER_TEMPLATE.format(
                title=title[:500],
                content_type=content_type,
                image_count=len(image_urls),
                content=content_text[:TEXT_LIMIT],
            )

            response = await vertex_ai_client.invoke_gemini_multimodal(
                prompt=prompt,
                image_urls=image_urls,
                system_prompt=CONTENT_MODERATION_SYSTEM_PROMPT,
                model_id=settings.VERTEX_MODERATION_MODEL_ID,
                max_tokens=250,
                temperature=0,
                timeout=settings.AI_MODERATION_TIMEOUT + (5 if image_urls else 0),
                json_mode=True,
                max_images=MAX_IMAGES_PER_REQUEST,
            )

            result = cls._parse_moderation_response(response)
            result.images_analyzed = response.get("images_analyzed", 0)

            if rule_result.decision == "FLAG":
                result.flags.extend(rule_result.reasons)

            result.processing_time_ms = int((time.monotonic() - start_time) * 1000)

            log_ai_cost(
                db, settings.VERTEX_MODERATION_MODEL_ID, "moderation",
                result.input_tokens, result.output_tokens, result.estimated_cost_usd,
            )

            cls._save_log(db, result, content_id=content_id, rule_engine_result=rule_result.decision)
            return result

        except VertexAIClientError as e:
            if _is_vertex_permission_denied(e):
                raise
            result = ModerationResult(
                decision="REVIEW",
                confidence=0.0,
                reasons=[f"AI moderation failed: {str(e)}"],
                flags=rule_result.reasons,
                source="fallback",
                processing_time_ms=int((time.monotonic() - start_time) * 1000),
            )
            cls._save_log(db, result, content_id=content_id, rule_engine_result=rule_result.decision)
            return result

    # --------------------------------------------------------------------------
    # INTERNAL
    # --------------------------------------------------------------------------

    @classmethod
    async def _call_product_moderation_llm(
        cls,
        name: str,
        description: str,
        category: str,
        price: float,
        label: str,
        region: str,
        image_urls: List[str],
        model_id: str,
        timeout: int,
    ) -> ModerationResult:
        """Gọi Gemini multimodal để kiểm duyệt sản phẩm."""
        prompt = MODERATION_USER_TEMPLATE.format(
            name=name[:300],
            description=description[:TEXT_LIMIT],
            category=category[:100],
            price=f"{price:,.0f}",
            label=label or "Không có",
            region=region or "Không rõ",
            image_count=len(image_urls),
        )

        response = await vertex_ai_client.invoke_gemini_multimodal(
            prompt=prompt,
            image_urls=image_urls,
            system_prompt=MODERATION_SYSTEM_PROMPT,
            model_id=model_id,
            max_tokens=250,
            temperature=0,
            timeout=timeout,
            json_mode=True,
            max_images=MAX_IMAGES_PER_REQUEST,
        )

        result = cls._parse_moderation_response(response)
        result.images_analyzed = response.get("images_analyzed", 0)
        return result

    @classmethod
    def _parse_moderation_response(cls, response: dict) -> ModerationResult:
        """Parse JSON response từ model. Fallback REVIEW nếu parse fail."""
        import re
        content = response.get("content", "")
        raw = content

        parsed = None
        parse_error = None

        # Attempt 1: Direct JSON parse (works when json_mode=True)
        try:
            parsed = json.loads(content.strip())
        except (json.JSONDecodeError, ValueError):
            pass

        # Attempt 2: Extract from markdown code block ```json ... ```
        if parsed is None:
            try:
                block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
                if block_match:
                    parsed = json.loads(block_match.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        # Attempt 3: Find first {...} JSON object anywhere in text
        if parsed is None:
            try:
                json_match = re.search(r"(\{[^{}]*\})", content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        # Attempt 4: Greedy search for outermost {...} block
        if parsed is None:
            try:
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    parsed = json.loads(content[start:end + 1])
            except (json.JSONDecodeError, ValueError) as e:
                parse_error = e

        if parsed is not None:
            decision = str(parsed.get("decision", "REVIEW")).upper()
            if decision not in ("APPROVE", "REVIEW", "REJECT"):
                decision = "REVIEW"

            model_id_str = response.get("model_id", "")
            source = "flash" if "flash" in model_id_str.lower() else "creative_model"

            return ModerationResult(
                decision=decision,
                confidence=float(parsed.get("confidence", 0.5)),
                reasons=parsed.get("reasons", []),
                flags=parsed.get("flags", []),
                image_issues=parsed.get("image_issues", []),
                source=source,
                model_used=model_id_str,
                input_tokens=response.get("input_tokens", 0),
                output_tokens=response.get("output_tokens", 0),
                estimated_cost_usd=response.get("estimated_cost_usd", 0.0),
                images_analyzed=response.get("images_analyzed", 0),
                raw_response=raw,
            )

        # All attempts failed
        logger.warning("Moderation JSON parse failed: %s — raw: %s", parse_error, raw[:300])
        return ModerationResult(
            decision="REVIEW",
            confidence=0.0,
            reasons=[f"AI response parse error: {str(parse_error)}"],
            source="parse_fail",
            model_used=response.get("model_id", ""),
            input_tokens=response.get("input_tokens", 0),
            output_tokens=response.get("output_tokens", 0),
            estimated_cost_usd=response.get("estimated_cost_usd", 0.0),
            images_analyzed=response.get("images_analyzed", 0),
            raw_response=raw,
        )

    @classmethod
    def _save_log(
        cls,
        db: Session,
        result: ModerationResult,
        product_id: Optional[int] = None,
        content_id: Optional[int] = None,
        rule_engine_result: str = "PASS",
    ) -> None:
        """Lưu log kiểm duyệt vào DB."""
        from app.models.ai_log import AIModerationLog

        try:
            log = AIModerationLog(
                product_id=product_id,
                content_id=content_id,
                rule_engine_result=rule_engine_result,
                rule_engine_flags=json.dumps(result.flags, ensure_ascii=False) if result.flags else None,
                model_used=result.model_used or result.source,
                ai_decision=result.decision,
                ai_confidence=result.confidence,
                ai_reasons=json.dumps(result.reasons, ensure_ascii=False) if result.reasons else None,
                ai_flags=json.dumps(
                    result.flags + (result.image_issues or []),
                    ensure_ascii=False
                ) if (result.flags or result.image_issues) else None,
                escalated=result.escalated,
                processing_time_ms=result.processing_time_ms,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                estimated_cost_usd=result.estimated_cost_usd,
                raw_response=result.raw_response[:5000] if result.raw_response else None,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning("Failed to save moderation log: %s", e)
