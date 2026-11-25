import urllib.request
import json
import re
from datetime import datetime
from logger import get_logger
logger = get_logger("weather")

REGIONS_BY_LANG = {
    "te": [
        {"name": "Hyderabad", "query": "Hyderabad,India"},
        {"name": "Visakhapatnam", "query": "Visakhapatnam,India"},
        {"name": "Vijayawada", "query": "Vijayawada,India"},
        {"name": "Tirupati", "query": "Tirupati,India"},
        {"name": "Bengaluru", "query": "Bengaluru,India"},
    ],
    "hi": [
        {"name": "New Delhi", "query": "New+Delhi,India"},
        {"name": "Mumbai", "query": "Mumbai,India"},
        {"name": "Jaipur", "query": "Jaipur,India"},
        {"name": "Varanasi", "query": "Varanasi,India"},
        {"name": "Lucknow", "query": "Lucknow,India"},
    ],
    "en": [
        {"name": "Hyderabad", "query": "Hyderabad,India"},
        {"name": "New Delhi", "query": "New+Delhi,India"},
        {"name": "Bengaluru", "query": "Bengaluru,India"},
        {"name": "Mumbai", "query": "Mumbai,India"},
        {"name": "London", "query": "London,UK"},
        {"name": "New York", "query": "New+York,USA"},
        {"name": "Dubai", "query": "Dubai,UAE"},
        {"name": "Singapore", "query": "Singapore"},
    ]
}


def fetch_weather(location_name: str, query: str) -> dict | None:
    try:
        url = f"https://wttr.in/{query}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "AutoYouTubePipeline/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        current = data["current_condition"][0]
        temp_c = int(current.get("temp_C", 25))
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
    loc = region["name"]
    wx = fetch_weather(loc, region["query"])

    if not wx:
        wx = {
            "location": loc,
            "temperature": 27,
            "description": "Pleasant and Clear Skies",
            "humidity": 50,
            "wind_speed": 10,
            "feels_like": 28,
        }

    temp_f = round(wx["temperature"] * 9 / 5 + 32)
    title = f"Weather Update: {wx['location']} — {wx['temperature']}°C ({wx['description']})"

    script_lines = [
        f"Here is your live daily weather forecast for {wx['location']}.",
        f"Current temperature is {wx['temperature']} degrees Celsius, feeling like {wx['feels_like']} degrees.",
        f"Atmospheric condition: {wx['description']}.",
        f"Humidity is recorded at {wx['humidity']} percent, with wind speed around {wx['wind_speed']} kilometers per hour.",
        f"Have a productive and wonderful day ahead in {wx['location']}!",
    ]

    description = (
        f"🌤️ Live Weather Report: {wx['location']}\n\n"
        f"🌡️ Temperature: {wx['temperature']}°C / {temp_f}°F (Feels like: {wx['feels_like']}°C)\n"
        f"☁️ Sky: {wx['description']}\n"
        f"💧 Humidity: {wx['humidity']}% | 💨 Wind: {wx['wind_speed']} km/h\n\n"
        f"📅 Date: {datetime.now().strftime('%B %d, %Y')}\n\n"
        f"#Weather #WeatherForecast #{wx['location'].replace(' ', '')} #LiveWeather #Climate"
    )
    tags = ["weather", "forecast", "climate", wx["location"].lower(),
            "temperature", "news", "daily forecast", "live weather"]

    return {
        "category": "weather",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "-1%",
    }
