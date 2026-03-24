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
from rendering.renderer import Renderer
from rendering.camera import Camera
from rendering.parallax import ParallaxBackground
from rendering.particle_system import ParticleSystem
from rendering.effects import ScreenEffects
from rendering.hud import HUD
from rendering.trail_renderer import current_trail_color

_PICKUP_RADIUS = 8.0   # extra tolerance added to collectible.radius on pickup


class Game:
    def __init__(self):
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Geometry Snake")
        set_target_fps(FPS)

        self.input = InputManager()
        self._accumulator = 0.0
        self._debug = False
        self._collision_checks = 0
        self._hud = HUD()
        self.reset()

    def reset(self):
        self.state = GameState.PLAYING
        self._accumulator = 0.0
        self._collision_checks = 0

        self.level        = Level(DEFAULT_LEVEL)
        self.player       = Player()
        self.trail        = Trail()
        self.collectibles = build_collectibles(self.level.collectibles)

        self.score_manager = ScoreManager()
        self.score_manager.setup(len(self.collectibles))

        cam_cfg = self.level.camera_config
        self.camera = Camera(
            level_width=self.level.level_end_x,
            lookahead=cam_cfg.get("lookahead", CAMERA_LOOKAHEAD),
            lerp=cam_cfg.get("lerp", CAMERA_LERP),
        )
        self.parallax = ParallaxBackground(
            level_width=self.level.level_end_x,
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
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while not window_should_close():
            dt = get_frame_time()
            self._update_loop(dt)
            self._render()
        close_window()

    def _update_loop(self, dt):
        if is_key_pressed(KEY_D):
            self._debug = not self._debug

        if self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            if is_key_pressed(KEY_R):
                self.reset()
            return

        if self.state == GameState.PAUSED:
            if is_key_pressed(KEY_P):
                self._accumulator = 0.0
                self.state = GameState.PLAYING
            return

        if self.state == GameState.PLAYING:
            if is_key_pressed(KEY_P):
                self.state = GameState.PAUSED
                return

        self._accumulator += dt
        if self._accumulator > MAX_ACCUMULATOR:
            self._accumulator = MAX_ACCUMULATOR

        holding = self.input.is_holding()
        while self._accumulator >= FIXED_DT:
            self._fixed_update(holding, FIXED_DT)
            self._accumulator -= FIXED_DT

    # ------------------------------------------------------------------
    # Physics tick
    # ------------------------------------------------------------------

    def _fixed_update(self, holding, dt):
        """Physics/model step — no draw calls here."""
        self.player.speed_mult = self.level.speed_multiplier_at(self.player.pos.x)
        self.player.apply_control(holding)
        self.player.update(dt)
        self.trail.update(self.player.pos)
        self.camera.update(self.player.pos, dt)
        self.particles.update(dt)
        self.effects.update(dt)

        if self.player.pos.x >= self.level.level_end_x:
            self.state = GameState.LEVEL_COMPLETE
            return

        self._check_collectibles()

        self._collision_checks += 1
        if self.collision.check_all():
            self.state = GameState.GAME_OVER
            self.camera.add_trauma(SHAKE_DEATH_TRAUMA)
            progress = min(1.0, self.player.pos.x / self.level.level_end_x)
            self.particles.emit_burst(
                self.player.pos.x, self.player.pos.y,
                PARTICLE_DEATH_COUNT,
                PARTICLE_DEATH_SPEED,
                current_trail_color(progress),
            )

    def _check_collectibles(self):
        px, py = self.player.pos.x, self.player.pos.y
        for col in self.collectibles:
            if col.collected:
                continue
            dx = px - col.x
            dy = py - col.y
            if (dx * dx + dy * dy) ** 0.5 < col.radius + _PICKUP_RADIUS:
                col.collected = True
                self.score_manager.collect(col.value)
                self.particles.emit_burst(
                    col.x, col.y, 15, 120, col.color,
                )

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def _render(self):
        interp   = self._accumulator / FIXED_DT
        progress = min(1.0, self.player.pos.x / self.level.level_end_x)

        begin_drawing()

        self.renderer.draw(progress, self.player.speed_mult)
        self.effects.draw()
        self._hud.draw(self.score_manager)

        if self.state == GameState.PAUSED:
            draw_text("PAUSED - Press P to Resume", 220, 280, 20, YELLOW)

        if self.state == GameState.GAME_OVER:
            draw_text("GAME OVER - Press R to Restart", 180, 280, 20, RED)

        if self.state == GameState.LEVEL_COMPLETE:
            draw_text("LEVEL COMPLETE! - Press R to Play Again", 130, 280, 20, GREEN)

        if self._debug:
            self._draw_debug_overlay(interp, progress)

        end_drawing()

    def _draw_debug_overlay(self, interp, progress):
        p = self.player
        lines = [
            f"FPS:        {get_fps()}",
            f"Pos:        ({p.pos.x:.1f}, {p.pos.y:.1f})",
            f"Vel:        ({p.vel.x:.1f}, {p.vel.y:.1f})",
            f"Speed mult: {p.speed_mult:.2f}",
            f"Progress:   {progress:.1%}",
            f"Score:      {self.score_manager.score}",
            f"Collected:  {self.score_manager.collected}/{self.score_manager.total}",
            f"Level end:  {self.level.level_end_x}",
            f"Scroll X:   {self.camera.scroll_x:.1f}",
            f"Trauma:     {self.camera.trauma:.2f}",
            f"Col checks: {self._collision_checks}",
            f"Interp:     {interp:.3f}",
            f"State:      {self.state.name}",
        ]
        for i, line in enumerate(lines):
            draw_text(line, 8, 8 + i * 18, 16, GREEN)
