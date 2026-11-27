"""
cover.py - Scroll-Stopping Frame 0 Hook Card Generator

Creates the 0.0s to 0.4s pattern-interrupt hook card that appears in the mobile Shorts feed:
- High-contrast visual backdrop with cinematic dark vignette.
- Top category pill with pure vector geometry.
- Giant, bold 3-to-4 word hook question in #FFDD00 gold with 5px solid black outline.
- Strictly keeps bottom 22% completely clear for YouTube Shorts native handle and UI.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import ASSETS_DIR
from logger import get_logger

logger = get_logger("cover")


def _get_font(size: int = 64) -> ImageFont.FreeTypeFont:
    """Return universal Nirmala font covering English, Telugu, and Hindi."""
    font_path = os.path.join(ASSETS_DIR, "fonts", "Nirmala.ttc")
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    # Fallback to system fonts
    for name in ["Nirmala UI", "Arial", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def generate_frame_0_hook_card(
    title: str,
    category: str,
    base_image_path: str | None,
    output_path: str,
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Generate Frame 0 Hook Card saved as PNG image.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Base image or cinematic dark background
    if base_image_path and os.path.exists(base_image_path):
        try:
            im = Image.open(base_image_path).convert("RGBA")
            im = im.resize((width, height), Image.Resampling.LANCZOS)
        except Exception:
            im = Image.new("RGBA", (width, height), (12, 14, 22, 255))
    else:
        im = Image.new("RGBA", (width, height), (12, 14, 22, 255))

    # Apply cinematic dark vignette so text pops
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_over = ImageDraw.Draw(overlay)
    # Top and center gradient overlay
    for y in range(height):
        # Heavy darkness in center and top
        alpha = int(140 + 80 * (1.0 - abs(y - height * 0.45) / (height * 0.5)))
        alpha = max(110, min(230, alpha))
        d_over.line([(0, y), (width, y)], fill=(8, 10, 18, alpha))
    im = Image.alpha_composite(im, overlay)

    draw = ImageDraw.Draw(im)

    # 1. Top Category Pill (y = 110)
    pill_text = category.upper()
    font_pill = _get_font(28)
    pill_bbox = draw.textbbox((0, 0), pill_text, font=font_pill)
    pw = pill_bbox[2] - pill_bbox[0] + 50
    ph = pill_bbox[3] - pill_bbox[1] + 20
    px = (width - pw) // 2
    py = 110

    # Draw pill background
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(18, 22, 34, 230), outline=(255, 221, 0, 180), width=2)
    # Draw pill text
    draw.text((px + 25, py + 8), pill_text, fill=(255, 221, 0), font=font_pill)

    # 2. Main Shocking Hook Headline (Centered at y = height * 0.40)
    # Extract short 3-5 word hook from title
    words = title.strip().split()
    if len(words) > 6:
        hook_lines = [" ".join(words[:4]), " ".join(words[4:8])]
    else:
        hook_lines = [title.strip()]

    font_hook = _get_font(68)
    start_y = int(height * 0.38)

    for idx, line in enumerate(hook_lines):
        line_bbox = draw.textbbox((0, 0), line, font=font_hook)
        lw = line_bbox[2] - line_bbox[0]
        lx = (width - lw) // 2
        ly = start_y + idx * 85

        # Draw 5px deep black stroke outline
        draw.text(
            (lx, ly),
            line,
            font=font_hook,
            fill=(255, 221, 0),  # Bright gold
            stroke_width=6,
            stroke_fill=(0, 0, 0)
        )

    # Convert to RGB and save
    im.convert("RGB").save(output_path, "PNG")
    logger.info(f"Generated Frame 0 Hook Card -> {output_path}")
    return output_path
