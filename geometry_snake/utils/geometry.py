"""
Geometry utilities for sweep-based collision detection.

All functions operate on plain (x, y) tuples — no pyray types — so they
can be unit-tested without a display context.
"""


def _cross2d(ax, ay, bx, by):
    return ax * by - ay * bx


def segment_intersect_segment(p1, p2, p3, p4):
    """Return True if segment p1->p2 intersects segment p3->p4."""
    rx, ry = p2[0] - p1[0], p2[1] - p1[1]
    sx, sy = p4[0] - p3[0], p4[1] - p3[1]

    rxs = _cross2d(rx, ry, sx, sy)
    qpx, qpy = p3[0] - p1[0], p3[1] - p1[1]

    if abs(rxs) < 1e-10:   # parallel or collinear — treat as no intersection
        return False

    t = _cross2d(qpx, qpy, sx, sy) / rxs
    u = _cross2d(qpx, qpy, rx, ry) / rxs

    return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0


def segment_intersect_rect(p1, p2, rx, ry, rw, rh):
    """Return True if segment p1->p2 intersects or is inside the AABB."""
    def _inside(p):
        return rx <= p[0] <= rx + rw and ry <= p[1] <= ry + rh

    if _inside(p1) or _inside(p2):
        return True

    # Test against all four edges of the rectangle
    tl, tr = (rx, ry), (rx + rw, ry)
    bl, br = (rx, ry + rh), (rx + rw, ry + rh)

    for edge in [(tl, tr), (tr, br), (br, bl), (bl, tl)]:
        if segment_intersect_segment(p1, p2, edge[0], edge[1]):
            return True

    return False


def point_to_segment_distance(p, a, b):
    """Minimum distance from point p to segment a->b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    len_sq = dx * dx + dy * dy

    if len_sq < 1e-10:   # degenerate segment — treat as a point
        return ((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2) ** 0.5

    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / len_sq))
    cx, cy = a[0] + t * dx, a[1] + t * dy
    return ((p[0] - cx) ** 2 + (p[1] - cy) ** 2) ** 0.5


def segment_segment_distance(p1, p2, p3, p4):
    """Minimum distance between segment p1->p2 and segment p3->p4."""
    if segment_intersect_segment(p1, p2, p3, p4):
        return 0.0

    return min(
        point_to_segment_distance(p1, p3, p4),
        point_to_segment_distance(p2, p3, p4),
        point_to_segment_distance(p3, p1, p2),
        point_to_segment_distance(p4, p1, p2),
    )
