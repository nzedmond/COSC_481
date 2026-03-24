from pyray import *
from config.settings import *
from core.input_manager import InputManager
from core.state import GameState
from entities.player import Player
from entities.trail import Trail
from entities.obstacle import Obstacle
from systems.collision_manager import CollisionManager
from rendering.renderer import Renderer


class Game:
    def __init__(self):
        init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Geometry Snake")
        set_target_fps(FPS)

        self.input = InputManager()
        self._accumulator = 0.0
        self._debug = False
        self._collision_checks = 0
        self.reset()

    def reset(self):
        self.state = GameState.PLAYING
        self._accumulator = 0.0
        self._collision_checks = 0
        self.player = Player()
        self.trail = Trail()

        self.obstacles = [
            Obstacle(400, 200, 40, 200),
            Obstacle(650, 0, 40, 300),
            Obstacle(900, 300, 40, 300),
        ]
        self.collision = CollisionManager(self.player, self.trail, self.obstacles)
        self.renderer = Renderer(self.player, self.trail, self.obstacles)

    def run(self):
        while not window_should_close():
            dt = get_frame_time()
            self._update_loop(dt)
            self._render()
        close_window()

    def _update_loop(self, dt):
        if is_key_pressed(KEY_D):
            self._debug = not self._debug

        if self.state == GameState.GAME_OVER:
            if is_key_pressed(KEY_R):
                self.reset()
            return

        if self.state == GameState.PAUSED:
            if is_key_pressed(KEY_P):
                self._accumulator = 0.0  # discard elapsed time so no phantom ticks on resume
                self.state = GameState.PLAYING
            return

        if self.state == GameState.PLAYING:
            if is_key_pressed(KEY_P):
                self.state = GameState.PAUSED
                return

        # Clamp accumulator to avoid spiral of death on slow machines
        self._accumulator += dt
        if self._accumulator > MAX_ACCUMULATOR:
            self._accumulator = MAX_ACCUMULATOR

        holding = self.input.is_holding()
        while self._accumulator >= FIXED_DT:
            self._fixed_update(holding, FIXED_DT)
            self._accumulator -= FIXED_DT

    def _fixed_update(self, holding, dt):
        """Physics/model step — no draw calls here."""
        self.player.apply_control(holding)
        self.player.update(dt)
        self.trail.update(self.player.pos)

        self._collision_checks += 1
        if self.collision.check_all():
            self.state = GameState.GAME_OVER

    def _render(self):
        """View step — interpolation alpha available for smooth visuals."""
        interp = self._accumulator / FIXED_DT

        begin_drawing()
        clear_background(BLACK)

        self.renderer.draw()

        if self.state == GameState.PAUSED:
            draw_text("PAUSED - Press P to Resume", 220, 280, 20, YELLOW)

        if self.state == GameState.GAME_OVER:
            draw_text("GAME OVER - Press R to Restart", 180, 280, 20, RED)

        if self._debug:
            self._draw_debug_overlay(interp)

        end_drawing()

    def _draw_debug_overlay(self, interp):
        p = self.player
        lines = [
            f"FPS: {get_fps()}",
            f"Pos:   ({p.pos.x:.1f}, {p.pos.y:.1f})",
            f"Vel:   ({p.vel.x:.1f}, {p.vel.y:.1f})",
            f"Collision checks: {self._collision_checks}",
            f"Interp alpha: {interp:.3f}",
            f"State: {self.state.name}",
        ]
        for i, line in enumerate(lines):
            draw_text(line, 8, 8 + i * 18, 16, GREEN)
