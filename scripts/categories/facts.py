"""
facts.py - Mind-Blowing Science & World Facts Storytelling Generator

Replaces dry trivia with captivating, wonder-inducing narratives:
- Powerful curiosity hook in sentence 1
- Deep mind-bending scientific revelation in sentences 2-4
- Memorable, thought-provoking philosophical takeaway in the final sentence
"""

import random
import html
from logger import get_logger

logger = get_logger("facts")

FACTS_BY_LANG = {
    "te": [
        (
            "సూర్యుని లోపల ప్రయాణించే కాంతి రహస్యం మీకు తెలుసా? #Shorts",
            [
                "సూర్యుని కేంద్రంలో పుట్టిన కాంతి కిరణం మన భూమిని చేరడానికి ఎంత సమయం పడుతుందో తెలుసా?",
                "సూర్యుని ఉపరితలం నుంచి భూమికి కేవలం 8 నిమిషాల 20 సెకన్లలోనే చేరుకుంటుంది.",
                "కానీ ఆశ్చర్యకరమైన విషయం ఏమిటంటే, సూర్యుని కోర్ లోపల ఉన్న దట్టమైన ప్లాస్మా నుంచి బయటకు రావడానికి ఆ కాంతికి లక్ష సంవత్సరాలు పడుతుంది!",
                "అంటే ఈరోజు మనం చూస్తున్న సూర్యకాంతి, లక్ష సంవత్సరాల పురాతన కాలం నాటిది.",
                "ప్రకృతిలో దాగి ఉన్న అద్భుతాలు నిజంగా మానవ ఊహకందనివి!"
            ]
        ),
        (
            "తేనె ఎప్పటికీ ఎందుకు పాడవదు — రహస్యం ఇదే! #Shorts",
            [
                "ప్రపంచంలో వందల ఏళ్లయినా పాడవని ఏకైక సహజ ఆహారం తేనె మాత్రమే!",
                "ఈజిప్ట్ పిరమిడ్లలో పురావస్తు శాస్త్రవేత్తలు 3000 ఏళ్ల నాటి తేనె కుండలను కనుగొన్నారు.",
                "ఆశ్చర్యకరంగా ఆ తేనె ఇప్పటికీ తాజాగా, తినడానికి అనుకూలంగా ఉంది.",
                "తేనెలో నీటి శాతం చాలా తక్కువగా ఉండడం మరియు ఆమ్ల గుణం వల్ల ఎలాంటి బ్యాక్టీరియా బ్రతకలేదు.",
                "ప్రకృతి మనకు ప్రసాదించిన అమృతం తేనె అని అనడంలో ఎలాంటి సందేహం లేదు!"
            ]
        ),
        (
            "ఆక్టోపస్‌కు 3 గుండెలు మరియు 9 మెదళ్లు ఉంటాయని తెలుసా? #Shorts",
            [
                "సముద్రపు జీవుల్లో అత్యంత వింతైన, అద్భుతమైన తెలివితేటలు కలిగిన జీవి ఆక్టోపస్!",
                "ఆక్టోపస్‌కు మూడు గుండెలు, తొమ్మిది మెదళ్లు మరియు నీలి రంగు రక్తం ఉంటుంది.",
                "దాని శరీరంలోని ప్రతి కాలికి ఒక చిన్న మెదడు ఉండి, స్వతంత్రంగా ఆలోచించి నిర్ణయాలు తీసుకోగలదు.",
                "ఒక కన్ను మూసి పడుకున్నా, మిగతా శరీరం శత్రువుల నుంచి తనను తాను రక్షించుకోగలదు.",
                "మన సముద్ర గర్భంలో భూమి కంటే అంతుచిక్కని అద్భుత ప్రపంచం దాగి ఉంది!"
            ]
        ),
    ],
    "hi": [
        (
            "सूरज की रोशनी का वो सच जो आप नहीं जानते! #Shorts",
            [
                "क्या आप जानते हैं कि आज जो धूप आप महसूस कर रहे हैं, वो कितनी पुरानी है?",
                "सूरज की सतह से धरती तक आने में रोशनी को सिर्फ 8 मिनट 20 सेकंड लगते हैं।",
                "लेकिन सूरज के केंद्र से उसकी सतह तक बाहर निकलने में उस रोशनी को 1 लाख साल से भी ज्यादा का समय लगता है!",
                "इसका मतलब आज जो किरणें आप देख रहे हैं, वो आदिमानव के समय सूरज के अंदर बनी थीं।",
                "ब्रह्मांड का यह अद्भुत रहस्य सचमुच इंसानी समझ से परे है!"
            ]
        ),
        (
            "शहद 3000 साल बाद भी खराब क्यों नहीं होता? #Shorts",
            [
                "दुनिया में केवल शहद ही ऐसा प्राकृतिक भोजन है जो कभी खराब नहीं होता!",
                "मिस्र के प्राचीन पिरामिडों में पुरातत्वविदों को 3000 साल पुराने शहद के बर्तन मिले।",
                "हैरानी की बात यह है कि वह शहद आज भी उतना ही मीठा और खाने योग्य था।",
                "नमी की कमी और खास एसिडिक गुणों के कारण इसमें बैक्टीरिया कभी पनप नहीं सकते।",
                "प्रकृति की इस अनमोल देन का रहस्य विज्ञान को भी हैरान कर देता है!"
            ]
        ),
    ],
    "en": [
        (
            "The 100,000 Year Journey of Sunlight #Shorts",
            [
                "Did you know the sunlight warming your face right now is actually ancient?",
                "While light takes just 8 minutes to travel from the Sun's surface to Earth...",
                "It takes over 100,000 years for a single photon to escape from the Sun's dense core to its surface!",
                "The light you see today was created before modern human civilization even began.",
                "The universe is far more magical and mysterious than we can ever imagine."
            ]
        ),
        (
            "Why Honey Never Spoils in 3,000 Years #Shorts",
            [
                "Honey is the only natural food known to humanity that never rots or spoils.",
                "Archaeologists excavating ancient Egyptian tombs found 3,000-year-old jars of honey that were perfectly preserved.",
                "Its virtually nonexistent moisture content and natural acidity make it impossible for bacteria to survive.",
                "Centuries can pass, and pure honey remains as sweet and edible as the day it was harvested.",
                "Nature engineered the ultimate immortal food long before modern preservation existed."
            ]
        ),
        (
            "The Alien Intelligence of the Octopus #Shorts",
            [
                "Octopuses are the closest thing to alien life living right here on Earth.",
                "They possess three beating hearts, blue copper-based blood, and nine distinct brains.",
                "Each of their eight arms contains its own autonomous mini-brain that can touch, taste, and act independently.",
                "They can edit their own genetic RNA to adapt to changing ocean temperatures in real time.",
                "The oceans hold mysteries deeper and stranger than outer space itself."
            ]
        ),
    ]
}


def generate_fact_content(lang: str = "te") -> dict:
    facts = FACTS_BY_LANG.get(lang, FACTS_BY_LANG["te"])
    title, script_lines = random.choice(facts)

    title = html.unescape(title)
    script_lines = [html.unescape(line) for line in script_lines]

    description = (
        f"🧠 Mind-Blowing World & Science Facts\n\n"
        f"{title}\n\n"
        f"{' '.join(script_lines[:3])}\n\n"
        f"#Facts #MindBlowing #Science #DidYouKnow #Knowledge #Viral #Shorts"
    )
    tags = ["facts", "did you know", "science", "mind blown", "education", "knowledge", "shorts", "viral"]

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
