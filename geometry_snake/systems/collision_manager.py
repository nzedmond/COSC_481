from config.settings import *
from utils.geometry import segment_intersect_rect


class CollisionManager:
    def __init__(self, player, trail, obstacles):
        self.player = player
        self.trail = trail
        self.obstacles = obstacles

    def check_all(self):
        return (
            self.check_wall_collision()
            or self.check_obstacle_collision()
        )

    def check_wall_collision(self):
        return (
            self.player.pos.y < 0 or
            self.player.pos.y > SCREEN_HEIGHT
        )

    def check_obstacle_collision(self):
        """Sweep the head segment p->q against each obstacle.

        AABB broad-phase first: skip any obstacle whose x-range doesn't
        overlap head.x +/- LOOKAHEAD, then do the exact segment-rect test.
        """
        p = (self.player.prev_pos.x, self.player.prev_pos.y)
        q = (self.player.pos.x, self.player.pos.y)
        head_x = self.player.pos.x

        for obs in self.obstacles:
            # Broad-phase: skip obstacles far from the head
            if head_x + LOOKAHEAD < obs.x or head_x - LOOKAHEAD > obs.x + obs.w:
                continue

            if segment_intersect_rect(p, q, obs.x, obs.y, obs.w, obs.h):
                return True

        return False

