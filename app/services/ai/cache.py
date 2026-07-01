"""
AI Response Cache
- Hash input → check cache → return cached hoặc gọi AI
- DB-backed persistence
- TTL configurable
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_cache_key(task_type: str, input_text: str, model_id: str = "") -> str:
    """Tạo hash key từ task_type + input_text + model_id."""
    raw = f"{task_type}:{model_id}:{input_text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cached_response(db: Session, cache_key: str) -> Optional[str]:
    """Lấy response từ cache nếu chưa hết hạn."""
    from app.models.ai_log import AIGenerationCache

    cached = (
        db.query(AIGenerationCache)
        .filter(
            AIGenerationCache.input_hash == cache_key,
            AIGenerationCache.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if cached:
        logger.info("Cache HIT: key=%s task=%s", cache_key[:16], cached.task_type)
        return cached.output_text

    return None


def set_cached_response(
    db: Session,
    cache_key: str,
    task_type: str,
    model_used: str,
    input_text: str,
    output_text: str,
    ttl_hours: Optional[int] = None,
) -> None:
    """Lưu response vào cache."""
    from app.models.ai_log import AIGenerationCache

    ttl = ttl_hours or settings.AI_CACHE_TTL_HOURS
    expires_at = datetime.utcnow() + timedelta(hours=ttl)

    # Upsert — tránh duplicate
    existing = (
        db.query(AIGenerationCache)
        .filter(AIGenerationCache.input_hash == cache_key)
        .first()
    )

    if existing:
        existing.output_text = output_text
        existing.model_used = model_used
        existing.expires_at = expires_at
        existing.created_at = datetime.utcnow()
    else:
        entry = AIGenerationCache(
            input_hash=cache_key,
            task_type=task_type,
            model_used=model_used,
            input_text=input_text[:5000],  # Limit storage
            output_text=output_text,
            expires_at=expires_at,
        )
        db.add(entry)

    try:
        db.commit()
        logger.info("Cache SET: key=%s task=%s ttl=%dh", cache_key[:16], task_type, ttl)
    except Exception as e:
        db.rollback()
        logger.warning("Cache SET failed: %s", e)


def cleanup_expired_cache(db: Session) -> int:
    """Xóa cache đã hết hạn. Trả về số bản ghi đã xóa."""
    from app.models.ai_log import AIGenerationCache

    try:
        deleted = (
            db.query(AIGenerationCache)
            .filter(AIGenerationCache.expires_at <= datetime.utcnow())
            .delete(synchronize_session=False)
        )
        db.commit()
        logger.info("Cache cleanup: removed %d expired entries", deleted)
        return deleted
    except Exception as e:
        db.rollback()
        logger.warning("Cache cleanup failed: %s", e)
        return 0
