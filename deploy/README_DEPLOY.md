# Auto YouTube AI Video Pipeline — Cloud Deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD VPS / VM                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  systemd service: auto-youtube-pipeline              │  │
│  │  Type=simple                                         │  │
│  │  ExecStart=.venv/bin/python scripts/pipeline.py     │  │
│  │               --scheduler                            │  │
│  │  Restart=on-failure                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 6:00 AM │  │ 7:00 AM │  │ 8:00 AM │  │ 12:00 PM│  │
│  │ weather │  │  news   │  │  kids   │  │  facts  │  │
│  │         │  │         │  │         │  │         │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  ┌──────────┐  ┌──────────┐                            │
│  │18:00 PM │  │ motiv.  │                            │
│  │         │  │         │                            │
│  └──────────┘  └──────────┘                            │
│                                                             │
│  Output → YouTube API → Upload → Thumbnail               │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Paths (choose one)

### Path A: Cloud VM via systemd (Recommended — full control, always-on)

1. Provision Linux VM (Ubuntu 22.04, 2GB RAM, 2 CPU, 25GB SSD)
2. SSH into VM: `ssh root@<ip>`
3. Install system deps: `apt install -y python3-venv python3-pip ffmpeg git`
4. Clone repo: `git clone <repo-url> /opt/auto-youtube-pipeline && cd /opt/auto-youtube-pipeline`
5. Setup venv: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
6. Copy fonts (for cross-platform rendering):
   ```bash
   mkdir -p /opt/auto-youtube-pipeline/assets/dejavu-fonts-ttf-2.37/ttf
   # Download DejaVu fonts into that dir (DejaVuSans.ttf, DejaVuSans-Bold.ttf)
   ```
7. Configure: `cp config/.env.example config/.env` and fill in YouTube tokens + ffmpeg path
8. Run auth: `source .venv/bin/activate && python scripts/setup_auth.py` (headless alternative below)
9. Install service: `sudo bash scripts/install_service.sh`
10. Enable: `sudo systemctl enable auto-youtube && sudo systemctl start auto-youtube`

### Path B: Docker (easiest to move between hosts)

```bash
docker build -t auto-youtube-pipeline .
docker run -d \
  -e YOUTUBE_REFRESH_TOKEN=xxx \
  -e GOOGLE_CLIENT_ID=xxx \
  -e GOOGLE_CLIENT_SECRET=xxx \
  -v ./output:/app/output \
  -v ./logs:/app/logs \
  -v ./cache:/app/cache \
  -v ./config:/app/config \
  -v ./scripts:/app/scripts \
  -v ./assets:/app/assets \
  --name auto-youtube \
  auto-youtube-pipeline
```

Or via docker-compose.

### Path C: GitHub Actions (free, no VM cost, scheduled)

A ready workflow exists at `.github/workflows/daily.yml`.

## Headless YouTube Token Setup (on server)

The full browser flow (`setup_auth.py`) is interactive. On a headless server, use this alternative:

```bash
# 1. Create OAuth client ID in Google Cloud Console (Desktop app type)
# 2. Download client_secret.json → /opt/auto-youtube-pipeline/config/client_secret.json
# 3. Run:
source /opt/auto-youtube-pipeline/.venv/bin/activate
python scripts/setup_auth.py
# If browser fails, use the manual flow:
python - << 'EOF'
import os, json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
flow = InstalledAppFlow.from_client_secrets_file(
    "/opt/auto-youtube-pipeline/config/client_secret.json", SCOPES)
creds = flow.run_console() if hasattr(flow, 'run_console') else flow.run_local_server(
    port=8080, open_browser=False)
with open("/opt/auto-youtube-pipeline/config/yt_token.json", "w") as f:
    f.write(creds.to_json())
print("Token saved. Refresh token:", creds.refresh_token)
EOF
```

Better: on a headless box, use `devicecode` flow or run Xvfb. For production simplicity, prefer the **Chromium/Playwright** headless browser approach or just run Xvfb:

```bash
apt install -y xvfb
Xvfb :99 &
export DISPLAY=:99
python scripts/setup_auth.py
```

## Server CPU / Resource Requirements

| Component | CPU | RAM | Storage |
|-----------|-----|-----|---------|
| TTS (Edge) | Low | Low | — |
| Frame gen (Pillow) | Low | Low | — |
| FFmpeg x264 encode | Medium | Low | — |
| YouTube upload | Medium | Low | — |
| systemd + Python | Low | Low | — |

**Recommended VM:** 2 vCPU, 2GB RAM, 25GB SSD. The pipeline is light enough for this.

## Free Tier Options

- **AWS Lightsail:** $3.5/mo (always-free tier available at higher tier)
- **GCP Compute Engine:** Free tier eligible (e2-micro)
- **Azure:** B1s free tier eligible
- **Oracle Cloud:** Always Free tier (2 AMD VMs, 1GB RAM each) — best value for always-on

## Verification Steps

```bash
# After install, check service status
sudo systemctl status auto-youtube

# Watch live logs
sudo journalctl -u auto-youtube -f

# Trigger a manual run
source /opt/auto-youtube-pipeline/.venv/bin/activate
python scripts/pipeline.py --category weather --test

# Check output files
ls -la /opt/auto-youtube-pipeline/output/
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Service won't start | `journalctl -u auto-youtube -n 50` |
| ffmpeg not found | `apt install ffmpeg` or set FFMPEG_PATH |
| No TTS audio | Check edge-tts network access; proxy needed if restricted |
| Upload fails | Verify YOUTUBE_REFRESH_TOKEN has valid scope |
| Videos not showing | Check `output/` dir and ledger |

---

## Next Action for User

Please provide:
1. **Which cloud provider** you prefer (AWS/GCP/Azure/Oracle/Linode/Vultr)
2. **Your YouTube account email** (the Gmail used to run the channel)
3. **Any OAuth client ID/secret** you have for the YouTube channel

Once you provide those, I will:
- Generate the OAuth credentials file
- Set up the headless token refresh flow
- Prepare the server deployment checklist
- Generate the final systemd unit and docker-compose config
- Verify the pipeline can run headless (no X display needed)