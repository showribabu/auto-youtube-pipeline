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
from config import OUTPUT_DIR, MAX_VIDEOS_PER_DAY, RETRY_DELAY, MAX_RETRIES, ENABLED_LANGUAGES
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
    from multilang import translate_content

    generators = {
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
        content = gen()
    except Exception as e:
        logger.error(f"Content generation failed for {category}: {e}")
        return None

    # Translate content for non-English languages
    content = translate_content(content, lang)

    title      = content["title"]
    script     = content["full_script"]
    script_lines = content["script_lines"]
    voice      = content.get("voice", "default_female")
    rate       = content.get("rate", "+0%")
    tags       = content["tags"]
    description= content["description"]

    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = _slug(title)
    if lang != "en":
        safe_title = f"{safe_title}_{lang}"
    out_dir = os.path.join(OUTPUT_DIR, f"{category}_{lang}")
    os.makedirs(out_dir, exist_ok=True)

    output_path     = os.path.join(out_dir, f"{ts_str}_{safe_title}.mp4")
    audio_path      = os.path.join(out_dir, f"{ts_str}_{safe_title}.mp3")
    thumbnail_path  = os.path.join(out_dir, f"{ts_str}_{safe_title}_thumb.jpg")

    logger.info(f"Generating video for: {title} [{category}]")

    # Step 1: Generate frames
    try:
        frames = generate_frame_sequence(script_lines, category, duration_per_line=5.0, output_dir=out_dir)
    except Exception as e:
        logger.error(f"Frame generation failed: {e}")
        return None

    # Step 2: Generate voiceover
    try:
        run_audio_sync(script, voice=voice, rate=rate, output_path=audio_path)
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        return None

    # Step 3: Assemble video
    try:
        assemble_video(frames, audio_path, output_path)
    except Exception as e:
        logger.error(f"Video assembly failed: {e}")
        return None

    # Step 4: Create thumbnail
    try:
        from PIL import Image, ImageDraw
        thumb = Image.new("RGB", (1280, 720), color=(30, 30, 60))
        draw = ImageDraw.Draw(thumb)
        font = get_font(48)
        lines = [title[:60], content["category"].upper()]
        y = 280
        for line in lines:
            dw = draw.textlength(line, font=font)
            draw.text(((1280 - dw) / 2, y), line, fill=(255, 255, 255), font=font)
            y += 70
        thumb.save(thumbnail_path, "JPEG", quality=90)
    except Exception as e:
        logger.warning(f"Thumbnail creation skipped: {e}")
        thumbnail_path = None

    # Step 5: Upload
    video_id = None
    if not dry_run:
        try:
            video_id = upload_video(output_path, title, description, tags)
            if video_id and thumbnail_path:
                set_thumbnail(video_id, thumbnail_path)
        except Exception as e:
            logger.error(f"Upload failed: {e}")
    else:
        logger.info(f"[DRY RUN] Would upload: {output_path}")

    _prune_outputs()

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


def run_all_categories(dry_run: bool = False):
    """Run every category × every enabled language (13 × 3 = 39 videos)."""
    ALL_CATEGORIES = ["kids", "news", "weather", "facts", "motivational",
                      "tech", "crypto", "health", "history", "gaming",
                      "language", "books", "cooking"]
    results = []
    for cat in ALL_CATEGORIES:
        for lang in ENABLED_LANGUAGES:
            lang = lang.strip()
            logger.info(f"━━━ Running category: {cat} / lang: {lang} ━━━")
            result = run_category(cat, dry_run=dry_run, lang=lang)
            if result:
                results.append(result)
            else:
                logger.warning(f"⚠ Category '{cat}' [{lang}] did not produce a video")
    logger.info(f"━━━ All done: {len(results)} / {len(ALL_CATEGORIES) * len(ENABLED_LANGUAGES)} videos produced ━━━")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto YouTube Pipeline")
    parser.add_argument("--category", type=str, help="Run single category")
    parser.add_argument("--lang", type=str, default="en", help="Language code (en, hi, te)")
    parser.add_argument("--run-all", action="store_true", help="Run all categories × all languages")
    parser.add_argument("--scheduler", action="store_true", help="Start cron scheduler")
    parser.add_argument("--test", action="store_true", help="Dry run (no uploads)")
    args = parser.parse_args()

    if args.category:
        r = run_category(args.category, dry_run=args.test, lang=args.lang)
        print(f"Result: {r}" if r else "No video generated")
    elif args.run_all:
        results = run_all_categories(dry_run=args.test)
        print(f"Generated {len(results)} video(s)")
    elif args.scheduler:
        from scheduler import start_scheduler
        start_scheduler(test_mode=args.test)
    else:
        parser.print_help()
