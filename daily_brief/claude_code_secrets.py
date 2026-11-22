"""Zeno Sensei's illustrated brief on Claude Code settings secret exposure.

Based on GitGuardian research published November 9, 2026.
All interfaces and keys are illustrative; no genuine credentials are used.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "claude_code_secrets.json"))

from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, burst, PURPLE, PINK, DARK, WHITE,
)
from manim import *


class ZenoClaudeCodeSecrets(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-22-claude-code-secrets":
            raise ValueError("Expected episodes/claude_code_secrets.json")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = (self.opening, self.numbers, self.valid, self.mechanism, self.protect)
        for index, (segment, shot) in enumerate(zip(episode["segments"], shots)):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(shots)-1)
            self.background(index)
            shot(segment)
            self.finish_beat()

    def opening(self, segment):
        title = headline("YOUR AI HELPER\nLEAKED A KEY?!", y=5.10, size=80,
                         height=2.15, color=PURPLE)
        zeno = sprite(3.55, -1.6, .4, max_width=3.3)
        key = text("API_KEY = [REDACTED]", size=45, width=5.6,
                   height=.75, color=WHITE)
        terminal = RoundedRectangle(width=6.4, height=2.0, corner_radius=.25,
                                    color=PURPLE, fill_color=DARK, fill_opacity=1)
        terminal.move_to(at(0, -1.35))
        key.move_to(terminal)
        warning = pill("EXPOSED?", color=PINK, ink=DARK)
        warning.scale(.8).move_to(at(1.7, 1.9))
        self.phase(.30, FadeIn(title, shift=DOWN*.3), FadeIn(zeno))
        self.phase(.69, FadeIn(terminal), Write(key), GrowFromCenter(warning))
        self.phase(1, FadeIn(caption(segment["caption"])), Indicate(warning, color=PURPLE))

    def numbers(self, segment):
        title = headline("31,088\nDISTINCT SECRETS", y=4.95, size=90,
                         height=2.1, color=PURPLE)
        repository = RoundedRectangle(width=6.2, height=4, corner_radius=.3,
                                      color=PURPLE, fill_color=WHITE, fill_opacity=1)
        repository.move_to(at(0,.15))
        bars = VGroup(*[
            RoundedRectangle(width=4.6, height=.48, corner_radius=.1,
                             color=PURPLE, fill_color=PURPLE if i == 2 else PINK,
                             fill_opacity=.7).move_to(at(0,1.25-i*1.05))
            for i in range(3)
        ])
        labels = VGroup(*[
            text(value, size=30, width=4.4, height=.43, color=DARK)
            .move_to(at(0,1.25-i*1.05))
            for i, value in enumerate(("PUBLIC GITHUB", "CLAUDE SETTINGS", "CREDENTIALS FOUND"))
        ])
        foot = text("GITGUARDIAN RESEARCH", size=33, width=5.8,
                    height=.6).move_to(at(0,-2.85))
        self.phase(.28, FadeIn(title), Create(repository))
        self.phase(.73, LaggedStart(*[FadeIn(bar, shift=RIGHT*.25) for bar in bars],
                                    lag_ratio=.17),
                   LaggedStart(*[FadeIn(label) for label in labels], lag_ratio=.17))
        self.phase(1, FadeIn(foot), FadeIn(caption(segment["caption"])))

    def valid(self, segment):
        title = headline("5,343\nVALID AT DETECTION", y=5.0, size=82,
                         height=2.1, color=PURPLE)
        shield = Circle(radius=2.15, color=PURPLE, stroke_width=10,
                        fill_color=WHITE, fill_opacity=.95).move_to(at(0,.25))
        mark = text("!", size=150, width=2, height=3, color=PINK).move_to(shield)
        zeno = sprite(2.0, 2.15, -2.6, max_width=2.0)
        qualifier = pill("NOT A LIVE KEY COUNT", color=PINK, ink=DARK)
        qualifier.scale(.78).move_to(at(0,-2.85))
        self.phase(.30, FadeIn(title), GrowFromCenter(shield))
        self.phase(.67, Write(mark), FadeIn(zeno))
        self.phase(1, GrowFromCenter(qualifier), FadeIn(caption(segment["caption"])))

    def mechanism(self, segment):
        title = headline("HOW CAN IT\nLEAK?", y=5.1, size=92,
                         height=1.9, color=PURPLE)
        names = ("APPROVE COMMAND", "SAVE SETTINGS", "COMMIT TO GITHUB", "SECRET EXPOSED")
        cards = [pill(name, color=PINK if i == 3 else PURPLE,
                      ink=DARK if i == 3 else WHITE).scale(.80)
                 for i, name in enumerate(names)]
        for i, card in enumerate(cards):
            card.move_to(at(0, 2.65-i*1.37))
        arrows = [Arrow(cards[i].get_bottom(), cards[i+1].get_top(),
                        color=PURPLE, stroke_width=4, buff=.09) for i in range(3)]
        note = text("ILLUSTRATION — NO REAL KEYS", size=24, width=6.3,
                    height=.5, color=DARK).move_to(at(0,-3.55))
        self.phase(.23, FadeIn(title), FadeIn(cards[0]))
        self.phase(.77, LaggedStart(*[FadeIn(c, shift=UP*.15) for c in cards[1:]],
                                    lag_ratio=.18),
                   LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=.18))
        self.phase(1, FadeIn(note), FadeIn(caption(segment["caption"])))

    def protect(self, segment):
        title = headline("KEEP YOUR\nSECRETS SAFE", y=5.05, size=84,
                         height=2, color=PURPLE)
        actions = ["DON'T COMMIT KEYS", "SCAN YOUR REPO", "ROTATE EXPOSED KEYS"]
        pills = [pill(action, color=PURPLE if i != 2 else PINK,
                      ink=WHITE if i != 2 else DARK).scale(.83)
                 for i, action in enumerate(actions)]
        for i, action in enumerate(pills):
            action.move_to(at(0,2.4-i*1.35))
        zeno = sprite(2.65, 0, -2.1, max_width=2.8)
        subscribe = text("FOLLOW LEARN WITH OBSCURE", size=39,
                         width=6.5, height=.8, color=PURPLE).move_to(at(0,-3.65))
        self.phase(.24, FadeIn(title), FadeIn(pills[0]))
        self.phase(.68, FadeIn(pills[1], shift=UP*.25),
                   FadeIn(pills[2], shift=UP*.25), FadeIn(zeno))
        self.phase(1, FadeIn(subscribe), FadeIn(caption(segment["caption"])),
                   Indicate(pills[2], color=PURPLE))
