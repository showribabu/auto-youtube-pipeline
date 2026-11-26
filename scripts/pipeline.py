"""
Auto YouTube Pipeline — Main Orchestrator

Usage:
    python pipeline.py --category kids              # manual run for one category
    python pipeline.py --run-all                    # generate + upload all categories once
    python pipeline.py --scheduler                  # start background task scheduler
    python pipeline.py --test                       # dry-run mode (no uploads)
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OUTPUT_DIR, MAX_VIDEOS_PER_DAY, RETRY_DELAY, MAX_RETRIES, ENABLED_LANGUAGES, FFPROBE
from logger import get_logger
from engine import generate_title_card, generate_frame_sequence, assemble_video, get_font
from audio import run_audio_sync
from upload import upload_video, set_thumbnail

logger = get_logger("pipeline")

LEDGER_PATH = os.path.join(OUTPUT_DIR, "upload_ledger.json")


def _ledger_load() -> list[dict]:
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _ledger_append(entry: dict) -> None:
    ledger = _ledger_load()
    ledger.append(entry)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)


def _count_today_uploads() -> int:
    """Count videos actually published today (from the ledger, not the filesystem)."""
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(
        1 for e in _ledger_load()
        if e.get("date") == today and e.get("video_id") and e["video_id"] != "dry-run"
    )


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip()
    s = re.sub(r"\s+", "_", s)[:80]
    return s or "video"


def _prune_outputs(max_file_age_days: int = 7) -> None:
    """Keep the always-on host from filling its disk."""
    cutoff = datetime.now().timestamp() - max_file_age_days * 86400
    for path in glob.glob(os.path.join(OUTPUT_DIR, "*", "*")):
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            pass


def run_category(category: str, dry_run: bool = False, lang: str = "en") -> dict | None:
    """Generate a video for one category in a given language and optionally upload it."""
    import categories.kids as kids_mod
    import categories.news as news_mod
    import categories.weather as weather_mod
    import categories.facts as facts_mod
    import categories.motivational as motiv_mod
    import categories.tech as tech_mod
    import categories.crypto as crypto_mod
    import categories.health as health_mod
    import categories.history as history_mod
    import categories.gaming as gaming_mod
    import categories.language_learning as lang_mod
    import categories.books as books_mod
    import categories.cooking as cooking_mod
    import categories.devotional as dev_mod
    from multilang import translate_content

    generators = {
        "devotional":     dev_mod.generate_devotional_content,
        "kids":           kids_mod.generate_kids_content,
        "news":           news_mod.generate_news_content,
        "weather":        weather_mod.generate_weather_content,
        "facts":          facts_mod.generate_fact_content,
        "motivational":   motiv_mod.generate_motivational_content,
        "tech":           tech_mod.generate_tech_content,
        "crypto":         crypto_mod.generate_crypto_content,
        "health":         health_mod.generate_health_content,
        "history":        history_mod.generate_history_content,
        "gaming":         gaming_mod.generate_gaming_content,
        "language":       lang_mod.generate_language_content,
        "books":          books_mod.generate_book_content,
        "cooking":        cooking_mod.generate_cooking_content,
    }

    gen = generators.get(category)
    if not gen:
        logger.error(f"Unknown category: {category}")
        return None

    try:
        import inspect
        sig = inspect.signature(gen)
        if "lang" in sig.parameters:
            content = gen(lang=lang)
        else:
            content = gen()
    except Exception as e:
        logger.error(f"Content generation failed for {category}: {e}")
        return None

    # Translate content for non-English languages
    content = translate_content(content, lang)

    # Import Shorts categories
    from engine import SHORTS_CATEGORIES

    is_shorts = category in SHORTS_CATEGORIES

    title        = content["title"]
    script       = content["full_script"]
    script_lines = content["script_lines"]
    voice        = content.get("voice", "default_female")
    rate         = content.get("rate", "+0%")
    tags         = list(content.get("tags", []))
    description  = content["description"]

    # Supercharge metadata for Shorts & Viral discoverability
    if is_shorts:
        if "#Shorts" not in title:
            # Ensure title has space for #Shorts within 100 char limit
            title = f"{title[:90]} #Shorts"
        tags.extend(["shorts", "viral", "trending", "youtubeshorts", "daily", "foryou"])
        description = f"{description}\n\n#Shorts #Viral #Trending #YouTubeShorts #DailyKnowledge"

    # QA Gate 1: Content & Metadata Validation
    from validator import (
        validate_content_metadata,
        validate_audio,
        validate_frame,
        validate_thumbnail,
        validate_video_file
    )
    content["title"] = title
    meta_ok, meta_msg = validate_content_metadata(content, lang=lang)
    if not meta_ok:
        logger.error(f"[QA REJECTED] Metadata validation failed: {meta_msg}")
        return None
    logger.info(f"✓ [QA PASSED] Metadata: {meta_msg}")

    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = _slug(title)
    if lang != "en":
        safe_title = f"{safe_title}_{lang}"
    out_dir = os.path.join(OUTPUT_DIR, f"{category}_{lang}")
    os.makedirs(out_dir, exist_ok=True)

    output_path     = os.path.join(out_dir, f"{ts_str}_{safe_title}.mp4")
    audio_path      = os.path.join(out_dir, f"{ts_str}_{safe_title}.mp3")
    thumbnail_path  = os.path.join(out_dir, f"{ts_str}_{safe_title}_thumb.jpg")

    logger.info(f"Generating video for: {title} [{category}] (Shorts={is_shorts})")

    # Step 1: Generate frames (1080x1920 for Shorts, 1280x720 for landscape)
    try:
        frames = generate_frame_sequence(
            script_lines, category, duration_per_line=4.0,
            output_dir=out_dir, is_shorts=is_shorts
        )
    except Exception as e:
        logger.error(f"Frame generation failed: {e}")
        return None

    # QA Gate 2: Frames Inspection
    exp_w = 1080 if is_shorts else 1280
    exp_h = 1920 if is_shorts else 720
    for idx, f_path in enumerate(frames):
        f_ok, f_msg = validate_frame(f_path, exp_w, exp_h)
        if not f_ok:
            logger.error(f"[QA REJECTED] Frame {idx} failed: {f_msg}")
            return None
    logger.info(f"✓ [QA PASSED] All {len(frames)} frames verified (dimensions & visual density).")

    # Step 2: Generate voiceover
    try:
        run_audio_sync(script, voice=voice, rate=rate, output_path=audio_path)
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        return None

    # QA Gate 3: Audio Stream Inspection
    a_ok, a_msg = validate_audio(audio_path, ffprobe_bin=FFPROBE)
    if not a_ok:
        logger.error(f"[QA REJECTED] Audio check failed: {a_msg}")
        return None
    logger.info(f"✓ [QA PASSED] Audio: {a_msg}")

    # Step 3: Assemble video
    try:
        assemble_video(frames, audio_path, output_path)
    except Exception as e:
        logger.error(f"Video assembly failed: {e}")
        return None

    # QA Gate 4: Final Video Render Inspection
    v_ok, v_msg = validate_video_file(output_path, ffprobe_bin=FFPROBE, is_shorts=is_shorts)
    if not v_ok:
        logger.error(f"[QA REJECTED] Final video verification failed: {v_msg}")
        return None
    logger.info(f"✓ [QA PASSED] Final video: {v_msg}")

    # Step 4: Create high-converting cinematic thumbnail
    try:
        from engine import generate_cinematic_thumbnail
        first_frame = frames[0] if frames else None
        generate_cinematic_thumbnail(
            title=title,
            category=category,
            lang=lang,
            base_bg=first_frame,
            output_path=thumbnail_path,
            is_shorts=is_shorts,
        )
    except Exception as e:
        logger.warning(f"Thumbnail creation fallback: {e}")
        thumbnail_path = None

    # QA Gate 5: Thumbnail Inspection
    if thumbnail_path:
        t_ok, t_msg = validate_thumbnail(thumbnail_path, is_shorts=is_shorts)
        if not t_ok:
            logger.warning(f"[QA WARNING] Thumbnail check failed ({t_msg}). Proceeding without custom thumbnail.")
            thumbnail_path = None
        else:
            logger.info(f"✓ [QA PASSED] Thumbnail: {t_msg}")

    # Step 5: Upload
    video_id = None
    if not dry_run:
        try:
            video_id = upload_video(output_path, title, description, tags)
            if video_id and video_id != "QUOTA_EXCEEDED" and thumbnail_path:
                set_thumbnail(video_id, thumbnail_path)
            
            # Send immediate notification on successful upload
            if video_id and video_id != "QUOTA_EXCEEDED":
                try:
                    from notify import notify_upload_success
                    notify_upload_success(
                        video_title=title,
                        video_id=video_id,
                        category=category,
                        lang=lang,
                        is_shorts=is_shorts
                    )
                except Exception as ne:
                    logger.warning(f"Notification error: {ne}")
        except Exception as e:
            logger.error(f"Upload failed: {e}")
    else:
        logger.info(f"[DRY RUN] Would upload: {output_path}")

    _prune_outputs()

    status_str = "Published: " + video_id if (video_id and video_id != "QUOTA_EXCEEDED") else ("Quota Deferred" if video_id == "QUOTA_EXCEEDED" else "dry-run")
    logger.info(f"Completed: {title} [{lang}] | Status: {status_str}")

    _ledger_append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": category,
        "lang": lang,
        "title": title,
        "video_id": video_id,
        "video_path": output_path,
        "dry_run": dry_run,
    })

    logger.info(f"Finished: {title} [{lang}] | Video ID: {video_id or 'dry-run'}")

    return {
        "category": category,
        "lang": lang,
        "title": title,
        "video_path": output_path,
        "video_id": video_id,
        "thumbnail": thumbnail_path,
        "dry_run": dry_run,
    }


def run_scheduled_slot(dry_run: bool = False, slot: str | None = None) -> list[dict]:
    """
    Intelligently select 2-3 videos for the current time slot.
    Morning (~02:15 UTC / 07:45 IST): Devotional (Telugu), Weather (Telugu), Motivation (Hindi)
    Midday (~07:20 UTC / 12:50 IST): Facts (Telugu), Cooking (Hindi), Health (English)
    Afternoon (~12:15 UTC / 17:45 IST): Tech (English), News (Telugu), Crypto (English)
    Evening (~15:20 UTC / 20:50 IST): History (Telugu), Kids (English), Books (Hindi)
    """
    utc_hour = datetime.utcnow().hour
    if slot is None:
        if 0 <= utc_hour < 5:
            slot = "morning"
        elif 5 <= utc_hour < 10:
            slot = "midday"
        elif 10 <= utc_hour < 14:
            slot = "afternoon"
        else:
            slot = "evening"

    SCHEDULE_PLANS = {
        "morning":   [("devotional", "te"), ("weather", "te"), ("motivational", "hi")],
        "midday":    [("facts", "te"), ("cooking", "hi"), ("health", "en")],
        "afternoon": [("tech", "en"), ("news", "te"), ("crypto", "en")],
        "evening":   [("history", "te"), ("kids", "en"), ("books", "hi")],
    }

    plan = SCHEDULE_PLANS.get(slot, SCHEDULE_PLANS["morning"])
    logger.info(f"━━━ Running Scheduled Slot: {slot.upper()} (Plan: {plan}) ━━━")
    results = []
    for cat, lang in plan:
        res = run_category(cat, dry_run=dry_run, lang=lang)
        if res:
            results.append(res)
            if res.get("video_id") == "QUOTA_EXCEEDED":
                logger.warning("YouTube 24-hr limit reached. Halting slot uploads.")
                break
    published = sum(1 for r in results if r.get("video_id") and r["video_id"] != "QUOTA_EXCEEDED")
    logger.info(f"━━━ Slot {slot.upper()} Finished: {published} video(s) published ━━━")
    return results


def run_all_categories(dry_run: bool = False):
    """Run every category × every enabled language (14 categories × 3 = 42 videos)."""
    ALL_CATEGORIES = ["devotional", "weather", "news", "facts", "motivational",
                      "health", "language", "books", "cooking", "kids",
                      "tech", "crypto", "history", "gaming"]
    results = []
    quota_hit = False
    for cat in ALL_CATEGORIES:
        if quota_hit:
            break
        for lang in ENABLED_LANGUAGES:
            lang = lang.strip()
            logger.info(f"━━━ Running category: {cat} / lang: {lang} ━━━")
            result = run_category(cat, dry_run=dry_run, lang=lang)
            if result:
                results.append(result)
                if result.get("video_id") == "QUOTA_EXCEEDED":
                    logger.warning("Stopping remaining uploads for this run because YouTube 24-hour upload limit was reached.")
                    quota_hit = True
                    break
            else:
                logger.warning(f"⚠ Category '{cat}' [{lang}] did not produce a video")

    published = sum(1 for r in results if r.get("video_id") and r["video_id"] != "QUOTA_EXCEEDED")
    deferred = sum(1 for r in results if r.get("video_id") == "QUOTA_EXCEEDED")
    logger.info(f"━━━ Summary: {len(results)} generated | {published} published | {deferred} quota-deferred ━━━")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto YouTube Pipeline")
    parser.add_argument("--category", type=str, help="Run single category")
    parser.add_argument("--lang", type=str, default="en", help="Language code (en, hi, te)")
    parser.add_argument("--auto-slot", action="store_true", help="Run time-of-day category slot (2-3 videos)")
    parser.add_argument("--slot", type=str, choices=["morning", "midday", "afternoon", "evening"], help="Run specific broadcast slot")
    parser.add_argument("--run-all", action="store_true", help="Run all categories × all languages")
    parser.add_argument("--scheduler", action="store_true", help="Start cron scheduler")
    parser.add_argument("--test", action="store_true", help="Dry run (no uploads)")
    args = parser.parse_args()

    if args.category:
        r = run_category(args.category, dry_run=args.test, lang=args.lang)
        print(f"Result: {r}" if r else "No video generated")
        if not args.test and (not r or not r.get("video_id") or r.get("video_id") == "QUOTA_EXCEEDED"):
            sys.exit(1)
    elif args.auto_slot or args.slot:
        results = run_scheduled_slot(dry_run=args.test, slot=args.slot)
        published = sum(1 for r in results if r.get("video_id") and r["video_id"] != "QUOTA_EXCEEDED")
        print(f"Slot run completed: {len(results)} generated, {published} published")
        if not args.test and published == 0:
            sys.exit(1)
    elif args.run_all:
        results = run_all_categories(dry_run=args.test)
        published = sum(1 for r in results if r.get("video_id") and r["video_id"] != "QUOTA_EXCEEDED")
        print(f"Generated {len(results)} video(s), Published {published} video(s)")
        if not args.test and published == 0:
            sys.exit(1)
    elif args.scheduler:
        from scheduler import start_scheduler
        start_scheduler(test_mode=args.test)
    else:
        parser.print_help()
