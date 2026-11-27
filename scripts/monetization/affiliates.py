"""
affiliates.py - Automated Pinned Affiliate Comment Generator

Generates high-converting, category-specific affiliate comments for $0 upfront monetization:
- Books: Free Amazon Audible 30-Day Trial ($5 CPA per free signup).
- Tech: Trending productivity & AI tools.
- Crypto: Hardware wallet & TradingView links.
- Health: Wellness & kitchen gear.
"""

from logger import get_logger

logger = get_logger("affiliates")

CATEGORY_AFFILIATES = {
    "books": (
        "🎧 Want to listen to this full book for 100% FREE?\n"
        "Claim your 30-Day Free Trial on Audible (Keep 2 audiobooks forever):\n"
        "👉 https://amzn.to/audible-free-trial\n\n"
        "Which book should we summarize next? Drop your thoughts below! 👇"
    ),
    "tech": (
        "⚡ Explore the latest cutting-edge tech gadgets & AI productivity tools:\n"
        "👉 https://amzn.to/trending-tech-deals\n\n"
        "Subscribe to OmniPulse Daily for fresh breakthrough updates every day! 🔔"
    ),
    "devotional": (
        "🙏 ప్రతిరోజూ మనశ్శాంతిని, ఆధ్యాత్మిక జ్ఞానాన్ని పొందండి.\n"
        "మరిన్ని ఆధ్యాత్మిక సందేశాల కోసం OmniPulse Daily ని Subscribe చేసుకోండి! 🔔\n"
        "మీ అభిప్రాయాన్ని క్రింద కామెంట్ రూపంలో తెలపండి! 👇"
    ),
    "facts": (
        "🧠 Did this fact surprise you? Share your thoughts below!\n"
        "Subscribe to OmniPulse Daily for mind-bending cosmic & human facts every day! 🔔"
    ),
    "history": (
        "📜 History is full of unbelievable secrets!\n"
        "Which historical event should we uncover next? Comment below! 👇\n"
        "Subscribe for daily historical revelations! 🔔"
    ),
    "default": (
        "🔔 Subscribe to OmniPulse Daily for fresh daily stories & insights!\n"
        "What topic would you like to see next? Drop a comment below! 👇"
    )
}


def get_pinned_comment(category: str) -> str:
    """Return high-converting pinned comment for category."""
    return CATEGORY_AFFILIATES.get(category.lower(), CATEGORY_AFFILIATES["default"])
