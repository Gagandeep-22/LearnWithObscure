"""Cached AI Universe narration and a no-render preparation CLI."""
import ast
import base64
import json
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import hashlib
import os
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIO_DIR = ROOT / "media" / "audio_files" / "ai_universe"
MODEL = os.getenv("LWO_GEMINI_TTS_MODEL", "gemini-3.8-flash-lite-tts")
VOICES = {"student": "Achird", "robot": "Leda"}

def clip_path(line, who):
    revision = "anime-call-v2" if who == "student" and line == "Zeno Sensei!" else ""
    key = hashlib.sha256(f"{MODEL}:{VOICES[who]}:{line}:{revision}".encode("utf-8")).hexdigest()[:20]
    return AUDIO_DIR / f"{key}.wav"

def duration(path):
    with wave.open(str(path), "rb") as f:
        frames = f.getnframes()
        rate = f.getframerate()
        if not frames or not rate:
            raise ValueError(f"Empty audio: {path}")
        if len(f.readframes(frames)) != frames * f.getnchannels() * f.getsampwidth():
            raise ValueError(f"Incomplete audio: {path}")
        return frames / rate

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
    
def extract_audio(response):
    """Read the first complete candidate containing audio, not text."""
    candidates = response.get("candidates") or []
    if not isinstance(candidates, list):
        raise RuntimeError("Gemini returned a malformed candidate list.")
    reasons = [c.get("finishReason", "unspecified") for c in candidates]
    for candidate in candidates:
        if candidate.get("finishReason") not in ("STOP", None):
            continue
        blobs = [p.get("inlineData") or p.get("inline_data") or {}
                 for p in (candidate.get("content") or {}).get("parts", [])]
        audio = [(b.get("mimeType") or b.get("mime_type") or "", b["data"])
                 for b in blobs if b.get("data") and
                 (b.get("mimeType") or b.get("mime_type") or "").lower().startswith("audio/")]
        if len(audio) == 1:
            mime, data = audio[0]
            return mime, base64.b64decode(data, validate=True)
        if len(audio) > 1:
            raise RuntimeError("Unexpected multiple audio parts; refusing to join blindly.")
    feedback = (response.get("promptFeedback") or {}).get("blockReason", "none")
    raise RuntimeError(f"Gemini returned no complete audio (candidates={len(candidates)}, "
                       f"finish reasons={reasons}, prompt block={feedback}). "
                       "Stop and investigate before spending more quota.")


def save_audio(path, mime, data):
    """Support both complete WAV and legacy 16-bit PCM responses."""
    if not data:
        raise ValueError("Gemini returned an empty audio payload.")
    temporary = path.with_suffix(".tmp.wav")
    try:
        if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
            temporary.write_bytes(data)
        elif mime.lower().startswith(("audio/l16", "audio/pcm")):
            rate_match = re.search(r"rate=(\d+)", mime, re.I)
            rate = int(rate_match.group(1)) if rate_match else 24000
            channels_match = re.search(r"channels=(\d+)", mime, re.I)
            channels = int(channels_match.group(1)) if channels_match else 1
            if rate <= 0 or channels <= 0 or len(data) % (2 * channels):
                raise ValueError("Invalid PCM audio parameters or byte count.")
            with wave.open(str(temporary), "wb") as f:
                f.setnchannels(channels)
                f.setsampwidth(2)
                f.setframerate(rate)
                f.writeframes(data)
        else:
            raise ValueError(f"Unsupported audio MIME type: {mime}")
        duration(temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def request_audio(line, who, path, key=None):
    """Call the Gemini Developer API directly; no Manim/SoX/SDK required."""
    if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+", MODEL):
        raise ValueError("Invalid LWO_GEMINI_TTS_MODEL.")
    if key == "intro-02":
        # Only the introductory call needs character-specific direction.
        # Never include this direction in the on-screen dialogue.
        transcript = (
            "Voice acting direction: Obscure is an overwhelmed, confused anime "
            "student surrounded by baffling AI, ML and RAG terms. He suddenly "
            "calls out to his mentor for help in a playful, slightly panicked "
            "anime-style cry. Say 'Zeno' fairly quickly and naturally; put the "
            "big emotional emphasis on 'SEN' in 'Sensei', and gently sustain "
            "the final 'ei' vowel like 'Senseiii!' for a pleading finish. "
            "The call should be expressive but never angry or robotic. "
            "Speak ONLY these words, with no direction spoken aloud: "
            "Zeno Senseiii!"
        )
    else:
        transcript = line if not MODEL.endswith("-preview") else "Read aloud exactly: " + line
    body = {
        "contents": [{"parts": [{"text": transcript}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {
                "voiceName": VOICES[who]}}},
        },
    }
    request = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        method="POST",
    )
    try:
        with urlopen(request, timeout=180) as result:
            response = json.load(result)
    except HTTPError as exc:
        try:
            status = json.loads(exc.read()).get("error", {}).get("status", "")
        except (ValueError, OSError):
            status = ""
        raise RuntimeError(f"Gemini HTTP {exc.code} {status}; model={MODEL}") from None
    mime, data = extract_audio(response)
    save_audio(path, mime, data)


def prepare(max_new=8, interval=22, check=False, only_id=None):
    lines = list(dialogue())
    if only_id is not None:
        lines = [item for item in lines if item[0] == only_id]
        if not lines:
            raise ValueError(f"Unknown dialogue ID: {only_id}")
    missing = {clip_path(line, who): (key, who, line) for key, who, line in lines
               if not ready(clip_path(line, who))}
    print(f"Model: {MODEL}; voices: {VOICES}")
    print(f"{len(lines)} dialogue beats; {len(missing)} unique clips missing.")
    if check or not missing:
        return 0 if not missing else 1
    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
    else:
        load_dotenv(ROOT / ".env")
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Set GEMINI_API_KEY locally in .env.")
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    last = None
    generated = 0
    for path, (key, who, line) in list(missing.items())[:max_new]:
        if last is not None:
            time.sleep(max(0, interval - (time.monotonic() - last)))
        # Never treat an unfinished WAV as a cache hit.
        if path.exists():
            path.unlink()
        print(f"Requesting {key} ({VOICES[who]})...", flush=True)
        last = time.monotonic()
        try:
            request_audio(line, who, path, key=key)
            duration(path)
        except Exception:
            if path.exists() and not ready(path):
                path.unlink()
            raise
        generated += 1
        print(f"Generated {key}: {duration(path):.2f}s ({generated}/{max_new})", flush=True)
    print(f"New clips: {generated}. Remaining: {len(missing)-generated}.")
    return 0
