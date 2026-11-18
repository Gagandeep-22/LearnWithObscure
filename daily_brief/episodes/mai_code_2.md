# Zeno's Brief — MAI Code 2 (19 November 2026)

Original announcements (17 November):
- https://github.blog/changelog/2026-11-17-mai-code-2-and-mai-code-2-flash-in-github-copilot/
- https://microsoft.ai/news/introducing-mai-code-2-and-mai-code-2-flash/

Seven dedicated vertical motion-graphics shots; original mascot, lavender palette,
measured narration timings and full-screen transitions. The picker and Java
files are illustrative, not screenshots or live demos. The outro explicitly
speaks the daily-news subscription invitation.

From the repository root in PowerShell:

```powershell
$env:ZENO_EPISODE = "daily_brief/episodes/mai_code_2.json"
$env:ZENO_TTS_MODEL = "gemini-3.8-flash-tts"
$env:ZENO_TTS_VOICE = "Leda"
uv run --env-file .env python daily_brief/prepare_audio.py --max-new 1
```

Review the first WAV in daily_brief/audio/2026-11-19-mai-code-2/.
If it sounds right, prepare the remaining clips:

```powershell
uv run --env-file .env python daily_brief/prepare_audio.py --max-new 7 --interval 65
Remove-Item Env:ZENO_PREVIEW, Env:ZENO_SILENT, Env:ZENO_AUDIO -ErrorAction SilentlyContinue
uv run manim --disable_caching -p daily_brief/mai_code_2.py ZenoMAICode2
```

For a silent preview, set ZENO_PREVIEW=1 and ZENO_SILENT=1 before rendering, and
clear both afterwards. Do not use landscape quality presets. Final resolution
is 1080x1920 at 30 fps. Actual audio determines total duration; the authored
silent estimate is 54 seconds. Check voice, layout and duration before upload.

After finishing, clear ZENO_EPISODE, ZENO_TTS_MODEL and ZENO_TTS_VOICE to avoid
selecting this episode elsewhere. The AI Universe model and cache are unaffected.
No paid audio or actual Manim render has been executed as part of this change.
