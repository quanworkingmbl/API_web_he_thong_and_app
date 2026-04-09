"""
AI Moderation Service
Pipeline: Rule Engine → Haiku → (Escalate Sonnet nếu cần)
Dùng cho cả Product và Content moderation.
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.ai.bedrock_client import bedrock_client, BedrockClientError
from app.services.ai.rule_engine import RuleEngine
from app.services.ai.cost_tracker import log_ai_cost, is_budget_exceeded
from app.services.ai.prompts import (
    MODERATION_SYSTEM_PROMPT,
    MODERATION_USER_TEMPLATE,
    CONTENT_MODERATION_SYSTEM_PROMPT,
    CONTENT_MODERATION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


def _is_bedrock_access_denied(error: Exception) -> bool:
    message = str(error)
    return (
        "AccessDeniedException" in message
        or "not authorized to perform: bedrock:InvokeModel" in message
    )


@dataclass
class ModerationResult:
    decision: str                   # APPROVE / REVIEW / REJECT
    confidence: float = 0.0
    reasons: List[str] = None
    flags: List[str] = None
    source: str = ""                # "rule_engine" | "haiku" | "sonnet"
    model_used: str = ""
    escalated: bool = False
    processing_time_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    raw_response: str = ""

    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
        if self.flags is None:
            self.flags = []

    def to_dict(self) -> dict:
        return asdict(self)


class ModerationService:
    """
    Kiểm duyệt product/content theo pipeline:
    1. Rule Engine (regex + blacklist) → REJECT ngay nếu vi phạm rõ
    2. Haiku (temperature=0, max_tokens=120) → APPROVE/REVIEW/REJECT
    3. Escalate Sonnet nếu: REVIEW + sản phẩm ưu tiên doanh thu
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
        """Kiểm duyệt sản phẩm. Returns ModerationResult."""
        start_time = time.monotonic()

        # Step 1: Rule Engine
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

        # Step 2: Gọi Haiku
        try:
            haiku_result = await cls._call_moderation_llm(
                name=name,
                description=description,
                category=category,
                price=price,
                label=label,
                region=region,
                model_id=settings.BEDROCK_MODERATION_MODEL_ID,
                timeout=settings.AI_MODERATION_TIMEOUT,
            )
        except BedrockClientError as e:
            logger.error("Moderation LLM failed: %s", e)
            if _is_bedrock_access_denied(e):
                # Bubble up IAM/model permission errors so API can return 503 clearly.
                raise
            # Fallback: REVIEW (an toàn)
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

        # Kết hợp flags từ rule engine
        if rule_result.decision == "FLAG":
            haiku_result.flags.extend(rule_result.reasons)

        # Step 3: Escalate to Sonnet nếu cần
        if haiku_result.decision == "REVIEW" and is_high_value:
            if not is_budget_exceeded(db):
                try:
                    sonnet_result = await cls._call_moderation_llm(
                        name=name,
                        description=description,
                        category=category,
                        price=price,
                        label=label,
                        region=region,
                        model_id=settings.BEDROCK_CREATIVE_MODEL_ID,
                        timeout=settings.AI_MODERATION_TIMEOUT + 4,  # Sonnet cần thêm thời gian
                    )
                    sonnet_result.escalated = True
                    sonnet_result.source = "sonnet"
                    sonnet_result.processing_time_ms = int((time.monotonic() - start_time) * 1000)

                    # Log cost cho Sonnet
                    log_ai_cost(
                        db, settings.BEDROCK_CREATIVE_MODEL_ID, "moderation",
                        sonnet_result.input_tokens, sonnet_result.output_tokens,
                        sonnet_result.estimated_cost_usd,
                    )

                    cls._save_log(db, sonnet_result, product_id=product_id, rule_engine_result=rule_result.decision)
                    return sonnet_result

                except BedrockClientError:
                    logger.warning("Sonnet escalation failed, keeping Haiku result")

        haiku_result.processing_time_ms = int((time.monotonic() - start_time) * 1000)

        # Log cost cho Haiku
        log_ai_cost(
            db, settings.BEDROCK_MODERATION_MODEL_ID, "moderation",
            haiku_result.input_tokens, haiku_result.output_tokens,
            haiku_result.estimated_cost_usd,
        )

        cls._save_log(db, haiku_result, product_id=product_id, rule_engine_result=rule_result.decision)
        return haiku_result

    @classmethod
    async def moderate_content(
        cls,
        db: Session,
        content_id: int,
        title: str,
        content_text: str = "",
        content_type: str = "",
    ) -> ModerationResult:
        """Kiểm duyệt content/blog."""
        start_time = time.monotonic()

        # Step 1: Rule Engine
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

        # Step 2: Gọi Haiku
        try:
            prompt = CONTENT_MODERATION_USER_TEMPLATE.format(
                title=title[:500],
                content_type=content_type,
                content=content_text[:2000],
            )

            response = await bedrock_client.invoke_claude(
                prompt=prompt,
                system_prompt=CONTENT_MODERATION_SYSTEM_PROMPT,
                model_id=settings.BEDROCK_MODERATION_MODEL_ID,
                max_tokens=120,
                temperature=0,
                timeout=settings.AI_MODERATION_TIMEOUT,
            )

            result = cls._parse_moderation_response(response)

            if rule_result.decision == "FLAG":
                result.flags.extend(rule_result.reasons)

            result.processing_time_ms = int((time.monotonic() - start_time) * 1000)

            log_ai_cost(
                db, settings.BEDROCK_MODERATION_MODEL_ID, "moderation",
                result.input_tokens, result.output_tokens, result.estimated_cost_usd,
            )

            cls._save_log(db, result, content_id=content_id, rule_engine_result=rule_result.decision)
            return result

        except BedrockClientError as e:
            if _is_bedrock_access_denied(e):
                # Bubble up IAM/model permission errors so API can return 503 clearly.
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
    async def _call_moderation_llm(
        cls,
        name: str,
        description: str,
        category: str,
        price: float,
        label: str,
        region: str,
        model_id: str,
        timeout: int,
    ) -> ModerationResult:
        """Gọi Claude để kiểm duyệt sản phẩm."""
        prompt = MODERATION_USER_TEMPLATE.format(
            name=name[:300],
            description=description[:2000],
            category=category[:100],
            price=f"{price:,.0f}",
            label=label or "Không có",
            region=region or "Không rõ",
        )

        response = await bedrock_client.invoke_claude(
            prompt=prompt,
            system_prompt=MODERATION_SYSTEM_PROMPT,
            model_id=model_id,
            max_tokens=120,
            temperature=0,
            timeout=timeout,
        )

        return cls._parse_moderation_response(response)

    @classmethod
    def _parse_moderation_response(cls, response: dict) -> ModerationResult:
        """Parse JSON response từ Claude. Fallback REVIEW nếu parse fail."""
        content = response.get("content", "")
        raw = content

        try:
            # Claude đôi khi wrap JSON trong markdown block
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            parsed = json.loads(content.strip())

            decision = parsed.get("decision", "REVIEW").upper()
            if decision not in ("APPROVE", "REVIEW", "REJECT"):
                decision = "REVIEW"

            return ModerationResult(
                decision=decision,
                confidence=float(parsed.get("confidence", 0.5)),
                reasons=parsed.get("reasons", []),
                flags=parsed.get("flags", []),
                source="haiku" if "haiku" in response.get("model_id", "").lower() else "sonnet",
                model_used=response.get("model_id", ""),
                input_tokens=response.get("input_tokens", 0),
                output_tokens=response.get("output_tokens", 0),
                estimated_cost_usd=response.get("estimated_cost_usd", 0.0),
                raw_response=raw,
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning("Moderation JSON parse failed: %s — raw: %s", e, raw[:200])
            return ModerationResult(
                decision="REVIEW",
                confidence=0.0,
                reasons=[f"AI response parse error: {str(e)}"],
                source="parse_fail",
                model_used=response.get("model_id", ""),
                input_tokens=response.get("input_tokens", 0),
                output_tokens=response.get("output_tokens", 0),
                estimated_cost_usd=response.get("estimated_cost_usd", 0.0),
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
                ai_flags=json.dumps(result.flags, ensure_ascii=False) if result.flags else None,
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
