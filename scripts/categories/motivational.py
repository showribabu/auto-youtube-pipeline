import random
from datetime import datetime

QUOTES = [
    ("The Power of Persistence", [
        "Success is not final, failure is not fatal — it is the courage to continue that counts.",
        "Every champion was once a contender that refused to give up.",
        "The difference between ordinary and extraordinary is that little extra.",
        "Your limitation — it's only your imagination.",
        "Push yourself, because no one else is going to do it for you.",
        "Great things never come from comfort zones. Dream bigger. Dare greater.",
        "Failure will never overtake me if my determination to succeed is strong enough.",
    ]),
    ("Rise Every Day", [
        "The only way to do great work is to love what you do.",
        "Believe you can and you're halfway there.",
        "It does not matter how slowly you go as long as you do not stop.",
        "The best time to plant a tree was 20 years ago. The second best time is now.",
        "Don't watch the clock; do what it does. Keep going.",
        "Everything you've ever wanted is on the other side of fear.",
    ]),
    ("Discipline Equals Freedom", [
        "Discipline is the bridge between goals and accomplishment.",
        "We are what we repeatedly do. Excellence, then, is not an act but a habit.",
        "Motivation gets you started. Habit keeps you going.",
        "The secret of getting ahead is getting started.",
        "Don't wait for opportunity. Create it.",
        "Stars can't shine without darkness.",
    ]),
    ("Wisdom for Today", [
        "The mind is everything. What you think you become.",
        "In the middle of difficulty lies opportunity.",
        "The only impossible journey is the one you never begin.",
        "With the new day comes new strength and new thoughts.",
        "Act as if what you do makes a difference. It does.",
        "What we think, we become.",
    ]),
]


def generate_motivational_content() -> dict:
    topic = random.choice(QUOTES)
    title, script_lines = topic
    title = f"Daily Motivation — {title}"

    description = (
        f"💪 Daily Motivation for {datetime.now().strftime('%A, %B %d')}\n\n"
        f"{title}\n\n"
        f"Start your day with inspiration!\n\n"
        f"#Motivation #Inspiration #DailyQuote #Success #Mindset #PositiveVibes"
    )
    tags = ["motivation", "inspiration", "daily quote", "success",
            "mindset", "positive vibes", "life quotes", "personal growth"]

    return {
        "category": "motivational",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "-3%",
    }
