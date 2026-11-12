"""Generate missing Bubble Sort narration clips without rendering animation.

Run from the repository root:
    uv run --env-file .env python scripts/prepare_bubble_sort_audio.py
    uv run --env-file .env python scripts/prepare_bubble_sort_audio.py --max-new 5
"""
import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from learnwithobscure.scenes.bubble_sort import (  # noqa: E402
    AudioPreparationLimitReached,
    BubbleSortDemo,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-new",
        type=int,
        default=8,
        help="Maximum new Gemini TTS requests in this run (default: 8).",
    )
    parser.add_argument(
        "--min-request-interval",
        type=float,
        default=22.0,
        help="Minimum seconds between new Gemini TTS requests (default: 22).",
    )
    args = parser.parse_args()
    if args.max_new < 1:
        parser.error("--max-new must be at least 1")
    if args.min_request_interval < 20:
        parser.error("--min-request-interval must be at least 20 seconds")
    if not os.getenv("GEMINI_API_KEY"):
        print(
            "GEMINI_API_KEY is not set. Add it to the root .env or local environment.",
            file=sys.stderr,
        )
        return 2

    os.environ["LWO_AUDIO_PREPARE_ONLY"] = "1"
    os.environ["LWO_AUDIO_PREPARE_MAX_NEW"] = str(args.max_new)
    os.environ["LWO_AUDIO_PREPARE_MIN_INTERVAL"] = str(args.min_request_interval)

    scene = BubbleSortDemo()
    try:
        scene.construct()
    except AudioPreparationLimitReached as exc:
        print(f"\n{exc}")
    except Exception as exc:
        print(
            f"\nAudio preparation stopped: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        print("Successfully generated clips remain cached; rerun later to continue.")
        return 1
    finally:
        for key in (
            "LWO_AUDIO_PREPARE_ONLY",
            "LWO_AUDIO_PREPARE_MAX_NEW",
            "LWO_AUDIO_PREPARE_MIN_INTERVAL",
        ):
            os.environ.pop(key, None)

    print(
        f"\nAudio preparation pass finished. Newly generated clips: "
        f"{scene.audio_prepare_generated}. Existing cached clips were reused."
    )
    print("No video was rendered. Rerun the command if clips remain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
