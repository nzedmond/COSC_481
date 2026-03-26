from pyray import *
from config.settings import *
from core.input_manager import InputManager
from core.state import GameState
from entities.player import Player
from entities.trail import Trail
from entities.collectible import build_collectibles
from systems.level import Level
from systems.collision_manager import CollisionManager
from systems.score_manager import ScoreManager
from systems.save_manager import SaveManager
from rendering.renderer import Renderer
from rendering.camera import Camera
from rendering.parallax import ParallaxBackground
from rendering.particle_system import ParticleSystem
from rendering.effects import ScreenEffects
from rendering.hud import HUD
from rendering.menu import MainMenu, PauseMenu, GameOverMenu, LevelCompleteMenu
from rendering.trail_renderer import current_trail_color

_PICKUP_RADIUS = 8.0   # extra tolerance added to collectible.radius on pickup

_LEVELS = [
    {"name": "Cave Run",      "path": "levels/level1.json"},
    {"name": "Crystal Depths","path": "levels/level2.json"},
    {"name": "The Gauntlet",  "path": "levels/level3.json"},
]


class Game:
    def __init__(self):
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Geometry Snake")
        set_target_fps(FPS)

        self.input                  = InputManager()
        self._physics_accumulator   = 0.0
        self._debug_mode            = False
        self._collision_check_count = 0

        self._save    = SaveManager()
        self._hud     = HUD()
        self._pause_menu    = PauseMenu()
        self._over_menu     = GameOverMenu()
        self._complete_menu = LevelCompleteMenu()
        self._main_menu     = MainMenu(_LEVELS, self._save)

        # Runtime result cache (populated on game-over / level-complete)
        self._run_score        = 0
        self._run_completion   = 0.0
        self._best_score       = 0
        self._best_completion  = 0.0
        self._is_new_best      = False

        # Start on the main menu
        self.state = GameState.MENU

    def reset(self, level_path=None):
        self.state = GameState.PLAYING
        self._physics_accumulator   = 0.0
        self._collision_check_count = 0

        path = level_path or self._main_menu.selected_level_path
        self.level        = Level(path)
        self.player       = Player()
        self.trail        = Trail()
        self.collectibles = build_collectibles(self.level.collectibles)

        self.score_manager = ScoreManager()
        self.score_manager.setup(len(self.collectibles))

        camera_config = self.level.camera_config
        self.camera = Camera(
            level_width=self.level.level_end_x,
            lookahead=camera_config.get("lookahead", CAMERA_LOOKAHEAD),
            lerp=camera_config.get("lerp", CAMERA_LERP),
        )
        self.parallax = ParallaxBackground(
            level_width=self.level.level_end_x,
            seed=self.level.parallax_seed,
            speed_overrides=self.level.parallax_config,
        )
        self.particles = ParticleSystem()
        self.effects   = ScreenEffects()
        self.effects.start_fade_in()

        self.collision = CollisionManager(
            self.player, self.trail, self.level.obstacles,
        )
        self.renderer = Renderer(
            self.player, self.trail, self.level.obstacles,
            self.camera, self.parallax, self.particles,
            self.collectibles,
        )

    # ------------------------------------------------------------------
    #                          MAIN LOOP
    # ------------------------------------------------------------------

    def run(self):
        '''Called once per rendered frame = varies with frame rate'''
        
        while not window_should_close():
            dt = get_frame_time()
            self._update_loop(dt)
            self._render()
        close_window()

    def _update_loop(self, dt):
        '''Handle everything that varies with real time: key presses and state transitions.'''
        
        if self.state == GameState.MENU:
            action = self._main_menu.handle_input()
            if action == "play":
                self.reset()
            return

        if is_key_pressed(KEY_D):
            self._debug_mode = not self._debug_mode

        if self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):  # WILL USE MATCH/CASE BEFORE SUBMITTING
            if is_key_pressed(KEY_R):
                self.reset()
            elif is_key_pressed(KEY_M):
                self.state = GameState.MENU
            return

        if self.state == GameState.PAUSED:
            if is_key_pressed(KEY_P):
                self._physics_accumulator = 0.0
                self.state = GameState.PLAYING
            elif is_key_pressed(KEY_M):
                self.state = GameState.MENU
            return

        if self.state == GameState.PLAYING:
            if is_key_pressed(KEY_P):
                self.state = GameState.PAUSED
                return

        # add the elapsed time to the running total. Decide how many physics ticks are due
        self._physics_accumulator += dt
        if self._physics_accumulator > MAX_ACCUMULATOR:
            self._physics_accumulator = MAX_ACCUMULATOR

        is_input_held = self.input.is_holding()
        while self._physics_accumulator >= FIXED_DT:
            self._fixed_update(is_input_held, FIXED_DT)
            self._physics_accumulator -= FIXED_DT

    def _fixed_update(self, is_input_held, dt):
        '''Physics tick: dt=1/60 always. Move the player, grow the trail, update the camera, check collisions.'''
        
        self.player.speed_mult = self.level.speed_multiplier_at(self.player.pos.x)
        self.player.apply_control(is_input_held)
        self.player.update(dt)
        self.trail.update(self.player.pos)
        self.camera.update(self.player.pos, dt)
        self.particles.update(dt)
        self.effects.update(dt)

        if self.player.pos.x >= self.level.level_end_x:
            self._end_run(completed=True)
            return

        self._check_collectibles()

        self._collision_check_count += 1
        if self.collision.check_all():
            progress = min(1.0, self.player.pos.x / self.level.level_end_x)
            self.camera.add_trauma(SHAKE_DEATH_TRAUMA)
            self.particles.emit_burst(
                self.player.pos.x, self.player.pos.y,
                PARTICLE_DEATH_COUNT,
                PARTICLE_DEATH_SPEED,
                current_trail_color(progress),
            )
            self._end_run(completed=False)

    def _end_run(self, completed: bool):
        completion_progress = min(1.0, self.player.pos.x / self.level.level_end_x)
        current_score       = self.score_manager.score
        level_name          = self.level.name

        is_new_best = self._save.update(level_name, current_score, completion_progress)
        saved_best_score, saved_best_completion, _ = self._save.get_best(level_name)

        self._run_score       = current_score
        self._run_completion  = completion_progress
        self._best_score      = saved_best_score
        self._best_completion = saved_best_completion
        self._is_new_best     = is_new_best

        self.state = GameState.LEVEL_COMPLETE if completed else GameState.GAME_OVER

    def _check_collectibles(self):
        player_x, player_y = self.player.pos.x, self.player.pos.y
        for collectible in self.collectibles:
            if collectible.collected:
                continue
            delta_x = player_x - collectible.x
            delta_y = player_y - collectible.y
            if (delta_x * delta_x + delta_y * delta_y) ** 0.5 < collectible.radius + _PICKUP_RADIUS:
                collectible.collected = True
                self.score_manager.collect(collectible.value)
                self.particles.emit_burst(
                    collectible.x, collectible.y, 15, 120, collectible.color,
                )

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def _render(self):
        begin_drawing()

        if self.state == GameState.MENU:
            clear_background(BLACK)
            self._main_menu.draw()
            end_drawing()
            return

        interpolation_factor = self._physics_accumulator / FIXED_DT
        progress = min(1.0, self.player.pos.x / self.level.level_end_x)

        self.renderer.draw(progress, self.player.speed_mult)
        self.effects.draw()
        self._hud.draw(self.score_manager, progress)

        if self.state == GameState.PAUSED:
            self._pause_menu.draw()

        elif self.state == GameState.GAME_OVER:
            self._over_menu.draw(
                self._run_score, self._best_score,
                self._run_completion,  self._best_completion,
                self._is_new_best,
            )

        elif self.state == GameState.LEVEL_COMPLETE:
            self._complete_menu.draw(
                self._run_score, self._best_score,
                self._run_completion,  self._best_completion,
                self._is_new_best,
            )

        if self._debug_mode:
            self._draw_debug_overlay(interpolation_factor, progress)

        end_drawing()

    def _draw_debug_overlay(self, interpolation_factor, progress):
        player = self.player
        lines = [
            f"FPS:        {get_fps()}",
            f"Pos:        ({player.pos.x:.1f}, {player.pos.y:.1f})",
            f"Vel:        ({player.vel.x:.1f}, {player.vel.y:.1f})",
            f"Speed mult: {player.speed_mult:.2f}",
            f"Progress:   {progress:.1%}",
            f"Score:      {self.score_manager.score}",
            f"Collected:  {self.score_manager.collected}/{self.score_manager.total}",
            f"Level end:  {self.level.level_end_x}",
            f"Scroll X:   {self.camera.scroll_x:.1f}",
            f"Trauma:     {self.camera.trauma:.2f}",
            f"Col checks: {self._collision_check_count}",
            f"Interp:     {interpolation_factor:.3f}",
            f"State:      {self.state.name}",
        ]
        draw_rectangle(8, 26, 120, 8+18*len(lines), Color(0, 0, 120))
        draw_rectangle_lines(8, 26, 120, 8+18*len(lines), WHITE)
        for i, line in enumerate(lines):
            draw_text(line, 8, 8 + i * 18, 16, GREEN)
