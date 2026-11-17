"""Vertical Manim template. Set ZENO_AUDIO=1 for cached narration."""
import json, os, wave
from pathlib import Path
from manim import *

ROOT = Path(__file__).resolve().parent
EP = json.loads(Path(os.environ.get('ZENO_EPISODE', str(ROOT/'episode.json'))).read_text(encoding='utf-8'))
config.frame_width = 9
config.frame_height = 16
# Set pixel dimensions explicitly; use ZENO_PREVIEW=1 for fast renders.
preview = os.getenv('ZENO_PREVIEW') == '1'
config.pixel_width, config.pixel_height = (540,960) if preview else (1080,1920)
config.frame_rate = 30
BG, PANEL, LAV, PINK, INK = '#111126','#211B3C','#A78BFA','#F472B6','#F8FAFC'

def words(s, size=42, width=7, color=INK):
    import textwrap
    t = Text('\n'.join(textwrap.wrap(s, width=30)), font_size=size, color=color, line_spacing=1.1)
    if t.width > width: t.scale_to_fit_width(width)
    return t

def tile(s, width=5.8, color=LAV):
    r = RoundedRectangle(width=width,height=.85,corner_radius=.18,stroke_color=color,fill_color=PANEL,fill_opacity=1)
    t=words(s,32,width-.35).move_to(r)
    return VGroup(r,t)

class ZenoDailyBrief(Scene):
    def construct(self):
        self.camera.background_color=BG
        header=words("ZENO'S DAILY TECH BRIEF",34,7,LAV).move_to(UP*6.95)
        date=Text(EP['date'],font_size=22,color=INK).move_to(UP*6.35)
        line=Line(LEFT*3.55,RIGHT*3.55,color=LAV).move_to(UP*6.02)
        zeno=ImageMobject(str(ROOT/'assets'/'zeno.png')).scale_to_fit_height(2.65).move_to(LEFT*2.1+DOWN*3.55)
        label=Text('ZENO SENSEI',font_size=20,color=LAV).next_to(zeno,DOWN,buff=.08)
        footer=words('LEARN WITH OBSCURE',23,6,LAV).move_to(DOWN*6.65)
        self.add(header,date,line,zeno,label,footer)
        for i,seg in enumerate(EP['segments']):
            start=self.time
            wav=ROOT/'audio'/EP['id']/f'{i:02d}.wav'
            duration=seg['seconds']
            if os.getenv('ZENO_AUDIO')=='1':
                if not wav.exists(): raise FileNotFoundError(f'Run daily_brief/prepare_audio.py first: {wav}')
                with wave.open(str(wav),'rb') as f: duration=f.getnframes()/f.getframerate()
                self.add_sound(str(wav))
            title=words(seg['title'],48,7.1).move_to(UP*4.95)
            caption=words(seg['caption'],30,6.9).move_to(DOWN*5.55)
            progress=Line(LEFT*3.4,LEFT*3.4+RIGHT*(6.8*(i+1)/len(EP['segments'])),color=PINK,stroke_width=5).shift(DOWN*7.12)
            graphic, motion=self.graphic(seg['visual'])
            self.play(FadeIn(title,shift=UP*.12),FadeIn(caption),FadeIn(graphic),FadeIn(progress),run_time=.45)
            if motion: self.play(motion,run_time=1.5)
            self.wait(max(.1,duration-(self.time-start)))
            self.play(FadeOut(title),FadeOut(caption),FadeOut(graphic),FadeOut(progress),run_time=.2)

    def graphic(self,kind):
        center=UP*1.25
        if kind in ('hook','cube'):
            # Isometric wireframe cube: no OpenGL or external model required.
            a=Square(side_length=2.15,color=LAV).shift(LEFT*.45+DOWN*.35)
            b=a.copy().shift(RIGHT*.9+UP*.7).set_color(PINK)
            edges=VGroup(*[Line(a.get_vertices()[i],b.get_vertices()[i],color=LAV) for i in range(4)])
            cube=VGroup(a,b,edges)
            for k in (-.55,0,.55):
                cube.add(Line(LEFT*1.075+UP*k,RIGHT*1.075+UP*k,color=LAV,stroke_opacity=.35).shift(LEFT*.45+DOWN*.35))
            cube.move_to(center)
            return cube,Rotate(cube,angle=PI/6,about_point=center)
        if kind=='deal':
            names=VGroup(tile('AMD',2.7,PINK),Text('+',font_size=42,color=LAV),tile('WORLD LABS',3.2)).arrange(RIGHT,buff=.15)
            amount=Text('$8.2B',font_size=100,color=PINK)
            note=words('Original announced valuation',25,6,LAV)
            g=VGroup(names,amount,note).arrange(DOWN,buff=.4).move_to(center)
            return g,Indicate(amount,color=INK)
        if kind=='room':
            floor=Rectangle(width=5.8,height=3.8,color=LAV,fill_color=PANEL,fill_opacity=1).move_to(center)
            grid=VGroup(*[Line(floor.get_left()+RIGHT*x+UP*1.9,floor.get_left()+RIGHT*x+DOWN*1.9,color=LAV,stroke_opacity=.18) for x in (1,2,3,4,5)],*[Line(floor.get_bottom()+UP*y+LEFT*2.9,floor.get_bottom()+UP*y+RIGHT*2.9,color=LAV,stroke_opacity=.18) for y in (1,2,3)])
            block=Square(side_length=.9,color=PINK,fill_opacity=.65).move_to(center)
            robot=Circle(radius=.24,color=WHITE,fill_color=LAV,fill_opacity=1).move_to(center+LEFT*2+DOWN*1.2)
            path=VMobject(color=GREEN).set_points_as_corners([robot.get_center(),center+LEFT*1+DOWN*1.2,center+RIGHT*1+DOWN*1.2,center+RIGHT*2+UP*1])
            goal=Dot(path.get_end(),color=GREEN)
            group=VGroup(floor,grid,block,path,goal,robot)
            return group,MoveAlongPath(robot,path)
        if kind=='scientist':
            g=VGroup(words('FEI-FEI LI',62,7,PINK),tile('Chief Scientist'),tile('Executive Vice President')).arrange(DOWN,buff=.4).move_to(center)
            return g,Indicate(g[1],color=LAV)
        if kind=='stack':
            items=VGroup(tile('AI MODELS'),tile('SOFTWARE'),tile('HARDWARE',color=PINK)).arrange(DOWN,buff=.55).move_to(center)
            arrows=VGroup(*[Arrow(a.get_bottom(),b.get_top(),buff=.05,color=LAV) for a,b in zip(items,items[1:])])
            return VGroup(items,arrows),LaggedStart(*[Indicate(x,color=PINK) for x in items],lag_ratio=.35)
        if kind=='outro':
            g=VGroup(words('LEARN. EXPLORE. SHARE.',50,7,LAV),tile('SUBSCRIBE',color=PINK)).arrange(DOWN,buff=.5).move_to(center)
            return g,Indicate(g[1],color=WHITE)
        return tile(kind).move_to(center),None
