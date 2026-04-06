import random

from raylib import *
from pyray import *
from settings import *


class Obstacle:
    def __init__(self, position):
        self.position = position
        self.size     = OBSTACLE_SIZE

    def draw(self):
        draw_rectangle(int(self.position.x), int(self.position.y),
                       self.size, self.size, OBSTACLE_COLOR)
        draw_rectangle_lines(int(self.position.x), int(self.position.y),
                             self.size, self.size, BLACK)

class ObstacleManager:
    def __init__(self, spawn_every=OBSTACLE_SPAWN_EVERY, dynamic=True):
        self._spawn_every = spawn_every
        self._dynamic = dynamic
        self.obstacles = []
        self._last_score = 0

    def reset(self, spawn_every=OBSTACLE_SPAWN_EVERY, dynamic=True):
        self._spawn_every = spawn_every
        self._dynamic = dynamic
        self.obstacles = []
        self._last_score = 0

    @property
    def positions(self):
        """Vector2 list for spawn-exclusion checks in food and powerup code."""
        return [obs.position for obs in self.obstacles]

    def update(self, score, snake, food):
        if not self._dynamic:
            return
        while (score - self._last_score >= self._spawn_every
               and len(self.obstacles) < OBSTACLE_MAX):
            self._last_score += self._spawn_every
            self._spawn(snake, food)

    def check_collision(self, snake):
        head = snake.body[0]
        return any(head.x == obs.position.x and head.y == obs.position.y
                   for obs in self.obstacles)

    def draw(self):
        for obs in self.obstacles:
            obs.draw()

    def _spawn(self, snake, food):
        occupied = {(s.x, s.y) for s in snake.body}
        occupied.add((food.position.x, food.position.y))
        for obs in self.obstacles:
            occupied.add((obs.position.x, obs.position.y))

        for _ in range(200):
            candidate = Vector2(
                random.randint(0, (WINDOW_WIDTH - OBSTACLE_SIZE) // OBSTACLE_SIZE) * OBSTACLE_SIZE,
                random.randint(HEADER_HEIGHT // OBSTACLE_SIZE,
                               (WINDOW_HEIGHT - OBSTACLE_SIZE) // OBSTACLE_SIZE) * OBSTACLE_SIZE,
            )
            if (candidate.x, candidate.y) not in occupied:
                self.obstacles.append(Obstacle(candidate))
                return
