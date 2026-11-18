"""AI Universe, opening + foundations. Cached narration; set LWO_DISABLE_VOICEOVER=1 for a silent preview.

Run: uv run manim --disable_caching -pql src/learnwithobscure/scenes/ai_universe.py AIUniverseFoundations
"""
import os
from manim import *
from manimpango import list_fonts
from math import ceil
from learnwithobscure.scenes.ai_universe_audio import clip_path, duration as audio_duration, preflight

from learnwithobscure.scenes.bubble_sort import (
    BG, DARK, PURPLE, LAVENDER, PINK, WHITE,
    STUDENT_IMAGE, ROBOT_IMAGE, create_character,
)

_fonts = {name.casefold(): name for name in list_fonts()}
FONT = next((_fonts[f.casefold()] for f in
             ("Poppins", "Montserrat", "Inter", "Segoe UI", "Arial",
              "DejaVu Sans", "Liberation Sans", "Noto Sans")
             if f.casefold() in _fonts), "sans-serif")


# Only reviewed artwork may be selected here. Never replace the master PNGs.
EXPRESSION_DIR = STUDENT_IMAGE.parent / "expressions"
EXPRESSION_ASSETS = {
    "student": {
        "confused": EXPRESSION_DIR / "obscure_confused.png",
        "questioning": EXPRESSION_DIR / "obscure_questioning.png",
        **{pose: EXPRESSION_DIR / f"obscure_{pose}.png"
           for pose in ("speaking", "thoughtful", "surprised", "blink", "happy")},
    },
    "robot": {
        pose: EXPRESSION_DIR / f"zeno_{pose}.png"
        for pose in ("speaking", "thoughtful", "surprised", "blink", "happy")
    },
}
MASTER_ASSETS = {"student": STUDENT_IMAGE, "robot": ROBOT_IMAGE}


def txt(value, size=32, color=DARK, width=11.8, height=1.35, bold=True):
    obj = Text(value, font=FONT, font_size=size, color=color,
               weight="BOLD" if bold else "NORMAL", line_spacing=1.05)
    obj.scale(min(1, width / obj.width, height / obj.height))
    return obj


def box(w, h, fill=WHITE, stroke=PURPLE, radius=.19):
    return RoundedRectangle(width=w, height=h, corner_radius=radius,
                            stroke_color=stroke, stroke_width=2,
                            fill_color=fill, fill_opacity=1)


def tag(value, size=23, fill=WHITE, color=DARK, width=3.4):
    label = txt(value, size, color, width=width-.35, height=.7)
    back = box(label.width+.38, label.height+.27, fill)
    return VGroup(back, label.move_to(back))


def pos(x, y):
    return RIGHT*x + UP*y


def arrow(a, b, color=PURPLE):
    return Arrow(a, b, buff=.13, color=color, stroke_width=5,
                 max_tip_length_to_length_ratio=.20)


def envelope(label, spam=False):
    shell = box(1.63, .88, fill=WHITE, stroke=PURPLE)
    seam = VMobject(color=LAVENDER, stroke_width=2).set_points_as_corners([
        shell.get_corner(UL)+DR*.13, shell.get_center()+DOWN*.13,
        shell.get_corner(UR)+DL*.13])
    badge = txt(label, 17, color=PURPLE if spam else DARK, width=1.4)
    badge.move_to(shell.get_center()+DOWN*.25)
    return VGroup(shell, seam, badge)


class AIUniverseFoundations(Scene):
    """First milestone only. Stable dialogue IDs make later audio integration easy."""

    def construct(self):
        if os.getenv("LWO_DISABLE_VOICEOVER") != "1":
            preflight()
        self.camera.background_color = BG
        self.caption = None
        self.dialogue_ids = set()
        self.characters = {}
        missing = [path for poses in EXPRESSION_ASSETS.values()
                   for path in poses.values() if not path.is_file()]
        if missing:
            message = ("Missing approved expression assets: "
                       + ", ".join(str(p.name) for p in missing)
                       + ". Put them in assets/characters/expressions/.")
            if os.getenv("LWO_REQUIRE_EXPRESSION_ASSETS") == "1":
                raise FileNotFoundError(message)
            print(message + " Using the original character as a fallback.")
        self.opening()
        self.ai_example()
        self.ml_example()
        self.deep_example()
        self.recap()
        self.wait(.5)

    def stage(self):
        # Keep one composition per teaching beat, never leave stale objects.
        if self.mobjects:
            self.play(*[FadeOut(m) for m in list(self.mobjects)], run_time=.42)
            self.clear()
        self.caption = None
        self.characters = {}
        halo = Circle(radius=3, stroke_width=0, fill_color=WHITE,
                      fill_opacity=.37).move_to(pos(6.3, 2.45))
        arc = Circle(radius=2.6, color=LAVENDER, stroke_width=3,
                     stroke_opacity=.45).move_to(pos(-7.35,-1.8))
        self.add(halo, arc)

    def title(self, value, subtitle=None):
        heading = txt(value, 46, PURPLE, width=12.6, height=.72).move_to(UP*3.32)
        self.play(FadeIn(heading, shift=DOWN*.17), run_time=.44)
        if subtitle:
            sub = txt(subtitle, 22, DARK, width=11.5, height=.4,
                      bold=False).move_to(UP*2.65)
            self.play(FadeIn(sub), run_time=.25)
        return heading

    def character(self, who, height, x, y, max_width=None):
        # Group remains the same scene object when its resident image changes.
        # This preserves all existing scene animations and avoids morphing pixels.
        image = create_character(MASTER_ASSETS[who], height)
        if max_width and image.width > max_width:
            image.scale_to_fit_width(max_width)
        sprite = Group(image).move_to(pos(x,y))
        self.characters[who] = sprite
        sprite.expression_path = MASTER_ASSETS[who]
        if (sprite.get_bottom()[1] < -2.60 or
                abs(sprite.get_center()[0]) + sprite.width/2 > config.frame_width/2-.10):
            raise ValueError("Character outside its safe layout area: " + who)
        return sprite

    def react(self, who, pose=None, motion=None):
        """Switch just the artwork, then use a short non-drifting reaction."""
        sprite = self.characters.get(who)
        if sprite is None or sprite not in self.mobjects:
            return 0.0  # Speaker has not entered this shot yet.
        if pose is not None:
            path = EXPRESSION_ASSETS[who].get(pose, MASTER_ASSETS[who])
            if not path.is_file():
                path = MASTER_ASSETS[who]
            if path != sprite.expression_path:
                previous = sprite[0]
                replacement = create_character(path, previous.height)
                if replacement.width > previous.width:
                    replacement.scale_to_fit_width(previous.width)
                replacement.move_to(previous).align_to(previous, DOWN)
                sprite.remove(previous)
                sprite.add(replacement)
                sprite.expression_path = path
        if motion == "question":
            self.play(sprite.animate.shift(UP*.12), rate_func=there_and_back, run_time=.45)
        elif motion == "think":
            self.play(sprite.animate.rotate(.045), rate_func=there_and_back, run_time=.45)
        elif motion == "realize":
            self.play(sprite.animate.shift(UP*.16), rate_func=there_and_back, run_time=.42)
        elif motion == "nod":
            self.play(sprite.animate.shift(DOWN*.075), rate_func=there_and_back, run_time=.40)
        else:
            return 0.0
        return .45 if motion in ("question","think") else (.42 if motion == "realize" else .40)

    def say(self, key, who, line, *animations, seconds=None, pose=None, reaction=None):
        """Narrated dialogue beat with optional approved pose and timed reaction."""
        if key in self.dialogue_ids:
            raise ValueError("Duplicate dialogue ID: " + key)
        self.dialogue_ids.add(key)
        speaker = "Obscure" if who == "student" else "Zeno Sensei"
        # Reserve the bottom 1.35 units: no teaching object should obscure it.
        panel = box(12.85, 1.12, fill=WHITE, stroke=LAVENDER).move_to(DOWN*3.22)
        name = txt(speaker, 20, PURPLE, width=2.15, height=.32)
        name.move_to(pos(-5.10,-3.22))
        divider = Line(pos(-3.94,-3.63), pos(-3.94,-2.81),
                       color=LAVENDER, stroke_width=2)
        # Wrap by words; fit both lines if a long line cannot fit at full size.
        import textwrap
        words = "\n".join(textwrap.wrap(line, width=63))
        body = txt(words, 29, DARK, width=9.7, height=.86,
                   bold=False).move_to(pos(1.08,-3.22))
        current = VGroup(panel, name, divider, body).set_z_index(20)
        if self.caption is not None:
            self.remove(self.caption)
        self.add(current)
        self.caption = current
        duration = seconds if seconds is not None else max(2.4, len(line.split())/2.9+.4)
        if os.getenv("LWO_DISABLE_VOICEOVER") != "1":
            audio = clip_path(line, who)
            duration = max(duration, audio_duration(audio) + .15)
            self.add_sound(str(audio))
        # Preserve explicit emotional poses; otherwise use the speaking sprite.
        pose = pose or {"question": "surprised", "think": "thoughtful",
                        "realize": "happy", "nod": "speaking"}.get(reaction, "speaking")
        listener = "robot" if who == "student" else "student"
        self.react(listener, "neutral")
        # Keep the total dialogue duration unchanged after adding reactions.
        start = self.time
        if pose is not None or reaction is not None:
            self.react(who, pose, reaction)
        remaining = max(1/config.frame_rate, duration-(self.time-start))
        if animations:
            self.play(*animations, run_time=min(1.10, remaining))
        remaining = duration-(self.time-start)
        if remaining > .9 and who in self.characters:
            # A brief blink between phrases; optional reviewed artwork only.
            blink = EXPRESSION_ASSETS[who].get("blink")
            if blink and blink.is_file():
                self.wait(.35)
                self.react(who, "blink")
                self.wait(max(1, ceil(.12 * config.frame_rate)) / config.frame_rate)
                self.react(who, pose)
        remaining = duration-(self.time-start)
        if remaining > 0:
            self.wait(ceil(remaining * config.frame_rate) / config.frame_rate)
        self.react(who, "neutral")

    def opening(self):
        self.stage()
        student = self.character("student", 3.6, 0, -.27)
        self.play(FadeIn(student, shift=UP*.4, scale=.85), run_time=.65)
        chips = VGroup()
        terms = [
            ("LLM", -4.7, 1.65), ("RAG", 4.6, 1.85),
            ("Generative AI", -4.25, .23), ("Agentic AI",4.30,.48),
            ("Deep Learning",-4.05,-1.35), ("MCP",4.65,-1.25),
            ("GPT",0,2.55),
        ]
        for i,(label,x,y) in enumerate(terms):
            chips.add(tag(label, 26, fill=WHITE if i%2 else "#F6EAFD").move_to(pos(x,y)))
        self.say("intro-01","student",
                 "Generative AI, agentic AI, LLMs, RAG... wasn't everything just called AI yesterday?",
                 LaggedStart(*[GrowFromCenter(c) for c in chips], lag_ratio=.12),
                 pose="questioning", reaction="question")
        self.say("intro-02","student","ZENOOOO!",
                 student.animate.shift(UP*.23).scale(1.065), seconds=2.2,
                 pose="confused", reaction="question")
        robot = self.character("robot",3.45,4.25,-.12)
        self.say("intro-03","robot",
                 "Relax! You're mixing up techniques, models, capabilities and tools.",
                 FadeOut(chips, shift=UP*1.1), FadeIn(robot, shift=LEFT*1.7),
                 student.animate.move_to(pos(-4.0,-.1)))
        clusters = VGroup(*[tag(v, 24, fill=WHITE) for v in
                            ("TECHNIQUES","MODELS","CAPABILITIES","TOOLS")])
        clusters.arrange(DOWN,buff=.24).move_to(UP*.42)
        self.say("intro-04","student","There are categories now?!",
                 LaggedStart(*[GrowFromCenter(c) for c in clusters],lag_ratio=.12),
                 pose="questioning", reaction="question")
        self.say("intro-05","robot",
                 "Once you understand how these concepts fit together, everything gets simpler.",
                 Indicate(clusters,color=PURPLE,scale_factor=1.06), reaction="nod")
        self.say("intro-06","student","Fine. Start from the beginning.",seconds=2.6,
                 pose="neutral", reaction="nod")
        self.stage()
        headline = txt("THE AI UNIVERSE", 78, PURPLE, width=12.2).move_to(UP*.75)
        sub = txt("AI  /  ML  /  DL  /  LLMs  /  AGENTS",28,DARK).next_to(headline,DOWN,buff=.35)
        orbit = VGroup(*[Circle(radius=r,color=LAVENDER,stroke_width=2,
                                 stroke_opacity=.40) for r in (1.7,2.4,3.2)])
        self.add(orbit)
        self.play(GrowFromCenter(headline), FadeIn(sub,shift=UP*.2),
                  orbit.animate.rotate(.25),run_time=1.2)
        self.wait(1.4)

    def ai_example(self):
        self.stage()
        self.title("01  /  Artificial Intelligence", "AI is the broad field")
        robot = self.character("robot",2.30,-5.97,-1.23,max_width=1.58)
        student = self.character("student",2.25,5.97,-1.23,max_width=1.58)
        self.play(FadeIn(robot,shift=RIGHT*.5),FadeIn(student,shift=LEFT*.5),run_time=.5)
        board = VGroup()
        origin = pos(-3.05,1.65)
        sz=.72
        for r in range(4):
            for c in range(4):
                square = Square(side_length=sz,stroke_width=1,stroke_color=WHITE,
                                fill_color=WHITE if (r+c)%2==0 else LAVENDER,
                                fill_opacity=1).move_to(origin+RIGHT*c*sz+DOWN*r*sz)
                board.add(square)
        origin2 = board[12].get_center()
        start = VGroup(Circle(radius=.23,color=PURPLE,fill_color=PURPLE,fill_opacity=1),
                       txt("N",23,WHITE,width=.4,height=.38)).move_to(origin2)
        target = board[5].get_center()
        enemy = VGroup(Circle(radius=.23,color=DARK,fill_color=DARK,fill_opacity=1),
                       txt("P",23,WHITE,width=.4,height=.38)).move_to(target)
        chess = tag("Chess search",26,fill=WHITE).next_to(board,DOWN,buff=.24)
        idea = VGroup(txt("RULES",25,PURPLE),txt("+",25),txt("SEARCH",25,PURPLE))
        idea.arrange(DOWN,buff=.16).move_to(pos(1.1,.7))
        decisions = VGroup(*[tag(v,19) for v in ("Move A","Move B","Move C")])
        decisions.arrange(DOWN,buff=.17).move_to(pos(3.3,.7))
        self.say("ai-01","robot",
                 "Artificial intelligence is the broad field of making machines perform tasks associated with intelligence.",
                 FadeIn(board),FadeIn(start),FadeIn(enemy),FadeIn(chess))
        self.say("ai-02","student","So every AI learns from data?",
                 pose="questioning", reaction="question")
        self.say("ai-03","robot",
                 "Not necessarily. A chess program can search possible moves using predefined rules, without learning from data.",
                 FadeIn(idea),LaggedStart(*[FadeIn(d,shift=LEFT*.25) for d in decisions],
                                         lag_ratio=.15), reaction="nod")
        # The knight marker moves two up and one right; this is a legal capture.
        route = VMobject(color=PINK,stroke_width=6).set_points_as_corners([
            origin2,origin2+UP*sz*2,target])
        self.play(Create(route),run_time=.52)
        self.play(MoveAlongPath(start,route),FadeOut(enemy),run_time=.65)
        self.say("ai-04","student","So AI is the big umbrella. Learning is optional!",
                 pose="neutral", reaction="realize")
        self.say("ai-05","robot","Exactly. Now imagine rules that are hard to write by hand.",
                 Indicate(idea,color=PURPLE))

    def ml_example(self):
        self.stage()
        self.title("02  /  Machine Learning", "Learn from examples, rather than writing every rule")
        student = self.character("student",2.12,-6.03,-1.32,max_width=1.50)
        robot = self.character("robot",2.12,6.03,-1.32,max_width=1.50)
        self.play(FadeIn(student,shift=RIGHT*.5),FadeIn(robot,shift=LEFT*.5),run_time=.5)
        mails = VGroup(*[envelope(v,b) for v,b in
                         (("PRIZE!",True),("Meeting",False),("WIN NOW",True),
                          ("Project",False))]).arrange_in_grid(rows=2,cols=2,buff=.12)
        mails.move_to(pos(-3.48,.65))
        labels = VGroup(*[txt(t,18,PURPLE if spam else DARK,width=1.7)
                          .next_to(mail,DOWN,buff=.04)
                          for mail,(t,spam) in zip(mails,(("Spam",True),("Not spam",False),
                                                        ("Spam",True),("Not spam",False)))])
        # Re-space the rows to leave room for labels.
        for i, mail in enumerate(mails):
            mail.shift(UP*.19 if i<2 else DOWN*.19)
            labels[i].next_to(mail,DOWN,buff=.05)
        model = VGroup(box(2.25,2.35,fill="#F5EAFB"),
                       txt("ML\nMODEL",34,PURPLE,width=1.9,height=1.4)).move_to(pos(0,.65))
        train = arrow(pos(-1.73,.65),pos(-1.12,.65))
        data_title = txt("Labeled training data",23,PURPLE,width=3.5).move_to(pos(-3.48,2.0))
        out_title = txt("Learned patterns",23,PURPLE,width=3.8).move_to(pos(3.5,2.0))
        patterns = VGroup(tag("Message words",20),tag("Sender signals",20),
                          tag("Other features",20)).arrange(DOWN,buff=.21).move_to(pos(3.48,.65))
        out = arrow(pos(1.14,.65),pos(2.10,.65))
        self.say("ml-01","student","Writing rules for every spam email sounds impossible.",
                 FadeIn(data_title),LaggedStart(*[FadeIn(m,shift=RIGHT*.3) for m in mails],
                                                 lag_ratio=.12),FadeIn(labels), pose="confused", reaction="think")
        self.say("ml-02","robot",
                 "Machine learning lets a system learn patterns from data. Here we have emails labeled spam or not spam.",
                 FadeIn(model,scale=.85),GrowArrow(train), reaction="nod")
        self.say("ml-03","robot",
                 "During training, the model learns useful signals. It can then classify new emails it hasn't seen before.",
                 GrowArrow(out),FadeIn(out_title),LaggedStart(*[GrowFromCenter(p) for p in patterns],
                                                             lag_ratio=.15))
        self.play(FadeOut(mails),FadeOut(labels),FadeOut(data_title),
                  FadeOut(patterns),FadeOut(out_title),FadeOut(train),FadeOut(out),run_time=.45)
        unseen = envelope("FREE GIFT",True).scale(1.20).move_to(pos(-3.45,.65))
        input_label = txt("New email",25).next_to(unseen,UP,buff=.35)
        outcome = tag("Likely spam",30,fill=PINK).move_to(pos(3.5,.65))
        predict_in = arrow(pos(-2.45,.65),pos(-1.12,.65))
        predict_out = arrow(pos(1.12,.65),pos(2.42,.65))
        self.say("ml-04","student","What happens when a completely new email arrives?",
                 FadeIn(unseen,shift=RIGHT*.4),FadeIn(input_label),GrowArrow(predict_in),
                 pose="questioning", reaction="question")
        self.say("ml-05","robot","The trained model predicts a label. It can still make mistakes.",
                 Indicate(model,color=PURPLE),GrowArrow(predict_out),GrowFromCenter(outcome))
        self.say("ml-06","student","Can we teach it to spot weekend messages from my manager?",
                 pose="confused", reaction="think")
        self.say("ml-07","robot","Technically, yes. Professionally, proceed with caution.",
                 reaction="nod")
        self.say("ml-08","student","Got it. Learning from data is what makes it machine learning.",
                 pose="neutral", reaction="realize")

    def deep_example(self):
        self.stage()
        self.title("03  /  Neural Networks & Deep Learning",
                   "Deep learning uses neural networks with multiple processing layers")
        robot = self.character("robot",2.12,6.03,-1.32,max_width=1.50)
        student = self.character("student",2.02,-6.03,-1.32,max_width=1.50)
        self.play(FadeIn(robot),FadeIn(student),run_time=.45)
        # A toy handwritten seven as a pixel grid; not a real trained model.
        bitmap = ("11111","00001","00010","00100","01000","01000","01000")
        pixels = VGroup()
        for r,row in enumerate(bitmap):
            for c,bit in enumerate(row):
                pixels.add(Square(side_length=.245,stroke_color=LAVENDER,stroke_width=1,
                                  fill_color=PURPLE if bit=="1" else WHITE,
                                  fill_opacity=1).move_to(pos(-4.77+c*.245,1.75-r*.245)))
        input_label = txt("Pixels",22).next_to(pixels,DOWN,buff=.17)
        xs=(-2.8,-.95,.90,2.75)
        ns=(5,5,4,3)
        layers=[]
        for x,n in zip(xs,ns):
            layer=VGroup(*[Circle(radius=.138,stroke_color=PURPLE,stroke_width=2,
                                  fill_color=WHITE,fill_opacity=1).move_to(
                                      pos(x, .65+(n-1-2*j)*.29)) for j in range(n)])
            layers.append(layer)
        links=[]
        for left,right in zip(layers,layers[1:]):
            links.append(VGroup(*[Line(a.get_center(),b.get_center(),color=LAVENDER,
                                       stroke_width=1.45,stroke_opacity=.60)
                                  for a in left for b in right]))
        labels = VGroup(*[txt(v,19,PURPLE,width=1.68).move_to(pos(x,-1.12))
                          for x,v in zip(xs,("Input","Hidden 1","Hidden 2","Output"))])
        digit = txt("7",86,PURPLE,width=1.25,height=1.3).move_to(pos(4.53,.65))
        result = txt("Prediction",20).next_to(digit,DOWN,buff=.23)
        self.say("dl-01","student","Where do neural networks come into this?",
                 FadeIn(pixels),FadeIn(input_label),FadeIn(layers[0]),FadeIn(labels[0]),
                 pose="questioning", reaction="question")
        self.say("dl-02","robot",
                 "A neural network has connected computational units that transform inputs using learned weights.",
                 Create(links[0]),FadeIn(layers[1]),FadeIn(labels[1]), reaction="nod")
        self.say("dl-03","robot",
                 "Deep learning uses networks with multiple processing layers. Later layers can combine simpler patterns into more complex ones.",
                 Create(links[1]),Create(links[2]),FadeIn(layers[2]),FadeIn(layers[3]),
                 FadeIn(labels[2]),FadeIn(labels[3]))
        # Pulses are a conceptual information-flow illustration, not training.
        for i, layer in enumerate(layers):
            self.play(*[n.animate.set_fill(PINK,opacity=1) for n in layer],
                      run_time=.23)
            if i < len(links):
                highlight = links[i].copy().set_stroke(color=PURPLE,width=2.3,opacity=.95)
                self.play(Create(highlight),run_time=.30)
                self.remove(highlight)
        self.say("dl-04","robot",
                 "For handwriting recognition, a trained network can turn pixel patterns into a digit prediction.",
                 GrowFromCenter(digit),FadeIn(result))
        self.say("dl-05","student","So multiple layers help it learn richer representations?",
                 pose="neutral", reaction="realize")
        self.say("dl-06","robot","Exactly. Not every machine-learning model is a deep neural network.")

    def recap(self):
        self.stage()
        self.title("How the pieces fit together")
        # Nested regions, not separate peer categories.
        outer = box(8.30,4.72,fill="#F3E9FA").move_to(pos(-1.1,.20))
        middle = box(6.50,3.65,fill="#D5BCE7").move_to(pos(-1.1,-.12))
        inner = box(4.55,2.50,fill=PURPLE).move_to(pos(-1.1,-.49))
        a=txt("ARTIFICIAL INTELLIGENCE",31,PURPLE,width=7.8).move_to(pos(-1.1,2.14))
        m=txt("MACHINE LEARNING",29,DARK,width=6.2).move_to(pos(-1.1,1.27))
        d=txt("DEEP LEARNING",28,WHITE,width=4.2).move_to(pos(-1.1,-.45))
        student=self.character("student",2.18,5.08,-.98,max_width=1.72)
        robot=self.character("robot",2.10,5.20,1.38,max_width=1.72)
        self.say("recap-01","student","AI is the broadest category.",
                 GrowFromCenter(outer),FadeIn(a),FadeIn(student))
        self.say("recap-02","student","Machine learning is inside AI.",
                 GrowFromCenter(middle),FadeIn(m), reaction="nod")
        self.say("recap-03","student","And deep learning is inside machine learning!",
                 GrowFromCenter(inner),FadeIn(d),FadeIn(robot,shift=LEFT*.4),
                 reaction="realize")
        self.say("recap-04","robot","Exactly. Three concepts unlocked.",
                 Indicate(d,color=WHITE,scale_factor=1.04), reaction="nod")
        self.stage()
        heading = self.title("QUICK CHALLENGE")
        question = txt("A chess program uses rules and search.\nIt does not learn from data.",36,
                       DARK,width=12.1,height=1.30)
        question.next_to(heading, DOWN, buff=.42).set_x(0)
        # Lay out the answers from the actual question bounds, not a fixed y.
        # Uniform rows also make the countdown and answer reveal easier to scan.
        options = VGroup()
        for value in ("A  /  AI only", "B  /  Machine learning", "C  /  Deep learning"):
            background = box(6.10, .68, fill=WHITE)
            label = txt(value, 29, width=5.65, height=.42).move_to(background)
            options.add(VGroup(background, label))
        options.arrange(DOWN, buff=.20)
        gap = .42
        caption_top = -3.22 + 1.12 / 2
        available = question.get_bottom()[1] - gap - (caption_top + .24)
        if available <= 0:
            raise ValueError("Question leaves no room for quiz options")
        if options.height > available:
            options.scale_to_fit_height(available)
        options.next_to(question, DOWN, buff=gap).set_x(0)
        # Guard both the question and later dialogue caption safe areas.
        if (options.get_top()[1] > question.get_bottom()[1] - .40
                or options.get_bottom()[1] < caption_top + .22):
            raise ValueError("Quick challenge layout overlaps question or caption")
        self.play(FadeIn(question),LaggedStart(*[FadeIn(o,shift=UP*.12) for o in options],
                                               lag_ratio=.15),run_time=.9)
        count = txt("3",46,PURPLE).next_to(options, RIGHT, buff=.85)
        self.play(GrowFromCenter(count),run_time=.3)
        for n in (2,1):
            self.wait(.72)
            nxt=txt(str(n),46,PURPLE).move_to(count)
            self.play(ReplacementTransform(count,nxt),run_time=.18)
            count=nxt
        self.wait(.72)
        self.play(FadeOut(count),options[0][0].animate.set_fill(PINK,opacity=1),
                  options[1].animate.set_opacity(.42),options[2].animate.set_opacity(.42),
                  run_time=.5)
        self.say("recap-05","robot","It's AI! Learning from data is not required.")
        self.stage()
        self.title("NEXT  /  What can AI actually do?")
        pair=VGroup(tag("PREDICT",40,width=5.8),tag("GENERATE",40,fill=PINK,width=5.8))
        pair.arrange(RIGHT,buff=.8).move_to(UP*.7)
        student=self.character("student",2.3,-4.5,-1.15)
        robot=self.character("robot",2.3,4.5,-1.15)
        self.say("recap-06","student","Now what about generative AI? Is it another layer?",
                 FadeIn(student),FadeIn(robot),LaggedStart(*[GrowFromCenter(p) for p in pair],
                                                            lag_ratio=.25))
        self.say("recap-07","robot","That's about what AI does, not simply how it learns. Let's explore that next.", reaction="nod")
