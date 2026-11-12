# Learn With Obscure Video Template

Use this guide when planning, scripting, animating, and reviewing a new programming lesson. It captures the storytelling and production approach established by the Binary Search demo while leaving room for each topic to have its own best examples and visuals.

For character dialogue and personality, also follow [CHARACTERS.md](CHARACTERS.md). For repository setup and current commands, see [README.md](README.md).

## Creative intent

Learn With Obscure presents programming as learning in public. The creator and audience are learners alongside Obscure, not students being lectured at. Each video should be approachable, visually clear, technically accurate, and comprehensive enough to cover the concept's useful context, examples, edge cases, code, and complexity when relevant.

The recurring teaching relationship is:

1. Obscure brings a concrete goal or confusion.
2. Zeno Sensei introduces the key idea in plain language.
3. Obscure asks a genuine question that exposes a likely learner misunderstanding.
4. Zeno answers while the visuals demonstrate the answer.
5. Obscure restates the insight in his own words.

Keep the humor gentle and in service of memory or clarity. Never make Obscure the joke. See [CHARACTERS.md](CHARACTERS.md) for the full voice guide.

## Reusable lesson arc

Treat these as planning beats, not mandatory separate scenes. Combine, reorder, or omit a beat when the topic calls for it, but preserve a clear path from learner problem to understanding and practical use.

1. **Hook:** Start with a specific problem, question, or surprising constraint. Make the viewer want the answer before naming the solution.
2. **Concept and prerequisites:** Introduce the concept and state any conditions it relies on. For binary search, that condition is sorted input.
3. **Visual vocabulary:** Establish the data, target, variables, or diagram labels viewers need to follow the explanation.
4. **Worked example:** Walk through one representative example from start to finish. Show the decision at each step and why it is valid.
5. **Code connected to state:** When teaching code, highlight the relevant statement while updating the visual state it controls. Explain both the line and its effect; do not make the viewer infer the connection.
6. **Learner questions:** Use Obscure's questions to surface the non-obvious reasoning, edge cases, and common misconceptions.
7. **Additional cases:** Include cases that materially change behavior, such as immediate success, a later success, and failure or boundary conditions. Choose cases appropriate to the topic.
8. **Practical guidance:** Explain when the technique is useful, its assumptions, and meaningful limitations or alternatives.
9. **Complexity or tradeoffs:** Give a short result overview before explaining why. Then show the reasoning for each relevant measure. State what is included in the measure; for example, distinguish auxiliary space from input storage.
10. **Complete implementation:** Present a usable implementation, split into readable pages if needed. Relate important code decisions back to the earlier walkthrough.
11. **Recap and close:** Let Obscure summarize the idea, reinforce the main takeaway, and close with a brief, natural channel call to action.

For a lesson that is not algorithmic, replace worked traces or complexity analysis with the equivalent demonstrations, tradeoffs, or evidence the topic needs. Do not add a section merely to match the outline.

## Story and script planning

Before animating, write a compact storyboard with one row per screen or major beat:

| Beat | Learner question or purpose | What appears | What changes | Narrator |
| --- | --- | --- | --- | --- |
| Hook | What problem needs solving? | Concrete task or data | Establish the challenge | Obscure |
| Explanation | What is the core idea? | Concept-specific visual | Demonstrate a decision | Zeno |
| Practice | Does it work in other cases? | New input or scenario | Show success, failure, or edge case | Both as useful |
| Summary | What should the viewer retain? | Result, code, or takeaway | Connect back to the hook | Both as useful |

For each narration line, check that it:

- Adds an explanation, question, or transition instead of reading every visible label aloud.
- Names the reason behind a decision, not just the action.
- Uses pronunciation-friendly wording for TTS, especially for symbols, identifiers, and code.
- Matches the animation beat and leaves enough time to understand the screen.

Keep in-scene dialogue captions shorter than the spoken narration. Captions are an on-screen summary, not a transcript. Avoid placing captions over code, state labels, or other important information.

## Visual language

The Binary Search demo establishes a recognizable visual baseline:

- Lavender background (`BG`), dark purple text (`DARK`), purple structure and labels (`PURPLE` / `LAVENDER`), and pink emphasis (`PINK`).
- Bold headings, readable body text, white rounded panels where a panel improves grouping, and clear contrast for highlighted values or decisions.
- Obscure and Zeno Sensei as visual participants, with consistent character assets and scale.
- Data structures and state updates drawn directly: array cells, indices, bounds, active ranges, counters, code highlights, and results.

Reuse this palette and character treatment unless a deliberate channel-wide visual change is planned. Let the topic determine the main visual metaphor. Keep the screen focused: one primary point per beat, stable positions for changing values, and enough spacing that labels do not collide. Design for a 16:9 frame and check that text remains legible at smaller playback sizes. Use native Manim `Text` for ordinary labels where practical; the current scene does not require LaTeX for its formulas.

When a screen changes, make ownership explicit: know which mobjects belong to the outgoing screen, fade or remove each outgoing group once, and then introduce the next screen. Do not animate an old group out again after it has already been removed; Manim may reintroduce those objects for that animation. Review screen transitions as carefully as individual frames.

## Voiceover and timing

The Binary Search scene uses `manim-voiceover` with Gemini TTS. The `speak()` helper adds the generated audio and holds the visual beat until speech completes; optional animations can play during the spoken line. Preserve this voice-led timing for future narrated videos instead of relying on guessed fixed waits.

Current Binary Search voice assignments are Obscure = `Achird` and Zeno Sensei = `Leda`, using `gemini-3.1-flash-tts-preview`. Treat these as the current project configuration, not a requirement that every future video must use the same voice settings.

Prepare or cache narration before expensive final renders. Keep generated audio and video under ignored `media/` paths, never in source control. For a new video, use a video-specific audio cache directory and preparation workflow so clips can be resumed and reused without regenerating the entire narration. Keep credentials in the ignored root `.env` or the local environment; never put API keys in code or tracked documentation.

Do not change narration solely to solve a visual layout issue. Update the display independently unless the script itself is being revised.

## Scene implementation conventions

- Put each substantial video in its own scene module under `src/learnwithobscure/scenes/`.
- Resolve assets from the repository root rather than from the shell's current directory.
- Reuse small helpers for text, headings, characters, repeated data elements, and state-dependent positions when they reduce duplication.
- Keep the visual state and algorithm/code state synchronized. Prefer one clear update per decision over many decorative movements.
- Use `Group` for mixed collections that contain `ImageMobject`s; use `VGroup` for vector mobjects where appropriate.
- Keep transitions explicit. If a screen's objects need to be removed later, retain the group or object references and remove them exactly once.
- Preserve distinct source strings for narration and captions. This keeps captions concise and avoids coupling speech edits to screen layout.

## Suggested project workflow

1. Read `PROJECT_CONTEXT.md` and `CHARACTERS.md`, then inspect a related scene for established helpers and style.
2. Confirm the concept, prerequisites, examples, edge cases, and complexity claims against a reliable technical source before scripting.
3. Draft the storyboard and narration. Check that the hook, example, questions, and summary form one coherent lesson.
4. Build the visual sequence incrementally. First validate a representative screen and its transitions, then complete the scene.
5. Generate missing voice clips through the project's preparation workflow. Keep requests resumable and respect current provider quotas.
6. Run a low-quality full render first. Watch the output around screen transitions and check text fit, audio synchronization, and every example's correctness.
7. Fix visual or timing problems at their source. Do not regenerate or edit narration when only display layout is wrong.
8. Render a higher-quality preview and inspect it before the final-quality export. Use the existing Manim quality presets documented in `README.md`.
9. Confirm the output video and audio are correct, then update project notes if the workflow, assets, voices, or scene structure changed.

## Per-video planning worksheet

Copy and fill this section when starting a new lesson:

- **Topic and audience takeaway:**
- **Hook problem or question:**
- **Prerequisites and assumptions:**
- **Core idea in one sentence:**
- **Example input and expected outcome:**
- **What Obscure asks:**
- **What Zeno demonstrates visually:**
- **Additional cases or edge conditions:**
- **Practical use and limitations:**
- **Complexity or other tradeoffs, if relevant:**
- **Code language and implementation:**
- **Visual metaphor and required assets:**
- **Narration voice mapping:**
- **Screens and transitions to inspect:**
- **Low-quality render reviewed:**
- **Final render reviewed:**
