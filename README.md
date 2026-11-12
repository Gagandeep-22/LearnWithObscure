# Learn With Obscure

Animated programming explainers made with Manim.

Use [VIDEO_PRODUCTION_TEMPLATE.md](VIDEO_PRODUCTION_TEMPLATE.md) as the reusable
story, visual, voiceover, and review guide when planning future videos. Follow
[CHARACTERS.md](CHARACTERS.md) for Obscure and Zeno Sensei's dialogue style.

## Setup

Install the project dependencies with `uv sync`.

Set `GEMINI_API_KEY` in your local environment or ignored `.env` file.
Keep the key local and never commit it.

## Prepare Binary Search narration

Generate missing narration audio separately from the animation render:

```powershell
uv run python scripts/prepare_binary_search_audio.py
```

The preparation command walks the Binary Search scene, reuses existing WAV
files, and generates only missing clips. It defaults to at most **8 new TTS
requests per run**, with at least **22 seconds between requests** to respect
the observed 3-requests-per-minute free-tier limit. If clips remain, run it
again after the quota resets. Use `--max-new 5` to set a smaller request
budget, or `--min-request-interval 25` for more spacing. If Gemini still
returns a quota or transient error, the script stops cleanly; completed WAV
files remain cached and can be resumed later.

This command does not render video. It saves audio persistently under
`media/audio_files/binary_search_demo/`.

The legacy preflight command is now a local configuration check only:

```powershell
uv run python scripts/preflight_gemini.py
```

It does not contact Gemini, validate the key, or consume request quota.

## Bubble Sort video

Prepare missing Bubble Sort narration clips separately from the render:

```powershell
uv run --env-file .env python scripts/prepare_bubble_sort_audio.py
```

The command reuses cached clips under `media/audio_files/bubble_sort_demo/` and
generates at most 8 new clips per run, with at least 22 seconds between TTS
requests. Rerun it to continue if clips remain. Then render a low-quality
review copy:

```powershell
uv run --env-file .env manim --disable_caching -pql src/learnwithobscure/scenes/bubble_sort.py BubbleSortDemo
```

Use `-pqh` for a high-quality preview or `-pqk` for the 4K/60 fps final render.
Keep `--disable_caching` so Manim does not skip voiceover audio.

To render a silent Bubble Sort video without reading cached audio or contacting
Gemini, set `LWO_DISABLE_VOICEOVER=1` in PowerShell and choose a separate output
name:

```powershell
$env:LWO_DISABLE_VOICEOVER = "1"
uv run manim --disable_caching -ql -o BubbleSortDemo_silent src/learnwithobscure/scenes/bubble_sort.py BubbleSortDemo
Remove-Item Env:LWO_DISABLE_VOICEOVER
```

## Render a scene

Once narration preparation has completed, render the Binary Search scene:

```powershell
uv run manim --disable_caching -pql src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
```

Use `-pqh` for a higher-quality preview or `-pqk` for the 4K/60 fps final
preset. The scene checks its persistent audio cache before requiring an API
key, so a fully cached render can run without making Gemini requests. If any
clip is still missing, the render reports that the API key is needed; run the
audio preparation command first.

Keep `--disable_caching` for this scene because cached Manim animations can
otherwise skip voiceover audio. This flag controls Manim animation caching; it
does not disable the separate WAV audio cache.

The introductory scene is:

```powershell
uv run manim -pql src/learnwithobscure/scenes/first_animation.py HelloLearn
```

## Project layout

```text
assets/characters/                  Character illustrations
src/learnwithobscure/                Python package
src/learnwithobscure/scenes/         Manim scenes
scripts/prepare_binary_search_audio.py  Resumable audio preparation
media/                               Generated renders and audio (ignored by Git)
```
