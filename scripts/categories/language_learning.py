import random
from datetime import datetime
from logger import get_logger
logger = get_logger("language_learning")

WORD_DATABASE = [
    {
        "word": "Ephemeral",
        "pronunciation": "eh-FEM-er-ul",
        "definition": "Lasting for a very short time; fleeting and transient.",
        "etymology": "From Greek 'ephemeros' meaning 'lasting only a day', from 'epi' (on) + 'hemera' (day).",
        "examples": [
            "The beauty of cherry blossoms is ephemeral — they bloom for just a few weeks each spring.",
            "Social media trends are ephemeral; what's viral today is forgotten tomorrow.",
            "He captured the ephemeral glow of the sunset in a stunning photograph.",
        ],
        "related_words": ["transient", "fleeting", "momentary", "evanescent"],
    },
    {
        "word": "Serendipity",
        "pronunciation": "ser-en-DIP-ih-tee",
        "definition": "The occurrence of events by chance in a happy or beneficial way.",
        "etymology": "Coined by Horace Walpole in 1754, from the Persian fairy tale 'The Three Princes of Serendip', whose heroes made discoveries by accident.",
        "examples": [
            "It was pure serendipity that she found the rare book at a garage sale.",
            "Many scientific breakthroughs, like penicillin, happened through serendipity.",
            "Their meeting at the airport was a moment of serendipity that changed both their lives.",
        ],
        "related_words": ["fortune", "luck", "providence", "happenstance"],
    },
    {
        "word": "Eloquent",
        "pronunciation": "EL-oh-kwent",
        "definition": "Fluent or persuasive in speaking or writing; clearly expressing feelings or ideas.",
        "etymology": "From Latin 'eloquens', present participle of 'eloqui' meaning 'to speak out', from 'ex' (out) + 'loqui' (to speak).",
        "examples": [
            "Martin Luther King Jr. was one of the most eloquent speakers of the 20th century.",
            "Her eloquent essay moved the entire audience to tears.",
            "He gave an eloquent defense of free speech that silenced his critics.",
        ],
        "related_words": ["articulate", "expressive", "persuasive", "fluent"],
    },
    {
        "word": "Resilient",
        "pronunciation": "rih-ZIL-yent",
        "definition": "Able to recover quickly from difficulties; tough and adaptable.",
        "etymology": "From Latin 'resilire' meaning 'to spring back, rebound', from 're' (back) + 'salire' (to jump, leap).",
        "examples": [
            "Children are remarkably resilient — they can bounce back from setbacks faster than adults.",
            "The resilient economy recovered within months after the crisis.",
            "Bamboo is one of nature's most resilient materials, bending without breaking.",
        ],
        "related_words": ["tough", "adaptable", "hardy", "durable"],
    },
    {
        "word": "Ubiquitous",
        "pronunciation": "yoo-BIK-wih-tus",
        "definition": "Present, appearing, or found everywhere; omnipresent.",
        "etymology": "From Latin 'ubique' meaning 'everywhere', from 'ubi' (where) + the generalizing suffix '-que'.",
        "examples": [
            "Smartphones have become ubiquitous — nearly everyone carries one today.",
            "Coffee shops are ubiquitous in modern cities; you can find one on every corner.",
            "Plastic pollution has become ubiquitous, found even in the deepest ocean trenches.",
        ],
        "related_words": ["omnipresent", "pervasive", "universal", "widespread"],
    },
    {
        "word": "Pragmatic",
        "pronunciation": "prag-MAT-ik",
        "definition": "Dealing with things sensibly and realistically, based on practical considerations.",
        "etymology": "From Greek 'pragmatikos' meaning 'fit for business', from 'pragma' (deed, act), from 'prassein' (to do).",
        "examples": [
            "She took a pragmatic approach to budgeting, cutting unnecessary expenses first.",
            "A pragmatic leader focuses on what works rather than what sounds ideal.",
            "Instead of debating endlessly, they made a pragmatic decision to test both options.",
        ],
        "related_words": ["practical", "realistic", "sensible", "rational"],
    },
    {
        "word": "Cacophony",
        "pronunciation": "kuh-KOF-uh-nee",
        "definition": "A harsh, discordant mixture of sounds; jarring noise.",
        "etymology": "From Greek 'kakophonia', from 'kakos' (bad, ugly) + 'phone' (voice, sound).",
        "examples": [
            "The cacophony of car horns during rush hour made it impossible to think.",
            "The orchestra's warm-up was a brief cacophony before the beautiful symphony began.",
            "A cacophony of barking dogs echoed through the neighborhood at dawn.",
        ],
        "related_words": ["discord", "dissonance", "clamor", "racket"],
    },
    {
        "word": "Altruistic",
        "pronunciation": "al-troo-IS-tik",
        "definition": "Showing a selfless concern for the well-being of others; unselfish.",
        "etymology": "From French 'altruisme', coined by Auguste Comte from Italian 'altrui' (of or to others), from Latin 'alter' (other).",
        "examples": [
            "Her altruistic decision to donate a kidney saved a stranger's life.",
            "Altruistic behavior in animals, like dolphins helping injured swimmers, fascinates researchers.",
            "He lived an altruistic life, spending decades building schools in underserved communities.",
        ],
        "related_words": ["selfless", "generous", "philanthropic", "humanitarian"],
    },
    {
        "word": "Sycophant",
        "pronunciation": "SIK-uh-fant",
        "definition": "A person who acts obsequiously toward someone important to gain advantage; a flatterer.",
        "etymology": "From Greek 'sykophantes' meaning 'informer', originally 'one who shows the fig', possibly referring to an obscene gesture used to denounce someone.",
        "examples": [
            "The CEO surrounded himself with sycophants who never challenged his ideas.",
            "History shows that leaders who listen only to sycophants make disastrous decisions.",
            "She refused to be a sycophant, always giving honest feedback even when it was unwelcome.",
        ],
        "related_words": ["flatterer", "toady", "yes-man", "bootlicker"],
    },
    {
        "word": "Paradigm",
        "pronunciation": "PAIR-uh-dime",
        "definition": "A typical example or pattern of something; a model or framework of thinking.",
        "etymology": "From Greek 'paradeigma' meaning 'pattern, model', from 'paradeiknynai' (to show side by side), from 'para' (beside) + 'deiknynai' (to show).",
        "examples": [
            "The internet created a paradigm shift in how humans access information.",
            "Einstein's theory of relativity introduced a new paradigm in physics.",
            "Remote work is challenging the traditional paradigm of the office-based workplace.",
        ],
        "related_words": ["model", "framework", "archetype", "standard"],
    },
    {
        "word": "Enigmatic",
        "pronunciation": "en-ig-MAT-ik",
        "definition": "Difficult to interpret or understand; mysterious and puzzling.",
        "etymology": "From Greek 'ainigma' meaning 'riddle', from 'ainissesthai' (to speak in riddles), from 'ainos' (fable, tale).",
        "examples": [
            "The Mona Lisa's enigmatic smile has fascinated art lovers for over 500 years.",
            "He was an enigmatic figure who rarely spoke about his past.",
            "The ancient ruins held enigmatic symbols that archaeologists are still trying to decode.",
        ],
        "related_words": ["mysterious", "cryptic", "puzzling", "inscrutable"],
    },
    {
        "word": "Tenacious",
        "pronunciation": "teh-NAY-shus",
        "definition": "Tending to keep a firm hold of something; persistent and determined.",
        "etymology": "From Latin 'tenax' meaning 'holding fast', from 'tenere' (to hold).",
        "examples": [
            "Her tenacious pursuit of justice led to a landmark court ruling.",
            "Ivy is a tenacious plant — once it takes root, it's nearly impossible to remove.",
            "The tenacious journalist spent three years uncovering the corruption scandal.",
        ],
        "related_words": ["persistent", "determined", "dogged", "resolute"],
    },
]


def generate_language_content() -> dict:
    entry = random.choice(WORD_DATABASE)
    word = entry["word"]

    script_lines = [
        f"Word of the Day: {word}.",
        f"Pronunciation: {entry['pronunciation']}.",
        f"Definition: {entry['definition']}",
        f"Etymology: {entry['etymology']}",
        f"Example one: {entry['examples'][0]}",
        f"Example two: {entry['examples'][1]}",
        f"Example three: {entry['examples'][2]}",
        f"Related words: {', '.join(entry['related_words'])}.",
        f"Try using '{word}' in a sentence today!",
    ]

    title = f"Word of the Day: {word} — Build Your Vocabulary"

    description = (
        f"📖 Word of the Day | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"Today's word: {word} ({entry['pronunciation']})\n"
        f"{entry['definition']}\n\n"
        f"Learn a new word every day and expand your vocabulary!\n\n"
        f"#Language #Vocabulary #WordOfTheDay #English #Education #Learning"
    )
    tags = ["language", "vocabulary", "word of the day", "english",
            "education", "learning"]

    return {
        "category": "language",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "-5%",
    }