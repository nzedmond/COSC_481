from entities.trail import Trail
from pyray import Vector2

def test_trail_growth():
    trail = Trail()
    
    trail.update(Vector2(0, 0))
    trail.update(Vector2(10, 0))
    
    assert len(trail.points) > 0