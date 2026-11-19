"""Zeno's Brief episode 3: Anthropic IPO. Offline render with cached narration."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("ZENO_EPISODE", str(ROOT / "episodes" / "anthropic_ipo.json"))
from daily_brief import (ZenoDailyBrief, SILENT, load_episode, narration_plan,
    voice_settings, at, text, headline, caption, pill, sprite, burst,
    BG, DARK, PURPLE, LAVENDER, PINK, WHITE)
from manim import *

class ZenoAnthropicIPO(ZenoDailyBrief):
    def construct(self):
        episode = load_episode()
        if episode["id"] != "2026-11-20-anthropic-ipo":
            raise ValueError("Select episodes/anthropic_ipo.json for this scene.")
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        for i, segment in enumerate(episode["segments"]):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[i]
            self.start_beat(duration + .30, wav, i == len(episode["segments"])-1)
            self.background(i)
            getattr(self, "shot_" + segment["visual"])(segment)
            self.finish_beat()

    def shot_hook(self, s):
        top = headline("CLAUDE'S CREATOR", y=5.15, size=61, height=.9)
        title = headline("MAKES\nHISTORY!", y=3.3, size=105, height=2.4, color=PURPLE)
        zeno = sprite(3.9,0,-.15)
        ring = Circle(radius=2.05,color=PINK,stroke_width=6).move_to(zeno)
        rays = burst(zeno.get_center(),2.25)
        zeno.set_z_index(2)
        self.add(top)
        self.phase(.35,GrowFromCenter(title),FadeIn(zeno,scale=.75),Create(ring))
        self.phase(.72,FadeIn(rays,scale=.7),zeno.animate.shift(UP*.12))
        self.phase(1,FadeIn(caption(s["caption"])),ring.animate.scale(1.08))

    def shot_record(self,s):
        title = headline("ANTHROPIC IPO",y=5.1,size=75,height=1.1,color=PURPLE)
        value = ValueTracker(0)
        number = DecimalNumber(0,num_decimal_places=1,font_size=120,color=PURPLE)
        number.add_updater(lambda m: m.set_value(value.get_value()).move_to(at(0,1.65)))
        dollar = headline("$",y=3.25,size=84,height=1.0,color=PURPLE)
        unit = headline("BILLION",y=.15,size=83,height=1.2)
        record = pill("WORLD RECORD",color=PINK,ink=DARK).move_to(at(0,-1.6))
        z = sprite(1.8,0,-3.15)
        self.phase(.20,FadeIn(title),FadeIn(dollar))
        self.add(number)
        self.phase(.64,value.animate.set_value(81.3),FadeIn(unit))
        number.clear_updaters()
        self.phase(.83,GrowFromCenter(record),FadeIn(z))
        self.phase(1,FadeIn(caption(s["caption"])))

    def shot_explain(self,s):
        title = headline("WHAT IS\nAN IPO?",y=4.8,size=96,height=2.1,color=PURPLE)
        building = VGroup(Rectangle(width=2.3,height=2.4,color=PURPLE,fill_color=LAVENDER,fill_opacity=1),
            *[Square(side_length=.35,color=WHITE,fill_opacity=1).move_to([x,y,0])
              for x in (-.65,0,.65) for y in (-.55,.05,.65)]).move_to(at(0,1.55))
        private = pill("PRIVATE COMPANY").move_to(at(0,-.05))
        public = pill("PUBLIC SHARES",color=PINK,ink=DARK).move_to(at(0,-.05))
        shares = VGroup(*[VGroup(RoundedRectangle(width=1.5,height=.85,corner_radius=.12,
            color=PURPLE,fill_color=WHITE,fill_opacity=1),text("SHARE",size=28,width=1.2,height=.4))
            .move_to(at(x,-2.25)) for x in (-1.8,0,1.8)])
        links = VGroup(*[Arrow(at(0,-.55),m.get_top(),buff=.12,color=PURPLE,stroke_width=4) for m in shares])
        self.phase(.26,FadeIn(title),GrowFromCenter(building),FadeIn(private))
        self.phase(.55,ReplacementTransform(private,public))
        self.phase(.84,Create(links),LaggedStart(*[FadeIn(m,shift=DOWN*.3) for m in shares],lag_ratio=.15))
        self.phase(1,FadeIn(caption(s["caption"])))

    def shot_ticker(self,s):
        title = headline("NASDAQ DEBUT",y=5.2,size=72,height=1.1,color=PURPLE)
        date = pill("19 NOV 2026",color=DARK).move_to(at(0,3.7))
        ticker = headline("ANT",y=1.8,size=156,height=2.0,color=PURPLE)
        price = headline("$83",y=-.25,size=128,height=1.65)
        label = headline("IPO PRICE PER SHARE",y=-1.75,size=38,height=.6,color=PURPLE)
        z = sprite(2.0,0,-3.1)
        self.phase(.24,FadeIn(title),FadeIn(date))
        self.phase(.52,GrowFromCenter(ticker))
        self.phase(.78,GrowFromCenter(price),FadeIn(label))
        self.phase(1,FadeIn(z),FadeIn(caption(s["caption"])))

    def shot_compute(self,s):
        title = headline("WHY DOES\nIT MATTER?",y=4.85,size=81,height=2.1,color=PURPLE)
        servers = VGroup(*[VGroup(RoundedRectangle(width=1.45,height=2.35,corner_radius=.13,
            color=PURPLE,fill_color=DARK,fill_opacity=1),*[Line([- .48,y,0],[.48,y,0],
            color=LAVENDER,stroke_width=4) for y in (-.7,-.2,.3,.8)],
            Dot([.48,-.95,0],radius=.07,color=PINK)).move_to(at(x,.95)) for x in (-1.85,0,1.85)])
        label = pill("COMPUTE + RESEARCH").move_to(at(0,-.85))
        z = sprite(2.4,0,-2.85)
        self.phase(.24,FadeIn(title))
        self.phase(.56,LaggedStart(*[FadeIn(m,shift=UP*.45) for m in servers],lag_ratio=.2))
        self.phase(.82,GrowFromCenter(label),FadeIn(z))
        self.phase(1,FadeIn(caption(s["caption"])),Indicate(servers,color=PINK,scale_factor=1.03))

    def shot_caveat(self,s):
        money = headline("MORE MONEY",y=4.2,size=88,height=1.25,color=PURPLE)
        neq = headline("≠",y=2.05,size=145,height=1.5,color=DARK)
        better = headline("BETTER AI",y=.25,size=100,height=1.45,color=PURPLE)
        z = sprite(2.5,0,-2.35)
        self.phase(.28,GrowFromCenter(money))
        self.phase(.58,GrowFromCenter(neq),FadeIn(better,shift=UP*.25))
        self.phase(1,FadeIn(z),FadeIn(caption(s["caption"])))

    def shot_outro(self,s):
        title = headline("DAILY TECH\nNEWS",y=4.85,size=90,height=2.1,color=PURPLE)
        z = sprite(4,0,.55)
        halo = Circle(radius=2.2,color=PINK,stroke_width=5).move_to(z)
        z.set_z_index(2)
        sub = pill("SUBSCRIBE",color=PINK,ink=DARK).scale(1.22).move_to(at(0,-2.4))
        brand = headline("LEARN WITH OBSCURE",y=-3.5,size=42,height=.8)
        signoff = headline("STAY CURIOUS, CODE CREW!",y=-4.8,size=32,height=.65,color=PURPLE)
        self.phase(.25,FadeIn(title),Create(halo),FadeIn(z,scale=.8))
        self.phase(.60,GrowFromCenter(sub),FadeIn(brand))
        self.phase(1,Indicate(sub,color=PURPLE),FadeIn(signoff),z.animate.shift(UP*.1))
