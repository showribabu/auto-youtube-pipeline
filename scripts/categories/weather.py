import urllib.request
import json
import re
from datetime import datetime
from logger import get_logger
logger = get_logger("weather")

REGIONS_BY_LANG = {
    "te": [
        {"name": "హైదరాబాద్ (Hyderabad)", "query": "Hyderabad,India", "loc_te": "హైదరాబాద్", "loc_hi": "हैदराबाद"},
        {"name": "విశాఖపట్నం (Visakhapatnam)", "query": "Visakhapatnam,India", "loc_te": "విశాఖపట్నం", "loc_hi": "विशाखापत्तनम"},
        {"name": "విజయవాడ (Vijayawada)", "query": "Vijayawada,India", "loc_te": "విజయవాడ", "loc_hi": "विजयवाड़ा"},
        {"name": "తిరుపతి (Tirupati)", "query": "Tirupati,India", "loc_te": "తిరుపతి", "loc_hi": "तिरुपति"},
        {"name": "బెంగళూరు (Bengaluru)", "query": "Bengaluru,India", "loc_te": "బెంగళూరు", "loc_hi": "बेंगलुरु"},
    ],
    "hi": [
        {"name": "New Delhi", "query": "New+Delhi,India", "loc_te": "న్యూఢిల్లీ", "loc_hi": "नई दिल्ली"},
        {"name": "Mumbai", "query": "Mumbai,India", "loc_te": "ముంబై", "loc_hi": "मुंबई"},
        {"name": "Jaipur", "query": "Jaipur,India", "loc_te": "జైపూర్", "loc_hi": "जयपुर"},
        {"name": "Varanasi", "query": "Varanasi,India", "loc_te": "వారణాసి", "loc_hi": "वाराणसी"},
        {"name": "Lucknow", "query": "Lucknow,India", "loc_te": "లక్నో", "loc_hi": "लखनऊ"},
    ],
    "en": [
        {"name": "Hyderabad", "query": "Hyderabad,India", "loc_te": "హైదరాబాద్", "loc_hi": "Hyderabad"},
        {"name": "New Delhi", "query": "New+Delhi,India", "loc_te": "న్యూఢిల్లీ", "loc_hi": "New Delhi"},
        {"name": "Bengaluru", "query": "Bengaluru,India", "loc_te": "బెంగళూరు", "loc_hi": "Bengaluru"},
        {"name": "Mumbai", "query": "Mumbai,India", "loc_te": "ముంబై", "loc_hi": "Mumbai"},
        {"name": "London", "query": "London,UK", "loc_te": "లండన్", "loc_hi": "London"},
        {"name": "New York", "query": "New+York,USA", "loc_te": "న్యూయార్క్", "loc_hi": "New York"},
        {"name": "Dubai", "query": "Dubai,UAE", "loc_te": "దుబాయ్", "loc_hi": "Dubai"},
    ]
}


def fetch_weather(location_name: str, query: str) -> dict | None:
    try:
        url = f"https://wttr.in/{query}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "AutoYouTubePipeline/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        current = data["current_condition"][0]
        temp_c = int(current.get("temp_C", 26))
        desc = current.get("weatherDesc", [{}])[0].get("value", "Partly Cloudy")
        humidity = int(current.get("humidity", "55"))
        wind_kmph = int(current.get("windspeedKmph", "12"))
        feels_like = int(current.get("FeelsLikeC", temp_c))
        return {
            "location": location_name,
            "temperature": temp_c,
            "description": desc,
            "humidity": humidity,
            "wind_speed": wind_kmph,
            "feels_like": feels_like,
        }
    except Exception as e:
        logger.warning(f"Live weather fetch failed for {location_name}: {e}")
        return None


def generate_weather_content(lang: str = "en") -> dict:
    regions = REGIONS_BY_LANG.get(lang, REGIONS_BY_LANG["en"])
    region = regions[datetime.now().day % len(regions)]
    loc_display = region["name"]
    loc_te = region.get("loc_te", loc_display)
    loc_hi = region.get("loc_hi", loc_display)
    wx = fetch_weather(loc_display, region["query"])

    if not wx:
        wx = {
            "location": loc_display,
            "temperature": 27,
            "description": "Clear and Sunny",
            "humidity": 50,
            "wind_speed": 10,
            "feels_like": 28,
        }

    temp_c = wx["temperature"]
    temp_f = round(temp_c * 9 / 5 + 32)
    desc = wx["description"]
    humidity = wx["humidity"]
    wind = wx["wind_speed"]
    feels = wx["feels_like"]

    if lang == "te":
        title = f"{loc_te} వాతావరణ సమాచారం — {temp_c}°C ({desc})"
        script_lines = [
            f"నమస్కారం! ఇది మీ రోజువారీ ప్రత్యక్ష వాతావరణ సమాచారం.",
            f"{loc_te}లో ప్రస్తుత ఉష్ణోగ్రత {temp_c} డిగ్రీల సెల్సియస్ గా నమోదైంది.",
            f"వాతావరణ పరిస్థితి: {desc}, మరియు గాలిలో తేమ {humidity} శాతం.",
            f"గంటకు {wind} కిలోమీటర్ల వేగంతో చల్లని గాలులు వీస్తున్నాయి.",
            f"ఈ రోజు మీ పనులన్నీ విజయవంతంగా, ఆహ్లాదకరంగా సాగాలని కోరుకుంటున్నాం!",
        ]
        description = (
            f"🌤️ {loc_te} ప్రత్యక్ష వాతావరణ నివేదిక\n\n"
            f"🌡️ ఉష్ణోగ్రత: {temp_c}°C / {temp_f}°F (ఫీల్స్ లైక్: {feels}°C)\n"
            f"☁️ వాతావరణం: {desc}\n"
            f"💧 తేమ: {humidity}% | 💨 గాలి వేగం: {wind} km/h\n\n"
            f"📅 తేదీ: {datetime.now().strftime('%d %B, %Y')}\n\n"
            f"#Weather #TeluguWeather #{loc_te} #LiveWeather #Shorts"
        )
        tags = ["weather", "telugu weather", loc_te, "daily forecast", "shorts", "viral"]
    elif lang == "hi":
        title = f"{loc_hi} आज का मौसम समाचार — {temp_c}°C ({desc})"
        script_lines = [
            f"नमस्कार! प्रस्तुत है आज का ताज़ा और सटीक मौसम समाचार।",
            f"{loc_hi} में इस समय तापमान {temp_c} डिग्री सेल्सियस दर्ज किया गया है।",
            f"मौसम की स्थिति: {desc}, और हवा में नमी {humidity} प्रतिशत है।",
            f"हवा की गति लगभग {wind} किलोमीटर प्रति घंटा बनी हुई है।",
            f"आपका आज का दिन सुखद, ऊर्जावान और मंगलमय रहे!",
        ]
        description = (
            f"🌤️ {loc_hi} ताज़ा मौसम रिपोर्ट\n\n"
            f"🌡️ तापमान: {temp_c}°C / {temp_f}°F (महसूस: {feels}°C)\n"
            f"☁️ मौसम: {desc}\n"
            f"💧 नमी: {humidity}% | 💨 हवा: {wind} km/h\n\n"
            f"📅 दिनांक: {datetime.now().strftime('%d %B, %Y')}\n\n"
            f"#Weather #HindiWeather #{loc_hi} #Mausam #Shorts"
        )
        tags = ["weather", "hindi weather", loc_hi, "mausam update", "shorts", "viral"]
    else:
        title = f"Weather Update: {loc_display} — {temp_c}°C ({desc})"
        script_lines = [
            f"Here is your live daily weather forecast for {loc_display}.",
            f"Current temperature is {temp_c} degrees Celsius, feeling like {feels} degrees.",
            f"Atmospheric condition: {desc}, with humidity around {humidity} percent.",
            f"Wind speed is blowing at {wind} kilometers per hour.",
            f"Have a wonderful and productive day ahead in {loc_display}!",
        ]
        description = (
            f"🌤️ Live Weather Report: {loc_display}\n\n"
            f"🌡️ Temperature: {temp_c}°C / {temp_f}°F (Feels like: {feels}°C)\n"
            f"☁️ Sky: {desc}\n"
            f"💧 Humidity: {humidity}% | 💨 Wind: {wind} km/h\n\n"
            f"📅 Date: {datetime.now().strftime('%B %d, %Y')}\n\n"
            f"#Weather #WeatherForecast #{loc_display.replace(' ', '')} #LiveWeather #Shorts"
        )
        tags = ["weather", "forecast", "climate", loc_display.lower(), "shorts", "viral"]

    full_script = " ".join(script_lines)

    return {
        "category": "weather",
        "title": title,
        "script_lines": script_lines,
        "full_script": full_script,
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "+0%",
    }
