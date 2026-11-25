import os
import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN,
    OUTPUT_DIR, BASE_DIR
)
from logger import get_logger
logger = get_logger("upload")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _load_creds() -> Credentials:
    token_path = os.path.join(BASE_DIR, "config", "yt_token.json")
    creds = None
    if os.path.exists(token_path):
        with open(token_path) as f:
            creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif YOUTUBE_REFRESH_TOKEN:
            from google.auth.transport.requests import Request as Req
            import requests as req_lib
            # Construct minimal token data and use standard constructor
            token_data = {
                "refresh_token": YOUTUBE_REFRESH_TOKEN,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "scopes": SCOPES,
            }
            creds = Credentials(token=None, **token_data)
            creds.refresh(Req())
        if not creds:
            raise RuntimeError(
                "No valid YouTube credentials. Set YOUTUBE_REFRESH_TOKEN in .env "
                "or run the auth flow."
            )
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "28",
    privacy_status: str = "public",
    thumbnail_path: str | None = None,
) -> str | None:
    try:
        creds = _load_creds()
        service = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(video_path, mimetype="video/mp4",
                                        resumable=True),
        )
        logger.info(f"Uploading: {title}")
        response = request.resumable_upload()
        video_id = response.get("id", "unknown")
        logger.info(f"Uploaded successfully. Video ID: {video_id}")
        return video_id
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return None


def set_thumbnail(video_id: str, thumbnail_path: str) -> bool:
    try:
        creds = _load_creds()
        service = build("youtube", "v3", credentials=creds)
        service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
        ).execute()
        logger.info(f"Thumbnail set for video {video_id}")
        return True
    except Exception as e:
        logger.error(f"Thumbnail upload failed: {e}", exc_info=True)
        return False
