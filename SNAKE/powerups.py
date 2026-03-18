class Powerup:
    """Base class for all power-ups (Phase 1)."""

    def __init__(self, kind, duration):
        self.kind = kind
        self.duration = duration
        self.timer = 0.0

    def apply(self, snake):
        pass

    def remove(self, snake):
        pass

    def update(self, dt, snake):
        """Advance timer. Returns True when the power-up expires."""
        self.timer += dt
        if self.timer >= self.duration:
            self.remove(snake)
            return True
        return False
