import math
import random
from pyray import *
from settings import *

# ── Trail colour ──────────────────────────────────────────────────────────────

TRAIL_HEAD_COLOR  = (0,   220, 255)   # bright cyan at level start
TRAIL_TAIL_COLOR  = (255,  60, 200)   # hot magenta at level end
TRAIL_WHITE_COLOR = (255, 255, 255)


def interpolate_color(start_color, end_color, t):
    t = max(0.0, min(1.0, t))
    return (int(start_color[0] + (end_color[0] - start_color[0]) * t),
            int(start_color[1] + (end_color[1] - start_color[1]) * t),
            int(start_color[2] + (end_color[2] - start_color[2]) * t))


def current_trail_color(progress):
    return interpolate_color(TRAIL_HEAD_COLOR, TRAIL_TAIL_COLOR, progress)


# ── Parallax background ───────────────────────────────────────────────────────

PARALLAX_LAYER_CONFIGS = [
    {"speed": 0.15, "color": Color(18, 12, 28, 255),  "count": 25, "min_w": 60,  "max_w": 150, "min_h": 80,  "max_h": 200},
    {"speed": 0.35, "color": Color(28, 20, 45, 255),  "count": 20, "min_w": 30,  "max_w": 80,  "min_h": 40,  "max_h": 120},
    {"speed": 0.65, "color": Color(40, 30, 65, 255),  "count": 30, "min_w": 10,  "max_w": 30,  "min_h": 20,  "max_h":  60},
]
CAVE_BACKGROUND_COLOR = Color(8, 6, 16, 255)


class ParallaxBackground:
    def __init__(self, level_width=LEVEL_WIDTH, seed=42, speed_overrides=None):
        rng = random.Random(seed)
        self._layers = []
        for i, layer_config in enumerate(PARALLAX_LAYER_CONFIGS):
            speed = layer_config["speed"]
            if speed_overrides and i < len(speed_overrides):
                speed = float(speed_overrides[i].get("speed", speed))
            rectangles = [(rng.randint(0, level_width), rng.randint(0, SCREEN_HEIGHT),
                           rng.randint(layer_config["min_w"], layer_config["max_w"]),
                           rng.randint(layer_config["min_h"], layer_config["max_h"]))
                          for _ in range(layer_config["count"])]
            self._layers.append({"speed": speed, "color": layer_config["color"], "rectangles": rectangles})

    def draw(self, scroll_x):
        clear_background(CAVE_BACKGROUND_COLOR)
        for layer in self._layers:
            offset = int(scroll_x * layer["speed"])
            for world_x, world_y, width, height in layer["rectangles"]:
                screen_x = world_x - offset
                if 0 <= screen_x + width and screen_x <= SCREEN_WIDTH:
                    draw_rectangle(screen_x, world_y, width, height, layer["color"])


# ── Trail renderer ────────────────────────────────────────────────────────────

def _draw_quad_as_triangles(p1, p2, p3, p4, color):
    draw_triangle(p2, p1, p4, color)
    draw_triangle(p1, p3, p4, color)


def _draw_trail_segment(point_a, point_b, half_width, color):
    delta_x  = point_b.x - point_a.x
    delta_y  = point_b.y - point_a.y
    length   = (delta_x * delta_x + delta_y * delta_y) ** 0.5
    if length < 0.001:
        return
    normal_x = -delta_y / length
    normal_y =  delta_x / length
    p1 = Vector2(point_a.x + normal_x * half_width, point_a.y + normal_y * half_width)
    p2 = Vector2(point_a.x - normal_x * half_width, point_a.y - normal_y * half_width)
    p3 = Vector2(point_b.x + normal_x * half_width, point_b.y + normal_y * half_width)
    p4 = Vector2(point_b.x - normal_x * half_width, point_b.y - normal_y * half_width)
    _draw_quad_as_triangles(p1, p2, p3, p4, color)


class TrailRenderer:
    def draw(self, points, progress, speed_mult):
        point_list  = list(points)
        point_count = len(point_list)
        if point_count < 2:
            return
        trail_color     = current_trail_color(progress)
        base_half_width = TRAIL_CORE_RADIUS + speed_mult * 1.5

        # Pass 1 — glow layer (near the head only)
        glow_segment_count = min(point_count - 1, TRAIL_GLOW_LENGTH)
        for i in range(glow_segment_count):
            taper      = 1.0 - i / glow_segment_count
            half_width = base_half_width * TRAIL_GLOW_MULTIPLIER * taper
            if half_width >= 0.5:
                _draw_trail_segment(point_list[i], point_list[i + 1], half_width,
                                    Color(trail_color[0], trail_color[1], trail_color[2],
                                          int(TRAIL_GLOW_ALPHA * taper)))

        # Pass 2 — solid core (full length, tapered toward tail)
        for i in range(point_count - 1):
            taper         = 1.0 - i / point_count
            half_width    = max(0.4, base_half_width * taper)
            segment_color = interpolate_color(TRAIL_WHITE_COLOR, trail_color, i / point_count)
            _draw_trail_segment(point_list[i], point_list[i + 1], half_width,
                                Color(segment_color[0], segment_color[1], segment_color[2], 255))


# ── Particle system ───────────────────────────────────────────────────────────

class _Particle:
    __slots__ = ('x', 'y', 'velocity_x', 'velocity_y', 'life', 'max_life', 'red', 'green', 'blue')
    def __init__(self): self.life = 0.0


class ParticleSystem:
    def __init__(self, pool_size=PARTICLE_POOL_SIZE):
        self._pool = [_Particle() for _ in range(pool_size)]

    def emit_burst(self, x, y, count, speed, color):
        emitted = 0
        for particle in self._pool:
            if emitted >= count: break
            if particle.life <= 0.0:
                angle                    = random.random() * 6.283185307
                particle_speed           = speed * (0.5 + random.random() * 0.5)
                particle.x, particle.y   = x, y
                particle.velocity_x      = math.cos(angle) * particle_speed
                particle.velocity_y      = math.sin(angle) * particle_speed
                particle.max_life        = 0.3 + random.random() * 0.4
                particle.life            = particle.max_life
                particle.red, particle.green, particle.blue = color
                emitted += 1

    def update(self, dt):
        for particle in self._pool:
            if particle.life > 0.0:
                particle.x          += particle.velocity_x * dt
                particle.y          += particle.velocity_y * dt
                particle.velocity_y += 150.0 * dt
                particle.life       -= dt

    def draw(self):
        for particle in self._pool:
            if particle.life > 0.0:
                lifetime_ratio = max(0.0, particle.life / particle.max_life)
                draw_circle(int(particle.x), int(particle.y),
                            max(1, int(3 * lifetime_ratio)),
                            Color(particle.red, particle.green, particle.blue,
                                  int(255 * lifetime_ratio)))


# ── Screen effects ────────────────────────────────────────────────────────────

class ScreenEffects:
    def __init__(self):
        self._fade_alpha = 255.0
        self._fading_in  = False

    def start_fade_in(self):
        self._fade_alpha = 255.0
        self._fading_in  = True

    def update(self, dt):
        if self._fading_in:
            self._fade_alpha -= (255.0 / FADE_DURATION) * dt
            if self._fade_alpha <= 0.0:
                self._fade_alpha = 0.0
                self._fading_in  = False

    def draw(self):
        for i in range(VIGNETTE_LAYERS):
            band_fade_ratio = 1.0 - i / VIGNETTE_LAYERS
            band_color      = Color(0, 0, 0, int(VIGNETTE_MAX_ALPHA * band_fade_ratio * band_fade_ratio))
            draw_rectangle(0,                    i,                     SCREEN_WIDTH,  1, band_color)
            draw_rectangle(0,                    SCREEN_HEIGHT - 1 - i, SCREEN_WIDTH,  1, band_color)
            draw_rectangle(i,                    0,                     1, SCREEN_HEIGHT, band_color)
            draw_rectangle(SCREEN_WIDTH - 1 - i, 0,                     1, SCREEN_HEIGHT, band_color)
        if self._fade_alpha > 0.0:
            draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                           Color(0, 0, 0, int(self._fade_alpha)))


# ── HUD ───────────────────────────────────────────────────────────────────────

PROGRESS_BAR_Y      = SCREEN_HEIGHT - 16
PROGRESS_BAR_MARGIN = 40
COLOR_LABEL         = Color(160, 160, 160, 255)
COLOR_UNCOLLECTED_DOT = Color(90, 90, 90, 255)
COLOR_BAR_BACKGROUND  = Color(40,  40,  40,  200)
COLOR_BAR_FILL        = Color(0,  220, 255,  220)


class HUD:
    def draw(self, score, collected, total, progress):
        draw_rectangle(8, 8, 200, 58, Color(0, 0, 0, 150))
        draw_rectangle_lines(8, 8, 200, 58, Color(255, 255, 255, 30))

        draw_text("SCORE", 18, 18, 12, COLOR_LABEL)
        score_text = f"{score:,}"
        draw_text(score_text, 208 - 10 - measure_text(score_text, 18), 16, 18, WHITE)

        collectibles_row_y = 44
        if total <= 12:
            for i in range(total):
                dot_x = 22 + i * 15
                if i < collected:
                    draw_circle(dot_x, collectibles_row_y, 5, YELLOW)
                else:
                    draw_circle_lines(dot_x, collectibles_row_y, 5, COLOR_UNCOLLECTED_DOT)
        else:
            draw_text("ITEMS", 18, collectibles_row_y - 6, 12, COLOR_LABEL)
            draw_text(f"{collected} / {total}", 68, collectibles_row_y - 7, 14, YELLOW)

        bar_width    = SCREEN_WIDTH - PROGRESS_BAR_MARGIN * 2
        filled_width = int(bar_width * max(0.0, min(1.0, progress)))
        draw_rectangle(PROGRESS_BAR_MARGIN, PROGRESS_BAR_Y, bar_width,    6, COLOR_BAR_BACKGROUND)
        if filled_width > 0:
            draw_rectangle(PROGRESS_BAR_MARGIN, PROGRESS_BAR_Y, filled_width, 6, COLOR_BAR_FILL)
        progress_text = f"{progress:.0%}"
        draw_text(progress_text, PROGRESS_BAR_MARGIN + bar_width + 8,
                  PROGRESS_BAR_Y - 2, 12, COLOR_LABEL)


# ── Menus ─────────────────────────────────────────────────────────────────────

COLOR_PANEL_BACKGROUND = Color(15,  15,  25, 230)
COLOR_TITLE            = Color(0,  220, 255, 255)
COLOR_BODY_TEXT        = Color(200, 200, 200, 255)
COLOR_DIMMED_TEXT      = Color(120, 120, 120, 255)
COLOR_SUCCESS          = Color(80,  220, 100, 255)
COLOR_DANGER           = Color(255,  80,  80, 255)
COLOR_BORDER           = Color(255, 255, 255,  40)
SCREEN_CENTER_X        = SCREEN_WIDTH  // 2
SCREEN_CENTER_Y        = SCREEN_HEIGHT // 2


def draw_panel(x, y, width, height):
    draw_rectangle(x, y, width, height, COLOR_PANEL_BACKGROUND)
    draw_rectangle_lines(x, y, width, height, COLOR_BORDER)


def draw_centered_text(text, y, size, color):
    draw_text(text, SCREEN_CENTER_X - measure_text(text, size) // 2, y, size, color)


def draw_key_hint(key, action, y):
    draw_centered_text(f"[{key}]  {action}", y, 14, YELLOW)


class MainMenu:
    def __init__(self, levels, save):
        self._levels   = levels
        self._save     = save
        self._selected = 0

    def handle_input(self):
        if is_key_pressed(KEY_DOWN):  self._selected = (self._selected + 1) % len(self._levels)
        if is_key_pressed(KEY_UP):    self._selected = (self._selected - 1) % len(self._levels)
        if is_key_pressed(KEY_ENTER) or is_key_pressed(KEY_SPACE):
            return "play"
        return None

    @property
    def selected_level_path(self): return self._levels[self._selected]["path"]

    def draw(self):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(0, 0, 0, 210))
        draw_centered_text("GEOMETRY SNAKE", SCREEN_CENTER_Y - 160, 48, COLOR_TITLE)
        draw_centered_text("navigate the cave without touching walls",
                           SCREEN_CENTER_Y - 105, 14, COLOR_DIMMED_TEXT)

        panel_width  = 420
        panel_height = 30 + len(self._levels) * 54 + 16
        panel_left   = SCREEN_CENTER_X - panel_width // 2
        panel_top    = SCREEN_CENTER_Y - 60
        draw_panel(panel_left, panel_top, panel_width, panel_height)

        for i, level in enumerate(self._levels):
            level_row_y = panel_top + 16 + i * 54
            if i == self._selected:
                draw_rectangle(panel_left + 4, level_row_y - 2,
                               panel_width - 8, 50, Color(0, 220, 255, 18))
            draw_centered_text(level["name"], level_row_y, 20,
                               COLOR_TITLE if i == self._selected else WHITE)
            best_score, best_completion, attempts = self._save.get_best(level["name"])
            if attempts == 0:
                draw_centered_text("No attempts yet", level_row_y + 24, 12, COLOR_DIMMED_TEXT)
            else:
                draw_centered_text(
                    f"Best: {best_score:,} pts  |  {best_completion:.1%} complete  |  "
                    f"{attempts} attempt{'s' if attempts != 1 else ''}",
                    level_row_y + 24, 12, COLOR_BODY_TEXT)

        hints_y = panel_top + panel_height + 20
        draw_key_hint("UP / DOWN",          "select level", hints_y)
        draw_key_hint("SPACE / ENTER",      "start",        hints_y + 22)
        draw_key_hint("HOLD SPACE / MOUSE", "steer up",     hints_y + 44)


class PauseMenu:
    def draw(self):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(0, 0, 0, 120))
        draw_panel(SCREEN_CENTER_X - 150, SCREEN_CENTER_Y - 70, 300, 140)
        draw_centered_text("PAUSED", SCREEN_CENTER_Y - 46, 28, WHITE)
        draw_key_hint("P", "resume",       SCREEN_CENTER_Y +  2)
        draw_key_hint("M", "quit to menu", SCREEN_CENTER_Y + 26)


class GameOverMenu:
    def draw(self, score, best_score, completion, best_completion, new_best):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(0, 0, 0, 150))
        draw_panel(SCREEN_CENTER_X - 180, SCREEN_CENTER_Y - 100, 360, 200)
        draw_centered_text("GAME OVER",                                             SCREEN_CENTER_Y - 82, 30, COLOR_DANGER)
        draw_centered_text(f"Score:    {score:,}",                                  SCREEN_CENTER_Y - 38, 18, WHITE)
        draw_centered_text(f"Reached:  {completion:.1%}",                           SCREEN_CENTER_Y - 14, 18, WHITE)
        draw_centered_text(f"Best:     {best_score:,}  |  {best_completion:.1%}",   SCREEN_CENTER_Y + 10, 14, COLOR_BODY_TEXT)
        if new_best: draw_centered_text("NEW BEST!", SCREEN_CENTER_Y + 34, 16, COLOR_SUCCESS)
        draw_key_hint("R", "retry",        SCREEN_CENTER_Y + 60)
        draw_key_hint("M", "quit to menu", SCREEN_CENTER_Y + 82)


class LevelCompleteMenu:
    def draw(self, score, best_score, best_completion, new_best):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Color(0, 0, 0, 150))
        draw_panel(SCREEN_CENTER_X - 180, SCREEN_CENTER_Y - 100, 360, 200)
        draw_centered_text("LEVEL COMPLETE!",                                       SCREEN_CENTER_Y - 82, 28, COLOR_SUCCESS)
        draw_centered_text(f"Score:  {score:,}",                                    SCREEN_CENTER_Y - 38, 18, WHITE)
        draw_centered_text(f"Best:   {best_score:,}  |  {best_completion:.1%}",     SCREEN_CENTER_Y - 14, 14, COLOR_BODY_TEXT)
        if new_best: draw_centered_text("NEW BEST!", SCREEN_CENTER_Y + 10, 16, COLOR_SUCCESS)
        draw_key_hint("R", "play again",   SCREEN_CENTER_Y + 50)
        draw_key_hint("M", "quit to menu", SCREEN_CENTER_Y + 72)


# ── In-game renderer ──────────────────────────────────────────────────────────

class Renderer:
    def __init__(self, player, trail, obstacles, camera, parallax, particles, collectibles):
        self.player          = player
        self.trail           = trail
        self.obstacles       = obstacles
        self.camera          = camera
        self.parallax        = parallax
        self.particles       = particles
        self.collectibles    = collectibles
        self._trail_renderer = TrailRenderer()

    def draw(self, progress, speed_mult):
        self.parallax.draw(self.camera.scroll_x)
        self.camera.begin()
        for obstacle in self.obstacles:
            draw_rectangle(obstacle.x, obstacle.y, obstacle.w, obstacle.h, RED)
        current_time = get_time()
        for collectible in self.collectibles:
            if collectible.collected: continue
            bob    = math.sin(current_time * 2.5 + collectible.x * 0.01) * 4.0
            center = Vector2(collectible.x, collectible.y + bob)
            red, green, blue = collectible.color
            draw_circle_v(center, collectible.radius * 1.8, Color(red, green, blue, 35))
            if collectible.type == "gem":
                draw_poly(center, 4, collectible.radius,        45.0, Color(red, green, blue, 255))
                draw_poly(center, 4, collectible.radius * 0.5,  45.0, Color(255, 255, 255, 180))
            elif collectible.type == "coin":
                draw_circle_v(center, collectible.radius,        Color(red, green, blue, 255))
                draw_circle_v(center, collectible.radius * 0.5,  Color(min(red + 30, 255), min(green + 30, 255), 0, 200))
            elif collectible.type == "star":
                draw_poly(center, 5, collectible.radius,        -18.0, Color(red, green, blue, 255))
                draw_circle_v(center, collectible.radius * 0.35, Color(255, 255, 255, 200))
        self._trail_renderer.draw(self.trail.points, progress, speed_mult)
        player_x, player_y = int(self.player.pos.x), int(self.player.pos.y)
        trail_red, trail_green, trail_blue = current_trail_color(progress)
        draw_circle(player_x, player_y, 12, Color(trail_red, trail_green, trail_blue, 60))
        draw_circle(player_x, player_y,  6, WHITE)
        self.particles.draw()
        self.camera.end()
