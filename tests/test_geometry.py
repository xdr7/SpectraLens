"""
Tests for Geometry Utilities Module
=====================================
"""
import pytest
import numpy as np
from utils.geometry import (
    euclidean_distance,
    euclidean_distance_batch,
    manhattan_distance,
    bounding_box,
    normalize_coordinates,
    denormalize_coordinates,
    grid_to_points,
    points_to_grid,
    rssi_to_percentage,
    rssi_to_quality,
    signal_strength_color,
    calculate_optimal_grid_resolution,
    is_point_in_bounds,
)


class TestGeometry:
    """Test suite for geometry utilities."""

    def test_euclidean_distance(self):
        """Test Euclidean distance calculation."""
        d = euclidean_distance((0, 0), (3, 4))
        assert d == 5.0

    def test_euclidean_distance_zero(self):
        """Test Euclidean distance between same points."""
        d = euclidean_distance((1, 1), (1, 1))
        assert d == 0.0

    def test_euclidean_distance_negative(self):
        """Test Euclidean distance with negative coordinates."""
        d = euclidean_distance((-1, -1), (2, 3))
        assert d == 5.0

    def test_euclidean_distance_batch(self):
        """Test batch Euclidean distance."""
        p1 = np.array([[0, 0], [1, 1]])
        p2 = np.array([[3, 4], [0, 0]])
        distances = euclidean_distance_batch(p1, p2)
        assert distances.shape == (2, 2)
        assert abs(distances[0, 0] - 5.0) < 1e-10

    def test_manhattan_distance(self):
        """Test Manhattan distance calculation."""
        d = manhattan_distance((0, 0), (3, 4))
        assert d == 7.0

    def test_manhattan_distance_zero(self):
        """Test Manhattan distance between same points."""
        d = manhattan_distance((1, 1), (1, 1))
        assert d == 0.0

    def test_bounding_box(self):
        """Test bounding box calculation."""
        points = np.array([[0, 0], [10, 5], [3, 7]])
        bbox = bounding_box(points, margin=0)
        assert bbox == (0.0, 10.0, 0.0, 7.0)

    def test_bounding_box_with_margin(self):
        """Test bounding box with margin."""
        points = np.array([[0, 0], [10, 10]])
        bbox = bounding_box(points, margin=1.0)
        assert bbox == (-1.0, 11.0, -1.0, 11.0)

    def test_bounding_box_empty(self):
        """Test bounding box with empty points."""
        points = np.array([]).reshape(0, 2)
        bbox = bounding_box(points)
        assert bbox == (0.0, 0.0, 0.0, 0.0)

    def test_normalize_coordinates(self):
        """Test coordinate normalization."""
        points = np.array([[0, 0], [10, 20]])
        normalized = normalize_coordinates(points)
        assert normalized[0, 0] == 0.0
        assert normalized[0, 1] == 0.0
        assert normalized[1, 0] == 1.0
        assert normalized[1, 1] == 1.0

    def test_normalize_coordinates_single_point(self):
        """Test normalization with single point."""
        points = np.array([[5, 5]])
        normalized = normalize_coordinates(points)
        assert normalized[0, 0] == 0.5
        assert normalized[0, 1] == 0.5

    def test_denormalize_coordinates(self):
        """Test coordinate denormalization."""
        normalized = np.array([[0.0, 0.0], [1.0, 1.0]])
        original = denormalize_coordinates(
            normalized,
            original_min=(0, 0),
            original_max=(10, 20)
        )
        assert original[0, 0] == 0.0
        assert original[0, 1] == 0.0
        assert original[1, 0] == 10.0
        assert original[1, 1] == 20.0

    def test_grid_to_points(self):
        """Test grid to points conversion."""
        grid_x = np.array([[0, 1], [0, 1]])
        grid_y = np.array([[0, 0], [1, 1]])
        grid_z = np.array([[-50, -60], [-70, -80]])
        points = grid_to_points(grid_x, grid_y, grid_z)
        assert points.shape == (4, 3)
        assert points[0, 2] == -50

    def test_points_to_grid(self):
        """Test points to grid conversion."""
        x = np.array([0, 1, 0, 1])
        y = np.array([0, 0, 1, 1])
        z = np.array([-50, -60, -70, -80])
        grid_x, grid_y, grid_z = points_to_grid(x, y, z, resolution=5)
        assert grid_x.shape == (5, 5)
        assert grid_y.shape == (5, 5)
        assert grid_z.shape == (5, 5)

    def test_rssi_to_percentage(self):
        """Test RSSI to percentage conversion."""
        assert rssi_to_percentage(-30) == 100.0
        assert rssi_to_percentage(-100) == 0.0
        assert rssi_to_percentage(-65) == 50.0

    def test_rssi_to_percentage_out_of_range(self):
        """Test RSSI to percentage with out-of-range values."""
        assert rssi_to_percentage(-20) == 100.0  # Above max
        assert rssi_to_percentage(-120) == 0.0  # Below min

    def test_rssi_to_quality(self):
        """Test RSSI to quality description."""
        assert rssi_to_quality(-40) == "Excellent"
        assert rssi_to_quality(-55) == "Good"
        assert rssi_to_quality(-65) == "Fair"
        assert rssi_to_quality(-75) == "Weak"
        assert rssi_to_quality(-90) == "Very Weak"

    def test_signal_strength_color(self):
        """Test signal strength color conversion."""
        r, g, b = signal_strength_color(-30)  # Strong
        assert r == 0
        assert g == 0
        assert b == 255

        r, g, b = signal_strength_color(-100)  # Weak
        assert r == 255
        assert g == 0
        assert b == 0

    def test_calculate_optimal_grid_resolution(self):
        """Test optimal grid resolution calculation."""
        res = calculate_optimal_grid_resolution(10, 10, points_per_meter=2)
        assert res == 20  # 10 * 2

    def test_calculate_optimal_grid_resolution_clamp(self):
        """Test optimal grid resolution clamping."""
        res = calculate_optimal_grid_resolution(1, 1, points_per_meter=2)
        assert res == 10  # Clamped to minimum

        res = calculate_optimal_grid_resolution(200, 200, points_per_meter=2)
        assert res == 200  # Clamped to maximum

    def test_is_point_in_bounds(self):
        """Test point in bounds check."""
        bounds = (0, 10, 0, 10)
        assert is_point_in_bounds(5, 5, bounds) == True
        assert is_point_in_bounds(-1, 5, bounds) == False
        assert is_point_in_bounds(5, 15, bounds) == False

    def test_is_point_in_bounds_edge(self):
        """Test point in bounds at edges."""
        bounds = (0, 10, 0, 10)
        assert is_point_in_bounds(0, 0, bounds) == True
        assert is_point_in_bounds(10, 10, bounds) == True
