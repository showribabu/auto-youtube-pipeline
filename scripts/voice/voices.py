"""
voices.py - Natural Multilingual Neural Voice Map for OmniPulse Daily
"""

VOICE_MAP = {
    # English Neural
    "en": "en-US-ChristopherNeural",
    "en_male": "en-US-ChristopherNeural",
    "en_female": "en-US-JennyNeural",
    "en_energetic": "en-US-GuyNeural",
    
    # Telugu Neural
    "te": "te-IN-MohanNeural",
    "te_male": "te-IN-MohanNeural",
    "te_female": "te-IN-ShrutiNeural",
    
    # Hindi Neural
    "hi": "hi-IN-MadhurNeural",
    "hi_male": "hi-IN-MadhurNeural",
    "hi_female": "hi-IN-SwaraNeural",
}


def get_voice(lang: str = "en", gender: str = "male") -> str:
    """Return the optimal natural neural voice for language and gender."""
    key = f"{lang}_{gender}"
    return VOICE_MAP.get(key, VOICE_MAP.get(lang, "en-US-ChristopherNeural"))
