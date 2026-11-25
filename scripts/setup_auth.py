"""
YouTube OAuth Setup — One-time flow to get refresh token.
Run this once to authorize your YouTube channel for auto-uploads.
"""
import os
import sys
import json
import re
from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CONFIG_DIR, BASE_DIR
from logger import get_logger

logger = get_logger("auth")
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def update_env_file(refresh_token: str):
    """Automatically write the refresh token to config/.env"""
    env_path = os.path.join(CONFIG_DIR, ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(BASE_DIR, "config", ".env")

    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "YOUTUBE_REFRESH_TOKEN=" in content:
            new_content = re.sub(
                r"YOUTUBE_REFRESH_TOKEN=.*",
                f"YOUTUBE_REFRESH_TOKEN={refresh_token}",
                content
            )
        else:
            new_content = content + f"\nYOUTUBE_REFRESH_TOKEN={refresh_token}\n"
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✓ Updated {env_path} with new YOUTUBE_REFRESH_TOKEN", flush=True)


def setup_credentials():
    print("=" * 60, flush=True)
    print("YouTube API Authentication Setup", flush=True)
    print("=" * 60, flush=True)

    credentials_file = os.path.join(CONFIG_DIR, "client_secret.json")
    if not os.path.exists(credentials_file):
        print(f"ERROR: Client secret file not found: {credentials_file}", flush=True)
        return False

    print(f"Found client secrets: {credentials_file}", flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        scopes=SCOPES,
        redirect_uri="http://localhost:8080/"
    )

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    print("\n" + "=" * 60, flush=True)
    print("AUTH_URL_START", flush=True)
    print(auth_url, flush=True)
    print("AUTH_URL_END", flush=True)
    print("=" * 60, flush=True)
    print("Waiting for authentication in browser on port 8080...", flush=True)

    try:
        creds = flow.run_local_server(
            port=8080,
            authorization_prompt_message="Open this URL in browser: {url}\n",
            success_message="Authentication successful! You can close this browser window.",
            open_browser=True
        )

        token_path = os.path.join(CONFIG_DIR, "yt_token.json")
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"\n✓ Credentials token saved to: {token_path}", flush=True)

        if creds.refresh_token:
            print(f"✓ Refresh token: {creds.refresh_token}", flush=True)
            update_env_file(creds.refresh_token)

        print("\nSUCCESS: YouTube channel authorized for automated uploads!", flush=True)
        return True

    except Exception as e:
        print(f"\nAuthentication failed: {e}", flush=True)
        return False


if __name__ == "__main__":
    success = setup_credentials()
    sys.exit(0 if success else 1)
