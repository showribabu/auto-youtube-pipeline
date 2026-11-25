"""
Daily Devotional & Spiritual Wisdom Module
Provides daily verses from Bhagavad Gita, Upanishads, mindfulness, and spiritual wisdom.
Supports English, Telugu, and Hindi translations.
"""
import random
from datetime import datetime
from logger import get_logger

logger = get_logger("devotional")

DEVOTIONAL_LESSONS = [
    {
        "topic": "Karma Yoga — The Art of Selfless Action",
        "verse": "Karmanye Vadhikaraste Ma Phaleshu Kadachana",
        "lines": [
            "Today's sacred wisdom from the Bhagavad Gita teaches us the secret of peace.",
            "You have the right to perform your prescribed duties, but never to the fruits of your actions.",
            "Never let the expectation of results become your motive, nor be attached to inaction.",
            "Focus completely on giving your best effort today with a calm, devoted mind.",
            "Peace and true fulfillment naturally follow selfless dedication.",
        ],
        "hi": {
            "title": "श्रीमद्भगवद्गीता ज्ञान — कर्मण्येवाधिकारस्ते (कर्म योग)",
            "lines": [
                "श्रीमद्भगवद्गीता का यह अमर संदेश हमें जीवन जीने की सच्ची कला सिखाता है।",
                "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन — तुम्हारा अधिकार केवल कर्म करने पर है, उसके फलों पर कभी नहीं।",
                "फल की चिंता छोड़कर अपने कर्तव्य को पूरी निष्ठा और भक्ति भाव से निभाएं।",
                "जब मन परिणाम के भय से मुक्त होता है, तब जीवन में असीम शांति और सफलता मिलती है।",
                "आज का दिन सकारात्मक भाव और ईश्वर पर विश्वास के साथ शुरू करें।",
            ]
        },
        "te": {
            "title": "భగవద్గీత అమృతవాణి — కర్మణ్యేవాధికారస్తే (కర్మ యోగం)",
            "lines": [
                "భగవద్గీతలోని ఈ పవిత్ర శ్లోకం మనకు నిజమైన ప్రశాంతతను, జీవన మార్గాన్ని అందిస్తుంది.",
                "కర్మణ్యేవాధికారస్తే మా ఫలేషు కదాచన — నీ కర్తవ్యాన్ని నిర్వహించడానికే నీకు అధికారం ఉంది, ఫలితాల మీద కాదు.",
                "ఫలితం గురించి చింతించకుండా మీ పనిని నిష్కామంగా, అంకితభావంతో నిర్వర్తించండి.",
                "ఫలితాన్ని భగవంతుని పాదాల చెంత సమర్పించినప్పుడు మనసు శాంతితో, ఆనందంతో నిండుతుంది.",
                "ఈ రోజును దైవస్మరణతో, నూతన ఉత్సాహంతో ప్రారంభించండి.",
            ]
        }
    },
    {
        "topic": "Inner Peace — Overcoming Anxiety and Fear",
        "verse": "Prasannachetaso Hy Ashu Buddhih Paryavatishthate",
        "lines": [
            "The Gita reveals that for one who has conquered the mind, inner peace is always present.",
            "A serene mind destroys all worldly sorrow and brings clarity of intellect.",
            "Whenever worries cloud your thoughts, turn inward with faith and stillness.",
            "Trust the divine order of life. Whatever happens happens for growth.",
            "May your day be filled with inner calm, grace, and spiritual strength.",
        ],
        "hi": {
            "title": "दैनिक भक्ति एवं आध्यात्मिक विचार — मन की शांति और ईश्वर विश्वास",
            "lines": [
                "जिस मनुष्य का मन शांत और स्थिर है, उसके सारे दुःख स्वतः समाप्त हो जाते हैं।",
                "ईश्वर पर पूर्ण विश्वास और समर्पण ही मन को चिंताओं से मुक्त करता है।",
                "जब भी मन व्याकुल हो, कुछ पल शांत बैठकर प्रभु का स्मरण करें।",
                "जो हुआ अच्छे के लिए हुआ, जो हो रहा है अच्छा हो रहा है, जो होगा वह भी अच्छा ही होगा।",
                "आज का दिन प्रेम, करुणा और शांति के साथ व्यतीत करें।",
            ]
        },
        "te": {
            "title": "ఆధ్యాత్మిక చింతన — ప్రశాంతమైన మనస్సు మరియు దైవభక్తి",
            "lines": [
                "మనస్సును అదుపులో ఉంచుకున్న వ్యక్తికి ఎల్లప్పుడూ ఆత్మశాంతి లభిస్తుంది.",
                "దైవంపై సంపూర్ణ విశ్వాసం ఉంచినప్పుడు ఎలాంటి భయాలు, ఆందోళనలు మనల్ని కలవరపెట్టలేవు.",
                "ప్రతిరోజూ కొన్ని క్షణాలు ప్రశాంతంగా కూర్చుని అంతర్గత దైవత్వాన్ని స్మరించుకోండి.",
                "జరిగినదంతా మంచిదే, జరుగుతున్నది మంచిదే, జరగబోయేది కూడా మంచిదే.",
                "ఈ రోజును దైవానుగ్రహంతో, సంతోషంతో గడపండి.",
            ]
        }
    },
    {
        "topic": "The Power of Faith and Devotion",
        "verse": "Shraddhamayo Yam Purusho Yo Yach-Chhraddhah Sa Eva Sah",
        "lines": [
            "We are made by our faith. What our faith is, so we become.",
            "Keep your thoughts pure, your heart humble, and your devotion steady.",
            "God is the friend of all beings, always seated within the heart of everyone.",
            "Offer every small deed as a prayer, and your entire day becomes sacred.",
            "May divine blessings surround you and your loved ones today.",
        ],
        "hi": {
            "title": "दैनिक भगवद्गीता सार — श्रद्धा और भक्ति की शक्ति",
            "lines": [
                "मनुष्य अपनी श्रद्धा से ही बनता है, जैसी उसकी श्रद्धा होती है वैसा ही वह बन जाता है।",
                "अपने हृदय को शुद्ध, मन को शांत और ईश्वर के प्रति निष्ठावान रखें।",
                "ईश्वर हर प्राणी के हृदय में निवास करते हैं और हमेशा हमारे साथ हैं।",
                "अपने हर कार्य को ईश्वर की पूजा मानकर करें, जीवन आनंदमय हो जाएगा।",
                "प्रभु की कृपा सदा आपके और आपके परिवार पर बनी रहे।",
            ]
        },
        "te": {
            "title": "భగవద్గీత సందేశం — విశ్వాసం మరియు భక్తి ప్రభావం",
            "lines": [
                "మనిషి యొక్క నమ్మకమే అతని వ్యక్తిత్వాన్ని తీర్చిదిద్దుతుంది. ఏది విశ్వసిస్తే అదే అవుతాడు.",
                "హృదయాన్ని పవిత్రంగా, మనసును నిర్మలంగా ఉంచి భగవంతుని ఆరాధించండి.",
                "భగవంతుడు ప్రతి ప్రాణి హృదయంలో కొలువై ఉంటాడు, మనల్ని ఎల్లప్పుడూ రక్షిస్తుంటాడు.",
                "మీరు చేసే ప్రతి పనిని భగవదర్పణంగా భావిస్తే రోజంతా పవిత్రంగా మారుతుంది.",
                "దైవాశీస్సులు మీపై, మీ కుటుంబంపై ఎల్లప్పుడూ ఉండాలని ప్రార్థిస్తున్నాము.",
            ]
        }
    }
]


def generate_devotional_content(lang: str = "en") -> dict:
    today_index = datetime.now().day % len(DEVOTIONAL_LESSONS)
    item = DEVOTIONAL_LESSONS[today_index]

    title = f"Daily Spiritual Wisdom: {item['topic']}"
    script_lines = item["lines"]
    full_script = " ".join(script_lines)

    description = (
        f"🕉️ Daily Spiritual Wisdom & Devotional Reflection | {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"📖 Topic: {item['topic']}\n"
        f"📜 Sacred Verse: {item['verse']}\n\n"
        f"{' '.join(script_lines[:3])}\n\n"
        f"May divine peace, clarity, and blessings accompany your day.\n\n"
        f"#Devotional #BhagavadGita #Spiritual #InnerPeace #Meditation #DailyWisdom #DailyPrayer"
    )
    tags = ["devotional", "bhagavad gita", "spiritual", "spirituality", "meditation",
            "inner peace", "hinduism", "wisdom", "daily prayer", "karma yoga", "peace"]

    return {
        "category": "devotional",
        "title": title,
        "script_lines": script_lines,
        "full_script": full_script,
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "-3%",
    }
