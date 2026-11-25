import asyncio
import edge_tts
import uuid
import os
from config import CACHE_DIR
from logger import get_logger
logger = get_logger("audio")

# Map friendly aliases to actual Edge TTS voice names
VOICE_MAP = {
    # English
    "default_female": "en-US-JennyNeural",
    "default_male": "en-US-GuyNeural",
    "kids_female": "en-US-JennyNeural",
    "kids_male": "en-US-JackNeural",
    # Hindi
    "hi_female": "hi-IN-SwaraNeural",
    "hi_male": "hi-IN-MadhurNeural",
    "hindi_female": "hi-IN-SwaraNeural",
    "hindi_male": "hi-IN-MadhurNeural",
    # Telugu
    "te_female": "te-IN-ShrutiNeural",
    "te_male": "te-IN-MohanNeural",
    "telugu_female": "te-IN-ShrutiNeural",
    "telugu_male": "te-IN-MohanNeural",
}

async def generate_audio(
    text: str,
    voice: str = "default_female",
    rate: str = "+0%",
    output_path: str | None = None,
) -> str:
    # If voice is already an explicit Edge TTS voice name (like 'te-IN-MohanNeural')
    if "-" in voice and ("Neural" in voice or "Standard" in voice):
        voicename = voice
    else:
        voicename = VOICE_MAP.get(voice, "en-US-SaraNeural")

    out = output_path or os.path.join(
        CACHE_DIR,
        f"audio_{uuid.uuid4().hex[:8]}.mp3"
    )
    communicate = edge_tts.Communicate(text, voicename, rate=rate)
    await communicate.save(out)
    logger.info(f"Audio generated ({voice} -> {voicename}): {out}")
    return out


def run_audio_sync(text: str, voice: str = "default_female",
                   rate: str = "+0%", output_path: str | None = None) -> str:
    return asyncio.run(generate_audio(text, voice, rate, output_path))
