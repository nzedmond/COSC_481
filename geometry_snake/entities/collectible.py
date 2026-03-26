"""
Pure-data collectible entity.  No pyray imports — rendering is in renderer.py.

Supported types
---------------
gem  — 10 pts  cyan diamond, medium risk
coin —  5 pts  gold circle, easy pickup
star — 50 pts  yellow pentagon, hard/risky placement
"""


COLLECTIBLE_TYPES = {
    "gem":  {"value": 10, "radius": 10.0, "color": (0,   220, 255)},
    "coin": {"value":  5, "radius":  8.0, "color": (255, 200,  50)},
    "star": {"value": 50, "radius": 12.0, "color": (255, 230,   0)},
}

DEFAULT_COLLECTIBLE = COLLECTIBLE_TYPES["gem"]


class Collectible:
    def __init__(self, x, y, type_name):
        curr_collectible = COLLECTIBLE_TYPES.get(type_name, DEFAULT_COLLECTIBLE)
        self.x         = float(x)
        self.y         = float(y)
        self.type      = type_name
        self.value     = curr_collectible["value"]
        self.radius    = curr_collectible["radius"]
        self.color     = curr_collectible["color"]   # (r, g, b) tuple
        self.collected = False


def build_collectibles(raw_list):
    """Convert the raw JSON list from Level into Collectible objects."""
    return [
        Collectible(item["x"], item["y"], item.get("type", "gem"))
        for item in raw_list
    ]
