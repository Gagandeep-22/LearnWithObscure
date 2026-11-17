"""Shared episode data and narration-cache validation.

This module requires no Manim or Gemini dependencies. Both preparation and
rendering use it so changing speech, voice or model invalidates stale clips.
"""
import hashlib
import json
import math
import os
import re
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = "gemini-3.1-flash-tts-preview"
DEFAULT_VOICE = "Leda"


def load_episode():
    path = Path(os.getenv("ZENO_EPISODE", str(ROOT / "episode.json")))
    episode = json.loads(path.read_text(encoding="utf-8"))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", episode["id"]):
        raise ValueError("Episode id must be a simple directory name.")
    if not isinstance(episode["date"], str) or not episode["date"].strip():
        raise ValueError("Episode date cannot be empty.")
    if not isinstance(episode["segments"], list) or not episode["segments"]:
        raise ValueError("Episode must contain at least one segment.")
    for index, segment in enumerate(episode["segments"]):
        for key in ("visual", "title", "caption", "speech"):
            if not isinstance(segment.get(key), str) or not segment[key].strip():
                raise ValueError(f"Segment {index}: {key} must be nonempty text.")
        seconds = float(segment["seconds"])
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError(f"Segment {index}: seconds must be positive and finite.")
    return episode


def voice_settings():
    return (
        os.getenv("ZENO_TTS_MODEL", DEFAULT_MODEL),
        os.getenv("ZENO_TTS_VOICE", DEFAULT_VOICE),
    )


def clip_path(episode, index):
    return ROOT / "audio" / episode["id"] / f"{index:02d}.wav"


def cache_key(segment, model, voice):
    # Preserve the v1 key format to reuse valid audio already generated.
    return hashlib.sha256(
        f'{model}:{voice}:{segment["speech"]}'.encode("utf-8")
    ).hexdigest()


def clip_duration(path):
    with wave.open(str(path), "rb") as wav:
        if wav.getnframes() <= 0 or wav.getframerate() <= 0:
            raise ValueError(f"Empty WAV: {path}")
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != 24000:
            raise ValueError(f"Unexpected Gemini PCM format: {path}")
        if len(wav.readframes(wav.getnframes())) != wav.getnframes() * 2:
            raise ValueError(f"Truncated WAV: {path}")
        return wav.getnframes() / wav.getframerate()


def valid_clip(episode, index, model, voice):
    path = clip_path(episode, index)
    try:
        if path.with_suffix(".sha256").read_text(encoding="utf-8").strip() != cache_key(
            episode["segments"][index], model, voice
        ):
            return None
        return clip_duration(path)
    except (OSError, EOFError, wave.Error, ValueError):
        return None


def narration_plan(episode, model, voice):
    """Preflight the whole episode before starting an expensive render."""
    plan = []
    missing = []
    for index in range(len(episode["segments"])):
        duration = valid_clip(episode, index, model, voice)
        path = clip_path(episode, index)
        if duration is None:
            missing.append(path.name)
        else:
            plan.append((path, duration))
    if missing:
        raise RuntimeError(
            "Missing, stale or invalid Zeno narration: " + ", ".join(missing)
            + ". Run uv run --env-file .env python daily_brief/prepare_audio.py "
              "and repeat until all clips are ready; or set ZENO_SILENT=1 "
              "for a silent preview."
        )
    return plan
