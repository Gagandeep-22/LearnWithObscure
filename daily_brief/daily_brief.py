"""Motion-graphics edition of the narrated 9:16 Zeno Sensei tech brief.

Each shot has its own composition and timed reveal beats. No permanent deck,
header, footer, or content cards. Rendering remains offline with cached audio.
"""
import math
import os
import sys
import textwrap
from pathlib import Path

import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from episode_support import load_episode, narration_plan, voice_settings

BG = "#E6D9F2"
DARK = "#352044"
PURPLE = "#7B3FA1"
LAVENDER = "#A987C5"
PINK = "#FF75AC"
WHITE = "#FFFFFF"

PREVIEW = os.getenv("ZENO_PREVIEW") == "1"
SILENT = os.getenv("ZENO_SILENT") == "1" or (
    PREVIEW and os.getenv("ZENO_AUDIO") != "1"
)
config.pixel_width, config.pixel_height = (540, 960) if PREVIEW else (1080, 1920)
config.frame_width, config.frame_height = 9, 16
config.frame_rate = 30
config.background_color = BG

# Reserve the right rail and bottom edge for Shorts overlays.
X = -.48


def at(x, y):
    return np.array([X+x, y, 0.0])


def text(value, size=62, width=6.45, height=2.3, color=DARK,
         bold=True, wrap=None):
    if wrap:
        value = "\n".join(textwrap.fill(line, width=wrap) for line in value.splitlines())
    obj = Text(value, font_size=size, color=color,
               weight="BOLD" if bold else "NORMAL", line_spacing=.95)
    if obj.width > width:
        obj.scale_to_fit_width(width)
    if obj.height > height:
        obj.scale_to_fit_height(height)
    return obj


def headline(value, y=4.95, **kwargs):
    return text(value, **kwargs).move_to(at(0, y))


def caption(value):
    # Short editorial captions, not a transcript. Keep them in the safe area.
    return text(value, size=33, width=6.0, height=1.08, bold=False,
                wrap=35).move_to(at(0, -4.82))


def pill(value, color=PURPLE, ink=WHITE):
    label = text(value, size=35, width=5.8, height=.6, color=ink)
    shape = RoundedRectangle(width=label.width+.62, height=label.height+.37,
                             corner_radius=.22, stroke_width=0,
                             fill_color=color, fill_opacity=1)
    return VGroup(shape, label.move_to(shape))


def sprite(height, x, y, max_width=5.6):
    zeno = ImageMobject(str(ROOT / "assets" / "zeno.png"))
    zeno.scale_to_fit_height(height)
    if zeno.width > max_width:
        zeno.scale_to_fit_width(max_width)
    return zeno.move_to(at(x, y))


def burst(center, radius=2.0, color=PINK, count=12):
    rays = []
    for i in range(count):
        theta = TAU*i/count
        direction = np.array([math.cos(theta), math.sin(theta), 0])
        rays.append(Line(center+direction*radius,
                         center+direction*(radius+.38),
                         color=color, stroke_width=5))
    return VGroup(*rays)


def projected(u, v, z=0):
    """Simple isometric projection, no OpenGL or external assets."""
    return np.array([(u-v)*.77, (u+v)*.38+z*.92, 0])


def face(points, color, opacity=1):
    return Polygon(*[projected(*p) for p in points], color=PURPLE,
                   stroke_width=2, fill_color=color, fill_opacity=opacity)


def block(u, v, w, d, h, top=PINK):
    a, b = u+w, v+d
    return VGroup(
        face([(u,v,0),(a,v,0),(a,v,h),(u,v,h)], LAVENDER),
        face([(a,v,0),(a,b,0),(a,b,h),(a,v,h)], PURPLE),
        face([(u,v,h),(a,v,h),(a,b,h),(u,b,h)], top),
    )


def world(include_walls=True):
    floor = face([(0,0,0),(4,0,0),(4,4,0),(0,4,0)], WHITE)
    grid = VGroup(*[
        Line(projected(i,0), projected(i,4), color=LAVENDER, stroke_width=1.4)
        for i in (1,2,3)
    ], *[
        Line(projected(0,i), projected(4,i), color=LAVENDER, stroke_width=1.4)
        for i in (1,2,3)
    ])
    walls = VGroup()
    if include_walls:
        walls.add(
            face([(0,4,0),(4,4,0),(4,4,2),(0,4,2)], LAVENDER, .42),
            face([(0,0,0),(0,4,0),(0,4,2),(0,0,2)], BG, .75),
        )
    furniture = VGroup(block(.75,2.8,.9,.7,.9),
                       block(2.2,2.0,1.0,.85,.55, WHITE),
                       block(2.7,.7,.55,.55,.8))
    # Far walls first, then floor and furniture, to keep depth legible.
    return VGroup(walls, floor, grid, furniture)


class ZenoDailyBrief(Scene):
    def construct(self):
        episode = load_episode()
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        shots = {
            "hook": self.hook, "deal": self.deal, "cube": self.spatial,
            "room": self.room, "scientist": self.scientist,
            "stack": self.stack, "outro": self.outro,
        }
        for index, segment in enumerate(episode["segments"]):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.start_beat(duration, wav, index == len(episode["segments"])-1)
            self.background(index)
            # The seven bespoke illustrations are specific to this story.
            # Do not show an AMD deal for an unrelated future episode.
            shot = shots.get(segment["visual"], self.generic) if (
                episode["id"] == "2026-11-17-amd-world-labs"
            ) else self.generic
            shot(segment, episode)
            self.finish_beat()

    def background(self, index):
        # Large abstract shapes bleed beyond the edge; the content stays central.
        self.camera.background_color = BG if index % 2 == 0 else WHITE
        halo = Circle(radius=3.55, stroke_width=0,
                      fill_color=WHITE if index % 2 == 0 else BG,
                      fill_opacity=.8).move_to([2.75, 2.8, 0])
        arcs = VGroup(
            Circle(radius=3.45, color=LAVENDER, stroke_width=3,
                   stroke_opacity=.35).move_to([-4.5,-2.6,0]),
            Circle(radius=3.05, color=PINK, stroke_width=4,
                   stroke_opacity=.35).move_to([4.45,6.2,0]),
        )
        dots = VGroup(*[
            Dot([3.55+.28*(i%2), 1.8+.32*(i//2),0],
                radius=.045, color=LAVENDER) for i in range(10)
        ])
        self.add(halo, arcs, dots)
        self.decor = halo

    def start_beat(self, duration, wav, last):
        self.last = last
        self.beat_start = self.time
        self.frames = max(15, math.ceil(duration*config.frame_rate))
        self.exit_frames = min(9, max(2, self.frames//12))
        self.usable_frames = self.frames-self.exit_frames
        self.used_frames = 0
        self.phase_count = 0
        if wav is not None:
            self.add_sound(str(wav))

    def phase(self, end, *animations):
        """Play to a cumulative fraction of the clip's usable duration.

        Fractions approximate the spoken beats, not word-level alignment.
        Frames are budgeted cumulatively so short clips and transitions do not
        cause overlapping narration, and long clips are not cut off.
        """
        target = round(self.usable_frames*end)
        frames = max(1, target-self.used_frames)
        frames = min(frames, self.usable_frames-self.used_frames)
        if frames <= 0:
            return
        self.used_frames += frames
        self.phase_count += 1
        seconds = frames/config.frame_rate
        if animations:
            # Preserve punchy motion rather than stretching an entrance for
            # several seconds. Use remaining time to drift the ambient shape.
            motion = min(seconds, 1.55)
            self.play(*animations, run_time=motion)
            hold = seconds-motion
            if hold >= 1/config.frame_rate:
                self.play(self.decor.animate.shift(
                    (LEFT if self.phase_count % 2 else RIGHT)*.12
                ), run_time=hold, rate_func=linear)
            elif hold > 0:
                self.wait(hold)
        else:
            self.wait(seconds)

    def finish_beat(self):
        remaining = self.frames/config.frame_rate-(self.time-self.beat_start)
        seconds = max(1/config.frame_rate, remaining)
        if self.last:
            self.wait(seconds)
        else:
            # Quick graphic wipe across the full canvas. Clear every outgoing
            # object exactly once; the next shot starts with a fresh composition.
            wipe = Rectangle(width=10.0, height=16.4, stroke_width=0,
                             fill_color=PURPLE, fill_opacity=1)
            stripe = Rectangle(width=.42, height=16.4, stroke_width=0,
                               fill_color=PINK, fill_opacity=1)
            stripe.next_to(wipe, RIGHT, buff=0)
            wipe_group = VGroup(wipe, stripe).move_to(LEFT*10)
            self.add(wipe_group)
            self.play(wipe_group.animate.move_to(ORIGIN),
                      run_time=seconds, rate_func=linear)
            self.remove(*list(self.mobjects))

    def swap_caption(self, previous, value):
        new = caption(value)
        return new, ReplacementTransform(previous, new)

    def hook(self, segment, episode):
        brand = headline("ZENO'S DAILY TECH BRIEF", y=6.0, size=27,
                         height=.42, color=PURPLE)
        question = headline("WHAT IF AI COULD", y=4.75, size=58, height=1)
        key = headline("UNDERSTAND\nTHE WORLD?", y=3.1, size=92,
                       height=2.35, color=PURPLE)
        zeno = sprite(4.35, 0, -.75)
        ring = Circle(radius=2.0, color=PINK, stroke_width=7).move_to(zeno)
        rays = burst(zeno.get_center(), 2.32)
        cap = caption(segment["caption"])
        self.phase(.23, FadeIn(brand, shift=DOWN*.15),
                   FadeIn(zeno, shift=UP*.65, scale=.72),
                   Create(ring), FadeIn(question, shift=DOWN*.22))
        self.phase(.58, GrowFromCenter(key),
                   LaggedStart(*[GrowFromCenter(r) for r in rays], lag_ratio=.08))
        self.phase(1, FadeIn(cap, shift=UP*.18),
                   zeno.animate.shift(UP*.12).scale(1.04),
                   ring.animate.scale(1.12), rays.animate.scale(1.08))

    def deal(self, segment, episode):
        # A typographic impact shot. Use names, not approximated company logos.
        amd = text("AMD", size=110, width=5.8, height=1.35,
                   color=PURPLE).move_to(at(0, 4.8))
        labs = text("WORLD LABS", size=87, width=6.4, height=1.25).move_to(at(0, 2.35))
        join = text("+", size=70, height=.9, color=PURPLE).move_to(at(0, 3.53))
        amount = text("$8.2B", size=160, width=6.15, height=2.2,
                      color=PURPLE).move_to(at(0, -.48))
        label = text("ORIGINALLY ANNOUNCED\nSTOCK VALUATION", size=31,
                     height=.86, color=DARK).move_to(at(0, -2.0))
        date = pill(episode["date"], color=DARK).scale(.75).move_to(at(0, 6.0))
        rays = burst(amount.get_center(), 2.45, PINK, 10)
        cap = caption(segment["caption"])
        self.phase(.18, FadeIn(date), FadeIn(amd, shift=RIGHT*1.2),
                   FadeIn(labs, shift=LEFT*1.2))
        self.phase(.38, GrowFromCenter(join),
                   amd.animate.shift(DOWN*.1), labs.animate.shift(UP*.1))
        self.phase(.72, GrowFromCenter(amount), FadeIn(rays, scale=.65),
                   FadeIn(label, shift=UP*.22))
        self.phase(1, Indicate(amount, color=PURPLE, scale_factor=1.06),
                   FadeIn(cap, shift=UP*.1), rays.animate.scale(1.1))

    def spatial(self, segment, episode):
        title = headline("SPATIAL\nINTELLIGENCE", y=4.8, size=85,
                         height=2.05, color=PURPLE)
        flat = Rectangle(width=3.8, height=2.55, color=PURPLE,
                         fill_color=WHITE, fill_opacity=1, stroke_width=3)
        mountains = Polygon([-1.65,-.9,0],[-.65,.72,0],[.1,-.1,0],
                            [.7,.53,0],[1.65,-.9,0], color=PURPLE,
                            fill_color=LAVENDER, fill_opacity=1)
        sun = Dot([1.04,.68,0], radius=.22, color=PINK)
        picture = VGroup(flat, mountains, sun).move_to(at(0,.55))
        label = pill("2D IMAGE").move_to(at(0,-2.0))
        cap = caption("A flat picture is only the beginning.")
        self.phase(.23, FadeIn(title, shift=DOWN*.35),
                   FadeIn(picture, shift=UP*.35, scale=.85),
                   GrowFromCenter(label), FadeIn(cap))
        room = world().scale_to_fit_width(6.15).move_to(at(0,.5))
        new_label = pill("INTERACTIVE 3D SPACE").move_to(at(0,-2.65))
        new_cap, change_cap = self.swap_caption(cap, segment["caption"])
        self.phase(.63, ReplacementTransform(picture, room),
                   ReplacementTransform(label,new_label), change_cap)
        zeno = sprite(1.20,-2.55,-3.65,max_width=1.40)
        spark = burst(at(0,.5), 2.65, PINK, 10)
        # Keep the world in focus; the presenter arrives only after the reveal.
        self.phase(1, FadeIn(zeno, shift=RIGHT*.5),
                   FadeIn(spark, scale=.82),
                   room.animate.shift(UP*.16).scale(1.025))

    def room(self, segment, episode):
        title = headline("TRAIN IN A\nVIRTUAL WORLD", y=4.85,
                         size=76, height=1.95, color=PURPLE)
        small = pill("ILLUSTRATIVE SIMULATION", color=DARK).scale(.78)
        small.move_to(at(0,3.35))
        # An overhead game-like navigation view with a clear obstacle route.
        floor = RoundedRectangle(width=6.05,height=4.55,corner_radius=.29,
                                 color=PURPLE,stroke_width=3,
                                 fill_color=WHITE,fill_opacity=1).move_to(at(0,.15))
        c = floor.get_center()
        grid = VGroup(*[
            Line(c+RIGHT*x+UP*2.1,c+RIGHT*x+DOWN*2.1,
                 color=LAVENDER,stroke_opacity=.40,stroke_width=1.4)
            for x in (-2,-1,0,1,2)
        ], *[
            Line(c+UP*y+LEFT*2.85,c+UP*y+RIGHT*2.85,
                 color=LAVENDER,stroke_opacity=.40,stroke_width=1.4)
            for y in (-1,0,1)
        ])
        obstacles = VGroup(*[
            RoundedRectangle(width=w,height=h,corner_radius=.13,
                             stroke_color=PURPLE,stroke_width=2,
                             fill_color=PINK,fill_opacity=.85).move_to(c+RIGHT*x+UP*y)
            for x,y,w,h in ((-.7,.4,1.2,1.3),(1.15,.65,.95,1.4))
        ])
        start = c+LEFT*2.25+DOWN*1.5
        end = c+RIGHT*2.15+UP*1.5
        points = [start,c+RIGHT*2.15+DOWN*1.5,end]
        path = VMobject(color=PURPLE,stroke_width=6).set_points_as_corners(points)
        target = VGroup(Circle(radius=.33,color=PURPLE,stroke_width=4),
                        Dot(radius=.13,color=PINK)).move_to(end)
        bot = VGroup(
            RoundedRectangle(width=.65,height=.56,corner_radius=.16,
                             stroke_color=PURPLE,stroke_width=3,
                             fill_color=BG,fill_opacity=1),
            Dot(LEFT*.13,radius=.045,color=PURPLE),
            Dot(RIGHT*.13,radius=.045,color=PURPLE),
        ).move_to(start)
        bot.set_z_index(3)
        target.set_z_index(2)
        cap = caption("A robot can practice in a simulated environment.")
        self.phase(.25, FadeIn(title), FadeIn(small),
                   FadeIn(floor,scale=.84), Create(grid),
                   LaggedStart(*[GrowFromCenter(o) for o in obstacles],lag_ratio=.18),
                   FadeIn(bot), FadeIn(target), FadeIn(cap))
        self.phase(.72, Create(path,rate_func=linear),
                   MoveAlongPath(bot,path.copy(),rate_func=linear))
        next_cap, change = self.swap_caption(cap, segment["caption"])
        success = pill("VIRTUAL → REAL").move_to(at(0,-3.22))
        self.phase(1, GrowFromCenter(success), change, Indicate(target,color=PURPLE))

    def scientist(self, segment, episode):
        eyebrow = headline("AI RESEARCH", y=5.65,size=35,height=.6,color=PURPLE)
        name = headline("FEI-FEI LI", y=3.95,size=115,height=1.65,color=DARK)
        slash = Line(at(-2.9,2.85),at(2.9,2.85),color=PINK,stroke_width=12)
        role = headline("CHIEF\nSCIENTIST", y=1.4,size=83,height=2.0,color=PURPLE)
        amd = pill("AT AMD").move_to(at(0,-.35))
        zeno = sprite(2.75,1.7,-2.73,max_width=2.6)
        other = text("EXECUTIVE\nVICE PRESIDENT",size=34,width=3.2,height=1.1,
                     color=DARK).move_to(at(-1.55,-2.55))
        cap = caption(segment["caption"])
        self.phase(.31, FadeIn(eyebrow), FadeIn(name,shift=RIGHT*.65), Create(slash))
        self.phase(.66, GrowFromCenter(role),FadeIn(amd,shift=UP*.25))
        self.phase(1, FadeIn(zeno,shift=LEFT*.55,scale=.85),
                   FadeIn(other,shift=RIGHT*.25),FadeIn(cap))

    def stack(self, segment, episode):
        title = headline("WHAT'S NEXT?",y=5.1,size=85,height=1.3,color=PURPLE)
        # Three isometric layers rise together like an exploded chip diagram.
        layers = []
        for i,(label,shade) in enumerate((("HARDWARE",PURPLE),("SOFTWARE",LAVENDER),
                                           ("AI MODELS",PINK))):
            slab = Polygon([-2.25,0,0],[0,-.82,0],[2.25,0,0],[0,.82,0],
                           color=PURPLE,stroke_width=3,
                           fill_color=shade,fill_opacity=1)
            ink = WHITE if i==0 else DARK
            label_mob = text(label,size=40,width=3.4,height=.6,color=ink)
            layer = VGroup(slab,label_mob.move_to(slab)).move_to(at(0,-.8+i*1.62))
            layers.append(layer)
        flow = VGroup(*[Arrow(at(2.65,-.8+i*1.62),at(2.65,.82+i*1.62),
                                  buff=.25,color=PURPLE,stroke_width=5)
                            for i in range(2)])
        cap = caption("Research could shape future AI infrastructure.")
        self.phase(.25, FadeIn(title,shift=DOWN*.4),
                   GrowFromCenter(layers[0]),FadeIn(cap))
        self.phase(.56, FadeIn(layers[1],shift=UP*.5),
                   FadeIn(layers[2],shift=UP*.6),Create(flow))
        caveat = pill("NOT A PRODUCT LAUNCH",color=PINK,ink=DARK).move_to(at(0,-3.2))
        final_cap, change = self.swap_caption(cap, segment["caption"])
        self.phase(1, GrowFromCenter(caveat), change,
                   LaggedStart(*[Indicate(l,color=PURPLE,scale_factor=1.04)
                                 for l in reversed(layers)],lag_ratio=.32))

    def outro(self, segment, episode):
        title = headline("THE NEXT BIG\nTHING IN AI?",y=5.0,size=73,
                         height=1.9,color=PURPLE)
        zeno = sprite(4.25,0,.3)
        rays = burst(zeno.get_center(),2.45)
        halo = Circle(radius=2.22,color=PURPLE,stroke_width=5).move_to(zeno)
        signoff = headline("STAY CURIOUS,\nCODE CREW!",y=-2.55,size=66,
                           height=1.62)
        subscribe = pill("SUBSCRIBE",color=PINK,ink=DARK).move_to(at(0,-4.25))
        brand = headline("LEARN WITH OBSCURE",y=-5.2,size=28,height=.48,color=PURPLE)
        self.phase(.24, FadeIn(title,shift=DOWN*.32),Create(halo),
                   FadeIn(zeno,scale=.72,shift=UP*.4))
        self.phase(.63, FadeIn(rays,scale=.7),GrowFromCenter(signoff),
                   zeno.animate.shift(UP*.10).scale(1.05))
        self.phase(1, GrowFromCenter(subscribe),FadeIn(brand),
                   halo.animate.scale(1.10),rays.animate.scale(1.07))

    def generic(self, segment, episode):
        title = headline(segment["title"],y=3.9,size=77,height=3.2,
                         color=PURPLE,wrap=20)
        cap = caption(segment["caption"])
        zeno = sprite(4.0,0,-.55)
        rays = burst(zeno.get_center(),2.35)
        self.phase(.32,FadeIn(zeno,scale=.8),GrowFromCenter(title))
        self.phase(.68,FadeIn(rays,scale=.7),FadeIn(cap))
        self.phase(1,zeno.animate.shift(UP*.12),rays.animate.scale(1.1))
