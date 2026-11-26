"""
OmniPulse Daily — Quality Assurance & Self-Healing Feedback Loop
Inspects every asset before publishing. If any defect is detected, triggers
intelligent self-healing auto-corrections to guarantee top-tier production quality.
"""
import os
import re
import subprocess
from PIL import Image, ImageStat
from logger import get_logger

logger = get_logger("validator")

FORBIDDEN_KEYWORDS = [
    "automated", "auto-generated", "bot", "ai pipeline", "gpt",
    "chatgpt", "deepseek", "synthetic", "openai", "claude", "gemini"
]


def heal_content_metadata(content: dict, lang: str = "en") -> dict:
    """Auto-heal content metadata: fix title length, ensure #Shorts tag, sanitize forbidden words."""
    title = content.get("title", "OmniPulse Daily Insight").strip()
    script_lines = content.get("script_lines", [])

    # 1. Sanitize forbidden words
    for kw in FORBIDDEN_KEYWORDS:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        title = pattern.sub("", title)
        script_lines = [pattern.sub("", line) for line in script_lines]

    # Clean double spaces
    title = re.sub(r"\s+", " ", title).strip()

    # 2. Ensure #Shorts tag and proper length (<= 95 chars)
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title[:80].strip()} #Shorts"
    elif len(title) > 95:
        # Title has #Shorts but is too long
        title = f"{title[:80].strip()} #Shorts"

    content["title"] = title
    content["script_lines"] = script_lines
    content["full_script"] = " ".join(script_lines)
    logger.info(f"✓ [SELF-HEALED] Content sanitized & formatted: {title}")
    return content


def validate_content_metadata(content: dict, lang: str = "en") -> tuple[bool, str]:
    """Validate title, script, and language integrity."""
    title = content.get("title", "").strip()
    script_lines = content.get("script_lines", [])
    full_script = content.get("full_script", "").strip()

    if not (10 <= len(title) <= 100):
        return False, f"Title length invalid ({len(title)} chars)."

    if "#Shorts" not in title and "#shorts" not in title:
        return False, "Title is missing #Shorts tag."

    for kw in FORBIDDEN_KEYWORDS:
        if kw in title.lower() or kw in full_script.lower():
            return False, f"Forbidden keyword detected: '{kw}'."

    if not (2 <= len(script_lines) <= 12):
        return False, f"Invalid script line count: {len(script_lines)}."

    if lang == "te":
        telugu_chars = sum(1 for c in full_script if 0x0C00 <= ord(c) <= 0x0C7F)
        if telugu_chars < 10:
            return False, f"Telugu content failed language check: only {telugu_chars} Telugu glyphs."
    elif lang == "hi":
        hindi_chars = sum(1 for c in full_script if 0x0900 <= ord(c) <= 0x097F)
        if hindi_chars < 10:
            return False, f"Hindi content failed language check: only {hindi_chars} Devanagari glyphs."

    return True, "Content metadata verified."


def validate_audio(audio_path: str, ffprobe_bin: str = "ffprobe") -> tuple[bool, str, float]:
    """Validate voiceover audio file existence, duration, and stream presence."""
    if not os.path.exists(audio_path):
        return False, f"Audio file missing: {audio_path}", 0.0

    size_kb = os.path.getsize(audio_path) / 1024
    if size_kb < 15:
        return False, f"Audio file suspiciously small: {size_kb:.1f} KB.", 0.0

    cmd = [
        ffprobe_bin, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(proc.stdout.strip())
        if dur < 10.0:
            return False, f"Audio duration too short: {dur:.1f}s (min 10s).", dur
        if dur > 59.5:
            return False, f"Audio duration exceeds YouTube Shorts 60s limit: {dur:.1f}s.", dur
    except Exception as e:
        return False, f"Failed to probe audio duration: {e}", 0.0

    return True, f"Audio verified ({dur:.1f}s).", dur


def validate_frame(frame_path: str, expected_w: int = 1080, expected_h: int = 1920) -> tuple[bool, str]:
    """Inspect an individual video frame for dimensions, corruption, and visual quality."""
    if not os.path.exists(frame_path):
        return False, f"Frame file missing: {frame_path}"

    try:
        with Image.open(frame_path) as img:
            w, h = img.size
            if (w, h) != (expected_w, expected_h):
                return False, f"Frame dimensions mismatch: {w}x{h}, expected {expected_w}x{expected_h}."

            stat = ImageStat.Stat(img)
            if max(stat.var) < 20.0:
                return False, f"Frame appears completely flat or blank (variance: {max(stat.var):.1f})."
    except Exception as e:
        return False, f"Corrupt image file: {e}"

    return True, "Frame verified."


def validate_thumbnail(thumb_path: str, is_shorts: bool = True) -> tuple[bool, str]:
    """Validate thumbnail file existence, resolution, and visual density."""
    if not thumb_path or not os.path.exists(thumb_path):
        return False, f"Thumbnail file missing: {thumb_path}"

    expected_w = 1080 if is_shorts else 1280
    expected_h = 1920 if is_shorts else 720

    try:
        with Image.open(thumb_path) as img:
            w, h = img.size
            if (w, h) != (expected_w, expected_h):
                return False, f"Thumbnail dimensions mismatch: {w}x{h}, expected {expected_w}x{expected_h}."

            stat = ImageStat.Stat(img)
            if max(stat.var) < 30.0:
                return False, f"Thumbnail appears blank (variance: {max(stat.var):.1f})."
    except Exception as e:
        return False, f"Thumbnail image corrupt: {e}"

    size_kb = os.path.getsize(thumb_path) / 1024
    if size_kb < 30:
        return False, f"Thumbnail file too small: {size_kb:.1f} KB."

    return True, f"Thumbnail verified ({size_kb:.1f} KB)."


def validate_video_file(video_path: str, ffprobe_bin: str = "ffprobe", is_shorts: bool = True) -> tuple[bool, str]:
    """Verify final rendered video file streams, duration, and resolution before YouTube upload."""
    if not os.path.exists(video_path):
        return False, f"Video file missing: {video_path}"

    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    if size_mb < 0.2:
        return False, f"Video file too small: {size_mb:.2f} MB."

    cmd = [
        ffprobe_bin, "-v", "error",
        "-show_entries", "stream=codec_type,width,height:format=duration",
        "-of", "json",
        video_path
    ]
    try:
        import json
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
        streams = data.get("streams", [])
        types = [s.get("codec_type") for s in streams]

        if "video" not in types:
            return False, "Rendered video has no video stream."
        if "audio" not in types:
            return False, "Rendered video has no audio stream."

        video_stream = next(s for s in streams if s.get("codec_type") == "video")
        vw, vh = video_stream.get("width"), video_stream.get("height")
        exp_w = 1080 if is_shorts else 1280
        exp_h = 1920 if is_shorts else 720
        if (vw, vh) != (exp_w, exp_h):
            return False, f"Rendered video resolution mismatch: {vw}x{vh}, expected {exp_w}x{exp_h}."

        dur = float(data.get("format", {}).get("duration", 0))
        if dur < 10.0 or dur > 60.0:
            return False, f"Rendered video duration invalid: {dur:.1f}s."

    except Exception as e:
        return False, f"Failed to probe video integrity: {e}"

    return True, f"Video file verified ({size_mb:.1f} MB, {dur:.1f}s, {vw}x{vh})."
