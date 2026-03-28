import json
import os
from collections import deque
from enum import Enum

from pyray import *
from settings import *
from camera import Camera
from collectible import build_collectibles
from ui import (ParallaxBackground, ParticleSystem, ScreenEffects,
                HUD, MainMenu, PauseMenu, GameOverMenu, LevelCompleteMenu,
                Renderer, current_trail_color)

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
        self.vel        = Vector2(PLAYER_SPEED_X, 0.0)
        self.heading_up = False
        self.speed_mult = 1.0

    def update(self, dt):
        self.prev_pos  = Vector2(self.pos.x, self.pos.y)
        velocity_x     = PLAYER_SPEED_X * self.speed_mult
        velocity_y     = -PLAYER_SPEED_Y if self.heading_up else PLAYER_SPEED_Y
        self.vel       = Vector2(velocity_x, velocity_y)
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
        self.parallax_config = raw.get("parallax", [])
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


# ── Game ──────────────────────────────────────────────────────────────────────

class GameState(Enum):
    """The five mutually exclusive states the game can be in at any moment.

    The Game class holds one current state and routes input and rendering
    through a match statement based on it.
    """

    MENU = 0; PLAYING = 1; PAUSED = 2; GAME_OVER = 3; LEVEL_COMPLETE = 4


GAME_LEVELS = [
    {"name": "Cave Run",       "path": "levels/level1.json"},
    {"name": "Crystal Depths", "path": "levels/level2.json"},
    {"name": "The Gauntlet",   "path": "levels/level3.json"},
]

PICKUP_DETECTION_RADIUS = 8.0
PICKUP_PARTICLE_COUNT   = 15
PICKUP_PARTICLE_SPEED   = 120


class Game:
    """Top-level controller that owns the game loop and all runtime objects.

    Initialises the raylib window and creates the menus and save manager in
    __init__.  reset() builds a fresh level, player, trail, camera, and renderer
    each time a run starts.  run() is the main loop: _update() advances the
    state machine and runs fixed-timestep physics ticks via _tick(), while
    _render() draws everything for the current frame.  All other classes are
    either called from here or passed into the Renderer.
    """

    def __init__(self):
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Geometry Snake")
        set_target_fps(FPS)

        self._save                = SaveManager()
        self._hud                 = HUD()
        self._pause_menu          = PauseMenu()
        self._game_over_menu      = GameOverMenu()
        self._level_complete_menu = LevelCompleteMenu()
        self._main_menu           = MainMenu(GAME_LEVELS, self._save)
        self._physics_accumulator = 0.0
        self._debug               = False
        self.state                = GameState.MENU
        self._run_score           = self._best_score      = 0
        self._run_completion      = self._best_completion = 0.0
        self._new_best            = False

    def reset(self):
        self.state                = GameState.PLAYING
        self._physics_accumulator = 0.0
        self.level        = Level(self._main_menu.selected_level_path)
        self.player       = Player()
        self.trail        = Trail()
        self.collectibles = build_collectibles(self.level.collectibles)
        self._score       = 0
        self._collected   = 0

        camera_config  = self.level.camera_config
        self.camera    = Camera(self.level.level_end_x,
                                camera_config.get("lookahead", CAMERA_LOOKAHEAD),
                                camera_config.get("lerp",      CAMERA_LERP))
        self.parallax  = ParallaxBackground(self.level.level_end_x,
                                            self.level.parallax_seed,
                                            self.level.parallax_config)
        self.particles = ParticleSystem()
        self.effects   = ScreenEffects()
        self.effects.start_fade_in()
        self.renderer  = Renderer(self.player, self.trail, self.level.obstacles,
                                  self.camera, self.parallax, self.particles,
                                  self.collectibles)

    def run(self):
        while not window_should_close():
            dt = get_frame_time()
            self._update(dt)
            self._render()
        close_window()

    def _update(self, dt):
        match self.state:
            case GameState.MENU:
                if self._main_menu.handle_input() == "play": self.reset()
                return
            case GameState.GAME_OVER | GameState.LEVEL_COMPLETE:
                if is_key_pressed(KEY_R): self.reset()
                elif is_key_pressed(KEY_M): self.state = GameState.MENU
                return
            case GameState.PAUSED:
                if is_key_pressed(KEY_P):
                    self._physics_accumulator = 0.0
                    self.state = GameState.PLAYING
                elif is_key_pressed(KEY_M): self.state = GameState.MENU
                return

        if is_key_pressed(KEY_D): self._debug = not self._debug
        if is_key_pressed(KEY_P): self.state = GameState.PAUSED; return

        self._physics_accumulator = min(self._physics_accumulator + dt, MAX_ACCUMULATOR)
        steering_up = is_key_down(KEY_SPACE) or is_mouse_button_down(MOUSE_LEFT_BUTTON)
        while self._physics_accumulator >= FIXED_DT:
            self._tick(steering_up, FIXED_DT)
            self._physics_accumulator -= FIXED_DT

    def _tick(self, steering_up, dt):
        self.player.speed_mult = self.level.speed_at(self.player.pos.x)
        self.player.heading_up = steering_up
        self.player.update(dt)
        self.trail.update(self.player.pos)
        self.camera.update(self.player.pos, dt)
        self.particles.update(dt)
        self.effects.update(dt)

        if self.player.pos.x >= self.level.level_end_x:
            self._end(completed=True); return

        for collectible in self.collectibles:
            if collectible.collected: continue
            delta_x = self.player.pos.x - collectible.x
            delta_y = self.player.pos.y - collectible.y
            if (delta_x * delta_x + delta_y * delta_y) ** 0.5 < collectible.radius + PICKUP_DETECTION_RADIUS:
                collectible.collected = True
                self._score     += collectible.value
                self._collected += 1
                self.particles.emit_burst(collectible.x, collectible.y,
                                          PICKUP_PARTICLE_COUNT, PICKUP_PARTICLE_SPEED,
                                          collectible.color)

        player_pos = self.player.pos
        if player_pos.y < 0 or player_pos.y > SCREEN_HEIGHT:
            self._die(); return

        prev_head = (self.player.prev_pos.x, self.player.prev_pos.y)
        curr_head = (player_pos.x, player_pos.y)
        for obstacle in self.level.obstacles:
            if abs(player_pos.x - obstacle.x) > LOOKAHEAD: continue
            if _segment_hits_rect(prev_head, curr_head, obstacle.x, obstacle.y, obstacle.w, obstacle.h):
                self._die(); return

    def _die(self):
        progress = min(1.0, self.player.pos.x / self.level.level_end_x)
        self.particles.emit_burst(self.player.pos.x, self.player.pos.y,
                                  PARTICLE_DEATH_COUNT, PARTICLE_DEATH_SPEED,
                                  current_trail_color(progress))
        self._end(completed=False)

    def _end(self, completed):
        progress               = min(1.0, self.player.pos.x / self.level.level_end_x)
        self._new_best         = self._save.update(self.level.name, self._score, progress)
        self._best_score, self._best_completion, _ = self._save.get_best(self.level.name)
        self._run_score        = self._score
        self._run_completion   = progress
        self.state             = GameState.LEVEL_COMPLETE if completed else GameState.GAME_OVER

    def _render(self):
        begin_drawing()
        if self.state == GameState.MENU:
            clear_background(BLACK)
            self._main_menu.draw()
            end_drawing()
            return

        progress = min(1.0, self.player.pos.x / self.level.level_end_x)
        self.renderer.draw(progress, self.player.speed_mult)
        self.effects.draw()
        self._hud.draw(self._score, self._collected, len(self.collectibles), progress)

        if self.state == GameState.PAUSED:
            self._pause_menu.draw()
        elif self.state == GameState.GAME_OVER:
            self._game_over_menu.draw(self._run_score, self._best_score,
                                      self._run_completion, self._best_completion, self._new_best)
        elif self.state == GameState.LEVEL_COMPLETE:
            self._level_complete_menu.draw(self._run_score, self._best_score,
                                           self._best_completion, self._new_best)

        if self._debug:
            debug_lines = [
                f"FPS:      {get_fps()}",
                f"Pos:      ({self.player.pos.x:.1f}, {self.player.pos.y:.1f})",
                f"Speed:    {self.player.speed_mult:.2f}",
                f"Progress: {progress:.1%}",
                f"Score:    {self._score}",
                f"Scroll X: {self.camera.scroll_x:.1f}",
                f"State:    {self.state.name}",
            ]
            draw_rectangle(8, 26, 160, 8 + 18 * len(debug_lines), Color(0, 0, 120, 200))
            for i, line in enumerate(debug_lines):
                draw_text(line, 12, 30 + i * 18, 14, GREEN)

        end_drawing()


if __name__ == "__main__":
    Game().run()
