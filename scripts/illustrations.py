"""
illustrations.py - High-Retention Stylized Character & Thematic Visual Engine

Generates expressive cartoon/doodle characters, spiritual celestial art, and
thematic storytelling props for YouTube Shorts and thumbnails.
Inspired by top viral creators (Casually Explained, Psych2Go, MinutePhysics, Alex Hormozi).
"""

import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _draw_glowing_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color: tuple, steps: int = 6):
    """Draw a soft glowing aura around a center point."""
    r_step = radius // steps
    for i in range(steps, 0, -1):
        r = i * r_step
        alpha = int(color[3] * (1.0 - (i / steps) * 0.7))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))


def draw_doodle_avatar(
    category: str,
    mood: str = "curious",
    width: int = 1080,
    height: int = 1920,
    target_cy: int | None = None
) -> Image.Image:
    """
    Draw a clean, viral doodle character (Psych2Go / Casually Explained style).
    Includes expressive facial features, animated body pose, and floating thematic story props.
    """
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")

    cx = width // 2
    cy = target_cy if target_cy is not None else int(height * 0.40)
    scale = width / 1080.0

    # 1. Subtle glowing backlight behind avatar
    _draw_glowing_circle(d, cx, cy, int(280 * scale), (255, 220, 100, 45), steps=8)

    # 2. Dimensions
    head_r = int(75 * scale)
    head_cy = cy - int(90 * scale)
    body_len = int(140 * scale)
    limb_w = max(4, int(7 * scale))

    # White head circle with bold black outline
    head_box = [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r]
    d.ellipse(head_box, fill=(255, 255, 255, 255), outline=(20, 20, 30, 255), width=limb_w)

    # Expressive facial features based on mood
    eye_offset_x = int(24 * scale)
    eye_r = max(3, int(6 * scale))
    eye_y = head_cy - int(6 * scale)

    if mood in ("shocked", "mindblown"):
        # Big wide eyes with surprised O mouth
        d.ellipse([cx - eye_offset_x - 10, eye_y - 12, cx - eye_offset_x + 10, eye_y + 12], fill=(20, 20, 30, 255))
        d.ellipse([cx + eye_offset_x - 10, eye_y - 12, cx + eye_offset_x + 10, eye_y + 12], fill=(20, 20, 30, 255))
        # Pupils highlight
        d.ellipse([cx - eye_offset_x - 5, eye_y - 8, cx - eye_offset_x, eye_y - 3], fill=(255, 255, 255, 255))
        d.ellipse([cx + eye_offset_x - 5, eye_y - 8, cx + eye_offset_x, eye_y - 3], fill=(255, 255, 255, 255))
        # Surprised O mouth
        d.ellipse([cx - 14, head_cy + int(24 * scale), cx + 14, head_cy + int(48 * scale)], fill=(20, 20, 30, 255))
        # Glowing thought sparks above head
        for ang in [-50, -25, 0, 25, 50]:
            rad = math.radians(ang - 90)
            x1 = cx + int((head_r + 15) * math.cos(rad))
            y1 = head_cy + int((head_r + 15) * math.sin(rad))
            x2 = cx + int((head_r + 45) * math.cos(rad))
            y2 = head_cy + int((head_r + 45) * math.sin(rad))
            d.line([(x1, y1), (x2, y2)], fill=(255, 215, 0, 255), width=max(3, int(5 * scale)))
    elif mood in ("happy", "celebrating"):
        # Cute curved smiling eyes (^ ^)
        d.arc([cx - eye_offset_x - 12, eye_y - 10, cx - eye_offset_x + 12, eye_y + 10], start=200, end=340, fill=(20, 20, 30, 255), width=limb_w)
        d.arc([cx + eye_offset_x - 12, eye_y - 10, cx + eye_offset_x + 12, eye_y + 10], start=200, end=340, fill=(20, 20, 30, 255), width=limb_w)
        # Happy open smile with rosy cheeks
        d.chord([cx - 22, head_cy + int(12 * scale), cx + 22, head_cy + int(42 * scale)], start=0, end=180, fill=(220, 50, 50, 240), outline=(20, 20, 30, 255), width=limb_w)
        # Rosy blush cheeks
        d.ellipse([cx - 48, head_cy + int(10 * scale), cx - 28, head_cy + int(24 * scale)], fill=(255, 150, 160, 180))
        d.ellipse([cx + 28, head_cy + int(10 * scale), cx + 48, head_cy + int(24 * scale)], fill=(255, 150, 160, 180))
    else:
        # Default cute friendly doodle eyes
        d.ellipse([cx - eye_offset_x - eye_r, eye_y - eye_r, cx - eye_offset_x + eye_r, eye_y + eye_r], fill=(20, 20, 30, 255))
        d.ellipse([cx + eye_offset_x - eye_r, eye_y - eye_r, cx + eye_offset_x + eye_r, eye_y + eye_r], fill=(20, 20, 30, 255))
        # Eye catchlight
        d.ellipse([cx - eye_offset_x - 2, eye_y - 3, cx - eye_offset_x + 2, eye_y + 1], fill=(255, 255, 255, 255))
        d.ellipse([cx + eye_offset_x - 2, eye_y - 3, cx + eye_offset_x + 2, eye_y + 1], fill=(255, 255, 255, 255))
        # Gentle curved smile
        d.arc([cx - 20, head_cy + int(10 * scale), cx + 20, head_cy + int(36 * scale)], start=20, end=160, fill=(20, 20, 30, 255), width=limb_w)

    # 3. Body
    body_top_y = head_cy + head_r
    body_bot_y = body_top_y + body_len
    d.line([(cx, body_top_y), (cx, body_bot_y)], fill=(20, 20, 30, 255), width=limb_w)

    # 4. Arms & Poses
    shoulder_y = body_top_y + int(30 * scale)
    if mood in ("happy", "celebrating"):
        # Raised victory hands \o/
        d.line([(cx, shoulder_y), (cx - int(70 * scale), shoulder_y - int(60 * scale))], fill=(20, 20, 30, 255), width=limb_w)
        d.line([(cx, shoulder_y), (cx + int(70 * scale), shoulder_y - int(60 * scale))], fill=(20, 20, 30, 255), width=limb_w)
    elif mood in ("thinking", "curious"):
        # One hand on chin, one on hip
        d.line([(cx, shoulder_y), (cx - int(50 * scale), shoulder_y + int(20 * scale)), (cx - int(25 * scale), head_cy + int(35 * scale))], fill=(20, 20, 30, 255), width=limb_w)
        d.line([(cx, shoulder_y), (cx + int(60 * scale), shoulder_y + int(30 * scale)), (cx + int(30 * scale), body_bot_y - int(20 * scale))], fill=(20, 20, 30, 255), width=limb_w)
    else:
        # Welcoming open gesture
        d.line([(cx, shoulder_y), (cx - int(65 * scale), shoulder_y + int(45 * scale))], fill=(20, 20, 30, 255), width=limb_w)
        d.line([(cx, shoulder_y), (cx + int(65 * scale), shoulder_y + int(45 * scale))], fill=(20, 20, 30, 255), width=limb_w)

    # 5. Legs
    leg_len = int(120 * scale)
    d.line([(cx, body_bot_y), (cx - int(55 * scale), body_bot_y + leg_len)], fill=(20, 20, 30, 255), width=limb_w)
    d.line([(cx, body_bot_y), (cx + int(55 * scale), body_bot_y + leg_len)], fill=(20, 20, 30, 255), width=limb_w)

    # 6. Floating Thematic Story Props around character
    _draw_category_props(d, category, cx, cy, scale)

    return layer


def _draw_category_props(d: ImageDraw.ImageDraw, category: str, cx: int, cy: int, scale: float):
    """Draw crisp thematic story props around the doodle character."""
    limb_w = max(3, int(5 * scale))

    if category in ("facts", "psychology"):
        # Floating Lightbulb (Idea / Discovery) on upper-right
        bx, by = cx + int(150 * scale), cy - int(120 * scale)
        d.ellipse([bx - 26, by - 32, bx + 26, by + 16], fill=(255, 230, 70, 240), outline=(20, 20, 30, 255), width=limb_w)
        d.rectangle([bx - 14, by + 16, bx + 14, by + 30], fill=(180, 180, 190, 255), outline=(20, 20, 30, 255), width=limb_w)
        # Glow lines
        for ang in [-45, 0, 45]:
            rad = math.radians(ang - 90)
            d.line([(bx + int(36 * math.cos(rad)), by + int(36 * math.sin(rad))),
                    (bx + int(52 * math.cos(rad)), by + int(52 * math.sin(rad)))], fill=(255, 215, 0, 255), width=limb_w)

        # Question mark on upper-left
        qx, qy = cx - int(150 * scale), cy - int(90 * scale)
        d.text((qx, qy), "?", fill=(255, 80, 80, 255), stroke_width=limb_w, stroke_fill=(20, 20, 30, 255))

    elif category in ("motivational", "finance", "business"):
        # Golden Trophy on upper-right
        tx, ty = cx + int(140 * scale), cy - int(100 * scale)
        # Cup
        d.polygon([(tx - 24, ty - 22), (tx + 24, ty - 22), (tx + 16, ty + 12), (tx - 16, ty + 12)],
                  fill=(255, 215, 0, 255), outline=(20, 20, 30, 255), width=limb_w)
        # Handles
        d.arc([tx - 36, ty - 18, tx - 16, ty + 6], start=90, end=270, fill=(20, 20, 30, 255), width=limb_w)
        d.arc([tx + 16, ty - 18, tx + 36, ty + 6], start=270, end=90, fill=(20, 20, 30, 255), width=limb_w)
        # Base
        d.rectangle([tx - 18, ty + 16, tx + 18, ty + 26], fill=(200, 160, 0, 255), outline=(20, 20, 30, 255), width=limb_w)

        # Rocket / Upward Growth Arrow on upper-left
        rx, ry = cx - int(150 * scale), cy - int(100 * scale)
        d.line([(rx, ry + 30), (rx + 25, ry - 20)], fill=(0, 220, 100, 255), width=max(4, int(7 * scale)))
        d.polygon([(rx + 25, ry - 30), (rx + 10, ry - 10), (rx + 35, ry - 5)], fill=(0, 220, 100, 255))

    elif category in ("tech", "crypto"):
        # Laptop / Code Screen
        lx, ly = cx + int(145 * scale), cy - int(60 * scale)
        d.rectangle([lx - 32, ly - 24, lx + 32, ly + 14], fill=(40, 50, 75, 240), outline=(0, 230, 255, 255), width=limb_w)
        d.rectangle([lx - 40, ly + 14, lx + 40, ly + 22], fill=(160, 170, 190, 255), outline=(20, 20, 30, 255), width=limb_w)
        # Screen glow code lines
        d.line([(lx - 22, ly - 14), (lx + 5, ly - 14)], fill=(0, 255, 180, 255), width=3)
        d.line([(lx - 22, ly - 4), (lx + 18, ly - 4)], fill=(0, 230, 255, 255), width=3)
        d.line([(lx - 22, ly + 6), (lx - 2, ly + 6)], fill=(255, 220, 60, 255), width=3)


def draw_devotional_celestial_art(
    width: int = 1080,
    height: int = 1920,
    target_cy: int | None = None
) -> Image.Image:
    """
    Generate high-impact sacred spiritual artwork:
    - Glowing golden celestial sunburst / radiant halo
    - Meditating yogic silhouette (Padmasana)
    - Blooming sacred lotus flower at the base with soft gold & crimson glow
    - Radiant diya flame with divine light rings
    """
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")

    cx = width // 2
    cy = target_cy if target_cy is not None else int(height * 0.40)
    scale = width / 1080.0

    # 1. Multi-layered Radiant Sunburst / Halo
    max_r = int(320 * scale)
    for r in range(max_r, 40, -15):
        alpha = int(75 * (1.0 - r / max_r) ** 1.3)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 215, 60, alpha))

    # Divine light rays radiating outwards
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        r1 = int(140 * scale)
        r2 = int(280 * scale)
        x1 = cx + int(r1 * math.cos(rad))
        y1 = cy + int(r1 * math.sin(rad))
        x2 = cx + int(r2 * math.cos(rad))
        y2 = cy + int(r2 * math.sin(rad))
        d.line([(x1, y1), (x2, y2)], fill=(255, 235, 140, 110), width=max(2, int(4 * scale)))

    # 2. Sacred Meditating Silhouette (Padmasana)
    head_r = int(48 * scale)
    head_cy = cy - int(95 * scale)

    # Aura halo around head
    d.ellipse([cx - head_r - 18, head_cy - head_r - 18, cx + head_r + 18, head_cy + head_r + 18],
              outline=(255, 235, 120, 220), width=max(3, int(6 * scale)))

    # Head
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
              fill=(255, 235, 160, 245), outline=(180, 130, 20, 255), width=3)

    # Glowing third-eye / Tilak
    d.ellipse([cx - 4, head_cy - 12, cx + 4, head_cy - 2], fill=(255, 50, 40, 255))

    # Shoulders & Meditating Body
    shoulder_y = head_cy + head_r + int(10 * scale)
    body_base_y = cy + int(70 * scale)
    d.polygon([
        (cx, head_cy + head_r),
        (cx - int(75 * scale), shoulder_y + int(20 * scale)),
        (cx - int(120 * scale), body_base_y),
        (cx + int(120 * scale), body_base_y),
        (cx + int(75 * scale), shoulder_y + int(20 * scale))
    ], fill=(255, 215, 110, 230), outline=(180, 130, 20, 255), width=3)

    # Lotus cross-legged base
    d.ellipse([cx - int(140 * scale), body_base_y - int(30 * scale),
               cx + int(140 * scale), body_base_y + int(40 * scale)],
              fill=(255, 200, 90, 220), outline=(180, 130, 20, 255), width=3)

    # 3. Sacred Blooming Lotus Flower at the base
    lotus_y = body_base_y + int(35 * scale)
    # Petals spreading left & right
    for p_angle in [-50, -30, -12, 0, 12, 30, 50]:
        rad = math.radians(p_angle)
        p_len = int(75 * scale)
        px = cx + int(p_len * math.sin(rad))
        py = lotus_y - int(p_len * math.cos(rad))
        d.ellipse([px - 22, py - 35, px + 22, py + 35],
                  fill=(255, 140, 180, 180), outline=(255, 230, 240, 230), width=2)

    # 4. Floating Diya (Sacred Oil Lamp)
    diya_y = lotus_y + int(40 * scale)
    d.chord([cx - int(55 * scale), diya_y - int(20 * scale), cx + int(55 * scale), diya_y + int(25 * scale)],
            start=0, end=180, fill=(200, 120, 20, 255), outline=(255, 230, 100, 255), width=3)
    # Flame with glowing core
    flame_y = diya_y - int(24 * scale)
    d.ellipse([cx - 14, flame_y - 25, cx + 14, flame_y + 10], fill=(255, 140, 0, 240))
    d.ellipse([cx - 7, flame_y - 18, cx + 7, flame_y + 4], fill=(255, 255, 180, 255))

    return layer


def draw_weather_art(
    width: int = 1080,
    height: int = 1920,
    target_cy: int | None = None
) -> Image.Image:
    """
    Generate dynamic weather visuals:
    - Radiant golden sun
    - Dramatic puffy cloud
    - Neon lightning bolt & raindrops
    """
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")

    cx = width // 2
    cy = target_cy if target_cy is not None else int(height * 0.40)
    scale = width / 1080.0

    # 1. Golden Radiant Sun on upper-right
    sx, sy = cx + int(100 * scale), cy - int(90 * scale)
    sun_r = int(90 * scale)
    for r in range(sun_r + 50, sun_r, -8):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 200, 0, 40))
    d.ellipse([sx - sun_r, sy - sun_r, sx + sun_r, sy + sun_r], fill=(255, 215, 0, 255), outline=(255, 245, 150, 255), width=4)

    # Sun rays
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = sx + int((sun_r + 10) * math.cos(rad))
        y1 = sy + int((sun_r + 10) * math.sin(rad))
        x2 = sx + int((sun_r + 40) * math.cos(rad))
        y2 = sy + int((sun_r + 40) * math.sin(rad))
        d.line([(x1, y1), (x2, y2)], fill=(255, 230, 80, 240), width=max(4, int(7 * scale)))

    # 2. Dramatic Puffy 3D Cloud
    cloud_color = (245, 248, 255, 245)
    cloud_outline = (180, 195, 215, 255)
    cl_w = max(4, int(6 * scale))
    cl_x, cl_y = cx - int(60 * scale), cy + int(20 * scale)

    d.ellipse([cl_x - 110, cl_y - 45, cl_x + 30, cl_y + 55], fill=cloud_color, outline=cloud_outline, width=cl_w)
    d.ellipse([cl_x - 40, cl_y - 95, cl_x + 110, cl_y + 40], fill=cloud_color, outline=cloud_outline, width=cl_w)
    d.ellipse([cl_x + 30, cl_y - 50, cl_x + 160, cl_y + 55], fill=cloud_color, outline=cloud_outline, width=cl_w)
    d.rectangle([cl_x - 90, cl_y, cl_x + 140, cl_y + 55], fill=cloud_color)
    d.line([(cl_x - 100, cl_y + 55), (cl_x + 150, cl_y + 55)], fill=cloud_outline, width=cl_w)

    # 3. Glowing Lightning Bolt
    lx, ly = cx - int(10 * scale), cy + int(90 * scale)
    d.polygon([
        (lx, ly), (lx - 25, ly + 45), (lx - 5, ly + 45),
        (lx - 20, ly + 90), (lx + 20, ly + 35), (lx + 2, ly + 35)
    ], fill=(255, 240, 0, 255), outline=(255, 255, 255, 255), width=3)

    # 4. Raindrops
    for rx, ry in [(cx - 90, cy + 110), (cx + 60, cy + 120), (cx + 110, cy + 100)]:
        d.line([(rx, ry), (rx - 12, ry + 30)], fill=(80, 190, 255, 240), width=max(3, int(5 * scale)))

    return layer


def get_thematic_artwork(category: str, width: int = 1080, height: int = 1920, target_cy: int | None = None) -> Image.Image:
    """Master factory function to produce the appropriate high-retention character/artwork for a category."""
    cat = category.lower()
    if cat == "devotional":
        return draw_devotional_celestial_art(width, height, target_cy)
    elif cat == "weather":
        return draw_weather_art(width, height, target_cy)
    elif cat in ("motivational", "finance", "business"):
        return draw_doodle_avatar(cat, mood="celebrating", width=width, height=height, target_cy=target_cy)
    elif cat in ("tech", "crypto"):
        return draw_doodle_avatar(cat, mood="thinking", width=width, height=height, target_cy=target_cy)
    else:
        # Default high-retention doodle character
        return draw_doodle_avatar(cat, mood="curious", width=width, height=height, target_cy=target_cy)
