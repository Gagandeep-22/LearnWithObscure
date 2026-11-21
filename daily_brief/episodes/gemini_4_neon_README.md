# Gemini 4 Neon — Zeno Sensei's Brief (21 November 2026)

This is a dedicated, 9:16 Zeno Short using an official launch image and an illustrated coding workflow. It keeps the canonical
`daily_brief/assets/zeno.png` illustration and existing narration tooling.
It does not modify the AI Universe video or any previous Shorts.

Source: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/

## 1. Download Google's real imagery to your local assets directory

```powershell
uv run python daily_brief/download_neon_images.py
```

The downloader reads the official Google article, downloads the article's
`og:image`, and optionally one news image from that article. The images
are stored under `daily_brief/assets/neon/`, accompanied by `sources.json`
with the actual source URLs. **Check the actual images before publishing**:
the opening and announcement use the launch image, while the later
coding-workflow segment uses a clearly labeled conceptual animation instead
of claiming to display a real product demo. No invented IDE screenshots are used. Google's imagery is
third-party copyrighted content: credit the source and follow the publisher's
reuse terms, or replace it with permission-cleared images.

## 2. Generate the five narration clips

```powershell
$env:ZENO_EPISODE = "daily_brief/episodes/gemini_4_neon.json"
uv run --env-file .env python daily_brief/prepare_audio.py
```

Repeat the audio preparation if a call limit leaves clips missing.

## 3. Preview in portrait mode

```powershell
$env:ZENO_PREVIEW = "1"
$env:ZENO_SILENT = "1"
uv run --env-file .env manim --disable_caching -p daily_brief/gemini_4_neon.py ZenoGemini4Neon
Remove-Item Env:ZENO_PREVIEW, Env:ZENO_SILENT -ErrorAction SilentlyContinue
```

## 4. Final narrated 1080 × 1920 render

```powershell
uv run --env-file .env manim --disable_caching -p daily_brief/gemini_4_neon.py ZenoGemini4Neon
Remove-Item Env:ZENO_EPISODE -ErrorAction SilentlyContinue
```

The scene loads real downloaded images from `sources.json`; it will fail
clearly if imagery is missing instead of quietly substituting stock art.
The official article URL belongs in the video description as attribution.
Manually check the rendered video for crop, image legibility and captions.
The image frame now sits behind the downloaded photo; if an opaque blank rectangle
remains after rendering, inspect the local asset files and report the frame.
The episode narration text was not changed, so existing TTS clips are reusable.
