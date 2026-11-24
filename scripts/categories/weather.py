import urllib.request
import json
import re
from datetime import datetime
from config import SCHEDULES, MAX_VIDEOS_PER_DAY, RETRY_DELAY, MAX_RETRIES
from logger import get_logger
logger = get_logger("weather")

REGIONS = [
    {"name": "New York", "query": "New York weather"},
    {"name": "London", "query": "London UK weather"},
    {"name": "Tokyo", "query": "Tokyo Japan weather"},
    {"name": "Sydney", "query": "Sydney Australia weather"},
    {"name": "Dubai", "query": "Dubai UAE weather"},
    {"name": "Paris", "query": "Paris France weather"},
    {"name": "Mumbai", "query": "Mumbai India weather"},
    {"name": "São Paulo", "query": "Sao Paulo Brazil weather"},
]


def fetch_weather(region: str) -> dict | None:
    try:
        url = f"https://wttr.in/{region.replace(' ', '+')}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        current = data["current_condition"][0]
        area = data["nearest_area"][0]["areaName"][0]["value"]
        temp_c = int(current.get("temp_C", 20))
        desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
        humidity = int(current.get("humidity", "50"))
        wind_kmph = int(current.get("windspeedKmph", "15"))
        feels_like = int(current.get("FeelsLikeC", temp_c))
        return {
            "location": area,
            "temperature": temp_c,
            "description": desc,
            "humidity": humidity,
            "wind_speed": wind_kmph,
            "feels_like": feels_like,
        }
    except Exception as e:
        logger.warning(f"Weather fetch failed for {region}: {e}")
        return None


def generate_weather_content() -> dict:
    region = REGIONS[datetime.now().day % len(REGIONS)]
    wx = fetch_weather(region["name"])

    if not wx:
        return _fallback_weather(region["name"])

    temp_f = round(wx["temperature"] * 9 / 5 + 32)
    title = f"Weather Update: {wx['location']} — {wx['temperature']}°C ({wx['description']})"

    script_lines = [
        f"Here is your weather report for {wx['location']}.",
        f"Current temperature is {wx['temperature']} degrees Celsius or {temp_f} Fahrenheit.",
        f"It feels like {wx['feels_like']} degrees Celsius.",
        f"Conditions: {wx['description']}.",
        f"Humidity is at {wx['humidity']} percent.",
        f"Wind speed is {wx['wind_speed']} kilometers per hour.",
        f"Stay safe and dress appropriately for the weather.",
    ]

    description = (
        f"🌤️ Weather Report for {wx['location']}\n\n"
        f"Temperature: {wx['temperature']}°C | {temp_f}°F\n"
        f"Condition: {wx['description']}\n"
        f"Humidity: {wx['humidity']}% | Wind: {wx['wind_speed']} km/h\n\n"
        f"Generated automatically on {datetime.now().strftime('%B %d, %Y')}.\n\n"
        f"#Weather #Forecast #{wx['location'].replace(' ', '')} #Climate"
    )
    tags = ["weather", "forecast", "climate", wx["location"].lower(),
            "temperature", "news", "daily forecast"]

    return {
        "category": "weather",
        "title": title,
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": description,
        "tags": tags,
        "voice": "default_female",
        "rate": "-2%",
    }


def _fallback_weather(location: str) -> dict:
    logger.warning(f"Using fallback weather for {location}")
    script_lines = [
        f"Here is your weather update for {location}.",
        "Today the weather is expected to be pleasant with clear skies.",
        "Temperatures are mild and conditions are favorable for outdoor activities.",
        "Remember to check local forecasts for the most accurate information.",
    ]
    return {
        "category": "weather",
        "title": f"Weather Update: {location}",
        "script_lines": script_lines,
        "full_script": " ".join(script_lines),
        "description": f"🌤️ Weather for {location}",
        "tags": ["weather", "forecast"],
        "voice": "default_female",
        "rate": "-2%",
    }
