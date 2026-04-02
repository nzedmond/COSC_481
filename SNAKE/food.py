import random

from raylib import *
from pyray import *
from settings import *


class Food:
    def __init__(self):
        self.size = FOOD_SIZE
        self.isActive = True
        self._init_type()
        self.position = self._spawn_position([])

    def _init_type(self):
        food_chance = random.random()
        if food_chance < FOOD_GOLDEN_CHANCE:
            self.food_type = FoodType.GOLDEN
        elif food_chance < FOOD_GOLDEN_CHANCE + FOOD_POISON_CHANCE:
            self.food_type = FoodType.POISON
        elif FOOD_POISON_CHANCE < FOOD_GOLDEN_CHANCE + FOOD_POISON_CHANCE + FOOD_MOVING_CHANCE:
            self.food_type = FoodType.MOVING
        else:
            self.food_type = FoodType.NORMAL

        match self.food_type:
            case FoodType.NORMAL: 
                self.color = FOOD_NORMAL_COLOR
                self.score_value = FOOD_NORMAL_SCORE
            case FoodType.GOLDEN: 
                self.color = FOOD_GOLDEN_COLOR
                self.score_value = FOOD_GOLDEN_SCORE
            case FoodType.POISON: 
                self.color = FOOD_POISON_COLOR
                self.score_value = FOOD_POISON_SCORE
            case FoodType.MOVING: 
                self.color = FOOD_MOVING_COLOR
                self.score_value = FOOD_MOVING_SCORE

        if self.food_type == FoodType.MOVING: 
            self.velocity = Vector2(
                random.choice([-1, 1]) * FOOD_MOVING_SPEED,
                random.choice([-1, 1]) * FOOD_MOVING_SPEED,
            )
        else:
            self.velocity = Vector2(0, 0)

        # Poison food counts up; 0 means no lifespan limit
        self.life_timer = 0 if self.food_type == FoodType.POISON else -1

    def _spawn_position(self, occupied):
        occupied_set = {(s.x, s.y) for s in occupied}
        while True:
            candidate = Vector2(
                random.randint(0, (WINDOW_WIDTH - self.size) // self.size) * self.size,
                random.randint(HEADER_HEIGHT // self.size, (WINDOW_HEIGHT - self.size) // self.size) * self.size,
            )
            if (candidate.x, candidate.y) not in occupied_set:
                return candidate

    def _move(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        
        if self.position.x < 0 or self.position.x + self.size > WINDOW_WIDTH: 
            self.velocity.x *= -1
            self.position.x = max(0.0, min(self.position.x, float(WINDOW_WIDTH - self.size)))
        if self.position.y < HEADER_HEIGHT or self.position.y + self.size > WINDOW_HEIGHT:
            self.velocity.y *= -1
            self.position.y = max(float(HEADER_HEIGHT), min(self.position.y, float(WINDOW_HEIGHT - self.size)))

    def draw(self):
        draw_rectangle(int(self.position.x), int(self.position.y), self.size, self.size, self.color)
        # Small label for non-normal types so the player can read the field at a glance
        match self.food_type:
            case FoodType.GOLDEN: draw_text("G", int(self.position.x) + 5, int(self.position.y) + 3, 12, BLACK)
            case FoodType.POISON: draw_text("!", int(self.position.x) + 7, int(self.position.y) + 3, 12, WHITE)
            case FoodType.MOVING: draw_text("~", int(self.position.x) + 4, int(self.position.y) + 3, 12, WHITE)
            case _: pass

        # Lifespan timer bar drawn above poison food (full = white, empty = gone)
        if self.life_timer >= 0:
            ratio = max(0.0, 1.0 - self.life_timer / FOOD_POISON_LIFESPAN)
            bar_w = int(self.size * ratio)
            draw_rectangle(int(self.position.x), int(self.position.y) - 4, self.size, 3, DARKGRAY)
            draw_rectangle(int(self.position.x), int(self.position.y) - 4, bar_w, 3, WHITE)

    def update(self, snake, extra_occupied=None):
        """Move food (if moving type) and check collision. Returns score delta.

        extra_occupied: optional list of Vector2 positions (obstacle tiles)
        that the new food must not spawn on.
        """
        if not self.isActive:
            return 0

        if self.food_type == FoodType.MOVING:
            self._move()

        # Poison lifespan: expire and replace with a new type when timer runs out
        if self.life_timer >= 0:
            self.life_timer += 1
            if self.life_timer >= FOOD_POISON_LIFESPAN:
                self._init_type()
                occupied = list(snake.body) + (extra_occupied or [])
                self.position = self._spawn_position(occupied)
                return 0

        # Box collision with snake head
        head = snake.body[0]
        if not (head.x < self.position.x + self.size and
                head.x + snake.size > self.position.x and
                head.y < self.position.y + self.size and
                head.y + snake.size > self.position.y):
            return 0

        score_delta = self.score_value

        if self.food_type == FoodType.POISON:
            if snake.length > 1:
                snake.body.pop()
                snake.length -= 1
        else:
            snake.body.append(Vector2(snake.body[-1].x, snake.body[-1].y))
            snake.length += 1

        # Spawn a new food of a random type, avoiding obstacles
        self.isActive = False
        self._init_type()
        occupied = list(snake.body) + (extra_occupied or [])
        self.position = self._spawn_position(occupied)
        self.isActive = True

        return score_delta
