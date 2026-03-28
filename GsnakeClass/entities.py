import json
import os
from collections import deque

from pyray import *
from settings import *

# ── Geometry helpers (collision) ──────────────────────────────────────────────

def _cross_product_2d(ax, ay, bx, by):
    return ax * by - ay * bx


def _segments_intersect(p1, p2, p3, p4):
    seg1_dir_x, seg1_dir_y = p2[0] - p1[0], p2[1] - p1[1]
    seg2_dir_x, seg2_dir_y = p4[0] - p3[0], p4[1] - p3[1]
    cross = _cross_product_2d(seg1_dir_x, seg1_dir_y, seg2_dir_x, seg2_dir_y)
    if abs(cross) < 1e-10:
        return False
    offset_x, offset_y = p3[0] - p1[0], p3[1] - p1[1]
    t = _cross_product_2d(offset_x, offset_y, seg2_dir_x, seg2_dir_y) / cross
    u = _cross_product_2d(offset_x, offset_y, seg1_dir_x, seg1_dir_y) / cross
    return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0


def _segment_hits_rect(p1, p2, rect_x, rect_y, rect_w, rect_h):
    def inside(p): return rect_x <= p[0] <= rect_x + rect_w and rect_y <= p[1] <= rect_y + rect_h
    if inside(p1) or inside(p2): return True
    top_left     = (rect_x,          rect_y)
    top_right    = (rect_x + rect_w, rect_y)
    bottom_left  = (rect_x,          rect_y + rect_h)
    bottom_right = (rect_x + rect_w, rect_y + rect_h)
    return any(_segments_intersect(p1, p2, edge[0], edge[1])
               for edge in [(top_left, top_right), (top_right, bottom_right),
                            (bottom_right, bottom_left), (bottom_left, top_left)])


# ── Entities ──────────────────────────────────────────────────────────────────

class Player:
    """The snake's head — owns position, velocity, and steering state.

    Moves automatically to the right every tick at a speed controlled by the
    level's speed curve.  Vertical movement is binary: holding the control input
    drives the head upward; releasing it drives the head downward.  prev_pos is
    recorded at the start of each update so the collision system can sweep-test
    the full movement segment rather than just the endpoint.
    """

    def __init__(self):
        self.pos        = Vector2(100, SCREEN_HEIGHT // 2)
        self.prev_pos   = Vector2(100, SCREEN_HEIGHT // 2)
        self.heading_up = False
        self.speed_mult = 1.0

    def update(self, dt):
        self.prev_pos  = Vector2(self.pos.x, self.pos.y)
        velocity_x     = PLAYER_SPEED_X * self.speed_mult
        velocity_y     = -PLAYER_SPEED_Y if self.heading_up else PLAYER_SPEED_Y
        self.pos.x    += velocity_x * dt
        self.pos.y    += velocity_y * dt


class Trail:
    """A capped history of past player positions that forms the snake's body.

    A new point is appended only when the player has moved at least
    TRAIL_MIN_STEP pixels from the last recorded point, preventing redundant
    entries at low speeds.  The deque is capped at TRAIL_MAX_LENGTH points; the
    oldest point is evicted when the cap is exceeded.  The TrailRenderer in
    ui.py reads this deque each frame to draw the quad-mesh trail.
    """

    def __init__(self):
        self.points = deque()

    def update(self, head):
        if not self.points:
            self.points.appendleft(Vector2(head.x, head.y))
            return
        last_point = self.points[0]
        if ((head.x - last_point.x) ** 2 + (head.y - last_point.y) ** 2) ** 0.5 >= TRAIL_MIN_STEP:
            self.points.appendleft(Vector2(head.x, head.y))
            if len(self.points) > TRAIL_MAX_LENGTH:
                self.points.pop()


class Obstacle:
    """An axis-aligned rectangular obstacle that kills the player on contact.

    Built by Level._build_obstacles() from the JSON level definition.  Stores
    only integer pixel coordinates; the collision system uses these to perform
    segment-rectangle intersection tests each physics tick.
    """

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = int(x), int(y), int(w), int(h)


# ── Level loader ──────────────────────────────────────────────────────────────

SPIKE_WIDTH, SPIKE_HEIGHT = 15, 30


class Level:
    """Loads and exposes a single level from its JSON file.

    Parses the JSON on construction and builds the list of Obstacle objects from
    the raw obstacle definitions (rectangles and spike rows).  Also stores the
    piecewise-linear speed curve, camera overrides, parallax configuration, and
    the raw collectible list.  speed_at(x) interpolates the speed multiplier for
    any world x-coordinate using the curve waypoints.
    """

    def __init__(self, path):
        with open(path) as f:
            raw = json.load(f)
        self.name            = raw["name"]
        self.level_end_x     = int(raw["length"])
        self.speed_curve     = sorted(raw.get("speed_curve", [{"x": 0, "mult": 1.0}]), key=lambda p: p["x"])
        self.camera_config   = raw.get("camera", {})
        self.parallax_seed   = int(raw.get("parallax_seed", 42))
        self.collectibles    = raw.get("collectibles", [])
        self.obstacles       = self._build_obstacles(raw["obstacles"])

    def speed_at(self, x):
        curve = self.speed_curve
        if x <= curve[0]["x"]:  return float(curve[0]["mult"])
        if x >= curve[-1]["x"]: return float(curve[-1]["mult"])
        for i in range(len(curve) - 1):
            x0, multiplier_0 = curve[i]["x"],     curve[i]["mult"]
            x1, multiplier_1 = curve[i + 1]["x"], curve[i + 1]["mult"]
            if x0 <= x <= x1:
                return multiplier_0 + (x - x0) / (x1 - x0) * (multiplier_1 - multiplier_0)
        return float(curve[-1]["mult"])

    def _build_obstacles(self, raw_list):
        obstacles = []
        for item in raw_list:
            if item["type"] == "rect":
                obstacles.append(Obstacle(item["x"], item["y"], item["w"], item["h"]))
            elif item["type"] == "spikes":
                base_y, start_x, count = int(item["y"]), int(item["x"]), int(item["count"])
                for k in range(count):
                    spike_x = start_x + k * SPIKE_WIDTH
                    spike_y = (base_y - SPIKE_HEIGHT) if item.get("dir", "up") == "up" else base_y
                    obstacles.append(Obstacle(spike_x, spike_y, SPIKE_WIDTH, SPIKE_HEIGHT))
        return obstacles


# ── Save manager ──────────────────────────────────────────────────────────────

SAVE_FILE_PATH = "saves/progress.json"


class SaveManager:
    """Persists per-level best scores and completion percentages across sessions.

    Reads saves/progress.json on startup and writes it back after every run.
    Each level is keyed by its name string and stores best_score, best_pct
    (0.0–1.0), and total attempt count.  update() returns True when the run
    sets a new best score or completion percentage, which the game uses to
    display the "NEW BEST!" indicator.
    """

    def __init__(self):
        self._data = {}
        if os.path.exists(SAVE_FILE_PATH):
            try:
                with open(SAVE_FILE_PATH) as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    def get_best(self, level_name):
        entry = self._data.get(level_name, {})
        return entry.get("best_score", 0), entry.get("best_pct", 0.0), entry.get("attempts", 0)

    def update(self, level_name, score, completion):
        entry = self._data.get(level_name, {"best_score": 0, "best_pct": 0.0, "attempts": 0})
        entry["attempts"] += 1
        new_best = False
        if score      > entry["best_score"]: entry["best_score"] = score;                  new_best = True
        if completion > entry["best_pct"]:   entry["best_pct"]   = round(completion, 4);  new_best = True
        self._data[level_name] = entry
        os.makedirs(os.path.dirname(SAVE_FILE_PATH), exist_ok=True)
        with open(SAVE_FILE_PATH, "w") as f:
            json.dump(self._data, f, indent=2)
        return new_best
