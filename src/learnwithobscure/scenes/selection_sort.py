"""Selection Sort: a complete character-led lesson with a live Java trace.

Render silently for review with LWO_DISABLE_VOICEOVER=1. Prepare narration
separately with scripts/prepare_selection_sort_audio.py before voiced renders.
"""

import hashlib
import json
from math import ceil
import os
from pathlib import Path
import wave

from manim import *
from manim_voiceover.services.gemini import GeminiService

from learnwithobscure.scenes.bubble_sort import (
    BG, DARK, PURPLE, LAVENDER, PINK, WHITE, PROJECT_ROOT,
    STUDENT_IMAGE, ROBOT_IMAGE, SUBSCRIBE_IMAGE,
    GEMINI_TTS_MODEL, GEMINI_VOICES, AudioPreparationLimitReached,
    make_text, make_heading, fit_within, create_character,
)
from learnwithobscure.scenes.selection_sort_trace import (
    JAVA_TRACE_LINES, JAVA_IMPLEMENTATION, selection_sort_events,
)

AUDIO_DIR = PROJECT_ROOT / "media" / "audio_files" / "selection_sort_demo"


class SelectionSortDemo(Scene):
    """Learn Selection Sort with Obscure and Zeno Sensei, statement by statement."""

    def __init__(self, *args, **kwargs):
        self.audio_prepare_mode = os.getenv("LWO_AUDIO_PREPARE_ONLY") == "1"
        self.voiceover_disabled = os.getenv("LWO_DISABLE_VOICEOVER") == "1"
        self.audio_prepare_max_new = int(os.getenv("LWO_AUDIO_PREPARE_MAX_NEW", "8"))
        self.audio_prepare_generated = 0
        self.audio_prepare_min_interval = float(
            os.getenv("LWO_AUDIO_PREPARE_MIN_INTERVAL", "22")
        )
        self.audio_prepare_last_request = None
        self.review_timeline = []
        super().__init__(*args, **kwargs)

    def play(self, *args, **kwargs):
        if self.audio_prepare_mode:
            return self
        return super().play(*args, **kwargs)

    def wait(self, *args, **kwargs):
        if self.audio_prepare_mode:
            return self
        return super().wait(*args, **kwargs)

    def make_narration_audio(self, narration, speaker):
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        voice = GEMINI_VOICES[speaker]
        cache_key = hashlib.sha256(
            f"{GEMINI_TTS_MODEL}:{voice}:{narration}".encode("utf-8")
        ).hexdigest()[:20]
        audio_path = AUDIO_DIR / f"{cache_key}.wav"

        if not audio_path.is_file() or audio_path.stat().st_size == 0:
            if self.audio_prepare_mode and self.audio_prepare_generated >= self.audio_prepare_max_new:
                raise AudioPreparationLimitReached(
                    f"Reached the preparation limit of {self.audio_prepare_max_new} new clips. "
                    "Run the command again later; completed clips will be reused."
                )
            if not os.getenv("GEMINI_API_KEY"):
                raise RuntimeError(
                    "GEMINI_API_KEY is required when Selection Sort narration is missing. "
                    "Set it locally, then rerun audio preparation."
                )

            if self.audio_prepare_mode and self.audio_prepare_last_request is not None:
                import time

                elapsed = time.monotonic() - self.audio_prepare_last_request
                delay = self.audio_prepare_min_interval - elapsed
                if delay > 0:
                    print(f"Waiting {delay:.1f}s before the next Gemini TTS request...")
                    time.sleep(delay)

            service = GeminiService(voice=voice, model=GEMINI_TTS_MODEL)
            if self.audio_prepare_mode:
                import time

                self.audio_prepare_last_request = time.monotonic()
            result = service.generate_from_text(
                narration,
                cache_dir=AUDIO_DIR,
                path=audio_path.name,
            )
            audio_path = AUDIO_DIR / result["original_audio"]
            if self.audio_prepare_mode:
                self.audio_prepare_generated += 1

        with wave.open(str(audio_path), "rb") as audio_file:
            duration = audio_file.getnframes() / audio_file.getframerate()
        return audio_path, duration

    def speak(self, narration, speaker="robot", *animations, run_time=1.2, **play_kwargs):
        self.review_mark("narration", speaker=speaker, text=narration)
        if self.voiceover_disabled:
            hold_time = max(run_time, min(4.0, 0.11 * len(narration.split())))
            if animations:
                self.play(*animations, run_time=run_time, **play_kwargs)
                if hold_time > run_time:
                    self.wait(hold_time - run_time)
            else:
                self.wait(hold_time)
            return
        audio_path, speech_duration = self.make_narration_audio(narration, speaker)
        if self.audio_prepare_mode:
            return
        speech_start = self.time
        self.add_sound(str(audio_path))
        if animations:
            self.play(*animations, run_time=run_time, **play_kwargs)
        # Use actual rendered time and whole frames, so the next line cannot
        # start before this clip ends. Leave a small conversational pause.
        remaining_speech = speech_duration + 0.1 - (self.time - speech_start)
        if remaining_speech > 0:
            frames = ceil(remaining_speech * config.frame_rate) + 1
            self.wait(frames / config.frame_rate)

    def caption_line(self, text):
        caption = make_text(text, size=15, color=DARK)
        available_width = self.caption_box.width - 0.5
        if caption.width > available_width:
            caption.scale_to_fit_width(available_width)
        return caption.move_to(self.caption_box)

    def caption_transition(self, text):
        next_caption = self.caption_line(text)
        transition = Succession(
            FadeOut(self.current_caption, run_time=0.18),
            FadeIn(next_caption, run_time=0.18),
        )
        self.current_caption = next_caption
        return transition

    def review_mark(self, name, **details):
        self.review_timeline.append({"name": name, "time": self.time, **details})

    def say(self, narration, caption, speaker="robot", *animations, run_time=0.8):
        """Keep speech independent of the short, readable caption summary."""
        label = "Obscure" if speaker == "student" else "Zeno Sensei"
        self.speak(
            narration, speaker, *animations,
            self.caption_transition(f"{label}: {caption}"), run_time=run_time,
        )

    def clear_stage(self, stage):
        # Each screen owns its objects. Never fade an already removed screen.
        self.play(FadeOut(stage), run_time=0.45)

    @staticmethod
    def pointer(label, color, x, y, above=True):
        tip = Triangle(stroke_width=0, fill_color=color, fill_opacity=1)
        tip.scale(0.065)
        if above:
            tip.rotate(PI)
        text = make_heading(label, size=14, color=color)
        parts = (text, tip) if above else (tip, text)
        return VGroup(*parts).arrange(DOWN, buff=0.045).move_to([x, y, 0])

    @staticmethod
    def array_row(values, center=(0, 1.05, 0), spacing=1.1):
        xs = [center[0] + spacing * (i - (len(values) - 1) / 2) for i in range(len(values))]
        boxes = VGroup(*[
            RoundedRectangle(
                width=0.88, height=0.76, corner_radius=0.1,
                stroke_color=PURPLE, stroke_width=2,
                fill_color=WHITE, fill_opacity=1,
            ).move_to([x, center[1], 0]) for x in xs
        ])
        numbers = [make_heading(str(value), size=25).move_to(box) for value, box in zip(values, boxes)]
        indices = VGroup(*[
            make_text(str(i), size=13, color=PURPLE).move_to([x, center[1] - 0.57, 0])
            for i, x in enumerate(xs)
        ])
        return boxes, numbers, indices, xs

    @staticmethod
    def code_lines(source_lines, width, height, size=17):
        """Retain leading indentation when lines are independent mobjects."""
        char_width = Text("M" * 10, font="Consolas", font_size=size).width / 10
        lines = VGroup()
        for index, source in enumerate(source_lines):
            indent = len(source) - len(source.lstrip())
            line = Text(
                source.lstrip() or "M", font="Consolas", font_size=size,
                color=DARK, disable_ligatures=True,
            )
            # Manim cannot build a ligature-disabled Text from whitespace alone.
            # An invisible glyph retains the blank row and its vertical spacing.
            if not source.strip():
                line.set_opacity(0)
            line.move_to([indent * char_width + line.width / 2, -0.31 * index, 0])
            lines.add(line)
        return fit_within(lines, width, height)

    @staticmethod
    def info_screen(title, lines):
        heading = fit_within(make_heading(title, size=27), 11.6, 0.55).move_to([0, 2.25, 0])
        content = VGroup(*[
            fit_within(make_text(line, size=21, color=PURPLE if i == 0 else DARK), 10.9, 0.8)
            for i, line in enumerate(lines)
        ]).arrange(DOWN, buff=0.4).move_to([0, 0.1, 0])
        return VGroup(heading, content)

    def visual_walkthrough(self, values):
        """Show every scan and every pass, swapping only after the full scan."""
        values = list(values)
        boxes, numbers, indices, xs = self.array_row(values)
        status = make_heading("Sort this array while keeping swaps down", size=22).move_to([0, -0.15, 0])
        detail = make_text("Ascending order: smallest to largest", size=18, color=PURPLE).move_to([0, -0.8, 0])
        counts = make_text("Comparisons: 0    Swaps: 0", size=17).move_to([0, -1.5, 0])
        stage = VGroup(boxes, *numbers, indices, status, detail, counts)
        self.play(FadeIn(stage), run_time=0.7)
        self.say(
            "Zeno Sensei, I have this array of numbers, and I want it sorted from smallest to largest. Comparing numbers is cheap, but moving them around is expensive. Can we sort it while keeping the swaps down?",
            "Can we sort this array with fewer swaps?", "student",
        )
        self.say(
            "Yes. We can use Selection Sort to keep the swaps down. It finds the smallest value in the unsorted part, then swaps that value into the next position. At most one swap per pass. Let's watch it work.",
            "Find the minimum; place it; repeat.", "robot",
            FadeIn(self.title),
        )
        start_pointer = self.pointer("start", DARK, xs[0], 2.45)
        minimum_pointer = self.pointer("minIndex", PURPLE, xs[0], 1.94)
        scan_pointer = self.pointer("scan", PINK, xs[1], -0.03, above=False)
        # The scan pointer lives below the index row; move the status down.
        self.play(status.animate.move_to([0, -0.65, 0]), detail.animate.move_to([0, -1.15, 0]),
                  counts.animate.move_to([0, -1.8, 0]), run_time=0.4)
        comparisons = swaps = 0
        for start in range(len(values) - 1):
            minimum = start
            if start == 0:
                self.say(
                    "Start marks the slot we are filling. Min index remembers the position of the smallest value seen so far. At first, nominate five. Scan checks the remaining candidates.",
                    "minIndex stores a position, not the value.", "robot",
                    FadeIn(start_pointer), FadeIn(minimum_pointer), FadeIn(scan_pointer),
                )
            else:
                scan_pointer.set_x(xs[start + 1])
                self.play(
                    start_pointer.animate.set_x(xs[start]), minimum_pointer.animate.set_x(xs[start]),
                    FadeIn(scan_pointer),
                    Transform(status, make_heading(f"Pass {start + 1}: fill index {start}", size=22).move_to(status)),
                    run_time=0.6,
                )
                if start == 1:
                    self.say(
                        "One is settled. Your turn: among five, four, two, and eight, which value gets the next slot? Pause here and choose before we scan.",
                        "Your turn: which remaining value comes next?", "student",
                    )
                    self.wait(2)
                elif start == 2:
                    self.say(
                        "The fixed prefix is one, two. Now search only the remaining three values; those first two have earned their seats.",
                        "Keep the fixed prefix; search the suffix.", "robot",
                    )
                else:
                    self.say(
                        "Only five and eight remain. We still check them, even though they look ready for the group photo.",
                        "Final pass: compare 8 with the candidate 5.", "robot",
                    )
            for scan in range(start + 1, len(values)):
                if scan != start + 1:
                    self.play(scan_pointer.animate.set_x(xs[scan]), run_time=0.4)
                candidate, current = values[minimum], values[scan]
                smaller = current < candidate
                comparisons += 1
                if start == 0:
                    explanations = {
                        1: "One is smaller than five. Move the minimum marker to index one. The numbers themselves stay where they are.",
                        2: "Four is not smaller than one. Keep index one as our candidate.",
                        3: "Two cannot beat one either. Remember, we compare against the current minimum, not against the previous neighbor.",
                        4: "Eight is larger too. Now every remaining value has been checked, so one is the confirmed minimum.",
                    }
                    narration = explanations[scan]
                elif start == 1:
                    narration = {
                        2: "Four takes the lead over five. Update the marker, without moving either value.",
                        3: "And two beats four. This is why we finish the scan before deciding what to swap.",
                        4: "Eight doesn't beat two. If you picked two, your prediction checks out.",
                    }[scan]
                else:
                    narration = None
                actions = [
                    Transform(status, make_heading(
                        f"{current} < {candidate}: {'new minimum' if smaller else 'keep candidate'}", size=22,
                    ).move_to(status)),
                    Transform(detail, make_text(
                        f"Compare arr[{scan}] with arr[{minimum}]", size=18, color=PURPLE,
                    ).move_to(detail)),
                    Transform(counts, make_text(f"Comparisons: {comparisons}    Swaps: {swaps}", size=17).move_to(counts)),
                ]
                if smaller:
                    minimum = scan
                    actions.append(minimum_pointer.animate.set_x(xs[minimum]))
                if narration:
                    self.say(narration, f"{current} < {candidate}: {'update minIndex' if smaller else 'keep minIndex'}.", "robot", *actions)
                else:
                    self.play(*actions, run_time=0.75)
                    self.wait(0.7)
                self.review_mark("visual_compare", start=start, scan=scan, min_index=minimum, values=values.copy())
                if start == 0 and scan == 1:
                    self.say(
                        "We found one. Why not swap it right now?",
                        "Why wait to swap?", "student",
                    )
                    self.say(
                        "Because another value later could be even smaller. We know one is the smallest seen so far. Only a complete scan proves it is the smallest remaining.",
                        "A candidate becomes confirmed after the whole scan.", "robot",
                    )
            self.play(FadeOut(scan_pointer), run_time=0.25)
            if minimum != start:
                if start == 0:
                    narration = "Now swap one with five. These slots can be far apart; Selection Sort does not require neighbors. The first slot is settled for good."
                else:
                    narration = "The scan chose two at index three. Exchange it with five at index one, then extend the fixed prefix."
                self.say(
                    narration, f"Swap positions {start} and {minimum}; fix index {start}.", "robot",
                    Swap(numbers[start], numbers[minimum], path_arc=PI / 2), run_time=1.1,
                )
                values[start], values[minimum] = values[minimum], values[start]
                numbers[start], numbers[minimum] = numbers[minimum], numbers[start]
                swaps += 1
            else:
                self.say(
                    "The minimum is already in the slot we're filling. Skip the exchange; the position is still confirmed.",
                    "minIndex equals start: no swap needed.", "robot",
                ) if start == 2 else self.say(
                    "Five stays where it is. The final leftover value, eight, must also be in place. Nothing remains unaccounted for.",
                    "Four passes fix all five positions.", "robot",
                )
            actions = [boxes[start].animate.set_fill(PINK, opacity=0.24),
                       Transform(status, make_heading(f"Pass {start + 1} complete: {values[start]} is fixed", size=22).move_to(status)),
                       Transform(counts, make_text(f"Comparisons: {comparisons}    Swaps: {swaps}", size=17).move_to(counts)),
                       Transform(detail, make_text(f"Fixed prefix: {values[:start + 1]}", size=18, color=PURPLE).move_to(detail))]
            if start == len(values) - 2:
                actions.append(boxes[-1].animate.set_fill(PINK, opacity=0.24))
                actions.append(Transform(detail, make_text("Every position is fixed: [1, 2, 4, 5, 8]", size=18, color=PURPLE).move_to(detail)))
            self.play(*actions, run_time=0.55)
            self.review_mark("visual_pass_complete", start=start, values=values.copy(), comparisons=comparisons, swaps=swaps)
        self.say(
            "So we do all the looking first, move just the chosen minimum, and grow the sorted part from the left. Ten comparisons, but only two swaps here.",
            "Scan first, swap once, grow the fixed prefix.", "student",
        )
        # The numeric glyphs have moved; collect their current references once.
        self.clear_stage(VGroup(boxes, *numbers, indices, status, detail, counts, start_pointer, minimum_pointer))

    def order_comparison(self):
        screen = self.info_screen("What if we want largest to smallest?", [
            "Ascending: choose the minimum", "arr[scan] < arr[minIndex]",
            "Descending: choose the maximum", "arr[scan] > arr[maxIndex]",
        ])
        self.say("Can I send the biggest number to the front instead?", "What about descending order?", "student", FadeIn(screen))
        self.say(
            "Yes. Reverse the comparison and track the maximum instead. Place the largest remaining value at start each pass. The scan and the guarded swap work the same way.",
            "Reverse the comparison; select the maximum.", "robot",
        )
        self.clear_stage(screen)

    def java_walkthrough(self, initial_values):
        """Drive the Java highlight and every assignment from the tested trace."""
        boxes, numbers, indices, xs = self.array_row(initial_values, center=(-2.85, 1.05, 0))
        panel = RoundedRectangle(
            width=6.65, height=4.75, corner_radius=0.12,
            stroke_color=LAVENDER, stroke_width=2, fill_color=WHITE, fill_opacity=1,
        ).move_to([3.45, 0.35, 0])
        source = self.code_lines(JAVA_TRACE_LINES, 6.15, 4.15, size=16).move_to(panel)
        code_label = make_heading("Java: the same input", size=18, color=PURPLE).move_to([3.45, 2.96, 0])
        def highlight_for(index):
            return SurroundingRectangle(source[index], buff=0.045, color=PINK,
                                        stroke_width=2, fill_color=PINK, fill_opacity=0.14)
        highlight = highlight_for(0)
        state = make_heading("One statement, one visible effect", size=18).move_to([-2.85, -0.55, 0])
        operation = make_text("Start with the original array again.", size=15).move_to([-2.85, -1.25, 0])
        badges = make_text("start = -    minIndex = -    scan = -", size=15, color=PURPLE).move_to([-2.85, -1.85, 0])
        count_label = make_text("Comparisons: 0    Swaps: 0", size=15).move_to([-3.45, -2.4, 0])
        temp_box = RoundedRectangle(width=0.9, height=0.55, corner_radius=0.08,
                                    stroke_color=PINK, fill_color=WHITE, fill_opacity=1).move_to([-0.6, -2.4, 0])
        temp_label = make_text("temp", size=14, color=PURPLE).next_to(temp_box, UP, buff=0.1)
        temp_number = make_heading("-", size=23, color=PINK).move_to(temp_box)
        # Reserve the right side of this row for the scan boundary cue.
        state.move_to([-3.35, -0.45, 0])
        fit_within(state, 4.0, 0.5)
        start_pointer = self.pointer("start", DARK, xs[0], 2.43)
        minimum_pointer = self.pointer("minIndex", PURPLE, xs[0], 1.92)
        scan_pointer = self.pointer("scan", PINK, xs[1], -0.03, above=False)
        boundary_note = make_text("scan = length\nno array read", size=13, color=PINK).move_to([-0.65, -0.48, 0])
        boundary_visible = False
        start_visible = minimum_visible = scan_visible = False
        objects = [boxes, *numbers, indices, panel, source, code_label, highlight,
                   state, operation, badges, count_label, temp_box, temp_label, temp_number]
        self.play(FadeIn(VGroup(*objects)), run_time=0.7)
        self.say(
            "Let's rebuild the same result in Java. The highlight arrives first; then that statement changes the array or a variable. Watch the difference between moving min index and moving a number.",
            "Follow each statement and its exact effect.", "robot",
        )
        narrated = set()
        active_line = 0
        displayed = list(initial_values)
        explanation = {
            "outer_init": ("Set start to zero, the first slot we want to fill.", "Initialize start = 0"),
            "outer_check": ("Continue while start is before the last slot. The last value will be fixed automatically.", "Check start < arr.length - 1"),
            "reset_min": ("Nominate the value at start. Min index stores its array position, not the number itself.", "minIndex = start"),
            "inner_init": ("Begin scanning one position after start. The candidate does not need to compete with itself.", "scan = start + 1"),
            "inner_check": ("Check that scan is still inside the array before reading that slot.", "Check scan < arr.length"),
            "compare": ("Compare the scanned value with the smallest value seen so far. A strict less than test chooses a new candidate only when it is smaller.", "Compare the two values"),
            "update_min": ("Remember this smaller value's index. This assignment moves the marker; the array does not change.", "minIndex = scan; no array write"),
            "inner_increment": ("Advance scan by one, then check the loop condition again.", "scan++"),
            "scan_complete": ("The scan has ended. Our candidate is now the minimum of the entire remaining part.", "The complete suffix has been checked"),
            "swap_check": ("Only exchange values when min index differs from start. Otherwise the minimum is already in the right slot.", "Check minIndex != start"),
            "save_temp": ("Save the original value at start in temp before overwriting that slot. The array is unchanged so far.", "Preserve arr[start] in temp"),
            "assign_start": ("Copy the minimum into the start slot. Both array slots briefly show the same number. Temp still protects the displaced value.", "Copy the minimum; temp protects the old value"),
            "assign_min": ("Copy temp back into the minimum's old slot. These two separate array writes complete one swap.", "Restore temp; complete the swap"),
            "pass_complete": ("This position is now fixed. All values in the remaining suffix are at least this large.", "Extend the fixed prefix"),
            "outer_increment": ("Advance start to the next slot. The next pass begins with a fresh minimum candidate.", "start++"),
            "done": ("The outer condition is false. Four passes, ten value comparisons, and two completed swaps sorted this array.", "Sorted: 1, 2, 4, 5, 8"),
        }
        contextual = {
            ("reset_min", 2, None): "Now nominate five at index one. The minimum marker resets for every pass; it must not keep pointing at the one we already fixed.",
            ("compare", 2, 2): "Four beats five. The next statement will remember index two.",
            ("compare", 2, 3): "Two beats four. Start is still at index one, and the array values have not moved.",
            ("swap_check", 3, None): "Min index equals start here, so the guard is false and all three swap assignments are skipped. We still have another pass to do.",
        }
        for event in selection_sort_events(initial_values):
            kind = event.kind
            begin = self.time
            if event.line_index is not None and event.line_index != active_line:
                self.play(Transform(highlight, highlight_for(event.line_index)), run_time=0.22)
                active_line = event.line_index
            narration, description = explanation[kind]
            caption = description
            actions = []
            if kind in ("outer_init", "outer_increment"):
                description = f"start = {event.start}: next slot to fill"
                if start_visible:
                    actions.append(start_pointer.animate.set_x(xs[event.start]))
                else:
                    actions.append(FadeIn(start_pointer))
                    start_visible = True
            elif kind == "outer_check":
                description = f"{event.start} < {len(initial_values) - 1}: {str(event.condition).lower()}"
                if not event.condition:
                    narration = "Start has reached the last index. The outer loop stops; that final value is already in place."
            elif kind == "reset_min":
                description = f"minIndex = start = {event.min_index}"
                if minimum_visible:
                    actions.append(minimum_pointer.animate.set_x(xs[event.min_index]))
                else:
                    minimum_pointer.set_x(xs[event.min_index])
                    actions.append(FadeIn(minimum_pointer))
                    minimum_visible = True
            elif kind == "inner_init":
                description = f"scan = {event.start} + 1 = {event.scan}"
                scan_pointer.set_x(xs[event.scan])
                actions.append(FadeIn(scan_pointer))
                scan_visible = True
            elif kind == "inner_check":
                description = f"{event.scan} < {len(initial_values)}: {str(event.condition).lower()}"
                if not event.condition:
                    narration = "Scan equals the array length, so stop before reading past the end. There is no array slot at index five."
            elif kind == "compare":
                current, candidate = event.values[event.scan], event.values[event.min_index]
                description = f"arr[{event.scan}] < arr[{event.min_index}]\n{current} < {candidate}: {str(event.condition).lower()}"
                if not event.condition:
                    narration = "This value is not smaller than the candidate, so skip the minimum update."
            elif kind == "update_min":
                description = f"minIndex = {event.min_index}; array unchanged"
                actions.append(minimum_pointer.animate.set_x(xs[event.min_index]))
            elif kind == "inner_increment":
                description = f"scan++: {event.scan - 1} becomes {event.scan}"
                # The final scan value is a boundary, not a valid array index.
                if event.scan < len(xs):
                    actions.append(scan_pointer.animate.set_x(xs[event.scan]))
                else:
                    actions.extend([FadeOut(scan_pointer), FadeIn(boundary_note)])
                    scan_visible = False
                    boundary_visible = True
            elif kind == "scan_complete":
                description = f"Minimum: {event.values[event.min_index]} at index {event.min_index}"
                if scan_visible:
                    actions.append(FadeOut(scan_pointer))
                if boundary_visible:
                    actions.append(FadeOut(boundary_note))
                    boundary_visible = False
                scan_visible = False
            elif kind == "swap_check":
                description = f"{event.min_index} != {event.start}: {str(event.condition).lower()}"
            elif kind in ("save_temp", "assign_start", "assign_min"):
                if kind == "save_temp":
                    origin, destination, value, color = numbers[event.start], temp_number, event.temp, PINK
                    description = f"temp = arr[{event.start}] = {event.temp}"
                elif kind == "assign_start":
                    origin, destination = numbers[event.min_index], numbers[event.start]
                    value, color = event.values[event.start], DARK
                    description = f"arr[{event.start}] = arr[{event.min_index}]\nBoth slots show {value}; temp = {event.temp}"
                    displayed[event.start] = value
                else:
                    origin, destination = temp_number, numbers[event.min_index]
                    value, color = event.values[event.min_index], DARK
                    description = f"arr[{event.min_index}] = temp = {value}"
                    displayed[event.min_index] = value
                target = make_heading(str(value), size=23 if kind == "save_temp" else 25, color=color).move_to(destination)
                actions.extend([FadeOut(destination), TransformFromCopy(origin, target, path_arc=-PI / 4)])
            elif kind == "pass_complete":
                description = f"Pass {event.pass_number}: first {event.sorted_until} position(s) fixed"
                actions.extend(box.animate.set_fill(PINK, opacity=0.24) for box in boxes[:event.sorted_until])
                # temp leaves its block scope; this is not a Java reset statement.
                actions.append(Transform(temp_number, make_heading("-", size=23, color=PINK).move_to(temp_box)))
                if minimum_visible:
                    actions.append(FadeOut(minimum_pointer))
                    minimum_visible = False
            elif kind == "done":
                description = "10 comparisons; 2 swaps; sorted in place"
                actions.extend(box.animate.set_fill(PINK, opacity=0.24) for box in boxes)
                if start_visible:
                    actions.append(FadeOut(start_pointer))
                    start_visible = False
            caption = description.replace("\n", "; ")
            status_text = explanation[kind][1]
            state_target = fit_within(make_heading(status_text, size=17), 4.0, 0.5).move_to(state)
            op_target = fit_within(make_text(description, size=15), 5.3, 0.7).move_to(operation)
            minimum_text = "-" if event.min_index is None else event.min_index
            scan_text = "-" if event.scan is None else event.scan
            # The trace retains start for diagnostics, but Java's loop-local
            # variable is no longer in scope once the loop has finished.
            start_text = "-" if kind == "done" else event.start
            actions.extend([
                Transform(state, state_target), Transform(operation, op_target),
                Transform(badges, make_text(f"start = {start_text}    minIndex = {minimum_text}    scan = {scan_text}", size=15, color=PURPLE).move_to(badges)),
                Transform(count_label, make_text(f"Comparisons: {event.comparisons}    Swaps: {event.swaps}", size=15).move_to(count_label)),
            ])
            key = (kind, event.condition)
            chosen = contextual.get((kind, event.pass_number, event.scan))
            if chosen is None and key not in narrated:
                chosen = narration
            narrated.add(key)
            if chosen:
                self.say(chosen, caption, "robot", *actions, run_time=0.9)
            else:
                self.play(*actions, self.caption_transition("Zeno Sensei: " + caption), run_time=0.65)
                self.wait(0.65)
            if kind in ("save_temp", "assign_start", "assign_min"):
                self.remove(target)
                destination.become(target)
                self.add(destination)
            if not self.audio_prepare_mode:
                if tuple(displayed) != event.values:
                    raise AssertionError(f"Java array out of sync at {kind}")
                if event.line_index is not None and abs(highlight.get_y() - source[event.line_index].get_y()) > 1e-5:
                    raise AssertionError(f"Java highlight out of sync at {kind}")
                for index, number in enumerate(numbers):
                    if abs(number.get_x() - boxes[index].get_x()) > 1e-5:
                        raise AssertionError(f"Array slot {index} moved during {kind}")
            self.review_mark(
                "java_step", kind=kind, line=event.line_index, start=event.start,
                min_index=event.min_index, scan=event.scan, temp=event.temp,
                values=list(event.values), comparisons=event.comparisons, swaps=event.swaps,
                begin=begin, sample=max(begin, self.time - 0.2),
            )
            if kind == "update_min" and event.pass_number == 1 and event.scan == 1:
                self.say("The marker moved, but five and one didn't. So min index is just keeping a note?", "A marker update is not a swap?", "student")
                self.say("Right. We write to the array only after the scan is finished. Min index is our bookmark, not a moving van.", "Yes. The array changes only in the swap block.", "robot")
        if start_visible:
            objects.append(start_pointer)
        if minimum_visible:
            objects.append(minimum_pointer)
        if scan_visible:
            objects.append(scan_pointer)
        if boundary_visible:
            objects.append(boundary_note)
        self.clear_stage(VGroup(*objects))

    def early_exit_question(self):
        boxes, numbers, indices, xs = self.array_row([1, 3, 2])
        heading = make_heading("No swap. Are we done?", size=26).move_to([0, 2.25, 0])
        note = make_text("Pass 1: minimum 1 is already at start", size=20, color=PURPLE).move_to([0, -0.1, 0])
        # Empty Text has no geometry, so it cannot retain a reserved position.
        # Position the actual result now and reveal it only after the swap.
        result = make_text("Sorted result: [1, 2, 3]", size=20).move_to([0, -1.05, 0])
        stage = VGroup(boxes, *numbers, indices, heading, note)
        self.say("Bubble Sort had a flag to stop after a pass with no swaps. Can we borrow that trick?", "Can no swaps mean an early exit?", "student", FadeIn(stage))
        self.say(
            "Try this array: one, three, two. The first scan confirms one is the minimum. No swap. Before I continue, does that prove the other two are sorted?",
            "Predict: is [1, 3, 2] sorted after pass 1?", "robot",
            boxes[0].animate.set_fill(PINK, opacity=0.24),
        )
        self.wait(2)
        self.say("No, three and two still need work. We only proved that one belongs at the front.", "A no-swap pass fixes one slot, not the entire array.", "student")
        self.say(
            "That's the catch. Bubble Sort's full no-swap pass checks every neighboring pair in its active range. A selection pass only finds one minimum. It cannot certify the order of the rest.",
            "Selection Sort must continue with the remaining suffix.", "robot",
            Transform(note, make_text("Pass 2: choose 2 and swap it with 3", size=20, color=PURPLE).move_to(note)),
            Swap(numbers[1], numbers[2], path_arc=PI / 2),
            FadeIn(result),
        )
        stage.add(result)
        self.review_mark("no_swap_counterexample", values=[1, 2, 3])
        self.clear_stage(stage)

    def extra_cases(self):
        cases = [
            ([1, 2, 3, 4], "Already sorted", "Everything is in place. Can we skip the comparisons?",
             "The swap guard skips every exchange, but each pass still scans the remaining values. Four numbers still need six value comparisons and zero swaps."),
            ([4, 3, 2, 1], "Reverse order", "What if the numbers arrive completely backwards?",
             "The same rule works: choose the minimum and place it at start. This input takes six comparisons and two swaps. Reverse order does not mean every pass needs an exchange."),
            ([0, -2, 0, -5], "Negatives and duplicates", "Do repeated values or minus signs need a special rule?",
             "No. Ordinary numeric comparisons already handle them. Negative five is smaller than negative two. Equal values do not replace the current candidate because our comparison is strictly less than."),
            ([], "Empty array", "And if there are no numbers at all?",
             "The outer condition is false immediately. There are no value comparisons and no array reads. The empty array is already sorted."),
            ([7], "One value", "Does seven need an opponent?",
             "No tournament required. A one-element array is already sorted too. The outer loop runs zero passes, with zero comparisons and zero swaps."),
        ]
        for values, title, question, answer in cases:
            final = selection_sort_events(values)[-1]
            stage = self.info_screen(title, [
                f"Input: {values}", f"Output: {list(final.values)}",
                f"Value comparisons: {final.comparisons}    Swaps: {final.swaps}",
            ])
            self.say(question, title + "?", "student", FadeIn(stage))
            self.say(answer, f"{final.comparisons} value comparisons; {final.swaps} swaps.", "robot")
            self.review_mark("extra_case", case=title, values=list(final.values), comparisons=final.comparisons, swaps=final.swaps)
            self.clear_stage(stage)

    def stability_demo(self):
        boxes, numbers, _, xs = self.array_row(["2A", "2B", "1"])
        heading = make_heading("Equal keys: does their order survive?", size=26).move_to([0, 2.25, 0])
        note = make_text("Compare only the number; A and B mark identity", size=19, color=PURPLE).move_to([0, -0.05, 0])
        order = make_heading("Before: 2A comes before 2B", size=21).move_to([0, -1.0, 0])
        stage = VGroup(boxes, *numbers, heading, note, order)
        self.say(
            "We never replace the candidate with an equal value. Does that keep equal items in their original order, like Bubble Sort did?",
            "Does strict < make Selection Sort stable?", "student", FadeIn(stage),
        )
        self.say(
            "Watch two A, two B, and one. A and B are name tags; we compare only the numbers. The minimum is one, so swap it with two A across the other two.",
            "Swap 1 with 2A across 2B.", "robot",
            Swap(numbers[0], numbers[2], path_arc=PI / 2),
            Transform(order, make_heading("After: 2B comes before 2A", size=21, color=PINK).move_to(order)),
        )
        self.say("The numbers are sorted, but those two name tags changed order. The swap jumped right over B!", "Sorted values, reversed equal-item order.", "student")
        self.say(
            "Exactly. Stable means equal keys preserve their original relative order. This swap-based Selection Sort is not stable, even with a strict comparison. A stable variant can shift values instead, but that changes the implementation and its movement cost.",
            "Long-distance swaps can reverse equal keys.", "robot",
        )
        self.review_mark("stability_counterexample", values=["1", "2B", "2A"])
        self.clear_stage(stage)

    def complexity_and_guidance(self):
        screen = self.info_screen("Selection Sort: time and space", [
            "Best, average, worst time: O(n^2)", "Auxiliary space: O(1)",
            "At most one swap per pass; in place; not stable",
        ])
        self.say(
            "Here's the cost before we unpack it. Best, average, and worst-case time are all quadratic. Extra space is constant. For a nonempty array, we make at most n minus one swaps.",
            "Quadratic scans, few swaps, constant extra space.", "robot", FadeIn(screen),
        )
        self.say("Even the already sorted input gets quadratic time? It must be tired of proving itself.", "Why is the best case still O(n^2)?", "student")
        self.clear_stage(screen)
        screen = self.info_screen("Count the comparisons, not just the swaps", [
            "5 values: 4 + 3 + 2 + 1 = 10",
            "n values: (n - 1) + ... + 1 = n(n - 1) / 2",
            "Same value-comparison count for every input order",
            "For n >= 2: best, average, worst are Theta(n^2)",
        ])
        self.say(
            "Every pass searches the whole remaining part. The first takes n minus one comparisons, the next n minus two, down to one. Add them: n times n minus one divided by two. Input order changes the swaps, but not that comparison count. So quadratic is a tight bound in every case.",
            "Every arrangement does n(n - 1) / 2 value comparisons.", "robot", FadeIn(screen),
        )
        self.say(
            "Our guard prevents pointless self-swaps. A nonempty array needs at most n minus one swaps; sorted input needs none. Empty input also needs none. Fewer swaps do not remove those quadratic scans.",
            "Nonempty: at most n - 1 swaps; empty: 0.", "robot",
        )
        self.clear_stage(screen)
        screen = self.info_screen("Where does the memory go?", [
            "Input array: reused in place", "Helpers: start, scan, minIndex, temp",
            "Fixed number of helpers -> O(1) auxiliary space",
        ])
        self.say("Min index, scan, start, temp... are we secretly building another array?", "Do the helper variables grow with the input?", "student", FadeIn(screen))
        self.say(
            "Just four helper variables, regardless of the array length. Temp holds one value during a swap. We reuse the input array, so auxiliary space is O of one. That measure excludes the input itself. The video records snapshots for teaching; the Java algorithm doesn't store those snapshots.",
            "The Java method uses constant extra memory.", "robot",
        )
        self.clear_stage(screen)
        screen = self.info_screen("When is it useful?", [
            "Simple to learn; works in place",
            "Few swaps can help when writes are expensive",
            "Still quadratic, even when already sorted",
            "For large inputs: prefer an efficient library sort",
        ])
        self.say("So when would I choose it over Bubble Sort?", "What do fewer swaps buy us?", "student", FadeIn(screen))
        self.say(
            "It's useful for learning, tiny inputs, or exploring the tradeoff when writes cost more than comparisons. Each swap writes two array slots, and each pass makes at most one swap. That's at most two array writes per pass. Comparisons still grow quadratically. For large inputs, use an efficient library sort and check its stability if equal-item order matters.",
            "Few writes are useful; quadratic comparisons still limit scale.", "robot",
        )
        self.clear_stage(screen)
        screen = self.info_screen("Bubble Sort and Selection Sort", [
            "Bubble: compare neighbors; fix the right end",
            "Selection: scan for a minimum; fix the left end",
            "Bubble with early exit: sorted input is O(n)",
            "Selection: O(n^2) even sorted; few swaps",
        ])
        self.say(
            "Bubble Sort keeps adjusting neighboring pairs. Selection Sort scouts the remaining values, then places one winner. With strict comparisons, our Bubble Sort is stable; this long-swap version is not. Same sorting goal, different evidence and different tradeoffs.",
            "Different passes prove different things.", "robot", FadeIn(screen),
        )
        self.clear_stage(screen)

    def complete_java(self):
        pages = [
            ("Complete Java implementation", JAVA_IMPLEMENTATION.splitlines(),
             "Here is the complete method. It expects a non-null integer array and changes that array in place. Empty and single-element arrays pass through safely. Keep the minimum search inside the outer loop and the swap outside the inner loop.",
             "Reset minIndex each pass; swap after the full scan."),
            ("Call it and check the output", [
                "int[] numbers = {5, 1, 4, 2, 8};", "selectionSort(numbers);", "",
                "for (int value : numbers) {", '    System.out.print(value + " ");', "}",
                "", "// Output: 1 2 4 5 8",
            ], "Call selection sort on the array, then print its values. It returns void because the changes happen in the original array. The output is one, two, four, five, eight.",
             "The method sorts the original array in place."),
        ]
        for title, lines, narration, caption in pages:
            heading = make_heading(title, size=26).move_to([0, 2.5, 0])
            panel = RoundedRectangle(
                width=10.9, height=4.5, corner_radius=0.12,
                stroke_color=LAVENDER, stroke_width=2, fill_color=WHITE, fill_opacity=1,
            ).move_to([0, -0.05, 0])
            source = self.code_lines(lines, 10.25, 4.0, size=18).move_to(panel)
            stage = VGroup(heading, panel, source)
            self.say(narration, caption, "robot", FadeIn(stage))
            self.wait(2)
            self.review_mark("complete_java", page=title)
            self.clear_stage(stage)

    def construct(self):
        self.camera.background_color = BG
        self.title = make_heading("Selection Sort", size=39).move_to([0, 3.3, 0])
        student = create_character(STUDENT_IMAGE, 1.45).move_to([-6.05, -2.57, 0])
        robot = create_character(ROBOT_IMAGE, 1.45).move_to([6.05, -2.57, 0])
        self.caption_box = RoundedRectangle(
            width=9.5, height=0.72, corner_radius=0.14,
            stroke_color=PURPLE, stroke_width=2, fill_color=WHITE, fill_opacity=1,
        ).move_to([0, -3.28, 0])
        self.current_caption = self.caption_line("Obscure: Could we sort with fewer swaps?")
        self.play(FadeIn(Group(student, robot, self.caption_box, self.current_caption)), run_time=0.7)
        self.visual_walkthrough([5, 1, 4, 2, 8])
        self.order_comparison()
        self.java_walkthrough([5, 1, 4, 2, 8])
        self.early_exit_question()
        self.extra_cases()
        self.stability_demo()
        self.complexity_and_guidance()
        self.complete_java()
        recap = self.info_screen("Your turn to explain it", [
            "Search the unsorted suffix", "Remember the minimum's index",
            "Swap into start if needed", "Grow the fixed prefix; repeat",
        ])
        self.say(
            "Let me try: keep the smallest remaining value's index, finish the scan, then swap it into start if needed. Move start right and repeat. No early-exit shortcut, and equal name tags might trade places.",
            "Scan fully, place the minimum, grow the prefix.", "student", FadeIn(recap),
        )
        self.say("You've got it. One chosen minimum per pass. The searching does the work; the swap gets the applause.", "The scan proves the choice; the swap places it.", "robot")
        self.clear_stage(recap)
        self.play(FadeOut(Group(student, robot, self.title, self.caption_box, self.current_caption)), run_time=0.5)
        outro = create_character(SUBSCRIBE_IMAGE, 4.3).move_to([-3.4, -0.1, 0])
        message = VGroup(
            make_heading("Learn With Obscure", size=29),
            make_heading("LIKE   SUBSCRIBE", size=21, color=PURPLE),
            make_text("Keep asking why. Keep learning together.", size=17),
        ).arrange(DOWN, buff=0.35).move_to([2.4, 0, 0])
        self.speak(
            "If you can explain why a no-swap selection pass cannot stop the algorithm, you've understood more than just the code. Tell us your explanation, and subscribe to Learn With Obscure so we can tackle the next idea together.",
            "student", FadeIn(outro), FadeIn(message), run_time=0.9,
        )
        self.wait(0.5)
        review_path = os.getenv("LWO_REVIEW_TIMELINE")
        if review_path and not self.audio_prepare_mode:
            timeline_path = Path(review_path)
            timeline_path.parent.mkdir(parents=True, exist_ok=True)
            timeline_path.write_text(json.dumps(self.review_timeline, indent=2), encoding="utf-8")

