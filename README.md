# Auto YouTube Pipeline

Fully autonomous AI-powered video generation and YouTube upload system. Generates videos across multiple categories and publishes them on schedule — zero daily involvement required.

## What It Does

| Category | Schedule | Content Source |
|----------|----------|----------------|
| Kids Stories | 8:00 AM | Pre-written story library |
| News Roundup | 7:00 AM | RSS feeds (BBC, NYT) + fallback topics |
| Weather Reports | 6:00 AM | wttr.in API (live data) |
| Fun Facts | 12:00 PM | Fact database |
| Motivational Quotes | 6:00 PM | Quote library |

Each video: **AI-generated voiceover** (Microsoft Edge TTS, free) + **custom animated slides** + **auto-upload to YouTube**.

## Setup (One-Time)

### 1. Install Dependencies
```powershell
cd D:\PROJECT\Coding\auto-youtube-pipeline
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Ensure ffmpeg is installed (check PATH):
```powershell
ffmpeg -version
```

### 2. Configure YouTube Access
```powershell
# Copy example config
Copy-Item config\.env.example config\.env

# Edit config\.env — add your Google OAuth credentials
# Then run the auth flow:
python scripts/setup_auth.py
```

This opens a browser where you sign in with your YouTube channel. The refresh token is saved automatically.

### 3. Run Test (No Uploads)
```powershell
python scripts/pipeline.py --run-all --test
```
Verifies all 5 categories generate videos successfully.

### 4. Enable Daily Automation
```powershell
# Option A: Windows Task Scheduler (recommended)
setup_cron.bat

# Option B: Background scheduler process
python scripts/pipeline.py --scheduler
```

For always-on operation, create a Windows Service or use PM2-like tooling. See below.

## Project Structure
```
auto-youtube-pipeline/
├── config/                  # .env, credentials
│   ├── .env.example         # Template
│   └── .env                 # YOUR secrets here
├── scripts/
│   ├── pipeline.py          # Main orchestrator
│   ├── engine.py            # Video/frame generation
│   ├── audio.py             # Text-to-speech (Edge TTS)
│   ├── upload.py            # YouTube API client
│   ├── scheduler.py         # APScheduler cron jobs
│   ├── setup_auth.py        # One-time YouTube OAuth
│   └── categories/          # Content generators
│       ├── kids.py
│       ├── news.py
│       ├── weather.py
│       ├── facts.py
│       └── motivational.py
├── output/                  # Generated videos go here
├── logs/                    # Execution logs
├── cache/                   # Temporary assets
├── requirements.txt
└── README.md
```

## Troubleshooting

- **Video too dark/frozen**: Check ffmpeg path in `.env`
- **Upload fails**: Re-run `python scripts/setup_auth.py`
- **Weather returns bad data**: Region names must be valid — check logs
- **"No module named"**: Reactivate venv and `pip install -r requirements.txt`

## How Videos Are Made

1. **Content Generation** — Category module provides script lines
2. **Title Card** — Pillow-rendered static image (PNG)
3. **Frame Sequence** — Animated slides with text, colored backgrounds, progress dots
4. **Voiceover** — Microsoft Edge TTS (free, no API key needed)
5. **Assembly** — FFmpeg combines frames → video, merges audio
6. **Upload** — Google YouTube Data API v3 (resumable upload)
7. **Thumbnail** — Uploaded alongside video via API

## Next Steps

To make this truly hands-off, consider:
- **Containerize** with Docker for reliable background execution
- **Add health checks** — monitor daily and alert on failures
- **Expand categories** — recipes, history, science, language learning
- **Analytics** — track views/subscribers via YouTube API
