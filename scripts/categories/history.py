import random
import datetime
from config import logger

HISTORY_EVENTS = [
    ("Today in History — Moon Landing", [
        "On July 20, 1969, humans first walked on the Moon.",
        "Neil Armstrong and Buzz Aldrin spent 21 hours on the lunar surface.",
        "Michael Collins orbited above in the command module.",
        "The mission fulfilled President Kennedy's 1961 promise.",
        "Over 600 million people watched live on television worldwide.",
    ]),
    ("Today in History — Berlin Wall Falls", [
        "On November 9, 1989, the Berlin Wall fell after 28 years.",
        "East German officials announced free passage — crowds swarmed the checkpoints.",
        "People chipped away at the wall with hammers and chisels.",
        "This marked the beginning of German reunification.",
        "A pivotal moment ending the Cold War division of Europe.",
    ]),
    ("Today in History — First Powered Flight", [
        "On December 17, 1903, the Wright brothers achieved powered flight.",
        "Orville flew 120 feet in 12 seconds at Kitty Hawk, North Carolina.",
        "Four flights that day, the longest 852 feet in 59 seconds.",
        "They built their own engine and propellers from scratch.",
        "This 12-second flight changed human transportation forever.",
    ]),
    ("Today in History — Penicillin Discovered", [
        "On September 28, 1928, Alexander Fleming discovered penicillin.",
        "A contaminated petri dish showed bacteria-free zones around mold.",
        "This accidental discovery revolutionized medicine.",
        "Antibiotics have saved hundreds of millions of lives since.",
        "Fleming warned of antibiotic resistance in his Nobel speech.",
    ]),
]


def generate_history_content() -> dict:
    today = datetime.datetime.now()
    # Simple hash to pick consistent event for the day
    day_hash = (today.month * 31 + today.day) % len(HISTORY_EVENTS)
    topic = HISTORY_EVENTS[day_hash]
    title, script_lines = topic
    title = f"Today in History — {title}"

    description = (
        f"📜 Today in History | {today.strftime('%B %d')}\n\n"
        f"{title}\n\n"
        f"Learn something new about our past every day!\n\n"
        f"#History #TodayInHistory #Education #Facts #Knowledge"
    )
    tags = ["history", "today in history", "education", "facts",
            "knowledge", "historical events", "on this day"]

    return {
        "category": "history",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+0%",
    }