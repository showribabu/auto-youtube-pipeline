from dotenv import load_dotenv
import os
import shutil
import sys

# Load .env from config/ directory first, then fallback to cwd
ENV_FILES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", ".env"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", ".env"),
    os.path.join(os.getcwd(), "config", ".env"),
]
for env_file in ENV_FILES:
    abs_env = os.path.abspath(env_file)
    if os.path.exists(abs_env):
        load_dotenv(abs_env)
        break
load_dotenv()  # also try default cwd location

# ─── Paths ──────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR    = os.path.join(BASE_DIR, "config")
BASE = BASE_DIR
SCRIPTS_DIR   = os.path.join(BASE_DIR, "scripts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR    = os.path.join(BASE_DIR, "output")
LOGS_DIR      = os.path.join(BASE_DIR, "logs")
CACHE_DIR     = os.path.join(BASE_DIR, "cache")
ASSETS_DIR    = os.path.join(BASE_DIR, "assets")
FONT_DIR      = os.path.join(ASSETS_DIR, "dejavu-fonts-ttf-2.37", "ttf")

for d in (OUTPUT_DIR, LOGS_DIR, CACHE_DIR):
    os.makedirs(d, exist_ok=True)

# Cross-platform ffmpeg: prefer PATH, fallback to env var
FFMPEG  = os.getenv("FFMPEG_PATH") or shutil.which("ffmpeg") or ""
FFPROBE = os.getenv("FFPROBE_PATH") or shutil.which("ffprobe") or ""

# ─── YouTube / Google ──────────────────────────────────
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN= os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# ─── TTS / Voice ───────────────────────────────────────
DEFAULT_VOICE_MALE   = os.getenv("DEFAULT_VOICE_MALE", "en-US-GuyNeural")
DEFAULT_VOICE_FEMALE = os.getenv("DEFAULT_VOICE_FEMALE", "en-US-SaraNeural")
KIDS_VOICE_MALE      = os.getenv("KIDS_VOICE_MALE", "en-US-JackNeural")
KIDS_VOICE_FEMALE    = os.getenv("KIDS_VOICE_FEMALE", "en-US-JennyNeural")

# ─── Video settings ────────────────────────────────────
OUTPUT_WIDTH, OUTPUT_HEIGHT  = (lambda s: tuple(int(x) for x in s.split("x")))(os.getenv("OUTPUT_RESOLUTION", "1280x720"))
OUTPUT_FPS                   = int(os.getenv("OUTPUT_FPS", "30"))
DEFAULT_DURATION             = int(os.getenv("DEFAULT_VIDEO_DURATION", "60"))
MAX_VIDEOS_PER_DAY           = int(os.getenv("MAX_VIDEOS_PER_DAY", "50"))

# ─── Schedule (cron) ───────────────────────────────────
SCHEDULES = {
    "kids":            os.getenv("SCHEDULE_KIDS", "0 8 * * *"),
    "news":            os.getenv("SCHEDULE_NEWS", "0 7 * * *"),
    "weather":         os.getenv("SCHEDULE_WEATHER", "0 6 * * *"),
    "facts":           os.getenv("SCHEDULE_FACTS", "0 12 * * *"),
    "motivational":    os.getenv("SCHEDULE_MOTIVATIONAL", "0 18 * * *"),
}

# New category schedules
SCHEDULES["tech"]           = os.getenv("SCHEDULE_TECH", "30 7 * * *")
SCHEDULES["crypto"]         = os.getenv("SCHEDULE_CRYPTO", "0 9 * * *")
SCHEDULES["health"]         = os.getenv("SCHEDULE_HEALTH", "30 8 * * *")
SCHEDULES["history"]        = os.getenv("SCHEDULE_HISTORY", "0 10 * * *")
SCHEDULES["gaming"]         = os.getenv("SCHEDULE_GAMING", "0 15 * * *")
SCHEDULES["language"]       = os.getenv("SCHEDULE_LANGUAGE", "30 9 * * *")
SCHEDULES["books"]          = os.getenv("SCHEDULE_BOOKS", "0 11 * * *")
SCHEDULES["cooking"]        = os.getenv("SCHEDULE_COOKING", "0 13 * * *")

# Language settings
ENABLED_LANGUAGES = os.getenv("ENABLED_LANGUAGES", "en,hi,te").split(",")

# ─── Retry ─────────────────────────────────────────────
MAX_RETRIES   = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY   = int(os.getenv("RETRY_DELAY_SECONDS", "30"))

# ─── Logging ───────────────────────────────────────────
LOG_LEVEL     = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE", os.path.join(LOGS_DIR, "pipeline.log"))
