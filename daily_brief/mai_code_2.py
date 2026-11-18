"""Independent motion-graphics episode for Zeno's Brief: MAI Code 2."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "mai_code_2.json"))
from daily_brief import (
    ZenoDailyBrief, SILENT, load_episode, narration_plan, voice_settings,
    at, text, headline, caption, pill, sprite, burst, BG, DARK, PURPLE,
    LAVENDER, PINK, WHITE,
)
from manim import *


class ZenoMAICode2(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-19-mai-code-2":
            raise ValueError("Select episodes/mai_code_2.json for this scene.")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = {"hook": self.opening, "reveal": self.reveal_models,
                 "complex": self.complex_fix, "flash": self.quick_fix,
                 "picker": self.copilot_picker, "choice": self.model_choice,
                 "outro": self.subscribe_outro}
        for index, segment in enumerate(episode["segments"]):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(episode["segments"])-1)
            self.background(index)
            shots[segment["visual"]](segment, episode)
            self.finish_beat()

    def opening(self, segment, episode):
        title = headline("AI CODING\nBATTLE", y=4.65, size=105, height=2.4, color=PURPLE)
        zeno = sprite(4.1, 0, -.2)
        a = pill("OPENAI", color=DARK).scale(.72).move_to(at(-1.85, 2.35))
        b = pill("ANTHROPIC", color=DARK).scale(.72).move_to(at(1.85, 2.35))
        c = pill("MICROSOFT", color=PINK, ink=DARK).move_to(at(0, -3.1))
        rays = burst(zeno.get_center(), 2.3)
        self.add(a, b)
        self.phase(.33, GrowFromCenter(title), FadeIn(zeno, scale=.8))
        self.phase(.70, GrowFromCenter(c), FadeIn(rays, scale=.7))
        self.phase(1, Indicate(c, color=PURPLE), FadeIn(caption(segment["caption"])))

    def reveal_models(self, segment, episode):
        title = headline("TWO NEW\nCODING MODELS", y=4.9, size=80, height=2.1, color=PURPLE)
        a = pill("MAI CODE 2").scale(1.2).move_to(at(0, 1.9))
        b = pill("MAI CODE 2 FLASH", color=PINK, ink=DARK).move_to(at(0, .4))
        zeno = sprite(2.7, 0, -2.2)
        date = pill("17 NOV 2026", color=DARK).scale(.75).move_to(at(0, 3.25))
        self.phase(.25, FadeIn(title), FadeIn(date))
        self.phase(.55, FadeIn(a, shift=RIGHT))
        self.phase(.82, FadeIn(b, shift=LEFT), FadeIn(zeno, shift=UP*.4))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def file_icon(self, label, x, y):
        card = RoundedRectangle(width=2.65, height=1.55, corner_radius=.15,
                                color=PURPLE, fill_color=WHITE, fill_opacity=1)
        name = text(label, size=30, width=2.35, height=.45).move_to(UP*.42)
        lines = VGroup(*[Line(LEFT*.85+UP*h, RIGHT*.85+UP*h,
                              color=LAVENDER, stroke_width=4) for h in (.04,-.22,-.48)])
        return VGroup(card, name, lines).move_to(at(x,y))

    def complex_fix(self, segment, episode):
        title = headline("MAI CODE 2", y=5, size=94, height=1.25, color=PURPLE)
        files = [self.file_icon("Service.java", -1.65, 2.15),
                 self.file_icon("Repo.java", 1.65, 2.15),
                 self.file_icon("Tests.java", 0, -.1)]
        arrows = VGroup(*[Arrow(f.get_bottom(), files[2].get_top(), buff=.12,
                                color=PURPLE, stroke_width=4) for f in files[:2]])
        bug = pill("BUG FOUND", color=PINK, ink=DARK).move_to(at(0, -1.65))
        fixed = pill("FIX + TEST").move_to(bug)
        zeno = sprite(1.65, 0, -3.2)
        self.phase(.25, FadeIn(title), LaggedStart(*[FadeIn(f, shift=UP*.3) for f in files], lag_ratio=.2))
        self.phase(.53, Create(arrows), GrowFromCenter(bug))
        self.phase(.79, ReplacementTransform(bug, fixed),
                   *[Indicate(f, color=PURPLE, scale_factor=1.03) for f in files])
        self.phase(1, FadeIn(zeno), FadeIn(caption(segment["caption"])))

    def quick_fix(self, segment, episode):
        title = headline("CODE 2 FLASH", y=5, size=88, height=1.3, color=PURPLE)
        code = self.file_icon("Quick edit", 0, 1.8).scale(1.55)
        a = pill("EXPLAIN").scale(.8).move_to(at(0, -.05))
        b = pill("EDIT").scale(.8).move_to(at(0, -1.1))
        c = pill("QUICK FIX", color=PINK, ink=DARK).move_to(at(0, -2.2))
        zeno = sprite(1.6, -2.35, -3.35)
        self.phase(.28, FadeIn(title), FadeIn(code, shift=UP*.4))
        self.phase(.55, FadeIn(a, shift=RIGHT), FadeIn(b, shift=LEFT))
        self.phase(.79, GrowFromCenter(c), Flash(c.get_center(), color=PINK, flash_radius=1.7))
        self.phase(1, FadeIn(zeno), FadeIn(caption(segment["caption"])))

    def copilot_picker(self, segment, episode):
        title = headline("GITHUB COPILOT", y=5, size=69, height=1.3, color=PURPLE)
        panel = RoundedRectangle(width=6.1, height=4.3, corner_radius=.2,
                                 color=PURPLE, fill_color=WHITE, fill_opacity=1).move_to(at(0, 1.0))
        label = text("SELECT A MODEL", size=35).move_to(at(0, 2.5))
        a = pill("MAI CODE 2").move_to(at(0, 1.3))
        b = pill("MAI CODE 2 FLASH", color=PINK, ink=DARK).move_to(at(0, .15))
        free = pill("FLASH: FREE PLAN*", color=DARK).scale(.8).move_to(at(0, -2.1))
        zeno = sprite(1.8, 0, -3.45)
        self.phase(.26, FadeIn(title), Create(panel), FadeIn(label))
        self.phase(.58, FadeIn(a, shift=DOWN*.2), FadeIn(b, shift=DOWN*.2))
        self.phase(.80, Indicate(b, color=PURPLE), FadeIn(free))
        self.phase(1, FadeIn(zeno), FadeIn(caption("*Subject to plan and usage limits.")))

    def model_choice(self, segment, episode):
        title = headline("CHOOSE THE RIGHT\nMODEL FOR THE JOB", y=4.8,
                         size=73, height=2.1, color=PURPLE)
        heavy = pill("COMPLEX TASKS").move_to(at(0, 2.0))
        light = pill("ROUTINE TASKS", color=PINK, ink=DARK).move_to(at(0, -.1))
        a = text("CODE 2", size=45).move_to(at(0, 1.0))
        b = text("CODE 2 FLASH", size=45).move_to(at(0, -1.1))
        zeno = sprite(2.2, 0, -3.0)
        self.phase(.26, FadeIn(title), FadeIn(heavy))
        self.phase(.58, GrowFromCenter(a), FadeIn(light))
        self.phase(.82, GrowFromCenter(b), FadeIn(zeno))
        self.phase(1, FadeIn(caption(segment["caption"])))

    def subscribe_outro(self, segment, episode):
        title = headline("DAILY TECH\nNEWS", y=4.85, size=90, height=2.1, color=PURPLE)
        zeno = sprite(4, 0, .55)
        halo = Circle(radius=2.2, color=PINK, stroke_width=5).move_to(zeno)
        zeno.set_z_index(2)
        subscribe = pill("SUBSCRIBE", color=PINK, ink=DARK).scale(1.22).move_to(at(0, -2.4))
        brand = headline("LEARN WITH OBSCURE", y=-3.5, size=42, height=.8)
        signoff = headline("STAY CURIOUS, CODE CREW!", y=-4.8, size=32, height=.65, color=PURPLE)
        self.phase(.25, FadeIn(title), Create(halo), FadeIn(zeno, scale=.8))
        self.phase(.60, GrowFromCenter(subscribe), FadeIn(brand))
        self.phase(1, Indicate(subscribe, color=PURPLE), FadeIn(signoff),
                   zeno.animate.shift(UP*.1))
