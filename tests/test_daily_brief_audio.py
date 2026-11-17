"""Offline regression tests for the Zeno narration pipeline."""
import importlib.util
import json
import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "episode_support",
    Path(__file__).resolve().parents[1] / "daily_brief" / "episode_support.py",
)
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


class NarrationCacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        mock = patch.object(support, "ROOT", self.root)
        mock.start()
        self.addCleanup(mock.stop)
        self.ep = {
            "id": "test", "date": "TEST",
            "segments": [
                {"visual": "hook", "title": "Hook", "caption": "Caption",
                 "speech": "Hello, Code Crew!", "seconds": 3},
                {"visual": "outro", "title": "Outro", "caption": "Bye",
                 "speech": "Stay curious!", "seconds": 2},
            ],
        }
        self.model, self.voice = "test-model", "Leda"

    def write_clip(self, index):
        path = support.clip_path(self.ep, index)
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(24000)
            f.writeframes(b"\x00\x00"*24000)
        path.with_suffix(".sha256").write_text(
            support.cache_key(self.ep["segments"][index], self.model, self.voice),
            encoding="utf-8",
        )
        return path

    def test_valid_cache_and_duration(self):
        path = self.write_clip(0)
        self.assertEqual(support.valid_clip(self.ep, 0, self.model, self.voice), 1)
        self.ep["segments"][0]["caption"] = "Revised visual caption"
        self.assertEqual(support.valid_clip(self.ep, 0, self.model, self.voice), 1)
        self.ep["segments"][0]["speech"] = "New narration"
        self.assertIsNone(support.valid_clip(self.ep, 0, self.model, self.voice))

    def test_voice_change(self):
        self.write_clip(0)
        self.assertIsNone(support.valid_clip(self.ep, 0, self.model, "Other"))

    def test_missing_and_corrupt_audio(self):
        self.write_clip(0)
        with self.assertRaisesRegex(RuntimeError, "01.wav"):
            support.narration_plan(self.ep, self.model, self.voice)
        path = self.write_clip(1)
        path.write_bytes(b"broken")
        self.assertIsNone(support.valid_clip(self.ep, 1, self.model, self.voice))

    def test_full_plan(self):
        paths = [self.write_clip(i) for i in range(2)]
        self.assertEqual(support.narration_plan(self.ep, self.model, self.voice),
                         [(paths[0], 1), (paths[1], 1)])

    def test_invalid_episode_id(self):
        self.ep["id"] = "../outside"
        path = self.root / "episode.json"
        path.write_text(json.dumps(self.ep), encoding="utf-8")
        with patch.dict(os.environ, {"ZENO_EPISODE": str(path)}):
            with self.assertRaises(ValueError):
                support.load_episode()


if __name__ == "__main__":
    unittest.main()
