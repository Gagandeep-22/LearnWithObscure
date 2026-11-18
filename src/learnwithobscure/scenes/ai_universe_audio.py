"""Cached AI Universe narration and a no-render preparation CLI."""
import ast
import hashlib
import os
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIO_DIR = ROOT / "media" / "audio_files" / "ai_universe"
MODEL = "gemini-3.1-flash-tts-preview"
VOICES = {"student": "Achird", "robot": "Leda"}

def clip_path(line, who):
    key = hashlib.sha256(f"{MODEL}:{VOICES[who]}:{line}".encode("utf-8")).hexdigest()[:20]
    return AUDIO_DIR / f"{key}.wav"

def duration(path):
    with wave.open(str(path), "rb") as f:
        if not f.getnframes() or not f.getframerate():
            raise ValueError(f"Empty audio: {path}")
        return f.getnframes() / f.getframerate()

def ready(path):
    try:
        duration(path)
        return True
    except (OSError, EOFError, wave.Error, ValueError):
        return False

def dialogue():
    ids = set()
    for name in ("ai_universe.py", "ai_capabilities.py", "ai_universe_full.py"):
        tree = ast.parse((Path(__file__).parent / name).read_text(encoding="utf-8"))
        calls = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Attribute)
                        and isinstance(n.func.value, ast.Name)
                        and n.func.value.id == "self" and n.func.attr == "say"),
                       key=lambda n: n.lineno)
        for node in calls:
            key, who, line = (ast.literal_eval(a) for a in node.args[:3])
            if key in ids:
                raise ValueError(f"Duplicate dialogue: {key}")
            ids.add(key)
            yield key, who, line

def preflight():
    missing = [key for key, who, line in dialogue() if not ready(clip_path(line, who))]
    if missing:
        raise RuntimeError(f"{len(missing)} narration clips missing or invalid. "
                           "Run uv run python scripts/prepare_ai_universe_audio.py first. "
                           "Use LWO_DISABLE_VOICEOVER=1 for silent preview.")
    
def prepare(max_new=8, interval=22, check=False):
    lines = list(dialogue())
    missing = {clip_path(line, who): (key, who, line) for key, who, line in lines
               if not ready(clip_path(line, who))}
    print(f"{len(lines)} dialogue beats; {len(missing)} unique clips missing.")
    if check or not missing:
        return 0 if not missing else 1
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Set GEMINI_API_KEY locally in .env.")
    from manim_voiceover.services.gemini import GeminiService
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    services = {}
    last = None
    generated = 0
    for path, (key, who, line) in list(missing.items())[:max_new]:
        if last is not None:
            time.sleep(max(0, interval - (time.monotonic() - last)))
        if who not in services:
            services[who] = GeminiService(voice=VOICES[who], model=MODEL)
        # Never treat an unfinished WAV as a cache hit.
        if path.exists():
            path.unlink()
        last = time.monotonic()
        try:
            result = services[who].generate_from_text(line, cache_dir=AUDIO_DIR, path=path.name)
            actual = AUDIO_DIR / result["original_audio"]
            if actual != path:
                actual.replace(path)
            duration(path)
        except Exception:
            if path.exists() and not ready(path):
                path.unlink()
            raise
        generated += 1
        print(f"Generated {key}: {duration(path):.2f}s ({generated}/{max_new})", flush=True)
    print(f"New clips: {generated}. Remaining: {len(missing)-generated}.")
    return 0
