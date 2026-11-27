"""
ass_builder.py - Advanced SubStation Alpha (.ass) Kinetic Karaoke Subtitle Compiler

Generates broadcast-quality, word-synced animated subtitles:
- Centered 1-to-3 word rapid pops.
- Currently spoken word highlighted in vibrant #FFDD00 gold.
- Inactive words rendered in crisp #FFFFFF white.
- 5px solid black outline shadow for 100% legibility against any background.
- Strictly keeps subtitles in the safe middle zone (y=540 above bottom).
"""

import os
from logger import get_logger

logger = get_logger("ass_builder")


def _format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp: H:MM:SS.cs (centiseconds)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_kinetic_ass(
    word_timings: list[dict],
    output_path: str,
    font_name: str = "Nirmala UI",
    font_size: int = 58,
    words_per_cue: int = 2
) -> str:
    """
    Compile word timings into an .ass subtitle file with word-by-word gold pop highlighting.
    Returns: path to generated .ass file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kinetic,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,5,1,2,40,40,540,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    if not word_timings:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header)
        return output_path

    # Group words into chunks of words_per_cue (1 to 2 words per chunk for rapid kinetic pop)
    n = len(word_timings)
    i = 0
    while i < n:
        chunk = word_timings[i : i + words_per_cue]
        chunk_start = chunk[0]["start"]
        chunk_end = chunk[-1]["end"]
        # Look ahead to next chunk to eliminate awkward blank gaps between sentences
        next_start = word_timings[i + words_per_cue]["start"] if (i + words_per_cue < n) else (chunk_end + 0.4)

        # For each word in the chunk, create a dialogue line where that word is highlighted
        for active_idx, target_word in enumerate(chunk):
            w_start = target_word["start"]
            if active_idx < len(chunk) - 1:
                w_end = min(target_word["end"], chunk[active_idx + 1]["start"])
            else:
                # Hold the final word of the cue smoothly across pauses so the screen is never blank
                w_end = max(chunk_end, min(chunk_end + 0.65, next_start))

            # Ensure valid duration
            if w_end <= w_start:
                w_end = w_start + 0.18

            t_start_str = _format_ass_time(w_start)
            t_end_str = _format_ass_time(w_end)

            # Build line text with color tags
            # Gold #FFDD00 in ASS is &H0000DDFF&
            # White #FFFFFF in ASS is &H00FFFFFF&
            line_parts = []
            for j, w_obj in enumerate(chunk):
                w_text = w_obj["word"]
                if j == active_idx:
                    line_parts.append(f"{{\\c&H0000DDFF&}}{w_text}{{\\c&H00FFFFFF&}}")
                else:
                    line_parts.append(w_text)

            dialogue_text = " ".join(line_parts)
            events.append(f"Dialogue: 0,{t_start_str},{t_end_str},Kinetic,,0,0,0,,{dialogue_text}")

        i += words_per_cue

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    logger.info(f"Compiled pro kinetic .ass with {len(events)} cues -> {output_path}")
    return output_path
