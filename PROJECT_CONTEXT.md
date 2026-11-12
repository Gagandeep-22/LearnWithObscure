# Project context: Learn With Obscure

This document is a handoff for future work on the project, including work from
another computer or a fresh assistant session. Read this together with the
README before changing the scenes. Use `VIDEO_PRODUCTION_TEMPLATE.md` as the
reusable lesson and production blueprint for future videos.

## Channel and project goal

Learn With Obscure is a YouTube channel built around learning programming
concepts in public. The creator is learning the material too, so the tone
should feel curious, approachable, and collaborative rather than like an
expert lecturing from a distance. The videos are intended to be useful and
polished, with the possibility of becoming a side income over time.

The aim is to explain concepts comprehensively. Keep useful context, examples,
edge cases, code, and complexity analysis when shaping a lesson. Improve the
hook, clarity, and pacing without stripping the topic down to only a short
visual demonstration.

## Recurring characters

The chibi learner is **Obscure** and the AI robot mentor is **Zeno Sensei**. Their
reusable personalities, dialogue style, and teaching rhythm live in
`CHARACTERS.md`. Use that file whenever creating or revising a learning video.
Obscure is curious and asks the audience's “why” and “how” questions; Zeno Sensei
is calm, clear, and gently playful without talking down to him.

## Current focus: binary search video

The first video is a complete animated introduction to binary search. The
primary scene is `BinarySearchDemo` in
`src/learnwithobscure/scenes/binary_search_complete.py`.

The current scene covers:

- A hook asking whether we can find 10 in three checks.
- The sorted-data prerequisite and the `low`, `high`, and `mid` indices.
- A worked search for 10 in `[2, 4, 6, 8, 10, 12, 14]`, showing the checks at
  8, 12, and 10.
- A paired Java-and-array walkthrough where the active code line and visual
  state update together. It shows the bounds, midpoint, branch decisions, and
  returned index.
- Additional cases: an immediate match, a match after narrowing the range,
  and a target that is absent.
- When binary search is useful, its advantages and limitations, time and space
  complexity, and a complete iterative Java implementation.

## Bubble Sort video

The next narrated lesson is `BubbleSortDemo` in
`src/learnwithobscure/scenes/bubble_sort.py`. It demonstrates adjacent
compare-and-swap passes on `[5, 1, 4, 2, 8]`, connects the live comparisons to
Java statements, explains early exit and time/space complexity, and presents
an optimized in-place Java implementation. Its resumable Gemini audio
preparation command is `scripts/prepare_bubble_sort_audio.py`; audio is cached
separately under `media/audio_files/bubble_sort_demo/`.

The visual style uses a lavender background, purple and pink accents, array
cells, and the student/robot character illustrations. Keep the code legible on
mobile-size screens and keep text inside its cards and panels.

## Dialogue and voiceover status

The scene uses Gemini voiceover through `manim-voiceover[gemini]`. Its `speak()`
helper selects a distinct voice for Obscure and Zeno Sensei, runs the animation during
the spoken explanation, and holds the beat until the audio finishes. The Java
walkthrough is deliberately line-by-line and includes voiceover for every code
decision and bound update.

Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the ignored `.env` file before
rendering. Generated audio is cached under `media/` and must remain out of
source control. Dialogue captions stay short for mobile readability; automatic
voiceover subtitles are disabled because they would overlap the in-scene caption
card and code-trace state text.

## Recent decisions and fixes

- Keep the broad binary-search coverage; the creator explicitly prefers a
  comprehensive video over covering only a few basics.
- Start with a stronger hook and avoid repetitive introductory dialogue.
- Give dialogue beats more reading time. The current helper waits 1.4 seconds
  after a beat; revise this when narration is added.
- The long description in the “ANSWER-SPACE SEARCH” card was wrapped onto two
  lines after it overflowed its card.
- The Java walkthrough is meant to distinguish this video by connecting code
  statements to the visual array changes at the same time.
- A Manim `VGroup` containing character `ImageMobject`s caused a runtime error.
  The mixed collection now uses `Group`.
- The relocated binary search scene was successfully rendered at low quality
  after the folder move.

## Repository layout

```text
assets/characters/                         Student and robot illustrations
src/learnwithobscure/                      Python package
src/learnwithobscure/scenes/               Manim scenes
src/learnwithobscure/scenes/binary_search_complete.py
                                             Main binary-search lesson
src/learnwithobscure/scenes/bubble_sort.py    Bubble Sort lesson
src/learnwithobscure/scenes/first_animation.py
                                             Small introductory scene
scripts/prepare_bubble_sort_audio.py          Resumable Bubble Sort TTS preparation
media/                                     Generated renders and caches
```

Manim output under `media/` is generated and ignored by Git. `.env` is also
ignored; do not put credentials into tracked files. Character images are stored
under `assets/characters/`. The binary-search scene resolves those assets from
the repository root, so render it from the project root as shown below.

## Setup and render commands

The project uses `uv` and declares Manim plus Manim Voiceover in `pyproject.toml`.
From the repository root:

```powershell
uv sync
uv run manim --disable_caching -pql src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
```

Use `-pqh` for a higher-quality preview render. The introductory scene is:

```powershell
uv run manim -pql src/learnwithobscure/scenes/first_animation.py HelloLearn
```

The binary-search scene previously rendered successfully to
`media/videos/binary_search_complete/480p15/BinarySearchDemo.mp4`. The local
Windows environment reported missing SoX and an unavailable DejaVu Sans font;
these were warnings and did not prevent rendering. If rendering fails on a new
machine, inspect the first actual exception in the Manim traceback and check
that the project dependencies and fonts are installed.

## Working preferences for future changes

- Preserve the creator’s learn-along voice and the broad educational scope.
- Prefer clear, animated links between the algorithm’s state and the Java code.
- Keep dialogue readable, and plan to replace fixed pauses with voiceover-aware
  timing once narration is recorded/generated.
- Render after meaningful scene, layout, asset-path, or animation changes, and
  check the output visually for overflow and mobile readability.
- Keep project notes and run instructions current when the structure changes.
