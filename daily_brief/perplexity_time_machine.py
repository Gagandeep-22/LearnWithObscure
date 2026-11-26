"""Zeno Sensei's Brief: Perplexity Time Machine (27 Nov 2026).
Official source: https://www.perplexity.ai/hub/blog/freeze-the-web-with-perplexity-time-machine
Optional credited original screenshot: daily_brief/assets/perplexity_time_machine_official.png
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "perplexity_time_machine.json"))

from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, PURPLE, PINK, DARK, WHITE,
)
from manim import *


class ZenoPerplexityTimeMachine(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-27-perplexity-time-machine":
            raise ValueError("Expected episodes/perplexity_time_machine.json")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = (self.hook, self.what, self.cutoff, self.example, self.outro)
        if len(episode["segments"]) != len(shots):
            raise ValueError("Expected five segments")
        for index, (segment, shot) in enumerate(zip(episode["segments"], shots)):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(shots) - 1)
            self.background(index)
            shot(segment)
            self.finish_beat()

    def hook(self, segment):
        title = headline("AI CAN TIME\nTRAVEL?!", y=5, size=79, height=2.1, color=PURPLE)
        zeno = sprite(3.12, -1.45, -.1, max_width=3.15)
        chip = pill("PERPLEXITY TIME MACHINE", color=PINK, ink=DARK).scale(.65).move_to(at(0, 1.7))
        self.phase(.3, FadeIn(title, shift=DOWN*.25), FadeIn(zeno))
        self.phase(.7, GrowFromCenter(chip))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def what(self, segment):
        title = headline("SEARCH THE\nPAST WEB", y=5, size=84, height=2.05, color=PURPLE)
        old = pill("PAST WEB SNAPSHOT", color=PURPLE, ink=WHITE).scale(.76).move_to(at(0, 1.6))
        today = pill("TODAY'S WEB", color=PINK, ink=DARK).scale(.85).move_to(at(0, -.3))
        result = pill("HISTORICAL RESULTS", color=PURPLE, ink=WHITE).scale(.77).move_to(at(0, -2.15))
        self.phase(.22, FadeIn(title), FadeIn(old))
        self.phase(.65, FadeIn(today, shift=UP*.2), FadeIn(result, shift=UP*.2))
        self.phase(1, Indicate(old, color=PINK), FadeIn(caption(segment["caption"])))

    def cutoff(self, segment):
        title = headline("CHOOSE A\nCUTOFF DATE", y=5, size=79, height=2.1, color=PURPLE)
        stamp = pill("snapshot_as_of", color=PURPLE, ink=WHITE).scale(.95).move_to(at(0, 1.35))
        date = pill("2026-10-20", color=PINK, ink=DARK).scale(.95).move_to(at(0, -.45))
        history = pill("OLDER SAVED PAGES", color=PURPLE, ink=WHITE).scale(.77).move_to(at(0, -2.1))
        self.phase(.25, FadeIn(title), GrowFromCenter(stamp))
        self.phase(.7, FadeIn(date), FadeIn(history))
        self.phase(1, Indicate(date, color=PURPLE), FadeIn(caption(segment["caption"])))

    def example(self, segment):
        title = headline("NO FUTURE\nSPOILERS!", y=5, size=82, height=2.1, color=PURPLE)
        question = pill("PREDICT AN EVENT", color=PURPLE, ink=WHITE).scale(.8).move_to(at(0, 1.75))
        cutoff = pill("PAST NEWS ONLY", color=PINK, ink=DARK).scale(.84).move_to(at(0, -.25))
        fair = pill("FAIRER AI TEST", color=PURPLE, ink=WHITE).scale(.86).move_to(at(0, -2.2))
        self.phase(.23, FadeIn(title), GrowFromCenter(question))
        self.phase(.68, FadeIn(cutoff, shift=UP*.2), FadeIn(fair, shift=UP*.2))
        self.phase(1, Indicate(fair, color=PINK), FadeIn(caption(segment["caption"])))

    def outro(self, segment):
        title = headline("WOULD YOU\nTRY IT?", y=5, size=86, height=2.0, color=PURPLE)
        zeno = sprite(3.12, -1.45, -.05, max_width=3.15)
        period = pill("UP TO 365 DAYS BACK", color=PINK, ink=DARK).scale(.75).move_to(at(0, 1.7))
        follow = text("FOLLOW LEARN WITH OBSCURE", size=36, width=6.4,
                      height=.8, color=PURPLE).move_to(at(0, -3.65))
        self.phase(.3, FadeIn(title), FadeIn(zeno))
        self.phase(.72, GrowFromCenter(period))
        self.phase(1, FadeIn(follow), FadeIn(caption(segment["caption"])))
