"""
Data-driven level loader.

Loads a JSON file, validates its schema, builds runtime Obstacle objects,
and exposes the speed curve for per-x speed multiplier look-ups.

Supported obstacle types
------------------------
rect   — axis-aligned rectangle  {type, x, y, w, h}
spikes — row of spike columns     {type, x, y, dir("up"|"down"), count}
"""

import json
import warnings
from entities.obstacle import Obstacle

_SPIKE_WIDTH  = 15
_SPIKE_HEIGHT = 30

_REQUIRED = {"name", "length", "obstacles"}


class Level:
    def __init__(self, path):
        with open(path, "r") as f:
            try:
                raw = json.load(f)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path!r}: {exc}") from exc

        self._validate_top(raw, path)

        self.name            = raw["name"]
        self.level_end_x     = int(raw["length"])
        self.start_x         = int(raw.get("start_x", 0))
        self.speed_curve     = self._validated_speed_curve(raw.get("speed_curve", [{"x": 0, "mult": 1.0}]))
        self.camera_config   = raw.get("camera", {})
        self.parallax_config = raw.get("parallax", [])
        self.parallax_seed   = int(raw.get("parallax_seed", 42))
        self.collectibles    = raw.get("collectibles", [])
        self.obstacles       = self._build_obstacles(raw["obstacles"])

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def speed_multiplier_at(self, x):
        """Return the linearly-interpolated speed multiplier at world x."""
        curve = self.speed_curve
        if x <= curve[0]["x"]:
            return float(curve[0]["mult"])
        if x >= curve[-1]["x"]:
            return float(curve[-1]["mult"])
        for i in range(len(curve) - 1):
            x0, m0 = curve[i]["x"],   curve[i]["mult"]
            x1, m1 = curve[i + 1]["x"], curve[i + 1]["mult"]
            if x0 <= x <= x1:
                t = (x - x0) / (x1 - x0)
                return m0 + t * (m1 - m0)
        return float(curve[-1]["mult"])

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_top(data, path):
        missing = _REQUIRED - data.keys()
        if missing:
            raise ValueError(f"{path!r} missing required fields: {sorted(missing)}")
        if not isinstance(data["length"], (int, float)) or data["length"] <= 0:
            raise ValueError(f"{path!r}: 'length' must be a positive number, got {data['length']!r}")
        if not isinstance(data["obstacles"], list):
            raise ValueError(f"{path!r}: 'obstacles' must be a list")

    @staticmethod
    def _validated_speed_curve(curve):
        if not isinstance(curve, list) or len(curve) == 0:
            raise ValueError("'speed_curve' must be a non-empty list")
        for i, pt in enumerate(curve):
            if "x" not in pt or "mult" not in pt:
                raise ValueError(f"speed_curve[{i}] missing 'x' or 'mult'")
        return sorted(curve, key=lambda p: p["x"])  # guarantee sorted by x

    @staticmethod
    def _require_keys(d, keys, context):
        missing = keys - d.keys()
        if missing:
            raise ValueError(f"{context} missing keys: {sorted(missing)}")

    # ------------------------------------------------------------------
    # Obstacle building
    # ------------------------------------------------------------------

    def _build_obstacles(self, raw_list):
        seen_rects = []
        obstacles  = []
        for i, item in enumerate(raw_list):
            obs_type = item.get("type")
            ctx      = f"obstacles[{i}]"

            if obs_type == "rect":
                self._require_keys(item, {"x", "y", "w", "h"}, ctx)
                obs = Obstacle(item["x"], item["y"], item["w"], item["h"])
                self._warn_overlap(obs, seen_rects, ctx)
                seen_rects.append(obs)
                obstacles.append(obs)

            elif obs_type == "spikes":
                self._require_keys(item, {"x", "y", "count"}, ctx)
                spikes = self._build_spikes(item)
                for s in spikes:
                    self._warn_overlap(s, seen_rects, ctx)
                    seen_rects.append(s)
                obstacles.extend(spikes)

            else:
                raise ValueError(f"{ctx}: unknown obstacle type {obs_type!r}")

        return obstacles

    @staticmethod
    def _build_spikes(item):
        count = int(item["count"])
        base_y = int(item["y"])
        start_x = int(item["x"])
        direction = item.get("dir", "up")

        spikes = []
        for k in range(count):
            sx = start_x + k * _SPIKE_WIDTH
            if direction == "up":
                # y is the floor line; spike extends upward
                sy = base_y - _SPIKE_HEIGHT
            else:
                # y is the ceiling line; spike extends downward
                sy = base_y
            spikes.append(Obstacle(sx, sy, _SPIKE_WIDTH, _SPIKE_HEIGHT))
        return spikes

    @staticmethod
    def _warn_overlap(new_obs, existing, context):
        for prev in existing:
            if (new_obs.x < prev.x + prev.w and new_obs.x + new_obs.w > prev.x and
                    new_obs.y < prev.y + prev.h and new_obs.y + new_obs.h > prev.y):
                warnings.warn(
                    f"{context}: obstacle overlaps an earlier one at "
                    f"({prev.x},{prev.y})",
                    stacklevel=3,
                )
                break
