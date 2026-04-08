"""
AI Cost Tracker & Budget Guardrail
- Log mỗi request: model, tokens, cost
- Kiểm tra daily budget
- Auto-downgrade khi vượt ngưỡng
"""

import logging
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)


def log_ai_cost(
    db: Session,
    model_id: str,
    task_type: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
) -> None:
    """Ghi log chi phí AI. Aggregate theo ngày + model + task."""
    from app.models.ai_log import AICostLog

    today = date.today()

    existing = (
        db.query(AICostLog)
        .filter(
            AICostLog.log_date == today,
            AICostLog.model_id == model_id,
            AICostLog.task_type == task_type,
        )
        .first()
    )

    if existing:
        existing.request_count += 1
        existing.total_input_tokens += input_tokens
        existing.total_output_tokens += output_tokens
        existing.total_cost_usd += cost_usd
    else:
        entry = AICostLog(
            log_date=today,
            model_id=model_id,
            task_type=task_type,
            request_count=1,
            total_input_tokens=input_tokens,
            total_output_tokens=output_tokens,
            total_cost_usd=cost_usd,
        )
        db.add(entry)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning("Cost logging failed: %s", e)


def get_daily_cost(db: Session, target_date: Optional[date] = None) -> float:
    """Lấy tổng chi phí AI trong ngày."""
    from app.models.ai_log import AICostLog

    d = target_date or date.today()
    result = (
        db.query(func.coalesce(func.sum(AICostLog.total_cost_usd), 0.0))
        .filter(AICostLog.log_date == d)
        .scalar()
    )
    return float(result)


def is_budget_exceeded(db: Session) -> bool:
    """Kiểm tra có vượt ngân sách ngày chưa."""
    daily_cost = get_daily_cost(db)
    exceeded = daily_cost >= settings.AI_DAILY_BUDGET_USD
    if exceeded:
        logger.warning(
            "AI daily budget EXCEEDED: $%.4f / $%.2f",
            daily_cost, settings.AI_DAILY_BUDGET_USD,
        )
    return exceeded


def should_use_sonnet(db: Session, force: bool = False) -> bool:
    """
    Quyết định có dùng Sonnet (đắt) hay Haiku (rẻ).
    Nếu budget vượt 80% → tự hạ xuống Haiku.
    """
    if force:
        return True

    daily_cost = get_daily_cost(db)
    budget_ratio = daily_cost / max(settings.AI_DAILY_BUDGET_USD, 0.01)

    if budget_ratio >= 0.8:
        logger.info(
            "Budget at %.0f%% — downgrading to Haiku (cost=$%.4f)",
            budget_ratio * 100, daily_cost,
        )
        return False

    return True


def get_cost_report(db: Session, date_from: date, date_to: date) -> dict:
    """Báo cáo chi phí AI theo khoảng thời gian."""
    from app.models.ai_log import AICostLog

    logs = (
        db.query(AICostLog)
        .filter(AICostLog.log_date >= date_from, AICostLog.log_date <= date_to)
        .order_by(AICostLog.log_date.desc())
        .all()
    )

    total_cost = sum(log.total_cost_usd for log in logs)
    total_requests = sum(log.request_count for log in logs)
    total_input_tokens = sum(log.total_input_tokens for log in logs)
    total_output_tokens = sum(log.total_output_tokens for log in logs)

    # Breakdown theo model
    by_model = {}
    for log in logs:
        if log.model_id not in by_model:
            by_model[log.model_id] = {"cost": 0.0, "requests": 0}
        by_model[log.model_id]["cost"] += log.total_cost_usd
        by_model[log.model_id]["requests"] += log.request_count

    # Breakdown theo task
    by_task = {}
    for log in logs:
        if log.task_type not in by_task:
            by_task[log.task_type] = {"cost": 0.0, "requests": 0}
        by_task[log.task_type]["cost"] += log.total_cost_usd
        by_task[log.task_type]["requests"] += log.request_count

    # Daily breakdown
    daily = {}
    for log in logs:
        day_str = log.log_date.isoformat()
        if day_str not in daily:
            daily[day_str] = {"cost": 0.0, "requests": 0}
        daily[day_str]["cost"] += log.total_cost_usd
        daily[day_str]["requests"] += log.request_count

    return {
        "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
        "total_cost_usd": round(total_cost, 6),
        "total_requests": total_requests,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "by_model": by_model,
        "by_task": by_task,
        "daily": daily,
        "budget_daily_usd": settings.AI_DAILY_BUDGET_USD,
    }
