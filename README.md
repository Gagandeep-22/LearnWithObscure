# Learn With Obscure

Animated programming explainers made with Manim.

## Setup

Install the project dependencies with `uv sync`.

## Render a scene

Run these commands from the project root:

```powershell
uv run manim --disable_caching -pql src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
uv run manim -pql src/learnwithobscure/scenes/first_animation.py HelloLearn
```

Use `-pqh` instead of `-pql` for a higher quality render. Manim writes rendered
videos, cached animations, and generated voiceover files under `media/`.
Disable caching for the binary-search scene so cached animations don't skip
voiceover audio.

## Project layout

```text
assets/characters/                 Character illustrations
src/learnwithobscure/               Python package
src/learnwithobscure/scenes/        Manim scene scripts
media/                              Generated renders and caches (ignored by Git)
```
