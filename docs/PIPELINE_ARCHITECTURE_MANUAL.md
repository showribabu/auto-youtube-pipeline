# OmniPulse Daily — Autonomous YouTube Pipeline Architecture & Operations Manual

This document serves as the permanent architectural reference, operational manual, and knowledge base for the **OmniPulse Daily** (`@OmniPulseDaily`) 100% autonomous cloud media production pipeline.

---

## 1. System Overview & Core Philosophy

OmniPulse Daily produces, validates, formats, and publishes vertical 9:16 YouTube Shorts (`1080x1920`) across **14 diverse niche categories** and **3 languages** (Telugu, Hindi, and English) on a 100% automated schedule with **zero manual intervention**.

### Key System Principles:
1. **100% Autonomous Cloud Execution:** The pipeline runs purely inside GitHub Actions on scheduled cron jobs. The user's personal machine does **not** need to be on, awake, or connected.
2. **Pre-Publish Self-Healing QA Loop:** Videos never publish blind. Every video must pass a 5-gate automated validation suite. If a gate fails, the pipeline automatically heals the asset (rescaling audio rate, sanitizing metadata, regenerating contrast) before retrying.
3. **High-Retention Visual Design:** Standards modeled after top-performing creators (Alex Hormozi, Psych2Go, MinutePhysics, Casually Explained) featuring:
   - **Frame 0 Intro Hook Card** (channel crest, category pill, golden headline question, swipe prompt).
   - **Kinetic Gold Highlighting** (first 1–2 words of every caption pop in `#FFDD00` gold, remainder in `#FFFFFF` with 4px black outline).
   - **Character & Thematic Storytelling Art** (doodle avatars with story props, sacred celestial deities, weather graphics).
   - **Split-Hero Thumbnails** (70% focal character + punchy 3-word yellow headline).
4. **Strict Compliance & Human Tone:** All AI/bot keywords (`"AI"`, `"automated"`, `"bot"`, `"GPT"`, `"pipeline"`) are strictly forbidden in user-facing metadata, slides, and titles (`CHANNEL_RULES.md`).

---

## 2. Category Distribution & Daily Broadcast Slots

### Why Videos Are Distributed Across 4 Daily Slots (Not Dumped All at Once):
YouTube enforces a strict **rolling 24-hour daily upload quota** on new and unverified channels (~8 to 10 videos per day). Attempting to publish all 14 categories in a single burst triggers YouTube API error `uploadLimitExceeded`.

To maximize channel reach and maintain healthy algorithmic velocity without ever hitting upload limits, the 14 categories rotate across **4 Daily Broadcast Slots** (2 to 3 videos per broadcast, ~10 videos per day):

| Broadcast Slot | UTC Cron | IST Time | Scheduled Categories & Languages |
| :--- | :--- | :--- | :--- |
| **Morning Broadcast** | `15 2 * * *` | **07:45 AM IST** | **Devotional** (Telugu), **Weather** (Telugu), **Motivational** (Hindi) |
| **Midday Broadcast** | `20 7 * * *` | **12:50 PM IST** | **Facts** (Telugu), **Cooking** (Hindi), **Health** (Telugu) |
| **Afternoon Broadcast** | `15 12 * * *` | **05:45 PM IST** | **Tech** (English), **News** (Telugu), **Crypto** (English) |
| **Evening Broadcast** | `20 15 * * *` | **08:50 PM IST** | **History** (Telugu), **Kids Stories** (English), **Book Summaries** (Hindi) |

*Additional rotating categories: `gaming` (English), `language` (English/Hindi).*

---

## 3. The Font & Missing Glyph Box (`□□□□`) Permanent Resolution

### Root Cause Analysis:
During early runs, titles and headers rendered square boxes (`#□□□□□□` and `□ OMNIPULSE DAILY □`). Deep investigation revealed two distinct causes:
1. **Regional Font Subsets Missing Latin Letters:** `NotoSansTelugu.ttf` and `NotoSansDevanagari.ttf` in `assets/fonts/` only contained Indic glyphs; their character maps contained **zero Latin letters** (`S`, `h`, `o`, `r`, `t`, `s` returned `False`). When `#Shorts` was drawn using this font, `#` succeeded, but the 6 English letters became 6 missing glyph boxes: `#□□□□□□`.
2. **Unsupported Unicode Emojis/Symbols:** Symbols like `✦` (`\u2726`) and `⚡` (`\u26A1`) placed inside string literals (`"✦ OMNIPULSE DAILY ✦"`) were missing from basic Linux fonts, causing them to render as `□ OMNIPULSE DAILY □`.

### Permanent Fix Applied:
1. **Universal Font Bundling:** Bundled `assets/fonts/Nirmala.ttc` directly into the repository. It contains 100% of Telugu, 100% of Hindi/Devanagari, and 100% of Latin English alphanumeric characters.
2. **Hashtag Stripping from Visual Canvas:** Automated regex sanitization (`clean_title = re.sub(r'#\w+', '', title).strip()`) strips `#Shorts` and all hashtags from the visual frames and thumbnail, while keeping them intact in YouTube's backend metadata and title.
3. **Pure Vector Geometry for Icons:** Replaced unicode symbols with Pillow geometric shapes (e.g. golden polygon diamonds and notification bells). Pure vector shapes never depend on font glyphs and render consistently across Windows and Linux.

---

## 4. The 5-Gate Active Self-Healing Feedback Loop

The pipeline operates an active self-healing feedback loop before any video is published:

```
[Content Generated]
       │
       ▼
[Gate 1: Metadata QA] ── Fails ──> [Auto-Heal: Strip forbidden words, fix tags, adjust length]
       │ (Pass)
       ▼
[Render Frames]
       │
       ▼
[Gate 2: Visual Frame QA] ── Fails ──> [Auto-Heal: Regenerate with high-contrast photographic bg]
       │ (Pass)
       ▼
[Synthesize TTS Audio]
       │
       ▼
[Gate 3: Audio Duration QA] ── Fails (<10s or >58s) ──> [Auto-Heal: Recalculate speech rate (+20% / -10%)]
       │ (Pass)
       ▼
[Assemble 1080x1920 Short via FFmpeg]
       │
       ▼
[Gate 4: Video Stream QA] ── Fails ──> [Auto-Heal: Re-encode with verified container parameters]
       │ (Pass)
       ▼
[Generate Split-Hero Thumbnail]
       │
       ▼
[Gate 5: Thumbnail QA] ── Fails ──> [Auto-Heal: Re-compose with high-density focal subject]
       │ (Pass)
       ▼
[Publish Live to YouTube & Dispatch Notification Email]
```

---

## 5. Visual Storytelling & B-Roll Engines

### Character Illustration Engine (`scripts/illustrations.py`)
Provides category-matched visual focal points in the center of the frame:
*   **Facts, Psychology, Motivation, Tech:** High-retention doodle avatars (Psych2Go / MinutePhysics style) with expressive faces (curious, happy, thinking) and floating thematic story props (lightbulbs, code screens, rockets, trophies).
*   **Devotional:** Multi-layered celestial sunbursts, glowing lotus blossoms in full bloom, meditative silhouettes in Padmasana, and sacred diya oil lamps.
*   **Weather:** Radiant golden sun, dramatic puffy 3D cloud, glowing neon lightning bolt, and raindrops.

### Real Video B-Roll Engine (`scripts/broll.py`)
Inspired by MoneyPrinterTurbo (`material.py`), this module queries Pexels / Pixabay for real 1080×1920 vertical MP4 video loops (moving water, clouds, incense smoke, cities) and stitches them with crossfades.

---

## 6. Email Notifications & Cloud Delivery

*   **Target Recipient:** `rajubai6419@gmail.com`
*   **Delivery Mechanism:** Every successful upload creates an issue on GitHub tagged `upload-confirmation`, assigning `@showribabu` and mentioning `cc: @showribabu`.
*   **Enabling Direct Email Delivery in GitHub:**
    1. Visit `https://github.com/settings/notifications`.
    2. Ensure "Default notification email" is set to `rajubai6419@gmail.com`.
    3. Under "Notify me", check the box for **"Email"** for Issues and @mentions.
    4. On `https://github.com/showribabu/auto-youtube-pipeline`, set the **Watch** button to **"All Activity"**.
    5. In Gmail, ensure emails from `notifications@github.com` are marked as "Not Spam" or added to Primary Inbox.

---

## 7. Directory & Module Reference

```text
auto-youtube-pipeline/
├── .github/
│   └── workflows/
│       └── daily.yml             # Cloud workflow (4 staggered broadcast crons + workflow_dispatch)
├── assets/
│   ├── fonts/
│   │   ├── Nirmala.ttc           # Universal multi-script font (Telugu + Devanagari + Latin)
│   │   ├── NotoSansTelugu.ttf    # Telugu Indic font
│   │   └── NotoSansDevanagari.ttf# Devanagari Indic font
│   ├── channel_avatar_official.png
│   └── channel_banner_omnipulse.png
├── docs/
│   └── PIPELINE_ARCHITECTURE_MANUAL.md # Permanent system architecture reference
├── output/
│   └── upload_ledger.json        # Permanent upload tracking ledger to prevent duplicates
└── scripts/
    ├── broll.py                  # Real 1080x1920 MP4 video B-roll sourcing (MoneyPrinterTurbo inspired)
    ├── illustrations.py          # Character avatars, celestial sacred art, and story props
    ├── engine.py                 # Core rendering engine (kinetic captions, intro hook card, thumbnails)
    ├── validator.py              # 5-stage automated QA validation gates & self-healing functions
    ├── pipeline.py               # Main autonomous pipeline runner & slot scheduler
    ├── notify.py                 # Automated email and GitHub notification dispatcher
    ├── audio.py                  # Edge-TTS voiceover synthesis with 1.6x dynamic volume boost
    └── categories/               # 14 distinct category script & content generators
```
