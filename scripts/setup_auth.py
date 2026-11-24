"""
YouTube OAuth Setup — One-time flow to get refresh token.
Run this once to authorize your YouTube channel for auto-uploads.
"""
import os
import sys
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, CONFIG_DIR
from logger import get_logger

logger = get_logger("auth")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def setup_credentials():
    print("=" * 50)
    print("YouTube API Authentication Setup")
    print("=" * 50)

    # Check if client secrets file exists (Google Cloud Console download)
    credentials_file = os.path.join(CONFIG_DIR, "client_secret.json")

    creds = None

    # Option 1: Use client_secrets.json from Google Cloud Console
    if os.path.exists(credentials_file):
        print(f"Found: {credentials_file}")
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, SCOPES
        )
    elif GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        print("Using credentials from .env file...")
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            SCOPES
        )
    else:
        print("""
ERROR: No credentials found!

You have two options:

OPTION 1 — Using client_secret.json (Recommended):
  1. Go to https://console.cloud.google.com/apis/credentials
  2. Create OAuth 2.0 Client ID (Desktop app type)
  3. Download the JSON file
  4. Save it as: config/client_secret.json

OPTION 2 — Using .env variables:
  Set these in config/.env:
    GOOGLE_CLIENT_ID=your_id_here.apps.googleusercontent.com
    GOOGLE_CLIENT_SECRET=your_secret_here
""")
        return False

    try:
        print("\nOpening browser for Google sign-in...")
        print("Please sign in with your YouTube channel account.\n")
        creds, _ = flow.run_local_server(
            port=8080,
            authorization_prompt_message="",
            success_message="You can close this window!",
            open_browser=True
        )

        # Save credentials
        token_path = os.path.join(CONFIG_DIR, "yt_token.json")
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print(f"\nCredentials saved to: {token_path}")

        # Also extract refresh token for .env backup
        if creds.refresh_token:
            print(f"\nRefresh token: {creds.refresh_token}")
            print("\nAdd this to your config/.env:")
            print(f'YOUTUBE_REFRESH_TOKEN={creds.refresh_token}')
            print("\nDone!")
            return True

    except Exception as e:
        print(f"\nAuthentication failed: {e}")
        return False


if __name__ == "__main__":
    success = setup_credentials()
    sys.exit(0 if success else 1)
