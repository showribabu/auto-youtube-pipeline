import random
from datetime import datetime

FACTS = [
    ("The Internet's First Message", [
        "In 1969, the first message sent over the internet was supposed to be 'LOGIN'.",
        "But the system crashed after just two letters — 'LO'.",
        "That moment marked the birth of global digital communication.",
        "Today, billions of messages are sent every second around the world.",
    ]),
    ("Octopus Intelligence", [
        "Octopuses have three hearts, nine brains, and blue blood.",
        "Two hearts pump blood to the gills, while the third pumps it to the rest of the body.",
        "Each arm has a mini-brain that can act independently.",
        "They are considered one of the most intelligent invertebrates on Earth.",
    ]),
    ("The Great Wall from Space", [
        "Contrary to popular belief, the Great Wall of China is NOT visible from space with the naked eye.",
        "Astronauts have confirmed this multiple times.",
        "However, from the Moon, even the Great Wall would be nearly impossible to see.",
        "What IS visible from low Earth orbit are man-made structures like cities and highways.",
    ]),
    ("Honey — The Eternal Food", [
        "Honey is the only food that never spoils.",
        "Archaeologists have found 3,000-year-old honey in Egyptian tombs that was still edible.",
        "Its low moisture content and acidic pH create an environment where bacteria cannot survive.",
        "Ancient civilizations valued honey not just as food, but as a medicine and preservative.",
    ]),
    ("Volcanic Thunderstorms", [
        "Volcanic eruptions can create their own thunderstorms, called dirty thunderstorms.",
        "Ash particles colliding generate massive static electricity.",
        "These storms can produce lightning strikes hot enough to melt rock.",
        "The 1991 eruption of Mount Pinatubo created lightning visible from hundreds of miles away.",
    ]),
    ("The Speed of Thought", [
        "Information travels through your neurons at speeds up to 120 meters per second.",
        "That is fast enough to circle the Earth about 7 times in a single second.",
        "Your brain processes sensory input in as little as 2 milliseconds.",
        "Some signals from your toes to your brain travel faster than a Formula 1 car.",
    ]),
]


def generate_fact_content() -> dict:
    topic = random.choice(FACTS)
    title, script_lines = topic
    title = f"Mind-Blowing Fact: {title}"

    description = (
        f"🧠 Daily Mind-Blowing Fact\n\n"
        f"{title}\n\n"
        f"Learn something incredible every day!\n\n"
        f"#Facts #DidYouKnow #MindBlown #Education #Science #Knowledge"
    )
    tags = ["facts", "did you know", "mind blowing", "education",
            "science", "knowledge", "learn", "interesting facts"]

    return {
        "category": "facts",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+0%",
    }
