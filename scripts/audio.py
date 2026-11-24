import asyncio
import edge_tts
import uuid
import os
from config import CACHE_DIR
from logger import get_logger
logger = get_logger("audio")

async def generate_audio(
    text: str,
    voice: str = "default_female",
    rate: str = "+0%",
    output_path: str | None = None,
) -> str:
    # Map friendly names to actual Edge TTS voice names
    voice_map = {
        "default_female": "en-US-JennyNeural",
        "default_male": "en-US-GuyNeural",
        "kids_female": "en-US-JennyNeural",
        "kids_male": "en-US-JackNeural",
    }
    voicename = voice_map.get(voice, "en-US-SaraNeural")
    out = output_path or os.path.join(
        CACHE_DIR,
        f"audio_{uuid.uuid4().hex[:8]}.mp3"
    )
    communicate = edge_tts.Communicate(text, voicename, rate=rate)
    await communicate.save(out)
    logger.info(f"Audio generated ({voice}/{voicename}): {out}")
    return out


def run_audio_sync(text: str, voice: str = "default_female",
                   rate: str = "+0%", output_path: str | None = None) -> str:
    return asyncio.run(generate_audio(text, voice, rate, output_path))
