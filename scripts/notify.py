"""
OmniPulse Daily — Notification System
Sends automated email confirmations to the channel owner whenever a video is uploaded.
"""
import os
import sys
import json
import smtplib
import urllib.request
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ensure logger is available
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logger import get_logger

logger = get_logger("notify")

DEFAULT_NOTIFY_EMAIL = "rajubai6419@gmail.com"
REPO_OWNER = "showribabu"
REPO_NAME = "auto-youtube-pipeline"


def send_email_smtp(subject: str, html_body: str, recipient: str = DEFAULT_NOTIFY_EMAIL) -> bool:
    """Send direct email via SMTP if SMTP credentials are provided in environment."""
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS") or os.environ.get("SMTP_PASSWORD")

    if not smtp_user or not smtp_pass:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"OmniPulse Daily <{smtp_user}>"
        msg["To"] = recipient

        part = MIMEText(html_body, "html")
        msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())

        logger.info(f"✓ SMTP email confirmation sent to {recipient}")
        return True
    except Exception as e:
        logger.warning(f"SMTP notification failed: {e}")
        return False


def send_github_email_notification(title: str, body_markdown: str) -> bool:
    """
    Creates a dedicated notification issue on GitHub which triggers GitHub's
    built-in email delivery directly to the repo owner (rajubai6419@gmail.com).
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT")
    if not token:
        logger.warning("No GITHUB_TOKEN or GH_PAT available for GitHub notification.")
        return False

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OmniPulse-Daily-Notifier"
    }

    payload = {
        "title": title,
        "body": f"cc: @{REPO_OWNER}\n\n{body_markdown}",
        "assignees": [REPO_OWNER],
        "labels": ["upload-confirmation", "automated-notification"]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            issue_number = data.get("number")
            issue_url = data.get("html_url")
            logger.info(f"✓ GitHub email notification dispatched! Issue #{issue_number}: {issue_url}")
            return True
    except Exception as e:
        logger.warning(f"GitHub notification trigger failed: {e}")
        return False


def notify_upload_success(
    video_title: str,
    video_id: str,
    category: str,
    lang: str,
    is_shorts: bool = True
) -> bool:
    """Send an immediate notification across all available channels upon successful upload."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    shorts_url = f"https://youtube.com/shorts/{video_id}" if is_shorts else video_url
    channel_url = "https://www.youtube.com/@omnipulsedaily"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subject = f"🎬 OmniPulse Daily: New Video Published — {video_title[:60]}"

    markdown_body = f"""## 🎬 OmniPulse Daily — Upload Confirmation

A new video has been successfully generated and published to **OmniPulse Daily** (@OmniPulseDaily).

---

### 📌 Video Information:
- **Title:** {video_title}
- **Category:** `{category}`
- **Language:** `{lang}`
- **Format:** {"9:16 Vertical Short" if is_shorts else "16:9 Standard"}
- **Video ID:** `{video_id}`
- **Published Timestamp:** `{now_str}`

### 🔗 Direct Watch Links:
- 📱 **Watch Short:** [{shorts_url}]({shorts_url})
- 🖥️ **YouTube Standard Link:** [{video_url}]({video_url})
- 📺 **Channel Home:** [{channel_url}]({channel_url})

---
*OmniPulse Daily Autonomous Channel Pipeline — Zero Manual Intervention*
"""

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
          <h2 style="color: #ff0000; border-bottom: 2px solid #eee; padding-bottom: 10px;">🎬 OmniPulse Daily — Upload Confirmation</h2>
          <p style="font-size: 15px; color: #333;">A new video has been generated and published to your YouTube channel:</p>
          <div style="background: #fafafa; border-left: 4px solid #ff0000; padding: 15px; margin: 15px 0;">
            <p><strong>Title:</strong> {video_title}</p>
            <p><strong>Category:</strong> {category.capitalize()}</p>
            <p><strong>Language:</strong> {lang.upper()}</p>
            <p><strong>Status:</strong> <span style="color: #00aa00; font-weight: bold;">LIVE & PUBLIC</span></p>
          </div>
          <p style="text-align: center; margin: 25px 0;">
            <a href="{shorts_url}" style="background-color: #ff0000; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Watch on YouTube</a>
          </p>
          <p style="font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px;">
            OmniPulse Daily Autonomous Pipeline &bull; rajubai6419@gmail.com
          </p>
        </div>
      </body>
    </html>
    """

    # 1. Try direct SMTP if configured
    smtp_ok = send_email_smtp(subject, html_body)

    # 2. Trigger GitHub Issue notification (sends email to rajubai6419@gmail.com)
    gh_ok = send_github_email_notification(subject, markdown_body)

    return smtp_ok or gh_ok


if __name__ == "__main__":
    # Test notification
    print("Testing notification...")
    res = notify_upload_success(
        video_title="టెస్ట్ వీడియో — OmniPulse Daily Test Notification",
        video_id="NrTpjouwx_Y",
        category="devotional",
        lang="te",
        is_shorts=True
    )
    print("Notification result:", res)
