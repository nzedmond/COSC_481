"""
Smooth quad-strip trail with two-pass rendering:
  Pass 1 — glow:  wider, semi-transparent, only the head region
  Pass 2 — core:  tapered quad mesh, color interpolated by level progress

Quad winding (raylib expects CCW in screen-space, y-axis pointing down):
  Given a segment a→b with perpendicular normal n, the four quad corners are:
    p1 = a + n*hw,  p2 = a - n*hw
    p3 = b + n*hw,  p4 = b - n*hw
  Triangles drawn as:  (p2, p1, p4)  and  (p1, p3, p4)  — both CCW verified.
"""

from pyray import *
from config.settings import *

# Trail colour palette: cyan at level start → magenta at level end
_C_HEAD  = (0,   220, 255)   # bright cyan
_C_TAIL  = (255,  60, 200)   # hot magenta
_C_WHITE = (255, 255, 255)


def _lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _trail_color(progress):
    """Current trail colour based on how far through the level the player is."""
    return _lerp_color(_C_HEAD, _C_TAIL, progress)


def _draw_quad(p1, p2, p3, p4, color):
    """Draw a quad as two CCW triangles (screen-space winding)."""
    draw_triangle(p2, p1, p4, color)
    draw_triangle(p1, p3, p4, color)


class TrailRenderer:
    def draw(self, points, progress, speed_mult):
        pts = list(points)
        n   = len(pts)
        if n < 2:
            return

        rgb      = _trail_color(progress)
        base_hw  = TRAIL_CORE_RADIUS + speed_mult * 1.5   # widens with speed

        # ------------------------------------------------------------------
        # Pass 1 — glow (drawn behind core so it bleeds outward)
        # ------------------------------------------------------------------
        glow_end = min(n - 1, TRAIL_GLOW_LENGTH)
        for i in range(glow_end):
            taper = 1.0 - i / glow_end
            hw    = base_hw * TRAIL_GLOW_MULT * taper
            if hw < 0.5:
                continue
            a, b  = pts[i], pts[i + 1]
            alpha = int(TRAIL_GLOW_ALPHA * taper)
            self._quad_for(a, b, hw, Color(rgb[0], rgb[1], rgb[2], alpha))

        # ------------------------------------------------------------------
        # Pass 2 — core mesh
        # ------------------------------------------------------------------
        for i in range(n - 1):
            taper = 1.0 - i / n
            hw    = max(0.4, base_hw * taper)
            a, b  = pts[i], pts[i + 1]
            # Blend white at head → trail colour toward tail
            c = _lerp_color(_C_WHITE, rgb, i / n)
            self._quad_for(a, b, hw, Color(c[0], c[1], c[2], 255))

    @staticmethod
    def _quad_for(a, b, hw, color):
        dx = b.x - a.x
        dy = b.y - a.y
        length = (dx * dx + dy * dy) ** 0.5
        if length < 0.001:
            return
        nx = -dy / length
        ny =  dx / length

        p1 = Vector2(a.x + nx * hw, a.y + ny * hw)
        p2 = Vector2(a.x - nx * hw, a.y - ny * hw)
        p3 = Vector2(b.x + nx * hw, b.y + ny * hw)
        p4 = Vector2(b.x - nx * hw, b.y - ny * hw)

        _draw_quad(p1, p2, p3, p4, color)


def current_trail_color(progress):
    """Utility — returns the (r, g, b) tuple for a given level progress.
    Used externally (e.g. game.py) to colour particle bursts."""
    return _trail_color(progress)
