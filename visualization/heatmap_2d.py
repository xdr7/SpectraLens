"""
Heatmap 2D Visualization Module
=================================
Membuat peta panas 2D distribusi kekuatan sinyal WiFi menggunakan
matplotlib dan seaborn.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple
import os


class Heatmap2D:
    """
    Generates 2D heatmap visualization of WiFi signal strength distribution.
    
    Menampilkan peta panas yang menunjukkan area dengan sinyal kuat (merah)
    dan lemah (biru) berdasarkan hasil interpolasi IDW.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 10), dpi: int = 150):
        self.figsize = figsize
        self.dpi = dpi
        self.output_dir = "output"
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14
        })
    
    def plot(self, points: np.ndarray, values: np.ndarray,
             grid_x: np.ndarray, grid_y: np.ndarray, grid_z: np.ndarray,
             title: str = "WiFi Signal Strength Heatmap",
             filename: Optional[str] = None,
             show_points: bool = True,
             show_colorbar: bool = True,
             cmap: str = "RdYlBu_r") -> str:
        """
        Generate and save a 2D heatmap.
        
        Args:
            points: Original data points (n, 2)
            values: Original RSSI values (n,)
            grid_x: X coordinates of interpolation grid
            grid_y: Y coordinates of interpolation grid
            grid_z: Interpolated values on grid
            title: Plot title
            filename: Output filename (auto-generated if None)
            show_points: Whether to overlay original data points
            show_colorbar: Whether to show colorbar
            cmap: Colormap (default: RdYlBu_r = red-yellow-blue reversed)
                  Red = strong signal, Blue = weak signal
            
        Returns:
            Path to saved image file
        """
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Auto-generate filename if not provided
        if filename is None:
            filename = f"heatmap_{len(points)}points.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot heatmap using contourf for smooth visualization
        contour = ax.contourf(grid_x, grid_y, grid_z, 
                              levels=50, cmap=cmap, alpha=0.85)
        
        # Add contour lines for better readability
        contour_lines = ax.contour(grid_x, grid_y, grid_z, 
                                   levels=10, colors='black', 
                                   linewidths=0.5, alpha=0.3)
        ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%.0f')
        
        # Overlay original data points
        if show_points and points is not None:
            scatter = ax.scatter(points[:, 0], points[:, 1], 
                               c=values, cmap=cmap, 
                               edgecolors='black', linewidth=1,
                               s=80, zorder=5, vmin=grid_z.min(), vmax=grid_z.max())
            
            # Add value labels next to points
            for i, (x, y) in enumerate(points):
                ax.annotate(f'{values[i]:.0f}', (x, y), 
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.2', 
                                   facecolor='white', alpha=0.7))
        
        # Add colorbar
        if show_colorbar:
            cbar = plt.colorbar(contour, ax=ax, label='Signal Strength (dBm)',
                               shrink=0.8)
            cbar.ax.yaxis.label.set_size(12)
        
        # Labels and title
        ax.set_xlabel('X Position (meters)')
        ax.set_ylabel('Y Position (meters)')
        ax.set_title(title, fontweight='bold', pad=15)
        
        # Set aspect ratio to equal
        ax.set_aspect('equal')
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add legend for data points
        if show_points:
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='gray', markersize=10,
                      label=f'Measurement Points ({len(points)})'),
                Line2D([0], [0], marker='', color='black', 
                      linewidth=0.5, label='Signal Contours')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
        
        # Add statistics box
        stats_text = (f"Min: {grid_z.min():.0f} dBm\n"
                     f"Max: {grid_z.max():.0f} dBm\n"
                     f"Avg: {grid_z.mean():.0f} dBm\n"
                     f"Grid: {grid_x.shape[0]}×{grid_x.shape[1]}")
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        print(f"[+] Heatmap saved: {filepath}")
        return filepath
    
    def plot_comparison(self, grid_x: np.ndarray, grid_y: np.ndarray,
                        grid_z_list: list, titles: list,
                        filename: str = "heatmap_comparison.png",
                        cmap: str = "RdYlBu_r") -> str:
        """
        Generate comparison heatmaps (e.g., different power/k values).
        
        Args:
            grid_x: X coordinates of interpolation grid
            grid_y: Y coordinates of interpolation grid
            grid_z_list: List of interpolated grids to compare
            titles: List of titles for each subplot
            filename: Output filename
            cmap: Colormap
            
        Returns:
            Path to saved image file
        """
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        
        n_plots = len(grid_z_list)
        cols = min(3, n_plots)
        rows = (n_plots + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 5*rows))
        axes = axes.flatten() if n_plots > 1 else [axes]
        
        for i, (grid_z, title) in enumerate(zip(grid_z_list, titles)):
            ax = axes[i]
            contour = ax.contourf(grid_x, grid_y, grid_z, 
                                 levels=50, cmap=cmap, alpha=0.85)
            ax.set_title(title, fontsize=12)
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_aspect('equal')
            plt.colorbar(contour, ax=ax, label='dBm', shrink=0.8)
        
        # Hide unused subplots
        for i in range(n_plots, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        print(f"[+] Comparison heatmap saved: {filepath}")
        return filepath
