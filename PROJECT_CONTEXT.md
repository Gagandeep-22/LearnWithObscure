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

The visual explanation uses one moving comparison window and completes each
comparison and swap before moving on. The Java walkthrough is a key part of
the channel: each highlighted statement must match its visible effect. Fixed
array slots, `i` and `end` pointers, and `temp` and `swapped` displays follow the
execution events in `bubble_sort_trace.py`. Show the temporary duplicate values
between the two array assignments; do not animate both assignments as one swap.
Short narration clips belong to individual steps rather than an entire pass.
Explain the first swap fully; later repetitions can use contextual comments
and readable silent beats, while retaining every statement's animation and
numeric caption. Avoid repeating narration verbatim. The `swapped` dialogue
uses the already-sorted second-pass result to explain optional early exit:
true records a change, while a complete no-swap pass proves sorting is done.
Removing the flag and its exit check still sorts with all shrinking passes.
Do not promise fast performance merely because input is nearly sorted.
Run `uv run python -m unittest discover -s tests -v` to verify the execution
model. Set `LWO_REVIEW_TIMELINE` to an ignored JSON path under `media/` when
rendering to record completed steps and frame-review timestamps.

The visual style uses a lavender background, purple and pink accents, array
cells, and the student/robot character illustrations. Keep the code legible on
mobile-size screens and keep text inside its cards and panels.

## Selection Sort video

`SelectionSortDemo` in `src/learnwithobscure/scenes/selection_sort.py` extends
the same lesson format to Selection Sort. See
`docs/selection_sort_storyboard.md` for the coverage map and review points.
Obscure opens with an array to sort when comparisons are cheap but moving values
is expensive, giving Zeno a reason to introduce Selection Sort. He then predicts
the next selection, questions the need to scan every remaining
value, and tests whether Bubble Sort's no-swap early exit carries over. Zeno
Sensei answers with visible evidence and occasional gentle humor. Avoid repeated
stock praise or narrating every repeated step with the same sentence.

The main example remains `[5, 1, 4, 2, 8]`, making the difference from Bubble
Sort visible: scan the unsorted suffix, remember the smallest value's index,
then swap once to extend the sorted prefix. Moving `minIndex` does not move
array values. The Java walkthrough follows the statement events in
`selection_sort_trace.py`, with separate temporary-value and array-assignment
steps. Preserve the intermediate duplicate values during a swap, just as in
Bubble Sort's code trace.

Cover ascending and descending order, already-sorted and reverse input,
duplicates and negative numbers, empty and single-element arrays, and the
stability counterexample `[2A, 2B, 1]`. Strict `<` keeps the first minimum seen
but does not make a long-distance swap stable. A no-swap pass does not prove
the entire array is sorted: `[1, 3, 2]` still needs its next pass.

This guarded implementation always makes `n(n - 1) / 2` value comparisons,
including sorted input, for quadratic best, average, and worst time as input
size grows. For nonempty input it makes at most `n - 1` swaps, skips swaps when
the minimum is already at the destination, and needs `O(1)` auxiliary space.
Explain the comparison-versus-write tradeoff, practical limitations, and
complete Java implementation with example output.

Prepare narration with
`uv run --env-file .env python scripts/prepare_selection_sort_audio.py`.
It reuses `media/audio_files/selection_sort_demo/`, defaults to 8 new requests
per run, and spaces new requests by at least 22 seconds. Then render with:

```powershell
uv run --env-file .env manim --disable_caching -pql src/learnwithobscure/scenes/selection_sort.py SelectionSortDemo
```

For a silent review, set `LWO_DISABLE_VOICEOVER=1`, render with a separate
output name such as `SelectionSortDemo_silent`, and remove the variable when
finished. Set `LWO_REVIEW_TIMELINE` to an ignored JSON path under `media/` to
record frame-review timestamps. Run
`uv run python -m unittest discover -s tests -v` for both execution models.
See the README for full silent-render commands and quality presets.

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

The standalone vertical tech brief lives in `daily_brief/`, separate from the
programming lessons. It contains `daily_brief.py`, `prepare_audio.py`,
`episode.json`, and `assets/zeno.png`. See `daily_brief/README.md` for commands.
It uses the shared root `.env`; generated narration in `daily_brief/audio/`
is ignored by Git.

```text
assets/characters/                         Student and robot illustrations
src/learnwithobscure/                      Python package
src/learnwithobscure/scenes/               Manim scenes
src/learnwithobscure/scenes/binary_search_complete.py
                                             Main binary-search lesson
src/learnwithobscure/scenes/bubble_sort.py    Bubble Sort lesson
src/learnwithobscure/scenes/selection_sort.py Selection Sort lesson
src/learnwithobscure/scenes/selection_sort_trace.py
                                             Selection Sort execution model
src/learnwithobscure/scenes/first_animation.py
                                             Small introductory scene
scripts/prepare_bubble_sort_audio.py          Resumable Bubble Sort TTS preparation
scripts/prepare_selection_sort_audio.py       Resumable Selection Sort TTS preparation
docs/selection_sort_storyboard.md             Selection Sort story and review guide
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
