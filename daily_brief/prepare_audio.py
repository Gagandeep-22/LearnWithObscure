"""Prepare missing or changed Gemini narration, independently of rendering."""
import argparse
import os
import time
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types
from episode_support import (
    ROOT, load_episode, voice_settings, clip_path, cache_key, valid_clip,
    clip_duration,
)


def main():
    load_dotenv(ROOT.parent / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-new", type=int, default=8)
    parser.add_argument("--interval", type=float, default=22)
    args = parser.parse_args()
    if args.interval < 20 or args.max_new < 1:
        parser.error("Use interval >=20 and max-new >=1")
    episode = load_episode()
    model, voice = voice_settings()
    client = None
    generated = 0
    last = 0
    try:
        for i, segment in enumerate(episode["segments"]):
            wav = clip_path(episode, i)
            if valid_clip(episode, i, model, voice) is not None:
                print("Cached:", wav.name)
                continue
            if generated >= args.max_new:
                break
            if client is None:
                key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if not key:
                    raise RuntimeError("Set GEMINI_API_KEY in the root .env.")
                client = genai.Client(api_key=key)
            wav.parent.mkdir(parents=True, exist_ok=True)
            time.sleep(max(0, args.interval-(time.monotonic()-last)))
            last = time.monotonic()
            response = client.models.generate_content(
                model=model, contents=segment["speech"],
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        )
                    ),
                ),
            )
            data = next(
                (part.inline_data.data for part in response.candidates[0].content.parts
                 if part.inline_data and part.inline_data.data), None
            )
            if not data or len(data) % 2:
                raise ValueError("Gemini returned empty or invalid PCM audio.")
            temp = wav.with_suffix(".tmp")
            stamp = wav.with_suffix(".sha256")
            try:
                with wave.open(str(temp), "wb") as f:
                    f.setnchannels(1)
                    f.setsampwidth(2)
                    f.setframerate(24000)
                    f.writeframes(data)
                clip_duration(temp)
                temp.replace(wav)
                stamp.write_text(cache_key(segment, model, voice), encoding="utf-8")
            finally:
                temp.unlink(missing_ok=True)
            generated += 1
            print("Generated:", wav.name)
    except Exception as exc:
        print(f"Audio preparation stopped ({type(exc).__name__}).")
        print("Check the API key, model availability, quota and connection. "
              "Completed clips are retained; rerun later.")
        return 1
    durations = [valid_clip(episode, i, model, voice)
                 for i in range(len(episode["segments"]))]
    remaining = sum(d is None for d in durations)
    print(f"New clips: {generated}; remaining: {remaining}.")
    if remaining:
        print("Rerun preparation to finish the remaining clips.")
        return 2
    print(f"Total narration: {sum(durations):.1f} seconds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
