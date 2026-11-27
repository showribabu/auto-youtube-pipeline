"""
synthesizer.py - Edge-TTS Speech Synthesis with Millisecond WordBoundary Streaming

Produces high-definition speech and captures exact start/end timestamps for every spoken word,
enabling true pro-grade kinetic subtitles.
"""

import asyncio
import edge_tts
import uuid
import os
from config import CACHE_DIR
from logger import get_logger

logger = get_logger("synthesizer")


async def _synthesize_async(
    text: str,
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+0%",
    output_path: str | None = None
) -> tuple[str, list[dict]]:
    """
    Stream audio to output_path while harvesting WordBoundary events.
    Returns: (audio_file_path, list_of_word_timings)
    """
    out_audio = output_path or os.path.join(CACHE_DIR, f"speech_{uuid.uuid4().hex[:8]}.mp3")
    os.makedirs(os.path.dirname(out_audio), exist_ok=True)

    # Use WordBoundary parameter for exact word timestamp streaming
    communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    word_timings = []

    with open(out_audio, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # offset and duration are in 100ns units -> divide by 10,000,000 for seconds
                start_sec = chunk["offset"] / 10_000_000.0
                dur_sec = chunk["duration"] / 10_000_000.0
                word_timings.append({
                    "word": chunk["text"],
                    "start": round(start_sec, 3),
                    "end": round(start_sec + dur_sec, 3)
                })

    logger.info(f"Synthesized {len(word_timings)} words with voice '{voice}' -> {out_audio}")
    return out_audio, word_timings


def generate_speech(
    text: str,
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+0%",
    output_path: str | None = None
) -> tuple[str, list[dict]]:
    """Synchronous wrapper for speech synthesis."""
    return asyncio.run(_synthesize_async(text, voice, rate, output_path))
