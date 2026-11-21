"""Remove the long silent gap in the already-generated intro-02 WAV, offline.

No API or TTS calls. Reads the v5 paused recording and writes the v6 cache file
that the Manim scene will use. Leaves the source recording untouched.
"""
import argparse
import hashlib
import math
import os
import struct
import wave
from pathlib import Path

from learnwithobscure.scenes.ai_universe_audio import AUDIO_DIR, MODEL, VOICES, clip_path

LINE = "Zeno Sensei!"
WHO = "student"
OLD_VERSION = "zeno-paused-v5"


def old_path():
    cache_key = f"{MODEL}:{VOICES[WHO]}:{LINE}:{OLD_VERSION}"
    digest = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()[:20]
    return AUDIO_DIR / f"{digest}.wav"


def process(source: Path, destination: Path, keep_ms: int = 45):
    with wave.open(str(source), "rb") as reader:
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        rate = reader.getframerate()
        frames = reader.getnframes()
        raw = reader.readframes(frames)
        compression = reader.getcomptype()
    if sample_width != 2 or channels not in (1, 2) or compression != "NONE":
        raise ValueError("This editor supports only 16-bit mono/stereo PCM WAV files.")
    if frames < rate // 2:
        raise ValueError("Recording is too short to safely detect a word gap.")
    n = len(raw) // 2
    samples = struct.unpack(f"<{n}h", raw)
    window = max(1, round(rate * .01))
    levels = []
    for start in range(0, frames, window):
        stop = min(frames, start + window)
        total = 0
        count = 0
        for i in range(start, stop):
            for ch in range(channels):
                value = samples[i * channels + ch]
                total += value * value
                count += 1
        levels.append(math.sqrt(total / count) / 32768 if count else 0)
    peak = max(levels)
    threshold = max(0.003, peak * .025)
    # Ignore leading and trailing silence; only investigate an internal gap.
    lo = round(len(levels) * .20)
    hi = round(len(levels) * .80)
    candidates = []
    start = None
    for i in range(lo, hi + 1):
        silent = i < hi and levels[i] < threshold
        if silent and start is None:
            start = i
        if not silent and start is not None:
            candidates.append((start, i))
            start = None
    if not candidates:
        raise RuntimeError("No internal silence detected; source unchanged.")
    a, b = max(candidates, key=lambda item: item[1] - item[0])
    gap_ms = (b - a) * 1000 * window / rate
    if gap_ms < 125:
        raise RuntimeError(f"No long pause detected (longest: {gap_ms:.0f} ms). Source unchanged.")
    trim_ms = max(0, gap_ms - keep_ms)
    # Leave half the allowed silence on either side of the join to avoid
    # cutting into the audible syllables.
    left = max(0, round((a * window + (keep_ms / 2) * rate / 1000)))
    right = min(frames, round(b * window - (keep_ms / 2) * rate / 1000))
    if right <= left:
        raise RuntimeError("No safe section to trim.")
    frame_bytes = channels * sample_width
    edited = raw[:left * frame_bytes] + raw[right * frame_bytes:]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(sample_width)
        writer.setframerate(rate)
        writer.writeframes(edited)
    print(f"Source: {source}")
    print(f"Original pause: approximately {gap_ms:.0f} ms")
    print(f"Trimmed: approximately {trim_ms:.0f} ms")
    print(f"Edited clip: {destination}")
    print("No Gemini call made. Listen and ensure both words remain intact.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-ms", type=int, default=45,
                        help="Silence to retain between words, in milliseconds")
    args = parser.parse_args()
    if not 20 <= args.keep_ms <= 100:
        parser.error("--keep-ms must be between 20 and 100")
    source = old_path()
    if not source.exists():
        parser.error(f"Previous paused recording not found: {source}")
    process(source, clip_path(LINE, WHO), args.keep_ms)
