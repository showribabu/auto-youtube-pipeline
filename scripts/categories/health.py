import random
from datetime import datetime
from logger import get_logger
logger = get_logger("health")

HEALTH_TOPICS = [
    ("Morning Routine for Energy All Day", [
        "Start with 500ml of water within 30 minutes of waking up.",
        "Get 10 minutes of sunlight within the first hour — regulates circadian rhythm.",
        "Move your body: stretch, walk, or do bodyweight exercises for 10 minutes.",
        "Eat a protein-rich breakfast within 90 minutes of waking.",
        "This routine sets your energy, mood, and metabolism for the entire day.",
    ]),
    ("The 3-2-1 Sleep Rule", [
        "3 hours before bed: stop eating heavy meals.",
        "2 hours before bed: stop work and intense mental activity.",
        "1 hour before bed: no screens — read, stretch, or meditate instead.",
        "This simple rule dramatically improves sleep quality and next-day energy.",
        "Consistency beats perfection — aim for 5 out of 7 nights.",
    ]),
    ("Micro-Habits That Transform Health", [
        "Drink a glass of water before every meal — improves digestion and reduces overeating.",
        "Take a 2-minute walk after each meal — regulates blood sugar spikes.",
        "Do 10 squats every time you use the bathroom — builds strength effortlessly.",
        "Breathe: 4 seconds in, hold 4, out 4, hold 4 — reduces stress instantly.",
        "Small consistent actions beat occasional heroic efforts every time.",
    ]),
]


def generate_health_content() -> dict:
    topic = random.choice(HEALTH_TOPICS)
    title, script_lines = topic
    title = f"Daily Health Tip — {title}"

    description = (
        f"💪 Daily Health Tip | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{title}\n\n"
        f"Small changes, big results!\n\n"
        f"#Health #Wellness #Fitness #Nutrition #Sleep #Habits #SelfCare"
    )
    tags = ["health", "wellness", "fitness", "nutrition",
            "sleep", "habits", "self care", "healthy lifestyle"]

    return {
        "category": "health",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "-2%",
    }