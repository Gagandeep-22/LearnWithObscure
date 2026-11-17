# Zeno's daily tech brief

A standalone 9:16 Manim template using the original Zeno Sensei illustration
and the same bright lavender palette as the programming lessons.

- `daily_brief.py`: animated scene with reserved space for Shorts controls.
- `episode.json`: date, source, visual beats, captions and narration.
- `prepare_audio.py`: resumable Gemini narration generation.
- `episode_support.py`: shared episode and WAV cache validation.
- `assets/zeno.png`: unchanged character illustration.
- `audio/`: generated WAVs and cache fingerprints (ignored by Git).

Run from the repository root after `uv sync`.

## 1. Silent preview (no Gemini calls)

```powershell
$env:ZENO_PREVIEW = "1"
$env:ZENO_SILENT = "1"
try {
    uv run manim --disable_caching -p -o ZenoDailyBrief_silent daily_brief/daily_brief.py ZenoDailyBrief
} finally {
    Remove-Item Env:ZENO_PREVIEW, Env:ZENO_SILENT -ErrorAction SilentlyContinue
}
```

Preview resolution: 540 x 960 at 30 fps.

## 2. Prepare narration

Use the existing ignored root .env with GEMINI_API_KEY.

```powershell
uv run --env-file .env python daily_brief/prepare_audio.py
```

The default model is gemini-3.1-flash-tts-preview and the voice is Leda.
Override either with ZENO_TTS_MODEL or ZENO_TTS_VOICE if desired; keep the
same values for generation and rendering. Existing valid v1 WAV caches
are reused when speech, model and voice have not changed. New requests
are spaced 22 seconds apart, with at most eight per run. Repeat until
the script reports zero remaining clips. No video is rendered here.

## 3. Narrated render (default)

```powershell
Remove-Item Env:ZENO_PREVIEW, Env:ZENO_SILENT -ErrorAction SilentlyContinue
uv run manim --disable_caching -p daily_brief/daily_brief.py ZenoDailyBrief
```

Final resolution: 1080 x 1920 at 30 fps. This render uses cached WAVs
only, with actual measured audio durations instead of fixed waits.
Missing, stale or corrupt clips stop the render before animation starts.
Do not use landscape quality presets or pass an alternate resolution.
Manim output remains in the ignored media directory.

For a 540 x 960 narrated preview, set ZENO_PREVIEW=1 and ZENO_AUDIO=1;
clear both afterwards. ZENO_SILENT=1 always overrides audio.

## Future episodes

Set ZENO_EPISODE to the path of another episode JSON for both commands.
Keep the episode id unique. Update the script and captions independently;
visual-only changes do not invalidate the narration cache. Graphics support
hook, deal, cube, room, scientist, stack and outro, plus a generic text tile.

The episode data is editorial input: verify the original source before
publishing. Review the actual render at mobile size, including caption fit,
voice timing, pronunciation, and platform UI overlays. The safe area is
a conservative layout guide, not a guarantee for every YouTube client.
