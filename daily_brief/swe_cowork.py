"""Zeno Sensei's Brief: SWE-CoWork research (24 November 2026).

Source: https://arxiv.org/abs/2611.20218
Research evaluates coding agents in simulated engineering organizations; the
under-8% figure is full task completion by the two leading models on this benchmark.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "swe_cowork.json"))

from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, PURPLE, PINK, DARK, WHITE,
)
from manim import *


class ZenoSweCoWork(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-24-swe-cowork":
            raise ValueError("Expected episodes/swe_cowork.json")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = (self.hook, self.study, self.result, self.contrast, self.outro)
        for index, (segment, shot) in enumerate(zip(episode["segments"], shots)):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(shots) - 1)
            self.background(index)
            shot(segment)
            self.finish_beat()

    def hook(self, segment):
        title = headline("AI CAN CODE...\nCAN IT DELIVER?", y=5.05, size=79,
                         height=2.1, color=PURPLE)
        robot = sprite(3.2, -1.45, -0.05, max_width=3.1)
        code = pill("CODE: DONE!", color=PURPLE, ink=WHITE).scale(.93)
        code.move_to(at(0, 1.55))
        question = pill("PROJECT: ???", color=PINK, ink=DARK).scale(.93)
        question.move_to(at(0, -2.65))
        self.phase(.28, FadeIn(title, shift=DOWN*.3), FadeIn(robot))
        self.phase(.70, GrowFromCenter(code), GrowFromCenter(question))
        self.phase(1, Indicate(question, color=PURPLE),
                   FadeIn(caption(segment["caption"])))

    def study(self, segment):
        title = headline("101 REAL\nCODE REPOSITORIES", y=5.1, size=81,
                         height=2.1, color=PURPLE)
        cards = []
        for i, label in enumerate(("REAL CODEBASES", "SIMULATED TEAM", "11 AI MODELS")):
            card = pill(label, color=PURPLE if i != 1 else PINK,
                        ink=WHITE if i != 1 else DARK).scale(.88)
            card.move_to(at(0, 2.25 - 1.75 * i))
            cards.append(card)
        zeno = sprite(1.8, 2.25, -2.95, max_width=1.8)
        self.phase(.25, FadeIn(title), FadeIn(cards[0], shift=UP*.3))
        self.phase(.75, FadeIn(cards[1], shift=UP*.25),
                   FadeIn(cards[2], shift=UP*.25), FadeIn(zeno))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def result(self, segment):
        title = headline("FULL TASK\nCOMPLETION", y=5.3, size=81,
                         height=1.85, color=PURPLE)
        number = text("< 8%", size=160, width=6.3, height=3.0,
                      color=PURPLE).move_to(at(0, .75))
        label = pill("TOP TWO MODELS", color=PINK, ink=DARK).scale(.92)
        label.move_to(at(0, -2.05))
        qualifier = text("SWE-CoWork benchmark", size=35, width=6.0,
                         height=.6, color=DARK).move_to(at(0, -3.12))
        self.phase(.30, FadeIn(title), GrowFromCenter(number))
        self.phase(.76, Indicate(number, color=PINK), FadeIn(label))
        self.phase(1, FadeIn(qualifier), FadeIn(caption(segment["caption"])))

    def contrast(self, segment):
        title = headline("WRITING CODE ≠\nFINISHING THE JOB", y=5.1,
                         size=72, height=2.15, color=PURPLE)
        labels = ("WRITE CODE", "FIND REQUIREMENTS", "WORK WITH TEAM", "PASS ALL TESTS")
        cards = []
        for i, name in enumerate(labels):
            card = pill(name, color=PURPLE if i == 0 else PINK,
                        ink=WHITE if i == 0 else DARK).scale(.77)
            card.move_to(at(0, 2.1 - i * 1.4))
            cards.append(card)
        self.phase(.22, FadeIn(title), FadeIn(cards[0]))
        self.phase(.74, LaggedStart(*[FadeIn(c, shift=UP*.2) for c in cards[1:]],
                                    lag_ratio=.20))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def outro(self, segment):
        title = headline("AI: REPLACEMENT\nOR TEAMMATE?", y=5.1, size=81,
                         height=2.05, color=PURPLE)
        zeno = sprite(3.2, -1.5, .0, max_width=3.25)
        debate = pill("YOUR TAKE?", color=PINK, ink=DARK).scale(.92)
        debate.move_to(at(0, 1.8))
        follow = text("FOLLOW LEARN WITH OBSCURE", size=37, width=6.5,
                      height=.8, color=PURPLE).move_to(at(0, -3.65))
        self.phase(.30, FadeIn(title), FadeIn(zeno))
        self.phase(.73, GrowFromCenter(debate), Indicate(debate, color=PURPLE))
        self.phase(1, FadeIn(follow), FadeIn(caption(segment["caption"])))
