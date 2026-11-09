"""Generate missing Binary Search narration clips without rendering animations.

Run from the repository root:
    uv run python scripts/prepare_binary_search_audio.py
    uv run python scripts/prepare_binary_search_audio.py --max-new 5
"""
import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from learnwithobscure.scenes.binary_search_complete import (  # noqa: E402
    AudioPreparationLimitReached,
    BinarySearchDemo,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-new",
        type=int,
        default=8,
        help="Maximum new Gemini TTS requests in this run (default: 8).",
    )
    args = parser.parse_args()
    if args.max_new < 1:
        parser.error("--max-new must be at least 1")

    if not os.getenv("GEMINI_API_KEY"):
        print(
            "GEMINI_API_KEY is not set. Add it to your local environment/.env "
            "before generating missing clips.",
            file=sys.stderr,
        )
        return 2

    os.environ["LWO_AUDIO_PREPARE_ONLY"] = "1"
    os.environ["LWO_AUDIO_PREPARE_MAX_NEW"] = str(args.max_new)

    scene = BinarySearchDemo()
    try:
        scene.construct()
    except AudioPreparationLimitReached as exc:
        print(f"\n{exc}")
    finally:
        os.environ.pop("LWO_AUDIO_PREPARE_ONLY", None)
        os.environ.pop("LWO_AUDIO_PREPARE_MAX_NEW", None)

    print(
        f"\nAudio preparation pass finished. Newly generated clips: "
        f"{scene.audio_prepare_generated}. Existing cached clips were reused."
    )
    print(
        "Run this command again to continue if clips remain. "
        "No Manim video was rendered."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
