import random
import urllib.request
import json
import re
from datetime import datetime
from config import logger

TECH_FEEDS = [
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/technology-lab/rss/",
]

FALLBACK_TECH = [
    ("AI Breakthrough: New Model Beats Human Performance", [
        "Researchers have developed an AI model that outperforms humans on complex reasoning tasks.",
        "The model uses a novel architecture that combines symbolic reasoning with neural networks.",
        "This breakthrough could accelerate scientific discovery and problem-solving.",
        "Experts say we are entering a new era of AI capabilities.",
    ]),
    ("Quantum Computing Milestone Achieved", [
        "A major tech company has demonstrated quantum advantage on a practical problem.",
        "The quantum processor solved a calculation in minutes that would take supercomputers years.",
        "This brings us closer to real-world quantum applications.",
        "Industries like cryptography, drug discovery, and optimization will be transformed.",
    ]),
    ("New Battery Technology Doubles EV Range", [
        "Scientists have developed a solid-state battery that doubles electric vehicle range.",
        "The new battery charges in 10 minutes and lasts 1000+ cycles.",
        "Major automakers are already planning to integrate this technology.",
        "This could accelerate the global transition to electric vehicles.",
    ]),
    ("Breakthrough in Nuclear Fusion Energy", [
        "Researchers achieved net energy gain in a fusion reaction for the first time.",
        "The experiment produced more energy than was put in to initiate the reaction.",
        "This is a historic milestone toward clean, limitless energy.",
        "Commercial fusion power plants could be reality within two decades.",
    ]),
]


def fetch_tech_headlines() -> list[dict]:
    for feed_url in TECH_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "AutoYouTubePipeline/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            headlines = _parse_rss(raw)
            if headlines:
                logger.info(f"Fetched {len(headlines)} tech headlines from {feed_url}")
                return [{"title": h, "source": feed_url} for h in headlines[:5]]
        except Exception as e:
            logger.warning(f"Tech RSS fetch failed for {feed_url}: {e}")
    return []


def _parse_rss(xml: str) -> list[str]:
    results = []
    import re
    items = re.findall(r"<item[^>]*>(.*?)</item>", xml, re.DOTALL)
    for item in items[:5]:
        title = re.search(r"<title[^>]*>(.*?)</title>", item)
        if title:
            text = title.group(1).strip()
            # Clean CDATA
            text = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text)
            if len(text) > 15:
                results.append(text)
    return results


def generate_tech_content() -> dict:
    existing = fetch_tech_headlines()
    if not existing:
        topic = random.choice(FALLBACK_TECH)
        script_lines = list(topic[1])
        title = topic[0]
    else:
        headlines = [h["title"] for h in existing]
        script_lines = headlines + [
            f"This is your daily tech update from {datetime.now().strftime('%B %d')}. Stay ahead of the curve."
        ]
        title = f"Daily Tech News — {datetime.now().strftime('%b %d, %Y')}"

    description = (
        f"💻 Daily Tech News Update | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{' '.join(script_lines[:3])}\n\n"
        f"#TechNews #Technology #AI #Innovation #Science #Future"
    )
    tags = ["tech", "technology", "ai", "innovation", "science",
            "future", "tech news", "artificial intelligence"]

    return {
        "category": "tech",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+2%",
    }