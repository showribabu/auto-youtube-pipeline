"""
Test pipeline without uploading — generates one video per category
and saves to output/ directory. Useful for verifying everything works.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OUTPUT_DIR, FFMPEG, FFPROBE
from logger import get_logger
from engine import generate_title_card, generate_frame_sequence, assemble_video
from audio import run_audio_sync

logger = get_logger("test")


def test_kids():
    """Test kids category video generation."""
    from categories.kids import generate_kids_content
    content = generate_kids_content()
    return content


def test_news():
    from categories.news import generate_news_content
    return generate_news_content()


def test_weather():
    from categories.weather import generate_weather_content
    return generate_weather_content()


def test_facts():
    from categories.facts import generate_fact_content
    return generate_fact_content()


def test_motivational():
    from categories.motivational import generate_motivational_content
    return generate_motivational_content()


def generate_single_video(content: dict, category: str) -> str:
    title = content["title"]
    script_lines = content["script_lines"]
    voice = content.get("voice", "default_female")
    rate = content.get("rate", "+0%")

    ts = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(OUTPUT_DIR, f"test_{category}")
    os.makedirs(out_dir, exist_ok=True)

    audio_path = os.path.join(out_dir, f"{ts}_audio.mp3")
    video_path = os.path.join(out_dir, f"{ts}_video.mp4")
    thumb_path = os.path.join(out_dir, f"{ts}_thumb.png")

    print(f"\n{'='*50}")
    print(f"Testing: {category} — '{title}'")
    print(f"{'='*50}")

    # Generate title card
    print("[1/4] Generating title card...")
    generate_title_card(title, category.upper(), bg_color=(20, 40, 80))

    # Generate frames
    print("[2/4] Generating frames...")
    frames = generate_frame_sequence(script_lines, category, duration_per_line=4.0, output_dir=out_dir)

    # Generate audio
    print("[3/4] Generating voiceover...")
    run_audio_sync(content["full_script"], voice=voice, rate=rate, output_path=audio_path)

    # Assemble video
    print("[4/4] Assembling video...")
    assemble_video(frames, audio_path, video_path)

    print(f"OK Complete! Video: {video_path}")
    return video_path


def main():
    print("Auto YouTube Pipeline — Test Mode")
    print("This will generate sample videos WITHOUT uploading to YouTube.\n")

    tests = [
        ("kids", test_kids),
        ("news", test_news),
        ("weather", test_weather),
        ("facts", test_facts),
        ("motivational", test_motivational),
    ]

    results = []
    for name, gen_fn in tests:
        try:
            content = gen_fn()
            path = generate_single_video(content, name)
            results.append((name, path, True))
        except Exception as e:
            logger.error(f"Test FAILED for {name}: {e}")
            traceback = __import__('traceback').format_exc()
            logger.error(traceback)
            results.append((name, None, False))

    print(f"\n{'='*50}")
    print("TEST RESULTS")
    print(f"{'='*50}")
    passed = sum(1 for _, _, ok in results if ok)
    for name, path, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n{passed}/{len(results)} categories passed")

    if passed == len(results):
        print("\nAll tests passed! Pipeline is ready.")
        print("\nTo enable uploads, configure your YouTube credentials:")
        print("  python scripts/setup_auth.py")
    else:
        print("\nSome tests failed. Check logs for details.")


if __name__ == "__main__":
    main()
