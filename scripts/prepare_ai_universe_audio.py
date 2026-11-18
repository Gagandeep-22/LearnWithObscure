"""Prepare narration without rendering; rerun to reuse cached clips."""
import argparse
from learnwithobscure.scenes.ai_universe_audio import prepare

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-new", type=int, default=8)
    parser.add_argument("--min-request-interval", type=float, default=22)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.max_new < 1 or args.min_request_interval < 20:
        parser.error("Use max-new >= 1 and interval >= 20 seconds.")
    try:
        raise SystemExit(prepare(args.max_new, args.min_request_interval, args.check))
    except Exception as exc:
        print(f"Preparation stopped: {type(exc).__name__}: {exc}")
        print("Completed clips remain cached. Rerun later to continue.")
        raise SystemExit(1)
