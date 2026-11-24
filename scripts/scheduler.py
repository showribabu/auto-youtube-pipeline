"""
Task Scheduler — Runs the pipeline on a schedule using APScheduler.
Each category fires at its configured time each day.
"""
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import SCHEDULES
from logger import get_logger
logger = get_logger("scheduler")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import run_category


def _job(category: str, test_mode: bool = False):
    logger.info(f"━━━ Scheduled job triggered: {category} ━━━")
    try:
        result = run_category(category, dry_run=test_mode)
        if result:
            logger.info(f"✓ {category}: {result['title']}")
        else:
            logger.warning(f"✗ {category}: no video produced")
    except Exception as e:
        logger.error(f"✗ {category} FAILED: {e}", exc_info=True)


def start_scheduler(test_mode: bool = False):
    scheduler = BackgroundScheduler(timezone="UTC")

    for cat, cron_expr in SCHEDULES.items():
        parts = cron_expr.strip().split()
        if len(parts) < 5:
            logger.warning(f"Invalid cron for {cat}: {cron_expr}")
            continue
        minute, hour, dom, month, dow = parts
        trigger = CronTrigger(
            minute=minute, hour=hour, day_of_week=dow,
            day=dom, month=month, timezone="UTC"
        )
        scheduler.add_job(_job, trigger, args=[cat, test_mode],
                          id=f"auto_{cat}", name=f"Auto {cat}")
        logger.info(f"Scheduled '{cat}' → cron: {cron_expr}")

    logger.info("Scheduler started. Press Ctrl+C to stop.")
    scheduler.start()

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
