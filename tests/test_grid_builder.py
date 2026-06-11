"""
Tests for Grid Builder Module
===============================
"""
import pytest
import numpy as np
from interpolation.grid_builder import GridBuilder


class TestGridBuilder:
    """Test suite for GridBuilder."""

    def test_init_basic(self):
        """Test initialization with basic points."""
        points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        gb = GridBuilder(points)
        assert gb.boundary_margin == 0.5
        assert gb.x_min == -0.5
        assert gb.x_max == 1.5
        assert gb.y_min == -0.5
        assert gb.y_max == 1.5

    def test_init_empty_points(self):
        """Test initialization with empty points."""
        points = np.array([]).reshape(0, 2)
        gb = GridBuilder(points)
        assert gb.x_min == 0.0
        assert gb.x_max == 0.0

    def test_init_custom_margin(self):
        """Test initialization with custom margin."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points, boundary_margin=2.0)
        assert gb.x_min == -2.0
        assert gb.x_max == 12.0

    def test_create_grid_default(self):
        """Test grid creation with default resolution."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        grid_x, grid_y = gb.create_grid()
        assert grid_x.shape == (50, 50)
        assert grid_y.shape == (50, 50)

    def test_create_grid_custom_resolution(self):
        """Test grid creation with custom resolution."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        grid_x, grid_y = gb.create_grid(resolution=100)
        assert grid_x.shape == (100, 100)

    def test_create_grid_low_resolution(self):
        """Test grid creation with resolution < 2 raises error."""
        points = np.array([[0, 0], [1, 1]])
        gb = GridBuilder(points)
        with pytest.raises(ValueError, match="must be >= 2"):
            gb.create_grid(resolution=1)

    def test_create_grid_values(self):
        """Test grid values are within expected range."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        grid_x, grid_y = gb.create_grid(resolution=5)

        assert grid_x[0, 0] == -0.5  # x_min
        assert grid_x[-1, -1] == 10.5  # x_max
        assert grid_y[0, 0] == -0.5  # y_min
        assert grid_y[-1, -1] == 10.5  # y_max

    def test_create_grid_with_step(self):
        """Test grid creation with step size."""
        points = np.array([[0, 0], [5, 5]])
        gb = GridBuilder(points, boundary_margin=0)
        grid_x, grid_y = gb.create_grid_with_step(step=1.0)

        assert grid_x.shape[0] == 6  # 0 to 5 inclusive
        assert grid_x[0, 0] == 0.0
        assert grid_x[-1, -1] == 5.0

    def test_create_grid_with_step_invalid(self):
        """Test grid creation with invalid step."""
        points = np.array([[0, 0], [1, 1]])
        gb = GridBuilder(points)
        with pytest.raises(ValueError, match="must be positive"):
            gb.create_grid_with_step(step=0)

    def test_get_bounds(self):
        """Test get_bounds returns correct values."""
        points = np.array([[2, 3], [8, 7]])
        gb = GridBuilder(points, boundary_margin=1.0)
        bounds = gb.get_bounds()

        assert bounds['x_min'] == 1.0
        assert bounds['x_max'] == 9.0
        assert bounds['y_min'] == 2.0
        assert bounds['y_max'] == 8.0
        assert bounds['width'] == 8.0
        assert bounds['height'] == 6.0

    def test_get_area(self):
        """Test get_area calculation."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points, boundary_margin=0)
        area = gb.get_area()
        assert area == 100.0  # 10 * 10

    def test_update_points(self):
        """Test updating points recomputes bounds."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        assert gb.x_max == 10.5

        new_points = np.array([[0, 0], [20, 20]])
        gb.update_points(new_points)
        assert gb.x_max == 20.5

    def test_set_margin(self):
        """Test setting new margin recomputes bounds."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        assert gb.x_min == -0.5

        gb.set_margin(2.0)
        assert gb.x_min == -2.0

    def test_repr(self):
        """Test string representation."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        assert "GridBuilder" in repr(gb)
        assert "bounds" in repr(gb)

    def test_single_point_grid(self):
        """Test grid creation with single point."""
        points = np.array([[5, 5]])
        gb = GridBuilder(points)
        grid_x, grid_y = gb.create_grid(resolution=3)
        assert grid_x.shape == (3, 3)
        assert grid_y.shape == (3, 3)
        # Grid should be centered around the single point
        assert grid_x[0, 0] < 5.0 < grid_x[-1, -1]
        assert grid_y[0, 0] < 5.0 < grid_y[-1, -1]
        # Each row should be identical (same x values per row)
        assert np.allclose(grid_x[0], grid_x[1])
        assert np.allclose(grid_x[1], grid_x[2])
        # Each column should be identical (same y values per column)
        assert np.allclose(grid_y[:, 0], grid_y[:, 1])
        assert np.allclose(grid_y[:, 1], grid_y[:, 2])

    def test_grid_monotonic(self):
        """Test grid values are monotonically increasing."""
        points = np.array([[0, 0], [10, 10]])
        gb = GridBuilder(points)
        grid_x, grid_y = gb.create_grid(resolution=10)

        # Each row should be increasing
        for row in grid_x:
            assert np.all(np.diff(row) > 0)
        # Each column should be increasing
        for col in grid_y.T:
            assert np.all(np.diff(col) > 0)
