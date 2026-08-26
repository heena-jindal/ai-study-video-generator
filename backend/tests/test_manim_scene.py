"""
Smoke test -- NOT part of the app. Confirms Manim can actually RENDER
something (Cairo + Pango + ffmpeg all working together), not just that
`import manim` succeeds. Deliberately uses plain Text, not MathTex --
we're avoiding LaTeX entirely (see Dockerfile comments for why).

Run from backend/ with:
manim -pql tests/test_manim_scene.py HelloScene

-p  = preview (opens the video when done)
-ql = quality low (fast render, fine for a smoke test)
"""

from manim import Scene, Text, Write


class HelloScene(Scene):
    def construct(self):
        text = Text("Manim is working!")
        self.play(Write(text))
        self.wait(1)