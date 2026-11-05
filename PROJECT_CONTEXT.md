# Project context: Learn With Obscure

This document is a handoff for future work on the project, including work from
another computer or a fresh assistant session. Read this together with the
README before changing the scenes.

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

The visual style uses a lavender background, purple and pink accents, array
cells, and the student/robot character illustrations. Keep the code legible on
mobile-size screens and keep text inside its cards and panels.

## Dialogue and voiceover status

The animation is currently a silent content-first cut. The `speak()` helper
uses its animation arguments and adds a short reading pause, but it does not
play the narration string as audio. Dialogue captions are short summaries of
the intended character lines.

The creator plans to add AI-generated voice dialogues later, after the visuals
are complete. Do not assume the current fixed pauses are final voiceover timing.
When adding voiceover, align each audio clip to the corresponding animation
beat, preserve enough reading time for on-screen text, and keep generated audio
out of source code. The project already includes the `manim-voiceover[gemini]`
dependency.

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
src/learnwithobscure/scenes/first_animation.py
                                             Small introductory scene
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
uv run manim -pql src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
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
