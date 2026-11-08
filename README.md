# Learn With Obscure

Animated programming explainers made with Manim.

## Setup

Install the project dependencies with `uv sync`.

Set a valid `GEMINI_API_KEY` in the environment before rendering. Keep the key
local and never commit it. Check access to both narration voices with:

```powershell
uv run python scripts/preflight_gemini.py
```

## Render a scene

Run these commands from the project root:

```powershell
uv run manim --disable_caching -pqk src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
uv run manim -pql src/learnwithobscure/scenes/first_animation.py HelloLearn
```

The binary-search scene uses Manim's 4K/60 fps `-qk` preset. Manim writes
rendered videos, cached animations, and generated voiceover files under `media/`.
Disable caching for the binary-search scene so cached animations don't skip
voiceover audio.

## Project layout

```text
assets/characters/                 Character illustrations
src/learnwithobscure/               Python package
src/learnwithobscure/scenes/        Manim scene scripts
media/                              Generated renders and caches (ignored by Git)
```
