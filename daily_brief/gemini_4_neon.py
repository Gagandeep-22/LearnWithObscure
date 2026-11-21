"""Gemini 4 Neon Zeno Brief with actual official news imagery.

The official Google assets must be downloaded locally first using
daily_brief/download_neon_images.py. No substitute stock images or invented
product screenshots are used.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "gemini_4_neon.json"))

from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, burst, PURPLE, PINK, DARK, WHITE,
)
from manim import *

IMAGE_DIR = ROOT / "assets" / "neon"


def official_images():
    manifest = IMAGE_DIR / "sources.json"
    if not manifest.is_file():
        raise RuntimeError(
            "Official Google photos are missing. Run: "
            "uv run python daily_brief/download_neon_images.py"
        )
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not data.get("images"):
        raise RuntimeError("No images recorded in the Google sources manifest.")
    images = []
    for entry in data["images"]:
        location = IMAGE_DIR / Path(entry["file"]).name
        if not location.is_file():
            raise FileNotFoundError(f"Missing official image: {location}")
        images.append(location)
    return images


def photo(path, height=5.1, width=6.5, x=0, y=.35):
    image = ImageMobject(str(path))
    image.scale_to_fit_width(width)
    if image.height > height:
        image.scale_to_fit_height(height)
    return image.move_to(at(x, y))


class ZenoGemini4Neon(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-21-gemini-4-neon":
            raise ValueError("Expected episodes/gemini_4_neon.json")
        pictures = official_images()
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = (self.opening, self.announcement, self.workflow,
                 self.evidence, self.subscribe)
        for index, (segment, shot) in enumerate(zip(episode["segments"], shots)):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(shots) - 1)
            self.background(index)
            shot(segment, pictures)
            self.finish_beat()

    def picture_frame(self, path, y=.55, height=5):
        img = photo(path, height=height, width=6.5, y=y)
        frame = RoundedRectangle(
            width=img.width + .20, height=img.height + .20,
            corner_radius=.16, color=PURPLE, stroke_width=3,
            fill_color=WHITE, fill_opacity=1,
        ).move_to(img)
        credit = text("IMAGE: GOOGLE", size=22, height=.42,
                      width=4.2, color=DARK).next_to(frame, DOWN, buff=.12)
        return frame, img, credit

    def opening(self, segment, pictures):
        title = headline("GEMINI 4\nNEON!", y=5.2, size=102,
                         height=2, color=PURPLE)
        frame, img, credit = self.picture_frame(pictures[0], y=.55, height=5.4)
        zeno = sprite(2.1, 2.15, -3.25, max_width=2.1)
        label = pill("GOOGLE'S NEW AI MODEL", color=PINK, ink=DARK)
        label.scale(.76).move_to(at(-.65, -3.25))
        self.phase(.30, FadeIn(title, shift=DOWN*.45), FadeIn(img, scale=.83),
                   FadeIn(frame))
        self.phase(.70, FadeIn(zeno, shift=UP*.35), GrowFromCenter(label),
                   FadeIn(credit))
        self.phase(1, FadeIn(caption(segment["caption"])),
                   img.animate.scale(1.03))

    def announcement(self, segment, pictures):
        heading = headline("MORE THAN\nCODE SUGGESTIONS", y=5,
                           size=75, height=2, color=PURPLE)
        frame, img, credit = self.picture_frame(pictures[0], y=1.0, height=4.55)
        steps = pill("SOFTWARE ENGINEERING", color=PURPLE)
        steps.scale(.82).move_to(at(0, -2.55))
        self.phase(.26, FadeIn(heading, shift=RIGHT*.4))
        self.phase(.66, FadeIn(frame), FadeIn(img, shift=UP*.4), FadeIn(credit))
        self.phase(1, GrowFromCenter(steps), FadeIn(caption(segment["caption"])))

    def workflow(self, segment, pictures):
        heading = headline("AGENTIC\nCODING", y=5, size=91,
                           height=2.1, color=PURPLE)
        stages = [pill(label, color=PINK if i == 3 else PURPLE,
                       ink=DARK if i == 3 else WHITE).scale(.94)
                  for i, label in enumerate(("PLAN", "CODE", "TEST", "ITERATE"))]
        for i, item in enumerate(stages):
            item.move_to(at(0, 2.7-i*1.35))
        arrows = [Arrow(stages[i].get_bottom(), stages[i+1].get_top(),
                        buff=.10, color=PURPLE, stroke_width=4)
                  for i in range(3)]
        zeno = sprite(2.2, 2.25, -3.2, max_width=2.1)
        self.phase(.25, FadeIn(heading), FadeIn(stages[0], shift=RIGHT))
        self.phase(.61, LaggedStart(*[FadeIn(s, shift=LEFT*.25)
                                     for s in stages[1:]], lag_ratio=.22),
                   LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=.2))
        self.phase(1, FadeIn(zeno), FadeIn(caption(segment["caption"])))

    def evidence(self, segment, pictures):
        heading = headline("SEE THE\nREAL DEMOS", y=5, size=88,
                           height=2, color=PURPLE)
        selected = pictures[1] if len(pictures) > 1 else pictures[0]
        frame, img, credit = self.picture_frame(selected, y=.6, height=5.3)
        label = pill("GOOGLE ANNOUNCEMENT").scale(.75).move_to(at(0, -3.35))
        self.phase(.27, GrowFromCenter(heading))
        self.phase(.72, FadeIn(frame), FadeIn(img, scale=.82),
                   FadeIn(credit), GrowFromCenter(label))
        self.phase(1, FadeIn(caption(segment["caption"])),
                   img.animate.scale(1.02))

    def subscribe(self, segment, pictures):
        title = headline("SMARTER AI.\nSMARTER DEVELOPERS.", y=5,
                         size=72, height=2, color=PURPLE)
        zeno = sprite(4.0, 0, .6)
        rays = burst(zeno.get_center(), 2.4)
        label = pill("SUBSCRIBE", color=PINK, ink=DARK)
        label.scale(1.18).move_to(at(0, -2.55))
        brand = headline("LEARN WITH OBSCURE", y=-3.6,
                         size=42, height=.8)
        self.phase(.25, FadeIn(title), FadeIn(zeno, scale=.75))
        self.phase(.64, FadeIn(rays), GrowFromCenter(label))
        self.phase(1, FadeIn(brand), FadeIn(caption(segment["caption"])),
                   Indicate(label, color=PURPLE))
