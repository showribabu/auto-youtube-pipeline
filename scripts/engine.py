import os
import subprocess
import tempfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import (
    OUTPUT_WIDTH, OUTPUT_HEIGHT, OUTPUT_FPS, DEFAULT_DURATION,
    FFMPEG, FFPROBE, CACHE_DIR, ASSETS_DIR
)
from logger import get_logger
logger = get_logger("engine")

def get_font(size: int, text: str = ""):
    # Detect Indic script for guaranteed character rendering
    has_telugu = any(0x0C00 <= ord(c) <= 0x0C7F for c in text)
    has_hindi = any(0x0900 <= ord(c) <= 0x097F for c in text)

    candidates = []
    if has_telugu:
        candidates.append(os.path.join(ASSETS_DIR, "fonts", "NotoSansTelugu.ttf"))
        candidates.append("C:/Windows/Fonts/Nirmala.ttc")
    elif has_hindi:
        candidates.append(os.path.join(ASSETS_DIR, "fonts", "NotoSansDevanagari.ttf"))
        candidates.append("C:/Windows/Fonts/Nirmala.ttc")

    candidates.extend([
        os.path.join(ASSETS_DIR, "fonts", "NotoSansTelugu.ttf"),
        os.path.join(ASSETS_DIR, "fonts", "NotoSansDevanagari.ttf"),
        "C:/Windows/Fonts/Nirmala.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/lohit-telugu/Lohit-Telugu.ttf",
        "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
        os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans.ttf"),
        os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans-Bold.ttf"),
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ])
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_title_card(
    title: str,
    category: str,
    subtitle: str = "",
    width: int = OUTPUT_WIDTH,
    height: int = OUTPUT_HEIGHT,
    *,
    bg_color: tuple = (20, 20, 60),
    accent_color: tuple = (255, 180, 0),
    output_path: str | None = None,
) -> str:
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    margin = int(width * 0.08)
    box_w = width - margin * 2

    # Category badge
    draw.rounded_rectangle(
        [margin, int(height * 0.06),
         margin + int(len(category) * 0.5 * 28), int(height * 0.06) + 44],
        radius=8, fill=accent_color,
    )
    font_sm = get_font(20)
    draw.text((margin + 10, int(height * 0.06) + 6), category.upper(),
              fill=(0, 0, 0), font=font_sm)

    # Title (wrapped)
    font_title = get_font(int(width * 0.05))
    lines = _wrap_text(draw, title, font_title, box_w)
    title_y = int(height * 0.22)
    line_h = int(font_title.size * 1.3)
    for line in lines:
        x = margin + (box_w - sum(draw.textlength(l, font=font_title) for l in [line])) / 2
        draw.text((x, title_y), line, fill=(255, 255, 255), font=font_title)
        title_y += line_h

    # Subtitle
    if subtitle:
        font_sub = get_font(int(width * 0.028))
        sub_lines = _wrap_text(draw, subtitle, font_sub, box_w)
        sub_y = title_y + int(height * 0.06)
        for sl in sub_lines:
            draw.text((margin, sub_y), sl, fill=(200, 200, 220), font=font_sub)
            sub_y += int(font_sub.size * 1.4)

    # Bottom bar with date
    date_str = datetime.now().strftime("%B %d, %Y")
    font_date = get_font(int(width * 0.022))
    draw.rectangle([0, height - 50, width, height], fill=accent_color)
    dw = draw.textlength(date_str, font=font_date)
    draw.text(((width - dw) / 2, height - 40), date_str,
              fill=(255, 255, 255), font=font_date)

    out = output_path or os.path.join(CACHE_DIR, f"title_{datetime.now().timestamp():.0f}.png")
    img.save(out, "PNG")
    logger.info(f"Title card saved: {out}")
    return out


# Shorts categories default to vertical 9:16 (1080x1920) for viral reach
SHORTS_CATEGORIES = {
    "facts", "motivational", "health", "language", "cooking",
    "crypto", "tech", "history", "devotional"
}

def generate_frame_sequence(
    script_lines: list[str],
    category: str,
    duration_per_line: float = 4.0,
    output_dir: str | None = None,
    is_shorts: bool | None = None,
) -> list[str]:
    out_dir = output_dir or CACHE_DIR
    os.makedirs(out_dir, exist_ok=True)
    palette = _get_category_palette(category)
    frames = []

    if is_shorts is None:
        is_shorts = category in SHORTS_CATEGORIES

    width = 1080 if is_shorts else OUTPUT_WIDTH
    height = 1920 if is_shorts else OUTPUT_HEIGHT

    full_sample_text = " ".join(script_lines)
    font_big = get_font(int(width * (0.065 if is_shorts else 0.055)), text=full_sample_text)
    font_badge = get_font(int(width * (0.035 if is_shorts else 0.025)))
    ts = int(datetime.now().timestamp())

    for i, line in enumerate(script_lines):
        img = Image.new("RGB", (width, height), color=palette["bg"])
        draw = ImageDraw.Draw(img)
        cx = width // 2
        cy = height // 2
        bw = width - int(width * (0.12 if is_shorts else 0.16))

        # Top Category & Shorts Header Banner
        if is_shorts:
            header_text = f"⚡ {category.upper()} • DAILY SHORTS"
            hw = draw.textlength(header_text, font=font_badge)
            draw.rounded_rectangle([cx - hw/2 - 20, 140, cx + hw/2 + 20, 200], radius=16, fill=palette["accent"])
            draw.text((cx - hw / 2, 152), header_text, fill=(20, 20, 20), font=font_badge)

        wrap_lines = _wrap_text(draw, line.strip(), font_big, bw)
        total_h = len(wrap_lines) * int(font_big.size * 1.4)
        y_start = cy - total_h // 2

        for j, wl in enumerate(wrap_lines):
            dw = draw.textlength(wl, font=font_big)
            draw.text((cx - dw / 2, y_start + j * int(font_big.size * 1.4)),
                      wl, fill=palette["text"], font=font_big)

        dot_count = min(i + 1, 6)
        dot_spacing = 28
        dx_start = cx - (dot_count - 1) * dot_spacing / 2
        dot_y = height - (200 if is_shorts else 80)
        for d in range(dot_count):
            draw.ellipse([dx_start + d * dot_spacing, dot_y,
                          dx_start + d * dot_spacing + 12, dot_y + 12],
                         fill=palette["accent"])

        frame_path = os.path.join(out_dir, f"frame_{ts:06d}_{i:03d}.png")
        img.save(frame_path, "PNG")
        frames.append(frame_path)

    logger.info(f"Generated {len(frames)} frames ({width}x{height}, shorts={is_shorts}) in {out_dir}")
    return frames


def get_audio_duration(audio_path: str) -> float:
    """Retrieve exact duration of audio in seconds."""
    cmd = [
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return max(3.0, float(proc.stdout.strip()))
    except Exception as e:
        logger.warning(f"Could not probe audio duration ({e}), defaulting to 25.0s")
        return 25.0


def assemble_video(
    frames: list[str],
    audio_path: str,
    output_path: str,
    fps: int = OUTPUT_FPS,
) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")
    if not frames:
        raise ValueError("No frames provided to assemble_video")

    # Calculate exact duration each frame must display to match the audio
    audio_dur = get_audio_duration(audio_path)
    frame_dur = max(1.5, audio_dur / len(frames))
    logger.info(f"Assembling video: total audio {audio_dur:.2f}s, {len(frames)} frames @ {frame_dur:.2f}s per frame")

    # Build a file-list for FFmpeg concat demuxer
    safe_frames = [fp.replace("\\", "/") for fp in frames]

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        for fp in safe_frames:
            f.write(f"file '{fp}'\n")
            f.write(f"duration {frame_dur:.3f}\n")
        # FFmpeg concat demuxer requires the last file to be repeated at the end
        f.write(f"file '{safe_frames[-1]}'\n")
        temp_list = f.name

    video_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

    # Step 1: Render timed video stream from frames
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", temp_list,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an", video_path,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.unlink(temp_list)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg video encode failed: {proc.stderr.decode()}")

    # Step 2: Merge timed video with speech audio and ambient soothing background music
    audio_cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=44100",
        "-filter_complex",
        f"[2:a]volume=0.025,lowpass=f=350[bgm]; [1:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{audio_dur:.2f}",
        output_path,
    ]
    proc2 = subprocess.run(audio_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.unlink(video_path)
    if proc2.returncode != 0:
        logger.warning(f"BGM mix failed ({proc2.stderr.decode()[:100]}), falling back to direct audio merge")
        fallback_cmd = [
            FFMPEG, "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac",
            "-t", f"{audio_dur:.2f}",
            output_path,
        ]
        subprocess.run(fallback_cmd, check=True)

    logger.info(f"✓ Video successfully assembled: {output_path} (Duration: {audio_dur:.1f}s)")
    return output_path


def _wrap_text(draw: ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = f"{current} {w}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines or [text]


def _get_category_palette(cat: str) -> dict:
    palettes = {
        "kids":           {"bg": (40, 80, 180), "text": (255, 255, 240), "accent": (255, 220, 50)},
        "news":           {"bg": (20, 25, 40),  "text": (240, 240, 240), "accent": (220, 50, 50)},
        "weather":        {"bg": (30, 70, 120), "text": (255, 255, 255), "accent": (100, 200, 255)},
        "facts":          {"bg": (50, 30, 80),   "text": (255, 250, 230), "accent": (180, 100, 255)},
        "motivational":   {"bg": (30, 30, 30),   "text": (255, 240, 200), "accent": (255, 160, 50)},
        "tech":           {"bg": (15, 20, 35),   "text": (200, 230, 255), "accent": (0, 180, 220)},
        "crypto":         {"bg": (20, 15, 35),   "text": (230, 220, 255), "accent": (140, 80, 255)},
        "health":         {"bg": (20, 50, 30),   "text": (220, 255, 220), "accent": (80, 220, 100)},
        "history":        {"bg": (40, 30, 20),   "text": (255, 240, 210), "accent": (200, 150, 50)},
        "gaming":         {"bg": (10, 20, 10),   "text": (200, 255, 200), "accent": (0, 255, 100)},
        "language":       {"bg": (35, 20, 50),   "text": (240, 220, 255), "accent": (180, 100, 255)},
        "books":          {"bg": (45, 30, 15),   "text": (255, 245, 230), "accent": (220, 160, 50)},
        "cooking":        {"bg": (50, 20, 10),   "text": (255, 240, 220), "accent": (255, 120, 50)},
        "devotional":     {"bg": (32, 14, 8),    "text": (255, 248, 225), "accent": (255, 160, 20)},
    }
    return palettes.get(cat, palettes["facts"])
