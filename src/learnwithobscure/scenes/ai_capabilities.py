"""Chapter 2: AI capabilities. Silent preview; no TTS calls.

Run: uv run manim --disable_caching -pql src/learnwithobscure/scenes/ai_capabilities.py AICapabilities
"""
from manim import *
from learnwithobscure.scenes.ai_universe import (
    AIUniverseFoundations, txt, box, tag, pos, arrow,
    BG, DARK, PURPLE, LAVENDER, PINK, WHITE,
)


class AICapabilities(AIUniverseFoundations):
    """Reuse the approved foundations layout and character reaction system."""

    def construct(self):
        import os
        from learnwithobscure.scenes.ai_universe_audio import preflight
        if os.getenv("LWO_DISABLE_VOICEOVER") != "1":
            preflight()
        self.camera.background_color = BG
        self.caption = None
        self.dialogue_ids = set()
        self.characters = {}
        self.predict()
        self.generate()
        self.vision()
        self.language()
        self.speech()
        self.spatial()
        self.challenge()
        self.wait(.5)

    def setup_topic(self, title, subtitle):
        self.stage()
        self.title(title, subtitle)
        student = self.character("student", 2.12, -6.03, -1.32, max_width=1.5)
        robot = self.character("robot", 2.12, 6.03, -1.32, max_width=1.5)
        self.play(FadeIn(student, shift=RIGHT*.4),
                  FadeIn(robot, shift=LEFT*.4), run_time=.45)

    def predict(self):
        self.setup_topic("04  /  Predictive AI", "Estimate an outcome from available information")
        axes = Axes(x_range=[0,6,1], y_range=[0,5,1],
                    x_length=5.2, y_length=2.8, tips=False,
                    axis_config={"color": DARK, "include_ticks": False}).move_to(pos(-2,.35))
        points = [axes.c2p(x,y) for x,y in [(0,.8),(1,1.5),(2,1.1),(3,2.7),(4,3.1)]]
        history = VMobject(color=PURPLE,stroke_width=5).set_points_as_corners(points)
        dots = VGroup(*[Dot(p, color=PURPLE, radius=.075) for p in points])
        forecast = DashedLine(points[-1], axes.c2p(5,3.8),color=PINK,stroke_width=5)
        future = Dot(axes.c2p(5,3.8),color=PINK,radius=.13)
        past = txt("Past data",21).next_to(axes,DOWN,buff=.16)
        result = VGroup(txt("Tomorrow",28,PURPLE),txt("Rain likely",37,DARK),
                        txt("Not a guarantee",19)).arrange(DOWN,buff=.23).move_to(pos(3.3,.65))
        self.say("cap-p01","student","Can AI tell me if it will rain tomorrow?",
                 Create(axes),FadeIn(past),pose="questioning",reaction="question")
        self.say("cap-p02","robot","Predictive AI uses available data to estimate outcomes, like the chance of rain.",
                 Create(history),FadeIn(dots))
        self.say("cap-p03","robot","The prediction is an estimate, not a promise.",
                 Create(forecast),GrowFromCenter(future),FadeIn(result))
        self.say("cap-p04","student","So I should carry an umbrella, not blame the algorithm?",pose="questioning")
        self.say("cap-p05","robot","Exactly. And prediction is only one thing AI can do.",reaction="nod")

    def generate(self):
        self.setup_topic("05  /  Generative AI", "Create new content from learned patterns")
        prompt = tag("Draw a cat astronaut",25,width=4.2).move_to(pos(-3.2,1.05))
        model = VGroup(Circle(radius=.75,color=PURPLE,fill_color=LAVENDER,fill_opacity=1),
                       txt("AI",35,DARK)).move_to(pos(0,1.05))
        a = arrow(pos(-1.3,1.05),pos(-.8,1.05))
        b = arrow(pos(.8,1.05),pos(1.68,1.05))
        from pathlib import Path
        import os
        assets = Path(__file__).resolve().parents[3] / "assets" / "ai_universe"
        image_path = assets / "astronaut_kitten.png"
        meow_path = assets / "kitten_meow.wav"
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing astronaut kitten: {image_path}")
        art = ImageMobject(str(image_path)).scale_to_fit_width(3.5)
        art.move_to(pos(3.5,1.05))
        outputs = VGroup(*[tag(t,22) for t in ("TEXT","IMAGES","AUDIO","CODE")])
        outputs.arrange(RIGHT,buff=.23).move_to(DOWN*1.15)
        self.say("cap-g01","student","What if I want AI to draw a cat in a spacesuit?",
                 GrowFromCenter(prompt),pose="questioning")
        self.say("cap-g02","robot","Generative AI creates content from patterns learned during training.",
                 GrowArrow(a),GrowFromCenter(model))
        self.say("cap-g03","robot","Depending on the model, it can create images, text, audio or code.",
                 GrowArrow(b),
                 LaggedStart(*[FadeIn(o,shift=UP*.15) for o in outputs],lag_ratio=.12))
        # Reveal only after Zeno's narration finishes, so the meow is isolated.
        if os.getenv("LWO_DISABLE_VOICEOVER") != "1":
            if not meow_path.is_file():
                raise FileNotFoundError(f"Missing kitten meow: {meow_path}")
            self.add_sound(str(meow_path), gain=-4)
        self.play(FadeIn(art, scale=0.85), run_time=.4)
        self.wait(1.7)
        self.say("cap-g04","student","Finally, a cat that takes its career seriously.",pose="neutral",reaction="realize")
        self.say("cap-g05","robot","And generated content can still contain mistakes.",reaction="nod")

    def vision(self):
        self.setup_topic("06  /  Computer Vision", "Interpret images and video")
        from pathlib import Path
        assets = Path(__file__).resolve().parents[3] / "assets" / "ai_universe"
        car_path = assets / "ai_car_side.png"
        pedestrian_path = assets / "obscure_pedestrian_side.png"

        ground = Line(pos(-5.2, -.85), pos(5.2, -.85),
                      color=DARK, stroke_width=3)
        if car_path.is_file() and pedestrian_path.is_file():
            # Illustrated, strictly side-on sprites, independently animatable.
            car = ImageMobject(str(car_path)).scale_to_fit_width(3.35)
            person = ImageMobject(str(pedestrian_path)).scale_to_fit_height(2.2)
            car.move_to(pos(-3.15, 0)).align_to(ground, DOWN)
            person.move_to(pos(2.65, 0)).align_to(ground, DOWN)
        else:
            # Keep the scene renderable until the approved artwork is installed.
            car = VGroup(box(1.6, .62, fill=LAVENDER),
                         *[Circle(radius=.16, color=DARK, fill_opacity=1).move_to(pos(x, -.35))
                           for x in (-.49, .49)])
            car.move_to(pos(-2.8, -.2))
            person = VGroup(
                Circle(radius=.16, color=PURPLE, fill_opacity=1).move_to(UP*.58),
                Line(UP*.4, DOWN*.1, color=PURPLE, stroke_width=5),
                Line(UP*.2, pos(-.32, -.05), color=PURPLE, stroke_width=5),
                Line(UP*.2, pos(.32, -.05), color=PURPLE, stroke_width=5),
                Line(DOWN*.1, pos(-.22, -.52), color=PURPLE, stroke_width=5),
                Line(DOWN*.1, pos(.22, -.52), color=PURPLE, stroke_width=5)
            ).move_to(pos(2.6, .1))

        detection = SurroundingRectangle(person, color=PINK, buff=.12,
                                         stroke_width=4)
        label = tag("Pedestrian", 21, fill=WHITE).next_to(
            detection, UP, buff=.12)
        self.say("cap-v01", "student", "Can AI identify what is in a camera image?",
                 Create(ground), FadeIn(car), FadeIn(person), pose="questioning")
        self.say("cap-v02", "robot", "Computer vision can classify images, detect objects or track movement.",
                 Create(detection), FadeIn(label))
        self.say("cap-v03", "robot", "For example, a driving system may detect a pedestrian ahead.",
                 car.animate.shift(RIGHT*1.25))
        self.say("cap-v04", "student", "Seeing the pedestrian is not the same as knowing how to drive?",
                 pose="questioning", reaction="think")
        self.say("cap-v05", "robot", "Right. Detection is one capability in a larger system.",
                 reaction="nod")

    def language(self):
        self.setup_topic("07  /  Natural Language Processing", "Work with human language")
        source = tag("Hello, how are you?",29,width=4.6).move_to(pos(-3.25,.95))
        target = tag("Hola, ¿cómo estás?",29,width=4.6,fill="#F5EAFB").move_to(pos(3.25,.95))
        bridge = arrow(pos(-1.1,.95),pos(1.1,.95))
        translation = txt("TRANSLATION",23,PURPLE).next_to(bridge,UP,buff=.24)
        tasks = VGroup(*[tag(x,23) for x in ("Classify","Translate","Summarize")])
        tasks.arrange(RIGHT,buff=.3).move_to(DOWN*.9)
        self.say("cap-n01","robot","Natural language processing, or NLP, is the field of working with human language.",
                 FadeIn(source))
        self.say("cap-n02","student","Like translating my messages into another language?",pose="questioning")
        self.say("cap-n03","robot","Exactly. It also includes sentiment classification and summarization.",
                 GrowArrow(bridge),FadeIn(translation),FadeIn(target),
                 LaggedStart(*[GrowFromCenter(t) for t in tasks],lag_ratio=.13))
        self.say("cap-n04","student","So NLP existed before modern chatbots?",pose="questioning",reaction="question")
        self.say("cap-n05","robot","Yes. Modern language models are one way to solve NLP tasks.",reaction="nod")

    def speech(self):
        self.setup_topic("08  /  Speech AI", "Recognize speech or synthesize a voice")
        wave = VGroup(*[Line(DOWN*h/2,UP*h/2,color=PURPLE,stroke_width=5)
                         for h in (.2,.45,.85,.55,1.25,.8,.4,.95,.55,.25)])
        wave.arrange(RIGHT,buff=.085).move_to(pos(-3.6,.8))
        text_chip = tag("Hello, Zeno!",27,width=3.15).move_to(pos(0,.8))
        wave_out = wave.copy().set_color(PINK).move_to(pos(3.6,.8))
        a = arrow(pos(-2.3,.8),pos(-1.35,.8))
        b = arrow(pos(1.35,.8),pos(2.3,.8))
        a_label = txt("Speech to text",20,PURPLE,width=3).move_to(pos(-1.9,-.35))
        b_label = txt("Text to speech",20,PURPLE,width=3).move_to(pos(1.9,-.35))
        self.say("cap-s01","student","Wait, isn't your own voice an example of AI?",pose="questioning",reaction="question")
        self.say("cap-s02","robot","Yes! Speech recognition turns spoken audio into text.",
                 LaggedStart(*[GrowFromCenter(w) for w in wave],lag_ratio=.07),
                 GrowArrow(a),FadeIn(a_label),GrowFromCenter(text_chip))
        self.say("cap-s03","robot","Text to speech does the reverse: it generates spoken audio from text.",
                 GrowArrow(b),FadeIn(b_label),
                 LaggedStart(*[GrowFromCenter(w) for w in wave_out],lag_ratio=.07))
        self.say("cap-s04","student","So the voice explaining AI is itself an AI example. That's meta.",reaction="realize")
        self.say("cap-s05","robot","And speech synthesis is also an example of generative AI.",reaction="nod")

    def spatial(self):
        self.setup_topic("09  /  Spatial AI", "Reason about space, geometry and relationships")
        def poly(coords, color):
            return Polygon(*[pos(x,y) for x,y in coords],color=PURPLE,
                           fill_color=color,fill_opacity=1,stroke_width=2)
        floor = poly([(-1.8,.2),(0,1.1),(1.8,.2),(0,-.7)],WHITE)
        left = poly([(-1.8,.2),(0,1.1),(0,2.25),(-1.8,1.35)],LAVENDER)
        right = poly([(0,1.1),(1.8,.2),(1.8,1.35),(0,2.25)],"#F5EAFB")
        room = VGroup(left,right,floor).move_to(pos(2.7,.65))
        block = VGroup(
            poly([(-.45,0),(0,.22),(.45,0),(0,-.22)],PINK),
            poly([(-.45,0),(0,-.22),(0,-.75),(-.45,-.53)],LAVENDER),
            poly([(0,-.22),(.45,0),(.45,-.53),(0,-.75)],PURPLE)
        ).move_to(room.get_center()+DOWN*.32)
        photo = VGroup(box(2.6,2.15,fill=WHITE),
                       Rectangle(width=1.8,height=1.3,color=LAVENDER),
                       txt("2D view",23).shift(DOWN*.83)).move_to(pos(-3.15,.65))
        path = VMobject(color=PINK,stroke_width=5).set_points_as_corners([
            room.get_center()+pos(-.95,-.45),
            room.get_center()+pos(-.55,-.75),
            room.get_center()+pos(.75,-.09)])
        self.say("cap-sp01","student","What about AI that understands where objects are in a room?",
                 FadeIn(photo),pose="questioning",reaction="question")
        self.say("cap-sp02","robot","Spatial AI works with geometry, locations and relationships between objects.",
                 GrowArrow(arrow(pos(-1.6,.65),pos(.7,.65))),FadeIn(room),FadeIn(block))
        self.say("cap-sp03","robot","It can help reconstruct a 3D scene or support robot navigation.",
                 Create(path))
        self.say("cap-sp04","student","So it is about understanding space, not just generating pictures?",pose="questioning")
        self.say("cap-sp05","robot","Exactly. Some systems generate worlds, others estimate geometry or plan movement. These categories overlap.",reaction="nod")

    def challenge(self):
        self.stage()
        self.title("QUICK CHALLENGE", "Which capabilities can overlap?")
        question = txt("An AI creates a spoken answer.\nWhich capabilities are involved?",34,width=11.8,height=1.15).move_to(UP*1.65)
        options = VGroup(*[tag(t,26,width=7.2) for t in
                           ("A  /  Speech synthesis only","B  /  Generative AI only",
                            "C  /  Both")]).arrange(DOWN,buff=.24).move_to(DOWN*.38)
        quiz_student = self.character("student",2.12,-5.85,-1.32,max_width=1.5)
        quiz_robot = self.character("robot",2.12,5.85,-1.32,max_width=1.5)
        self.say("cap-q-ask","robot",
                 "Ready for another challenge, Obscure? Code Crew, think along with him! An AI creates a spoken answer. Which capabilities are involved? A, speech synthesis only, B, generative AI only, or C, both?",
                 FadeIn(quiz_student),FadeIn(quiz_robot),FadeIn(question),
                 LaggedStart(*[FadeIn(o) for o in options],lag_ratio=.13))
        self.quiz_countdown()
        self.say("cap-q-answer","student","I'll go with C, Sensei. Both!",pose="thoughtful",reaction="realize")
        self.say("cap-q01","robot","Exactly right! Generative AI describes what is created, and speech synthesis describes the specific task.",
                 options[2][0].animate.set_fill(PINK,opacity=1),
                 options[0].animate.set_opacity(.45),options[1].animate.set_opacity(.45),reaction="nod")
        self.stage()
        self.title("NEXT  /  Models behind the capabilities")
        student = self.character("student",2.3,-4.5,-1.15)
        robot = self.character("robot",2.3,4.5,-1.15)
        model = VGroup(tag("TRANSFORMERS",30,width=5.4),tag("LLMs",33,fill=PINK,width=5.4))
        model.arrange(DOWN,buff=.28).move_to(UP*.55)
        self.say("cap-q02","student","Okay, but where do transformers and LLMs fit into all this?",
                 FadeIn(student),FadeIn(robot),FadeIn(model),pose="questioning")
        self.say("cap-q03","robot","Those are about the models and architectures behind the capabilities. That's our next stop!",reaction="nod")
