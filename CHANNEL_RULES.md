# OmniPulse Daily — Channel & Production Standards

This document records the permanent design, editorial, and engineering rules for **OmniPulse Daily** (`@OmniPulseDaily`). All updates to scripts, templates, or assets must strictly follow these rules.

---

## 1. Editorial & Authenticity Rules
- **Zero Automation Footprints:** Never use words like `"automated"`, `"auto-generated"`, `"bot"`, `"AI pipeline"`, or `"daily automated upload"` in any video title, description, slide text, banner, or channel bio.
- **Human-Curated Brand Voice:** Present all content naturally as **OmniPulse Daily** (`OMNIPULSE DAILY`).
- **Content Priority:** **Devotional** (Bhagavad Gita wisdom & spiritual reflections) runs first in daily schedules, followed by Weather, News, Facts, Motivation, Health, Language, Books, Cooking, Kids, Tech, Crypto, History, and Gaming.

## 2. Visual & Typography Rules
- **Strict Script-to-Font Mapping:**
  - **Telugu** (`0x0C00–0x0C7F`): Must render with `assets/fonts/NotoSansTelugu.ttf`.
  - **Hindi / Devanagari** (`0x0900–0x097F`): Must render with `assets/fonts/NotoSansDevanagari.ttf`.
  - **English / Latin**: Must render with bold Latin fonts (`DejaVuSans-Bold.ttf` / `segoeuib.ttf`).
  - Never allow missing glyph boxes (`□□□□`). Always visually inspect generated frames/banners when modifying typography.
- **No Watermarks:** Crop bottom 6% (`int(oh * 0.94)`) of fetched background images before resizing to eliminate any third-party corner watermarks.
- **Rich, Vivid Backgrounds:** Avoid plain flat solid-color slides. Use topic-matched photography/artwork enhanced for clarity (`Brightness 0.86`, `Contrast 1.12`, `Color 1.15`) behind a bottom-weighted gradient and glassmorphic caption card.
- **YouTube CTA & Clean Frame:**
  - Include the YouTube-red **SUBSCRIBE** pill + Golden **Bell** notification icon at the bottom of video frames.
  - **Do NOT** draw a duplicate progress bar inside the video (YouTube's player already provides its native scrubber bar).

## 3. Video & Audio Engineering Rules
- **Audio-Synced Slide Timing:** Always probe exact speech duration via `ffprobe` and pace slides across `audio_dur / len(frames)` with `0.5s` `xfade` crossfade transitions.
- **Loud, Clear Voiceover:** When mixing speech with ambient background audio in FFmpeg `amix`, always pass `normalize=0` and boost speech (`volume=1.6`) so the narration is loud and crisp on mobile speakers.
- **Format:** `1080×1920` (9:16 vertical `#Shorts`) for short-form categories; `1280×720` for long-form stories/roundups.

## 4. Cloud Automation & Reliability Rules
- **100% Cloud Execution:** Runs on GitHub Actions (`.github/workflows/daily.yml`) across 4 daily schedules (`02:00`, `07:00`, `12:00`, `15:00 UTC`).
- **Honest Exit Codes & Quota Handling:** If YouTube returns `uploadLimitExceeded`, stop early for that run, mark `QUOTA_EXCEEDED` in `output/upload_ledger.json`, and exit non-zero when `0` videos were published so GitHub Actions never reports a false success.
