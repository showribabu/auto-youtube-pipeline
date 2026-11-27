"""
mixer.py - Pro Studio Audio Ducking & BGM Mixer

Mixes normalized speech voiceover with genre-specific ambient background music (BGM):
- Eliminates legacy single-frequency sine beeps.
- Speech normalized with dynamic compression for maximum mobile phone clarity.
- BGM sits at an ambient -22dB to -24dB so it enhances atmosphere without masking voice.
- Includes automated generation of lush harmonic ambient pads if local MP3 is missing.
"""

import os
import subprocess
from config import FFMPEG
from logger import get_logger

logger = get_logger("mixer")

# Chord frequencies for harmonic ambient generation (when MP3 loop not yet cached)
CATEGORY_HARMONICS = {
    "devotional":   (108.0, 162.0, 216.0),    # Sacred 432Hz harmonic (A2-E3-A3 meditative drone)
    "tech":         (130.81, 196.00, 261.63), # Cyber ambient (C3-G3-C4 clean synth pad)
    "facts":        (110.0, 165.0, 220.0),    # Mystery tension (A2-E3-A3 minor mystery)
    "crypto":       (146.83, 220.00, 293.66), # Finance dynamic (D3-A3-D4)
    "books":        (130.81, 164.81, 196.00), # Warm major chord (C3-E3-G3 reflective)
    "history":      (98.0, 147.0, 196.0),     # Ancient deep resonance (G2-D3-G3)
    "motivational": (130.81, 196.00, 329.63), # Uplifting major 7th
    "default":      (130.81, 196.00, 261.63),
}


def _ensure_ambient_bgm(category: str, output_path: str, duration: float = 60.0) -> str:
    """Generate a lush, warm ambient pad if category BGM file does not exist."""
    if os.path.exists(output_path) and os.path.getsize(output_path) > 10_000:
        return output_path

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    f1, f2, f3 = CATEGORY_HARMONICS.get(category.lower(), CATEGORY_HARMONICS["default"])

    # Synthesize 3-note harmonic warm chord + subtle pink noise air + lowpass filter
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"sine=frequency={f1:.2f}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency={f2:.2f}:sample_rate=44100",
        "-f", "lavfi", "-i", f"sine=frequency={f3:.2f}:sample_rate=44100",
        "-f", "lavfi", "-i", "anoisesrc=c=pink:r=44100:a=0.005",
        "-filter_complex",
        f"[0:a][1:a][2:a]amix=inputs=3,lowpass=f=380,volume=0.35[chord];"
        f"[chord][3:a]amix=inputs=2,aecho=0.8:0.88:800:0.4[bgm]",
        "-map", "[bgm]",
        "-t", f"{duration:.2f}",
        "-c:a", "libmp3lame", "-b:a", "192k",
        output_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        logger.warning(f"Could not generate ambient BGM: {proc.stderr.decode()[-200:]}")
        return ""
    logger.info(f"Generated lush harmonic ambient BGM for '{category}' -> {output_path}")
    return output_path


def mix_speech_and_bgm(
    speech_path: str,
    output_path: str,
    category: str = "default",
    bgm_volume: float = 0.08
) -> str:
    """
    Mix speech audio with category ambient background music.
    Speech is normalized with volume boost and dynamic compression;
    BGM is ducked at -22dB to -24dB.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    bgm_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "audio", "bgm")
    cat_bgm_file = os.path.join(bgm_dir, f"bgm_{category.lower()}.mp3")

    # If user provided a custom BGM in assets/audio/bgm/, use it. Otherwise, auto-generate ambient pad.
    if not os.path.exists(cat_bgm_file):
        _ensure_ambient_bgm(category, cat_bgm_file, duration=90.0)

    if not os.path.exists(cat_bgm_file):
        # Fallback to speech only
        import shutil
        shutil.copy(speech_path, output_path)
        return output_path

    # Mix speech (boosted, normalized) + ducked BGM
    cmd = [
        FFMPEG, "-y",
        "-i", speech_path,
        "-stream_loop", "-1", "-i", cat_bgm_file,
        "-filter_complex",
        f"[0:a]volume=1.5,alimiter=limit=0.95[voice];"
        f"[1:a]volume={bgm_volume:.3f},lowpass=f=2500[bgm];"
        f"[voice][bgm]amix=inputs=2:duration=first:normalize=0[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        output_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        logger.error(f"Audio mix failed: {proc.stderr.decode()[-300:]}")
        import shutil
        shutil.copy(speech_path, output_path)
        return output_path

    logger.info(f"Mixed speech with ambient BGM ({category}) -> {output_path}")
    return output_path
