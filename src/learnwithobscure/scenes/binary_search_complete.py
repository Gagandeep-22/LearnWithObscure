import hashlib
import os
from pathlib import Path
import wave

from manim import *
from manim_voiceover.services.gemini import GeminiService


# Render this scene with --disable_caching to preserve all narration sounds.


# ============================================================
# LEARN WITH OBSCURE - BINARY SEARCH
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
SUBSCRIBE_IMAGE = ASSET_DIR / "Chibi Creator\u2019s Subscribe Moment.png"
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
GEMINI_VOICES = {"student": "Achird", "robot": "Leda"}


def make_text(content, size=24, color=DARK, font="Arial", **kwargs):
    """Consistent typography for the whole animation."""
    return Text(
        content,
        font=font,
        font_size=size,
        color=color,
        **kwargs,
    )


def make_heading(content, size=24, color=DARK, **kwargs):
    """Consistent, bold headings that remain legible in mobile renders."""
    return make_text(content, size=size, color=color, weight="BOLD", **kwargs)


def create_student():
    """Load Obscure, the illustrated chibi learner avatar."""
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
    avatar.scale_to_fit_height(3.05)
    return avatar


def create_robot():
    """Load Zeno Sensei, the calm robot mentor avatar."""
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
    robot.scale_to_fit_height(2.95)
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
    index_label.next_to(square, DOWN, buff=0.20)

    return VGroup(square, number), index_label


def make_array_range(cells, index_labels, low_index, high_index, color):
    """Frame the active cells and their index labels together."""
    contents = VGroup(
        *cells[low_index:high_index + 1],
        *index_labels[low_index:high_index + 1],
    )
    return SurroundingRectangle(
        contents, color=color, buff=0.12, stroke_width=2.5
    )


# ============================================================
# LEARN WITH OBSCURE - FULL BINARY SEARCH LESSON
# Narration uses Gemini TTS; set GEMINI_API_KEY before rendering.
# Render from the project root:
# uv run manim --disable_caching -p -qk src/learnwithobscure/scenes/binary_search_complete.py BinarySearchDemo
# ============================================================

class BinarySearchDemo(Scene):
    """A narrated, character-led introduction to binary search."""

    def make_narration_audio(self, narration, speaker):
        """Generate and cache Gemini speech for one dialogue beat."""
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add a valid Gemini API key before rendering."
            )

        audio_dir = PROJECT_ROOT / "media" / "audio_files" / "binary_search_demo"
        audio_dir.mkdir(parents=True, exist_ok=True)
        voice = GEMINI_VOICES.get(speaker, GEMINI_VOICES["robot"])
        cache_key = hashlib.sha256(
            f"{GEMINI_TTS_MODEL}:{voice}:{narration}".encode("utf-8")
        ).hexdigest()[:20]
        audio_path = audio_dir / f"{cache_key}.wav"
        if not audio_path.exists():
            service = GeminiService(voice=voice, model=GEMINI_TTS_MODEL)
            result = service.generate_from_text(
                narration,
                cache_dir=audio_dir,
                path=audio_path.name,
            )
            audio_path = audio_dir / result["original_audio"]
        with wave.open(str(audio_path), "rb") as audio_file:
            return audio_path, audio_file.getnframes() / audio_file.getframerate()

    def speak(self, narration, speaker="robot", *animations, run_time=1.2, **play_kwargs):
        """Play a quick visual beat, then hold until the spoken line finishes."""
        audio_path, speech_duration = self.make_narration_audio(narration, speaker)
        self.add_sound(str(audio_path))
        if animations:
            self.play(*animations, run_time=run_time, **play_kwargs)
            self.wait(max(0, speech_duration - run_time))
        else:
            self.wait(speech_duration)

    def dialogue_line(self, text, size=18):
        return make_text(text, size=size, color=DARK).move_to(self.dialogue_box)

    def construct(self):
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add a valid Gemini API key before rendering."
            )

        self.camera.background_color = BG

        # ----------------------------------------------------
        # Title and characters - retain the original layout
        # ----------------------------------------------------
        title = make_heading("Binary Search", size=40, color=DARK)
        title.move_to([0, 3.28, 0])
        subtitle = make_heading(
            "Obscure needs to find 10 in a sorted array.", size=21, color=PURPLE
        )
        subtitle.next_to(title, DOWN, buff=0.10)
        self.play(
            FadeIn(title, shift=DOWN * 0.15),
            FadeIn(subtitle, shift=DOWN * 0.10),
            run_time=0.8,
        )

        student = create_student().move_to([-5.1, -1.28, 0])
        robot = create_robot().move_to([5.1, -1.28, 0])
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
        dialogue = make_text("Obscure: Help me find 10, Zeno Sensei!", size=19, color=DARK)
        dialogue.move_to(self.dialogue_box)
        self.play(
            FadeIn(self.dialogue_box, shift=UP * 0.12),
            FadeIn(dialogue, scale=0.92),
            run_time=0.65,
        )
        # ----------------------------------------------------
        # Introduction: Obscure brings a real problem before the algorithm appears.
        # ----------------------------------------------------
        self.speak(
            "Zeno Sensei, I need your help! I have a sorted array with seven numbers, and I need to find ten. Do I have to check every number one at a time, or is there a faster way?",
            "student",
            Transform(dialogue, self.dialogue_line("Obscure: Is there a faster way than checking each number?", 17)),
            student.animate.shift(UP * 0.12),
            run_time=0.8,
        )
        self.speak(
            "Of course! Let me introduce you to binary search. It finds a target in a sorted array by checking "
            "the middle value. The comparison tells us which half can be discarded, so we repeat the process "
            "on a smaller range until we find the target or run out of values.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: Check the middle, then keep the possible half.", 16)),
            run_time=0.7,
        )

        # ----------------------------------------------------
        # Array and target - same values and positions as original
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
            "Here are the values, in order: two, four, six, eight, ten, twelve, and fourteen.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: The values are sorted from 2 to 14.", 16)),
            LaggedStart(*[FadeIn(cell, scale=0.82) for cell in cells], lag_ratio=0.10),
            FadeIn(index_labels),
            run_time=1.8,
        )
        self.speak(
            "Each value is greater than the one before it. That sorted order is our clue: comparing the middle tells us which side we can rule out.",
            "robot",
            LaggedStart(*[Indicate(cell, color=PURPLE) for cell in cells], lag_ratio=0.12),
            run_time=2.5,
        )

        target_label = make_text("TARGET", size=15, color=PURPLE)
        target_value = make_text("10", size=27, color=PINK)
        target_group = VGroup(target_label, target_value).arrange(RIGHT, buff=0.15)
        target_group.move_to([0, -0.78, 0])
        self.speak(
            "Our target is ten. We compare the middle value with ten and keep only the half that could still contain it.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: We compare each value with our target, 10.", 16)),
            FadeIn(target_group, scale=0.9),
            run_time=0.5,
        )
        self.speak(
            "Why does being sorted help? Do the numbers line up and confess?",
            "student",
            Transform(dialogue, self.dialogue_line("Obscure: Why does sorted help?", 17)),
            run_time=0.6,
        )
        self.speak(
            "If the middle is eight, every value before it is smaller too. Since our target is ten, we can rule out that whole side at once.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: Sorted order lets us rule out half at once.", 16)),
            Indicate(cells[3], color=PINK),
            Indicate(VGroup(*cells[0:3]), color=LAVENDER),
            run_time=2.0,
        )

        # ----------------------------------------------------
        # Explain low, high, and mid
        # ----------------------------------------------------
        def intro_marker_positions(low_index, mid_index, high_index):
            indices = {"low": low_index, "mid": mid_index, "high": high_index}
            positions = {}
            for index in set(indices.values()):
                occupants = [name for name in ("low", "mid", "high") if indices[name] == index]
                offsets = {1: (0.0,), 2: (0.27, -0.27), 3: (0.48, 0.0, -0.48)}[len(occupants)]
                for name, offset in zip(occupants, offsets):
                    positions[name] = [x_positions[index], 1.7 + offset, 0]
            return positions

        initial_positions = intro_marker_positions(0, 3, 6)
        low = make_text("LOW", size=17, color=PURPLE).move_to(initial_positions["low"])
        mid = make_text("MID", size=17, color=PINK).move_to(initial_positions["mid"])
        high = make_text("HIGH", size=17, color=PURPLE).move_to(initial_positions["high"])
        self.speak(
            "We track three indices. LOW and HIGH mark the ends of the active range; MID marks the position we inspect next. At the start, LOW is zero and HIGH is six.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: LOW and HIGH set the range; MID is our next check.", 16)),
            FadeIn(low, shift=DOWN * 0.12),
            FadeIn(mid, shift=DOWN * 0.12),
            FadeIn(high, shift=DOWN * 0.12),
            run_time=0.65,
        )
        active_range = make_array_range(cells, index_labels, 0, 6, LAVENDER)
        self.speak(
            "All seven positions are still candidates: LOW starts at zero and HIGH at six.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: All seven positions are still possible.", 16)),
            Create(active_range),
            run_time=0.8,
        )
        self.speak(
            "MID is halfway between LOW and HIGH. Add zero and six, divide by two, and keep the whole-number result: index three. Its value is eight.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: (0 + 6) / 2 gives MID = 3, value 8.", 16)),
            Indicate(cells[3], color=PINK, scale_factor=1.12),
            run_time=0.8,
        )

        # ----------------------------------------------------
        # Iteration 1: middle value 8, discard left section
        # ----------------------------------------------------
        self.speak(
            "Our first middle index is three, and its value is eight. Eight is not ten; it is smaller. So if ten is in the array, it must be somewhere to the right of index three.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: MID is 8, below 10, so search right.", 16)),
            run_time=0.9,
        )
        self.speak(
            "Eight is smaller than ten, so I see why we move right of eight. But why can we also throw away two, four, and six? We never compared those values with ten directly. "
            "They did nothing wrong.",
            "student",
            Transform(dialogue, self.dialogue_line("Obscure: Why rule out numbers we never checked?", 17)),
            run_time=0.55,
        )
        new_low = make_text("LOW", size=17, color=PURPLE).move_to(intro_marker_positions(4, 3, 6)["low"])
        right_range = SurroundingRectangle(
            VGroup(*cells[4:7]), color=PINK, buff=0.09, stroke_width=3
        )
        self.speak(
            "Because the array is sorted, two, four, and six are also below ten. We can rule out that whole side without checking each value.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: 2, 4, and 6 must also be too small.", 16)),
            Indicate(cells[3], color=PINK),
            Indicate(VGroup(*cells[0:3]), color=LAVENDER),
            run_time=2.0,
        )
        self.speak(
            "LOW moves to index four. Ten, twelve, and fourteen are the candidates that remain.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: Sorted order rules out 2, 4, and 6; LOW moves to 4.", 15)),
            low.animate.move_to(new_low),
            Transform(active_range, right_range),
            run_time=1.2,
        )

        # ----------------------------------------------------
        # Iteration 2: middle value 12, discard right section
        # ----------------------------------------------------
        new_mid = make_text("MID", size=17, color=PINK).move_to(intro_marker_positions(4, 5, 6)["mid"])
        self.speak(
            "The active range is indices four through six. Add the bounds, four and six, and divide by two: the new middle is index five. Its value is twelve, so we compare twelve with our target, ten.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: MID is index 5, where the value is 12.", 16)),
            mid.animate.move_to(new_mid),
            Indicate(cells[5], color=PINK, scale_factor=1.12),
            run_time=0.9,
        )
        self.speak(
            "Twelve is larger than ten. In a sorted array, twelve and everything after it are too large.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: 12 is too large; search to its left.", 16)),
            Indicate(VGroup(*cells[5:7]), color=LAVENDER),
            run_time=1.5,
        )
        self.speak(
            "Then we can discard twelve and fourteen because both are too large. The remaining candidates are ten and the value before it, right?",
            "student",
            Transform(dialogue, self.dialogue_line("Obscure: So we can rule out 12 and 14?", 17)),
            run_time=0.6,
        )
        new_high = make_text("HIGH", size=17, color=PURPLE).move_to(intro_marker_positions(4, 5, 4)["high"])
        final_range = SurroundingRectangle(cells[4], color=PINK, buff=0.10, stroke_width=3.2)
        self.speak(
            "Right. HIGH moves to one before MID, index four. LOW is already there, so one candidate remains: ten.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: LOW and HIGH meet at index 4: one candidate.", 16)),
            high.animate.move_to(new_high),
            Transform(active_range, final_range),
            run_time=0.7,
        )

        # ----------------------------------------------------
        # Iteration 3: target found
        # ----------------------------------------------------
        self.speak(
            "When low and high meet at index four, the middle is also index four. We check that last candidate. Its value is ten, exactly equal to our target.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: The last candidate is at index 4: value 10.", 16)),
            FadeOut(low),
            FadeOut(high),
            mid.animate.move_to(intro_marker_positions(4, 4, 4)["mid"]),
            Indicate(cells[4], color=PINK, scale_factor=1.18),
            run_time=0.9,
        )
        found_message = self.dialogue_line("Zeno Sensei: 10 found at index 4.", 16)
        self.speak(
            "The value is ten and our target is ten, so the comparison is equal. We found the target at index four. The search stops as soon as that equality check succeeds.",
            "robot",
            Transform(dialogue, found_message),
            cells[4][0].animate.set_fill(PINK, opacity=0.28),
            cells[4][0].animate.set_stroke(PINK, width=4),
            run_time=0.8,
        )
        self.speak(
            "I get it! We keep cutting the possible values in half.",
            "student",
            Transform(dialogue, self.dialogue_line("Obscure: We keep cutting the possible values in half!", 17)),
            student.animate.shift(UP * 0.18),
            robot.animate.shift(UP * 0.18),
            rate_func=there_and_back,
            run_time=0.65,
        )
        success = make_text("FOUND IN 3 COMPARISONS!", size=21, color=PURPLE)
        success.move_to([0, -1.55, 0])
        self.speak(
            "Three comparisons found ten: we ruled out the left half, then the right, and checked the final candidate.",
            "robot",
            Transform(dialogue, self.dialogue_line("Zeno Sensei: Three checks found 10 by halving the range.", 16)),
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

        trace_title = make_heading(
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
                line, font="Consolas", font_size=15,
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

        marker_mobjects = {}

        def marker_positions(low_index, mid_index, high_index):
            """Keep distinct markers aligned; stack markers sharing one index."""
            indices = {"low": low_index, "mid": mid_index, "high": high_index}
            positions = {}
            for index in set(indices.values()):
                occupants = [
                    name for name in ("low", "mid", "high")
                    if indices[name] == index
                ]
                offsets = {
                    1: (0.0,),
                    2: (0.27, -0.27),
                    3: (0.48, 0.0, -0.48),
                }[len(occupants)]
                for name, offset in zip(occupants, offsets):
                    positions[name] = [trace_x[index], 1.65 + offset, 0]
            return positions

        def marker_moves(low_index, mid_index, high_index, names=("low", "mid", "high")):
            positions = marker_positions(low_index, mid_index, high_index)
            return [
                marker_mobjects[name].animate.move_to(positions[name])
                for name in names
            ]

        initial_marker_positions = marker_positions(0, 3, 6)
        low_marker = make_text("LOW", size=14, color=PURPLE).move_to(initial_marker_positions["low"])
        mid_marker = make_text("MID", size=14, color=PINK).move_to(initial_marker_positions["mid"])
        high_marker = make_text("HIGH", size=14, color=PURPLE).move_to(initial_marker_positions["high"])
        marker_mobjects.update(low=low_marker, mid=mid_marker, high=high_marker)
        trace_target = make_text("TARGET = 10", size=19, color=PINK).move_to([-3.45, -0.65, 0])
        trace_state = make_text("low = 0     high = 6     mid = none", size=17, color=DARK)
        trace_state.move_to([-3.45, -1.35, 0])
        trace_result = make_text("Result: searching...", size=17, color=PURPLE).move_to([-3.45, -2.15, 0])
        current_highlight = code_highlight(0)

        self.speak(
            "Now let us slow down and let the code drive every decision. "
            "Watch the highlighted line, the three markers, and the state below the array.",
            "robot",
            FadeIn(trace_title), FadeIn(trace_panel),
            FadeIn(trace_cells), FadeIn(trace_indices),
            FadeIn(low_marker), FadeIn(mid_marker), FadeIn(high_marker),
            FadeIn(trace_target), FadeIn(trace_state), FadeIn(trace_result),
            FadeIn(current_highlight), FadeIn(code_group),
            run_time=1.4,
        )

        def focus_code(narration, line_index, *animations, speaker="robot", run_time=1.0):
            nonlocal current_highlight
            next_highlight = code_highlight(line_index)
            self.speak(
                narration,
                speaker,
                Transform(current_highlight, next_highlight),
                *animations,
                run_time=run_time,
            )

        """Legacy rapid trace retained temporarily for scene-edit comparison.
        focus_code(1, run_time=0.55)
        focus_code(2, run_time=0.55)
        focus_code(3, Indicate(trace_cells[3], color=PINK), run_time=0.8)
        self.play(Transform(
            trace_state,
            make_text("low = 0     high = 6     mid = 3  ->  arr[3] = 8", size=16, color=DARK)
                .move_to(trace_state),
        ), run_time=0.65)
        focus_code(4, run_time=0.45)  # Equality check is false for 8.
        focus_code(5, run_time=0.55)
        self.play(
            low_marker.animate.move_to([trace_x[4], 1.55, 0]),
            Transform(
                trace_state,
                make_text("8 < 10  ->  low = mid + 1 = 4", size=17, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=0.75,
        )
        focus_code(2, run_time=0.45)
        focus_code(3, mid_marker.animate.move_to([trace_x[5], 1.55, 0]), Indicate(trace_cells[5], color=PINK), run_time=0.8)
        self.play(Transform(
            trace_state,
            make_text("low = 4     high = 6     mid = 5  ->  arr[5] = 12", size=16, color=DARK)
                .move_to(trace_state),
        ), run_time=0.65)
        focus_code(4, run_time=0.45)  # Equality check is false for 12.
        focus_code(6, run_time=0.55)
        self.play(
            high_marker.animate.move_to([trace_x[4], 1.55, 0]),
            Transform(
                trace_state,
                make_text("12 > 10  ->  high = mid - 1 = 4", size=17, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=0.75,
        )
        focus_code(2, run_time=0.45)
        focus_code(3, mid_marker.animate.move_to([trace_x[4], 1.55, 0]), Indicate(trace_cells[4], color=PINK), run_time=0.8)
        self.play(Transform(
            trace_state,
            make_text("low = high = mid = 4  ->  arr[4] = 10", size=16, color=DARK)
                .move_to(trace_state),
        ), run_time=0.65)
        focus_code(4, run_time=0.6)
        self.play(
            trace_cells[4][0].animate.set_fill(PINK, opacity=0.28),
            Transform(
                trace_result,
                make_text("return mid -> index 4", size=20, color=PURPLE)
                    .move_to(trace_result),
            ),
            run_time=0.75,
        )
        """

        # Initialize bounds, then trace every comparison and branch at voiceover pace.
        focus_code(
            "First, low starts at zero: the leftmost index we are still considering.",
            0,
            run_time=1.1,
        )
        focus_code(
            "Next, high starts at the final index, six. The whole sorted array is currently in play.",
            1,
            run_time=1.1,
        )
        focus_code(
            "The while loop continues only while low is less than or equal to high. "
            "In other words, while at least one possible index remains.",
            2,
            run_time=1.2,
        )
        focus_code(
            "We calculate the middle: zero plus half the distance to six gives index three. "
            "The value at index three is eight.",
            3,
            Indicate(trace_cells[3], color=PINK),
            Transform(
                trace_state,
                make_text("low = 0     high = 6     mid = 3  ->  arr[3] = 8", size=16, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=1.4,
        )
        focus_code(
            "The equality check asks whether eight is our target, ten. It is not, so the search continues.",
            4,
            run_time=1.1,
        )
        self.speak(
            "Eight is too small. Does low move past it now?",
            "student",
            run_time=0.8,
        )
        focus_code(
            "Yes. Eight is smaller than ten, and the array is sorted, so every value through index three is too small. "
            "The code moves low to mid plus one: index four.",
            5,
            *marker_moves(4, 3, 6, names=("low",)),
            Transform(
                trace_state,
                make_text("8 < 10  ->  low = mid + 1 = 4", size=17, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=1.5,
        )
        focus_code(
            "The loop checks again. Low is four and high is six, so there are still candidates to inspect.",
            2,
            run_time=1.1,
        )
        focus_code(
            "The new middle is index five. Its value is twelve.",
            3,
            *marker_moves(4, 5, 6, names=("mid",)),
            Indicate(trace_cells[5], color=PINK),
            Transform(
                trace_state,
                make_text("low = 4     high = 6     mid = 5  ->  arr[5] = 12", size=16, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=1.4,
        )
        focus_code(
            "Twelve is not equal to ten, so again we choose the correct half rather than checking items one by one.",
            4,
            run_time=1.1,
        )
        self.speak(
            "Twelve is too large, so high runs back to the left?",
            "student",
            run_time=0.8,
        )
        focus_code(
            "Exactly. Because twelve is larger than ten, twelve and everything to its right are too large. "
            "High becomes mid minus one: index four. LOW and HIGH now stack at index four.",
            6,
            *marker_moves(4, 5, 4, names=("low", "high")),
            Transform(
                trace_state,
                make_text("12 > 10  ->  high = mid - 1 = 4", size=17, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=1.5,
        )
        focus_code(
            "The loop continues because low and high are both four. One candidate remains.",
            2,
            run_time=1.1,
        )
        focus_code(
            "The middle is now index four. Since low, mid, and high all point there, the labels stack neatly instead of overlapping.",
            3,
            *marker_moves(4, 4, 4),
            Indicate(trace_cells[4], color=PINK),
            Transform(
                trace_state,
                make_text("low = high = mid = 4  ->  arr[4] = 10", size=16, color=DARK)
                    .move_to(trace_state),
            ),
            run_time=1.5,
        )
        focus_code(
            "This time the equality check succeeds: the value at index four is ten, our target.",
            4,
            run_time=1.2,
        )
        self.speak(
            "The method returns mid, which is index four. We found ten without checking every value.",
            "robot",
            trace_cells[4][0].animate.set_fill(PINK, opacity=0.28),
            Transform(
                trace_result,
                make_text("return mid -> index 4", size=20, color=PURPLE)
                    .move_to(trace_result),
            ),
            run_time=1.3,
        )
        scenario_dialogue = self.dialogue_line(
            "Obscure: Can we try a few more searches?", 17
        )
        self.speak(
            "Can we try a few more searches and see how the steps change?",
            "student",
            FadeOut(VGroup(
                trace_title, trace_panel, code_group, current_highlight,
                trace_cells, trace_indices, low_marker, mid_marker, high_marker,
                trace_target, trace_state, trace_result,
            )),
            FadeIn(student, shift=UP * 0.18),
            FadeIn(robot, shift=UP * 0.18),
            FadeIn(self.dialogue_box, shift=UP * 0.12),
            FadeIn(scenario_dialogue, scale=0.92),
            run_time=0.8,
        )
        scenario_intro_title = make_heading(
            "Let's Explore Three Scenarios", size=29, color=DARK
        ).move_to([0, 3.15, 0])
        self.play(FadeIn(scenario_intro_title, shift=DOWN * 0.12), run_time=0.5)
        self.speak(
            "Absolutely. We'll try an immediate match, a target found after narrowing the range, "
            "and one that is not in the array.",
            "robot",
            Transform(
                scenario_dialogue,
                self.dialogue_line(
                    "Zeno Sensei: Let's try an instant match, a narrowed search, and a miss.",
                    15,
                ),
            ),
            run_time=0.8,
        )
        self.play(
            FadeOut(Group(
                scenario_intro_title, student, robot,
                self.dialogue_box, scenario_dialogue,
            )),
            run_time=0.6,
        )

        # ----------------------------------------------------
        # Additional scenarios: best case, early success, and not found
        # ----------------------------------------------------

        def scenario_card(title_text, target, steps, result_text, result_color=PURPLE):
            """Show each scenario with moving bounds, midpoint, and active range."""
            heading = make_heading(title_text, size=27, color=DARK).move_to([0, 2.85, 0])
            scenario_student = create_student().scale_to_fit_height(1.55)
            scenario_student.move_to([-5.65, -2.45, 0])
            scenario_robot = create_robot().scale_to_fit_height(1.55)
            scenario_robot.move_to([5.65, -2.45, 0])
            scenario_values = [2, 4, 6, 8, 10, 12, 14]
            row = VGroup()
            labels = VGroup()
            cell_x = [(i - 3) * 0.91 for i in range(7)]

            for i, value in enumerate(scenario_values):
                cell, index_label = make_cell(value, i, cell_x[i])
                row.add(cell)
                labels.add(index_label)

            row.shift(DOWN * 0.15)
            labels.shift(DOWN * 0.15)

            target_text = make_text(f"TARGET: {target}", size=21, color=PINK)
            target_text.move_to([4.55, 0.40, 0])

            explanation = make_text(
                "Begin with the complete sorted array.", size=16, color=DARK
            ).move_to([0, -1.05, 0])
            counter = make_text("Comparisons: 0", size=18, color=PURPLE)
            counter.move_to([0, -1.75, 0])

            def marker_positions(low_index, mid_index, high_index):
                indices = {"low": low_index, "mid": mid_index, "high": high_index}
                positions = {}
                for index in set(indices.values()):
                    occupants = [name for name in ("low", "mid", "high") if indices[name] == index]
                    offsets = {
                        1: (0.0,),
                        2: (0.27, -0.27),
                        3: (0.48, 0.0, -0.48),
                    }[len(occupants)]
                    for name, offset in zip(occupants, offsets):
                        positions[name] = [cell_x[index], 1.50 + offset, 0]
                return positions

            low_bound = 0
            high_bound = len(scenario_values) - 1
            mid_index = steps[0][0]
            initial_positions = marker_positions(low_bound, mid_index, high_bound)
            low_marker = make_text("LOW", size=14, color=PURPLE).move_to(initial_positions["low"])
            mid_marker = make_text("MID", size=14, color=PINK).move_to(initial_positions["mid"])
            high_marker = make_text("HIGH", size=14, color=PURPLE).move_to(initial_positions["high"])
            active_range = make_array_range(
                row, labels, low_bound, high_bound, LAVENDER
            )

            if target == 8:
                opening = (
                    "First, the best case. The target is eight, which is already at the first middle index, "
                    "so one comparison should be enough."
                )
            elif target == 4:
                opening = (
                    "Next, look for four. The first middle is too large, so we will keep the left half "
                    "and check its middle."
                )
            else:
                opening = (
                    "Finally, look for eleven, which is not in this array. We will keep narrowing the "
                    "range until LOW passes HIGH and no candidate remains."
                )

            opening_text = make_text(opening, size=15, color=DARK).move_to(explanation)
            self.speak(
                opening,
                "robot",
                FadeIn(heading), FadeIn(row), FadeIn(labels),
                FadeIn(target_text), Transform(explanation, opening_text), FadeIn(counter),
                FadeIn(low_marker), FadeIn(mid_marker), FadeIn(high_marker),
                Create(active_range),
                FadeIn(scenario_student, shift=UP * 0.12),
                FadeIn(scenario_robot, shift=UP * 0.12),
                run_time=1.0,
            )

            for step_index, (mid_index, message) in enumerate(steps):
                value = scenario_values[mid_index]
                next_low, next_high = low_bound, high_bound
                if value == target:
                    branch_explanation = (
                        f"The value {value} equals the target, so we stop after this comparison."
                    )
                elif value < target:
                    next_low = mid_index + 1
                    branch_explanation = (
                        f"{value} is below {target}. Since the list is sorted, every value through "
                        f"index {mid_index} is too small. LOW moves to index {next_low}."
                    )
                else:
                    next_high = mid_index - 1
                    branch_explanation = (
                        f"{value} is above {target}. Since the list is sorted, this value and everything "
                        f"after it are too large. HIGH moves to index {next_high}."
                    )

                display_explanation = f"{message}\n{branch_explanation}"
                next_explanation = make_text(
                    display_explanation, size=14, color=DARK, line_spacing=0.85
                ).scale_to_fit_width(11.8).move_to(explanation)
                next_counter = make_text(
                    f"Comparisons: {step_index + 1}", size=18, color=PURPLE
                ).move_to(counter)

                next_mid = (
                    steps[step_index + 1][0]
                    if value != target and step_index + 1 < len(steps)
                    else mid_index
                )
                next_positions = marker_positions(next_low, next_mid, next_high)
                marker_animations = [
                    low_marker.animate.move_to(next_positions["low"]),
                    mid_marker.animate.move_to(next_positions["mid"]),
                    high_marker.animate.move_to(next_positions["high"]),
                ]
                if next_low <= next_high:
                    next_range = make_array_range(
                        row, labels, next_low, next_high, PINK
                    )
                    marker_animations.append(Transform(active_range, next_range))
                else:
                    marker_animations.append(FadeOut(active_range))

                self.speak(
                    f"{message} {branch_explanation}",
                    "robot",
                    Indicate(row[mid_index], color=PINK, scale_factor=1.12),
                    *marker_animations,
                    Transform(explanation, next_explanation),
                    Transform(counter, next_counter),
                    run_time=1.0,
                )
                low_bound, high_bound = next_low, next_high

            final_result = make_text(result_text, size=21, color=result_color)
            final_result.move_to([0, -2.55, 0])
            self.speak(
                result_text,
                "robot",
                FadeIn(final_result, scale=0.9),
                run_time=0.8,
            )

            self.play(
                FadeOut(Group(
                    heading, row, labels, target_text, explanation, counter,
                    final_result, low_marker, mid_marker, high_marker, active_range,
                    scenario_student, scenario_robot,
                )),
                run_time=0.8,
            )

        # Best case: the first midpoint is exactly the target.
        scenario_card(
            "Scenario 1 - Best Case: Found Immediately",
            8,
            [(3, "Middle index 3 has value 8.")],
            "FOUND after 1 comparison - Best case: O(1)",
        )

        # Early success: target is found after moving into the left half.
        scenario_card(
            "Scenario 2 - Early Success",
            4,
            [
                (3, "Check index 3: value 8."),
                (1, "Check index 1: value 4."),
            ],
            "FOUND after 2 comparisons",
        )

        # Unsuccessful search: demonstrate the range becoming empty.
        scenario_card(
            "Scenario 3 - Unsuccessful Search",
            11,
            [
                (3, "Check index 3: value 8."),
                (5, "Check index 5: value 12."),
                (4, "Check index 4: value 10."),
            ],
            "NOT FOUND - The search range is empty",
            result_color=PINK,
        )

        # Move straight from the scenarios into time complexity.
        self.play(
            FadeOut(Group(title, subtitle, student, robot, self.dialogue_box, dialogue,
                          cells, index_labels, target_group, low, high, mid,
                          active_range, success)),
            run_time=0.8,
        )

        # ----------------------------------------------------
        # Time complexity: demonstrate repeated halving
        # ----------------------------------------------------
        def section_title(text):
            return make_heading(text, size=30, color=DARK).move_to([0, 3.15, 0])

        complexity_title = section_title("Why Is the Time Complexity O(log n)?")

        explanation = make_text(
            "Imagine searching a sorted array containing 16 values.",
            size=19, color=DARK
        ).move_to([0, 2.25, 0])

        self.play(
            FadeIn(complexity_title), FadeIn(explanation),
            run_time=0.9,
        )
        self.speak(
            "Now let's see why the number of comparisons grows so slowly. Imagine a sorted array with sixteen possible values. We'll follow the candidates through each iteration.",
            "robot",
        )

        remaining_counts = [16, 8, 4, 2, 1]
        halving_rows = VGroup()

        halving_narration = [
            "We start with sixteen possible values. That's our whole search space.",
            "After the first comparison, at most eight candidates remain. One check lets us keep just the half that could contain the target.",
            "We don't start over; we check the middle of those eight. After the second comparison, at most four candidates remain.",
            "Same idea again: four possibilities become at most two.",
            "After the fourth comparison, at most one candidate remains. If it hasn't matched yet, we check that final value.",
        ]

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
                f"{count} possible candidates",
                size=15,
                color=DARK
            )

            row = VGroup(label, bar, count_label).arrange(RIGHT, buff=0.22)
            halving_rows.add(row)

        halving_rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        halving_rows.scale_to_fit_width(11.8)
        halving_rows.move_to([0, -0.15, 0])

        for step, row in enumerate(halving_rows):
            self.speak(
                halving_narration[step],
                "robot",
                FadeIn(row, shift=RIGHT * 0.12),
                run_time=0.65,
            )

        time_reason = make_text(
            "16 -> 8 -> 4 -> 2 -> 1: each check roughly halves candidates.",
            size=16, color=DARK
        ).move_to([0, -2.35, 0])

        # Use native text so this lesson can render without a LaTeX installation.
        time_formula = make_text(
            "2^k >= n   so   k is about log2(n) halvings", size=27, color=PURPLE
        ).scale_to_fit_width(11.8).move_to([0, -2.95, 0])

        self.play(
            FadeIn(time_reason),
            Write(time_formula),
            run_time=1.0
        )
        self.speak(
            "Each round halves the remaining search. Doubling the array adds only about one more halving step. "
            "A final candidate may still need checking, but the growth remains logarithmic: O of log n.",
            "robot",
            Indicate(halving_rows, color=PURPLE),
            Indicate(time_formula, color=PINK),
            run_time=2.0,
        )

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

        space_formula = make_text(
            "constant number of variables means O(1)", size=27, color=PINK
        ).scale_to_fit_width(11.8).move_to([0, -1.55, 0])

        recursion_note = make_text(
            "No new array and no recursive call stack in this iterative version.",
            size=16,
            color=PURPLE
        ).move_to([0, -2.35, 0])

        self.play(
            FadeOut(VGroup(
                complexity_title, explanation, halving_rows, time_reason, time_formula
            )),
            FadeIn(space_title),
            FadeIn(array_label),
            FadeIn(memory_array),
            run_time=1.0,
        )

        self.speak(
            "The input array already exists, so we are measuring the extra memory used by the search. "
            "The array itself is not copied.",
            "robot",
        )

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

        self.speak(
            "The algorithm keeps only three indices: low, high, and mid. Their number stays the same "
            "whether the array has seven items or seven million.",
            "robot",
        )

        self.play(
            Write(space_formula),
            FadeIn(recursion_note),
            run_time=1.0
        )

        self.speak(
            "Because this is iterative, it creates no recursive call stack and no additional array. "
            "The extra space is constant, O of one.",
            "robot",
        )

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

        self.speak(
            "To summarize, iterative binary search takes O of log n time in the worst case and O of one "
            "extra space. Next, let's read the complete Java implementation.",
            "robot",
        )

        # ----------------------------------------------------
        # Complete Java implementation - split across two pages
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
                font="Consolas",
                font_size=17,
                line_spacing=0.78,
                color=DARK,
                disable_ligatures=True,
            )

            code_text.scale_to_fit_width(11.9)
            code_text.scale_to_fit_height(5.05)
            code_text.move_to(code_panel.get_center())

            page_label = make_text(
                "Complete iterative binary search - Java",
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

            if page_index == 0:
                page_narration = (
                    "LOW and HIGH bound the active range. While it is nonempty, we check MID and move one "
                    "bound inward. The midpoint formula avoids integer overflow."
                )
            else:
                page_narration = (
                    "If no match is found, the method returns minus one. Here we search a sorted array for "
                    "ten and get index four. The input must be sorted for the decisions to work."
                )
            self.speak(page_narration, "robot")

            code_title_prev = code_title
            code_panel_prev = code_panel
            code_text_prev = code_text
            page_label_prev = page_label

        closing_dialogue_box = RoundedRectangle(
            width=8.35, height=0.78, corner_radius=0.18,
            stroke_color=PURPLE, stroke_width=2.2,
            fill_color=WHITE, fill_opacity=1,
        ).move_to([0, -3.28, 0])
        self.dialogue_box = closing_dialogue_box
        closing_dialogue = make_text(
            "Obscure: Thank you, Zeno Sensei, for helping me understand binary search!",
            size=15,
            color=DARK,
        ).scale_to_fit_width(7.95).move_to(closing_dialogue_box)

        self.speak(
            "Thank you, Zeno Sensei, for helping me understand binary search! "
            "Now I see how checking the middle helps us narrow down the search.",
            "student",
            FadeOut(VGroup(
                code_title_prev, code_panel_prev, code_text_prev, page_label_prev
            )),
            FadeIn(title),
            FadeIn(subtitle),
            FadeIn(student, shift=UP * 0.18),
            FadeIn(robot, shift=UP * 0.18),
            FadeIn(closing_dialogue_box, shift=UP * 0.12),
            FadeIn(closing_dialogue, scale=0.92),
            run_time=0.9,
        )
        self.speak(
            "You're welcome, Obscure! Keep practicing, and you'll be a binary search expert in no time.",
            "robot",
            Transform(
                closing_dialogue,
                self.dialogue_line(
                    "Zeno Sensei: You're welcome! Keep practicing, Obscure.", 16
                ),
            ),
            robot.animate.shift(UP * 0.08),
            run_time=0.8,
        )

        # Close with the creator's subscribe artwork and a spoken call to action.
        outro_image = ImageMobject(
            str(SUBSCRIBE_IMAGE),
            scale_to_resolution=1080,
            resampling_algorithm=RESAMPLING_ALGORITHMS["bicubic"],
        )
        outro_image.scale_to_fit_height(4.85).move_to([-3.6, -0.05, 0])

        outro_title = make_heading(
            "Keep learning with me!", size=30, color=DARK
        ).move_to([2.0, 1.35, 0])
        outro_actions = make_heading(
            "LIKE   SHARE   SUBSCRIBE", size=21, color=PURPLE
        ).move_to([2.0, 0.35, 0])
        outro_message = make_text(
            "More coding concepts, explained one step at a time.",
            size=18,
            color=DARK,
        ).move_to([2.0, -0.55, 0])
        outro_thanks = make_text(
            "Thanks for learning with us!", size=18, color=PINK
        ).move_to([2.0, -1.35, 0])

        self.speak(
            "If you enjoyed learning binary search with us, please like and share this video, "
            "and subscribe if you want to learn more coding concepts with me. We will keep "
            "breaking each idea down one step at a time. Thanks for learning with us!",
            "student",
            FadeOut(Group(
                title, subtitle, student, robot,
                closing_dialogue_box, closing_dialogue,
            )),
            FadeIn(outro_image, scale=0.92),
            FadeIn(outro_title, shift=UP * 0.12),
            FadeIn(outro_actions, shift=UP * 0.08),
            FadeIn(outro_message),
            FadeIn(outro_thanks),
            run_time=0.9,
        )
        self.speak(
            "Thanks for watching!",
            "student",
            FadeOut(Group(
                outro_image, outro_title, outro_actions, outro_message, outro_thanks
            )),
            run_time=0.8,
        )

        
