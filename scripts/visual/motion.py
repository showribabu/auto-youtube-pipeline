"""
motion.py - 60fps Continuous Camera Motion & Scene Slicing Engine

Transforms high-resolution visual assets into cinematic, moving video clips
using smooth FFmpeg camera push-in physics (Ken Burns zoompan) and stitches them
with smooth crossfades every 2.5 to 3.5 seconds.
"""

import os
import subprocess
from config import FFMPEG
from logger import get_logger

logger = get_logger("motion")


def create_ken_burns_clip(
    image_path: str,
    duration: float,
    output_path: str,
    zoom_in: bool = True,
    fps: int = 30
) -> str:
    """
    Apply continuous cinematic camera push-in or pull-out zoom to a still image.
    Produces vertical 1080x1920 MP4 at specified FPS.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    total_frames = int(duration * fps) + 5

    # Smooth subtle zoom from 1.0 to 1.14
    if zoom_in:
        zoom_expr = "min(zoom+0.0012,1.14)"
    else:
        zoom_expr = "max(1.14-0.0012*on,1.0)"

    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:s=1080x1920:fps={fps}"
    )

    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", image_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-t", f"{duration:.2f}",
        output_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        logger.error(f"Ken Burns zoom failed: {proc.stderr.decode()[-300:]}")
        # Fallback to simple static loop if zoompan fails on rare image dimensions
        cmd_fallback = [
            FFMPEG, "-y",
            "-loop", "1", "-i", image_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-t", f"{duration:.2f}",
            output_path
        ]
        subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    logger.info(f"Created Ken Burns motion clip ({duration:.1f}s) -> {output_path}")
    return output_path


def concatenate_scenes_with_crossfade(
    scene_clips: list[str],
    output_path: str,
    crossfade_dur: float = 0.35,
    clip_dur: float = 3.0
) -> str:
    """
    Stitch multiple video clips with smooth crossfade (xfade) transitions.
    """
    if not scene_clips:
        raise ValueError("No scene clips provided")
    if len(scene_clips) == 1:
        import shutil
        shutil.copy(scene_clips[0], output_path)
        return output_path

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    in_args = []
    for c in scene_clips:
        in_args.extend(["-i", c])

    fc_parts = []
    prev = "[0:v]"
    for idx in range(1, len(scene_clips)):
        offset = idx * (clip_dur - crossfade_dur)
        nxt = f"[v{idx}]" if idx < len(scene_clips) - 1 else "[vout]"
        fc_parts.append(f"{prev}[{idx}:v]xfade=transition=fade:duration={crossfade_dur:.2f}:offset={offset:.2f}{nxt}")
        prev = nxt

    filter_complex = ";".join(fc_parts)
    cmd = [
        FFMPEG, "-y",
        *in_args,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        logger.warning(f"xfade failed: {proc.stderr.decode()[-300:]}. Falling back to concat.")
        # Fallback to concat demuxer
        list_file = output_path + ".txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for c in scene_clips:
                f.write(f"file '{os.path.abspath(c)}'\n")
        cmd_concat = [
            FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", output_path
        ]
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(list_file):
            os.remove(list_file)

    logger.info(f"Stitched {len(scene_clips)} motion scenes -> {output_path}")
    return output_path
