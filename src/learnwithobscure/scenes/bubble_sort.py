import hashlib
import json
from math import ceil
import os
from pathlib import Path
import wave

from manim import *
from manim_voiceover.services.gemini import GeminiService
from learnwithobscure.scenes.bubble_sort_trace import bubble_sort_events


BG = "#E6D9F2"
DARK = "#352044"
PURPLE = "#7B3FA1"
LAVENDER = "#A987C5"
PINK = "#FF75AC"
WHITE = "#FFFFFF"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = PROJECT_ROOT / "assets" / "characters"
STUDENT_IMAGE = ASSET_DIR / "student_chibi.png"
ROBOT_IMAGE = ASSET_DIR / "robot_mentor.png"
SUBSCRIBE_IMAGE = ASSET_DIR / "Chibi Creator\u2019s Subscribe Moment.png"
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
GEMINI_VOICES = {"student": "Achird", "robot": "Leda"}
AUDIO_DIR = PROJECT_ROOT / "media" / "audio_files" / "bubble_sort_demo"


def make_text(content, size=24, color=DARK, font="Arial", **kwargs):
    return Text(content, font=font, font_size=size, color=color, **kwargs)


def make_heading(content, size=30, color=DARK, **kwargs):
    return make_text(content, size=size, color=color, weight="BOLD", **kwargs)


def fit_within(mobject, width, height):
    """Preserve the chosen font size unless the content needs to shrink."""
    mobject.scale(min(1, width / mobject.width, height / mobject.height))
    return mobject


def create_character(image_path, height):
    if not image_path.exists():
        raise FileNotFoundError(f"Character artwork not found: {image_path}")
    image = ImageMobject(
        str(image_path),
        scale_to_resolution=1080,
        resampling_algorithm=RESAMPLING_ALGORITHMS["bicubic"],
    )
    image.scale_to_fit_height(height)
    return image


class AudioPreparationLimitReached(RuntimeError):
    """Raised before exceeding the configured TTS request budget."""


class BubbleSortDemo(Scene):
    """A narrated, character-led Bubble Sort lesson."""

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
                    "GEMINI_API_KEY is required when Bubble Sort narration is missing. "
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

    @staticmethod
    def comparison_frame(index, slot_x):
        return RoundedRectangle(
            width=2.1,
            height=0.96,
            corner_radius=0.1,
            stroke_color=PINK,
            stroke_width=3,
            fill_opacity=0,
        ).move_to([(slot_x[index] + slot_x[index + 1]) / 2, 1.05, 0])

    def review_mark(self, name, **details):
        """Record finished visual beats for frame-by-frame review."""
        self.review_timeline.append({"name": name, "time": self.time, **details})

    def visual_walkthrough(self, initial_values, value_cells, slot_x):
        compare_state = make_heading("One window, two neighboring values", size=18)
        compare_state.move_to([0, -0.1, 0])
        pass_state = make_text("Ascending order: smaller values go left.", size=15, color=PURPLE)
        pass_state.move_to([0, -0.72, 0])
        window = self.comparison_frame(0, slot_x)
        self.speak(
            "The pink window selects two neighboring values. Start with five and one. We will make one complete pass, moving the window from left to right.",
            "robot", Create(window), FadeIn(compare_state), FadeIn(pass_state),
            self.caption_transition("Zeno Sensei: The window selects the pair we compare."),
            run_time=1.0,
        )
        values = initial_values.copy()
        cells = value_cells.copy()
        swap_count = 0
        for index in range(len(values) - 1):
            if index:
                move_narration = (
                    "Now slide the window one place to the right." if index == 1 else
                    "One more move brings us to the last comparison." if index == len(values) - 2 else
                    "Carry on to the next pair."
                )
                self.speak(
                    move_narration, "robot",
                    Transform(window, self.comparison_frame(index, slot_x)),
                    Transform(compare_state, make_heading(f"Select positions {index} and {index + 1}", size=18).move_to(compare_state)),
                    Transform(pass_state, make_text("Check this pair before moving again.", size=15, color=PURPLE).move_to(pass_state)),
                    self.caption_transition("Zeno Sensei: Slide one position to the next neighboring pair."),
                    run_time=0.9,
                )
            left, right = values[index:index + 2]
            should_swap = left > right
            relation = ">" if should_swap else "<="
            if should_swap:
                compare_narration = (
                    f"Compare {left} and {right}. The left value is larger, so this pair is out of ascending order."
                    if index == 0 else
                    f"{left} is larger than {right} as well. Let's put this pair in order."
                    if index == 1 else
                    f"Here it is {left} and {right}. The same swap rule applies."
                )
            elif left == right:
                compare_narration = "These values are equal, so keep their original order."
            else:
                compare_narration = f"Now {left} is not larger than {right}. This pair already has the order we want."
            self.speak(
                compare_narration,
                "robot",
                Transform(compare_state, make_heading(
                    f"{left} {relation} {right}: {'swap' if should_swap else 'keep'}", size=18
                ).move_to(compare_state)),
                self.caption_transition(
                    f"Zeno Sensei: {left} {relation} {right}; {'swap this pair' if should_swap else 'keep this pair'}."
                ), run_time=0.75,
            )
            self.review_mark("visual_compare", pair=index, values=values.copy())
            if should_swap:
                swap_narration = (
                    "Swap these neighbors. The smaller value goes left, and the larger value goes right."
                    if swap_count == 0 else
                    f"That puts {right} before {left}. Notice how {left} keeps moving right."
                    if swap_count == 1 else
                    f"The same process puts {right} on the left, leaving {left} ready for the next comparison."
                )
                self.speak(
                    swap_narration,
                    "robot", Swap(cells[index], cells[index + 1], path_arc=PI / 2),
                    Transform(compare_state, make_heading("Swap the selected neighbors", size=18).move_to(compare_state)),
                    Transform(pass_state, make_text(
                        f"{right} goes left; {left} continues toward the right.", size=15, color=PURPLE
                    ).move_to(pass_state)),
                    self.caption_transition("Zeno Sensei: Swap the selected pair before moving the window."),
                    run_time=1.1,
                )
                values[index], values[index + 1] = right, left
                cells[index], cells[index + 1] = cells[index + 1], cells[index]
                swap_count += 1
                self.play(Transform(compare_state, make_heading(f"Pair now: {right}, {left}", size=18).move_to(compare_state)), run_time=0.35)
            else:
                self.speak(
                    "Keep both values where they are. A comparison does not always need a swap.",
                    "robot", Indicate(VGroup(cells[index], cells[index + 1]), color=LAVENDER),
                    Transform(pass_state, make_text("This pair stays in place.", size=15, color=PURPLE).move_to(pass_state)),
                    self.caption_transition("Zeno Sensei: Already in order, so no swap."), run_time=0.9,
                )
            self.review_mark("visual_pair_finished", pair=index, values=values.copy())

        self.speak(
            "The pass has checked every neighboring pair. Eight is the largest value, and its position at the right is now confirmed. The other values still need another pass.",
            "robot", FadeOut(window), cells[-1][0].animate.set_fill(PINK, opacity=0.24),
            Transform(compare_state, make_heading("Pass one complete: 8 is fixed", size=18).move_to(compare_state)),
            Transform(pass_state, make_text("Next pass: stop before the sorted end.", size=15, color=PURPLE).move_to(pass_state)),
            self.caption_transition("Zeno Sensei: 8 is fixed; the remaining values still need sorting."),
        )
        self.speak(
            "So we move through the row, swapping neighbors, and the large values settle at the end?",
            "student", self.caption_transition("Obscure: Neighboring swaps put the large values at the end?"),
        )
        self.speak(
            "Exactly. We've just finished one pass. Eight is fixed, so next time we can stop one position earlier.",
            "robot", Indicate(VGroup(*cells[:-1]), color=LAVENDER),
            self.caption_transition("Zeno Sensei: Yes. Fix the largest remaining value, then shorten the next pass."),
        )
        self.review_mark("visual_pass_complete", values=values.copy())
        return compare_state, pass_state

    def java_walkthrough(self, initial_values, title):
        """Animate each executed Java statement before advancing to the next."""
        slot_x = [-4.35, -3.25, -2.15, -1.05, 0.05]
        code_lines = [
            "for (int end = arr.length - 1; end > 0; end--) {",
            "    boolean swapped = false;",
            "    for (int i = 0; i < end; i++) {",
            "        if (arr[i] > arr[i + 1]) {",
            "            int temp = arr[i];",
            "            arr[i] = arr[i + 1];",
            "            arr[i + 1] = temp;",
            "            swapped = true;",
            "        }",
            "    }",
            "    if (!swapped) break;",
            "}",
        ]
        code_panel = RoundedRectangle(
            width=5.4, height=4.7, corner_radius=0.12,
            stroke_color=LAVENDER, stroke_width=2, fill_color=WHITE, fill_opacity=1,
        ).move_to([4.1, 0.7, 0])
        # Place indentation explicitly: aligning the glyph bounds of separate
        # Text objects would otherwise discard their leading spaces.
        char_width = Text("M" * 10, font="Consolas", font_size=16).width / 10
        code_group = VGroup()
        for line_index, line in enumerate(code_lines):
            indent = len(line) - len(line.lstrip())
            source_line = Text(line.lstrip(), font="Consolas", font_size=16, color=DARK, disable_ligatures=True)
            source_line.move_to([indent * char_width + source_line.width / 2, -0.34 * line_index, 0])
            code_group.add(source_line)
        fit_within(code_group, 4.9, 4.2)
        code_group.move_to(code_panel)

        def highlight_for(line_index):
            return SurroundingRectangle(
                code_group[line_index], buff=0.055, color=PINK, stroke_width=2,
                fill_color=PINK, fill_opacity=0.14,
            )

        current_highlight = highlight_for(0)
        boxes = VGroup(*[
            RoundedRectangle(
                width=0.88, height=0.76, corner_radius=0.1,
                stroke_color=PURPLE, stroke_width=2, fill_color=WHITE, fill_opacity=1,
            ).move_to([x, 1.05, 0]) for x in slot_x
        ])
        numbers = [make_heading(str(value), size=25).move_to(boxes[index]) for index, value in enumerate(initial_values)]
        indices = VGroup(*[
            make_text(str(index), size=14, color=PURPLE).move_to([x, 0.48, 0])
            for index, x in enumerate(slot_x)
        ])
        pass_label = make_heading("Trace the same input in Java", size=17, color=PURPLE).move_to([-2.15, 2.65, 0])
        compare_state = make_heading("One highlighted line, one action", size=18).move_to([-2.15, -0.1, 0])
        operation = make_text("Watch the array and the helper variables.", size=15).move_to([-2.15, -2.25, 0])
        i_badge = make_text("i = -", size=15, color=PURPLE).move_to([-4.1, -0.75, 0])
        end_badge = make_text("end = -", size=15, color=PURPLE).move_to([-2.5, -0.75, 0])
        flag_badge = make_text("swapped = -", size=15, color=PURPLE).move_to([-0.6, -0.75, 0])
        temp_box = RoundedRectangle(
            width=1.15, height=0.65, corner_radius=0.08,
            stroke_color=PINK, stroke_width=2, fill_color=WHITE, fill_opacity=1,
        ).move_to([-2.15, -1.45, 0])
        temp_label = make_text("temp", size=16, color=PURPLE).next_to(temp_box, LEFT, buff=0.22)
        temp_value = make_heading("-", size=25, color=PINK).move_to(temp_box)

        def pointer(label, color, x, y):
            tip = Triangle(stroke_width=0, fill_color=color, fill_opacity=1).scale(0.07).rotate(PI)
            return VGroup(make_heading(label, size=14, color=color), tip).arrange(DOWN, buff=0.05).move_to([x, y, 0])

        i_pointer = pointer("i", PINK, slot_x[0], 1.84)
        end_pointer = pointer("end", PURPLE, slot_x[-1], 2.28)
        window = self.comparison_frame(0, slot_x)
        window_visible = i_visible = end_visible = False
        displayed_values = initial_values.copy()
        active_line = 0

        self.play(
            FadeIn(code_panel), FadeIn(code_group), FadeIn(current_highlight),
            FadeIn(boxes), FadeIn(VGroup(*numbers)), FadeIn(indices),
            FadeIn(pass_label), FadeIn(compare_state), FadeIn(operation),
            FadeIn(i_badge), FadeIn(end_badge), FadeIn(flag_badge),
            FadeIn(temp_box), FadeIn(temp_label), FadeIn(temp_value),
            title.animate.move_to([-2.15, 3.2, 0]), run_time=0.8,
        )
        self.speak(
            "Let's replay the same input with the Java code. First we highlight a line, then show exactly what that line changes. During a swap, watch temp and the two separate array assignments.",
            "robot", self.caption_transition("Zeno Sensei: Follow the highlighted line, then its exact effect."),
        )

        # Explain each operation fully once. Later repetitions retain their
        # own highlight, numeric caption, animation and settled reading pause.
        narrated_steps = set()
        contextual_narration = {
            ("outer_check", 2, None): "This time the range is shorter. Eight is already fixed, so we leave it alone.",
            ("outer_check", 3, None): "Let's check the order once more, with a fresh flag for this pass.",
            ("compare", 1, 1): "Five is larger again. We'll use the same three assignments for this pair.",
            ("compare", 1, 2): "Five also needs to move past two. Follow those assignments once more.",
            ("compare", 1, 3): "Five doesn't exceed eight, so skip the swap block. The flag stays true because earlier swaps still count.",
            ("compare", 2, 0): "One is already before four. We can leave these two where they are.",
            ("compare", 2, 1): "Four is greater than two. Let's apply the same assignments to this pair.",
            ("compare", 2, 2): "Four and five are in order as well.",
            ("compare", 3, 0): "One is not greater than two. No exchange here.",
            ("compare", 3, 1): "Two is not greater than four either. Still no changes.",
            ("inner_check", 3, 2): "We've reached the boundary without making a swap.",
        }

        def step(event, narration, caption, description, *animations, run_time=0.9):
            nonlocal active_line
            # Establish the active statement before changing its operands.
            if event.line_index is not None and event.line_index != active_line:
                self.play(Transform(current_highlight, highlight_for(event.line_index)), run_time=0.3)
                active_line = event.line_index
            actions = [*animations,
                Transform(operation, make_text(description, size=15).move_to(operation)),
                self.caption_transition("Zeno Sensei: " + caption),
            ]
            key = (event.kind, event.condition)
            chosen_narration = contextual_narration.get((event.kind, event.pass_number, event.i))
            if chosen_narration is None and key not in narrated_steps:
                chosen_narration = narration
            narrated_steps.add(key)
            if chosen_narration:
                self.speak(chosen_narration, "robot", *actions, run_time=run_time)
            else:
                self.play(*actions, run_time=run_time)
                self.wait(0.75)

        def copy_number(event, source, destination, value, color, narration, caption, description, context_heading=None):
            target = make_heading(str(value), size=25, color=color).move_to(destination)
            actions = [FadeOut(destination), TransformFromCopy(source, target, path_arc=-PI / 4)]
            if context_heading:
                actions.append(Transform(compare_state, make_heading(context_heading, size=18).move_to(compare_state)))
            step(
                event, narration, caption, description,
                *actions, run_time=1.15,
            )
            # Keep a fixed mobject for each array slot; only its glyph changes.
            self.remove(target)
            destination.become(target)
            self.add(destination)

        def discuss_swapped_flag(event):
            """Pause at the evaluated early-exit line; no code/data advances."""
            obscure = create_character(STUDENT_IMAGE, 1.3).move_to([-5.75, -2.6, 0])
            zeno = create_character(ROBOT_IMAGE, 1.3).move_to([5.75, -2.6, 0])
            self.review_mark("swapped_dialogue_start", values=list(event.values), swapped=event.swapped)
            self.play(
                FadeIn(obscure), FadeIn(zeno),
                Transform(compare_state, make_heading("Already ordered. Why continue?", size=18).move_to(compare_state)),
                run_time=0.4,
            )
            self.speak(
                "It already looks sorted. Why are we checking again?", "student",
                self.caption_transition("Obscure: It's sorted already. Why check again?"),
            )
            self.speak(
                "It is sorted. But we exchanged four and two in this pass, so swapped is still true. True only means something changed; it doesn't mean the row is still out of order.",
                "robot", Indicate(flag_badge, color=PURPLE),
                self.caption_transition("Zeno Sensei: True records a swap; it doesn't prove disorder remains."),
            )
            self.speak(
                "Could we just sort without that flag?", "student",
                self.caption_transition("Obscure: Can we sort without the flag?"),
            )
            self.speak(
                "Yes. Remove the flag and its early-exit check, and the shrinking loops can still run all n minus one passes. The flag is an optimization: if a whole pass leaves it false, we know we're done and can skip the rest.",
                "robot", self.caption_transition("Zeno Sensei: The flag saves work by allowing an early exit."),
            )
            self.speak(
                "So the comparison chooses the swaps, and the flag helps us stop early?", "student",
                self.caption_transition("Obscure: The comparison chooses swaps; the flag enables early exit?"),
            )
            self.speak(
                "That's it. Let's see what the next pass tells us.", "robot",
                self.caption_transition("Zeno Sensei: Exactly. Watch whether the next pass changes anything."),
            )
            self.play(FadeOut(Group(obscure, zeno)), run_time=0.4)
            self.review_mark("swapped_dialogue_end", values=list(event.values), swapped=event.swapped)

        for event in bubble_sort_events(initial_values):
            kind = event.kind
            event_start = self.time
            if kind == "outer_init":
                step(event, "Set end to the last array index.", f"end = {event.end}: the last unsorted position.",
                     f"end = {len(initial_values)} - 1 = {event.end}",
                     Transform(compare_state, make_heading("Set the unsorted boundary", size=18).move_to(compare_state)),
                     Transform(end_badge, make_text(f"end = {event.end}", size=15, color=PURPLE).move_to(end_badge)),
                     FadeIn(end_pointer))
                end_visible = True
            elif kind == "outer_check":
                step(event, "The outer loop continues while end is greater than zero." if event.condition else "The boundary has reached zero, so the outer loop ends.",
                     f"end > 0: {str(event.condition).lower()}.", f"{event.end} > 0 is {str(event.condition).lower()}",
                     Transform(compare_state, make_heading(f"Outer loop: end = {event.end}", size=18).move_to(compare_state)),
                     Transform(pass_label, make_heading(f"Pass {event.pass_number}", size=17, color=PURPLE).move_to(pass_label)))
            elif kind == "reset_swapped":
                step(event, "Start this pass with swapped set to false.", "Reset the flag for this pass.",
                     "swapped = false",
                     Transform(compare_state, make_heading("Start a fresh pass", size=18).move_to(compare_state)),
                     Transform(flag_badge, make_text("swapped = false", size=15, color=PURPLE).move_to(flag_badge)))
            elif kind == "inner_init":
                actions = [Transform(i_badge, make_text("i = 0", size=15, color=PURPLE).move_to(i_badge))]
                if i_visible:
                    actions.append(i_pointer.animate.move_to([slot_x[0], 1.84, 0]))
                else:
                    i_pointer.move_to([slot_x[0], 1.84, 0])
                    actions.append(FadeIn(i_pointer))
                    i_visible = True
                step(event, "Start i at zero, the first position.", "i = 0: start at the left.", "Initialize i = 0", *actions,
                     Transform(compare_state, make_heading("Start at the first position", size=18).move_to(compare_state)))
            elif kind == "inner_check":
                if event.condition:
                    if window_visible:
                        action = Transform(window, self.comparison_frame(event.i, slot_x))
                    else:
                        window.become(self.comparison_frame(event.i, slot_x))
                        action = FadeIn(window)
                        window_visible = True
                    step(event, "i is before end, so we can compare this neighboring pair.",
                         f"{event.i} < {event.end}: true. Select positions {event.i} and {event.i + 1}.",
                         f"Check i < end: {event.i} < {event.end} is true", action,
                         Transform(compare_state, make_heading(f"Select positions {event.i} and {event.i + 1}", size=18).move_to(compare_state)))
                else:
                    actions = [FadeOut(window)] if window_visible else []
                    step(event, "i has reached end. This pass has no more pairs to check.",
                         f"{event.i} < {event.end}: false. Leave the inner loop.",
                         f"Check i < end: {event.i} < {event.end} is false", *actions,
                         Transform(compare_state, make_heading("No more pairs in this pass", size=18).move_to(compare_state)))
                    window_visible = False
            elif kind == "compare":
                left, right = displayed_values[event.i:event.i + 2]
                result = str(event.condition).lower()
                step(event,
                     "The left value is larger. Enter the swap block." if event.condition else "The left value is not larger. Skip the swap block.",
                     f"{left} > {right}: {result}. {'Enter' if event.condition else 'Skip'} the swap block.",
                     f"arr[{event.i}] > arr[{event.i + 1}]\n{left} > {right} is {result}",
                     Transform(compare_state, make_heading(f"{left} > {right}: {result}", size=18).move_to(compare_state)))
            elif kind == "save_temp":
                copy_number(event, numbers[event.i], temp_value, event.temp, PINK,
                            "Save the left value in temp. The array has not changed yet.",
                            f"temp = arr[{event.i}]: save {event.temp}.",
                            f"temp = arr[{event.i}]\nSave {event.temp}; leave both array slots unchanged",
                            context_heading="Swap block: earlier check was true")
            elif kind == "assign_left":
                value = event.values[event.i]
                copy_number(event, numbers[event.i + 1], numbers[event.i], value, DARK,
                            "Copy the right value into the left slot. Temp keeps the original left value safe.",
                            f"arr[{event.i}] = arr[{event.i + 1}]: copy {value} left.",
                            f"arr[{event.i}] = arr[{event.i + 1}]\nBoth slots now show {value}; temp still holds {event.temp}")
                displayed_values[event.i] = value
            elif kind == "assign_right":
                value = event.values[event.i + 1]
                copy_number(event, temp_value, numbers[event.i + 1], value, DARK,
                            "Copy temp into the right slot. Now the pair is in ascending order.",
                            f"arr[{event.i + 1}] = temp: restore {value} on the right.",
                            f"arr[{event.i + 1}] = temp\nThe pair is now {event.values[event.i]}, {value}")
                displayed_values[event.i + 1] = value
            elif kind == "mark_swapped":
                step(event, "Set swapped to true to record that this pass changed a pair.",
                     "swapped = true: this pass made a change.", "swapped = true",
                     Transform(flag_badge, make_text("swapped = true", size=15, color=PINK).move_to(flag_badge)))
            elif kind == "inner_increment":
                actions = [
                    Transform(compare_state, make_heading("Advance i, then check end", size=18).move_to(compare_state)),
                    Transform(i_badge, make_text(f"i = {event.i}", size=15, color=PURPLE).move_to(i_badge)),
                    i_pointer.animate.move_to([slot_x[event.i], 1.84, 0]),
                ]
                if window_visible:
                    actions.append(window.animate.set_stroke(opacity=0.3))
                # The local temp has left scope; this is not an extra Java assignment.
                if event.temp is None:
                    actions.append(Transform(temp_value, make_heading("-", size=25, color=PINK).move_to(temp_box)))
                step(event, "Increase i by one, then check the loop condition again.",
                     f"i++: i becomes {event.i}. Check i < end next.",
                     f"i++: {event.i - 1} becomes {event.i}", *actions)
            elif kind == "pass_complete":
                actions = [box.animate.set_fill(PINK, opacity=0.24) for box in boxes[event.sorted_from:]]
                actions.append(Transform(i_badge, make_text("i = -", size=15, color=PURPLE).move_to(i_badge)))
                actions.append(Transform(compare_state, make_heading(f"Pass {event.pass_number}: {event.values[event.end]} is fixed", size=18).move_to(compare_state)))
                if i_visible:
                    actions.append(FadeOut(i_pointer))
                    i_visible = False
                self.play(*actions, run_time=0.6)
            elif kind == "early_exit_check":
                step(event,
                     "The flag stayed false for the entire pass." if event.condition else "A swap happened, so this check cannot stop early. The outer loop will decide whether another pass runs.",
                     f"!swapped is {str(event.condition).lower()}: {'take break' if event.condition else 'continue'}.",
                     f"if (!swapped): {str(event.condition).lower()}",
                     Transform(compare_state, make_heading("Did this pass make any swaps?", size=18).move_to(compare_state)),
                     Indicate(flag_badge, color=PURPLE))
                if event.pass_number == 2 and not event.condition and event.end > 1 and event.values == tuple(sorted(initial_values)):
                    discuss_swapped_flag(event)
            elif kind == "break":
                step(event, "That proves no out-of-order neighbors remain. Break stops the loop here.",
                     "break: the no-swap pass proves the array is sorted.", "break exits the outer loop",
                     Transform(compare_state, make_heading("No swaps: the array is sorted", size=18, color=PURPLE).move_to(compare_state)),
                     *[box.animate.set_fill(PINK, opacity=0.24) for box in boxes])
            elif kind == "outer_decrement":
                step(event, "Move end one position left to skip the value that is now fixed.",
                     f"end--: end becomes {event.end}; skip the fixed value.", f"end--: end becomes {event.end}",
                     Transform(end_badge, make_text(f"end = {event.end}", size=15, color=PURPLE).move_to(end_badge)),
                     Transform(flag_badge, make_text("swapped = -", size=15, color=PURPLE).move_to(flag_badge)),
                     Transform(compare_state, make_heading("Shorten the unsorted range", size=18).move_to(compare_state)),
                     end_pointer.animate.move_to([slot_x[event.end], 2.28, 0]))
            elif kind == "done":
                actions = [
                    Transform(compare_state, make_heading("Sorted in ascending order", size=18, color=PURPLE).move_to(compare_state)),
                    Transform(end_badge, make_text("end = -", size=15, color=PURPLE).move_to(end_badge)),
                    Transform(flag_badge, make_text("swapped = -", size=15, color=PURPLE).move_to(flag_badge)),
                ]
                if end_visible:
                    actions.append(FadeOut(end_pointer))
                    end_visible = False
                self.play(*actions, run_time=0.6)
            else:
                raise AssertionError(f"Unrendered Java event: {kind}")
            if tuple(displayed_values) != event.values:
                raise AssertionError(f"Visible array disagrees with Java at {kind}: {displayed_values} != {event.values}")
            if not self.audio_prepare_mode:
                def same_position(actual, expected):
                    return all(abs(a - b) < 1e-5 for a, b in zip(actual, expected))

                if event.line_index is not None and not same_position(current_highlight.get_center(), code_group[event.line_index].get_center()):
                    raise AssertionError(f"Code highlight is out of sync at {kind}")
                for index, number in enumerate(numbers):
                    if not same_position(number.get_center(), boxes[index].get_center()):
                        raise AssertionError(f"Array slot {index} moved during {kind}")
                if i_visible and event.i is not None and abs(i_pointer.get_x() - slot_x[event.i]) > 1e-5:
                    raise AssertionError(f"i pointer is out of sync at {kind}")
                if end_visible and abs(end_pointer.get_x() - slot_x[event.end]) > 1e-5:
                    raise AssertionError(f"end pointer is out of sync at {kind}")
            self.review_mark(
                "java_step", kind=kind, line=event.line_index, values=list(event.values),
                temp=event.temp, swapped=event.swapped, i=event.i, end=event.end,
                start=event_start, sample=max(event_start, self.time - 0.2),
            )

        self.wait(1)
        outgoing = [boxes, *numbers, indices, code_panel, code_group, current_highlight,
                    pass_label, compare_state, operation, i_badge, end_badge, flag_badge,
                    temp_box, temp_label, temp_value]
        if window_visible:
            outgoing.append(window)
        if i_visible:
            outgoing.append(i_pointer)
        if end_visible:
            outgoing.append(end_pointer)
        self.play(FadeOut(VGroup(*outgoing)), title.animate.move_to([0, 3.2, 0]), run_time=0.7)

    def construct(self):
        self.camera.background_color = BG
        title = make_heading("Bubble Sort", size=40).move_to([0, 3.2, 0])
        subtitle = make_text(
            "Ascending order: smallest to largest", size=19, color=PURPLE
        ).move_to([0, 2.65, 0])
        student = create_character(STUDENT_IMAGE, 2.45).move_to([-5.25, -1.78, 0])
        robot = create_character(ROBOT_IMAGE, 2.4).move_to([5.25, -1.78, 0])

        initial_values = [5, 1, 4, 2, 8]
        # Use the full stage for the visual explanation. The Java trace later
        # restores the left-hand layout to make room for its code panel.
        slot_x = [-2.2, -1.1, 0, 1.1, 2.2]
        value_cells = []
        index_labels = VGroup()
        for index, value in enumerate(initial_values):
            box = RoundedRectangle(
                width=0.88,
                height=0.76,
                corner_radius=0.1,
                stroke_color=PURPLE,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            )
            number = make_heading(str(value), size=25)
            cell = VGroup(box, number).move_to([slot_x[index], 1.05, 0])
            value_cells.append(cell)
            index_labels.add(
                make_text(str(index), size=14, color=PURPLE).move_to([slot_x[index], 0.48, 0])
            )

        self.caption_box = RoundedRectangle(
            width=8.5,
            height=0.72,
            corner_radius=0.14,
            stroke_color=PURPLE,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to([0, -3.22, 0])
        self.current_caption = self.caption_line(
            "Obscure: I want to sort this array of numbers."
        )
        self.play(
            LaggedStart(*[FadeIn(cell) for cell in value_cells], lag_ratio=0.12),
            FadeIn(index_labels),
            FadeIn(student, shift=UP * 0.15),
            FadeIn(robot, shift=UP * 0.15),
            FadeIn(self.caption_box),
            FadeIn(self.current_caption),
            run_time=0.9,
        )
        self.speak(
            "Zeno Sensei, I want to sort this array of numbers. Do I need to copy these numbers into another array and compare them again and again until they are sorted?",
            "student",
            self.caption_transition("Obscure: Do we need another array and repeated comparisons?"),
        )
        self.speak(
            "No extra array is needed. Bubble Sort rearranges these values in place. We will sort in ascending order, from smallest to largest. It compares neighbors and swaps them only when they are out of order. Let's watch the values move before we look at code.",
            "robot",
            # The cached narration names Bubble Sort after its first sentence.
            Succession(
                Wait(2.45),
                AnimationGroup(
                    FadeIn(title, shift=DOWN * 0.1),
                    FadeIn(subtitle),
                    run_time=0.55,
                ),
            ),
            self.caption_transition("Zeno Sensei: Ascending order means smallest to largest."),
            run_time=3.0,
        )

        compare_state, pass_state = self.visual_walkthrough(initial_values, value_cells, slot_x)

        order_title = make_heading("The comparison chooses the order", size=22).move_to([0, 2.05, 0])
        ascending_panel = RoundedRectangle(
            width=5.6,
            height=2.55,
            corner_radius=0.12,
            stroke_color=LAVENDER,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to([-2.9, 0.2, 0])
        descending_panel = RoundedRectangle(
            width=5.6,
            height=2.55,
            corner_radius=0.12,
            stroke_color=PINK,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to([2.9, 0.2, 0])
        ascending_content = VGroup(
            make_heading("Ascending", size=20, color=PURPLE),
            make_text("1 < 2 < 4 < 5 < 8", size=18, color=DARK),
            make_text("Swap if left > right", size=17, color=DARK),
        ).arrange(DOWN, buff=0.24).move_to(ascending_panel)
        descending_content = VGroup(
            make_heading("Descending", size=20, color=PINK),
            make_text("8 > 5 > 4 > 2 > 1", size=18, color=DARK),
            make_text("Swap if left < right", size=17, color=DARK),
        ).arrange(DOWN, buff=0.24).move_to(descending_panel)
        order_group = VGroup(
            order_title,
            ascending_panel,
            descending_panel,
            ascending_content,
            descending_content,
        )
        self.play(
            FadeOut(Group(
                *value_cells, index_labels, compare_state, pass_state, student, robot
            )),
            run_time=0.55,
        )
        self.speak(
            "For descending order, reverse the comparison: swap when the left value is smaller than the right. Each left-to-right pass then fixes the smallest remaining value at the right.",
            "robot",
            FadeIn(order_group),
            self.caption_transition("Zeno Sensei: For descending, swap when left < right."),
        )
        self.speak(
            "So the algorithm stays the same, and we just reverse the comparison?",
            "student",
            self.caption_transition("Obscure: Same passes, but reverse the comparison?"),
        )
        self.speak(
            "That's right. Everything else works the same way. Let's use the ascending version for the Java walkthrough.",
            "robot",
            Indicate(descending_content, color=PINK),
            self.caption_transition("Zeno Sensei: Only the comparison changes."),
        )
        self.play(FadeOut(order_group), FadeOut(subtitle), run_time=0.45)
        self.java_walkthrough(initial_values, title)

        summary_title = make_heading("Bubble Sort Complexity", size=28).move_to([0, 1.9, 0])
        summary_lines = VGroup(
            make_heading("Average and worst time: O(n^2)", size=20, color=DARK),
            make_heading("Best time with early exit: O(n)", size=20, color=DARK),
            make_heading("Auxiliary space: O(1)", size=20, color=DARK),
            make_text("In-place and stable; often slow on large inputs.", size=17, color=PURPLE),
        ).arrange(DOWN, buff=0.38).move_to([0, -0.05, 0])
        summary_group = VGroup(summary_title, summary_lines)
        self.speak(
            "Let's look at Bubble Sort's time and space complexity. Average and worst-case time are O of n squared. With an early-exit check, best-case time is O of n. Extra space is O of one.",
            "robot",
            FadeIn(summary_group, shift=UP * 0.1),
            self.caption_transition("Zeno Sensei: The early-exit version improves the already-sorted case."),
        )

        time_detail_title = make_heading("Why can the worst case be O(n^2)?", size=27).move_to([0, 2.0, 0])
        time_formula = make_heading("(n - 1) + ... + 1 = n(n - 1) / 2", size=22, color=PURPLE).move_to([0, 0.8, 0])
        time_explanation = make_text(
            "Each pass checks the remaining unsorted neighbors.\nThe number of comparisons grows proportionally to n squared.",
            size=19,
            color=DARK,
            line_spacing=1.25,
        ).move_to([0, -0.45, 0])
        best_case_note = make_text(
            "Already sorted: n - 1 checks with early exit.\nWithout early exit: n(n - 1) / 2 checks.",
            size=16,
            color=PURPLE,
            line_spacing=1.2,
        ).move_to([0, -1.55, 0])
        time_group = VGroup(time_detail_title, time_formula, time_explanation, best_case_note)
        self.play(FadeOut(summary_group), run_time=0.4)
        self.speak(
            "Those shrinking passes can make n minus one, plus n minus two, down to one comparisons. That totals n times n minus one over two, so the worst case is quadratic. With the swapped flag, already sorted input needs just one pass, or n minus one comparisons. Without that early exit, even sorted input would go through the full quadratic count.",
            "robot",
            FadeIn(time_group),
            self.caption_transition("Zeno Sensei: Worst case O(n^2); an already sorted input can stop in O(n)."),
        )

        space_title = make_heading("Why is the extra space O(1)?", size=27).move_to([0, 2.0, 0])
        input_label = make_text("The input array is rearranged in place", size=20, color=PURPLE).move_to([0, 1.1, 0])
        swap_values = VGroup(
            make_heading("left", size=22),
            make_heading("right", size=22),
            make_heading("one temporary value", size=22, color=PINK),
        ).arrange(RIGHT, buff=0.8).move_to([0, 0.1, 0])
        space_explanation = make_text(
            "One temporary value, loop indices, and a flag.\nThe number of helper variables stays fixed.",
            size=18,
            color=DARK,
            line_spacing=1.25,
        ).move_to([0, -0.85, 0])
        space_formula = make_heading("Auxiliary space: O(1)", size=26, color=PURPLE).move_to([0, -1.75, 0])
        space_group = VGroup(space_title, input_label, swap_values, space_explanation, space_formula)
        self.play(FadeOut(time_group), run_time=0.4)
        self.speak(
            "A swap uses one temporary value. The loop indices and a flag also need only a fixed amount of storage. Their memory use does not grow with the input size, so auxiliary space is O of one.",
            "robot",
            FadeIn(space_group),
            self.caption_transition("Zeno Sensei: We sort in place with one temporary value."),
        )

        pros_title = make_heading("When should we use Bubble Sort?", size=27).move_to([0, 2.0, 0])
        pros_panel = RoundedRectangle(
            width=5.1, height=2.65, corner_radius=0.12,
            stroke_color=LAVENDER, stroke_width=2,
            fill_color=WHITE, fill_opacity=1,
        ).move_to([-3.0, 0.25, 0])
        cons_panel = RoundedRectangle(
            width=5.1, height=2.65, corner_radius=0.12,
            stroke_color=PINK, stroke_width=2,
            fill_color=WHITE, fill_opacity=1,
        ).move_to([3.0, 0.25, 0])
        pros_text = VGroup(
            make_heading("Advantages", size=20, color=PURPLE),
            make_text("Simple to understand and implement\nSorts in place; stable\nCan stop early when already sorted", size=15),
        ).arrange(DOWN, buff=0.28).move_to(pros_panel)
        cons_text = VGroup(
            make_heading("Limitations", size=20, color=PINK),
            make_text("Average and worst time are O(n^2)\nMany comparisons and swaps\nPoor choice for large inputs", size=15),
        ).arrange(DOWN, buff=0.28).move_to(cons_panel)
        use_case = make_text(
            "Useful for learning and tiny lists.\nNearly sorted inputs can still take O(n^2).",
            size=16,
            color=DARK,
            line_spacing=1.2,
        ).move_to([0, -1.55, 0])
        guidance_group = VGroup(pros_title, pros_panel, cons_panel, pros_text, cons_text, use_case)
        self.speak(
            "Bubble Sort is so simple and it sorts in place. Why not use it for every list?",
            "student",
            self.caption_transition("Obscure: If it's simple, why not use it every time?"),
        )
        self.play(FadeOut(space_group), run_time=0.4)
        self.speak(
            "Because all those passes add up. A small value at the far right can move left only one position per pass, even if the rest is ordered. Average and worst-case time are quadratic. It's a good learning tool for tiny lists, but for larger applications, use a more efficient sort.",
            "robot",
            FadeIn(guidance_group),
            self.caption_transition("Zeno Sensei: Great for learning and tiny inputs, not large lists."),
        )

        java_pages = [
            [
                "public static void bubbleSort(int[] arr) {",
                "    int n = arr.length;",
                "    for (int end = n - 1; end > 0; end--) {",
                "        boolean swapped = false;",
                "        for (int i = 0; i < end; i++) {",
                "            if (arr[i] > arr[i + 1]) {",
                "                int temp = arr[i];",
                "                arr[i] = arr[i + 1];",
                "                arr[i + 1] = temp;",
                "                swapped = true;",
                "            }",
                "        }",
                "        if (!swapped) break;",
                "    }",
                "}",
            ],
            [
                "int[] numbers = {5, 1, 4, 2, 8};",
                "bubbleSort(numbers);",
                "",
                "for (int value : numbers) {",
                "    System.out.print(value + \" \");",
                "}",
                "",
                "// Output: 1 2 4 5 8",
            ],
        ]
        code_titles = ["Java implementation", "Run the example"]
        sources = [
            Text(
                "\n".join(lines), font="Consolas", font_size=19,
                line_spacing=0.82, color=DARK, disable_ligatures=True,
            )
            for lines in java_pages
        ]
        # Both pages use the same scale, including the shorter output example.
        source_scale = min(
            1, *(10.8 / source.width for source in sources),
            *(3.15 / source.height for source in sources),
        )
        for source in sources:
            source.scale(source_scale)
        code_objects = None
        for page_index, lines in enumerate(java_pages):
            page_title = make_heading(code_titles[page_index], size=27).move_to([0, 2.05, 0])
            panel = RoundedRectangle(
                width=11.6,
                height=3.7,
                corner_radius=0.12,
                stroke_color=LAVENDER,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1,
            ).move_to([0, -0.3, 0])
            source = sources[page_index]
            source.move_to(panel.get_center())
            page_label = make_text("Bubble Sort in Java", size=14, color=PURPLE).move_to([0, -2.35, 0])
            new_objects = VGroup(page_title, panel, source, page_label)
            if code_objects is None:
                self.play(FadeOut(guidance_group), run_time=0.45)
                self.play(FadeIn(new_objects), run_time=0.65)
                self.speak(
                    "Here's the complete method, with the same boundaries, swap, and early exit we've just followed.",
                    "robot",
                    self.caption_transition("Zeno Sensei: The swapped flag lets a pass stop early."),
                )
            else:
                self.play(FadeOut(code_objects), run_time=0.4)
                self.play(FadeIn(new_objects), run_time=0.55)
                self.speak(
                    "This small example sorts the numbers in place. Its output is one, two, four, five, eight.",
                    "robot",
                    self.caption_transition("Zeno Sensei: The sorted output is 1, 2, 4, 5, 8."),
                )
            code_objects = new_objects

        closing_caption = self.caption_transition(
            "Obscure: Thank you, Zeno Sensei, for teaching me Bubble Sort!"
        )
        self.play(FadeOut(code_objects), run_time=0.4)
        self.speak(
            "Thank you, Zeno Sensei, for teaching me Bubble Sort!",
            "student",
            FadeIn(student, shift=UP * 0.12),
            FadeIn(robot, shift=UP * 0.12),
            closing_caption,
            run_time=0.8,
        )
        self.speak(
            "You're welcome, Obscure!",
            "robot",
            self.caption_transition("Zeno Sensei: You're welcome, Obscure!"),
        )
        outro_image = create_character(SUBSCRIBE_IMAGE, 4.3).move_to([-3.3, -0.25, 0])
        outro_text = VGroup(
            make_heading("Learn With Obscure", size=29, color=DARK),
            make_heading("LIKE   SUBSCRIBE", size=20, color=PURPLE),
            make_text("Let's learn more concepts together.", size=17, color=DARK),
        ).arrange(DOWN, buff=0.35).move_to([2.35, 0, 0])
        self.play(
            FadeOut(Group(title, student, robot, self.caption_box, self.current_caption)),
            run_time=0.45,
        )
        self.speak(
            "Now I understand how Bubble Sort works! If this video helped you understand it too, please like and subscribe to Learn With Obscure, where we can learn more concepts together.",
            "student",
            FadeIn(outro_image),
            FadeIn(outro_text),
            run_time=0.9,
        )
        self.wait(0.5)
        review_path = os.getenv("LWO_REVIEW_TIMELINE")
        if review_path and not self.audio_prepare_mode:
            timeline_path = Path(review_path)
            timeline_path.parent.mkdir(parents=True, exist_ok=True)
            timeline_path.write_text(json.dumps(self.review_timeline, indent=2), encoding="utf-8")
