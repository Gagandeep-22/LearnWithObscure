from pathlib import Path
from tempfile import TemporaryDirectory

from manim_voiceover.services.gemini import GeminiService


VOICES = ("Achird", "Leda")
MODEL = "gemini-3.1-flash-tts-preview"
TEST_TEXT = "This is a short Gemini voice readiness check."


def main():
    with TemporaryDirectory() as cache_dir:
        for voice in VOICES:
            service = GeminiService(voice=voice, model=MODEL)
            result = service.generate_from_text(TEST_TEXT, cache_dir=cache_dir)
            audio_path = Path(cache_dir) / result["original_audio"]
            if not audio_path.is_file() or audio_path.stat().st_size == 0:
                raise RuntimeError(f"Gemini did not return valid audio for {voice}.")
            print(f"{voice}: ready ({audio_path.stat().st_size} bytes of test audio)")


if __name__ == "__main__":
    main()