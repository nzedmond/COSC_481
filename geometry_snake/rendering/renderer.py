from pyray import *
from rendering.trail_renderer import TrailRenderer


class Renderer:
    def __init__(self, player, trail, obstacles, camera, parallax, particles):
        self.player    = player
        self.trail     = trail
        self.obstacles = obstacles
        self.camera    = camera
        self.parallax  = parallax
        self.particles = particles
        self._trail_renderer = TrailRenderer()

    def draw(self, progress, speed_mult):
        # 1. Parallax fills background in screen space (no camera transform)
        self.parallax.draw(self.camera.scroll_x)

        # 2. Everything in world space
        self.camera.begin()
        self._draw_obstacles()
        self._trail_renderer.draw(self.trail.points, progress, speed_mult)
        self._draw_player(progress)
        self.particles.draw()
        self.camera.end()

    # ------------------------------------------------------------------
    # Private draw helpers
    # ------------------------------------------------------------------

    def _draw_player(self, progress):
        x, y = int(self.player.pos.x), int(self.player.pos.y)
        # Glow halo — uses current trail colour
        from rendering.trail_renderer import current_trail_color
        r, g, b = current_trail_color(progress)
        draw_circle(x, y, 12, Color(r, g, b, 60))
        draw_circle(x, y,  6, WHITE)

    def _draw_obstacles(self):
        for obs in self.obstacles:
            draw_rectangle(obs.x, obs.y, obs.w, obs.h, RED)
