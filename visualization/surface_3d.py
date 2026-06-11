"""
3D Surface Visualization Module
=================================
Membuat plot permukaan 3D dari data kekuatan sinyal WiFi menggunakan
Plotly (interaktif) dan Matplotlib (static).

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from typing import Optional, Tuple
import os


class Surface3D:
    """
    Generates 3D surface visualization of WiFi signal strength.
    
    Menampilkan "medan frekuensi" 3D yang menunjukkan area dengan
    sinyal terbaik (puncak) dan terburuk (lembah).
    
    Supports both interactive (Plotly HTML) and static (Matplotlib PNG) output.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (14, 10), dpi: int = 150):
        self.figsize = figsize
        self.dpi = dpi
        self.output_dir = "output"
    
    def plot(self, grid_x: np.ndarray, grid_y: np.ndarray, grid_z: np.ndarray,
             title: str = "WiFi Signal Strength - 3D Surface",
             filename: Optional[str] = None,
             elevation: int = 30, azimuth: int = -60,
             cmap: str = "RdYlBu_r") -> str:
        """
        Generate and save a static 3D surface plot using Matplotlib.
        
        Args:
            grid_x: X coordinates of interpolation grid
            grid_y: Y coordinates of interpolation grid
            grid_z: Interpolated values on grid
            title: Plot title
            filename: Output filename (auto-generated if None)
            elevation: Camera elevation angle
            azimuth: Camera azimuth angle
            cmap: Colormap
            
        Returns:
            Path to saved image file
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        if filename is None:
            filename = f"surface_3d_{grid_x.shape[0]}x{grid_x.shape[1]}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create figure with 3D projection
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot surface
        surf = ax.plot_surface(grid_x, grid_y, grid_z, 
                               cmap=cmap, alpha=0.9,
                               linewidth=0, antialiased=True,
                               edgecolor='none')
        
        # Add wireframe for structure
        # Use stride to reduce density
        stride = max(1, grid_x.shape[0] // 20)
        ax.plot_wireframe(grid_x, grid_y, grid_z, 
                         rstride=stride, cstride=stride,
                         color='gray', alpha=0.15, linewidth=0.3)
        
        # Labels and title
        ax.set_xlabel('X Position (meters)', labelpad=10)
        ax.set_ylabel('Y Position (meters)', labelpad=10)
        ax.set_zlabel('Signal Strength (dBm)', labelpad=10)
        ax.set_title(title, fontweight='bold', pad=20, fontsize=16)
        
        # Set viewing angle
        ax.view_init(elev=elevation, azim=azimuth)
        
        # Add colorbar
        cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=20, pad=0.1)
        cbar.set_label('Signal Strength (dBm)', fontsize=12)
        
        # Add statistics
        z_min, z_max = grid_z.min(), grid_z.max()
        stats_text = (f"Peak: {z_max:.0f} dBm\n"
                     f"Lowest: {z_min:.0f} dBm\n"
                     f"Range: {z_max - z_min:.0f} dB")
        ax.text2D(0.02, 0.98, stats_text, transform=ax.transAxes,
                 fontsize=9, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        print(f"[+] 3D Surface (static) saved: {filepath}")
        return filepath
    
    def plot_interactive(self, grid_x: np.ndarray, grid_y: np.ndarray, 
                         grid_z: np.ndarray,
                         title: str = "WiFi Signal Strength - 3D Surface",
                         filename: Optional[str] = None,
                         points: Optional[np.ndarray] = None,
                         values: Optional[np.ndarray] = None) -> str:
        """
        Generate and save an interactive 3D surface plot using Plotly.
        
        Args:
            grid_x: X coordinates of interpolation grid
            grid_y: Y coordinates of interpolation grid
            grid_z: Interpolated values on grid
            title: Plot title
            filename: Output HTML filename
            points: Original data points to overlay
            values: Original RSSI values
            
        Returns:
            Path to saved HTML file
        """
        try:
            import plotly.graph_objects as go
            import plotly.io as pio
        except ImportError:
            print("[!] Plotly not installed. Install with: pip install plotly")
            print("[!] Falling back to static 3D plot.")
            return self.plot(grid_x, grid_y, grid_z, title, filename)
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        if filename is None:
            filename = f"surface_3d_interactive_{grid_x.shape[0]}x{grid_x.shape[1]}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create 3D surface trace
        surface_trace = go.Surface(
            x=grid_x[0, :],  # Unique x values
            y=grid_y[:, 0],  # Unique y values
            z=grid_z,
            colorscale='RdYlBu_r',
            opacity=0.9,
            contours={
                "z": {"show": True, "usecolormap": True, 
                      "highlightcolor": "limegreen", "project": {"z": True}}
            },
            colorbar=dict(title="dBm", thickness=20),
            hovertemplate='X: %{x:.2f}m<br>Y: %{y:.2f}m<br>Signal: %{z:.0f} dBm<extra></extra>'
        )
        
        data = [surface_trace]
        
        # Add original data points as scatter3d
        if points is not None and values is not None:
            scatter_trace = go.Scatter3d(
                x=points[:, 0],
                y=points[:, 1],
                z=values,
                mode='markers+text',
                marker=dict(
                    size=8,
                    color=values,
                    colorscale='RdYlBu_r',
                    cmin=grid_z.min(),
                    cmax=grid_z.max(),
                    colorbar=dict(title="dBm"),
                    line=dict(color='black', width=1)
                ),
                text=[f'{v:.0f}' for v in values],
                textposition='top center',
                textfont=dict(size=10, color='black'),
                name='Measurements',
                hovertemplate='X: %{x:.2f}m<br>Y: %{y:.2f}m<br>RSSI: %{z:.0f} dBm<extra>Measurement</extra>'
            )
            data.append(scatter_trace)
        
        # Create layout
        layout = go.Layout(
            title=dict(text=title, font=dict(size=20)),
            scene=dict(
                xaxis=dict(title='X Position (meters)', 
                          backgroundcolor="rgb(230, 230, 230)",
                          gridcolor="white", showbackground=True),
                yaxis=dict(title='Y Position (meters)',
                          backgroundcolor="rgb(230, 230, 230)",
                          gridcolor="white", showbackground=True),
                zaxis=dict(title='Signal Strength (dBm)',
                          backgroundcolor="rgb(230, 230, 230)",
                          gridcolor="white", showbackground=True),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.7)
            ),
            hovermode='closest',
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Create figure and save
        fig = go.Figure(data=data, layout=layout)
        pio.write_html(fig, filepath, auto_open=False)
        
        print(f"[+] 3D Surface (interactive) saved: {filepath}")
        return filepath
    
    def plot_both(self, grid_x: np.ndarray, grid_y: np.ndarray, grid_z: np.ndarray,
                  title: str = "WiFi Signal Strength - 3D Surface",
                  points: Optional[np.ndarray] = None,
                  values: Optional[np.ndarray] = None) -> Tuple[str, str]:
        """
        Generate both static and interactive 3D plots.
        
        Returns:
            Tuple of (static_filepath, interactive_filepath)
        """
        static_path = self.plot(grid_x, grid_y, grid_z, title)
        interactive_path = self.plot_interactive(grid_x, grid_y, grid_z, title, 
                                                points=points, values=values)
        return static_path, interactive_path
