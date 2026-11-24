# Auto YouTube Pipeline — DEPLOY NOW (One Command)

## What You Need to Do (5 Minutes Total)

### Step 1: Get GitHub Token (1 min)
1. Go to: https://github.com/settings/tokens/new
2. **Token name**: `auto-youtube-pipeline`
3. **Expiration**: `90 days`
4. **Scopes**: Check ✅ `repo` and ✅ `workflow`
5. Click **"Generate token"** at bottom
6. **Copy the token** (starts with `ghp_xxxxx`)

---

### Step 2: Run One Command (30 seconds)
Open PowerShell as Administrator and run:

```powershell
cd D:\PROJECT\Coding\auto-youtube-pipeline
python deploy/setup.py YOUR_GITHUB_TOKEN_HERE
```

Replace `YOUR_GITHUB_TOKEN_HERE` with your actual token.

**OR** set it as environment variable first:
```powershell
$env:GH_TOKEN = "your_token_here"
python deploy/setup.py
```

---

### Step 3: Set Up YouTube Uploads (Optional but Recommended)

To make videos actually upload to your YouTube channel:

#### A. Create Google Cloud Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. New Project → Name: `auto-youtube-pipeline`
3. Enable API: Search **"YouTube Data API v3"** → Enable
4. **Create OAuth Client ID** → Application type: **Desktop app**
   - Name: `auto-youtube-uploader`
   - Download the JSON file

#### B. Generate Refresh Token (for auto-upload)
Run on your computer:
```powershell
cd D:\PROJECT\Coding\auto-youtube-pipeline
.\.venv\Scripts\activate
python scripts/setup_auth.py
```
This opens a browser → sign in with rajubai6419@gmail.com → save refresh token

#### C. Add Secrets to GitHub
1. Go to: https://github.com/rajubai6419/auto-youtube-pipeline/settings/secrets/actions
2. Add these 3 secrets:
   - `YOUTUBE_REFRESH_TOKEN` → paste the refresh token from above
   - `GOOGLE_CLIENT_ID` → from downloaded JSON
   - `GOOGLE_CLIENT_SECRET` → from downloaded JSON

---

## What Happens After Deployment

✅ **Without YouTube credentials:**
- Videos generate daily at 6 AM UTC automatically
- Saved locally in `output/` folder on GitHub Actions runner
- You download them manually if needed

✅ **With YouTube credentials:**
- Videos generate AND upload automatically to your YouTube channel
- Daily uploads start immediately after setup
- Thumbnails auto-generated
- Tags optimized for each category

---

## 5 Video Categories Generated Daily

| Time (UTC) | Category | Content Source |
|------------|----------|----------------|
| 6:00 AM | Weather | Live wttr.in API |
| 7:00 AM | News | BBC/NYT RSS feeds |
| 8:00 AM | Kids | Story library (rotating) |
| 12:00 PM | Facts | Science/nature facts |
| 6:00 PM | Motivational | Quotes & inspiration |

---

## Monitor Your Pipeline

After deploying, watch progress here:
👉 https://github.com/rajubai6419/auto-youtube-pipeline/actions

When a workflow runs, you'll see:
- Green checkmark = success
- Red X = error (click to view logs)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Push fails | Check token permissions (needs `repo` + `workflow`) |
| Tests fail | Ensure ffmpeg installed: `apt-get install ffmpeg` |
| Upload fails | Verify all 3 GitHub secrets are set correctly |
| No video generated | Check Actions logs for errors |

---

## Summary

1. ✅ Pipeline built and tested (all 5 categories pass)
2. ✅ One command to deploy to GitHub
3. ✅ Automated daily generation at fixed times
4. ✅ Optional auto-upload to YouTube
5. ✅ Zero maintenance required after setup

**Your autonomous AI video pipeline is ready.** Just run the one command above!
