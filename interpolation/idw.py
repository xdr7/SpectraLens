"""
IDW Interpolation Module
=========================
Implementasi algoritma Inverse Distance Weighting (IDW) dengan KNN
untuk interpolasi spasial data kekuatan sinyal WiFi.

Rumus:
    weight = 1 / (distance ^ power)
    value = Σ(weight_i × rssi_i) / Σ(weight_i)

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
from scipy.spatial import cKDTree
from typing import Optional, Tuple, List


class IDWInterpolator:
    """
    Inverse Distance Weighting (IDW) interpolator with KNN optimization.
    
    Menginterpolasi nilai pada titik yang tidak terukur berdasarkan
    rata-rata tertimbang dari titik-titik terdekat yang sudah diketahui.
    
    Parameters:
        power (float): Power parameter (p). Semakin tinggi, semakin cepat
                      pengaruh sinyal berkurang dengan jarak. Default: 2
        k (int): Number of nearest neighbors (KNN). Default: 5
        smoothing (float): Smoothing factor untuk menghindari division by zero.
                          Default: 1e-12
    """
    
    def __init__(self, power: float = 2.0, k: int = 5, smoothing: float = 1e-12):
        self.power = power
        self.k = k
        self.smoothing = smoothing
        self.points: Optional[np.ndarray] = None
        self.values: Optional[np.ndarray] = None
        self.tree: Optional[cKDTree] = None
        self._is_fitted = False
    
    def fit(self, points: np.ndarray, values: np.ndarray):
        """
        Fit the interpolator with known data points.
        
        Args:
            points: Array of shape (n, 2) containing (x, y) coordinates
            values: Array of shape (n,) containing RSSI values
        """
        self.points = np.asarray(points, dtype=np.float64)
        self.values = np.asarray(values, dtype=np.float64)
        
        if self.points.shape[0] != self.values.shape[0]:
            raise ValueError(
                f"Number of points ({self.points.shape[0]}) must match "
                f"number of values ({self.values.shape[0]})"
            )
        
        if self.points.shape[1] != 2:
            raise ValueError(
                f"Points must be 2D (x, y), got shape {self.points.shape}"
            )
        
        # Build KDTree for efficient nearest neighbor search
        self.tree = cKDTree(self.points)
        self._is_fitted = True
    
    def interpolate(self, grid_x: np.ndarray, grid_y: np.ndarray) -> np.ndarray:
        """
        Interpolate values at given grid points.
        
        Args:
            grid_x: 2D array of X coordinates
            grid_y: 2D array of Y coordinates (same shape as grid_x)
            
        Returns:
            2D array of interpolated values (same shape as grid_x)
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before interpolation. Call fit() first.")
        
        grid_x = np.asarray(grid_x, dtype=np.float64)
        grid_y = np.asarray(grid_y, dtype=np.float64)
        
        if grid_x.shape != grid_y.shape:
            raise ValueError("grid_x and grid_y must have the same shape")
        
        # Flatten grid for querying
        flat_x = grid_x.ravel()
        flat_y = grid_y.ravel()
        query_points = np.column_stack([flat_x, flat_y])
        
        # Query KNN for each grid point
        # k is limited by number of available points
        k_actual = min(self.k, len(self.points))
        distances, indices = self.tree.query(query_points, k=k_actual)
        
        # Handle single vs multiple neighbors
        if k_actual == 1:
            distances = distances.reshape(-1, 1)
            indices = indices.reshape(-1, 1)
        
        # Calculate IDW weights
        # Add smoothing to avoid division by zero
        weights = 1.0 / (distances ** self.power + self.smoothing)
        
        # Get values of neighbors
        neighbor_values = self.values[indices]
        
        # Calculate weighted average
        weighted_sum = np.sum(weights * neighbor_values, axis=1)
        weight_sum = np.sum(weights, axis=1)
        
        # Avoid division by zero
        interpolated = np.where(weight_sum > 0, weighted_sum / weight_sum, 0)
        
        # Reshape back to grid shape
        return interpolated.reshape(grid_x.shape)
    
    def interpolate_point(self, x: float, y: float) -> float:
        """
        Interpolate value at a single point.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Interpolated value at (x, y)
        """
        grid_x = np.array([[x]])
        grid_y = np.array([[y]])
        result = self.interpolate(grid_x, grid_y)
        return float(result[0, 0])
    
    def get_weights_at_point(self, x: float, y: float) -> Tuple[List[float], List[float]]:
        """
        Get the weights and distances for neighbors at a given point.
        Berguna untuk debugging dan visualisasi bobot.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (distances list, weights list)
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted first.")
        
        k_actual = min(self.k, len(self.points))
        distances, indices = self.tree.query([[x, y]], k=k_actual)
        
        distances = distances[0]
        indices = indices[0]
        
        weights = 1.0 / (distances ** self.power + self.smoothing)
        weights = weights / np.sum(weights)
        
        return distances.tolist(), weights.tolist()
    
    def get_parameters(self) -> dict:
        """Get current interpolation parameters."""
        return {
            'power': self.power,
            'k': self.k,
            'smoothing': self.smoothing,
            'n_points': len(self.points) if self.points is not None else 0,
            'is_fitted': self._is_fitted
        }
    
    def set_parameters(self, power: Optional[float] = None, 
                       k: Optional[int] = None,
                       smoothing: Optional[float] = None):
        """
        Update interpolation parameters.
        
        Args:
            power: New power parameter
            k: New number of neighbors
            smoothing: New smoothing factor
        """
        if power is not None:
            self.power = power
        if k is not None:
            self.k = k
        if smoothing is not None:
            self.smoothing = smoothing
    
    def __repr__(self) -> str:
        return (f"IDWInterpolator(power={self.power}, k={self.k}, "
                f"smoothing={self.smoothing}, fitted={self._is_fitted})")
