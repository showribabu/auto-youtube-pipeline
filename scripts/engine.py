import os
import io
import random
import urllib.request
import urllib.parse
import subprocess
import tempfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from config import (
    OUTPUT_WIDTH, OUTPUT_HEIGHT, OUTPUT_FPS, DEFAULT_DURATION,
    FFMPEG, FFPROBE, CACHE_DIR, ASSETS_DIR
)
from logger import get_logger
logger = get_logger("engine")

# Shorts categories default to vertical 9:16 (1080x1920)
SHORTS_CATEGORIES = {
    "facts", "motivational", "health", "language", "cooking",
    "crypto", "tech", "history", "devotional"
}

CATEGORY_VISUAL_PROMPTS = {
    "devotional":   "sacred golden lotus glowing temple diya lamps spiritual warm morning light cinematic",
    "kids":         "magical enchanted storybook forest cute friendly animals glowing fireflies pixar style",
    "tech":         "futuristic glowing artificial intelligence holographic neural network sleek dark blue",
    "crypto":       "glowing golden digital finance blockchain network futuristic trading dark aesthetic",
    "health":       "serene sunrise morning wellness healthy nature green mountains peaceful sunlight",
    "history":      "ancient classical architecture golden hour dramatic sky cinematic photography",
    "cooking":      "delicious gourmet meal plating steam rising warm rustic kitchen food photography",
    "books":        "cozy aesthetic library open book warm golden desk lamp bokeh background",
    "facts":        "breathtaking deep space nebula glowing stars earth horizon cosmos cinematic",
    "motivational": "person standing on mountain summit sunrise golden clouds triumph cinematic",
    "weather":      "dramatic colorful sky clouds sunbeams landscape atmospheric photography",
    "news":         "modern metropolitan city skyline twilight aerial photography sleek",
    "gaming":       "vibrant neon cyberpunk futuristic arena glowing lights ultra detailed",
    "language":     "classic vintage books calligraphy fountain pen warm aesthetic study desk",
}


def get_font(size: int, text: str = ""):
    """Select the best font supporting Telugu, Hindi (Devanagari), or Latin scripts."""
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
        os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans-Bold.ttf"),
        os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans.ttf"),
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ])
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _fetch_background_image(category: str, width: int, height: int, slide_idx: int) -> Image.Image | None:
    """Fetch a real, high-resolution topic-matched background image (Pollinations AI -> Picsum fallback)."""
    base_prompt = CATEGORY_VISUAL_PROMPTS.get(category, "cinematic dramatic nature landscape photography")
    seed = int(datetime.now().timestamp()) + slide_idx * 137

    # 1. Primary: Topic-specific visual via Pollinations
    encoded_prompt = urllib.parse.quote(f"{base_prompt}, scene {slide_idx + 1}, high quality 4k")
    urls = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&nologo=true",
        f"https://picsum.photos/{width}/{height}?random={seed}",
    ]

    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=18) as resp:
                raw = resp.read()
                if len(raw) > 8000:
                    img = Image.open(io.BytesIO(raw)).convert("RGB")
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    # Slightly darken image for clean text contrast
                    img = ImageEnhance.Brightness(img).enhance(0.68)
                    return img
        except Exception as e:
            logger.debug(f"Background fetch failed ({url[:45]}...): {e}")
            continue

    return None


def _draw_gradient_overlay(base_img: Image.Image) -> Image.Image:
    """Apply a cinematic vertical dark gradient vignette so text stands out clearly."""
    width, height = base_img.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top subtle vignette
    for y in range(0, int(height * 0.25)):
        alpha = int(140 * (1 - y / (height * 0.25)))
        draw.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))

    # Center-to-bottom rich vignette for captions
    start_y = int(height * 0.30)
    for y in range(start_y, height):
        progress = (y - start_y) / (height - start_y)
        alpha = int(170 * min(1.0, progress * 1.3))
        draw.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))

    combined = Image.alpha_composite(base_img.convert("RGBA"), overlay)
    return combined


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
    bg = _fetch_background_image(category, width, height, 0)
    if bg is None:
        bg = Image.new("RGB", (width, height), color=bg_color)
    img = _draw_gradient_overlay(bg).convert("RGB")
    draw = ImageDraw.Draw(img)

    margin = int(width * 0.08)
    box_w = width - margin * 2
    font_title = get_font(int(width * 0.055), text=title)
    lines = _wrap_text(draw, title, font_title, box_w)
    title_y = int(height * 0.35)
    line_h = int(font_title.size * 1.35)
    for line in lines:
        dw = draw.textlength(line, font=font_title)
        draw.text(((width - dw) / 2, title_y), line, fill=(255, 255, 255), font=font_title)
        title_y += line_h

    out = output_path or os.path.join(CACHE_DIR, f"title_{datetime.now().timestamp():.0f}.png")
    img.save(out, "PNG")
    logger.info(f"Title card saved: {out}")
    return out


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
    font_big = get_font(int(width * (0.056 if is_shorts else 0.048)), text=full_sample_text)
    font_brand = get_font(int(width * (0.030 if is_shorts else 0.022)))
    ts = int(datetime.now().timestamp())

    # Fetch up to 3 distinct real background images per video and cycle smoothly
    bg_pool = []
    num_unique_bgs = min(3, max(1, len(script_lines)))
    for b_idx in range(num_unique_bgs):
        bg = _fetch_background_image(category, width, height, b_idx)
        if bg is not None:
            bg_pool.append(bg)

    for i, line in enumerate(script_lines):
        if bg_pool:
            base_bg = bg_pool[i % len(bg_pool)].copy()
        else:
            base_bg = Image.new("RGB", (width, height), color=palette["bg"])

        rgba_img = _draw_gradient_overlay(base_bg)
        draw = ImageDraw.Draw(rgba_img, "RGBA")

        cx = width // 2
        cy = int(height * (0.58 if is_shorts else 0.55))
        bw = width - int(width * 0.14)

        # Clean subtle channel header watermark (NO "automated" or bot labels)
        brand_text = "OMNIPULSE DAILY"
        btw = draw.textlength(brand_text, font=font_brand)
        header_y = 110 if is_shorts else 40
        draw.rounded_rectangle(
            [cx - btw / 2 - 22, header_y - 8, cx + btw / 2 + 22, header_y + font_brand.size + 12],
            radius=20,
            fill=(15, 18, 28, 160),
            outline=(*palette["accent"], 200),
            width=2
        )
        draw.text((cx - btw / 2, header_y), brand_text, fill=palette["accent"], font=font_brand)

        # Wrap text and compute glassmorphic caption card dimensions
        wrap_lines = _wrap_text(draw, line.strip(), font_big, bw - 40)
        line_h = int(font_big.size * 1.42)
        total_h = len(wrap_lines) * line_h
        y_start = cy - total_h // 2

        card_pad_x = 36
        card_pad_y = 32
        card_x0 = int(width * 0.07) - 10
        card_x1 = width - int(width * 0.07) + 10
        card_y0 = y_start - card_pad_y
        card_y1 = y_start + total_h + card_pad_y

        # Semi-transparent glassmorphic card behind text
        draw.rounded_rectangle(
            [card_x0, card_y0, card_x1, card_y1],
            radius=28,
            fill=(10, 12, 22, 185),
            outline=(*palette["accent"], 140),
            width=3,
        )

        # Draw crisp shadowed typography
        for j, wl in enumerate(wrap_lines):
            dw = draw.textlength(wl, font=font_big)
            tx = cx - dw / 2
            ty = y_start + j * line_h
            # Subtle drop shadow
            draw.text((tx + 2, ty + 3), wl, fill=(0, 0, 0, 200), font=font_big)
            draw.text((tx, ty), wl, fill=(255, 255, 255, 255), font=font_big)

        # Sleek bottom progress bar
        bar_y = height - (150 if is_shorts else 50)
        bar_w = int(width * 0.72)
        bar_x0 = cx - bar_w // 2
        progress_ratio = (i + 1) / max(1, len(script_lines))
        draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + bar_w, bar_y + 10], radius=5, fill=(255, 255, 255, 60))
        draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + int(bar_w * progress_ratio), bar_y + 10], radius=5, fill=(*palette["accent"], 255))

        frame_path = os.path.join(out_dir, f"frame_{ts:06d}_{i:03d}.png")
        rgba_img.convert("RGB").save(frame_path, "PNG")
        frames.append(frame_path)

    logger.info(f"Generated {len(frames)} cinematic frames ({width}x{height}, real_bgs={len(bg_pool)}) in {out_dir}")
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

    audio_dur = get_audio_duration(audio_path)
    frame_dur = max(1.5, audio_dur / len(frames))
    logger.info(f"Assembling cinematic video: audio {audio_dur:.2f}s, {len(frames)} slides @ {frame_dur:.2f}s/slide")

    # Get target dimensions from first frame
    with Image.open(frames[0]) as im:
        w, h = im.size

    safe_frames = [fp.replace("\\", "/") for fp in frames]
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        for fp in safe_frames:
            f.write(f"file '{fp}'\n")
            f.write(f"duration {frame_dur:.3f}\n")
        f.write(f"file '{safe_frames[-1]}'\n")
        temp_list = f.name

    video_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

    # Step 1: Encode video with subtle gentle motion zoom effect (1.0 -> 1.04 smooth pulse)
    # Using scale + crop gentle zoompan or clean 25fps encoding
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", temp_list,
        "-vf", f"scale={w}:{h},format=yuv420p",
        "-r", "25",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-an", video_path,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.unlink(temp_list)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg video encode failed: {proc.stderr.decode()}")

    # Step 2: Merge video with speech audio and subtle harmonic background pad
    audio_cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=44100",
        "-filter_complex",
        "[2:a]volume=0.02,lowpass=f=350[bgm]; [1:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
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
        logger.warning(f"BGM mix fallback triggered: {proc2.stderr.decode()[:100]}")
        fallback_cmd = [
            FFMPEG, "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac",
            "-t", f"{audio_dur:.2f}",
            output_path,
        ]
        subprocess.run(fallback_cmd, check=True)

    logger.info(f"✓ Cinematic video assembled: {output_path} ({audio_dur:.1f}s)")
    return output_path


def _wrap_text(draw: ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = f"{current} {w}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
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
        "facts":          {"bg": (50, 30, 80),  "text": (255, 250, 230), "accent": (180, 100, 255)},
        "motivational":   {"bg": (30, 30, 30),  "text": (255, 240, 200), "accent": (255, 160, 50)},
        "tech":           {"bg": (15, 20, 35),  "text": (200, 230, 255), "accent": (0, 180, 220)},
        "crypto":         {"bg": (20, 15, 35),  "text": (230, 220, 255), "accent": (140, 80, 255)},
        "health":         {"bg": (20, 50, 30),  "text": (220, 255, 220), "accent": (80, 220, 100)},
        "history":        {"bg": (40, 30, 20),  "text": (255, 240, 210), "accent": (200, 150, 50)},
        "gaming":         {"bg": (10, 20, 10),  "text": (200, 255, 200), "accent": (0, 255, 100)},
        "language":       {"bg": (35, 20, 50),  "text": (240, 220, 255), "accent": (180, 100, 255)},
        "books":          {"bg": (45, 30, 15),  "text": (255, 245, 230), "accent": (220, 160, 50)},
        "cooking":        {"bg": (50, 20, 10),  "text": (255, 240, 220), "accent": (255, 120, 50)},
        "devotional":     {"bg": (32, 14, 8),   "text": (255, 248, 225), "accent": (255, 180, 40)},
    }
    return palettes.get(cat, palettes["facts"])
