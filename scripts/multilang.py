"""
Multilingual Support Module for Auto YouTube Pipeline
Provides translations, localized content, and Edge TTS voice mapping for:
- English (en)
- Hindi (hi)
- Telugu (te)
"""

from datetime import datetime
from logger import get_logger

logger = get_logger("multilang")

LANGUAGES = {
    "en": {
        "name": "English",
        "tag": "English",
        "voice_male": "en-US-GuyNeural",
        "voice_female": "en-US-JennyNeural",
        "kids_male": "en-US-JackNeural",
        "kids_female": "en-US-JennyNeural",
    },
    "hi": {
        "name": "Hindi",
        "tag": "हिंदी (Hindi)",
        "voice_male": "hi-IN-MadhurNeural",
        "voice_female": "hi-IN-SwaraNeural",
        "kids_male": "hi-IN-MadhurNeural",
        "kids_female": "hi-IN-SwaraNeural",
    },
    "te": {
        "name": "Telugu",
        "tag": "తెలుగు (Telugu)",
        "voice_male": "te-IN-MohanNeural",
        "voice_female": "te-IN-ShrutiNeural",
        "kids_male": "te-IN-MohanNeural",
        "kids_female": "te-IN-ShrutiNeural",
    },
}

# Rich translations for pre-written and curated category content
TRANSLATIONS = {
    # ── Kids Stories ──
    "The Brave Little Rabbit": {
        "hi": {
            "title": "बहादुर छोटा खरगोश (The Brave Little Rabbit)",
            "lines": [
                "एक समय की बात है, कोको नाम का एक छोटा खरगोश रहता था जिसे नई जगहें देखना बहुत पसंद था।",
                "एक सुनहरी सुबह, उसे सतरंगी गाजरों से भरा एक जादुई बगीचा मिला।",
                "उसने वे स्वादिष्ट गाजरें अपने सभी जंगल के दोस्तों के साथ बांटी।",
                "सभी ने मिलकर जंगल में अब तक की सबसे शानदार दावत मनाई!",
            ],
        },
        "te": {
            "title": "ధైర్యవంతుడైన చిన్న కుందేలు (The Brave Little Rabbit)",
            "lines": [
                "అనగనగా ఒక అడవిలో కోకో అనే చిన్న కుందేలు ఉండేది. దానికి కొత్త విషయాలు అన్వేషించడం చాలా ఇష్టం.",
                "ఒక అందమైన ఉదయం, దానికి రంగురంగుల క్యారెట్లతో నిండిన ఒక రహస్య తోట కనిపించింది.",
                "కోకో ఆ క్యారెట్లను తన స్నేహితులందరితో ఆనందంగా పంచుకుంది.",
                "అందరూ కలిసి అడవిలో ఒక గొప్ప పండుగను జరుపుకున్నారు!",
            ],
        },
    },
    "The Magic Paintbrush": {
        "hi": {
            "title": "जादुई तूलिका (The Magic Paintbrush)",
            "lines": [
                "टॉमी को एक जादुई तूलिका मिली जिससे वह जो भी बनाता, वह सच हो जाता था।",
                "उसने एक सुंदर तितली बनाई, और वह फुर्र से आसमान में उड़ गई।",
                "उसने एक बड़ा महल बनाया, और वह उसके बगीचे में प्रकट हो गया।",
                "लेकिन सबसे अनमोल चीज़ जो उसने बनाई, वह थी उसकी माँ के चेहरे पर एक प्यारी सी मुस्कान।",
            ],
        },
        "te": {
            "title": "మాయా కుంచె (The Magic Paintbrush)",
            "lines": [
                "టిమ్మీకి ఒక మాయా కుంచె దొరికింది, దానితో ఏది గీసినా ప్రాణం వచ్చేది.",
                "అతను ఒక సీతాకోకచిలుకను గీయగానే, అది గాల్లోకి ఎగిరిపోయింది.",
                "ఒక కోటను గీయగానే, అది పెరట్లో ప్రత్యక్షమైంది.",
                "కానీ అతను గీసిన అన్నిటికంటే అందమైనది తన తల్లి ముఖంలో విరిసిన చిరునవ్వు.",
            ],
        },
    },
    "The Friendly Dragon": {
        "hi": {
            "title": "दोस्ताना ड्रैगन (The Friendly Dragon)",
            "lines": [
                "यह ड्रैगन दूसरे सभी ड्रैगनों से बिल्कुल अलग और अनोखा था।",
                "आग उगलने के बजाय, वह रंग-बिरंगे बुलबुले बनाता था!",
                "गाँव के सभी बच्चे उससे बहुत प्यार करते थे और साथ खेलते थे।",
                "जब गाँव पर संकट आया, तो ड्रैगन ने अपने विशाल बुलबुले से सबकी रक्षा की।",
            ],
        },
        "te": {
            "title": "స్నేహపూర్వక డ్రాగన్ (The Friendly Dragon)",
            "lines": [
                "ఈ డ్రాగన్ ఇతర డ్రాగన్ల కంటే చాలా భిన్నమైనది.",
                "నిప్పులు కక్కడానికి బదులుగా, అది అందమైన బుడగలను ఊదేది!",
                "గ్రామ ప్రజలు, పిల్లలు అందరూ దానితో ఎంతో ఆప్యాయంగా ఉండేవారు.",
                "ఒకరోజు ముప్పు వచ్చినప్పుడు, తన పెద్ద బుడగ కవచంతో అందరినీ కాపాడింది.",
            ],
        },
    },

    # ── Motivational ──
    "Discipline Equals Freedom": {
        "hi": {
            "title": "दैनिक प्रेरणा — अनुशासन ही स्वतंत्रता है",
            "lines": [
                "सच्ची आज़ादी और सफलता अनुशासन के रास्ते से ही मिलती है।",
                "जब आप अपने समय और आदतों पर नियंत्रण रखते हैं, तो आप अपना भविष्य खुद बनाते हैं।",
                "आलस थोड़े समय का आराम देता है, लेकिन अनुशासन जीवन भर का गौरव देता है।",
                "आज ही शुरुआत करें, क्योंकि हर बड़ा सफर एक छोटे कदम से शुरू होता है।",
            ],
        },
        "te": {
            "title": "రోజువారీ ప్రేరణ — క్రమశిక్షణే నిజమైన స్వేచ్ఛ",
            "lines": [
                "నిజమైన స్వేచ్ఛ క్రమశిక్షణ ద్వారా మాత్రమే సాధ్యమవుతుంది.",
                "మీ సమయాన్ని, అలవాట్లను మీరు నియంత్రించినప్పుడు మీ భవిష్యత్తు మీ చేతుల్లో ఉంటుంది.",
                "సోమరితనం క్షణిక సుఖాన్ని ఇస్తుంది, కానీ క్రమశిక్షణ శాశ్వత విజయాన్ని ఇస్తుంది.",
                "ఈ రోజే ప్రారంభించండి, గొప్ప విజయం ఒక్క అడుగుతోనే మొదలవుతుంది.",
            ],
        },
    },
    "Rise Every Day": {
        "hi": {
            "title": "दैनिक प्रेरणा — हर दिन नया सवेरा, नई उम्मीद",
            "lines": [
                "हर सुबह आपके लिए एक नया अवसर और नई संभावना लेकर आती है।",
                "बीते हुए कल की गलतियों को भूलकर आज को बेहतर बनाने में अपनी पूरी शक्ति लगाएं।",
                "निरंतर प्रयास और सकारात्मक सोच ही आपको अपनी मंजिल तक पहुंचाएगी।",
                "उठो, जागो और तब तक मत रुको जब तक लक्ष्य प्राप्त न हो जाए।",
            ],
        },
        "te": {
            "title": "రోజువారీ ప్రేరణ — ప్రతిరోజూ కొత్త ఉత్సాహంతో ముందడుగు",
            "lines": [
                "ప్రతి ఉదయం సరికొత్త అవకాశాన్ని, నూతన శక్తిని మోసుకొస్తుంది.",
                "నిన్నటి తప్పుల గురించి ఆలోచించక, నేటి రోజును విజయవంతం చేసుకోవడానికి కృషి చేయండి.",
                "నిరంతర సాధన, సానుకూల దృక్పథం మిమ్మల్ని గమ్యానికి చేరుస్తాయి.",
                "మేల్కొనండి, లక్ష్యం చేరేవరకు విశ్రమించకండి.",
            ],
        },
    },

    # ── Health ──
    "Morning Routine for Energy All Day": {
        "hi": {
            "title": "दैनिक स्वास्थ्य — दिनभर ऊर्जा बनाए रखने की दिनचर्या",
            "lines": [
                "सुबह उठने के 30 मिनट के भीतर कम से कम 500 मिलीलीटर पानी जरूर पिएं।",
                "पहले घंटे में 10 मिनट धूप लें, इससे आपकी नींद और ऊर्जा चक्र बेहतर होता है।",
                "10 मिनट हल्का व्यायाम या स्ट्रेचिंग करें, जिससे शरीर में स्फूर्ति बनी रहे।",
                "पौष्टिक और प्रोटीन से भरपूर नाश्ता करें और दिनभर तरोताज़ा महसूस करें।",
            ],
        },
        "te": {
            "title": "రోజువారీ ఆరోగ్యం — రోజంతా ఉల్లాసంగా ఉండే మార్నింగ్ రొటీన్",
            "lines": [
                "నిద్రలేచిన 30 నిమిషాల్లోపు అర లీటరు గోరువెచ్చని నీటిని తాగండి.",
                "మొదటి గంటలో 10 నిమిషాల పాటు లేలేత ఎండలో నడవండి, ఇది శరీరానికి ఎంతో మేలు చేస్తుంది.",
                "రోజూ 10 నిమిషాల పాటు సాధారణ వ్యాయామం లేదా యోగా సాధన చేయండి.",
                "ప్రోటీన్ అధికంగా ఉండే పోషకాహార అల్పాహారాన్ని తీసుకోండి.",
            ],
        },
    },
    "The 3-2-1 Sleep Rule": {
        "hi": {
            "title": "दैनिक स्वास्थ्य — बेहतर नींद का 3-2-1 नियम",
            "lines": [
                "सोने से 3 घंटे पहले भारी भोजन करना बंद कर दें।",
                "सोने से 2 घंटे पहले काम और तनाव वाले विचार छोड़ दें।",
                "सोने से 1 घंटा पहले मोबाइल और टीवी स्क्रीन से पूरी तरह दूर रहें।",
                "यह सरल नियम आपकी नींद की गुणवत्ता और मानसिक शांति को कई गुना बढ़ा देगा।",
            ],
        },
        "te": {
            "title": "రోజువారీ ఆరోగ్యం — చక్కని నిద్ర కోసం 3-2-1 నియమం",
            "lines": [
                "పడుకోవడానికి 3 గంటల ముందే రాత్రి భోజనం పూర్తి చేయండి.",
                "నిద్రకు 2 గంటల ముందు పనులను, మానసిక ఒత్తిడిని పక్కన పెట్టండి.",
                "పడుకోవడానికి 1 గంట ముందు స్మార్ట్‌ఫోన్, టీవీ స్క్రీన్లకు దూరంగా ఉండండి.",
                "ఈ చిన్న మార్పు మీ నిద్ర నాణ్యతను, మరుసటి రోజు ఉత్సాహాన్ని అద్భుతంగా పెంచుతుంది.",
            ],
        },
    },

    # ── Books ──
    "Atomic Habits": {
        "hi": {
            "title": "किताब का सार: एटॉमिक हैबिट्स (जेम्स क्लियर)",
            "lines": [
                "छोटे-छोटे सुधार समय के साथ बहुत बड़े परिणाम देते हैं।",
                "लक्ष्यों पर ध्यान केंद्रित करने के बजाय अच्छी आदतों की प्रणाली बनाएं।",
                "अपनी पहचान बदलें: आप जो बनना चाहते हैं, वैसा आचरण अपनाएं।",
                "अच्छी आदतों को आसान और आकर्षक बनाएं, बुरी आदतों को मुश्किल बनाएं।",
            ],
        },
        "te": {
            "title": "పుస్తక సారాంశం: అటామిక్ హ్యాబిట్స్ (జేమ్స్ క్లియర్)",
            "lines": [
                "ప్రతిరోజూ చేసే ఒక్క శాతం చిన్న మార్పు కాలక్రమేణా అద్భుతమైన ఫలితాలను ఇస్తుంది.",
                "లక్ష్యాల కంటే బలమైన అలవాట్ల వ్యవస్థను రూపొందించడం ముఖ్యం.",
                "మీ గుర్తింపును మార్చుకోండి: మీరు సాధించాలనుకున్న వ్యక్తిలా ఆలోచించండి.",
                "మంచి అలవాట్లను సులభంగా, ఆకర్షణీయంగా మార్చుకోండి; చెడు అలవాట్లకు దూరంగా ఉండండి.",
            ],
        },
    },
    "Rich Dad Poor Dad": {
        "hi": {
            "title": "किताब का सार: रिच डैड पुअर डैड (रॉबर्ट कियोसाकी)",
            "lines": [
                "अमीर लोग पैसे के लिए काम नहीं करते, वे पैसे से अपने लिए काम करवाते हैं।",
                "सच्ची संपत्ति वह है जो आपकी जेब में पैसे डाले, न कि जेब से पैसे निकाले।",
                "वित्तीय साक्षरता जीवन की सबसे महत्वपूर्ण कौशलों में से एक है।",
                "जोखिम को समझदारी से प्रबंधित करें और नए अवसर तलाशें।",
            ],
        },
        "te": {
            "title": "పుస్తక సారాంశం: రిచ్ డాడ్ పూర్ డాడ్ (రాబర్ట్ కియోసాకి)",
            "lines": [
                "ధనవంతులు డబ్బు కోసం పనిచేయరు, డబ్బు వారికోసం పనిచేసేలా చేస్తారు.",
                "ఆస్తులకి, అప్పులకి మధ్య ఉన్న తేడాను గుర్తించడం అతి ముఖ్యమైన ఆర్థిక పాఠం.",
                "ఆర్థిక విజ్ఞానం సంపద సృష్టికి అసలైన పునాది.",
                "రిస్క్ మేనేజ్‌మెంట్ ద్వారా స్థిరమైన సంపదను నిర్మించుకోండి.",
            ],
        },
    },

    # ── Cooking ──
    "Recipe of the Day": {
        "hi": {
            "title": "आज का खास व्यंजन — स्वादिष्ट और पौष्टिक",
            "lines": [
                "आज की रेसिपी ताज़ी सामग्री और सुगंधित मसालों से तैयार की गई है।",
                "धीमी आंच पर पकाने से सभी मसालों का स्वाद निखर कर आता है।",
                "गरमागरम परोसें और अपने परिवार के साथ इस लज़ीज़ स्वाद का आनंद लें।",
                "स्वस्थ खाएं, खुश रहें और नई-नई रेसिपीज़ सीखते रहें!",
            ],
        },
        "te": {
            "title": "నేటి రుచికరమైన వంటకం — ఆరోగ్యం మరియు రుచి",
            "lines": [
                "నేటి వంటకం తాజా పదార్థాలు, పరిమళభరిత మసాలాలతో సులువుగా తయారు చేసుకోవచ్చు.",
                "సన్నని మంటపై ఉడికించడం వల్ల రుచి అద్భుతంగా కుదురుతుంది.",
                "వేడివేడిగా వడ్డించి కుటుంబ సభ్యులతో కలిసి ఆనందించండి.",
                "ఆరోగ్యకరమైన ఆహారం తీసుకోండి, సంతోషంగా జీవించండి!",
            ],
        },
    },
}


def get_voice(lang: str, voice_role: str = "female") -> str:
    """Return the Edge TTS voice name for a given language and role."""
    config = LANGUAGES.get(lang, LANGUAGES["en"])
    if "kids" in voice_role:
        return config.get("kids_female" if "female" in voice_role else "kids_male")
    if "male" in voice_role:
        return config.get("voice_male")
    return config.get("voice_female")


def translate_content(content: dict, lang: str) -> dict:
    """
    Translate/localize content for the target language:
    - Sets appropriate TTS voice
    - Uses native script translations where available
    - Adds language tags and hashtags
    """
    if lang == "en":
        return content

    cat = content.get("category", "")
    title = content.get("title", "")
    voice_role = content.get("voice", "default_female")
    target_voice = get_voice(lang, voice_role)

    # Check for direct translation matches in our translation dictionary
    matched = None
    for key, trans_dict in TRANSLATIONS.items():
        if key.lower() in title.lower():
            matched = trans_dict.get(lang)
            break

    if matched:
        new_title = matched["title"]
        new_lines = matched["lines"]
        new_script = " ".join(new_lines)
    else:
        # Generative / RSS fallback localization
        lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
        lang_name = lang_info["name"]
        lang_tag = lang_info["tag"]

        if lang == "hi":
            prefix = "[हिंदी] "
            closing = f"आज का {cat} अपडेट सुनने के लिए धन्यवाद। चैनल को लाइक और सब्सक्राइब जरूर करें!"
            new_title = f"{prefix}{title}"
            new_lines = list(content.get("script_lines", []))
            if new_lines:
                new_lines.append(closing)
            new_script = " ".join(new_lines)
        elif lang == "te":
            prefix = "[తెలుగు] "
            closing = f"నేటి {cat} సమాచారం విన్నందుకు ధన్యవాదాలు. మరిన్ని అప్‌డేట్స్ కోసం లైక్, సబ్‌స్క్రైబ్ చేయండి!"
            new_title = f"{prefix}{title}"
            new_lines = list(content.get("script_lines", []))
            if new_lines:
                new_lines.append(closing)
            new_script = " ".join(new_lines)
        else:
            new_title = f"[{lang.upper()}] {title}"
            new_lines = content.get("script_lines", [])
            new_script = content.get("full_script", "")

    # Localize tags and description
    lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
    tags = list(content.get("tags", []))
    tags.extend([lang_info["name"].lower(), lang, f"{cat} in {lang_info['name'].lower()}"])

    description = (
        f"{new_title}\n\n"
        f"{new_script[:200]}...\n\n"
        f"🌐 Language: {lang_info['tag']}\n"
        f"🔔 Daily automated upload. Subscribe for more!\n\n"
        f"#{cat.title()} #{lang_info['name']} #{cat.title()}News #Shorts #DailyUpdates"
    )

    return {
        "category": cat,
        "title": new_title[:100],
        "script_lines": new_lines,
        "full_script": new_script,
        "description": description,
        "tags": list(set(tags)),
        "voice": target_voice,
        "rate": content.get("rate", "+0%"),
    }
