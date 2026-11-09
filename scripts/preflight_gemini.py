"""Check local Gemini TTS configuration without making an API request.

This is intentionally a no-network check: it does not verify the key or consume
Gemini request quota. Use prepare_binary_search_audio.py to generate missing
voice clips.
"""
import os


def main() -> int:
    if os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is present in this environment.")
        print("No API request was made; key validity and voice access were not tested.")
        return 0

    print("GEMINI_API_KEY is not set.")
    print("Set it locally before generating missing narration clips.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
