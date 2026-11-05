from manim import *


class HelloLearn(Scene):
    def construct(self):
        text = Text("Hello, Learn with Obscure!")

        self.play(Write(text))
        self.wait(2)