COLLECTIBLE_TYPES = {
    "gem":  {"value": 10, "radius": 10.0, "color": (0,   220, 255)},
    "coin": {"value":  5, "radius":  8.0, "color": (255, 200,  50)},
    "star": {"value": 50, "radius": 12.0, "color": (255, 230,   0)},
}

DEFAULT_COLLECTIBLE_TYPE = COLLECTIBLE_TYPES["gem"]


class Collectible:
    """A pickup item the player can collect by flying through it.

    Holds the item's world position, point value, collision radius, display
    color, and whether it has already been collected this run.  The visual
    appearance is determined by the type name ('gem', 'coin', or 'star') and
    looked up from COLLECTIBLE_TYPES at construction time.
    """

    def __init__(self, x, y, type_name):
        type_config    = COLLECTIBLE_TYPES.get(type_name, DEFAULT_COLLECTIBLE_TYPE)
        self.x         = float(x)
        self.y         = float(y)
        self.type      = type_name
        self.value     = type_config["value"]
        self.radius    = type_config["radius"]
        self.color     = type_config["color"]
        self.collected = False


def build_collectibles(raw_list):
    return [Collectible(item["x"], item["y"], item.get("type", "gem")) for item in raw_list]
