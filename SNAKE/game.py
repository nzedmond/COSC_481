import json
import logging
import os
from raylib import *
from pyray import *
from settings import *
from snake import Snake
from food import Food
from ui import UI
from powerups import PowerupManager, Shield
from obstacles import ObstacleManager
from audio import AudioManager


os.makedirs("data", exist_ok=True)
logging.basicConfig(
    filename="data/snake.log",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger(__name__)


def load_high_score(path="data/highscore.json"):
    try:
        with open(path) as f:
            return json.load(f).get("high_score", 0)
    except FileNotFoundError:
        return 0


def save_high_score(score, path="data/highscore.json"):
    with open(path, "w") as f:
        json.dump({"high_score": score}, f)


class ScreenManager:
    def __init__(self):
        self.current = Screen.MENU

    def transition_to(self, screen: Screen):
        self.current = screen

    def is_on(self, screen: Screen) -> bool:
        return self.current == screen


class Game:
    def __init__(self):
        self.screens       = ScreenManager()
        self.snake         = Snake()
        self.food          = Food()
        self.ui            = UI()
        self.powerup_mgr   = PowerupManager()
        self.obstacle_mgr  = ObstacleManager()
        self.score         = 0
        self.high_score    = load_high_score()
        self.mode               = Mode.CLASSIC
        self.selected_mode      = 0       # index into _MODES list
        self.time_left          = 0       # frames remaining (Time Attack only)
        self._food_pops         = []      # active eat animations: [Vector2, Color, timer]
        self.score_pop_timer    = 0       # frames remaining for score text pop
        self.debug              = False
        self.god_mode           = False
        self.audio_mgr          = AudioManager()

    def update(self):
        self.audio_mgr.update(self.screens.current, self.mode)
        match self.screens.current:
            case Screen.MENU:         self._update_menu()
            case Screen.GAMEPLAY:     self._update_gameplay()
            case Screen.PAUSED:       self._update_paused()
            case Screen.GAME_OVER:    self._update_game_over()
            case Screen.INSTRUCTIONS: self._update_instructions()

    _MODES = [Mode.CLASSIC, Mode.TIME_ATTACK, Mode.SURVIVAL]

    def _update_menu(self):
        if is_key_pressed(KEY_DOWN):
            self.selected_mode = (self.selected_mode + 1) % len(self._MODES)
        if is_key_pressed(KEY_UP):
            self.selected_mode = (self.selected_mode - 1) % len(self._MODES)
        if is_key_pressed(KEY_ENTER):
            self.mode = self._MODES[self.selected_mode]
            self._start_game()
        if is_key_pressed(KEY_I):
            self.screens.transition_to(Screen.INSTRUCTIONS)

    def _update_instructions(self):
        if is_key_pressed(KEY_BACKSPACE) or is_key_pressed(KEY_I):
            self.screens.transition_to(Screen.MENU)

    def _update_gameplay(self):
        if is_key_pressed(KEY_D):
            self.debug = not self.debug
        if is_key_pressed(KEY_P):
            self.screens.transition_to(Screen.PAUSED)
            return

        if self.debug:
            if is_key_pressed(KEY_G):
                self.god_mode = not self.god_mode
                log.info(f"God mode {'ON' if self.god_mode else 'OFF'}")
            if is_key_pressed(KEY_F):
                snake = self.snake
                snake.body.append(Vector2(snake.body[-1].x, snake.body[-1].y))
                snake.length += 1
                self.score += 1
                occupied = list(snake.body) + self.obstacle_mgr.positions
                self.food._init_type()
                self.food.position = self.food._spawn_position(occupied)
                log.info(f"Debug: force-ate food, score={self.score}")
            if is_key_pressed(KEY_N):
                self.powerup_mgr.spawn_timer = POWERUP_SPAWN_INTERVAL
                log.info("Debug: forced powerup spawn")

        # Time Attack: count down every frame (not just on snake moves)
        if self.mode == Mode.TIME_ATTACK:
            self.time_left -= 1
            if self.time_left <= 0:
                self._trigger_game_over()
                return

        # Survival: override speed based on current score
        if self.mode == Mode.SURVIVAL:
            self.snake.move_interval = max(
                1, SNAKE_MOVE_INTERVAL - self.score // SURVIVAL_SPEED_INTERVAL
            )

        self.snake.handle_input()
        moved = self.snake.update()

        # Tick pop animations every frame regardless of snake movement
        for pop in self._food_pops:
            pop[2] += 1
        self._food_pops = [p for p in self._food_pops if p[2] < FOOD_POP_DURATION]
        if self.score_pop_timer > 0:
            self.score_pop_timer -= 1

        if not moved:
            return  # Skip collision checks if the snake didn't move this frame

        self.check_wall_collision()
        self.check_self_collision()
        self.check_obstacle_collision()

        if self.screens.is_on(Screen.GAME_OVER):
            return

        obs_positions = self.obstacle_mgr.positions
        self.powerup_mgr.update(self.snake, self.food, obs_positions)

        eaten_pos   = Vector2(self.food.position.x, self.food.position.y)
        eaten_color = self.food.color
        eaten_type  = self.food.food_type
        score_delta = self.food.update(self.snake, obs_positions)
        if score_delta != 0:
            self.audio_mgr.play_hit(eaten_type)
            self._food_pops.append([eaten_pos, eaten_color, 0])
            self.score_pop_timer = SCORE_POP_DURATION
            self.score = max(0, self.score + score_delta)
            log.info(f"Food eaten ({eaten_type.name}) — delta: {score_delta}, score: {self.score}")

        self.obstacle_mgr.update(self.score, self.snake, self.food)

    def _update_paused(self):
        if is_key_pressed(KEY_D):
            self.debug = not self.debug
        if is_key_pressed(KEY_P):
            self.screens.transition_to(Screen.GAMEPLAY)

    def _update_game_over(self):
        if is_key_pressed(KEY_ENTER):
            self.reset()
        if is_key_pressed(KEY_M):
            self.reset()
            self.screens.transition_to(Screen.MENU)

    def check_wall_collision(self):
        head = self.snake.body[0]
        if (
            head.x + SNAKE_SIZE >= WINDOW_WIDTH
            or head.y + SNAKE_SIZE >= WINDOW_HEIGHT
            or head.x < 0
            or head.y < HEADER_HEIGHT
        ):
            self._trigger_game_over()

    def check_obstacle_collision(self):
        if self.obstacle_mgr.check_collision(self.snake):
            self._trigger_game_over()

    def check_self_collision(self):
        head = self.snake.body[0]
        for segment in self.snake.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                self._trigger_game_over()
                break

    def _trigger_game_over(self):
        if self.god_mode:
            return
        if self.snake.shielded:
            self.snake.shielded = False
            self.snake.active_powerups = [
                p for p in self.snake.active_powerups if not isinstance(p, Shield)
            ]
            log.info("Shield absorbed a collision")
            return
        log.info(f"Game over — score: {self.score}, best: {self.high_score}")
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
            log.info(f"New high score: {self.high_score}")
        self.screens.transition_to(Screen.GAME_OVER)

    def draw(self):
        match self.screens.current:
            case Screen.MENU:         self._draw_menu()
            case Screen.GAMEPLAY:     self._draw_gameplay()
            case Screen.PAUSED:       self._draw_paused()
            case Screen.GAME_OVER:    self._draw_game_over()
            case Screen.INSTRUCTIONS: self._draw_instructions()

    def _draw_menu(self):
        self.ui.draw_menu(self.selected_mode)

    def _draw_instructions(self):
        self.ui.draw_instructions()

    def _draw_gameplay(self):
        self.ui.draw_header(self.score, self.high_score, self.mode, self.time_left, self.score_pop_timer)
        self.ui.draw_grid()
        self.obstacle_mgr.draw()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        self.ui.draw_food_pops(self._food_pops)
        self.powerup_mgr.draw()
        self.ui.draw_active_powerups(self.snake.active_powerups)
        if self.debug:
            self.ui.draw_debug_overlay(self)

    def _draw_paused(self):
        self.ui.draw_header(self.score, self.high_score, self.mode, self.time_left, self.score_pop_timer)
        self.ui.draw_grid()
        self.obstacle_mgr.draw()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        self.ui.draw_food_pops(self._food_pops)
        self.powerup_mgr.draw()
        self.ui.draw_active_powerups(self.snake.active_powerups)
        draw_text("GAME PAUSED!", WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2, 50, BLACK)
        if self.debug:
            self.ui.draw_debug_overlay(self)

    def _draw_game_over(self):
        self.ui.draw_header(self.score, self.high_score, self.mode, self.time_left)
        self.ui.draw_grid()
        self.obstacle_mgr.draw()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        self.ui.draw_food_pops(self._food_pops)
        self.powerup_mgr.draw()
        self.ui.draw_game_over(self.score, self.high_score)

    def startup(self):
        self.audio_mgr.load()

    def _start_game(self):
        """Set up a fresh round for the current mode and transition to gameplay."""
        self.snake              = Snake()
        self.food               = Food()
        self.score              = 0
        self._food_pops         = []
        self.score_pop_timer    = 0

        match self.mode:
            case Mode.CLASSIC:
                self.powerup_mgr.reset()
                self.obstacle_mgr.reset()
                self.time_left = 0

            case Mode.TIME_ATTACK:
                self.powerup_mgr.reset()
                self.obstacle_mgr.reset()
                self.time_left = TIME_ATTACK_DURATION

            case Mode.SURVIVAL:
                self.powerup_mgr.reset()
                self.obstacle_mgr.reset(spawn_every=2)   # obstacles spawn faster
                self.time_left = 0

        self.screens.transition_to(Screen.GAMEPLAY)
        log.info(f"Game started — mode: {self.mode.name}")

    def reset(self):
        """Restart the current mode (called from game-over screen)."""
        self._start_game()

    def shutdown(self):
        self.audio_mgr.unload()

