# AI Universe — visual prototype

## Review milestone

Opening and foundations only, designed for the standard 16:9 main video. The original Obscure and Zeno Sensei assets and existing pastel color palette are reused.

From the repository root:

```powershell
uv run manim --disable_caching -pql src/learnwithobscure/scenes/ai_universe.py AIUniverseFoundations
```

Use `-pqh` for a higher quality review. This scene is silent by design: no Gemini requests, API key or narration cache needed. Dialogue appears as timed captions and has stable identifiers for subsequent voiceover integration. Silent timings are estimates and will change when real recordings are available.

## Character expression assets

Place the two reviewed transparent PNGs under `assets/characters/expressions/`:

- `obscure_confused.png` — original pose, changed expression.
- `obscure_questioning.png` — open-palm gesture.

Do not overwrite `student_chibi.png` or `robot_mentor.png`. The scene uses the master image if an expression is unavailable and prints a warning. To require both reviewed images for a visual review, set `$env:LWO_REQUIRE_EXPRESSION_ASSETS = "1"` before rendering and remove it afterward. The assets need to be copied locally because they are not included in this code-only change.

The new reactions include brief bounces, thinking tilts and nods. Poses are selected per dialogue beat, and the replacement is bounded to the existing character slot. Zeno continues using the original illustration with movement; further pose artwork must be approved before use.

Quiz answers now lay out below the measured question bounds, with equal-sized rows and a reserved caption region. The layout guard rejects overlaps if a future question or font is too large. Other scenes still require visual review.

## Sequence

1. Buzzword overload and character entrance; Zeno organizes the terms into techniques, models, capabilities and tools.
2. AI: chess search with predefined rules, illustrating that learning is not required. The small board shows an illustrative legal knight move, not a chess engine.
3. ML: labeled training emails, learned features and an unseen email prediction. The mail labels are illustrative, not actual classifier results.
4. Deep learning: handwritten digit, a conceptual network and animated signal flow. This is an illustration, not actual neural network inference.
5. Nested AI / ML / deep learning hierarchy, three-second audience challenge, and transition toward predictive versus generative AI.

## Later chapters (not yet implemented)

- Capabilities: predictive and generative AI, NLP, vision, speech, spatial AI.
- Models: foundation models, transformers, LLMs/SLMs, multimodality, reasoning, tokens, context, training and inference.
- Augmentation: prompts, embeddings, vector search, RAG, fine-tuning, tools and MCP.
- Agents: workflows, agentic systems and multi-agent orchestration, ending with AGI as a research goal.

Keep the concepts grouped by what they mean rather than drawing every term as a strict hierarchy. Use an example per concept and short character exchanges, and preserve the original character artwork.

## Review checklist

- Character placement and readable dialogue, especially when viewed on a phone.
- Clear visual examples, timing, transitions and no object overlaps.
- Test the low-quality render before expanding the rest of the scenes.
- Add actual narration and synchronize beats only after visual approval.

Source prototype only: a complete Manim render has not been executed in the authoring environment.
