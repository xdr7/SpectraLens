"""
Tests for IDW Interpolation Module
====================================
"""
import pytest
import numpy as np
from interpolation.idw import IDWInterpolator


class TestIDWInterpolator:
    """Test suite for IDWInterpolator."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        interp = IDWInterpolator()
        assert interp.power == 2.0
        assert interp.k == 5
        assert interp.smoothing == 1e-12
        assert interp._is_fitted == False

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        interp = IDWInterpolator(power=3.0, k=10, smoothing=1e-10)
        assert interp.power == 3.0
        assert interp.k == 10
        assert interp.smoothing == 1e-10

    def test_fit_basic(self):
        """Test fitting with basic data."""
        interp = IDWInterpolator()
        points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        values = np.array([-50, -60, -70, -80])
        interp.fit(points, values)
        assert interp._is_fitted == True
        assert interp.points.shape == (4, 2)
        assert interp.values.shape == (4,)

    def test_fit_mismatched_shapes(self):
        """Test fit with mismatched points/values raises error."""
        interp = IDWInterpolator()
        points = np.array([[0, 0], [1, 0]])
        values = np.array([-50, -60, -70])
        with pytest.raises(ValueError, match="must match"):
            interp.fit(points, values)

    def test_fit_wrong_dimension(self):
        """Test fit with 1D points raises error."""
        interp = IDWInterpolator()
        points = np.array([0, 1, 2, 3])
        values = np.array([-50, -60, -70, -80])
        with pytest.raises((ValueError, IndexError)):
            interp.fit(points, values)

    def test_interpolate_without_fit(self):
        """Test interpolate without fit raises error."""
        interp = IDWInterpolator()
        grid_x = np.array([[0, 1], [0, 1]])
        grid_y = np.array([[0, 0], [1, 1]])
        with pytest.raises(RuntimeError, match="must be fitted"):
            interp.interpolate(grid_x, grid_y)

    def test_interpolate_single_point(self):
        """Test interpolation returns exact value at known point."""
        interp = IDWInterpolator()
        points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        values = np.array([-50, -60, -70, -80])
        interp.fit(points, values)

        # At exact point location, should be close to original value
        result = interp.interpolate_point(0, 0)
        assert abs(result - (-50)) < 1.0

    def test_interpolate_grid(self):
        """Test grid interpolation returns correct shape."""
        interp = IDWInterpolator()
        points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
        values = np.array([-50, -60, -70, -80])
        interp.fit(points, values)

        grid_x = np.array([[0, 0.5, 1], [0, 0.5, 1]])
        grid_y = np.array([[0, 0, 0], [1, 1, 1]])
        result = interp.interpolate(grid_x, grid_y)

        assert result.shape == (2, 3)
        assert not np.any(np.isnan(result))

    def test_interpolate_mismatched_grids(self):
        """Test interpolation with mismatched grid shapes."""
        interp = IDWInterpolator()
        points = np.array([[0, 0], [1, 0]])
        values = np.array([-50, -60])
        interp.fit(points, values)

        grid_x = np.array([[0, 1], [0, 1]])
        grid_y = np.array([[0, 0]])
        with pytest.raises(ValueError, match="same shape"):
            interp.interpolate(grid_x, grid_y)

    def test_interpolate_point(self):
        """Test single point interpolation."""
        interp = IDWInterpolator()
        points = np.array([[0, 0], [1, 1]])
        values = np.array([-50, -80])
        interp.fit(points, values)

        # Midpoint should be between -50 and -80
        result = interp.interpolate_point(0.5, 0.5)
        assert -80 < result < -50

    def test_get_weights_at_point(self):
        """Test weight calculation."""
        interp = IDWInterpolator(k=3)
        points = np.array([[0, 0], [1, 0], [0, 1]])
        values = np.array([-50, -60, -70])
        interp.fit(points, values)

        distances, weights = interp.get_weights_at_point(0, 0)
        assert len(distances) == 3
        assert len(weights) == 3
        assert abs(sum(weights) - 1.0) < 1e-10  # Weights sum to 1

    def test_get_weights_without_fit(self):
        """Test get_weights without fit raises error."""
        interp = IDWInterpolator()
        with pytest.raises(RuntimeError, match="must be fitted"):
            interp.get_weights_at_point(0, 0)

    def test_get_parameters(self):
        """Test get_parameters returns correct dict."""
        interp = IDWInterpolator(power=3.0, k=7)
        params = interp.get_parameters()
        assert params['power'] == 3.0
        assert params['k'] == 7
        assert params['is_fitted'] == False

    def test_set_parameters(self):
        """Test set_parameters updates correctly."""
        interp = IDWInterpolator()
        interp.set_parameters(power=4.0, k=10)
        assert interp.power == 4.0
        assert interp.k == 10

    def test_set_parameters_partial(self):
        """Test set_parameters with partial updates."""
        interp = IDWInterpolator()
        interp.set_parameters(power=3.0)
        assert interp.power == 3.0
        assert interp.k == 5  # Unchanged

    def test_repr(self):
        """Test string representation."""
        interp = IDWInterpolator(power=2.0, k=5)
        assert "IDWInterpolator" in repr(interp)
        assert "power=2.0" in repr(interp)

    def test_interpolation_smoothness(self):
        """Test that interpolation produces smooth results."""
        interp = IDWInterpolator(power=2, k=3)
        points = np.array([[0, 0], [2, 0], [0, 2], [2, 2], [1, 1]])
        values = np.array([-50, -60, -70, -80, -65])
        interp.fit(points, values)

        grid_x, grid_y = np.meshgrid(
            np.linspace(0, 2, 10),
            np.linspace(0, 2, 10)
        )
        result = interp.interpolate(grid_x, grid_y)

        # Check no NaN values
        assert not np.any(np.isnan(result))
        # Check values are within expected range
        assert np.all(result >= -100) and np.all(result <= -30)

    def test_k_greater_than_points(self):
        """Test when k is larger than number of points."""
        interp = IDWInterpolator(k=10)
        points = np.array([[0, 0], [1, 0], [0, 1]])
        values = np.array([-50, -60, -70])
        interp.fit(points, values)

        result = interp.interpolate_point(0.5, 0.5)
        assert not np.isnan(result)

    def test_smoothing_prevents_division_by_zero(self):
        """Test smoothing prevents division by zero at exact points."""
        interp = IDWInterpolator(smoothing=1e-12)
        points = np.array([[0, 0]])
        values = np.array([-50])
        interp.fit(points, values)

        result = interp.interpolate_point(0, 0)
        assert not np.isnan(result)
        assert np.isfinite(result)
