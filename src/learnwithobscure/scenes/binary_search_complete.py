from pathlib import Path

from manim import *


# Render this scene with -qh (1080p) or -qk (4K), not -ql (480p preview).


# ============================================================
# LEARN WITH OBSCURE — BINARY SEARCH
# Complete Manim scene with illustrated character assets
# ============================================================

# Brand palette
BG = "#E6D9F2"
DARK = "#352044"
PURPLE = "#7B3FA1"
LAVENDER = "#A987C5"
PINK = "#FF75AC"
WHITE = "#FFFFFF"

# Resolve assets from the repository root, independent of the current directory.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = PROJECT_ROOT / "assets" / "characters"
STUDENT_IMAGE = ASSET_DIR / "student_chibi.png"
ROBOT_IMAGE = ASSET_DIR / "robot_mentor.png"


def make_text(content, size=24, color=DARK, font="DejaVu Sans", **kwargs):
    """Consistent typography for the whole animation."""
    return Text(
        content,
        font=font,
        font_size=size,
        color=color,
        **kwargs,
    )


def create_student():
    """Load the illustrated chibi learner avatar."""
    if not STUDENT_IMAGE.exists():
        raise FileNotFoundError(
            f"Couldn't find {STUDENT_IMAGE}. "
            "Make sure assets/characters is present in the project root."
        )

    avatar = ImageMobject(
        str(STUDENT_IMAGE),
        scale_to_resolution=1080,
        resampling_algorithm=RESAMPLING_ALGORITHMS["bicubic"],
    )
    avatar.scale_to_fit_height(2.55)
    return avatar


def create_robot():
    """Load the illustrated anime-style robot mentor."""
    if not ROBOT_IMAGE.exists():
        raise FileNotFoundError(
            f"Couldn't find {ROBOT_IMAGE}. "
            "Make sure assets/characters is present in the project root."
        )

    robot = ImageMobject(
        str(ROBOT_IMAGE),
        scale_to_resolution=1080,
        resampling_algorithm=RESAMPLING_ALGORITHMS["bicubic"],
    )
    robot.scale_to_fit_height(2.45)
    return robot


def make_cell(value, index, x):
    square = RoundedRectangle(
        width=0.78,
        height=0.78,
        corner_radius=0.08,
        stroke_color=PURPLE,
        stroke_width=2.2,
        fill_color=WHITE,
        fill_opacity=1,
    ).move_to([x, 0.55, 0])

    number = make_text(str(value), size=27, color=DARK)
    number.move_to(square)

    index_label = make_text(str(index), size=17, color=PURPLE)
    index_label.next_to(square, DOWN, buff=0.10)

    return VGroup(square, number), index_label


# ============================================================
# LEARN WITH OBSCURE — FULL BINARY SEARCH LESSON
# Silent content-first cut; voiceover will be added after visuals are finalized.
# Render from the project root:
# uv run manim -pqh src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
# ============================================================

class BinarySearchDemo(Scene):
    """A complete, silent, content-first introduction to binary search.

    Dialogue text and animation are retained. Voiceover can be added after
    the educational content and visuals are finalized.
    """

    def speak(self, narration, speaker="robot", *animations, run_time=1.2, **play_kwargs):
        """Play a deliberately paced visual beat; voiceover will be added later."""
        if animations:
            self.play(*animations, run_time=run_time, **play_kwargs)
        # Give each dialogue beat a little extra reading time; voiceover timing
        # can replace this fixed pause when narration is added.
        self.wait(1.4)

    def dialogue_line(self, text, size=18):
        return make_text(text, size=size, color=DARK).move_to(self.dialogue_box)

    def construct(self):
        self.camera.background_color = BG

        # ----------------------------------------------------
        # Title and characters — retain the original layout
        # ----------------------------------------------------
        title = make_text("Binary Search", size=40, color=DARK)
        title.move_to([0, 3.28, 0])
        subtitle = make_text(
            "Can we find 10 in just 3 checks?", size=21, color=PURPLE
        )
        subtitle.next_to(title, DOWN, buff=0.10)
        self.play(
            FadeIn(title, shift=DOWN * 0.15),
            FadeIn(subtitle, shift=DOWN * 0.10),
            run_time=0.8,
        )

        student = create_student().move_to([-5.35, -1.45, 0])
        robot = create_robot().move_to([5.35, -1.45, 0])
        self.play(
            FadeIn(student, shift=UP * 0.22, scale=0.94),
            FadeIn(robot, shift=UP * 0.22, scale=0.94),
            run_time=1.0,
        )
        self.play(
            student.animate.shift(UP * 0.08),
            robot.animate.shift(UP * 0.08),
            rate_func=there_and_back,
            run_time=0.55,
        )

        self.dialogue_box = RoundedRectangle(
            width=8.35, height=0.78, corner_radius=0.18,
            stroke_color=PURPLE, stroke_width=2.2,
            fill_color=WHITE, fill_opacity=1,
        ).move_to([0, -3.28, 0])
        dialogue = make_text("Let's find 10 together!", size=19, color=DARK)
        dialogue.move_to(self.dialogue_box)
        self.play(
            FadeIn(self.dialogue_box, shift=UP * 0.12),
            FadeIn(dialogue, scale=0.92),
            run_time=0.65,
        )

        # ----------------------------------------------------
        # Introduction: problem, sorted data, and target
        # ----------------------------------------------------
        self.speak(
            "Can we find ten without checking every number? Let's try binary search.",
            "student",
            Transform(dialogue, self.dialogue_line("Chibi: Can we find 10 in 3 checks?")),
            student.animate.shift(UP * 0.12),
            run_time=0.8,
        )
        self.speak(
            "Let's work through an example together. First, there is one very important requirement: "
            "the list must already be sorted, from smallest to largest.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: Binary search needs sorted data.")),
            run_time=0.7,
        )

        # ----------------------------------------------------
        # Array and target — same values and positions as original
        # ----------------------------------------------------
        values = [2, 4, 6, 8, 10, 12, 14]
        cells = VGroup()
        index_labels = VGroup()
        x_positions = [(i - 3) * 0.91 for i in range(len(values))]
        for i, value in enumerate(values):
            cell, index_label = make_cell(value, i, x_positions[i])
            cells.add(cell)
            index_labels.add(index_label)
        self.speak(
            "Here is our sorted list: two, four, six, eight, ten, twelve, and fourteen. "
            "Notice that the numbers are in ascending order.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: Here is our sorted list.")),
            LaggedStart(*[FadeIn(cell, scale=0.82) for cell in cells], lag_ratio=0.10),
            FadeIn(index_labels),
            run_time=1.0,
        )

        target_label = make_text("TARGET", size=15, color=PURPLE)
        target_value = make_text("10", size=27, color=PINK)
        target_group = VGroup(target_label, target_value).arrange(RIGHT, buff=0.15)
        target_group.move_to([0, -0.78, 0])
        self.speak(
            "And the number we want to find is ten. We will call this our target.",
            "robot",
            FadeIn(target_group, scale=0.9),
            run_time=0.5,
        )
        self.speak(
            "Got it! We are looking for ten in this sorted list.",
            "student",
            Transform(dialogue, self.dialogue_line("Chibi: Our target is 10!")),
            run_time=0.6,
        )

        # ----------------------------------------------------
        # Explain low, high, and mid
        # ----------------------------------------------------
        low = make_text("LOW", size=17, color=PURPLE).move_to([x_positions[0], 1.55, 0])
        mid = make_text("MID", size=17, color=PINK).move_to([x_positions[3], 1.55, 0])
        high = make_text("HIGH", size=17, color=PURPLE).move_to([x_positions[6], 1.55, 0])
        self.speak(
            "Binary search keeps track of three positions. Low marks the first index we are still considering. "
            "High marks the last index. And mid points to the middle index between them.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: Meet LOW, MID, and HIGH.")),
            FadeIn(low, shift=DOWN * 0.12),
            FadeIn(mid, shift=DOWN * 0.12),
            FadeIn(high, shift=DOWN * 0.12),
            run_time=0.65,
        )
        active_range = SurroundingRectangle(
            VGroup(*cells[0:7]), color=LAVENDER, buff=0.09, stroke_width=2.5
        )
        self.speak(
            "At the beginning, the whole list is available to search. So low is at index zero, "
            "and high is at index six.",
            "robot",
            Create(active_range),
            run_time=0.5,
        )
        self.speak(
            "To find mid, we add low and high, then divide by two. "
            "In programming, we use integer division so the result is a whole-number index. "
            "Here, zero plus six, divided by two, gives us index three.",
            "robot",
            Indicate(cells[3], color=PINK, scale_factor=1.12),
            run_time=0.8,
        )

        # ----------------------------------------------------
        # Iteration 1: middle value 8, discard left section
        # ----------------------------------------------------
        self.speak(
            "Let's check the value at index three. It is eight. Is eight our target, ten?",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: MID points to 8. Is it 10?")),
            run_time=0.9,
        )
        self.speak(
            "No! Eight is smaller than ten.",
            "student",
            Transform(dialogue, self.dialogue_line("Chibi: No, 8 is smaller than 10!")),
            run_time=0.55,
        )
        new_low = make_text("LOW", size=17, color=PURPLE).move_to([x_positions[4], 1.55, 0])
        right_range = SurroundingRectangle(
            VGroup(*cells[4:7]), color=PINK, buff=0.09, stroke_width=3
        )
        self.speak(
            "Exactly! Since the list is sorted, every value to the left of eight must be even smaller. "
            "Those values cannot be ten, so we can safely discard them. We move low to index four. "
            "The remaining search range is now ten, twelve, and fourteen.",
            "robot",
            low.animate.move_to(new_low),
            Transform(active_range, right_range),
            run_time=0.7,
        )

        # ----------------------------------------------------
        # Iteration 2: middle value 12, discard right section
        # ----------------------------------------------------
        new_mid = make_text("MID", size=17, color=PINK).move_to([x_positions[5], 1.55, 0])
        self.speak(
            "Now low is four and high is six. Their middle index is five. "
            "Let's inspect the value at index five.",
            "robot",
            mid.animate.move_to(new_mid),
            Indicate(cells[5], color=PINK, scale_factor=1.12),
            run_time=0.9,
        )
        self.speak(
            "The value is twelve. That is larger than our target, ten.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: 12 is larger than 10.")),
            run_time=0.55,
        )
        self.speak(
            "So ten must be somewhere to the left of twelve. We can remove twelve and fourteen from our search!",
            "student",
            Transform(dialogue, self.dialogue_line("Chibi: Keep the left side!", 17)),
            run_time=0.6,
        )
        new_high = make_text("HIGH", size=17, color=PURPLE).move_to([x_positions[4], 1.55, 0])
        final_range = SurroundingRectangle(cells[4], color=PINK, buff=0.10, stroke_width=3.2)
        self.speak(
            "Perfect. We move high back to index four. Now low and high both point to index four. "
            "Only one value remains in our search range.",
            "robot",
            high.animate.move_to(new_high),
            Transform(active_range, final_range),
            run_time=0.7,
        )

        # ----------------------------------------------------
        # Iteration 3: target found
        # ----------------------------------------------------
        self.speak(
            "When low and high point to the same index, that index is also the middle. "
            "Let's check index four!",
            "robot",
            FadeOut(low),
            FadeOut(high),
            mid.animate.move_to([x_positions[4], 1.55, 0]),
            Indicate(cells[4], color=PINK, scale_factor=1.18),
            run_time=0.9,
        )
        found_message = self.dialogue_line("Robot: 10! We found it!", 20)
        self.speak(
            "And the value is ten! It matches our target. We found it!",
            "robot",
            Transform(dialogue, found_message),
            cells[4][0].animate.set_fill(PINK, opacity=0.28),
            cells[4][0].animate.set_stroke(PINK, width=4),
            run_time=0.8,
        )
        self.speak(
            "Yay! We found ten in just three comparisons! That was much quicker than checking every number one by one.",
            "student",
            student.animate.shift(UP * 0.18),
            robot.animate.shift(UP * 0.18),
            rate_func=there_and_back,
            run_time=0.65,
        )
        success = make_text("FOUND IN 3 COMPARISONS!", size=21, color=PURPLE)
        success.move_to([0, -1.55, 0])
        self.speak(
            "Three comparisons. And each time, we reduced the number of possible locations. "
            "That is the key idea behind binary search.",
            "robot",
            FadeIn(success, scale=0.82),
            Flash(cells[4], color=PINK, flash_radius=0.55),
            run_time=0.8,
        )

        # ----------------------------------------------------
        # Connect the Java statements to the live visual trace
        # ----------------------------------------------------
        self.play(
            FadeOut(Group(
                title, subtitle, student, robot, self.dialogue_box, dialogue,
                cells, index_labels, target_group, low, high, mid,
                active_range, success
            )),
            run_time=0.8,
        )

        trace_title = make_text(
            "Now watch the code drive each visual step", size=29, color=DARK
        ).move_to([0, 3.25, 0])
        trace_panel = RoundedRectangle(
            width=6.5, height=5.35, corner_radius=0.16,
            stroke_color=LAVENDER, stroke_width=2,
            fill_color=WHITE, fill_opacity=1,
        ).move_to([3.25, 0.05, 0])
        code_lines = [
            "int low = 0;",
            "int high = arr.length - 1;",
            "while (low <= high) {",
            "  int mid = low + (high - low) / 2;",
            "  if (arr[mid] == target) return mid;",
            "  if (arr[mid] < target) low = mid + 1;",
            "  else high = mid - 1;",
            "}",
            "return -1;",
        ]
        code_group = VGroup(*[
            Text(
                line, font="DejaVu Sans Mono", font_size=15,
                color=DARK, disable_ligatures=True,
            )
            for line in code_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        code_group.scale_to_fit_width(6.0)
        code_group.move_to([3.18, 0.05, 0])

        def code_highlight(line_index):
            return SurroundingRectangle(
                code_group[line_index], buff=0.055,
                color=PINK, stroke_width=1.5,
                fill_color=PINK, fill_opacity=0.18,
            )

        trace_values = [2, 4, 6, 8, 10, 12, 14]
        trace_cells = VGroup()
        trace_indices = VGroup()
        trace_x = [-3.45 + (i - 3) * 0.72 for i in range(7)]
        for i, value in enumerate(trace_values):
            cell, index_label = make_cell(value, i, trace_x[i])
            trace_cells.add(cell)
            trace_indices.add(index_label)
        low_marker = make_text("LOW", size=14, color=PURPLE).move_to([trace_x[0], 1.55, 0])
        mid_marker = make_text("MID", size=14, color=PINK).move_to([trace_x[3], 1.55, 0])
        high_marker = make_text("HIGH", size=14, color=PURPLE).move_to([trace_x[6], 1.55, 0])
        trace_target = make_text("TARGET = 10", size=19, color=PINK).move_to([-3.45, -0.65, 0])
        trace_state = make_text("low = 0     high = 6     mid = —", size=17, color=DARK)
        trace_state.move_to([-3.45, -1.35, 0])
        trace_result = make_text("Result: searching...", size=17, color=PURPLE).move_to([-3.45, -2.15, 0])
        current_highlight = code_highlight(0)

        self.play(
            FadeIn(trace_title), FadeIn(trace_panel),
            FadeIn(trace_cells), FadeIn(trace_indices),
            FadeIn(low_marker), FadeIn(mid_marker), FadeIn(high_marker),
            FadeIn(trace_target), FadeIn(trace_state), FadeIn(trace_result),
            FadeIn(current_highlight), FadeIn(code_group),
            run_time=1.0,
        )
        self.wait(0.8)

        def focus_code(line_index, *animations, run_time=0.7):
            nonlocal current_highlight
            next_highlight = code_highlight(line_index)
            self.play(
                Transform(current_highlight, next_highlight),
                *animations,
                run_time=run_time,
            )

        # Initialize bounds, calculate mid, then follow the two branch updates.
        focus_code(1, run_time=0.55)
        focus_code(2, run_time=0.55)
        focus_code(3, Indicate(trace_cells[3], color=PINK), run_time=0.8)
        self.play(Transform(
            trace_state,
            make_text("low = 0     high = 6     mid = 3  →  arr[3] = 8", size=16, color=DARK)
                .move_to(trace_state),
        ), run_time=0.65)
        focus_code(4, run_time=0.45)  # Equality check is false for 8.
        focus_code(5, run_time=0.55)
        self.play(
            low_marker.animate.move_to([trace_x[4], 1.55, 0]),
            Transform(
                trace_state,
                make_text("8 < 10  →  low = mid + 1 = 4", size=17, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=0.75,
        )
        focus_code(2, run_time=0.45)
        focus_code(3, mid_marker.animate.move_to([trace_x[5], 1.55, 0]), Indicate(trace_cells[5], color=PINK), run_time=0.8)
        self.play(Transform(
            trace_state,
            make_text("low = 4     high = 6     mid = 5  →  arr[5] = 12", size=16, color=DARK)
                .move_to(trace_state),
        ), run_time=0.65)
        focus_code(4, run_time=0.45)  # Equality check is false for 12.
        focus_code(6, run_time=0.55)
        self.play(
            high_marker.animate.move_to([trace_x[4], 1.55, 0]),
            Transform(
                trace_state,
                make_text("12 > 10  →  high = mid − 1 = 4", size=17, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=0.75,
        )
        focus_code(2, run_time=0.45)
        focus_code(3, mid_marker.animate.move_to([trace_x[4], 1.55, 0]), Indicate(trace_cells[4], color=PINK), run_time=0.8)
        self.play(Transform(
            trace_state,
            make_text("low = high = mid = 4  →  arr[4] = 10", size=16, color=DARK)
                .move_to(trace_state),
        ), run_time=0.65)
        focus_code(4, run_time=0.6)
        self.play(
            trace_cells[4][0].animate.set_fill(PINK, opacity=0.28),
            Transform(
                trace_result,
                make_text("return mid → index 4", size=20, color=PURPLE)
                    .move_to(trace_result),
            ),
            run_time=0.75,
        )
        self.wait(1.2)
        self.play(
            FadeOut(VGroup(
                trace_title, trace_panel, code_group, current_highlight,
                trace_cells, trace_indices, low_marker, mid_marker, high_marker,
                trace_target, trace_state, trace_result,
            )),
            run_time=0.8,
        )

        # ----------------------------------------------------
        # Additional scenarios: best case, early success, and not found
        # ----------------------------------------------------

        def scenario_card(title_text, target, steps, result_text, result_color=PURPLE):
            """Show a readable binary-search trace on the same sorted array."""
            heading = make_text(title_text, size=27, color=DARK).move_to([0, 2.85, 0])
            scenario_values = [2, 4, 6, 8, 10, 12, 14]
            row = VGroup()
            labels = VGroup()
            positions = [(i - 3) * 0.91 for i in range(7)]

            for i, value in enumerate(scenario_values):
                cell, index_label = make_cell(value, i, positions[i])
                row.add(cell)
                labels.add(index_label)

            row.shift(DOWN * 0.15)
            labels.shift(DOWN * 0.15)

            target_text = make_text(f"TARGET: {target}", size=21, color=PINK)
            target_text.move_to([0, 1.45, 0])

            explanation = make_text(
                "Begin with the complete sorted array.", size=17, color=DARK
            ).move_to([0, -1.05, 0])

            counter = make_text("Comparisons: 0", size=18, color=PURPLE)
            counter.move_to([0, -1.75, 0])

            self.play(
                FadeIn(heading), FadeIn(row), FadeIn(labels),
                FadeIn(target_text), FadeIn(explanation), FadeIn(counter),
                run_time=1.0,
            )
            self.wait(1.5)

            for comparison, (mid_index, message) in enumerate(steps, start=1):
                next_explanation = make_text(message, size=17, color=DARK)
                next_explanation.move_to(explanation)

                next_counter = make_text(
                    f"Comparisons: {comparison}", size=18, color=PURPLE
                ).move_to(counter)

                self.play(
                    Indicate(row[mid_index], color=PINK, scale_factor=1.12),
                    Transform(explanation, next_explanation),
                    Transform(counter, next_counter),
                    run_time=1.0,
                )
                self.wait(1.7)

            final_result = make_text(result_text, size=21, color=result_color)
            final_result.move_to([0, -2.55, 0])

            self.play(FadeIn(final_result, scale=0.9), run_time=0.8)
            self.wait(2.2)

            self.play(
                FadeOut(VGroup(
                    heading, row, labels, target_text,
                    explanation, counter, final_result
                )),
                run_time=0.8,
            )

        # Best case: the first midpoint is exactly the target.
        scenario_card(
            "Scenario 1 — Best Case: Found Immediately",
            8,
            [(3, "Middle index is 3. The value is 8 — it matches the target!")],
            "FOUND after 1 comparison • Best case: O(1)",
        )

        # Early success: target is found after moving into the left half.
        scenario_card(
            "Scenario 2 — Early Success",
            4,
            [
                (3, "Check index 3: value 8. It is greater than 4, so keep the left half."),
                (1, "Check index 1: value 4. It matches the target!"),
            ],
            "FOUND after 2 comparisons",
        )

        # Unsuccessful search: demonstrate the range becoming empty.
        scenario_card(
            "Scenario 3 — Unsuccessful Search",
            11,
            [
                (3, "Check index 3: value 8. It is smaller than 11, so search right."),
                (5, "Check index 5: value 12. It is larger than 11, so search left."),
                (4, "Check index 4: value 10. It is smaller than 11; the range becomes empty."),
            ],
            "NOT FOUND • The search range is empty",
            result_color=PINK,
        )

        # Bring the characters and dialogue back for the recap.
        self.play(
            FadeIn(student), FadeIn(robot), FadeIn(self.dialogue_box),
            FadeIn(dialogue), run_time=0.9,
        )
        self.wait(1.0)

        # ----------------------------------------------------
        # Recap, prerequisite, and efficiency
        # ----------------------------------------------------
        self.speak(
            "Let's recap. Start with a sorted list. Set low to the first index and high to the last index. "
            "Find the middle index, then compare its value with the target.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: Sorted list. Find the middle. Compare.", 16)),
            run_time=0.7,
        )
        self.speak(
            "If the middle value is the target, we are done. If it is too small, search the right half. "
            "If it is too large, search the left half. Repeat until we find the target or the search range becomes empty.",
            "robot",
            run_time=0.7,
        )
        self.speak(
            "And remember, binary search only works correctly when the data is sorted. "
            "If the list is not sorted, we must sort it first or use a different search method.",
            "robot",
            run_time=0.7,
        )
        self.speak(
            "One last cool fact: binary search has logarithmic time complexity, written as big O of log n. "
            "That means even when the list becomes much larger, the number of comparisons grows very slowly, "
            "because we cut the remaining search space roughly in half each time.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: Time complexity — O(log n)!", 18)),
            run_time=0.7,
        )
        self.speak(
            "I get it now! Instead of checking every item, we keep eliminating half of the possibilities. "
            "Thanks for teaching me!",
            "student",
            Transform(dialogue, self.dialogue_line("Chibi: That makes sense. Thank you!", 17)),
            run_time=0.7,
        )
        self.speak(
            "You're welcome! Remember: sorted data, check the middle, and eliminate half. "
            "That's binary search! See you in the next lesson.",
            "robot",
            Transform(dialogue, self.dialogue_line("Robot: Sorted. Middle. Eliminate half!", 17)),
            run_time=0.7,
        )

        # ----------------------------------------------------
        # When binary search is the right tool
        # ----------------------------------------------------
        self.play(
            FadeOut(Group(
                title, subtitle, student, robot, self.dialogue_box, dialogue,
                cells, index_labels, target_group, low, high, mid,
                active_range, success
            ), shift=DOWN * 0.15),
            run_time=0.8,
        )

        def section_title(text):
            heading = make_text(text, size=34, color=DARK)
            heading.move_to([0, 3.15, 0])
            underline = Line(LEFT * 2.0, RIGHT * 2.0, color=PINK, stroke_width=4)
            underline.next_to(heading, DOWN, buff=0.12)
            return VGroup(heading, underline)

        use_title = section_title("When Should We Use Binary Search?")
        use_intro = make_text(
            "It is especially useful when the data is sorted and we need fast lookups.",
            size=19, color=PURPLE
        ).move_to([0, 2.25, 0])

        use_cards = VGroup()
        use_items = [
            ("SORTED DATA", "Searching a sorted array or list repeatedly."),
            ("LARGE DATASETS", "Finding an item without scanning every element."),
            ("FAST LOOKUPS", "Searching names, IDs, scores, or timestamps in order."),
            (
                "ANSWER-SPACE SEARCH",
                "Finding the smallest or largest value that\nsatisfies a monotonic condition.",
            ),
        ]

        card_positions = [
            (-3.15, 0.95), (3.15, 0.95),
            (-3.15, -1.05), (3.15, -1.05)
        ]

        for (heading, body), (x, y) in zip(use_items, card_positions):
            card = RoundedRectangle(
                width=5.55, height=1.45, corner_radius=0.16,
                stroke_color=LAVENDER, stroke_width=2,
                fill_color=WHITE, fill_opacity=1
            ).move_to([x, y, 0])

            h = make_text(heading, size=18, color=PURPLE)
            h.move_to(card.get_top() + DOWN * 0.35)

            b = make_text(body, size=15, color=DARK, line_spacing=0.9)
            b.move_to(card.get_center() + DOWN * 0.18)

            use_cards.add(VGroup(card, h, b))

        self.play(FadeIn(use_title), FadeIn(use_intro), run_time=0.6)
        self.play(
            LaggedStart(
                *[FadeIn(card, shift=UP * 0.12) for card in use_cards],
                lag_ratio=0.12
            ),
            run_time=1.2
        )
        self.wait(2.0)

        # ----------------------------------------------------
        # Advantages and limitations
        # ----------------------------------------------------
        pros_title = section_title("Advantages & Disadvantages")

        pros_panel = RoundedRectangle(
            width=5.8, height=4.45, corner_radius=0.18,
            stroke_color=PURPLE, stroke_width=2.2,
            fill_color=WHITE, fill_opacity=1
        ).move_to([-3.15, -0.15, 0])

        cons_panel = RoundedRectangle(
            width=5.8, height=4.45, corner_radius=0.18,
            stroke_color=PINK, stroke_width=2.2,
            fill_color=WHITE, fill_opacity=1
        ).move_to([3.15, -0.15, 0])

        pros_heading = make_text("PROS", size=23, color=PURPLE)
        pros_heading.move_to(pros_panel.get_top() + DOWN * 0.42)

        cons_heading = make_text("CONS", size=23, color=PINK)
        cons_heading.move_to(cons_panel.get_top() + DOWN * 0.42)

        pros_lines = [
            "• Very fast: O(log n) time",
            "• Eliminates about half the range",
            "• Iterative version uses O(1) space",
            "• Excellent for repeated lookups",
        ]

        cons_lines = [
            "• Data must be sorted first",
            "• Sorting first can cost O(n log n)",
            "• Slow on linked lists (no fast indexing)",
            "• Sorted-array inserts/deletes can cost O(n)",
        ]

        pros_text = VGroup(*[
            make_text(line, size=16, color=DARK)
            for line in pros_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        pros_text.move_to(pros_panel.get_center() + DOWN * 0.18)

        cons_text = VGroup(*[
            make_text(line, size=16, color=DARK)
            for line in cons_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        cons_text.move_to(cons_panel.get_center() + DOWN * 0.18)

        self.play(
            FadeOut(VGroup(use_title, use_intro, use_cards)),
            FadeIn(pros_title),
            run_time=0.7
        )

        self.play(
            FadeIn(pros_panel), FadeIn(cons_panel),
            FadeIn(pros_heading), FadeIn(cons_heading),
            FadeIn(pros_text), FadeIn(cons_text),
            run_time=0.9
        )
        self.wait(2.2)

                # ----------------------------------------------------
        # Time complexity: demonstrate repeated halving
        # ----------------------------------------------------
        complexity_title = section_title("Why Is the Time Complexity O(log n)?")

        explanation = make_text(
            "Imagine searching a sorted array containing 16 values.",
            size=19, color=DARK
        ).move_to([0, 2.25, 0])

        self.play(
            FadeOut(VGroup(pros_title, pros_panel, cons_panel, pros_heading,
                           cons_heading, pros_text, cons_text)),
            FadeIn(complexity_title), FadeIn(explanation),
            run_time=0.9,
        )
        self.wait(1.8)

        remaining_counts = [16, 8, 4, 2, 1]
        halving_rows = VGroup()

        for step, count in enumerate(remaining_counts):
            label = make_text(
                "Start" if step == 0 else f"After comparison {step}",
                size=15, color=PURPLE
            )

            bar = RoundedRectangle(
                width=max(0.55, count * 0.40),
                height=0.42,
                corner_radius=0.07,
                stroke_color=PURPLE,
                fill_color=LAVENDER,
                fill_opacity=0.65
            )

            count_label = make_text(
                f"{count} possible value(s)",
                size=15,
                color=DARK
            )

            row = VGroup(label, bar, count_label).arrange(RIGHT, buff=0.22)
            halving_rows.add(row)

        halving_rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        halving_rows.scale_to_fit_width(11.8)
        halving_rows.move_to([0, -0.15, 0])

        for row in halving_rows:
            self.play(
                FadeIn(row, shift=RIGHT * 0.12),
                run_time=0.65
            )
            self.wait(1.0)

        time_reason = make_text(
            "16 → 8 → 4 → 2 → 1: each comparison removes about half the candidates.",
            size=16, color=DARK
        ).move_to([0, -2.35, 0])

        time_formula = MathTex(
            r"2^k \geq n \quad\Rightarrow\quad k \approx \log_2(n)",
            color=PURPLE
        ).scale(0.82).move_to([0, -2.95, 0])

        self.play(
            FadeIn(time_reason),
            Write(time_formula),
            run_time=1.0
        )
        self.wait(3.0)

        # Explain best case versus worst case.
        case_summary = VGroup(
            make_text("BEST CASE", size=19, color=PURPLE),

            make_text(
                "The first middle value is the target: 1 comparison → O(1).",
                size=16, color=DARK
            ),

            make_text("WORST CASE", size=19, color=PINK),

            make_text(
                "The target is found only after repeatedly halving, or is absent. "
                "We continue until one candidate remains or the range is empty → O(log n).",
                size=15, color=DARK
            ),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        case_summary.scale_to_fit_width(11.7)
        case_summary.move_to([0, -0.05, 0])

        self.play(
            FadeOut(VGroup(
                explanation,
                halving_rows,
                time_reason,
                time_formula
            )),
            FadeIn(case_summary),
            run_time=0.9,
        )
        self.wait(3.0)

        # ----------------------------------------------------
        # Space complexity: show the variables that occupy memory
        # ----------------------------------------------------
        space_title = section_title(
            "Why Is Iterative Space Complexity O(1)?"
        )

        memory_array = VGroup()

        for i, value in enumerate([2, 4, 6, 8, 10, 12, 14]):
            cell, _ = make_cell(value, i, (i - 3) * 0.91)
            memory_array.add(cell)

        memory_array.move_to([0, 1.45, 0])

        array_label = make_text(
            "Input array (already provided)",
            size=17,
            color=PURPLE
        ).move_to([0, 2.1, 0])

        variable_rows = VGroup()

        for name, value in [
            ("low", "0"),
            ("high", "6"),
            ("mid", "3")
        ]:
            variable_rows.add(
                make_text(f"{name} = {value}", size=20, color=DARK)
            )

        variable_rows.arrange(
            RIGHT,
            buff=0.75
        ).move_to([0, -0.05, 0])

        variables_label = make_text(
            "Only three index variables are maintained, regardless of array size.",
            size=16,
            color=DARK
        ).move_to([0, -0.7, 0])

        space_formula = MathTex(
            r"\text{constant number of variables}\quad\Rightarrow\quad O(1)",
            color=PINK
        ).scale(0.78).move_to([0, -1.55, 0])

        recursion_note = make_text(
            "No new array and no recursive call stack in this iterative version.",
            size=16,
            color=PURPLE
        ).move_to([0, -2.35, 0])

        self.play(
            FadeOut(VGroup(complexity_title, case_summary)),
            FadeIn(space_title),
            FadeIn(array_label),
            FadeIn(memory_array),
            run_time=1.0,
        )

        self.wait(1.5)

        self.play(
            LaggedStart(
                *[
                    FadeIn(item, shift=UP * 0.1)
                    for item in variable_rows
                ],
                lag_ratio=0.25
            ),
            FadeIn(variables_label),
            run_time=1.0,
        )

        self.wait(1.8)

        self.play(
            Write(space_formula),
            FadeIn(recursion_note),
            run_time=1.0
        )

        self.wait(3.0)

        complexity_footer = make_text(
            "Iterative binary search: best time O(1), worst time O(log n), "
            "auxiliary space O(1).",
            size=15,
            color=PURPLE
        ).move_to([0, -3.15, 0])

        self.play(
            FadeIn(complexity_footer),
            run_time=0.7
        )

        self.wait(2.0)

        # ----------------------------------------------------
        # Complete Java implementation — split across two pages
        # ----------------------------------------------------
        java_code_pages = [
            [
                "public class BinarySearchExample {",
                "    public static int binarySearch(int[] arr, int target) {",
                "        int low = 0;",
                "        int high = arr.length - 1;",
                "",
                "        while (low <= high) {",
                "            int mid = low + (high - low) / 2;",
                "",
                "            if (arr[mid] == target) {",
                "                return mid;  // Target found",
                "            }",
                "            else if (arr[mid] < target) {",
                "                low = mid + 1;  // Search right half",
                "            }",
            ],
            [
                "            else {",
                "                high = mid - 1; // Search left half",
                "            }",
                "        }",
                "",
                "        return -1; // Target is not present",
                "    }",
                "",
                "    public static void main(String[] args) {",
                "        int[] numbers = {2, 4, 6, 8, 10, 12, 14};",
                "        int target = 10;",
                "",
                "        int result = binarySearch(numbers, target);",
                "        System.out.println(\"Index: \" + result);",
                "    }",
                "}",
            ],
        ]

        code_titles = [
            "Java Implementation (1/2)",
            "Java Implementation (2/2)",
        ]

        for page_index, lines in enumerate(java_code_pages):

            code_title = section_title(code_titles[page_index])

            code_panel = RoundedRectangle(
                width=12.65,
                height=5.65,
                corner_radius=0.16,
                stroke_color=LAVENDER,
                stroke_width=2,
                fill_color=WHITE,
                fill_opacity=1
            ).move_to([0, -0.05, 0])

            code_text = Text(
                "\n".join(lines),
                font="DejaVu Sans Mono",
                font_size=17,
                line_spacing=0.78,
                color=DARK,
                disable_ligatures=True,
            )

            code_text.scale_to_fit_width(11.9)
            code_text.scale_to_fit_height(5.05)
            code_text.move_to(code_panel.get_center())

            page_label = make_text(
                "Complete iterative binary search • Java",
                size=14,
                color=PURPLE
            ).move_to([0, -3.45, 0])

            if page_index == 0:
                self.play(
                    FadeOut(VGroup(
                        space_title,
                        array_label,
                        memory_array,
                        variable_rows,
                        variables_label,
                        space_formula,
                        recursion_note,
                        complexity_footer
                    )),
                    FadeIn(code_title),
                    run_time=0.65
                )
            else:
                self.play(
                    FadeOut(VGroup(
                        code_title_prev,
                        code_panel_prev,
                        code_text_prev,
                        page_label_prev
                    )),
                    FadeIn(code_title),
                    run_time=0.65
                )

            self.play(
                FadeIn(code_panel),
                FadeIn(code_text, shift=UP * 0.08),
                FadeIn(page_label),
                run_time=0.8
            )

            # Longer reading time for the Java implementation.
            self.wait(5.0)

            code_title_prev = code_title
            code_panel_prev = code_panel
            code_text_prev = code_text
            page_label_prev = page_label

        # The complete Java implementation is the final section of the video.
        # Leave the second page visible long enough for viewers to read it.
        self.wait(3.0)

        
