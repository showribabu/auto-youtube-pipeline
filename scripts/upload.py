import os
import json
import time
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError, ResumableUploadError
from config import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN,
    OUTPUT_DIR, BASE_DIR, MAX_RETRIES, RETRY_DELAY
)
from logger import get_logger
logger = get_logger("upload")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def _load_creds() -> Credentials:
    token_path = os.path.join(BASE_DIR, "config", "yt_token.json")
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "r", encoding="utf-8") as f:
            creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif YOUTUBE_REFRESH_TOKEN:
            from google.auth.transport.requests import Request as Req
            token_data = {
                "refresh_token": YOUTUBE_REFRESH_TOKEN,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "scopes": SCOPES,
            }
            creds = Credentials(token=None, **token_data)
            creds.refresh(Req())
        if not creds or not creds.valid:
            raise RuntimeError(
                "No valid YouTube credentials found. Run python scripts/setup_auth.py once to authenticate."
            )
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds


def verify_youtube_channel() -> dict | None:
    """Verify credentials and get authenticated YouTube channel information."""
    try:
        creds = _load_creds()
        service = build("youtube", "v3", credentials=creds)
        res = service.channels().list(part="snippet,statistics", mine=True).execute()
        items = res.get("items", [])
        if not items:
            logger.warning("No channel found for current credentials.")
            return None
        ch = items[0]
        snippet = ch.get("snippet", {})
        stats = ch.get("statistics", {})
        info = {
            "channel_id": ch.get("id"),
            "channel_title": snippet.get("title"),
            "channel_url": f"https://www.youtube.com/channel/{ch.get('id')}",
            "video_count": stats.get("videoCount"),
            "subscriber_count": stats.get("subscriberCount"),
            "view_count": stats.get("viewCount"),
        }
        logger.info(f"Verified Channel: {info['channel_title']} ({info['channel_url']})")
        return info
    except Exception as e:
        logger.error(f"Failed to verify channel: {e}")
        return None


def verify_uploaded_videos(max_results: int = 15) -> list[dict]:
    """Fetch recent videos published on the authenticated YouTube channel to verify end-to-end."""
    try:
        creds = _load_creds()
        service = build("youtube", "v3", credentials=creds)
        res = service.channels().list(part="contentDetails", mine=True).execute()
        items = res.get("items", [])
        if not items:
            return []
        uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        playlist_res = service.playlistItems().list(
            part="snippet,status",
            playlistId=uploads_playlist_id,
            maxResults=max_results,
        ).execute()
        
        videos = []
        for item in playlist_res.get("items", []):
            vid = item["snippet"]["resourceId"]["videoId"]
            videos.append({
                "video_id": vid,
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={vid}",
            })
        return videos
    except Exception as e:
        logger.error(f"Failed to verify uploaded videos: {e}")
        return []


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "28",
    privacy_status: str = "public",
    thumbnail_path: str | None = None,
) -> str | None:
    """Uploads a video to YouTube with automatic retry, exponential backoff, and quota awareness."""
    max_attempts = max(1, MAX_RETRIES)
    
    for attempt in range(1, max_attempts + 1):
        try:
            creds = _load_creds()
            service = build("youtube", "v3", credentials=creds)
            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description[:5000],
                    "tags": tags[:30],
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
                media_body=MediaFileUpload(video_path, mimetype="video/mp4", resumable=True),
            )
            logger.info(f"Uploading to YouTube (Attempt {attempt}/{max_attempts}): {title}")
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response.get("id")
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info(f"✓ Video successfully published! URL: {watch_url}")
            
            if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
                set_thumbnail(video_id, thumbnail_path)
                
            return video_id

        except Exception as e:
            err_str = str(e)
            # 1. YouTube Daily Quota Exceeded (not a bug — 24-hr safety limit on new channels)
            if "uploadLimitExceeded" in err_str:
                logger.warning(
                    f"⚠️ YouTube 24-Hour Daily Upload Limit Reached (uploadLimitExceeded). "
                    f"Video '{title}' is rendered & saved locally. Will resume on next scheduled run."
                )
                return "QUOTA_EXCEEDED"

            # 2. Transient network or 5xx server errors -> Retry with backoff
            is_transient = any(code in err_str for code in ["500", "502", "503", "504", "timed out", "ConnectionResetError"])
            if attempt < max_attempts and is_transient:
                backoff = RETRY_DELAY * attempt
                logger.warning(f"Upload attempt {attempt} failed ({e}). Retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                logger.error(f"Upload permanently failed for '{title}': {e}")
                return None


def set_thumbnail(video_id: str, thumbnail_path: str) -> bool:
    try:
        creds = _load_creds()
        service = build("youtube", "v3", credentials=creds)
        service.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
        ).execute()
        logger.info(f"Custom thumbnail set for video {video_id}")
        return True
    except Exception as e:
        logger.info(f"Custom thumbnail skipped (channel uses auto-generated thumbnail): {e}")
        return False
