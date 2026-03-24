from config.settings import *
from utils.geometry import segment_intersect_rect, segment_segment_distance


class CollisionManager:
    def __init__(self, player, trail, obstacles):
        self.player = player
        self.trail = trail
        self.obstacles = obstacles

    def check_all(self):
        return (
            self.check_wall_collision()
            or self.check_obstacle_collision()
            or self.check_self_collision()
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

    def check_self_collision(self):
        """Check whether the head sweep segment comes within COLLISION_RADIUS
        of any trail segment, skipping SELF_COLLISION_SKIP newest points.

        Uses segment-segment distance so fast movement can't tunnel through
        nearby trail curves.
        """
        points = list(self.trail.points)
        if len(points) < SELF_COLLISION_SKIP + 2:
            return False

        head_p = (self.player.prev_pos.x, self.player.prev_pos.y)
        head_q = (self.player.pos.x, self.player.pos.y)
        threshold = COLLISION_RADIUS - COLLISION_MARGIN

        skipped = points[SELF_COLLISION_SKIP:]
        for i in range(len(skipped) - 1):
            a = (skipped[i].x, skipped[i].y)
            b = (skipped[i + 1].x, skipped[i + 1].y)

            if segment_segment_distance(head_p, head_q, a, b) < threshold:
                return True

        return False
