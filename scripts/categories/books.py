import random
from datetime import datetime
from logger import get_logger
logger = get_logger("books")

BOOK_LIBRARY = [
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "takeaways": [
            "Small habits compound over time — a 1% improvement each day makes you 37 times better in a year.",
            "Focus on systems, not goals. Goals set direction, but systems drive progress.",
            "Make good habits obvious, attractive, easy, and satisfying — the four laws of behavior change.",
            "Identity change is the deepest level of habit change: decide who you want to be, then prove it with small wins.",
            "Environment design beats willpower. Remove friction for good habits, add friction for bad ones.",
            "Never miss twice. Missing once is an accident; missing twice is the start of a new bad habit.",
        ],
    },
    {
        "title": "Thinking, Fast and Slow",
        "author": "Daniel Kahneman",
        "takeaways": [
            "Your brain has two systems: System 1 is fast, intuitive, and emotional. System 2 is slow, deliberate, and logical.",
            "Most of our daily decisions are made by System 1 — quick but often biased.",
            "Anchoring bias: the first number you hear heavily influences your judgment, even when irrelevant.",
            "Loss aversion: losing $100 feels roughly twice as painful as the pleasure of gaining $100.",
            "Overconfidence is one of the most significant biases — we consistently overestimate what we know.",
            "The planning fallacy: we underestimate time, costs, and risks while overestimating benefits of our plans.",
        ],
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "takeaways": [
            "Homo sapiens conquered the world because of our unique ability to believe in shared fictions — money, nations, religions.",
            "The Agricultural Revolution was history's biggest fraud — it made life harder for individuals but enabled population growth.",
            "Money is the most universal system of mutual trust ever devised by humans.",
            "Empires have been the most common form of political organization throughout history.",
            "Happiness does not necessarily increase with wealth, power, or technological progress.",
            "We are on the verge of becoming gods — with the power to design life — but we still don't know what we want.",
        ],
    },
    {
        "title": "The 7 Habits of Highly Effective People",
        "author": "Stephen R. Covey",
        "takeaways": [
            "Be proactive: focus on what you can control and influence, not on what you can't.",
            "Begin with the end in mind: define your personal mission statement and align actions with values.",
            "Put first things first: prioritize important-but-not-urgent tasks over urgent distractions.",
            "Think win-win: seek solutions where everyone benefits rather than competing at others' expense.",
            "Seek first to understand, then to be understood — empathic listening is the key to influence.",
            "Sharpen the saw: regularly renew yourself physically, mentally, socially, and spiritually.",
        ],
    },
    {
        "title": "Rich Dad Poor Dad",
        "author": "Robert T. Kiyosaki",
        "takeaways": [
            "The rich don't work for money — they make money work for them through assets and investments.",
            "An asset puts money in your pocket; a liability takes money out. Your house is often a liability, not an asset.",
            "Financial literacy is the most important skill: understanding cash flow, taxes, and investing.",
            "Mind your own business: build your asset column while keeping your day job.",
            "The fear of losing money stops most people from ever getting rich — the rich learn to manage risk, not avoid it.",
            "Work to learn, not to earn. Seek jobs that teach sales, marketing, and management skills.",
        ],
    },
    {
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "takeaways": [
            "When you want something, all the universe conspires in helping you achieve it — follow your Personal Legend.",
            "The fear of failure is worse than failure itself. Most regrets come from paths not taken.",
            "The journey matters more than the destination — wisdom is found along the way, not at the end.",
            "Listen to your heart. It knows things the mind will never understand.",
            "Every search begins with beginner's luck and ends with the victor being severely tested.",
            "The treasure you seek may be closer than you think — sometimes it's right where you started.",
        ],
    },
    {
        "title": "Deep Work",
        "author": "Cal Newport",
        "takeaways": [
            "Deep work — focused, uninterrupted concentration — is becoming rare and increasingly valuable in our distracted world.",
            "Shallow work fills time but doesn't create value. Email, meetings, and social media are the enemies of deep work.",
            "Schedule deep work blocks like appointments — if it's not on your calendar, it won't happen.",
            "Embrace boredom. Training your mind to resist distraction outside of work strengthens focus during work.",
            "Quit social media — or at least audit it ruthlessly. Most platforms deliver little professional or personal value.",
            "The craftsman approach: apply intense focus to produce rare and valuable output that the market rewards.",
        ],
    },
    {
        "title": "Ikigai: The Japanese Secret to a Long and Happy Life",
        "author": "Héctor García and Francesc Miralles",
        "takeaways": [
            "Ikigai is the intersection of what you love, what you're good at, what the world needs, and what you can be paid for.",
            "The people of Okinawa, Japan, live the longest — their secret is purpose, community, and simple living.",
            "Stay active and don't retire. Those who maintain purpose and activity live significantly longer.",
            "Eat until you are 80% full — the Okinawan practice of 'hara hachi bu' prevents overeating and promotes longevity.",
            "Surround yourself with good friends. Social connection is one of the strongest predictors of long life.",
            "Flow — being completely immersed in an activity — is a daily experience for those who have found their ikigai.",
        ],
    },
    {
        "title": "The Power of Now",
        "author": "Eckhart Tolle",
        "takeaways": [
            "The present moment is all you ever have. The past is memory, the future is imagination — only now is real.",
            "Most human suffering is self-created through overthinking, dwelling on the past, or fearing the future.",
            "You are not your thoughts. Observe your mind without judgment — this creates a gap between you and your reactions.",
            "The ego thrives on conflict, comparison, and complaint. Awareness of the ego dissolves its power over you.",
            "Acceptance of the present moment is the foundation of inner peace — resist nothing, allow everything.",
            "True fulfillment never comes from external achievements; it comes from being fully present in each moment.",
        ],
    },
    {
        "title": "Man's Search for Meaning",
        "author": "Viktor E. Frankl",
        "takeaways": [
            "Those who have a 'why' to live can bear almost any 'how' — meaning is the primary motivation of human life.",
            "Frankl survived Nazi concentration camps by finding purpose even in the most horrific suffering.",
            "We cannot avoid suffering, but we can choose how to cope with it, find meaning in it, and move forward.",
            "Happiness cannot be pursued directly — it must ensue as a side effect of dedicating yourself to a cause or a person.",
            "The last of human freedoms is to choose one's attitude in any given set of circumstances.",
            "Logotherapy: healing comes not from pleasure or power, but from discovering meaning in every situation.",
        ],
    },
]


def generate_book_content() -> dict:
    book = random.choice(BOOK_LIBRARY)
    title = f"Book Summary: {book['title']} by {book['author']}"

    script_lines = [
        f"Today we're exploring key ideas from '{book['title']}' by {book['author']}.",
    ] + book["takeaways"] + [
        f"That's a quick summary of '{book['title']}'. Pick up a copy and dive deeper!",
    ]

    description = (
        f"📚 Book Summary | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"{title}\n\n"
        f"Key takeaways and life-changing ideas from one of the best books of all time.\n\n"
        f"#Books #Reading #BookSummary #SelfImprovement #Education"
    )
    tags = ["books", "reading", "book summary", "self improvement", "education"]

    return {
        "category": "books",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_male",
        "rate": "+0%",
    }