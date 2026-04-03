import random
from pyray import *
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

LAYER_DEFS = [
    # Far background — large 
    {
        "speed": 0.15,
        "color": Color(18, 12, 28, 255),
        "count": 25,
        "min_w": 60, "max_w": 150,
        "min_h": 80, "max_h": 200,
    },
    # Mid layer — medium
    {
        "speed": 0.35,
        "color": Color(28, 20, 45, 255),
        "count": 20,
        "min_w": 30, "max_w": 80,
        "min_h": 40, "max_h": 120,
    },
    # Near foreground — small 
    {
        "speed": 0.65,
        "color": Color(40, 30, 65, 255),
        "count": 30,
        "min_w": 10, "max_w": 30,
        "min_h": 20, "max_h": 60,
    },
]

BG_COLOR = Color(8, 6, 16, 255)


class ParallaxBackground:
    """Parallax background built from randomised rectangles.

    Rectangles are generated once with a fixed seed so they look the same
    every run.
    """

    def __init__(self, seed=42):
        rng = random.Random(seed)
        self._layers = []
        for cfg in LAYER_DEFS:
            rects = []
            for _ in range(cfg["count"]):
                wx = rng.randint(0, WINDOW_WIDTH)
                wy = rng.randint(0, WINDOW_HEIGHT)
                w  = rng.randint(cfg["min_w"], cfg["max_w"])
                h  = rng.randint(cfg["min_h"], cfg["max_h"])
                rects.append((wx, wy, w, h))
            self._layers.append({
                "speed": cfg["speed"],
                "color": cfg["color"],
                "rects": rects,
            })

    def draw(self, scroll_x=0):
        """Render all layers. Clears the screen first."""
        clear_background(BG_COLOR)
        for layer in self._layers:
            offset = int(scroll_x * layer["speed"])
            for wx, wy, w, h in layer["rects"]:
                sx = wx - offset
                if sx + w < 0 or sx > WINDOW_WIDTH:
                    continue
                draw_rectangle(sx, wy, w, h, layer["color"])
