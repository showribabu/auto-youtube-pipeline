"""
dedup.py - 60-Day Ledger Anti-Duplicate Engine & String Sanitizer

Prevents duplicate video uploads by cross-referencing output/upload_ledger.json
and sanitizes titles by eliminating accidental duplicate prefixes.
"""

import os
import json
import re
from datetime import datetime, timedelta
from logger import get_logger

logger = get_logger("dedup")


def clean_title(title: str) -> str:
    """Sanitize title: strip duplicate prefixes, HTML entities, and redundant spaces."""
    if not title:
        return ""
    import html
    s = html.unescape(title)
    
    # Fix doubled prefixes like 'Today in History — Today in History — '
    s = re.sub(r"^(Today in History\s*—\s*)+", "Today in History — ", s, flags=re.IGNORECASE)
    s = re.sub(r"^(Book Summary:\s*)+", "Book Summary: ", s, flags=re.IGNORECASE)
    s = re.sub(r"^(Mind-Blowing Fact:\s*)+", "Mind-Blowing Fact: ", s, flags=re.IGNORECASE)
    s = re.sub(r"^(భగవద్గీత సందేశం\s*—\s*)+", "భగవద్గీత సందేశం — ", s)
    s = re.sub(r"^(Daily Tech News\s*—\s*)+", "Daily Tech News — ", s, flags=re.IGNORECASE)
    
    # Remove #Shorts or hashtags from visual title (metadata keeps them separately)
    s = re.sub(r"#\w+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_title(title: str) -> str:
    """Normalize title for exact duplicate matching: strip hashtags and non-alphanumerics."""
    if not title:
        return ""
    t = re.sub(r"#\w+", "", title)
    return re.sub(r"[^a-zA-Z0-9\u0C00-\u0C7F\u0900-\u097F]", "", t.lower())


def load_recent_titles(ledger_path: str, days: int = 60) -> set[str]:
    """Extract normalized titles published within the last N days."""
    if not os.path.exists(ledger_path):
        return set()
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
        cutoff = datetime.now() - timedelta(days=days)
        recent = set()
        for entry in ledger:
            date_str = entry.get("date")
            title = entry.get("title")
            if not date_str or not title:
                continue
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                if entry_date >= cutoff and entry.get("video_id"):
                    norm = normalize_title(title)
                    if norm:
                        recent.add(norm)
            except ValueError:
                pass
        logger.info(f"Loaded {len(recent)} recent published titles for deduplication (cutoff: {cutoff.strftime('%Y-%m-%d')})")
        return recent
    except Exception as e:
        logger.warning(f"Could not load ledger for dedup: {e}")
        return set()


def is_topic_duplicate(title: str, recent_titles: set[str]) -> bool:
    """Check if normalized title matches any recent upload."""
    if not title or not recent_titles:
        return False
    norm = normalize_title(title)
    return norm in recent_titles
