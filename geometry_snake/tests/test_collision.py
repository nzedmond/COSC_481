"""
Unit tests for utils/geometry.py — segment intersection and distance helpers.
Run with: pytest tests/test_collision.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.geometry import (
    segment_intersect_segment,
    segment_intersect_rect,
    point_to_segment_distance,
)


# ---------------------------------------------------------------------------
# segment_intersect_segment
# ---------------------------------------------------------------------------

def test_crossing_segments_intersect():
    # + shape
    assert segment_intersect_segment((0, 1), (2, 1), (1, 0), (1, 2)) is True

def test_parallel_segments_do_not_intersect():
    assert segment_intersect_segment((0, 0), (2, 0), (0, 1), (2, 1)) is False

def test_collinear_segments_do_not_intersect():
    # Treated as non-intersecting (parallel branch)
    assert segment_intersect_segment((0, 0), (2, 0), (3, 0), (5, 0)) is False

def test_t_junction_intersects():
    # One endpoint lands exactly on the other segment
    assert segment_intersect_segment((0, 0), (2, 0), (1, 0), (1, 2)) is True

def test_non_crossing_segments_do_not_intersect():
    assert segment_intersect_segment((0, 0), (1, 0), (2, 0), (3, 0)) is False

def test_degenerate_zero_length_segment():
    # Zero-length "segment" — rxs == 0, returns False
    assert segment_intersect_segment((1, 1), (1, 1), (0, 0), (2, 2)) is False


# ---------------------------------------------------------------------------
# segment_intersect_rect
# ---------------------------------------------------------------------------

def test_segment_crosses_rect():
    # Horizontal segment through rect (10,10)-(30,30)
    assert segment_intersect_rect((0, 20), (40, 20), 10, 10, 20, 20) is True

def test_segment_inside_rect():
    assert segment_intersect_rect((15, 15), (25, 25), 10, 10, 20, 20) is True

def test_segment_endpoint_on_rect_edge():
    assert segment_intersect_rect((10, 20), (0, 20), 10, 10, 20, 20) is True

def test_segment_misses_rect_completely():
    assert segment_intersect_rect((0, 0), (5, 5), 10, 10, 20, 20) is False

def test_segment_parallel_beside_rect():
    # Runs alongside the rect but never enters
    assert segment_intersect_rect((0, 5), (40, 5), 10, 10, 20, 20) is False

def test_segment_diagonal_corner_graze():
    # Passes exactly through top-left corner
    assert segment_intersect_rect((0, 0), (10, 10), 10, 10, 20, 20) is True


# ---------------------------------------------------------------------------
# point_to_segment_distance
# ---------------------------------------------------------------------------

def test_point_above_midpoint_of_segment():
    # Closest point is the foot of the perpendicular
    assert abs(point_to_segment_distance((1, 2), (0, 0), (2, 0)) - 2.0) < 1e-9

def test_point_past_end_of_segment():
    # Closest point is the endpoint (3, 0), distance = 1
    assert abs(point_to_segment_distance((4, 0), (0, 0), (3, 0)) - 1.0) < 1e-9

def test_point_before_start_of_segment():
    assert abs(point_to_segment_distance((-1, 0), (0, 0), (3, 0)) - 1.0) < 1e-9

def test_point_on_segment():
    assert point_to_segment_distance((1, 0), (0, 0), (3, 0)) < 1e-9

def test_degenerate_segment_point_distance():
    # Zero-length segment behaves like a point
    assert abs(point_to_segment_distance((3, 4), (0, 0), (0, 0)) - 5.0) < 1e-9


