import hashlib
import os
from pathlib import Path
import wave

from manim import *
from manim_voiceover.services.gemini import GeminiService


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
        self.add_sound(str(audio_path))
        if animations:
            self.play(*animations, run_time=run_time, **play_kwargs)
            remaining_speech = speech_duration - run_time
            if remaining_speech > 0:
                self.wait(remaining_speech)
        else:
            self.wait(speech_duration)

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
            height=1.1,
            corner_radius=0.1,
            stroke_color=PINK,
            stroke_width=3,
            fill_opacity=0,
        ).move_to([(slot_x[index] + slot_x[index + 1]) / 2, 1.05, 0])

    def construct(self):
        self.camera.background_color = BG
        title = make_heading("Bubble Sort", size=40).move_to([0, 3.2, 0])
        subtitle = make_text(
            "Ascending order: smallest to largest", size=19, color=PURPLE
        ).move_to([0, 2.65, 0])
        student = create_character(STUDENT_IMAGE, 2.45).move_to([-5.25, -1.78, 0])
        robot = create_character(ROBOT_IMAGE, 2.4).move_to([5.25, -1.78, 0])
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
            "Obscure: Can we sort these numbers without copying the array?"
        )
        self.play(
            FadeIn(title, shift=DOWN * 0.1),
            FadeIn(subtitle),
            FadeIn(student, shift=UP * 0.15),
            FadeIn(robot, shift=UP * 0.15),
            FadeIn(self.caption_box),
            FadeIn(self.current_caption),
            run_time=0.9,
        )
        self.speak(
            "Zeno Sensei, do I need to copy these numbers into another array and compare them again and again until they are sorted?",
            "student",
            self.caption_transition("Obscure: Do we need another array and repeated comparisons?"),
        )
        self.speak(
            "No extra array is needed. Bubble Sort rearranges these values in place. We will sort in ascending order, from smallest to largest. It compares neighbors and swaps them only when they are out of order. Let's watch the values move before we look at code.",
            "robot",
            self.caption_transition("Zeno Sensei: Ascending order means smallest to largest."),
        )

        initial_values = [5, 1, 4, 2, 8]
        slot_x = [-4.35, -3.25, -2.15, -1.05, 0.05]
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

        compare_state = make_heading("Compare neighboring values", size=18, color=DARK)
        compare_state.move_to([-2.15, -0.1, 0])
        pass_state = make_text("Each pass moves a large value toward the right.", size=15, color=PURPLE)
        pass_state.move_to([-2.15, -0.72, 0])

        code_panel = RoundedRectangle(
            width=4.8,
            height=3.5,
            corner_radius=0.12,
            stroke_color=LAVENDER,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to([4.5, 1.45, 0])
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
        code_group = VGroup(*[
            Text(line, font="Consolas", font_size=14, color=DARK, disable_ligatures=True)
            for line in code_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.17)
        fit_within(code_group, 4.25, 3.05)
        code_group.move_to(code_panel.get_center())
        current_highlight = SurroundingRectangle(
            code_group[2], buff=0.06, color=PINK, stroke_width=1.5,
            fill_color=PINK, fill_opacity=0.16,
        )

        self.speak(
            "First, we look at one neighboring pair: five and one. The left value is larger, so the pair changes places.",
            "robot",
            LaggedStart(*[FadeIn(cell) for cell in value_cells], lag_ratio=0.12),
            FadeIn(index_labels),
            FadeIn(compare_state),
            FadeIn(pass_state),
            self.caption_transition("Zeno Sensei: Compare a neighboring pair."),
            run_time=1.4,
        )

        values = initial_values.copy()
        cells = value_cells.copy()

        def highlight_for(line_index):
            return SurroundingRectangle(
                code_group[line_index], buff=0.06, color=PINK, stroke_width=1.5,
                fill_color=PINK, fill_opacity=0.16,
            )

        introduction = [
            (
                "1. Start at the left and compare neighbors",
                "Start at the left edge and compare the first two neighboring values.",
                "Zeno Sensei: Start with the first neighboring pair.",
            ),
            (
                "2. Swap only when left is greater",
                "If the left value is larger, swap. Otherwise keep the pair in place. Five is larger than one, so they switch.",
                "Zeno Sensei: Swap only when the left value is bigger.",
            ),
            (
                "3. Move one position right and compare again",
                "Move one position to the right. The next pair shares a value with the previous pair.",
                "Zeno Sensei: Shift one place and compare the next pair.",
            ),
            (
                "4. Each pass places a large value at the end",
                "Continue to the end of the unsorted part. The largest remaining value moves right one place at a time.",
                "Zeno Sensei: The largest remaining value settles at the right.",
            ),
            (
                "5. Stop early if a pass makes no swaps",
                "Repeat on the remaining part. If a pass makes no swaps, the whole array is already sorted.",
                "Zeno Sensei: A pass with no swaps means we are done.",
            ),
        ]
        introduction_steps = VGroup()
        first_pair_frame = self.comparison_frame(0, slot_x)
        for step_index, (display_text, narration, caption_text) in enumerate(introduction):
            step = make_text(display_text, size=15, color=DARK)
            step.move_to([-2.15, -1.15 - step_index * 0.34, 0])
            introduction_steps.add(step)
            animations = [
                FadeIn(step, shift=RIGHT * 0.08),
                self.caption_transition(caption_text),
            ]
            if step_index == 0:
                animations.append(Create(first_pair_frame))
            elif step_index == 1:
                animations.append(Indicate(first_pair_frame, color=PINK))
            elif step_index == 2:
                animations.append(Indicate(VGroup(*value_cells[1:4]), color=LAVENDER))
            elif step_index == 4:
                animations.append(Indicate(value_cells[-1], color=PINK))
            self.speak(
                narration,
                "robot",
                *animations,
                run_time=0.75,
            )
        self.play(
            FadeOut(first_pair_frame),
            FadeOut(introduction_steps),
            self.caption_transition("Zeno Sensei: Now let's watch a complete pass."),
            run_time=0.45,
        )

        visual_values = values.copy()
        visual_cells = cells.copy()
        for index in range(len(visual_values) - 1):
            left_value, right_value = visual_values[index:index + 2]
            frame = self.comparison_frame(index, slot_x)
            if left_value > right_value:
                narration = (
                    f"Compare {left_value} with {right_value}. The left value is larger, so swap them in the same array. "
                    f"The pair becomes {right_value}, {left_value}."
                )
                visual_swap = AnimationGroup(
                    visual_cells[index].animate.move_to([slot_x[index + 1], 1.05, 0]),
                    visual_cells[index + 1].animate.move_to([slot_x[index], 1.05, 0]),
                )
                visual_values[index], visual_values[index + 1] = right_value, left_value
                visual_cells[index], visual_cells[index + 1] = (
                    visual_cells[index + 1], visual_cells[index]
                )
            else:
                narration = (
                    f"Compare {left_value} with {right_value}. They are already in order, "
                    "so we leave them where they are."
                )
                visual_swap = Indicate(VGroup(visual_cells[index], visual_cells[index + 1]))
            self.speak(
                narration,
                "robot",
                Create(frame),
                Transform(
                    compare_state,
                    make_heading(
                        f"Compare {left_value} and {right_value}", size=18
                    ).move_to(compare_state),
                ),
                visual_swap,
                self.caption_transition(
                        f"Zeno Sensei: {left_value} {'>' if left_value > right_value else '<='} {right_value}"
                        f"; {'swap' if left_value > right_value else 'keep the order'}."
                ),
                run_time=0.75,
            )
            self.play(FadeOut(frame), run_time=0.12)

        visual_sorted_cell = visual_cells[-1]
        self.speak(
            "After the first pass, eight has reached the end. We did not create another array; each comparison changed the same row of values.",
            "robot",
            visual_sorted_cell[0].animate.set_fill(PINK, opacity=0.24),
            Transform(
                pass_state,
                make_text("End of pass one: 8 is in its final position.", size=15, color=PURPLE)
                    .move_to(pass_state),
            ),
            self.caption_transition("Zeno Sensei: The largest value has bubbled to the end."),
        )
        self.speak(
            "So we move through the row, swapping neighbors, and the large values settle at the end?",
            "student",
            self.caption_transition("Obscure: One row, neighboring swaps, sorted values at the end?"),
        )

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
            "We are sorting in ascending order, from smallest to largest. The first pass fixed the largest value at the right; more passes sort the rest. For descending order, keep the same neighbors and passes, but swap when the left value is smaller than the right. Each left-to-right pass then places the smallest remaining value at the right.",
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
            "Exactly. Left greater than right gives ascending order; left less than right gives descending order. Now let's trace the ascending version in Java.",
            "robot",
            Indicate(descending_content, color=PINK),
            self.caption_transition("Zeno Sensei: Only the comparison changes."),
        )
        self.play(FadeOut(order_group), run_time=0.45)
        for index, cell in enumerate(value_cells):
            cell.move_to([slot_x[index], 1.05, 0])
            cell[0].set_fill(WHITE, opacity=1)
        values = initial_values.copy()
        cells = value_cells.copy()
        compare_state.become(make_heading("Start pass one", size=18, color=DARK).move_to(compare_state))
        pass_state.become(make_text("i moves through the unsorted portion.", size=15, color=PURPLE).move_to(pass_state))
        self.play(
            FadeIn(VGroup(*value_cells)),
            FadeIn(index_labels),
            FadeIn(compare_state),
            FadeIn(pass_state),
            FadeIn(code_panel),
            FadeIn(code_group),
            FadeIn(current_highlight),
            FadeOut(subtitle),
            run_time=0.7,
        )
        self.speak(
            "Before each pass, swapped starts false. The outer loop moves end left each time, so we skip values already fixed at the right side.",
            "robot",
            Transform(current_highlight, highlight_for(0)),
            Indicate(code_group[1], color=PURPLE),
            self.caption_transition("Zeno Sensei: Each pass shortens the unsorted range."),
        )
        self.speak(
            "The loop moves i from the left toward end, the last index that is still unsorted. That is why each comparison uses i and i plus one.",
            "robot",
            Transform(current_highlight, highlight_for(2)),
            self.caption_transition("Zeno Sensei: i and i + 1 identify neighboring positions."),
        )
        self.speak(
            "This snippet checks each adjacent pair. The condition compares the left value with the one after it; only an out-of-order pair enters the swap block.",
            "robot",
            Transform(current_highlight, highlight_for(3)),
            self.caption_transition("Zeno Sensei: The condition decides whether this pair needs swapping."),
        )

        def run_pass(pass_number, comparison_count, narration, caption_text):
            if self.voiceover_disabled:
                speech_duration = 0
            else:
                audio_path, speech_duration = self.make_narration_audio(narration, "robot")
                if not self.audio_prepare_mode:
                    self.add_sound(str(audio_path))

            elapsed = 0
            swapped_this_pass = False
            for index in range(comparison_count):
                left_value, right_value = values[index], values[index + 1]
                should_swap = left_value > right_value
                comparison = (
                    f"{left_value} > {right_value}: swap"
                    if should_swap else f"{left_value} <= {right_value}: keep order"
                )
                frame = self.comparison_frame(index, slot_x)
                if not self.audio_prepare_mode:
                    self.play(
                        Create(frame),
                        Transform(current_highlight, highlight_for(3)),
                        Transform(
                            compare_state,
                            make_heading(comparison, size=18).move_to(compare_state),
                        ),
                        self.caption_transition(caption_text),
                        run_time=0.4,
                    )
                    elapsed += 0.4
                if should_swap:
                    left_cell, right_cell = cells[index], cells[index + 1]
                    if not self.audio_prepare_mode:
                        self.play(
                            Succession(
                                AnimationGroup(
                                    Transform(current_highlight, highlight_for(4)),
                                    run_time=0.25,
                                ),
                                AnimationGroup(
                                    Transform(current_highlight, highlight_for(5)),
                                    left_cell.animate.move_to([slot_x[index + 1], 1.05, 0]),
                                    right_cell.animate.move_to([slot_x[index], 1.05, 0]),
                                    run_time=0.55,
                                ),
                                AnimationGroup(
                                    Transform(current_highlight, highlight_for(6)),
                                    Transform(
                                        pass_state,
                                        make_text(
                                            f"temp = {left_value}; swap positions {index} and {index + 1}.",
                                            size=15,
                                            color=PURPLE,
                                        ).move_to(pass_state),
                                    ),
                                    run_time=0.4,
                                ),
                                AnimationGroup(
                                    Transform(current_highlight, highlight_for(7)),
                                    run_time=0.25,
                                ),
                            ),
                            run_time=1.45,
                        )
                        elapsed += 1.45
                    values[index], values[index + 1] = right_value, left_value
                    cells[index], cells[index + 1] = right_cell, left_cell
                    swapped_this_pass = True
                elif not self.audio_prepare_mode:
                    self.play(Indicate(frame, color=LAVENDER), run_time=0.3)
                    elapsed += 0.3

                if not self.audio_prepare_mode:
                    self.play(FadeOut(frame), run_time=0.12)
                    elapsed += 0.12

            sorted_index = len(values) - pass_number
            sorted_cell = cells[sorted_index]
            if not self.audio_prepare_mode:
                self.play(
                    sorted_cell[0].animate.set_fill(PINK, opacity=0.24),
                    Transform(
                        pass_state,
                        make_text(
                            f"Pass {pass_number}: {values[sorted_index]} is fixed.",
                            size=15,
                            color=PURPLE,
                        ).move_to(pass_state),
                    ),
                    run_time=0.4,
                )
                elapsed += 0.4
                remaining_speech = speech_duration - elapsed
                if remaining_speech > 0:
                    self.wait(remaining_speech)
            return swapped_this_pass

        run_pass(
            1,
            4,
            "Five is greater than one, so the if condition is true. Temp holds five while one moves left; then temp goes into the right slot and swapped becomes true. The same process moves five past four and two, but not past eight.",
            "Zeno Sensei: The pair swaps, then i moves to the next position.",
        )
        run_pass(
            2,
            3,
            "The next pass stops one position earlier because eight is already in its final place. Four swaps with two, and five is now fixed beside eight.",
            "Zeno Sensei: The sorted end shrinks the next pass.",
        )
        swapped_on_third = run_pass(
            3,
            2,
            "On pass three, the remaining neighbors are already ordered, so no swaps happen. The early-exit check can stop here; the full array is sorted.",
            "Zeno Sensei: No swaps this pass, so sorting can stop.",
        )
        if swapped_on_third:
            raise AssertionError("The sorted Bubble Sort example should finish on a no-swap pass.")
        if values != sorted(initial_values):
            raise AssertionError("The Bubble Sort example did not produce sorted values.")
        self.speak(
            "At the end of a pass, if swapped is still false, no pair needed changing. The break exits early instead of checking the array again.",
            "robot",
            Transform(current_highlight, highlight_for(10)),
            Indicate(code_group[10], color=PURPLE),
            self.caption_transition("Zeno Sensei: No swaps means the break ends the loop."),
        )
        sorted_message = make_heading("1   2   4   5   8", size=22, color=PURPLE)
        sorted_message.move_to([-2.15, -1.35, 0])
        self.play(FadeIn(sorted_message, shift=UP * 0.08), run_time=0.45)

        example_group = VGroup(
            *value_cells, index_labels, compare_state, pass_state,
            code_panel, code_group, current_highlight, sorted_message,
        )
        self.play(FadeOut(example_group), FadeOut(subtitle), run_time=0.55)

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
        time_formula = make_heading("(n - 1) + (n - 2) + ... + 1", size=22, color=PURPLE).move_to([0, 0.8, 0])
        time_explanation = make_text(
            "Each pass checks the remaining unsorted neighbors.\nThe number of comparisons grows proportionally to n squared.",
            size=19,
            color=DARK,
            line_spacing=1.25,
        ).move_to([0, -0.45, 0])
        best_case_note = make_text(
            "If a complete pass makes no swaps, the optimized version stops early: O(n).",
            size=16,
            color=PURPLE,
        ).move_to([0, -1.55, 0])
        time_group = VGroup(time_detail_title, time_formula, time_explanation, best_case_note)
        self.play(FadeOut(summary_group), run_time=0.4)
        self.speak(
            "In the worst case, each pass checks almost every remaining neighbor. The comparisons add up as n minus one, plus n minus two, down to one, which grows quadratically. If the input is already sorted, one pass with no swaps lets the optimized version finish in linear time.",
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
            "The algorithm swaps array entries; it does not build another array.\nOnly a fixed number of helper variables are used.",
            size=18,
            color=DARK,
            line_spacing=1.25,
        ).move_to([0, -0.85, 0])
        space_formula = make_heading("Auxiliary space: O(1)", size=26, color=PURPLE).move_to([0, -1.75, 0])
        space_group = VGroup(space_title, input_label, swap_values, space_explanation, space_formula)
        self.play(FadeOut(time_group), run_time=0.4)
        self.speak(
            "Bubble Sort rearranges the input array itself. A swap uses a temporary value, but it does not create another collection. The extra memory stays constant, or O of one.",
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
            "Best for learning, tiny lists, or nearly sorted data with early exit.",
            size=16,
            color=DARK,
        ).move_to([0, -1.55, 0])
        guidance_group = VGroup(pros_title, pros_panel, cons_panel, pros_text, cons_text, use_case)
        self.speak(
            "Bubble Sort is so simple and it sorts in place. Why not use it for every list?",
            "student",
            self.caption_transition("Obscure: If it's simple, why not use it every time?"),
        )
        self.play(FadeOut(space_group), run_time=0.4)
        self.speak(
            "Its repeated comparisons and swaps grow quadratically, so large inputs can take a long time. It is useful for learning, tiny lists, or nearly sorted data when the no-swap early exit is included. For larger real-world inputs, choose a more efficient sort.",
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
                    "Here is the optimized Java version. Each pass shortens the unsorted range, and the swapped flag lets it stop when a pass makes no changes.",
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
            "Obscure: Compare neighbors, swap when needed, and stop when a pass makes no swaps!"
        )
        self.play(FadeOut(code_objects), run_time=0.4)
        self.speak(
            "So Bubble Sort checks neighboring values, swaps out-of-order pairs, and stops after a pass with no swaps. I can see how the values bubble into place!",
            "student",
            FadeIn(student, shift=UP * 0.12),
            FadeIn(robot, shift=UP * 0.12),
            closing_caption,
            run_time=0.8,
        )
        outro_image = create_character(SUBSCRIBE_IMAGE, 4.3).move_to([-3.3, -0.25, 0])
        outro_text = VGroup(
            make_heading("Keep learning with me!", size=29, color=DARK),
            make_heading("LIKE   SHARE   SUBSCRIBE", size=20, color=PURPLE),
            make_text("More coding concepts, one step at a time.", size=17, color=DARK),
        ).arrange(DOWN, buff=0.35).move_to([2.35, 0, 0])
        self.play(
            FadeOut(Group(title, student, robot, self.caption_box, self.current_caption)),
            run_time=0.45,
        )
        self.speak(
            "If this helped you understand Bubble Sort, like and share the video, and subscribe to learn more coding concepts with us. Thanks for learning with us!",
            "student",
            FadeIn(outro_image),
            FadeIn(outro_text),
            run_time=0.9,
        )
        self.wait(0.5)
