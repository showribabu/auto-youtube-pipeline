# OmniPulse Daily — Pro-Grade Video Pipeline Transformation Plan

**Document Version:** 2.0.0  
**Target Channel:** OmniPulse Daily (`@OmniPulseDaily`)  
**Scope:** Complete upgrade from static slide generation to a high-retention, pro-grade automated short-form video studio.

---

## 1. Executive Summary & Root Cause Analysis

Our live audit of YouTube Studio (`studio.youtube.com`) for OmniPulse Daily revealed:
- **Real-Time Performance:** 264 views across 20 uploads; 51.9% traffic coming from the Shorts feed.
- **The Retention Bottleneck:** **33.3% Stayed to watch vs. 66.7% Swiped away.**
- **The Root Cause:** Our legacy pipeline rendered flat static PIL slides with whole paragraphs of text, paired with a synthetic 220Hz sine wave beep, dry textbook trivia, and hardcoded modulo loops that uploaded the exact same Penicillin history topic 3 times.

This document outlines the uncompromising, full-spectrum architectural plan to transform OmniPulse Daily into a world-class, automated short-form video production studio using 100% free, production-tested resources.

---

## 2. The 6-Pillar System Architecture

```
                                  ┌──────────────────────────────────────────────────┐
                                  │           OMNIPULSE PRO ENGINE (v2.0)            │
                                  └────────────────────────┬─────────────────────────┘
                                                           │
              ┌─────────────────────────┬──────────────────┴───────────────┬─────────────────────────┐
              │                         │                                  │                         │
              ▼                         ▼                                  ▼                         ▼
    1. SCRIPT & TRENDS        2. VOICE & WORD TIMINGS            3. VISUAL & MOTION         4. AUDIO DESIGN
    (scripts/content/)        (scripts/voice/)                   (scripts/visual/)          (scripts/audio/)
    ├── 2026 Tech & Science   ├── Edge-TTS Neural Voice          ├── Multi-clip Video B-Roll├── Normalized Voice (-14 LUFS)
    ├── Modern Life Dilemmas  ├── Millisecond Word Boundaries    ├── 60fps Ken Burns Zoom   ├── Royalty-Free Ambient BGM
    ├── 3-Act Viral Formula   ├── Word Cue Alignment             ├── 2.5s Rapid Scene Cuts  ├── Sidechain Auto-Ducking (-24dB)
    └── 60-Day Anti-Duplicate └── Multilingual (TE, HI, EN)      └── Frame 0 Hook Billboard └── Transition Whoosh SFX
              │                         │                                  │                         │
              └─────────────────────────┼──────────────────────────────────┴─────────────────────────┘
                                        │
                                        ▼
                         5. KINETIC SUBTITLE ENGINE (scripts/subtitles/)
                         ├── Advanced SubStation Alpha (.ass) Compiler
                         ├── Centered 1-to-2 Word Dynamic Pop
                         ├── Active Word Highlight: Vibrant Gold (#FFDD00)
                         ├── Inactive Words: Crisp White (#FFFFFF) with 5px Solid Black Outline
                         └── Universal Font: Nirmala.ttc (100% Telugu, Hindi, English Glyphs)
                                        │
                                        ▼
                         6. COMPOSITOR & 6-GATE QA (scripts/qa/)
                         ├── Gate 1: Trend Freshness & 60-Day Ledger Anti-Duplicate
                         ├── Gate 2: Audio Normalization & True BGM Presence Check
                         ├── Gate 3: Continuous Motion & 2.5s Cut Pacing Check
                         ├── Gate 4: Zero Missing Glyph Boxes (□) & Subtitle Alignment Check
                         ├── Gate 5: Strict 22% Bottom Safe-Zone Compliance
                         └── Gate 6: Technical Stream Validation (1080x1920, 60fps, AAC Stereo)
                                        │
                                        ▼
                         AUTOMATED PUBLISHER (scripts/publisher/)
                         ├── YouTube Shorts API Upload
                         ├── Automated Pinned Affiliate Comment (Zero-Cost Monetization)
                         └── Multi-Platform Syndication Hook (Instagram & Facebook Reels)
```

---

## 3. Detailed Component Specifications

### Component 1: Content & Storytelling Engine (`scripts/content/`)
- **`vault.py`:** Expansive repository of 100+ vetted, high-curiosity narratives per category:
  - *Devotional:* Real-world moral dilemmas from Mahabharata/Gita (workplace politics, anger control, family peace) rather than generic quotes.
  - *Tech:* Cutting-edge 2026 breakthroughs (Neuralink human trials, humanoid factory workers, solid-state EV batteries, quantum compute).
  - *Facts:* Cosmic paradoxes, deep-sea anomalies, and neurobiological mysteries.
  - *Books:* Actionable psychological rules from *Atomic Habits*, *The Psychology of Money*, *48 Laws of Power*, and *Deep Work*.
- **`trending.py`:** Real-time ingestion scraper for live tech and science breakthroughs.
- **`dedup.py`:** Reads `output/upload_ledger.json` and enforces a strict 60-day cool-down window for every topic. Strips duplicate title prefixes (`Today in History — Today in History — `).
- **The 3-Act Viral Structure:**
  1. *Act 1 (0.0s – 2.0s):* Cliffhanger / impossible curiosity hook starting at second 0.1.
  2. *Act 2 (2.0s – 22.0s):* Rapid escalation, maximum 6–8 words per spoken thought, visual cut every 2.5 seconds.
  3. *Act 3 (22.0s – 28.0s):* Infinite loop ending that connects seamlessly back into the opening sentence (driving 110%+ APV).

---

### Component 2: Speech & Word-Boundary Timing (`scripts/voice/`)
- **`synthesizer.py`:** Uses `edge_tts.Communicate.stream()` to write high-definition audio while simultaneously harvesting `WordBoundary` events.
  - Extracts exact millisecond start and end boundaries:
    ```python
    {
      "word": "paralyzed",
      "start": 0.150,
      "end": 0.620
    }
    ```
- **`voices.py`:** Curated natural neural voice mapping:
  - Telugu: `te-IN-MohanNeural` (Authoritative/Storyteller) & `te-IN-ShrutiNeural` (Warm/Narrative)
  - Hindi: `hi-IN-MadhurNeural` (Deep/Engaging) & `hi-IN-SwaraNeural` (Expressive)
  - English: `en-US-ChristopherNeural` (Cinematic/Paced) & `en-US-GuyNeural` (Energetic)

---

### Component 3: Kinetic Subtitle Engine (`scripts/subtitles/`)
- **`ass_builder.py`:** Replaces flat PIL image text with an **Advanced SubStation Alpha (`.ass`)** subtitle file.
  - **Why `.ass`?** FFmpeg's `libass` engine renders subtitles natively onto video streams with sub-pixel antialiasing, millisecond karaoke timing, and rich geometric styling without performance loss.
  - **Visual Specs:**
    - Font: `Nirmala UI` / `assets/fonts/Nirmala.ttc` (100% support for Latin, Telugu, and Devanagari).
    - Font Size: 56pt (Shorts optimal readability).
    - Active Word: Highlighted in `#FFDD00` bright gold.
    - Inactive Words: Crisp `#FFFFFF` white with 5px solid black outline shadow (`Outline=5`).
    - Positioning: Centered (`Alignment=2`), vertically positioned in safe middle zone (`MarginV=540`).
    - Chunks: Groups words into 1-to-2 word rapid bursts.

---

### Component 4: Continuous Motion & B-Roll Engine (`scripts/visual/`)
- **`broll.py`:** Fetches real vertical `1080x1920` MP4 video clips from open royalty-free feeds (Pexels, Pixabay, open archives) matching semantic keywords.
- **`motion.py`:** Continuous camera physics engine:
  - If high-resolution photographic assets are used, FFmpeg applies a continuous smooth camera push-in (`zoompan=z='min(zoom+0.0015,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1920:fps=60`).
  - Enforces rapid scene cuts every **2.5 to 3.5 seconds**. The screen is never frozen.
- **`cover.py`:** Dedicated Frame 0 (0.0s to 0.4s) Hook Card:
  - High-contrast visual shock.
  - 3-word bold gold hook headline.
  - Zero channel intros or logo delays.

---

### Component 5: Sound Design & Multi-Track Mixing (`scripts/audio/`)
- **`mixer.py`:** Permanently removes the legacy 220Hz sine wave beep and implements a 3-track studio audio mix in FFmpeg:
  1. *Track 1 (Voice):* Normalized to `-14 LUFS` with dynamic peak compression.
  2. *Track 2 (BGM):* Genre-curated royalty-free ambient loops stored in `assets/audio/bgm/`:
     - Devotional: Sacred tanpura and bamboo flute drone.
     - Tech: Cyber ambient synth pulse.
     - Facts: Mystery tension riser.
     - Books: Reflective cinematic piano.
     - Mixed at `-24 dB` during speech, automatically swelling during pauses via sidechain ducking.
  3. *Track 3 (SFX):* Sub-bass impact at second `0.0` and subtle air whooshes on scene transitions.

---

### Component 6: The 6-Gate End-to-End QA Validation Suite (`scripts/qa/`)
Every video must pass all 6 gates with a 100% score before publication is permitted:
1. **Gate 1: Freshness & Anti-Duplicate Check:** Rejects topics used in the last 60 days, eliminates string prefix duplicates.
2. **Gate 2: Audio & BGM Verification:** Confirms duration is between 22s and 45s, verifies real BGM presence, verifies zero audio clipping.
3. **Gate 3: Motion & Pacing Verification:** Verifies scene cuts occur every 2.5–3.5s, confirms 60fps continuous camera motion.
4. **Gate 4: Subtitle & Glyph Integrity:** Validates that word timings are non-empty and every rendered character contains a valid glyph (zero `□` boxes).
5. **Gate 5: Safe-Zone Protection:** Strictly enforces that the bottom 22% (pixels 1498 to 1920) contains zero text or buttons to protect YouTube Shorts' native channel handle and subscribe UI.
6. **Gate 6: Technical Container Probe:** Uses `ffprobe` to ensure vertical 1080×1920 resolution, H.264 video codec, YUV420p pixel format, and stereo AAC audio.

---

### Component 7: Monetization & Syndication (`scripts/monetization/`)
- **`affiliates.py`:** Automatically posts a category-specific affiliate pinned comment on every upload:
  - Books: Amazon Audible 30-Day Free Trial ($5 CPA per free signup).
  - Tech: Amazon Associates gadgets & high-ticket SaaS tools ($20–$50 CPA).
  - Crypto: Hardware wallet & charting tools ($10–$25 CPA).
  - Health/Cooking: Kitchen essentials & supplements.
- **`syndicate.py`:** Automated hooks to syndicate finished 1080×1920 MP4s to Instagram Reels and Facebook Reels for 3x audience reach at zero additional production cost.

---

## 4. Modular Directory Structure

```
scripts/
├── content/
│   ├── vault.py          ──► 100+ high-hook story databases per category
│   ├── trending.py       ──► Real-time 2026 tech and science scrapers
│   └── dedup.py          ──► 60-day ledger history checking and title sanitization
├── voice/
│   ├── synthesizer.py    ──► Edge-TTS neural speech with WordBoundary event streaming
│   └── voices.py         ──► Natural voice mappings for Telugu, Hindi, and English
├── visual/
│   ├── broll.py          ──► Multi-source vertical video B-roll fetching & caching
│   ├── motion.py         ──► 60fps Ken Burns camera pan/zoom and scene slicing (2.5s cuts)
│   └── cover.py          ──► Frame 0 scroll-stopping hook card generator
├── audio/
│   ├── mixer.py          ──► FFmpeg multi-track audio ducking (-24dB BGM + speech normalization)
│   └── sfx.py            ──► Transition whooshes and hook sub-bass placement
├── subtitles/
│   └── ass_builder.py    ──► Advanced SubStation Alpha (.ass) kinetic karaoke subtitle compiler
├── qa/
│   └── validator.py      ──► 6-Gate pre-publish inspection suite
├── monetization/
│   ├── affiliates.py     ──► Automated pinned comment affiliate engine
│   └── syndicate.py      ──► Multi-platform distribution hooks
└── pipeline.py           ──► Clean master coordinator executing steps in isolated try/catch blocks
```

---

## 5. Execution Roadmap

- **Stage 1:** Deploy `scripts/content/dedup.py` and `scripts/content/vault.py` (Immediate fix for duplicate uploads and outdated topics).
- **Stage 2:** Deploy `scripts/voice/synthesizer.py` and `scripts/subtitles/ass_builder.py` (Word-level kinetic captions with gold pop highlights).
- **Stage 3:** Deploy `scripts/audio/mixer.py` and curate `assets/audio/bgm/` (Eliminate 220Hz sine wave, add real ambient music and whoosh SFX).
- **Stage 4:** Deploy `scripts/visual/motion.py` and `scripts/visual/broll.py` (Continuous 60fps Ken Burns camera push-in and 2.5s scene cuts).
- **Stage 5:** Deploy `scripts/qa/validator.py` (Enforce the 6-Gate validation suite).
- **Stage 6:** Local end-to-end integration test of 1 complete Short, verification across all 6 gates, commit and push to `origin/main` for automated cloud execution.
