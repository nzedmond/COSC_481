import random
from pyray import *
from config.settings import *

# Layer definitions: speed=0 means fixed on screen, speed=1 moves 1:1 with camera.
# Lower speed → appears farther away.
_LAYER_DEFS = [
    # Far background — large cave-wall slabs
    {
        "speed": 0.15,
        "color": Color(18, 12, 28, 255),
        "count": 25,
        "min_w": 60, "max_w": 150,
        "min_h": 80, "max_h": 200,
    },
    # Mid layer — medium pillars/stalactites
    {
        "speed": 0.35,
        "color": Color(28, 20, 45, 255),
        "count": 20,
        "min_w": 30, "max_w": 80,
        "min_h": 40, "max_h": 120,
    },
    # Near foreground — small details
    {
        "speed": 0.65,
        "color": Color(40, 30, 65, 255),
        "count": 30,
        "min_w": 10, "max_w": 30,
        "min_h": 20, "max_h": 60,
    },
]

_BG_COLOR = Color(8, 6, 16, 255)


class ParallaxBackground:
    """Procedural parallax background built from randomised rectangles.

    Elements are generated once at construction with a fixed seed so they
    are deterministic across resets. Draw this BEFORE camera.begin() so
    elements stay in screen space.
    """

    def __init__(self, level_width=LEVEL_WIDTH, seed=42, speed_overrides=None):
        """speed_overrides: optional list of {"speed": float} from level JSON,
        one entry per layer.  Extra or missing entries are handled gracefully."""
        rng = random.Random(seed)
        self._layers = []
        for i, cfg in enumerate(_LAYER_DEFS):
            speed = cfg["speed"]
            if speed_overrides and i < len(speed_overrides):
                speed = float(speed_overrides[i].get("speed", speed))
            rects = []
            for _ in range(cfg["count"]):
                wx = rng.randint(0, level_width)
                wy = rng.randint(0, SCREEN_HEIGHT)
                w  = rng.randint(cfg["min_w"], cfg["max_w"])
                h  = rng.randint(cfg["min_h"], cfg["max_h"])
                rects.append((wx, wy, w, h))
            self._layers.append({
                "speed": speed,
                "color": cfg["color"],
                "rects": rects,
            })

    def draw(self, scroll_x):
        """Render all layers.  scroll_x is camera.scroll_x (world units)."""
        clear_background(_BG_COLOR)

        for layer in self._layers:
            offset = int(scroll_x * layer["speed"])
            for wx, wy, w, h in layer["rects"]:
                sx = wx - offset
                if sx + w < 0 or sx > SCREEN_WIDTH:
                    continue
                draw_rectangle(sx, wy, w, h, layer["color"])
