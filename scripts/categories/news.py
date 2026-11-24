import json
import urllib.request
import os
from datetime import datetime
from config import SCHEDULES, MAX_VIDEOS_PER_DAY, RETRY_DELAY, MAX_RETRIES
from logger import get_logger
logger = get_logger("news")

NEWS_TOPICS = [
    ("Space Exploration Update", [
        "NASA continues to push the boundaries of space exploration with new missions planned for Mars.",
        "Scientists have discovered water vapor on distant exoplanets, raising hopes for finding extraterrestrial life.",
        "The James Webb Space Telescope has captured stunning new images of galaxy formation in the early universe.",
        "Space tourism is becoming more accessible as private companies develop reusable rockets.",
    ]),
    ("Technology Breakthroughs", [
        "Artificial intelligence is transforming healthcare with faster diagnoses and personalized treatment plans.",
        "Quantum computing milestones bring us closer to solving problems once thought impossible.",
        "New battery technology could double the range of electric vehicles within the next few years.",
        "5G networks are expanding globally, connecting remote areas and enabling smart city infrastructure.",
    ]),
    ("Climate & Environment", [
        "Renewable energy production has reached record highs worldwide, with solar power leading the charge.",
        "Scientists warn that ocean temperatures continue to rise, affecting marine ecosystems globally.",
        "Major cities are investing in green infrastructure to combat air pollution and urban heat.",
        "Deforestation rates in the Amazon have shown signs of declining thanks to stricter enforcement.",
    ]),
    ("World Economy & Innovation", [
        "Global markets see shifts as emerging economies drive new patterns of trade and investment.",
        "Cryptocurrency regulation evolves as governments seek balance between innovation and consumer protection.",
        "Sustainable investing grows as investors prioritize environmental and social responsibility.",
        "The gig economy continues to reshape how people work, with new platforms launching regularly.",
    ]),
    ("Science & Discovery", [
        "Researchers have developed a new material that could make electronics faster and more efficient.",
        "Mars rovers have found evidence of ancient microbial habitats beneath the planet's surface.",
        "Gene therapy advances offer hope for treating previously incurable genetic disorders.",
        "Ocean explorers have mapped previously unknown underwater mountain ranges in the Pacific.",
    ]),
]


def fetch_news_headlines() -> list[dict]:
    """Try RSS feeds; fall back to predefined topics."""
    feeds = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    ]
    for feed_url in feeds:
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "AutoYouTubePipeline/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            headlines = _parse_rss(raw)
            if headlines:
                logger.info(f"Fetched {len(headlines)} headlines from {feed_url}")
                return [{"title": h, "source": feed_url} for h in headlines[:5]]
        except Exception as e:
            logger.warning(f"RSS fetch failed for {feed_url}: {e}")
    return []


def _parse_rss(xml: str) -> list[str]:
    results = []
    import re
    items = re.findall(r"<item[^>]*>(.*?)</item>", xml, re.DOTALL)
    for item in items[:5]:
        title = re.search(r"<title[^>]*>(.*?)</title>", item)
        if title:
            text = title.group(1).strip()
            if len(text) > 10:
                results.append(text)
    return results


def generate_news_content() -> dict:
    existing = fetch_news_headlines()
    if not existing:
        topic = News_TOPICS[datetime.now().weekday() % len(NEWS_TOPICS)]
        script_lines = list(topic[1])
        title = topic[0]
    else:
        headlines = [h["title"] for h in existing]
        script_lines = headlines + [
            f"This is your daily news update from {datetime.now().strftime('%B %d')}. Stay informed."
        ]
        title = f"Daily News Roundup — {datetime.now().strftime('%b %d, %Y')}"

    description = (
        f"📰 Daily News Update | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{' '.join(script_lines[:3])}\n\n"
        f"#News #DailyNews #Headlines #CurrentEvents #WorldNews"
    )
    tags = ["news", "daily news", "headlines", "current events",
            "world news", "information", "update"]

    return {
        "category": "news",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+2%",
    }
