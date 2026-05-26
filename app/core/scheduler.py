"""
app/core/scheduler.py
=====================
Tác vụ định kỳ (Cron Jobs) cho hệ thống.

Dùng APScheduler (AsyncIOScheduler) tích hợp với FastAPI lifecycle.

Danh sách tác vụ:
- release_reserves_job  : Chạy mỗi ngày lúc 2:00 SA
                          Giải phóng 20% reserve đã quá 30 ngày
                          về available_balance cho tất cả seller.

Cách tích hợp: gọi start_scheduler() trong lifespan của FastAPI (app/main.py).
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.services.wallet import release_matured_reserves
from app.models.user import User

logger = logging.getLogger(__name__)

# Singleton scheduler instance
_scheduler: BackgroundScheduler | None = None


# ==============================================================================
# JOB DEFINITIONS
# ==============================================================================

def _release_reserves_all_sellers() -> None:
    """
    Giải phóng reserve đã đủ 30 ngày cho TẤT CẢ seller có reserve chờ.

    Logic:
    1. Lấy danh sách seller_id còn reserve chưa giải phóng.
    2. Gọi release_matured_reserves() cho từng seller.
    3. Log kết quả.

    Chạy: mỗi ngày lúc 02:00 SA (UTC) — giờ thấp điểm.
    """
    db = SessionLocal()
    try:
        # Lấy danh sách seller_id có đơn reserve chưa release
        from sqlalchemy import text
        result = db.execute(text(
            "SELECT DISTINCT seller_id FROM orders "
            "WHERE wallet_credited = TRUE "
            "  AND reserve_release_at IS NOT NULL "
            "  AND reserve_release_at <= NOW() "
            "  AND (reserve_released IS NULL OR reserve_released = FALSE)"
        ))
        seller_ids = [row[0] for row in result.fetchall()]

        if not seller_ids:
            logger.info("[Scheduler] release_reserves: Không có reserve nào cần giải phóng.")
            return

        total_released_all = 0
        released_sellers = 0
        for seller_id in seller_ids:
            try:
                released = release_matured_reserves(seller_id, db)
                if released > 0:
                    db.commit()
                    total_released_all += released
                    released_sellers += 1
            except Exception as e:
                db.rollback()
                logger.error(
                    "[Scheduler] release_reserves: Lỗi seller #%s: %s",
                    seller_id, e, exc_info=True
                )

        logger.info(
            "[Scheduler] release_reserves: Hoàn tất — giải phóng %s VND cho %d/%d seller.",
            total_released_all, released_sellers, len(seller_ids)
        )

    except Exception as e:
        logger.error("[Scheduler] release_reserves: Lỗi nghiêm trọng: %s", e, exc_info=True)
        db.rollback()
    finally:
        db.close()


# ==============================================================================
# SCHEDULER LIFECYCLE
# ==============================================================================

def start_scheduler() -> BackgroundScheduler:
    """
    Khởi động scheduler và đăng ký tất cả cron jobs.
    Dùng BackgroundScheduler (thread-based) — tương thích Gunicorn UvicornWorker.
    Gọi trong FastAPI lifespan startup.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.warning("[Scheduler] Scheduler đã chạy, bỏ qua start.")
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")

    # ── Job 1: Release reserve mỗi ngày 2:00 SA (giờ VN) ──────────────────
    _scheduler.add_job(
        _release_reserves_all_sellers,
        trigger=CronTrigger(hour=2, minute=0),
        id="release_reserves_daily",
        name="Giải phóng reserve 30 ngày cho seller",
        replace_existing=True,
        misfire_grace_time=3600,  # Nếu server down, cho phép chạy bù trong vòng 1h
    )

    _scheduler.start()
    logger.info(
        "[Scheduler] Đã khởi động. Jobs: %s",
        [job.id for job in _scheduler.get_jobs()]
    )
    return _scheduler


def stop_scheduler() -> None:
    """Dừng scheduler gracefully. Gọi trong FastAPI lifespan shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Đã dừng scheduler.")
    _scheduler = None
