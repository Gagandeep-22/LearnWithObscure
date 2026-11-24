"""Zeno Sensei's Brief: Cashfree prepaid AI-agent wallet (24 Nov 2026)."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "cashfree_wallet.json"))

from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, PURPLE, PINK, DARK, WHITE,
)
from manim import *


class ZenoCashfreeWallet(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-24-cashfree-wallet":
            raise ValueError("Expected episodes/cashfree_wallet.json")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = (self.hook, self.wallet, self.limits, self.flow, self.outro)
        if len(episode["segments"]) != len(shots):
            raise ValueError("Expected five segments")
        for index, (segment, shot) in enumerate(zip(episode["segments"], shots)):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(shots) - 1)
            self.background(index)
            shot(segment)
            self.finish_beat()

    def hook(self, segment):
        title = headline("AI CAN PAY\nYOUR BILLS?!", y=5.0, size=80, height=2.1, color=PURPLE)
        zeno = sprite(3.15, -1.45, -0.1, max_width=3.15)
        bill = pill("BILL DUE", color=PINK, ink=DARK).scale(.98).move_to(at(0, 1.65))
        self.phase(.32, FadeIn(title, shift=DOWN * .25), FadeIn(zeno))
        self.phase(.74, GrowFromCenter(bill))
        self.phase(1, Indicate(bill, color=PURPLE), FadeIn(caption(segment["caption"])))

    def wallet(self, segment):
        title = headline("MEET THE\nAI WALLET", y=5.0, size=85, height=2.05, color=PURPLE)
        wallet = pill("PREPAID WALLET", color=PURPLE, ink=WHITE).scale(.92).move_to(at(0, 1.5))
        funds = pill("ADD FUNDS", color=PINK, ink=DARK).scale(.93).move_to(at(0, -.25))
        agent = pill("AUTHORIZE AGENT", color=PURPLE, ink=WHITE).scale(.76).move_to(at(0, -2.05))
        self.phase(.22, FadeIn(title), GrowFromCenter(wallet))
        self.phase(.67, FadeIn(funds, shift=UP * .3), FadeIn(agent, shift=UP * .3))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def limits(self, segment):
        title = headline("YOU SET THE\nSPENDING RULES", y=5.05, size=74, height=2.1, color=PURPLE)
        cards = []
        for i, label in enumerate(("SPENDING LIMITS", "AUTHORIZED ACTIONS", "BANK DETAILS STAY PRIVATE")):
            p = pill(label, color=PURPLE if i != 1 else PINK,
                     ink=WHITE if i != 1 else DARK).scale(.73).move_to(at(0, 2.0 - 1.7 * i))
            cards.append(p)
        self.phase(.2, FadeIn(title), FadeIn(cards[0]))
        self.phase(.72, FadeIn(cards[1], shift=UP * .25), FadeIn(cards[2], shift=UP * .25))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def flow(self, segment):
        title = headline("HOW A BILL\nGETS PAID", y=5.0, size=82, height=2.1, color=PURPLE)
        cards = []
        for i, label in enumerate(("AI AGENT", "PREPAID WALLET", "ELIGIBLE BILL")):
            p = pill(label, color=PURPLE if i != 1 else PINK,
                     ink=WHITE if i != 1 else DARK).scale(.85).move_to(at(0, 2.2 - i * 2.0))
            cards.append(p)
        self.phase(.2, FadeIn(title), FadeIn(cards[0]))
        self.phase(.68, FadeIn(cards[1]), FadeIn(cards[2]))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def outro(self, segment):
        title = headline("WOULD YOU\nTRUST AI?", y=5.05, size=87, height=2.0, color=PURPLE)
        zeno = sprite(3.1, -1.45, -.05, max_width=3.15)
        choice = pill("YES OR NO?", color=PINK, ink=DARK).scale(.9).move_to(at(0, 1.65))
        follow = text("FOLLOW LEARN WITH OBSCURE", size=36, width=6.4,
                      height=.8, color=PURPLE).move_to(at(0, -3.65))
        self.phase(.3, FadeIn(title), FadeIn(zeno))
        self.phase(.73, GrowFromCenter(choice))
        self.phase(1, FadeIn(follow), FadeIn(caption(segment["caption"])))
