import math
from pyray import *
from rendering.trail_renderer import TrailRenderer, current_trail_color


class Renderer:
    """Draws all in-game entities each frame.

    Owns a TrailRenderer internally and coordinates the layered draw order:
    parallax background → obstacles → collectibles → trail → player → particles.
    """

    def __init__(self, player, trail, obstacles, camera, parallax, particles,
                 collectibles):
        self.player      = player
        self.trail       = trail
        self.obstacles   = obstacles
        self.camera      = camera
        self.parallax    = parallax
        self.particles   = particles
        self.collectibles = collectibles
        self._trail_renderer = TrailRenderer()

    def draw(self, progress, speed_mult):
        """Render one frame.

        Args:
            progress: 0.0–1.0 cycle position used to compute the trail's hue shift.
            speed_mult: current speed multiplier, passed to TrailRenderer to scale
                        trail visual intensity.
        """
        # 1. Parallax fills background in screen space
        self.parallax.draw(self.camera.scroll_x)

        # 2. Everything in world space
        self.camera.begin()
        self._draw_obstacles()
        self._draw_collectibles()
        self._trail_renderer.draw(self.trail.points, progress, speed_mult)
        self._draw_player(progress)
        self.particles.draw()
        self.camera.end()

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_player(self, progress):
        x, y = int(self.player.pos.x), int(self.player.pos.y)
        r, g, b = current_trail_color(progress)
        draw_circle(x, y, 12, Color(r, g, b, 60))
        draw_circle(x, y,  6, WHITE)

    def _draw_obstacles(self):
        for obs in self.obstacles:
            draw_rectangle(obs.x, obs.y, obs.w, obs.h, RED)

    def _draw_collectibles(self):
        t = get_time()
        for col in self.collectibles:
            if col.collected:
                continue
            bob    = math.sin(t * 2.5 + col.x * 0.01) * 4.0
            center = Vector2(col.x, col.y + bob)
            r, g, b = col.color

            # Outer glow
            draw_circle_v(center, col.radius * 1.8, Color(r, g, b, 35))

            if col.type == "gem":
                draw_poly(center, 4, col.radius,       45.0, Color(r, g, b, 255))
                draw_poly(center, 4, col.radius * 0.5, 45.0, Color(255, 255, 255, 180))

            elif col.type == "coin":
                draw_circle_v(center, col.radius,       Color(r, g, b, 255))
                draw_circle_v(center, col.radius * 0.5, Color(min(r + 30, 255), min(g + 30, 255), 0, 200))

            elif col.type == "star":
                draw_poly(center, 5, col.radius,        -18.0, Color(r, g, b, 255))
                draw_circle_v(center, col.radius * 0.35, Color(255, 255, 255, 200))
