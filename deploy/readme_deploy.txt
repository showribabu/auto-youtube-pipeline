# Cloud Deployment Guide for Auto YouTube AI Video Pipeline

## Overview
This is a fully autonomous AI video generation system that creates and uploads videos across 5 categories (weather, news, kids, facts, motivational) on a daily schedule.

## Prerequisites for Deployment

### 1. Cloud Server Requirements
- Linux VM (Ubuntu 22.04 LTS recommended)
- 1GB RAM (minimum), 2CPU, 25GB storage
- Public IP or domain name
- Public SSH access (port 22)
- FFmpeg installed

### 2. Cloud Server Setup
```bash
# 1. Create VM (AWS EC2, GCP Compute Engine, or Azure VM)
# 2. Connect via SSH
ssh root@your-server-ip

# 3. Install dependencies
sudo apt update && sudo apt install -y python3 python3-venv python3-pip ffmpeg git

# 4. Clone this repository
git clone https://github.com/your-repo/auto-youtube-pipeline.git
cd auto-youtube-pipeline

# 5. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment
cp config/.env.example config/.env
# Edit config/.env to add:
# - YOUTUBE_REFRESH_TOKEN=your_refresh_token_here
# - GOOGLE_CLIENT_ID=your_google_client_id
# - GOOGLE_CLIENT_SECRET=your_google_client_secret
# - FFMPEG_PATH=/usr/bin/ffmpeg (or leave empty if in PATH)

# 7. Set up YouTube credentials
python scripts/setup_auth.py
# This will open a browser window - sign in with your YouTube account
# The refresh token will be saved automatically

# 8. Test the pipeline
python scripts/pipeline.py --run-all --test
# Should generate 5 videos in output/ directory

# 9. Install as systemd service (runs 24/7)
sudo bash scripts/install_service.sh
# Then enable auto-start:
sudo systemctl enable auto-youtube.service
sudo systemctl start auto-youtube.service
sudo systemctl status auto-youtube.service
```

## Deployment Options

### Option A: Self-Hosted Cloud VM (Recommended)
1. Use AWS Lightsail, GCP Compute Engine, or Azure VM
2. Follow the setup steps above
3. Your server will run the pipeline 24/7 with no laptop required

### Option B: GitHub Actions (Free Tier)
Use this if you want to run the pipeline daily on GitHub's servers:
1. Create a GitHub repo
2. Add the code and your secrets (YOUTUBE_REFRESH_TOKEN, etc.)
3. Create .github/workflows/daily.yml:
```yaml
name: Daily YouTube Pipeline
on:
  schedule:
    - cron: '0 6 * * *'  # 6:00 UTC daily
  jobs:
    daily-run:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - name: Install dependencies
          run: |
            python -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        - name: Run pipeline
          env:
            YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
            GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
            GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
          run: |
            source venv/bin/activate
            python scripts/pipeline.py --run-all
```

## Maintenance

### Logs
- View logs: `journalctl -u auto-youtube -f`
- Pipeline logs: `tail -f /opt/auto-youtube-pipeline/logs/pipeline.log`

### Updates
1. Pull latest changes: `git pull`
2. Reinstall dependencies: `source .venv/bin/activate && pip install -r requirements.txt`
3. Restart service: `sudo systemctl restart auto-youtube.service`

## Monitoring

### Check if service is running:
```bash
systemctl is-active auto-youtube.service
```

### View recent logs:
```bash
journalctl -u auto-youtube.service -n 50 --no-pager
```

### Manual test run:
```bash
source .venv/bin/activate
python scripts/pipeline.py --run-all --test
```

## Troubleshooting

- "No video files generated": Check ffmpeg is installed and in PATH
- "Upload failed": Verify YOUTUBE_REFRESH_TOKEN is valid and has permission
- "No audio generated": Check voice parameters in config/.env

## Notes
- All videos are 60 seconds long by default
- Videos are generated in HD (1280x720) with 30fps
- The pipeline automatically handles daily upload limits (3 videos/day)
- All videos are uploaded as "public" - adjust in upload.py if needed
- The systemd service will auto-restart on failure

```

## Next Steps for You
1. Choose a cloud provider (AWS, GCP, Azure, Oracle Cloud - all have free tiers)
2. Create a Linux VM with the specs above
3. Follow the deployment guide
4. Let the system run autonomously forever