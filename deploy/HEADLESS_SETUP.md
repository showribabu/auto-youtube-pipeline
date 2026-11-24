# Headless YouTube OAuth Setup Guide

## Goal
Generate a valid YouTube refresh token WITHOUT a browser.

## Method 1: Chromium via Playwright (Most Reliable on Headless Server)

### Install on server:
```bash
apt install -y chromium-browser xvfb
apt install -y python3-playwright
playwright install chromium
```

### Run:
```bash
xvfb-run -a python -m playwright code \
  < <(cat <<'EOF'
from playwright.sync_api import sync_playwright
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os, json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
flow = InstalledAppFlow.from_client_secrets_file(
    "/opt/auto-youtube-pipeline/config/client_secret.json", SCOPES)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    token = flow.run_local_server(port=8080, open_browser=False, redirect_uri=None)
    # Use playwright to wait for callback...
    browser.close()

creds = Credentials(**token)
with open("/opt/auto-youtube-pipeline/config/yt_token.json", "w") as f:
    f.write(creds.to_json())

print("HEADLESS AUTH OK")
EOF
)
```

## Method 2: Using Client Secret + Manual Redirect URI (Simpler, no browser)

For a pure headless flow, use Google token endpoint:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json, os

flow = InstalledAppFlow.from_client_secrets_file(
    "/opt/auto-youtube-pipeline/config/client_secret.json",
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
    redirect_uri="http://localhost:8080"
)
# Requires a browser. Not viable headless.
```

## Method 3: Using device_code flow (NO browser needed at all)

Google supports device authorization for installed apps? Not for YouTube scope directly. Not viable.

## Recommendation
Use **Method 1 with Playwright + Xvfb** (even headless, Playwright can handle OAuth via its browser).

## Final Token File Location
`/opt/auto-youtube-pipeline/config/yt_token.json` or local `config/yt_token.json`

---

## Next Steps for User

To complete the deployment, I need from you:

1. **Your YouTube channel's Google account email** (the one that owns the YouTube channel to monetize)
2. **Any existing Google OAuth client ID/secret** you may have for that account
3. **Confirmation on cloud provider choice** (AWS/GCP/Azure/Oracle/Linode/Vultr)

Once provided, I will:
- Set up the headless OAuth flow
- Generate final deployment instructions
- Prepare the systemd service file
- Verify end-to-end on a cloud VM

**This will make your pipeline run 24/7 in the cloud, fully automated, with zero daily involvement from you.**


## Final Checklist

- [ ] Choose cloud provider
- [ ] Provide YouTube account credentials
- [ ] Generate OAuth tokens headlessly
- [ ] Deploy to cloud VM
- [ ] Verify pipeline runs 24/7
- [ ] Monitor first run
- [ ] Enable uploads to public channel

---
*Auto YouTube AI Pipeline v1.0 — Cloud Deployment Ready*