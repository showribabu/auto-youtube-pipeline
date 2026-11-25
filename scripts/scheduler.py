"""
Task Scheduler — Runs the pipeline on a schedule using APScheduler.
Each category × language fires at its configured time each day,
staggered by 2 minutes per language variant.
"""
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import SCHEDULES, ENABLED_LANGUAGES
from logger import get_logger
logger = get_logger("scheduler")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import run_category


def _job(category: str, lang: str, test_mode: bool = False):
    logger.info(f"━━━ Scheduled job triggered: {category} [{lang}] ━━━")
    try:
        result = run_category(category, dry_run=test_mode, lang=lang)
        if result:
            logger.info(f"✓ {category}[{lang}]: {result['title']}")
        else:
            logger.warning(f"✗ {category}[{lang}]: no video produced")
    except Exception as e:
        logger.error(f"✗ {category}[{lang}] FAILED: {e}", exc_info=True)


def start_scheduler(test_mode: bool = False):
    scheduler = BackgroundScheduler(timezone="UTC")

    for cat, cron_expr in SCHEDULES.items():
        parts = cron_expr.strip().split()
        if len(parts) < 5:
            logger.warning(f"Invalid cron for {cat}: {cron_expr}")
            continue
        base_minute, hour, dom, month, dow = parts

        for lang_idx, lang in enumerate(ENABLED_LANGUAGES):
            lang = lang.strip()
            # Stagger by 2 minutes per language variant
            staggered_minute = (int(base_minute) + lang_idx * 2) % 60
            # If stagger pushes past 59, bump the hour
            staggered_hour = int(hour) + (int(base_minute) + lang_idx * 2) // 60
            if staggered_hour > 23:
                staggered_hour = staggered_hour % 24

            trigger = CronTrigger(
                minute=str(staggered_minute), hour=str(staggered_hour),
                day_of_week=dow, day=dom, month=month, timezone="UTC"
            )
            job_id = f"auto_{cat}_{lang}"
            scheduler.add_job(_job, trigger, args=[cat, lang, test_mode],
                              id=job_id, name=f"Auto {cat} [{lang}]")
            logger.info(f"Scheduled '{cat}[{lang}]' → cron: {staggered_minute} {staggered_hour} {dom} {month} {dow}")

    total_jobs = len(SCHEDULES) * len(ENABLED_LANGUAGES)
    logger.info(f"Scheduler started with {total_jobs} jobs. Press Ctrl+C to stop.")
    scheduler.start()

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
