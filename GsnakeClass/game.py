from enum import Enum

from pyray import *
from settings import *
from camera import Camera
from collectible import build_collectibles
from ui import (ParallaxBackground, ParticleSystem, ScreenEffects,
                HUD, MainMenu, PauseMenu, GameOverMenu, LevelCompleteMenu,
                Renderer, current_trail_color)
from entities import Player, Trail, Level, SaveManager, _segment_hits_rect

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
                                            self.level.parallax_seed)
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
