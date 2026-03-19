import json
import logging
import os

from raylib import *
from pyray import *
from settings import *
from snake import Snake
from food import Food
from ui import UI


# ── Logging setup ──────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
logging.basicConfig(
    filename="data/snake.log",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger(__name__)


# ── High score persistence ─────────────────────────────────────────────────────
def load_high_score(path="data/highscore.json"):
    try:
        with open(path) as f:
            return json.load(f).get("high_score", 0)
    except FileNotFoundError:
        return 0


def save_high_score(score, path="data/highscore.json"):
    with open(path, "w") as f:
        json.dump({"high_score": score}, f)


# ── Screen manager ─────────────────────────────────────────────────────────────
class ScreenManager:
    def __init__(self):
        self.current = Screen.MENU

    def transition_to(self, screen: Screen):
        self.current = screen

    def is_on(self, screen: Screen) -> bool:
        return self.current == screen


# ── Game ───────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screens    = ScreenManager()
        self.snake      = Snake()
        self.food       = Food()
        self.ui         = UI()
        self.score      = 0
        self.high_score = load_high_score()

    def update(self):
        match self.screens.current:
            case Screen.MENU:      self._update_menu()
            case Screen.GAMEPLAY:  self._update_gameplay()
            case Screen.PAUSED:    self._update_paused()
            case Screen.GAME_OVER: self._update_game_over()

    def _update_menu(self):
        if is_key_pressed(KEY_ENTER):
            self.screens.transition_to(Screen.GAMEPLAY)

    def _update_gameplay(self):
        if is_key_pressed(KEY_P):
            self.screens.transition_to(Screen.PAUSED)
            return

        self.snake.handle_input()
        moved = self.snake.update()

        if not moved:
            return  # Skip collision checks if the snake didn't move this frame

        self.check_wall_collision()
        self.check_self_collision()

        if self.screens.is_on(Screen.GAME_OVER):
            return

        score_delta = self.food.update(self.snake)
        if score_delta != 0:
            self.score = max(0, self.score + score_delta)
            log.info(f"Food eaten ({self.food.food_type.name}) — delta: {score_delta}, score: {self.score}")

    def _update_paused(self):
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
            or head.x <= 0
            or head.y <= HEADER_HEIGHT
        ):
            self._trigger_game_over()

    def check_self_collision(self):
        head = self.snake.body[0]
        for segment in self.snake.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                self._trigger_game_over()
                break

    def _trigger_game_over(self):
        log.info(f"Game over — score: {self.score}, best: {self.high_score}")
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
            log.info(f"New high score: {self.high_score}")
        self.screens.transition_to(Screen.GAME_OVER)

    def draw(self):
        match self.screens.current:
            case Screen.MENU:      self._draw_menu()
            case Screen.GAMEPLAY:  self._draw_gameplay()
            case Screen.PAUSED:    self._draw_paused()
            case Screen.GAME_OVER: self._draw_game_over()

    def _draw_menu(self):
        self.ui.draw_menu()

    def _draw_gameplay(self):
        self.ui.draw_header(self.score, self.high_score)
        self.ui.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()

    def _draw_paused(self):
        self.ui.draw_header(self.score, self.high_score)
        self.ui.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        draw_text("GAME PAUSED!", WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2, 50, BLACK)

    def _draw_game_over(self):
        self.ui.draw_header(self.score, self.high_score)
        self.ui.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        self.ui.draw_game_over(self.score, self.high_score)

    def startup(self):
        pass

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.screens.transition_to(Screen.GAMEPLAY)

    def shutdown(self):
        pass

