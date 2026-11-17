"""AI Universe, opening + foundations. Silent visual prototype; no TTS calls.

Run: uv run manim --disable_caching -pql src/learnwithobscure/scenes/ai_universe.py AIUniverseFoundations
"""
from manim import *
from manimpango import list_fonts

from learnwithobscure.scenes.bubble_sort import (
    BG, DARK, PURPLE, LAVENDER, PINK, WHITE,
    STUDENT_IMAGE, ROBOT_IMAGE, create_character,
)

_fonts = {name.casefold(): name for name in list_fonts()}
FONT = next((_fonts[f.casefold()] for f in
             ("Poppins", "Montserrat", "Inter", "Segoe UI", "Arial",
              "DejaVu Sans", "Liberation Sans", "Noto Sans")
             if f.casefold() in _fonts), "sans-serif")


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
        self.camera.background_color = BG
        self.caption = None
        self.dialogue_ids = set()
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

    def character(self, who, height, x, y):
        asset = STUDENT_IMAGE if who == "student" else ROBOT_IMAGE
        return create_character(asset, height).move_to(pos(x,y))

    def say(self, key, who, line, *animations, seconds=None):
        """Silent dialogue beat. Full lines stay in code; no audio dependency."""
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
        # Motion occurs during the line, then the remainder is held for reading.
        motion = min(1.10, duration)
        if animations:
            self.play(*animations, run_time=motion)
            self.wait(max(1/config.frame_rate, duration-motion))
        else:
            self.wait(duration)

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
                 LaggedStart(*[GrowFromCenter(c) for c in chips], lag_ratio=.12))
        self.say("intro-02","student","ZENOOOO!",
                 student.animate.shift(UP*.23).scale(1.065), seconds=2.2)
        robot = self.character("robot",3.45,4.25,-.12)
        self.say("intro-03","robot",
                 "Relax! You're mixing up techniques, models, capabilities and tools.",
                 FadeOut(chips, shift=UP*1.1), FadeIn(robot, shift=LEFT*1.7),
                 student.animate.move_to(pos(-4.0,-.1)))
        clusters = VGroup(*[tag(v, 24, fill=WHITE) for v in
                            ("TECHNIQUES","MODELS","CAPABILITIES","TOOLS")])
        clusters.arrange(DOWN,buff=.24).move_to(UP*.42)
        self.say("intro-04","student","There are categories now?!",
                 LaggedStart(*[GrowFromCenter(c) for c in clusters],lag_ratio=.12))
        self.say("intro-05","robot",
                 "Once you understand how these concepts fit together, everything gets simpler.",
                 Indicate(clusters,color=PURPLE,scale_factor=1.06))
        self.say("intro-06","student","Fine. Start from the beginning.",seconds=2.6)
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
        robot = self.character("robot",2.65,-5.55,-.9)
        student = self.character("student",2.35,5.42,-.94)
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
        self.say("ai-02","student","So every AI learns from data?")
        self.say("ai-03","robot",
                 "Not necessarily. A chess program can search possible moves using predefined rules, without learning from data.",
                 FadeIn(idea),LaggedStart(*[FadeIn(d,shift=LEFT*.25) for d in decisions],
                                         lag_ratio=.15))
        # The knight marker moves two up and one right; this is a legal capture.
        route = VMobject(color=PINK,stroke_width=6).set_points_as_corners([
            origin2,origin2+UP*sz*2,target])
        self.play(Create(route),run_time=.52)
        self.play(MoveAlongPath(start,route),FadeOut(enemy),run_time=.65)
        self.say("ai-04","student","So AI is the big umbrella. Learning is optional!")
        self.say("ai-05","robot","Exactly. Now imagine rules that are hard to write by hand.",
                 Indicate(idea,color=PURPLE))

    def ml_example(self):
        self.stage()
        self.title("02  /  Machine Learning", "Learn from examples, rather than writing every rule")
        student = self.character("student",2.25,-5.55,-.9)
        robot = self.character("robot",2.25,5.55,-.9)
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
                                                 lag_ratio=.12),FadeIn(labels))
        self.say("ml-02","robot",
                 "Machine learning lets a system learn patterns from data. Here we have emails labeled spam or not spam.",
                 FadeIn(model,scale=.85),GrowArrow(train))
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
                 FadeIn(unseen,shift=RIGHT*.4),FadeIn(input_label),GrowArrow(predict_in))
        self.say("ml-05","robot","The trained model predicts a label. It can still make mistakes.",
                 Indicate(model,color=PURPLE),GrowArrow(predict_out),GrowFromCenter(outcome))
        self.say("ml-06","student","Can we teach it to spot weekend messages from my manager?")
        self.say("ml-07","robot","Technically, yes. Professionally, proceed with caution.",
                 robot.animate.shift(UP*.14))
        self.say("ml-08","student","Got it. Learning from data is what makes it machine learning.")

    def deep_example(self):
        self.stage()
        self.title("03  /  Neural Networks & Deep Learning",
                   "Deep learning uses neural networks with multiple processing layers")
        robot = self.character("robot",2.12,5.75,-1.20)
        student = self.character("student",2.02,-5.75,-1.20)
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
                 FadeIn(pixels),FadeIn(input_label),FadeIn(layers[0]),FadeIn(labels[0]))
        self.say("dl-02","robot",
                 "A neural network has connected computational units that transform inputs using learned weights.",
                 Create(links[0]),FadeIn(layers[1]),FadeIn(labels[1]))
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
        self.say("dl-05","student","So multiple layers help it learn richer representations?")
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
        student=self.character("student",2.18,5.08,-.98)
        robot=self.character("robot",2.10,5.20,1.38)
        self.say("recap-01","student","AI is the broadest category.",
                 GrowFromCenter(outer),FadeIn(a),FadeIn(student))
        self.say("recap-02","student","Machine learning is inside AI.",
                 GrowFromCenter(middle),FadeIn(m))
        self.say("recap-03","student","And deep learning is inside machine learning!",
                 GrowFromCenter(inner),FadeIn(d),FadeIn(robot,shift=LEFT*.4))
        self.say("recap-04","robot","Exactly. Three concepts unlocked.",
                 Indicate(d,color=WHITE,scale_factor=1.04))
        self.stage()
        self.title("QUICK CHALLENGE")
        question = txt("A chess program uses rules and search.\nIt does not learn from data.",38,
                       DARK,width=12.4,height=1.5).move_to(UP*1.66)
        options = VGroup(*[tag(v,30,fill=WHITE,width=5.4) for v in
                           ("A  /  AI only","B  /  Machine learning","C  /  Deep learning")])
        options.arrange(DOWN,buff=.20).move_to(DOWN*.03)
        self.play(FadeIn(question),LaggedStart(*[FadeIn(o,shift=UP*.15) for o in options],
                                               lag_ratio=.15),run_time=.9)
        count = txt("3",46,PURPLE).move_to(pos(5.35,-.35))
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
        self.say("recap-07","robot","That's about what AI does, not simply how it learns. Let's explore that next.")
