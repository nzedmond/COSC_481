"""
Pool-based particle system — no allocations after construction.

Particles are in world space; draw them inside camera.begin()/end().
"""

import math
import random
from pyray import *
from config.settings import *


class _Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'r', 'g', 'b')

    def __init__(self):
        self.life = 0.0   # 0 = dead / available


class ParticleSystem:
    def __init__(self, pool_size=PARTICLE_POOL_SIZE):
        self._pool = [_Particle() for _ in range(pool_size)]

    # ------------------------------------------------------------------
    # Emission
    # ------------------------------------------------------------------

    def emit_burst(self, x, y, count, speed, color):
        """Emit up to *count* particles from world position (x, y).

        color — (r, g, b) tuple
        Silently skips if the pool is exhausted.
        """
        emitted = 0
        for p in self._pool:
            if emitted >= count:
                break
            if p.life <= 0.0:
                angle = random.random() * 6.283185307
                spd   = speed * (0.5 + random.random() * 0.5)
                p.x, p.y     = x, y
                p.vx         = math.cos(angle) * spd
                p.vy         = math.sin(angle) * spd
                p.max_life   = 0.3 + random.random() * 0.4
                p.life       = p.max_life
                p.r, p.g, p.b = color
                emitted += 1

    # ------------------------------------------------------------------
    # Update / draw  (called from fixed-update and render respectively)
    # ------------------------------------------------------------------

    def update(self, dt):
        for p in self._pool:
            if p.life > 0.0:
                p.x  += p.vx * dt
                p.y  += p.vy * dt
                p.vy += 150.0 * dt   # gravity pulls down in screen space
                p.life -= dt

    def draw(self):
        for p in self._pool:
            if p.life > 0.0:
                t     = max(0.0, p.life / p.max_life)
                alpha = int(255 * t)
                draw_circle(int(p.x), int(p.y), max(1, int(3 * t)),
                            Color(p.r, p.g, p.b, alpha))
