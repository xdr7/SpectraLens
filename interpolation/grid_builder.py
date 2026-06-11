"""
Grid Builder Module
====================
Membangun grid koordinat untuk visualisasi interpolasi spasial.
Mengubah titik-titik data diskrit menjadi grid kontinu untuk plotting.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
from typing import Tuple, Optional


class GridBuilder:
    """
    Builds a regular grid from scattered data points for visualization.
    
    Mengubah titik-titik data (x, y) yang tersebar menjadi grid seragam
    yang siap digunakan untuk interpolasi dan plotting.
    
    Parameters:
        points (np.ndarray): Array of shape (n, 2) containing (x, y) coordinates
        boundary_margin (float): Margin tambahan di sekitar data (dalam meter).
                                Default: 0.5
    """
    
    def __init__(self, points: np.ndarray, boundary_margin: float = 0.5):
        self.points = np.asarray(points, dtype=np.float64)
        self.boundary_margin = boundary_margin
        self._compute_bounds()
    
    def _compute_bounds(self):
        """Compute the bounding box of the data points."""
        if len(self.points) == 0:
            self.x_min = self.x_max = self.y_min = self.y_max = 0.0
            return
        
        self.x_min = float(np.min(self.points[:, 0])) - self.boundary_margin
        self.x_max = float(np.max(self.points[:, 0])) + self.boundary_margin
        self.y_min = float(np.min(self.points[:, 1])) - self.boundary_margin
        self.y_max = float(np.max(self.points[:, 1])) + self.boundary_margin
    
    def create_grid(self, resolution: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a regular 2D grid for interpolation.
        
        Args:
            resolution: Number of points along each axis.
                       Total grid points = resolution × resolution.
                       Default: 50
            
        Returns:
            Tuple of (grid_x, grid_y) - 2D arrays of shape (resolution, resolution)
        """
        if resolution < 2:
            raise ValueError(f"Resolution must be >= 2, got {resolution}")
        
        # Create evenly spaced points along each axis
        x_axis = np.linspace(self.x_min, self.x_max, resolution)
        y_axis = np.linspace(self.y_min, self.y_max, resolution)
        
        # Create 2D meshgrid
        grid_x, grid_y = np.meshgrid(x_axis, y_axis)
        
        return grid_x, grid_y
    
    def create_grid_with_step(self, step: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create a grid with a specified step size (in meters).
        
        Args:
            step: Distance between grid points in meters. Default: 0.5
            
        Returns:
            Tuple of (grid_x, grid_y) - 2D arrays
        """
        if step <= 0:
            raise ValueError(f"Step must be positive, got {step}")
        
        x_axis = np.arange(self.x_min, self.x_max + step, step)
        y_axis = np.arange(self.y_min, self.y_max + step, step)
        
        grid_x, grid_y = np.meshgrid(x_axis, y_axis)
        
        return grid_x, grid_y
    
    def get_bounds(self) -> dict:
        """Get the bounding box of the grid."""
        return {
            'x_min': self.x_min,
            'x_max': self.x_max,
            'y_min': self.y_min,
            'y_max': self.y_max,
            'width': self.x_max - self.x_min,
            'height': self.y_max - self.y_min
        }
    
    def get_area(self) -> float:
        """Get the area covered by the grid in square meters."""
        bounds = self.get_bounds()
        return bounds['width'] * bounds['height']
    
    def update_points(self, points: np.ndarray):
        """Update the data points and recompute bounds."""
        self.points = np.asarray(points, dtype=np.float64)
        self._compute_bounds()
    
    def set_margin(self, margin: float):
        """Set a new boundary margin and recompute bounds."""
        self.boundary_margin = margin
        self._compute_bounds()
    
    def __repr__(self) -> str:
        bounds = self.get_bounds()
        return (f"GridBuilder(bounds=[{bounds['x_min']:.1f}, {bounds['x_max']:.1f}, "
                f"{bounds['y_min']:.1f}, {bounds['y_max']:.1f}], "
                f"area={bounds['width']:.1f}×{bounds['height']:.1f}m)")
