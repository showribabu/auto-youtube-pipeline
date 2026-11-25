import random
import urllib.request
import json
import re
from datetime import datetime
from config import SCHEDULES, MAX_VIDEOS_PER_DAY, RETRY_DELAY, MAX_RETRIES
from logger import get_logger
logger = get_logger("gaming")

GAMING_FEEDS = [
    "https://www.ign.com/rss",
    "https://www.gamespot.com/feeds/mashup/",
    "https://www.pcgamer.com/rss/",
]

FALLBACK_GAMING = [
    ("Major Game Release This Week", [
        "A highly anticipated AAA title launches this week across all platforms.",
        "Early reviews praise the graphics, storytelling, and innovative gameplay mechanics.",
        "The open world is 3x larger than the previous entry in the series.",
        "Pre-orders have already broken franchise records.",
    ]),
    ("Esports Tournament Breaks Viewership Records", [
        "The international championship finals drew 5 million concurrent viewers.",
        "Prize pool exceeds 40 million dollars — largest in esports history.",
        "Underdog team stages incredible comeback in grand finals.",
        "Esports continues its meteoric rise toward mainstream recognition.",
    ]),
    ("Next-Gen Console Sales Surpass 50 Million", [
        "Combined PS5 and Xbox Series X/S sales cross the 50 million milestone.",
        "Supply chain issues finally resolved — consoles readily available globally.",
        "Exclusive titles driving hardware adoption faster than previous generation.",
        "Cloud gaming services gain traction as complementary platform.",
    ]),
]


def fetch_gaming_headlines() -> list[dict]:
    for feed_url in GAMING_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "AutoYouTubePipeline/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            headlines = _parse_rss(raw)
            if headlines:
                logger.info(f"Fetched {len(headlines)} gaming headlines from {feed_url}")
                return [{"title": h, "source": feed_url} for h in headlines[:5]]
        except Exception as e:
            logger.warning(f"Gaming RSS fetch failed for {feed_url}: {e}")
    return []


def _parse_rss(xml: str) -> list[str]:
    results = []
    import re
    items = re.findall(r"<item[^>]*>(.*?)</item>", xml, re.DOTALL)
    for item in items[:5]:
        title = re.search(r"<title[^>]*>(.*?)</title>", item)
        if title:
            text = title.group(1).strip()
            text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text)
            if len(text) > 15:
                results.append(text)
    return results


def generate_gaming_content() -> dict:
    existing = fetch_gaming_headlines()
    if not existing:
        topic = random.choice(FALLBACK_GAMING)
        script_lines = list(topic[1])
        title = topic[0]
    else:
        headlines = [h["title"] for h in existing]
        script_lines = headlines + [
            f"This is your daily gaming update from {datetime.now().strftime('%B %d')}. Game on!"
        ]
        title = f"Daily Gaming News — {datetime.now().strftime('%b %d, %Y')}"

    description = (
        f"🎮 Daily Gaming News | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{' '.join(script_lines[:3])}\n\n"
        f"#Gaming #VideoGames #Esports #GamingNews #PS5 #Xbox #PCGaming"
    )
    tags = ["gaming", "video games", "esports", "gaming news",
            "ps5", "xbox", "pc gaming", "nintendo"]

    return {
        "category": "gaming",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+3%",
    }