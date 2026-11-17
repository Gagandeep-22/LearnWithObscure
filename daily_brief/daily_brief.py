"""Bright, narration-led 9:16 Zeno Sensei Shorts template."""
import math
import os
import sys
import textwrap
from pathlib import Path

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


def words(value, size=42, width=6.5, height=1.4, color=DARK,
          bold=False, wrap=30):
    text = Text(
        "\n".join(textwrap.fill(line, width=wrap) for line in value.splitlines()),
        font_size=size, color=color,
        weight="BOLD" if bold else "NORMAL", line_spacing=1.05,
    )
    if text.width > width:
        text.scale_to_fit_width(width)
    if text.height > height:
        text.scale_to_fit_height(height)
    return text


def panel(width, height, color=WHITE, stroke=LAVENDER):
    return RoundedRectangle(
        width=width, height=height, corner_radius=.24,
        stroke_color=stroke, stroke_width=2,
        fill_color=color, fill_opacity=1,
    )


def tile(label, width=5.5, height=.85, color=WHITE, accent=PURPLE):
    rect = panel(width, height, color, accent)
    label = words(label, 33, width-.35, height-.22, bold=True)
    return VGroup(rect, label.move_to(rect))


class ZenoDailyBrief(Scene):
    # Content stays within x=-3.95..2.85 and y=-5.15..6.7:
    # reserve the right rail and lower edge for Shorts UI.
    X = -.48

    def construct(self):
        episode = load_episode()
        clips = None if SILENT else narration_plan(episode, *voice_settings())
        self.camera.background_color = BG
        self.add(*self.chrome(episode))
        zeno = ImageMobject(str(ROOT / "assets" / "zeno.png"))
        zeno.scale_to_fit_height(2.55)
        if zeno.width > 2.0:
            zeno.scale_to_fit_width(2.0)
        zeno.move_to([-2.91, -3.61, 0])
        # Preserve the original illustration; animate the whole sprite only.
        self.add(zeno)
        baseline = zeno.get_center().copy()
        elapsed = ValueTracker(0)
        zeno.add_updater(
            lambda m: m.move_to(baseline + UP * .055 * math.sin(
                TAU * elapsed.get_value() / 2.8
            ))
        )
        n = len(episode["segments"])
        for index, segment in enumerate(episode["segments"]):
            wav, duration = (None, float(segment["seconds"])) if SILENT else clips[index]
            self.beat(episode, segment, index, n, wav, duration, elapsed)
        zeno.clear_updaters()

    def chrome(self, episode):
        header = tile("ZENO'S DAILY TECH BRIEF", 6.8, .77, WHITE, PURPLE)
        header.move_to([self.X, 6.36, 0])
        date = words(episode["date"], 25, 6.4, .4, PURPLE, bold=True)
        date.move_to([self.X, 5.72, 0])
        stage = panel(6.75, 5.32).move_to([self.X, 1.0, 0])
        stage.set_stroke(LAVENDER, width=2)
        caption_card = panel(4.38, 2.16).move_to([.62, -3.58, 0])
        speaker = words("ZENO SENSEI", 22, 4, .34, PURPLE, bold=True)
        speaker.move_to([.62, -2.79, 0])
        footer = words("LEARN WITH OBSCURE", 24, 6.3, .38, PURPLE, bold=True)
        footer.move_to([self.X, -5.02, 0])
        track = Line(LEFT*3.2, RIGHT*3.2, color=LAVENDER, stroke_width=6)
        track.move_to([self.X, 5.23, 0])
        return header, date, stage, caption_card, speaker, footer, track

    def beat(self, episode, segment, index, count, wav, duration, clock):
        title = words(segment["title"], 49, 6.55, 1.15, bold=True, wrap=23)
        title.move_to([self.X, 4.45, 0])
        caption = words(segment["caption"], 32, 3.98, 1.30, wrap=22)
        caption.move_to([.62, -3.75, 0])
        graphic, animate = self.graphic(segment["visual"])
        progress = Line(
            [-3.68, 5.23, 0],
            [-3.68 + 6.4*(index+1)/count, 5.23, 0],
            stroke_width=6, color=PURPLE,
        )
        # Fit all beats to measured WAV duration. No extra per-scene gaps,
        # no overlapping narration, and no remote calls during rendering.
        # Very short clips still get enough time for an entrance and exit.
        duration = max(duration, 1.0)
        # Round up to whole frames so the next clip cannot overlap this one.
        duration = math.ceil(duration * config.frame_rate) / config.frame_rate
        entrance = min(.40, duration*.16)
        exit_time = min(.20, duration*.10)
        action_time = min(2.35, duration*.48)
        start = self.time
        initial_clock = clock.get_value()
        if wav is not None:
            self.add_sound(str(wav))
        self.play(
            FadeIn(title, shift=DOWN*.15), FadeIn(caption, shift=RIGHT*.12),
            FadeIn(graphic, shift=UP*.16), Create(progress),
            clock.animate.set_value(initial_clock + entrance),
            run_time=entrance,
        )
        if animate is not None:
            # All animated children belong to the displayed graphic.
            self.play(animate, clock.animate.increment_value(action_time),
                      run_time=action_time)
        remaining = duration - (self.time-start) - exit_time
        if remaining > 1 / config.frame_rate:
            self.play(clock.animate.increment_value(remaining),
                      run_time=remaining, rate_func=linear)
        self.play(
            FadeOut(title), FadeOut(caption), FadeOut(graphic), FadeOut(progress),
            clock.animate.increment_value(exit_time), run_time=exit_time,
        )

    def graphic(self, kind):
        center = RIGHT*self.X + UP*1.0
        if kind in ("hook", "cube"):
            # A flat image and a spatial wireframe, shown as a simple metaphor.
            flat = Rectangle(width=1.55, height=1.35, color=PURPLE,
                             fill_color=BG, fill_opacity=1)
            mountain = Polygon(
                [-.62, -.43, 0], [-.12, .34, 0], [.62, -.43, 0],
                color=PURPLE, fill_color=LAVENDER, fill_opacity=.8,
            ).move_to(flat)
            image = VGroup(flat, mountain)
            front = Square(side_length=1.55, color=PURPLE)
            back = front.copy().shift(RIGHT*.59+UP*.52).set_color(PINK)
            edges = VGroup(*[
                Line(front.get_vertices()[i], back.get_vertices()[i],
                     color=PURPLE, stroke_width=3) for i in range(4)
            ])
            cube = VGroup(front, back, edges)
            grid = VGroup(*[
                Line(LEFT*.775+UP*y, RIGHT*.775+UP*y, color=LAVENDER,
                     stroke_width=1.5) for y in (-.38, 0, .38)
            ]).move_to(front)
            cube.add(grid)
            left = VGroup(image, words("2D IMAGE", 25, 1.65, .45, PURPLE,
                                       bold=True)).arrange(DOWN, buff=.28)
            right = VGroup(cube, words("3D SPACE", 25, 2.3, .45, PURPLE,
                                       bold=True)).arrange(DOWN, buff=.28)
            arrow = Arrow(LEFT*.36, RIGHT*.36, buff=0, color=PURPLE)
            diagram = VGroup(left, arrow, right).arrange(RIGHT, buff=.26)
            caption = words("From pictures to spatial environments", 27,
                            5.5, .7, wrap=30)
            graphic = VGroup(diagram, caption).arrange(DOWN, buff=.55).move_to(center)
            return graphic, AnimationGroup(
                Indicate(arrow, color=PINK, scale_factor=1.12),
                Indicate(cube, color=PURPLE, scale_factor=1.08),
                lag_ratio=.35,
            )
        if kind == "deal":
            names = VGroup(
                tile("AMD", 2.05, .85, BG),
                words("+", 39, .5, .55, PURPLE, bold=True),
                tile("WORLD LABS", 2.85, .85, BG),
            ).arrange(RIGHT, buff=.16)
            amount = words("$8.2B", 108, 5.45, 1.60, PURPLE, bold=True)
            note = words("Originally announced stock valuation", 26,
                         5.7, .8, wrap=28)
            g = VGroup(names, amount, note).arrange(DOWN, buff=.45).move_to(center)
            return g, Indicate(amount, color=PURPLE, scale_factor=1.12)
        if kind == "room":
            floor = panel(5.35, 3.40, BG, PURPLE).move_to(center+UP*.35)
            grid = VGroup(
                *[Line(floor.get_left()+RIGHT*x+UP*1.5,
                       floor.get_left()+RIGHT*x+DOWN*1.5,
                       color=LAVENDER, stroke_opacity=.45) for x in (1,2,3,4)],
                *[Line(floor.get_bottom()+UP*y+LEFT*2.45,
                       floor.get_bottom()+UP*y+RIGHT*2.45,
                       color=LAVENDER, stroke_opacity=.45) for y in (1,2)],
            )
            block = RoundedRectangle(width=1.0, height=1.25, corner_radius=.12,
                                     color=PURPLE, fill_color=PINK,
                                     fill_opacity=.85).move_to(floor)
            robot = Dot(floor.get_center()+LEFT*1.95+DOWN*.95,
                        radius=.22, color=PURPLE)
            path = VMobject(color=PURPLE, stroke_width=3)
            path.set_points_as_corners([
                robot.get_center(), floor.get_center()+LEFT*1.1+DOWN*.95,
                floor.get_center()+RIGHT*1.15+DOWN*.95,
                floor.get_center()+RIGHT*1.95+UP*.95,
            ])
            goal = Circle(radius=.26, color=PURPLE, fill_color=WHITE,
                          fill_opacity=1).move_to(path.get_end())
            goal_mark = words("!", 25, .3, .35, PURPLE, bold=True).move_to(goal)
            label = words("Illustrative simulation", 25, 5.5, .45, PURPLE)
            label.next_to(floor, DOWN, buff=.23)
            group = VGroup(floor, grid, block, path, goal, goal_mark, label, robot)
            return group, MoveAlongPath(robot, path, rate_func=linear)
        if kind == "scientist":
            name = words("FEI-FEI LI", 72, 5.8, 1.15, PURPLE, bold=True)
            role = tile("Chief Scientist", 5.55, .9, BG)
            other = tile("Executive Vice President", 5.55, .9)
            g = VGroup(name, role, other).arrange(DOWN, buff=.36).move_to(center)
            return g, AnimationGroup(
                Indicate(name, color=PURPLE, scale_factor=1.08),
                Indicate(role, color=PURPLE, scale_factor=1.06), lag_ratio=.4)
        if kind == "stack":
            items = VGroup(
                tile("AI MODELS", 5.05, .87, BG),
                tile("SOFTWARE", 5.05, .87),
                tile("HARDWARE", 5.05, .87, BG, PINK),
            ).arrange(DOWN, buff=.49).move_to(center+UP*.15)
            arrows = VGroup(*[
                Arrow(a.get_bottom(), b.get_top(), buff=.04, color=PURPLE,
                      stroke_width=4, max_tip_length_to_length_ratio=.32)
                for a, b in zip(items, items[1:])
            ])
            note = words("Potential future integration", 25, 5.5, .4, PURPLE)
            note.next_to(items, DOWN, buff=.27)
            return VGroup(items, arrows, note), LaggedStart(
                *[Indicate(item, color=PURPLE, scale_factor=1.06)
                  for item in items], lag_ratio=.55)
        if kind == "outro":
            headline = words("LEARN.\nEXPLORE.\nSHARE.", 57, 5.8, 2.1,
                             PURPLE, bold=True)
            button = tile("SUBSCRIBE", 4.6, 1.0, PINK, PURPLE)
            g = VGroup(headline, button).arrange(DOWN, buff=.42).move_to(center)
            return g, Indicate(button, color=PURPLE, scale_factor=1.09)
        return tile(kind, 5.6, 1.25, BG).move_to(center), None
