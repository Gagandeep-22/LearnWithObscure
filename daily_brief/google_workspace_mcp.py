"""Zeno's Brief: Google Workspace MCP servers (28 November 2026).

Independent five-shot vertical episode using the existing narration, animation,
and original Zeno Sensei asset pipeline. Never fetches Google credentials.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "google_workspace_mcp.json"))

from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, PURPLE, PINK, DARK, WHITE,
)
from manim import *


class ZenoGoogleWorkspaceMCP(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-28-google-workspace-mcp":
            raise ValueError("Expected episodes/google_workspace_mcp.json")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = (self.hook, self.reveal, self.connections, self.permissions, self.outro)
        if len(episode["segments"]) != len(shots):
            raise ValueError("Expected five narration segments")
        for index, (segment, shot) in enumerate(zip(episode["segments"], shots)):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(shots) - 1)
            self.background(index)
            shot(segment)
            self.finish_beat()

    def hook(self, segment):
        title = headline("YOUR AI AGENT\\nMEETS WORKSPACE", y=5.0, size=72, height=2.0, color=PURPLE)
        zeno = sprite(3.0, -1.5, -.15, max_width=3.15)
        msg = pill("GMAIL  +  DRIVE  +  CALENDAR", color=PINK, ink=DARK).scale(.65).move_to(at(0, 1.6))
        self.phase(.28, FadeIn(title, shift=DOWN * .25), FadeIn(zeno))
        self.phase(.72, GrowFromCenter(msg))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def reveal(self, segment):
        title = headline("GOOGLE WORKSPACE\\n+ MCP", y=5.1, size=80, height=2.15, color=PURPLE)
        acronym = pill("MODEL CONTEXT PROTOCOL", color=PURPLE, ink=WHITE).scale(.69).move_to(at(0, 1.3))
        agents = text("AI AGENT", size=56, width=5.0, color=DARK).move_to(at(0, -.65))
        self.phase(.3, FadeIn(title), GrowFromCenter(acronym))
        self.phase(.73, FadeIn(agents, shift=UP * .2))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def connections(self, segment):
        title = headline("ONE STANDARD\\nMANY TOOLS", y=5.1, size=77, height=2.0, color=PURPLE)
        hub = pill("AI AGENT", color=PURPLE, ink=WHITE).scale(.95).move_to(at(0, 1.65))
        services = [
            pill(name, color=PINK if i % 2 == 0 else PURPLE,
                 ink=DARK if i % 2 == 0 else WHITE).scale(.78).move_to(at(x, y))
            for i, (name, x, y) in enumerate((
                ("GMAIL", -1.65, -.3), ("DRIVE", 1.65, -.3),
                ("CALENDAR", -1.65, -2.35), ("DOCS", 1.65, -2.35)
            ))
        ]
        self.phase(.22, FadeIn(title), GrowFromCenter(hub))
        self.phase(.74, *[FadeIn(service, shift=UP * .2) for service in services])
        self.phase(1, FadeIn(caption(segment["caption"])))

    def permissions(self, segment):
        title = headline("PERMISSIONS\\nSTILL MATTER", y=5.05, size=82, height=2.0, color=PURPLE)
        allowed = pill("AUTHORIZED ACCESS", color=PURPLE, ink=WHITE).scale(.83).move_to(at(0, 1.4))
        limited = pill("NOT UNLIMITED ACCESS", color=PINK, ink=DARK).scale(.79).move_to(at(0, -.8))
        self.phase(.25, FadeIn(title), GrowFromCenter(allowed))
        self.phase(.75, FadeIn(limited, shift=UP * .2))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def outro(self, segment):
        title = headline("WE'RE BUILDING\\nAN AI AGENT!", y=5.05, size=79, height=2.05, color=PURPLE)
        zeno = sprite(3.05, -1.45, -.1, max_width=3.15)
        badge = pill("ZENO TECH SCOUT", color=PINK, ink=DARK).scale(.82).move_to(at(0, 1.5))
        follow = text("FOLLOW LEARN WITH OBSCURE", size=34, width=6.35,
                      height=.8, color=PURPLE).move_to(at(0, -3.65))
        self.phase(.3, FadeIn(title), FadeIn(zeno))
        self.phase(.75, GrowFromCenter(badge))
        self.phase(1, FadeIn(follow), FadeIn(caption(segment["caption"])))
