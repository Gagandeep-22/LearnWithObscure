"""Full silent AI Universe review. No API calls.
uv run manim --disable_caching -pql src/learnwithobscure/scenes/ai_universe_full.py AIUniverseFull
"""
from manim import *
from learnwithobscure.scenes.ai_capabilities import AICapabilities
from learnwithobscure.scenes.ai_universe import (
    txt, box, tag, pos, arrow, BG, DARK, PURPLE, LAVENDER, PINK, WHITE,
)


class AIUniverseFull(AICapabilities):
    def construct(self):
        # The original foundations and capabilities are preserved verbatim.
        self.foundations()
        for method in (self.predict, self.generate, self.vision, self.language,
                       self.speech, self.spatial, self.challenge,
                       self.foundation_models, self.transformers, self.language_models,
                       self.model_lifecycle, self.multimodal, self.reasoning,
                       self.prompts, self.embeddings, self.rag, self.fine_tuning,
                       self.tools, self.mcp, self.workflows, self.agents,
                       self.multi_agent, self.agi, self.final_recap):
            method()
        self.wait(1)

    def foundations(self):
        # Invoke the original construct on this same scene, retaining dialogue IDs.
        from learnwithobscure.scenes.ai_universe import AIUniverseFoundations
        AIUniverseFoundations.construct(self)

    def chain(self, labels, y=.7):
        nodes = VGroup(*[tag(s, 25, width=2.85) for s in labels])
        nodes.arrange(RIGHT, buff=.65).move_to(UP*y)
        if nodes.width > 10.4:
            nodes.scale_to_fit_width(10.4)
        links = VGroup(*[arrow(a.get_right(), b.get_left())
                         for a,b in zip(nodes, list(nodes)[1:])])
        return nodes, links

    def reveal_chain(self, nodes, links):
        return LaggedStart(*[FadeIn(o, shift=UP*.1) if i%2==0 else GrowArrow(o)
                             for i,o in enumerate([v for pair in zip(nodes,links)
                                                   for v in pair]+[nodes[-1]])],
                           lag_ratio=.16)

    def foundation_models(self):
        self.setup("10  /  Foundation models", "Broad pretraining, many downstream uses")
        data = VGroup(*[tag(x,22) for x in ("Books","Images","Code")]).arrange(DOWN,buff=.18).move_to(pos(-3.8,.8))
        core = VGroup(Circle(radius=.83,color=PURPLE,fill_color=LAVENDER,fill_opacity=1),
                      txt("MODEL",23,DARK)).move_to(UP*.8)
        tasks = VGroup(*[tag(x,22) for x in ("Summarize","Translate","Assist")]).arrange(DOWN,buff=.18).move_to(pos(3.8,.8))
        inbound = VGroup(*[arrow(d.get_right(),core.get_left()) for d in data])
        outbound = VGroup(*[arrow(core.get_right(),d.get_left()) for d in tasks])
        self.say("model-01","student","Do we need to train a separate AI for every little job?",FadeIn(data),pose="questioning")
        self.say("model-02","robot","A foundation model is broadly pretrained and can be adapted to many tasks. The training data depends on the model.",FadeIn(core),*[GrowArrow(a) for a in inbound])
        self.say("model-03","robot","One language model might support translation, summarization and coding assistance.",FadeIn(tasks),*[GrowArrow(a) for a in outbound])
        self.say("model-04","student","One model, many jobs. My manager would approve.",reaction="realize")

    def transformers(self):
        self.setup("11  /  Transformers", "An architecture using attention")
        words = VGroup(*[tag(x,25,width=2) for x in ("The","animal","was","tired")]).arrange(RIGHT,buff=.35).move_to(UP*1.25)
        links = VGroup(*[CurvedArrow(words[-1].get_bottom(),words[i].get_bottom(),
                                    angle=-.55,color=PINK if i==1 else LAVENDER,
                                    stroke_width=5 if i==1 else 2) for i in range(3)])
        caption = txt("Illustrative attention connections",20).move_to(DOWN*.9)
        self.say("tr-01","student","Is a transformer a robot in disguise?",FadeIn(words),pose="questioning")
        self.say("tr-02","robot","Not this time. It is a neural network architecture that uses attention to combine information from different tokens.",Create(links),FadeIn(caption))
        self.say("tr-03","robot","Here, the connections illustrate how context can matter. Real models learn many attention patterns.",Indicate(words[1],color=PURPLE))
        self.say("tr-04","student","So architecture means how the model is built, not what job it does?",reaction="realize")
        self.say("tr-05","robot","Exactly. Many modern language models use transformers, but not all AI does.",reaction="nod")

    def language_models(self):
        self.setup("12  /  LLMs and SLMs", "Language models learn patterns over tokens")
        prefix = txt("The sky is",46,PURPLE).move_to(pos(-2.9,1.1))
        choices = VGroup(*[tag(x,27) for x in ("blue","clear","dark")]).arrange(DOWN,buff=.19).move_to(pos(3.1,1.0))
        connector = arrow(prefix.get_right(),choices.get_left())
        self.say("lm-01","student","What exactly is a large language model?",FadeIn(prefix),pose="questioning")
        self.say("lm-02","robot","An LLM is trained on large amounts of data to model language. Many generate text by predicting one token after another.",GrowArrow(connector),FadeIn(choices))
        self.say("lm-03","robot","A token can be a word, part of a word, or another unit. These are illustrative possible next tokens.",choices[0][0].animate.set_fill(PINK,opacity=1))
        self.play(FadeOut(prefix),FadeOut(choices),FadeOut(connector),run_time=.4)
        large = VGroup(Circle(radius=1.35,color=PURPLE,fill_color=LAVENDER,fill_opacity=1),txt("LLM",36)).move_to(pos(-2,.55))
        small = VGroup(Circle(radius=.76,color=PURPLE,fill_color=WHITE,fill_opacity=1),txt("SLM",28)).move_to(pos(2,.55))
        self.say("lm-04","student","What about small language models?",GrowFromCenter(large),GrowFromCenter(small),pose="questioning")
        self.say("lm-05","robot","SLMs generally use fewer parameters and may cost less to run. They can be useful for focused tasks. There is no universal size cutoff.",Indicate(small,color=PURPLE))
        self.say("lm-06","student","Bigger is not automatically better. Finally, some good news for my laptop.",reaction="realize")

    def model_lifecycle(self):
        self.setup("13  /  Training, inference & context", "Learning and using a model are different")
        nodes, links = self.chain(("DATA","TRAIN","MODEL","INFER"))
        self.say("life-01","robot","Training adjusts model weights using data. Inference uses a trained model to produce an output.",self.reveal_chain(nodes,links))
        self.say("life-02","student","So every time I ask a question, the model does not automatically retrain?",pose="questioning")
        self.say("life-03","robot","Correct. The context window is the limited amount of tokenized information the model can consider at once.",FadeOut(nodes),FadeOut(links))
        window = box(8.8,1.65,fill=WHITE).move_to(UP*.65)
        tokens = VGroup(*[tag(x,21,width=1.3) for x in ("You","are","a","help","ful","bot",".")]).arrange(RIGHT,buff=.12).move_to(window)
        if tokens.width>8.2: tokens.scale_to_fit_width(8.2)
        self.say("life-04","robot","A longer context can hold more instructions or documents, but context is not the same as permanent memory.",Create(window),FadeIn(tokens))
        self.say("life-05","student","I'll stop pasting my entire project into one message. Maybe.",reaction="think")

    def multimodal(self):
        self.setup("14  /  Multimodal AI", "Work with multiple modalities")
        icons = VGroup(*[tag(x,25) for x in ("TEXT","IMAGE","AUDIO")]).arrange(DOWN,buff=.24).move_to(pos(-3.7,.75))
        model = VGroup(Circle(radius=.8,color=PURPLE,fill_color=LAVENDER,fill_opacity=1),txt("AI",36)).move_to(UP*.75)
        result = tag("A cat in space!",27,width=3.6,fill=PINK).move_to(pos(3.35,.75))
        edges = [arrow(i.get_right(),model.get_left()) for i in icons]
        self.say("multi-01","student","Can one model take a picture and a question together?",FadeIn(icons),pose="questioning")
        self.say("multi-02","robot","Multimodal models process more than one kind of information, such as text and images. Supported inputs and outputs vary.",FadeIn(model),*[GrowArrow(a) for a in edges])
        self.say("multi-03","robot","For example, a model can answer a question about a picture.",GrowArrow(arrow(model.get_right(),result.get_left())),GrowFromCenter(result))
        self.say("multi-04","student","Our astronaut cat is back. It has a cinematic universe now.",reaction="realize")

    def reasoning(self):
        self.setup("15  /  Reasoning models", "Designed for more deliberate problem solving")
        steps, links = self.chain(("PROBLEM","PLAN","CHECK","ANSWER"))
        self.say("reason-01","student","Why do some models take longer to answer a puzzle?",pose="questioning")
        self.say("reason-02","robot","Reasoning models are designed to spend more computation on difficult multi-step tasks. This schematic is not their hidden reasoning.",self.reveal_chain(steps,links))
        self.say("reason-03","robot","They can be useful for mathematics, coding or planning, but their results still need verification.",Indicate(steps[2],color=PURPLE))
        self.say("reason-04","student","Thinking longer does not guarantee being right. Relatable.",reaction="nod")

    def prompts(self):
        self.setup("16  /  Prompt engineering", "Specify task, context and constraints")
        vague = tag("Write code",32,width=4.8).move_to(pos(-3,.75))
        clear = VGroup(box(5.2,2.1,fill=WHITE),txt("Java method\nHandle null input\nInclude two tests",29,width=4.8,height=1.6)).move_to(pos(2.75,.75))
        self.say("prompt-01","student","I asked for code and got an entire novel.",FadeIn(vague),pose="confused")
        self.say("prompt-02","robot","Prompt engineering is designing instructions and examples to guide a model's output.",GrowArrow(arrow(vague.get_right(),clear.get_left())),FadeIn(clear))
        self.say("prompt-03","robot","Specify the programming language, edge cases and output format. This changes the input, not the model weights.",Indicate(clear,color=PURPLE))
        self.say("prompt-04","student","So the problem was my requirements document. Awkward.",reaction="think")

    def embeddings(self):
        self.setup("17  /  Embeddings & vector databases", "Search by similarity in a learned representation")
        axes = Axes(x_range=[0,5,1],y_range=[0,4,1],x_length=7,y_length=2.8,tips=False,axis_config={"color":DARK,"include_ticks":False}).move_to(UP*.65)
        items = [(1,2.7,"cat"),(1.65,2.3,"kitten"),(3.8,.8,"Java"),(4.3,1.4,"Python")]
        marks = VGroup()
        for x,y,label in items:
            d=Dot(axes.c2p(x,y),color=PURPLE,radius=.09)
            marks.add(VGroup(d,txt(label,20).next_to(d,UP,buff=.09)))
        query=Dot(axes.c2p(1.3,1.95),color=PINK,radius=.12)
        q=txt("pet",20).next_to(query,DOWN,buff=.1)
        self.say("embed-01","robot","Embeddings represent information as numerical vectors. Similar meanings may have nearby representations.",Create(axes),FadeIn(marks))
        self.say("embed-02","student","So I can search for pets even if a document says kitten?",GrowFromCenter(query),FadeIn(q),pose="questioning")
        self.say("embed-03","robot","Yes. A vector database can store and search those vectors. This two-dimensional map is only illustrative.",Create(Line(query.get_center(),marks[1][0].get_center(),color=PINK,stroke_width=5)))
        self.say("embed-04","student","Search by meaning instead of just matching words. Nice.",reaction="realize")

    def rag(self):
        self.setup("18  /  Retrieval-augmented generation", "Retrieve relevant evidence before generating")
        nodes, links = self.chain(("QUESTION","RETRIEVE","CONTEXT","LLM"))
        doc = tag("Company docs",24,width=3.3,fill=PINK).move_to(pos(-1.5,-.8))
        self.say("rag-01","student","How can a chatbot answer questions about our private codebase?",pose="questioning")
        self.say("rag-02","robot","RAG retrieves relevant information from an authorized source and supplies it to the model as context.",self.reveal_chain(nodes,links),FadeIn(doc))
        self.say("rag-03","robot","It can improve grounding without retraining the model. Bad retrieval or unsupported answers remain possible.",Indicate(nodes[2],color=PURPLE))
        self.say("rag-04","student","An open-book exam for AI. Still has to read the right page.",reaction="realize")

    def fine_tuning(self):
        self.setup("19  /  Fine-tuning", "Adapt learned model parameters")
        nodes, links=self.chain(("BASE MODEL","EXAMPLES","ADAPTED"))
        self.say("fine-01","student","Is fine-tuning just another name for RAG?",pose="questioning")
        self.say("fine-02","robot","No. Fine-tuning further trains a model on selected examples, changing weights to adapt behavior or task performance.",self.reveal_chain(nodes,links))
        self.say("fine-03","robot","For instance, examples can teach a support model a consistent response format. RAG instead retrieves information at runtime.",Indicate(nodes[-1],color=PURPLE))
        self.say("fine-04","student","Learning a new skill versus looking something up. Got it.",reaction="realize")

    def tools(self):
        self.setup("20  /  Tool calling", "A model requests an external operation")
        nodes,links=self.chain(("MODEL","CALCULATOR","RESULT"))
        answer=txt("17 × 23 = 391",42,PURPLE).move_to(DOWN*.85)
        self.say("tool-01","student","Can I make a model use an actual calculator?",pose="questioning")
        self.say("tool-02","robot","Tool calling lets a model request a defined operation. The host validates and executes it, then returns the result.",self.reveal_chain(nodes,links))
        self.say("tool-03","robot","Calculators, database queries and APIs are examples. Permissions and validation matter.",GrowFromCenter(answer))
        self.say("tool-04","student","My calculator finally got promoted to AI infrastructure.",reaction="realize")

    def mcp(self):
        self.setup("21  /  Model Context Protocol", "A standard interface between AI applications and servers")
        host=tag("AI HOST",28,width=3.2).move_to(pos(-3.8,.8))
        hub=tag("MCP",34,fill=PINK,width=2.3).move_to(UP*.8)
        servers=VGroup(*[tag(x,23,width=3) for x in ("Files","Database","Tools")]).arrange(DOWN,buff=.17).move_to(pos(3.7,.8))
        self.say("mcp-01","student","What is MCP, then? Another model?",pose="questioning")
        self.say("mcp-02","robot","No. Model Context Protocol is a standard for connecting AI applications with servers that expose tools, resources or prompts.",FadeIn(host),GrowFromCenter(hub),GrowArrow(arrow(host.get_right(),hub.get_left())))
        self.say("mcp-03","robot","It standardizes interactions; it does not automatically grant access or make every tool safe.",FadeIn(servers),*[GrowArrow(arrow(hub.get_right(),s.get_left())) for s in servers])
        self.say("mcp-04","student","A common connector, rather than a new brain.",reaction="realize")

    def workflows(self):
        self.setup("22  /  AI workflows", "A predefined sequence of steps")
        nodes,links=self.chain(("INPUT","CLASSIFY","DRAFT","REVIEW"))
        self.say("flow-01","robot","A workflow can connect AI and ordinary software in predefined steps. For example, classify a ticket, draft a reply and request review.",self.reveal_chain(nodes,links))
        self.say("flow-02","student","Does using AI automatically make that an agent?",pose="questioning")
        self.say("flow-03","robot","Not necessarily. An agent typically has more discretion over which actions to take toward a goal.",Indicate(nodes[2],color=PURPLE))

    def agents(self):
        self.setup("23  /  AI agents & agentic AI", "Goal-directed action with feedback")
        nodes,links=self.chain(("OBSERVE","DECIDE","ACT","CHECK"),y=.95)
        loop=CurvedArrow(nodes[-1].get_bottom(),nodes[0].get_bottom(),angle=-.65,color=PINK,stroke_width=5)
        gate=tag("Approval for risky actions",22,width=5.1).move_to(DOWN*1.35)
        self.say("agent-01","student","Can AI actually fix a bug instead of just suggesting code?",pose="questioning")
        self.say("agent-02","robot","An AI agent can use authorized tools, choose actions, observe results and adjust its approach toward a goal.",self.reveal_chain(nodes,links))
        self.say("agent-03","robot","For example, inspect files, propose a patch, run tests and retry if needed. Agentic AI describes this goal-directed behavior.",Create(loop))
        self.say("agent-04","robot","Autonomy varies. Set limits, stop conditions and approvals for important actions.",FadeIn(gate))
        self.say("agent-05","student","So it can fix my tests, but should not deploy on a Friday without asking.",reaction="realize")

    def multi_agent(self):
        self.setup("24  /  Multi-agent systems", "Coordinate several agents")
        goal=tag("GOAL",28,fill=PINK).move_to(UP*1.9)
        roles=VGroup(*[tag(x,25,width=2.8) for x in ("Researcher","Coder","Tester")]).arrange(RIGHT,buff=.5).move_to(UP*.45)
        result=tag("Reviewed result",24,width=3.5).move_to(DOWN*1.05)
        self.say("team-01","student","Can agents work together like a development team?",FadeIn(goal),pose="questioning")
        self.say("team-02","robot","Multi-agent systems coordinate agents with different roles or perspectives. An orchestrator may delegate tasks and collect results.",FadeIn(roles),*[GrowArrow(arrow(goal.get_bottom(),r.get_top())) for r in roles])
        self.say("team-03","robot","They can help on complex tasks, but add latency, cost and coordination risks. More agents do not guarantee better answers.",FadeIn(result),*[GrowArrow(arrow(r.get_bottom(),result.get_top())) for r in roles])
        self.say("team-04","student","Even AI teams have communication problems. That explains a lot.",reaction="think")

    def agi(self):
        self.setup("25  /  Artificial general intelligence", "A debated research goal, not a specific tool")
        orbit=VGroup(*[Circle(radius=r,color=LAVENDER,stroke_width=2) for r in (1,1.6,2.1)]).move_to(UP*.45)
        center=txt("AGI?",60,PURPLE).move_to(orbit)
        self.say("agi-01","student","And AGI? Is that just a really big chatbot?",pose="questioning")
        self.say("agi-02","robot","Artificial general intelligence usually refers to broadly capable intelligence across many tasks. There is no universally agreed test or definition.",Create(orbit),GrowFromCenter(center))
        self.say("agi-03","robot","It is not simply another model architecture, and an agent using tools does not automatically qualify.",Indicate(center,color=PURPLE))
        self.say("agi-04","student","So we should be careful with the hype.",reaction="nod")

    def final_recap(self):
        self.stage()
        self.title("THE AI UNIVERSE  /  Your mental map")
        rows=VGroup(*[VGroup(txt(a,24,PURPLE,width=2.5),
                              txt(b,23,DARK,width=8.4,bold=False)).arrange(RIGHT,buff=.35)
                      for a,b in (
                         ("METHODS","AI, ML, neural networks, deep learning"),
                         ("CAPABILITIES","Predict, generate, see, hear, understand space"),
                         ("MODELS","Foundation models, transformers, LLMs, SLMs"),
                         ("ENHANCEMENTS","Prompts, RAG, fine-tuning, tool calling, MCP"),
                         ("SYSTEMS","Workflows, agents, multi-agent systems"))])
        rows.arrange(DOWN,aligned_edge=LEFT,buff=.28).move_to(UP*.45)
        self.say("end-01","robot","Remember: methods, capabilities, model architectures, enhancements and systems answer different questions. They can overlap.",LaggedStart(*[FadeIn(r,shift=RIGHT*.2) for r in rows],lag_ratio=.17))
        self.say("end-02","student","AI is the umbrella, not a collection of unrelated buzzwords!")
        self.stage()
        self.title("ONE LAST CHALLENGE")
        question=txt("A coding assistant retrieves project docs,\nruns tests and revises its plan. What fits?",34,width=11.6,height=1.2).move_to(UP*1.65)
        options=VGroup(*[tag(s,27,width=7.3) for s in ("A  /  RAG only","B  /  Agent only","C  /  RAG + tool-using agent")]).arrange(DOWN,buff=.2).move_to(DOWN*.25)
        self.play(FadeIn(question),FadeIn(options),run_time=.6)
        self.wait(3)
        self.say("end-03","robot","C! Retrieval can ground the answer, and a tool-using agent can act and adapt. One system can combine several concepts.",options[2][0].animate.set_fill(PINK,opacity=1))
        self.stage()
        self.title("NEXT  /  Build an AI agent")
        student=self.character("student",3,-3.8,-.85,max_width=2.8)
        robot=self.character("robot",3,3.8,-.85,max_width=2.8)
        self.say("end-04","student","Now that I know what an agent is, can we build one?",FadeIn(student),FadeIn(robot),pose="questioning")
        self.say("end-05","robot","That's our next adventure. If you learned something new, subscribe and join us.",reaction="nod")
        self.say("end-06","student","See you in the next video!")
        self.say("end-07","robot","Stay curious, Code Crew!",reaction="nod")
