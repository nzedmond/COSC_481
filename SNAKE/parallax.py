import random
from pyray import *
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

LAYER_DEFS = [
    # Far background — large cave-wall slabs
    {
        "color": Color(18, 12, 28, 255),
        "count": 25,
        "min_w": 60, "max_w": 150,
        "min_h": 80, "max_h": 200,
    },
    # Mid layer — medium pillars
    {
        "color": Color(28, 20, 45, 255),
        "count": 20,
        "min_w": 30, "max_w": 80,
        "min_h": 40, "max_h": 120,
    },
    # Near foreground — small details
    {
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
        rand_num = random.Random(seed)
        self._layers = []
        for layer in LAYER_DEFS:
            rects = []
            for _ in range(layer["count"]):
                wx = rand_num.randint(0, WINDOW_WIDTH)
                wy = rand_num.randint(0, WINDOW_HEIGHT)
                w  = rand_num.randint(layer["min_w"], layer["max_w"])
                h  = rand_num.randint(layer["min_h"], layer["max_h"])
                rects.append((wx, wy, w, h))
            self._layers.append({
                "color": layer["color"],
                "rects": rects,
            })

    def draw(self):
        """Render all layers"""
        clear_background(BG_COLOR)
        for layer in self._layers:
            for x, y, w, h in layer["rects"]:
                draw_rectangle(x, y, w, h, layer["color"])
