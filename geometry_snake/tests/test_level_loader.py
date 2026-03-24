"""
Unit tests for systems/level.py
Run with: pytest tests/test_level_loader.py
"""
import json
import os
import sys
import tempfile
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from systems.level import Level

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_level(data):
    """Write a dict as JSON to a temp file and return the path."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, f)
    f.close()
    return f.name


MINIMAL = {
    "name": "Test Level",
    "length": 3000,
    "obstacles": [],
}

FULL = {
    "name": "Full Level",
    "length": 5000,
    "start_x": 100,
    "speed_curve": [
        {"x": 0,    "mult": 1.0},
        {"x": 2500, "mult": 1.3},
        {"x": 5000, "mult": 1.6},
    ],
    "camera": {"lookahead": 180, "lerp": 0.06},
    "parallax": [{"speed": 0.1}, {"speed": 0.4}, {"speed": 0.7}],
    "obstacles": [
        {"type": "rect",   "x": 400, "y": 100, "w": 40, "h": 200},
        {"type": "spikes", "x": 800, "y": 480, "dir": "up",   "count": 4},
        {"type": "spikes", "x": 1200, "y": 0,  "dir": "down", "count": 3},
    ],
    "collectibles": [{"type": "gem", "x": 600, "y": 150}],
}


# ---------------------------------------------------------------------------
# Loading & basic fields
# ---------------------------------------------------------------------------

def test_minimal_level_loads():
    path = _write_level(MINIMAL)
    lv = Level(path)
    assert lv.name == "Test Level"
    assert lv.level_end_x == 3000
    assert lv.obstacles == []


def test_full_level_loads():
    path = _write_level(FULL)
    lv = Level(path)
    assert lv.name == "Full Level"
    assert lv.level_end_x == 5000
    assert lv.start_x == 100
    assert lv.camera_config == {"lookahead": 180, "lerp": 0.06}
    assert len(lv.parallax_config) == 3
    assert len(lv.collectibles) == 1


def test_default_start_x_is_zero():
    path = _write_level(MINIMAL)
    lv = Level(path)
    assert lv.start_x == 0


def test_default_speed_curve_returns_1():
    path = _write_level(MINIMAL)
    lv = Level(path)
    assert lv.speed_multiplier_at(0) == 1.0
    assert lv.speed_multiplier_at(9999) == 1.0


# ---------------------------------------------------------------------------
# Obstacle building
# ---------------------------------------------------------------------------

def test_rect_obstacle_count():
    data = {**MINIMAL, "obstacles": [
        {"type": "rect", "x": 100, "y": 50, "w": 30, "h": 100},
        {"type": "rect", "x": 300, "y": 50, "w": 30, "h": 100},
    ]}
    lv = Level(_write_level(data))
    assert len(lv.obstacles) == 2


def test_rect_obstacle_properties():
    data = {**MINIMAL, "obstacles": [
        {"type": "rect", "x": 123, "y": 45, "w": 67, "h": 89},
    ]}
    lv = Level(_write_level(data))
    obs = lv.obstacles[0]
    assert obs.x == 123 and obs.y == 45 and obs.w == 67 and obs.h == 89


def test_spikes_up_generates_correct_count():
    data = {**MINIMAL, "obstacles": [
        {"type": "spikes", "x": 500, "y": 480, "dir": "up", "count": 6},
    ]}
    lv = Level(_write_level(data))
    assert len(lv.obstacles) == 6


def test_spikes_down_generates_correct_count():
    data = {**MINIMAL, "obstacles": [
        {"type": "spikes", "x": 500, "y": 0, "dir": "down", "count": 3},
    ]}
    lv = Level(_write_level(data))
    assert len(lv.obstacles) == 3


def test_spikes_up_y_position():
    """Upward spikes should extend above the y baseline."""
    data = {**MINIMAL, "obstacles": [
        {"type": "spikes", "x": 0, "y": 480, "dir": "up", "count": 1},
    ]}
    lv = Level(_write_level(data))
    spike = lv.obstacles[0]
    assert spike.y < 480  # extends above baseline


def test_spikes_down_y_position():
    """Downward spikes should start at the y baseline."""
    data = {**MINIMAL, "obstacles": [
        {"type": "spikes", "x": 0, "y": 0, "dir": "down", "count": 1},
    ]}
    lv = Level(_write_level(data))
    spike = lv.obstacles[0]
    assert spike.y == 0


def test_mixed_obstacles_total_count():
    path = _write_level(FULL)
    lv = Level(path)
    # 1 rect + 4 spikes-up + 3 spikes-down = 8
    assert len(lv.obstacles) == 8


def test_overlapping_obstacles_warns():
    data = {**MINIMAL, "obstacles": [
        {"type": "rect", "x": 100, "y": 100, "w": 50, "h": 50},
        {"type": "rect", "x": 110, "y": 110, "w": 50, "h": 50},  # overlaps
    ]}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        Level(_write_level(data))
    assert any("overlaps" in str(w.message) for w in caught)


# ---------------------------------------------------------------------------
# Speed curve interpolation
# ---------------------------------------------------------------------------

def test_speed_multiplier_before_curve_start():
    path = _write_level(FULL)
    lv = Level(path)
    assert lv.speed_multiplier_at(-100) == 1.0


def test_speed_multiplier_after_curve_end():
    path = _write_level(FULL)
    lv = Level(path)
    assert lv.speed_multiplier_at(99999) == 1.6


def test_speed_multiplier_at_midpoint():
    path = _write_level(FULL)
    lv = Level(path)
    # Midpoint between x=0 (1.0) and x=2500 (1.3) is x=1250 → 1.15
    result = lv.speed_multiplier_at(1250)
    assert abs(result - 1.15) < 1e-6


def test_speed_multiplier_at_knot():
    path = _write_level(FULL)
    lv = Level(path)
    assert lv.speed_multiplier_at(2500) == 1.3


def test_speed_curve_sorted_on_load():
    """Unsorted speed_curve entries should be sorted by x on load."""
    data = {**MINIMAL, "speed_curve": [
        {"x": 500, "mult": 1.5},
        {"x": 0,   "mult": 1.0},
    ]}
    lv = Level(_write_level(data))
    assert lv.speed_multiplier_at(250) == 1.25  # midpoint of [0,1.0]→[500,1.5]


# ---------------------------------------------------------------------------
# Validation — invalid inputs
# ---------------------------------------------------------------------------

def test_missing_name_raises():
    data = {"length": 1000, "obstacles": []}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "name" in str(exc)


def test_missing_length_raises():
    data = {"name": "X", "obstacles": []}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "length" in str(exc)


def test_missing_obstacles_raises():
    data = {"name": "X", "length": 1000}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "obstacles" in str(exc)


def test_negative_length_raises():
    data = {**MINIMAL, "length": -1}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_zero_length_raises():
    data = {**MINIMAL, "length": 0}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_unknown_obstacle_type_raises():
    data = {**MINIMAL, "obstacles": [{"type": "laser", "x": 0, "y": 0}]}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "laser" in str(exc)


def test_rect_missing_field_raises():
    data = {**MINIMAL, "obstacles": [{"type": "rect", "x": 0, "y": 0, "w": 10}]}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "h" in str(exc)


def test_invalid_json_raises():
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    f.write("{not valid json")
    f.close()
    try:
        Level(f.name)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_obstacles_not_list_raises():
    data = {**MINIMAL, "obstacles": "not a list"}
    try:
        Level(_write_level(data))
        assert False, "expected ValueError"
    except ValueError:
        pass
