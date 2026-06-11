"""
Geometry Utilities Module
==========================
Fungsi-fungsi bantuan untuk perhitungan geometri, jarak, dan koordinat
yang digunakan dalam interpolasi spasial dan visualisasi.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
from typing import Tuple, List, Optional
from math import sqrt, hypot


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two 2D points.
    
    Args:
        p1: First point (x1, y1)
        p2: Second point (x2, y2)
    
    Returns:
        Euclidean distance
    """
    return hypot(p2[0] - p1[0], p2[1] - p1[1])


def euclidean_distance_batch(points1: np.ndarray, points2: np.ndarray) -> np.ndarray:
    """
    Calculate Euclidean distances between two sets of points.
    
    Args:
        points1: Array of shape (n, 2)
        points2: Array of shape (m, 2)
    
    Returns:
        Array of shape (n, m) with pairwise distances
    """
    return np.sqrt(np.sum((points1[:, np.newaxis] - points2[np.newaxis, :]) ** 2, axis=2))


def manhattan_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Manhattan distance between two 2D points.
    
    Args:
        p1: First point (x1, y1)
        p2: Second point (x2, y2)
    
    Returns:
        Manhattan distance
    """
    return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])


def bounding_box(points: np.ndarray, margin: float = 0.0) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box of a set of points.
    
    Args:
        points: Array of shape (n, 2)
        margin: Extra margin to add (in same units as coordinates)
    
    Returns:
        Tuple of (x_min, x_max, y_min, y_max)
    """
    if len(points) == 0:
        return (0.0, 0.0, 0.0, 0.0)
    
    x_min = float(np.min(points[:, 0])) - margin
    x_max = float(np.max(points[:, 0])) + margin
    y_min = float(np.min(points[:, 1])) - margin
    y_max = float(np.max(points[:, 1])) + margin
    
    return (x_min, x_max, y_min, y_max)


def normalize_coordinates(points: np.ndarray) -> np.ndarray:
    """
    Normalize coordinates to [0, 1] range.
    
    Args:
        points: Array of shape (n, 2)
    
    Returns:
        Normalized array of shape (n, 2)
    """
    if len(points) == 0:
        return points
    
    x_min, x_max = np.min(points[:, 0]), np.max(points[:, 0])
    y_min, y_max = np.min(points[:, 1]), np.max(points[:, 1])
    
    normalized = points.copy().astype(np.float64)
    
    if x_max > x_min:
        normalized[:, 0] = (normalized[:, 0] - x_min) / (x_max - x_min)
    else:
        normalized[:, 0] = 0.5
    
    if y_max > y_min:
        normalized[:, 1] = (normalized[:, 1] - y_min) / (y_max - y_min)
    else:
        normalized[:, 1] = 0.5
    
    return normalized


def denormalize_coordinates(normalized: np.ndarray, 
                            original_min: Tuple[float, float],
                            original_max: Tuple[float, float]) -> np.ndarray:
    """
    Denormalize coordinates back to original range.
    
    Args:
        normalized: Normalized array of shape (n, 2)
        original_min: Original minimum (x_min, y_min)
        original_max: Original maximum (x_max, y_max)
    
    Returns:
        Denormalized array of shape (n, 2)
    """
    result = normalized.copy()
    result[:, 0] = normalized[:, 0] * (original_max[0] - original_min[0]) + original_min[0]
    result[:, 1] = normalized[:, 1] * (original_max[1] - original_min[1]) + original_min[1]
    return result


def grid_to_points(grid_x: np.ndarray, grid_y: np.ndarray, grid_z: np.ndarray) -> np.ndarray:
    """
    Convert 2D grid data to point cloud format.
    
    Args:
        grid_x: 2D array of X coordinates
        grid_y: 2D array of Y coordinates
        grid_z: 2D array of Z values
    
    Returns:
        Array of shape (n, 3) with columns [x, y, z]
    """
    n_points = grid_x.size
    points = np.column_stack([
        grid_x.ravel(),
        grid_y.ravel(),
        grid_z.ravel()
    ])
    return points


def points_to_grid(x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                   resolution: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert scattered points to regular grid using simple binning.
    
    Args:
        x: Array of X coordinates
        y: Array of Y coordinates
        z: Array of Z values
        resolution: Grid resolution
    
    Returns:
        Tuple of (grid_x, grid_y, grid_z)
    """
    from scipy.interpolate import griddata
    
    grid_x_axis = np.linspace(np.min(x), np.max(x), resolution)
    grid_y_axis = np.linspace(np.min(y), np.max(y), resolution)
    grid_x, grid_y = np.meshgrid(grid_x_axis, grid_y_axis)
    
    grid_z = griddata(
        np.column_stack([x, y]), z,
        (grid_x, grid_y),
        method='cubic',
        fill_value=np.mean(z)
    )
    
    return grid_x, grid_y, grid_z


def rssi_to_percentage(rssi: float, rssi_min: float = -100, rssi_max: float = -30) -> float:
    """
    Convert RSSI (dBm) to percentage for easier interpretation.
    
    Args:
        rssi: RSSI value in dBm
        rssi_min: Minimum expected RSSI (default: -100 dBm)
        rssi_max: Maximum expected RSSI (default: -30 dBm)
    
    Returns:
        Percentage value (0-100)
    """
    if rssi <= rssi_min:
        return 0.0
    if rssi >= rssi_max:
        return 100.0
    
    return ((rssi - rssi_min) / (rssi_max - rssi_min)) * 100.0


def rssi_to_quality(rssi: float) -> str:
    """
    Convert RSSI to qualitative description.
    
    Args:
        rssi: RSSI value in dBm
    
    Returns:
        Quality description string
    """
    if rssi >= -50:
        return "Excellent"
    elif rssi >= -60:
        return "Good"
    elif rssi >= -70:
        return "Fair"
    elif rssi >= -80:
        return "Weak"
    else:
        return "Very Weak"


def signal_strength_color(rssi: float) -> Tuple[int, int, int]:
    """
    Get RGB color for a given RSSI value.
    
    Args:
        rssi: RSSI value in dBm
    
    Returns:
        RGB tuple (r, g, b) with values 0-255
    """
    # Map RSSI from [-100, -30] to [0, 1]
    normalized = max(0, min(1, (rssi + 100) / 70))
    
    # Red (weak) -> Yellow -> Green (strong)
    if normalized < 0.5:
        r = int(255 * (1 - normalized * 2))
        g = int(255 * (normalized * 2))
        b = 0
    else:
        r = 0
        g = int(255 * (1 - (normalized - 0.5) * 2))
        b = int(255 * ((normalized - 0.5) * 2))
    
    return (r, g, b)


def calculate_optimal_grid_resolution(area_width: float, area_height: float, 
                                       points_per_meter: float = 2.0) -> int:
    """
    Calculate optimal grid resolution based on area size.
    
    Args:
        area_width: Width of area in meters
        area_height: Height of area in meters
        points_per_meter: Desired points per meter (default: 2)
    
    Returns:
        Recommended grid resolution
    """
    max_dim = max(area_width, area_height)
    resolution = int(max_dim * points_per_meter)
    return max(10, min(200, resolution))  # Clamp between 10 and 200


def is_point_in_bounds(x: float, y: float, bounds: Tuple[float, float, float, float]) -> bool:
    """
    Check if a point is within given bounds.
    
    Args:
        x: X coordinate
        y: Y coordinate
        bounds: Tuple of (x_min, x_max, y_min, y_max)
    
    Returns:
        True if point is within bounds
    """
    x_min, x_max, y_min, y_max = bounds
    return x_min <= x <= x_max and y_min <= y <= y_max
