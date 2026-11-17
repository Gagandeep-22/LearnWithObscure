# Daily tech brief

This folder contains the standalone vertical Zeno Sensei tech brief:

- `daily_brief.py`: the `ZenoDailyBrief` Manim scene.
- `prepare_audio.py`: resumable Gemini narration preparation.
- `episode.json`: episode metadata, captions, and narration.
- `assets/zeno.png`: the brief's character illustration.
- `audio/`: generated narration cache (ignored by Git).

Run commands from the project root. Use the shared root `.env` for
`GEMINI_API_KEY`.

Prepare narration:

```powershell
uv run --env-file .env python daily_brief/prepare_audio.py
```

Render a silent preview:

```powershell
$env:ZENO_PREVIEW = "1"
uv run manim daily_brief/daily_brief.py ZenoDailyBrief
Remove-Item Env:ZENO_PREVIEW
```

Render with prepared narration:

```powershell
$env:ZENO_AUDIO = "1"
try {
    uv run manim daily_brief/daily_brief.py ZenoDailyBrief
} finally {
    Remove-Item Env:ZENO_AUDIO -ErrorAction SilentlyContinue
}
```

`ZENO_EPISODE` can select another episode JSON path, relative to the working
directory or absolute. Both scripts default to this folder's `episode.json`
and share `audio/<episode-id>/`. Manim renders remain under the root `media/`.
