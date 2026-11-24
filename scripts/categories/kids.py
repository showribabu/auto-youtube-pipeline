import random
from datetime import datetime

STORIES = [
    ("The Brave Little Rabbit", "Once upon a time, there was a little rabbit named Coco who loved to explore. One sunny morning, she found a hidden garden full of rainbow carrots. She shared them with all her friends, and they had the biggest party ever!"),
    ("Leo the Lion Who Lost His Roar", "Leo the lion could not roar anymore. He asked every animal for help. Finally, his best friend said, 'Your roar is inside you.' Leo closed his eyes, took a deep breath, and ROARED! The jungle shook with joy."),
    ("The Magic Paintbrush", "Timmy found a paintbrush that made everything he drew come to life. He painted a butterfly, and it flew away. He painted a castle, and it appeared in his backyard. But the most beautiful thing he painted was a smile on his mom's face."),
    ("Bunny's Missing Carrot", "Bunny woke up and his favorite carrot was gone! He asked the birds, the squirrels, and even the old turtle. In the end, he found it behind the tree — he had planted it and forgotten. Now a whole carrot patch is growing!"),
    ("The Friendly Dragon", "Dragon was different from all the other dragons. Instead of breathing fire, he breathed bubbles! All the kids in the village loved him. One day, a real problem came, and Dragon saved everyone with his giant bubble shield."),
    ("Samuel and the Star", "A tiny star fell from the sky and landed in Samuel's yard. It was sad and dim. Samuel talked to it every night until it remembered how bright it could be. With a sparkle, the star flew back home, and now it shines extra bright for Samuel."),
]

FUN_FACTS_KIDS = [
    "Honey never spoils! Archaeologists found 3000-year-old honey in Egyptian tombs that was still good to eat.",
    "Octopuses have three hearts and blue blood!",
    "A group of flamingos is called a 'flamboyance'!",
    "Bananas are berries, but strawberries aren't!",
    "Cows have best friends and get stressed when they are separated.",
    "The shortest war in history lasted 38 minutes between England and Zanzibar in 1896.",
    "There are more stars in the universe than grains of sand on all Earth's beaches.",
    "A jiffy is an actual unit of time — it equals 1/100th of a second.",
    "Sea otters hold hands while sleeping so they don't drift apart.",
    "The inventor of the microwave oven discovered it by accident when a chocolate bar melted in his pocket.",
]

ALPHABET_STORIES = {
    "A": "Alligator Alex always arrives at amazing adventures above all ancient apples.",
    "B": "Brave Bobby the bear builds big bridges beyond bubbling brooks.",
}


def generate_kids_content() -> dict:
    story = random.choice(STORIES)
    title, script_text = story
    today = datetime.now().strftime("%B %d, %Y")

    description = (
        f"🌟 New Kids Story Time! 🌟\n\n"
        f"{title}\n\n"
        f"A fun and educational story for kids!\n\n"
        f"Timestamps:\n0:00 - The Story Begins\n"
        f"\n#Kids #Storytime #Cartoon #Children #Education #Fun #Learning"
    )

    tags = ["kids", "children", "cartoon", "storytime", "education",
            "fun", "learning", "animation", "bedtime stories", "kids videos"]

    return {
        "category": "kids",
        "title": title,
        "script_lines": script_text.split(". "),
        "full_script": script_text,
        "description": description,
        "tags": tags,
        "voice": "kids_female",
        "rate": "+5%",
    }


def generate_fact_video() -> dict:
    fact = random.choice(FUN_FACTS_KIDS)
    title = f"Did You Know? {fact[:50]}..."
    lines = [
        "Did you know?",
        fact,
        "Amazing, right? Stay curious!"
    ]

    description = (
        f"🧠 Fun Facts for Kids!\n\n"
        f"{fact}\n\n"
        f"Learn something new every day!\n\n"
        f"#FunFacts #KidsEducation #Learning #DidYouKnow #ScienceForKids"
    )
    tags = ["fun facts", "kids education", "science", "did you know",
            "children", "learning", "facts"]

    return {
        "category": "kids",
        "title": title,
        "script_lines": lines,
        "full_script": " ".join(lines),
        "description": description,
        "tags": tags,
        "voice": "kids_male",
        "rate": "+0%",
    }
