import random
import urllib.request
import json
import re
from datetime import datetime
from config import SCHEDULES, MAX_VIDEOS_PER_DAY, RETRY_DELAY, MAX_RETRIES
from logger import get_logger
logger = get_logger("crypto")

CRYPTO_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
]

FALLBACK_CRYPTO = [
    ("Bitcoin Reaches New All-Time High", [
        "Bitcoin has surged past previous records amid growing institutional adoption.",
        "Major corporations are adding Bitcoin to their treasury reserves.",
        "ETF approvals have opened the floodgates for mainstream investment.",
        "Analysts predict continued upward momentum through the year.",
    ]),
    ("Ethereum Layer 2 Solutions Scale Massively", [
        "Ethereum Layer 2 networks now process more transactions than the mainnet.",
        "Arbitrum and Optimism lead the way with billions in TVL.",
        "Gas fees have dropped 90% making DeFi accessible to everyone.",
        "This scaling breakthrough enables mainstream crypto adoption.",
    ]),
    ("Stablecoins Become Global Payment Standard", [
        "USDC and USDT now settle trillions in annual transaction volume.",
        "Major payment processors integrate stablecoins for instant global transfers.",
        "Countries explore stablecoin frameworks for financial inclusion.",
        "Traditional banking faces disruption from programmable money.",
    ]),
]


def fetch_crypto_headlines() -> list[dict]:
    for feed_url in CRYPTO_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "AutoYouTubePipeline/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            headlines = _parse_rss(raw)
            if headlines:
                logger.info(f"Fetched {len(headlines)} crypto headlines from {feed_url}")
                return [{"title": h, "source": feed_url} for h in headlines[:5]]
        except Exception as e:
            logger.warning(f"Crypto RSS fetch failed for {feed_url}: {e}")
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


def generate_crypto_content() -> dict:
    existing = fetch_crypto_headlines()
    if not existing:
        topic = random.choice(FALLBACK_CRYPTO)
        script_lines = list(topic[1])
        title = topic[0]
    else:
        headlines = [h["title"] for h in existing]
        script_lines = headlines + [
            f"This is your daily crypto market update from {datetime.now().strftime('%B %d')}. Trade smart."
        ]
        title = f"Daily Crypto Update — {datetime.now().strftime('%b %d, %Y')}"

    description = (
        f"₿ Daily Crypto Market Update | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{' '.join(script_lines[:3])}\n\n"
        f"#Crypto #Bitcoin #Ethereum #DeFi #Web3 #Blockchain"
    )
    tags = ["crypto", "bitcoin", "ethereum", "defi", "web3",
            "blockchain", "cryptocurrency", "trading"]

    return {
        "category": "crypto",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+0%",
    }