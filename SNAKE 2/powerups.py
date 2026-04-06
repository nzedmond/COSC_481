import random

from raylib import *
from pyray import *
from settings import *


class Powerup:
    """Base class for all timed power-up effects applied to the snake."""
    COLOR = WHITE
    LABEL = "?"

    def __init__(self, kind, duration):
        self.kind = kind
        self.duration = duration
        self.timer = 0
        self.color = self.__class__.COLOR
        self.label = self.__class__.LABEL

    def apply(self, snake):  pass
    def remove(self, snake): pass

    def update(self, snake):
        """Advance timer by one frame. Returns True when the effect expires."""
        self.timer += 1
        if self.timer >= self.duration:
            self.remove(snake)
            return True
        return False

    @property
    def ratio(self):
        """Remaining life as 0.0–1.0 (1 = just picked up, 0 = expired)."""
        return max(0.0, 1.0 - self.timer / self.duration)


class Shield(Powerup):
    """Absorbs the next lethal collision instead of ending the game."""
    COLOR = YELLOW
    LABEL = "H"

    def __init__(self):
        super().__init__(PowerupType.SHIELD, POWERUP_SHIELD_DURATION)

    def apply(self, snake):
        snake.shielded = True

    def remove(self, snake):
        snake.shielded = False


class Shrink(Powerup):
    """Instantly removes tail segments — useful for tight situations."""
    COLOR = LIME
    LABEL = "Z"

    def __init__(self):
        super().__init__(PowerupType.SHRINK, POWERUP_SHRINK_DURATION)

    def apply(self, snake):
        for _ in range(POWERUP_SHRINK_SEGMENTS):
            if snake.length > 1:
                snake.body.pop()
                snake.length -= 1

    def remove(self, snake): pass


_POWERUP_CLASSES = {
    PowerupType.SHIELD:  Shield,
    PowerupType.SHRINK:  Shrink,
}


class PowerupPickup:
    def __init__(self, occupied):
        self.size = POWERUP_SIZE
        self.kind = random.choice(list(PowerupType))
        cls = _POWERUP_CLASSES[self.kind]
        self.color = cls.COLOR
        self.label = cls.LABEL
        self.position = self._spawn(occupied)

    def _spawn(self, occupied):
        occupied_set = {(s.x, s.y) for s in occupied}
        while True:
            candidate = Vector2(
                random.randint(0, (WINDOW_WIDTH - self.size) // self.size) * self.size,
                random.randint(HEADER_HEIGHT // self.size, (WINDOW_HEIGHT - self.size) // self.size) * self.size,
            )
            if (candidate.x, candidate.y) not in occupied_set:
                return candidate

    def draw(self):
        # White border distinguishes pickups from food at a glance
        draw_rectangle(int(self.position.x) - 2, int(self.position.y) - 2,
                       self.size + 4, self.size + 4, WHITE)
        draw_rectangle(int(self.position.x), int(self.position.y),
                       self.size, self.size, self.color)
        draw_text(self.label, int(self.position.x) + 5, int(self.position.y) + 3, 12, BLACK)

    def is_collected(self, snake):
        head = snake.body[0]
        return (head.x < self.position.x + self.size and
                head.x + snake.size > self.position.x and
                head.y < self.position.y + self.size and
                head.y + snake.size > self.position.y)

class PowerupManager:
    def __init__(self):
        self.pickup = None   # one pickup on the field at a time
        self.spawn_timer = 0

    def reset(self):
        self.pickup = None
        self.spawn_timer = 0

    def update(self, snake, food, extra_occupied=None):
        self.spawn_timer += 1
        if self.pickup is None and self.spawn_timer >= POWERUP_SPAWN_INTERVAL:
            self.spawn_timer = 0
            occupied = list(snake.body) + [food.position] + (extra_occupied or [])
            self.pickup = PowerupPickup(occupied)

        if self.pickup is not None and self.pickup.is_collected(snake):
            effect = _POWERUP_CLASSES[self.pickup.kind]()
            effect.apply(snake)
            if effect.duration > 1:          # instant effects (Shrink) need no tracking
                snake.active_powerups.append(effect)
            self.pickup = None
            self.spawn_timer = 0             # brief pause before next spawn

        snake.active_powerups = [p for p in snake.active_powerups if not p.update(snake)]

    def draw(self):
        if self.pickup is not None:
            self.pickup.draw()
