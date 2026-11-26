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

# All 14 categories default to vertical 9:16 Shorts (1080x1920) for maximum viral reach
SHORTS_CATEGORIES = {
    "devotional", "weather", "news", "facts", "motivational",
    "health", "language", "books", "cooking", "kids",
    "tech", "crypto", "history", "gaming"
}

# High-converting competitor-grade prompts with realistic human presenters, expressive characters & cinematic lighting
CATEGORY_VISUAL_PROMPTS = {
    "devotional":   "peaceful indian spiritual devotee with folded hands praying glowing temple diya lamps morning sunlight cinematic photography 8k",
    "weather":      "professional weather presenter standing next to futuristic holographic weather cloud map dramatic lighting cinematic 8k",
    "news":         "professional television news anchor sitting at high tech studio desk breaking news lighting 8k",
    "motivational": "triumphant inspiring person on mountain peak arms open towards glorious golden sunrise cinematic photography 8k",
    "facts":        "curious inquisitive person looking in wonder at glowing cosmic hologram planet secrets of universe cinematic 8k",
    "health":       "vibrant energetic young person smiling holding fresh organic green smoothie bright sunlit modern kitchen 8k",
    "cooking":      "passionate smiling chef plating a delicious steaming gourmet masterpiece warm rustic kitchen photography 8k",
    "tech":         "smart technology innovator interacting with glowing transparent artificial intelligence interface cyber 8k",
    "crypto":       "confident young digital finance analyst viewing holographic trading candlestick charts futuristic aesthetic 8k",
    "history":      "ancient majestic royal court with king and scholars golden classical architecture epic cinema still 8k",
    "kids":         "delightful friendly animated 3d pixar style talking animal character smiling warmly in magical colorful fairytale forest 8k",
    "books":        "thoughtful person immersed in reading an open leather book in cozy grand wooden library golden bokeh 8k",
    "gaming":       "enthusiastic young gamer wearing glowing headset celebrating victory futuristic neon esports room 8k",
    "language":     "warm friendly language tutor holding notebook smiling in modern sunlit creative classroom 8k",
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
    else:
        # Pure Latin / English text -> use bold Latin fonts first
        candidates.extend([
            os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans-Bold.ttf"),
            os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans.ttf"),
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ])

    candidates.extend([
        os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf", "DejaVuSans-Bold.ttf"),
        os.path.join(ASSETS_DIR, "fonts", "NotoSansTelugu.ttf"),
        os.path.join(ASSETS_DIR, "fonts", "NotoSansDevanagari.ttf"),
        "C:/Windows/Fonts/Nirmala.ttc",
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
                    # Crop bottom 6% to ensure zero corner watermarks, then resize cleanly
                    ow, oh = img.size
                    img = img.crop((0, 0, ow, int(oh * 0.94)))
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                    # Keep backgrounds vivid, bright, and lifelike
                    img = ImageEnhance.Brightness(img).enhance(0.86)
                    img = ImageEnhance.Contrast(img).enhance(1.12)
                    img = ImageEnhance.Color(img).enhance(1.15)
                    return img
        except Exception as e:
            logger.debug(f"Background fetch failed ({url[:45]}...): {e}")
            continue

    return None


def _draw_gradient_overlay(base_img: Image.Image) -> Image.Image:
    """Apply a clean bottom-weighted gradient vignette so vivid photography shines through."""
    width, height = base_img.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Very light top vignette for header readability
    for y in range(0, int(height * 0.16)):
        alpha = int(110 * (1 - y / (height * 0.16)))
        draw.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))

    # Smooth bottom vignette for captions & Subscribe CTA
    start_y = int(height * 0.45)
    for y in range(start_y, height):
        progress = (y - start_y) / (height - start_y)
        alpha = int(165 * min(1.0, progress * 1.2))
        draw.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))

    combined = Image.alpha_composite(base_img.convert("RGBA"), overlay)
    return combined


def _draw_subscribe_cta(draw: ImageDraw.ImageDraw, cx: int, y: int, font_cta, is_shorts: bool):
    """Draw a sleek YouTube-style Red SUBSCRIBE button + Golden Bell notification icon."""
    # Red Subscribe Pill
    sub_text = "SUBSCRIBE"
    stw = draw.textlength(sub_text, font=font_cta)
    btn_w = int(stw + 44)
    btn_h = int(font_cta.size + 22)
    bx0 = cx - btn_w // 2 - 28
    by0 = y

    # Red rounded button
    draw.rounded_rectangle([bx0, by0, bx0 + btn_w, by0 + btn_h], radius=btn_h // 2, fill=(230, 20, 20, 240))
    draw.text((bx0 + 22, by0 + 9), sub_text, fill=(255, 255, 255, 255), font=font_cta)

    # Golden Bell Notification Icon next to Subscribe button
    bell_cx = bx0 + btn_w + 34
    bell_cy = by0 + btn_h // 2
    # Bell dome & body
    draw.ellipse([bell_cx - 12, bell_cy - 13, bell_cx + 12, bell_cy + 7], fill=(255, 200, 40, 255))
    draw.polygon([(bell_cx - 14, bell_cy + 7), (bell_cx + 14, bell_cy + 7), (bell_cx + 17, bell_cy + 12), (bell_cx - 17, bell_cy + 12)], fill=(255, 200, 40, 255))
    # Bell clapper
    draw.ellipse([bell_cx - 4, bell_cy + 11, bell_cx + 4, bell_cy + 17], fill=(255, 220, 100, 255))


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


def generate_cinematic_thumbnail(
    title: str,
    category: str,
    lang: str = "en",
    base_bg=None,
    output_path: str | None = None,
    is_shorts: bool = True
) -> str:
    """
    Generate a high-converting, eye-catching YouTube thumbnail / cover image.
    Features:
    - High-contrast topic-matched photographic background with vignette darkening
    - Glowing top brand crest: ✦ OMNIPULSE DAILY ✦
    - Glassmorphic card container with category-accented outline
    - Bold, readable title typography in native Telugu/Hindi/Latin with ZERO box glyphs
    - Vibrant call-to-action badge: 🔴 WATCH NOW #SHORTS
    """
    width = 1080 if is_shorts else 1280
    height = 1920 if is_shorts else 720

    # 1. Base image
    img = None
    if isinstance(base_bg, str) and os.path.exists(base_bg):
        try:
            img = Image.open(base_bg).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
        except Exception:
            img = None
    elif isinstance(base_bg, Image.Image):
        img = base_bg.copy().resize((width, height), Image.Resampling.LANCZOS)

    if img is None:
        img = _fetch_background_image(category, width, height, 0)
    if img is None:
        palette = _get_category_palette(category)
        img = Image.new("RGB", (width, height), color=palette["bg"])

    # Enhance vividness
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Color(img).enhance(1.20)
    palette = _get_category_palette(category)
    accent = palette.get("accent", (255, 200, 40))

    # Dark gradient overlays for high text contrast
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)

    # Top gradient
    top_h = int(height * 0.22)
    for y in range(top_h):
        alpha = int(180 * (1 - y / top_h))
        d_overlay.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))

    # Center-bottom dark vignette for title card readability
    mid_y = int(height * 0.38)
    for y in range(mid_y, height):
        progress = (y - mid_y) / (height - mid_y)
        alpha = int(220 * min(1.0, progress * 1.3))
        d_overlay.line([(0, y), (width, y)], fill=(6, 8, 16, alpha))

    combined = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(combined, "RGBA")
    cx = width // 2

    # Brand header pill
    font_brand = get_font(int(width * (0.038 if is_shorts else 0.026)), text="OMNIPULSE DAILY")
    brand_text = "✦ OMNIPULSE DAILY ✦"
    btw = draw.textlength(brand_text, font=font_brand)
    b_y = int(height * (0.08 if is_shorts else 0.06))
    draw.rounded_rectangle(
        [cx - btw / 2 - 26, b_y - 10, cx + btw / 2 + 26, b_y + font_brand.size + 14],
        radius=22,
        fill=(12, 14, 24, 220),
        outline=(*accent, 255),
        width=3
    )
    draw.text((cx - btw / 2, b_y), brand_text, fill=accent, font=font_brand)

    # Main Headline
    font_title = get_font(int(width * (0.068 if is_shorts else 0.054)), text=title)
    max_w = width - int(width * 0.16)
    wrapped = _wrap_text(draw, title.strip(), font_title, max_w)
    wrapped = wrapped[:4]
    line_h = int(font_title.size * 1.38)
    total_h = len(wrapped) * line_h
    start_y = int(height * (0.46 if is_shorts else 0.36)) - total_h // 2

    # High-impact thumbnail text floating directly over cinematic photography — NO dark card box
    for i, wl in enumerate(wrapped):
        dw = draw.textlength(wl, font=font_title)
        tx = cx - dw / 2
        ty = start_y + i * line_h
        fill_col = (255, 235, 70, 255) if i == 0 else (255, 255, 255, 255)
        # Bold stroke outline ensures 100% legibility on any background without blocking the image
        draw.text(
            (tx, ty), wl,
            fill=fill_col,
            font=font_title,
            stroke_width=5,
            stroke_fill=(0, 0, 0, 245)
        )

    # Bottom CTA Badge
    font_cta = get_font(int(width * (0.040 if is_shorts else 0.028)), text="WATCH NOW #SHORTS")
    cta_text = "🔴 WATCH NOW #SHORTS" if is_shorts else "▶ WATCH FULL VIDEO"
    ctw = draw.textlength(cta_text, font=font_cta)
    cta_y = int(height * (0.84 if is_shorts else 0.82))
    draw.rounded_rectangle(
        [cx - ctw / 2 - 30, cta_y - 12, cx + ctw / 2 + 30, cta_y + font_cta.size + 16],
        radius=25,
        fill=(225, 25, 25, 240),
        outline=(255, 255, 255, 220),
        width=2
    )
    draw.text((cx - ctw / 2, cta_y), cta_text, fill=(255, 255, 255, 255), font=font_cta)

    out_file = output_path or os.path.join(CACHE_DIR, f"thumb_{int(datetime.now().timestamp())}.jpg")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    combined.convert("RGB").save(out_file, "JPEG", quality=95)
    logger.info(f"✓ High-converting cinematic thumbnail created: {out_file}")
    return out_file


def _draw_kinetic_line(draw: ImageDraw.ImageDraw, line: str, font, cx: int, ty: int):
    """Draw caption line with first 1-2 words in bright golden-yellow highlight, rest in white."""
    words = line.split(" ")
    if len(words) <= 1:
        dw = draw.textlength(line, font=font)
        draw.text((cx - dw / 2, ty), line, fill=(255, 255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0, 240))
        return

    highlight_count = min(2, len(words) // 2) or 1
    h_text = " ".join(words[:highlight_count]) + " "
    rest_text = " ".join(words[highlight_count:])

    total_w = draw.textlength(line, font=font)
    hw = draw.textlength(h_text, font=font)

    x0 = cx - total_w / 2
    # Draw highlighted word in vibrant gold
    draw.text((x0, ty), h_text, fill=(255, 225, 45, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0, 240))
    # Draw rest in pure white
    draw.text((x0 + hw, ty), rest_text, fill=(255, 255, 255, 255), font=font, stroke_width=4, stroke_fill=(0, 0, 0, 240))


def generate_frame_sequence(
    script_lines: list[str],
    category: str,
    duration_per_line: float = 4.0,
    output_dir: str | None = None,
    is_shorts: bool | None = None,
    title: str = "",
) -> list[str]:
    out_dir = output_dir or CACHE_DIR
    os.makedirs(out_dir, exist_ok=True)
    palette = _get_category_palette(category)
    frames = []

    if is_shorts is None:
        is_shorts = category in SHORTS_CATEGORIES

    width = 1080 if is_shorts else OUTPUT_WIDTH
    height = 1920 if is_shorts else OUTPUT_HEIGHT

    font_brand = get_font(int(width * (0.030 if is_shorts else 0.022)), text="OMNIPULSE DAILY")
    font_cta = get_font(int(width * (0.026 if is_shorts else 0.020)), text="SUBSCRIBE")
    ts = int(datetime.now().timestamp())
    cx = width // 2
    header_y = 110 if is_shorts else 40
    brand_text = "✦ OMNIPULSE DAILY ✦"
    btw = font_brand.size * 10

    # Fetch up to 3 distinct real background images per video and cycle smoothly
    bg_pool = []
    num_unique_bgs = min(3, max(1, len(script_lines)))
    for b_idx in range(num_unique_bgs):
        bg = _fetch_background_image(category, width, height, b_idx)
        if bg is not None:
            bg_pool.append(bg)

    # ─── Frame 0: Cinematic Intro Hook Slide ──────────────────
    if title:
        hook_bg = bg_pool[0].copy() if bg_pool else Image.new("RGB", (width, height), color=palette["bg"])
        rgba_hook = _draw_gradient_overlay(hook_bg)
        draw_hook = ImageDraw.Draw(rgba_hook, "RGBA")

        # Top Channel Crest
        draw_hook.rounded_rectangle(
            [cx - btw / 2 - 24, header_y - 10, cx + btw / 2 + 24, header_y + font_brand.size + 14],
            radius=22, fill=(12, 14, 24, 220), outline=(*palette["accent"], 255), width=3
        )
        draw_hook.text((cx - btw / 2, header_y), brand_text, fill=palette["accent"], font=font_brand)

        # Category Badge Pill
        cat_badge = f"⚡ {category.upper()} ⚡"
        font_badge = get_font(int(width * (0.034 if is_shorts else 0.024)), text=cat_badge)
        cbw = draw_hook.textlength(cat_badge, font=font_badge)
        badge_y = header_y + font_brand.size + 36
        draw_hook.rounded_rectangle(
            [cx - cbw / 2 - 18, badge_y - 6, cx + cbw / 2 + 18, badge_y + font_badge.size + 10],
            radius=16, fill=(220, 25, 25, 230), outline=(255, 255, 255, 200), width=2
        )
        draw_hook.text((cx - cbw / 2, badge_y), cat_badge, fill=(255, 255, 255, 255), font=font_badge)

        # Big Title Hook
        font_hook = get_font(int(width * (0.066 if is_shorts else 0.052)), text=title)
        hook_lines = _wrap_text(draw_hook, title.strip(), font_hook, width - int(width * 0.14))[:3]
        h_line_h = int(font_hook.size * 1.38)
        h_total_h = len(hook_lines) * h_line_h
        h_start_y = int(height * (0.50 if is_shorts else 0.45)) - h_total_h // 2

        for k, hl in enumerate(hook_lines):
            hl_w = draw_hook.textlength(hl, font=font_hook)
            draw_hook.text(
                (cx - hl_w / 2, h_start_y + k * h_line_h),
                hl,
                fill=(255, 235, 50, 255) if k == 0 else (255, 255, 255, 255),
                font=font_hook,
                stroke_width=5,
                stroke_fill=(0, 0, 0, 245)
            )

        # Bottom Swipe / Watch Hook
        cta_y = height - (210 if is_shorts else 95)
        _draw_subscribe_cta(draw_hook, cx, cta_y, font_cta, is_shorts)

        frame_0_path = os.path.join(out_dir, f"frame_{ts:06d}_000_intro.png")
        rgba_hook.convert("RGB").save(frame_0_path, "PNG")
        frames.append(frame_0_path)

    # ─── Frames 1 to N: Kinetic Narrative Slides ──────────────
    for i, line in enumerate(script_lines):
        if bg_pool:
            base_bg = bg_pool[(i + 1) % len(bg_pool)].copy()
        else:
            base_bg = Image.new("RGB", (width, height), color=palette["bg"])

        rgba_img = _draw_gradient_overlay(base_bg)
        draw = ImageDraw.Draw(rgba_img, "RGBA")

        cy = int(height * (0.58 if is_shorts else 0.55))
        bw = width - int(width * 0.14)

        # Channel watermark
        draw.rounded_rectangle(
            [cx - btw / 2 - 22, header_y - 8, cx + btw / 2 + 22, header_y + font_brand.size + 12],
            radius=20,
            fill=(15, 18, 28, 160),
            outline=(*palette["accent"], 200),
            width=2
        )
        draw.text((cx - btw / 2, header_y), brand_text, fill=palette["accent"], font=font_brand)

        # Kinetic captions floating over video
        font_line = get_font(int(width * (0.058 if is_shorts else 0.048)), text=line)
        wrap_lines = _wrap_text(draw, line.strip(), font_line, bw)
        line_h = int(font_line.size * 1.40)
        total_h = len(wrap_lines) * line_h
        y_start = cy - total_h // 2

        for j, wl in enumerate(wrap_lines):
            ty = y_start + j * line_h
            _draw_kinetic_line(draw, wl, font_line, cx, ty)

        # YouTube Subscribe + Bell CTA
        cta_y = height - (210 if is_shorts else 95)
        _draw_subscribe_cta(draw, cx, cta_y, font_cta, is_shorts)

        frame_path = os.path.join(out_dir, f"frame_{ts:06d}_{i+1:03d}.png")
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

    if len(frames) == 1:
        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-t", f"{audio_dur:.2f}", "-i", frames[0],
            "-i", audio_path,
            "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=44100",
            "-filter_complex",
            "[1:a]volume=1.6[voice];[2:a]volume=0.02,lowpass=f=350[bgm];[voice][bgm]amix=inputs=2:duration=first:normalize=0[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-pix_fmt", "yuv420p", "-r", "25",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-t", f"{audio_dur:.2f}",
            output_path,
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg single-slide encode failed: {proc.stderr.decode()[-400:]}")
        logger.info(f"✓ Cinematic video assembled: {output_path} ({audio_dur:.1f}s)")
        return output_path

    # Multi-slide smooth xfade crossfade transitions + LOUD normalized speech audio
    fade = min(0.5, frame_dur * 0.25)
    in_args = []
    for f_path in frames:
        in_args.extend(["-loop", "1", "-t", f"{frame_dur + fade:.3f}", "-i", f_path])

    fc_parts = []
    prev = "[0:v]"
    for idx in range(1, len(frames)):
        offset = idx * frame_dur - fade * 0.5
        nxt = f"[v{idx}]" if idx < len(frames) - 1 else "[vout]"
        fc_parts.append(f"{prev}[{idx}:v]xfade=transition=fade:duration={fade:.2f}:offset={offset:.2f}{nxt}")
        prev = nxt

    audio_idx = len(frames)
    bgm_idx = len(frames) + 1
    fc_parts.append(f"[{audio_idx}:a]volume=1.6[voice]")
    fc_parts.append(f"[{bgm_idx}:a]volume=0.02,lowpass=f=350[bgm]")
    fc_parts.append("[voice][bgm]amix=inputs=2:duration=first:normalize=0[aout]")

    filter_complex = ";".join(fc_parts)

    cmd = [
        FFMPEG, "-y",
        *in_args,
        "-i", audio_path,
        "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=44100",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-pix_fmt", "yuv420p",
        "-r", "25",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{audio_dur:.2f}",
        output_path,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg xfade encode failed: {proc.stderr.decode()[-400:]}")

    logger.info(f"✓ Cinematic video assembled with crossfades & boosted audio: {output_path} ({audio_dur:.1f}s)")
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
