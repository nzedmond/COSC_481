from raylib import *
from food import Food
from snake import Snake
from pyray import *
from settings import *


class ScreenManager:
    def __init__(self):
        self.current = Screen.MENU

    def transition_to(self, screen: Screen):
        self.current = screen

    def is_on(self, screen: Screen) -> bool:
        return self.current == screen


class Game:
    def __init__(self):
        self.screens = ScreenManager()
        self.snake = Snake()
        self.food = Food()
        self.cell_size = SNAKE_SIZE
        self.offset_x = WINDOW_WIDTH % self.cell_size
        self.offset_y = WINDOW_HEIGHT % self.cell_size

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

        self.food.update(self.snake)

    def _update_paused(self):
        if is_key_pressed(KEY_P):
            self.screens.transition_to(Screen.GAMEPLAY)

    def _update_game_over(self):
        if is_key_pressed(KEY_ENTER):
            self.reset()

    def check_wall_collision(self):
        head = self.snake.body[0]

        # Currently debugging this section -----||||||||||--------

        if (
            head.x + self.cell_size >= WINDOW_WIDTH
            or head.y + self.cell_size >= WINDOW_HEIGHT
            or head.x < 0
            or head.y < 0
        ):
            self.screens.transition_to(Screen.GAME_OVER)

    def check_self_collision(self):
        head = self.snake.body[0]

        for segment in self.snake.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                self.screens.transition_to(Screen.GAME_OVER)
                break

    def draw(self):
        match self.screens.current:
            case Screen.MENU:      self._draw_menu()
            case Screen.GAMEPLAY:  self._draw_gameplay()
            case Screen.PAUSED:    self._draw_paused()
            case Screen.GAME_OVER: self._draw_game_over()

    def _draw_menu(self):
        draw_text("SNAKE", WINDOW_WIDTH // 3, WINDOW_HEIGHT // 3, 60, DARKGREEN)
        draw_text("Press ENTER to start", WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2, 24, BLACK)

    def _draw_gameplay(self):
        self.draw_instructions()
        self.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()

    def _draw_paused(self):
        self.draw_instructions()
        self.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        draw_text("GAME PAUSED!", WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2, 50, BLACK)

    def _draw_game_over(self):
        self.draw_instructions()
        self.draw_grid()
        self.snake.draw()
        if self.food.isActive:
            self.food.draw()
        draw_text("GAME OVER!", WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2, 50, DARKBROWN)
        draw_text("Press ENTER to restart", WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2 + 60, 24, BLACK)

    def draw_grid(self):
        for i in range(WINDOW_WIDTH // self.cell_size + 1):
            x = int(self.cell_size * i + self.offset_x / 2)
            draw_line(
                x,
                int(self.offset_y / 2),
                x,
                int(WINDOW_HEIGHT - self.offset_y / 2),
                LIGHTGRAY,
            )

        for i in range(WINDOW_HEIGHT // self.cell_size + 1):
            y = int(self.cell_size * i + self.offset_y / 2)
            draw_line(
                int(self.offset_x / 2),
                y,
                int(WINDOW_WIDTH - self.offset_x / 2),
                y,
                LIGHTGRAY,
            )

    def draw_instructions(self):
        draw_text("Movement: ARROW KEYS", 20, 10, 10, RAYWHITE)

    def startup(self):
        pass

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.screens.transition_to(Screen.GAMEPLAY)

    def shutdown(self):
        pass
