"""
Signal Propagation Module
==========================
Model propagasi sinyal WiFi dan visualisasi gradient vectors.
Mengimplementasikan model matematis untuk prediksi redaman sinyal.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List, Dict
import os


class SignalPropagation:
    """
    Model propagasi sinyal WiFi dan visualisasi.
    
    Models:
    1. Free Space Path Loss (FSPL)
    2. Log-Distance Path Loss Model
    3. Two-Ray Ground Reflection
    4. ITU Indoor Propagation Model
    """
    
    def __init__(self, figsize: Tuple[int, int] = (14, 10), dpi: int = 120):
        self.figsize = figsize
        self.dpi = dpi
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    @staticmethod
    def free_space_path_loss(freq_mhz: float, distance_m: float) -> float:
        """
        Free Space Path Loss (FSPL) model.
        
        FSPL(dB) = 20*log10(d) + 20*log10(f) + 32.44
        
        Args:
            freq_mhz: Frequency in MHz (e.g., 2412 for ch1)
            distance_m: Distance in meters
            
        Returns:
            Path loss in dB
        """
        if distance_m <= 0:
            return 0
        return 20 * np.log10(distance_m) + 20 * np.log10(freq_mhz) + 32.44
    
    @staticmethod
    def log_distance_path_loss(distance_m: float, 
                               distance_ref: float = 1.0,
                               path_loss_exponent: float = 3.0,
                               ref_loss: float = 40.0) -> float:
        """
        Log-Distance Path Loss Model.
        
        PL(d) = PL(d0) + 10 * n * log10(d/d0) + X_sigma
        
        Args:
            distance_m: Distance in meters
            distance_ref: Reference distance (default: 1m)
            path_loss_exponent: Path loss exponent (n)
                - 2.0: Free space
                - 2.5: Urban area (line of sight)
                - 3.0: Urban area (non-line of sight)
                - 3.5: Indoor (obstructed)
                - 4.0: Indoor (heavy obstruction)
            ref_loss: Path loss at reference distance (dB)
            
        Returns:
            Path loss in dB
        """
        if distance_m <= 0:
            return ref_loss
        return ref_loss + 10 * path_loss_exponent * np.log10(distance_m / distance_ref)
    
    @staticmethod
    def itu_indoor_path_loss(distance_m: float, 
                             freq_mhz: float,
                             floors: int = 1,
                             loss_per_floor: float = 15.0) -> float:
        """
        ITU Indoor Propagation Model.
        
        L = 20*log10(f) + N*log10(d) + Lf(n) - 28
        
        Args:
            distance_m: Distance in meters
            freq_mhz: Frequency in MHz
            floors: Number of floors penetrated
            loss_per_floor: Loss per floor in dB
            
        Returns:
            Path loss in dB
        """
        if distance_m <= 0:
            distance_m = 0.1
        
        # N factor based on frequency
        if freq_mhz < 2000:
            N = 28  # For 900 MHz
        elif freq_mhz < 5000:
            N = 30  # For 2.4 GHz
        else:
            N = 32  # For 5 GHz
        
        # Floor penetration loss
        floor_loss = floors * loss_per_floor if floors > 0 else 0
        
        return 20 * np.log10(freq_mhz) + N * np.log10(distance_m) + floor_loss - 28
    
    @staticmethod
    def two_ray_path_loss(distance_m: float, 
                          freq_mhz: float,
                          tx_height: float = 2.0,
                          rx_height: float = 1.0) -> float:
        """
        Two-Ray Ground Reflection Model.
        
        Args:
            distance_m: Distance in meters
            freq_mhz: Frequency in MHz
            tx_height: Transmitter height in meters (default: 2m)
            rx_height: Receiver height in meters (default: 1m)
            
        Returns:
            Path loss in dB
        """
        if distance_m <= 0:
            distance_m = 0.1
        
        c = 3e8  # Speed of light
        wavelength = c / (freq_mhz * 1e6)
        
        # Critical distance
        d_critical = (4 * tx_height * rx_height) / wavelength
        
        if distance_m < d_critical:
            # Free space path loss
            return SignalPropagation.free_space_path_loss(freq_mhz, distance_m)
        else:
            # Two-ray model
            return 40 * np.log10(distance_m) - (
                20 * np.log10(tx_height) + 
                20 * np.log10(rx_height)
            )
    
    def plot_path_loss_curves(self,
                              freq_mhz: float = 2412,
                              max_distance: float = 100,
                              title: str = "Signal Propagation Models Comparison",
                              filename: Optional[str] = None) -> str:
        """
        Plot comparison of different path loss models.
        
        Args:
            freq_mhz: Frequency in MHz
            max_distance: Maximum distance in meters
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved image file
        """
        if filename is None:
            filename = f"path_loss_comparison_{freq_mhz}mhz.png"
        filepath = os.path.join(self.output_dir, filename)
        
        distances = np.linspace(1, max_distance, 200)
        
        # Calculate path losses
        fspl = [self.free_space_path_loss(freq_mhz, d) for d in distances]
        log_dist_free = [self.log_distance_path_loss(d, path_loss_exponent=2.0) for d in distances]
        log_dist_urban = [self.log_distance_path_loss(d, path_loss_exponent=3.0) for d in distances]
        log_dist_indoor = [self.log_distance_path_loss(d, path_loss_exponent=3.5) for d in distances]
        itu = [self.itu_indoor_path_loss(d, freq_mhz) for d in distances]
        two_ray = [self.two_ray_path_loss(d, freq_mhz) for d in distances]
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.plot(distances, fspl, '-', label='Free Space (FSPL)', linewidth=2, alpha=0.8)
        ax.plot(distances, log_dist_free, '--', label='Log-Distance (n=2.0, Free Space)', linewidth=2)
        ax.plot(distances, log_dist_urban, '-.', label='Log-Distance (n=3.0, Urban)', linewidth=2)
        ax.plot(distances, log_dist_indoor, ':', label='Log-Distance (n=3.5, Indoor)', linewidth=2)
        ax.plot(distances, itu, '-', label=f'ITU Indoor ({freq_mhz/1000:.1f} GHz)', linewidth=2, alpha=0.7)
        ax.plot(distances, two_ray, '--', label='Two-Ray Ground', linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Distance (meters)', fontsize=12)
        ax.set_ylabel('Path Loss (dB)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='lower right')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#f8f9fa')
        
        # Add annotation
        ax.text(0.98, 0.02, f'Frequency: {freq_mhz} MHz ({freq_mhz/1000:.1f} GHz)',
               transform=ax.transAxes, ha='right', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def plot_gradient_vectors(self,
                              grid_x: np.ndarray,
                              grid_y: np.ndarray,
                              grid_z: np.ndarray,
                              points: Optional[np.ndarray] = None,
                              values: Optional[np.ndarray] = None,
                              title: str = "Signal Gradient Vectors",
                              filename: Optional[str] = None,
                              stride: int = 3) -> str:
        """
        Plot gradient vectors showing direction of signal change.
        Menampilkan panah-panah yang menunjukkan arah gradient sinyal
        (ke mana sinyal menguat/melemah).
        
        Args:
            grid_x: X coordinates of interpolation grid
            grid_y: Y coordinates of interpolation grid
            grid_z: Interpolated values on grid
            points: Original data points
            values: Original RSSI values
            title: Plot title
            filename: Output filename
            stride: Subsampling stride for gradient vectors
            
        Returns:
            Path to saved image file
        """
        if filename is None:
            filename = f"gradient_vectors_{grid_x.shape[0]}x{grid_x.shape[1]}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate gradient
        dy, dx = np.gradient(grid_z)
        
        # Magnitude of gradient
        magnitude = np.sqrt(dx**2 + dy**2)
        
        # Subsample for cleaner visualization
        subsample_x = grid_x[::stride, ::stride]
        subsample_y = grid_y[::stride, ::stride]
        subsample_dx = dx[::stride, ::stride]
        subsample_dy = dy[::stride, ::stride]
        subsample_mag = magnitude[::stride, ::stride]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # --- Left: Heatmap with gradient vectors ---
        contour = ax1.contourf(grid_x, grid_y, grid_z, levels=50, 
                               cmap='RdYlBu_r', alpha=0.85)
        ax1.contour(grid_x, grid_y, grid_z, levels=10, 
                    colors='black', linewidths=0.3, alpha=0.2)
        
        # Plot gradient vectors as quiver
        q = ax1.quiver(subsample_x, subsample_y, 
                       subsample_dx, subsample_dy,
                       subsample_mag,
                       cmap='viridis', scale=50, width=0.003,
                       alpha=0.8, pivot='mid')
        
        plt.colorbar(contour, ax=ax1, label='Signal Strength (dBm)', shrink=0.8)
        
        # Overlay original points
        if points is not None:
            ax1.scatter(points[:, 0], points[:, 1], 
                       c=values, cmap='RdYlBu_r',
                       edgecolors='black', linewidth=1, s=60, zorder=5)
        
        ax1.set_xlabel('X Position (meters)')
        ax1.set_ylabel('Y Position (meters)')
        ax1.set_title('Signal Gradient Map\n(Arrows show direction of increasing signal)', 
                     fontsize=12, fontweight='bold')
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.2, linestyle='--')
        
        # --- Right: Gradient magnitude heatmap ---
        im = ax2.imshow(magnitude, extent=[grid_x.min(), grid_x.max(),
                                           grid_y.min(), grid_y.max()],
                       origin='lower', cmap='hot', aspect='equal')
        plt.colorbar(im, ax=ax2, label='Gradient Magnitude', shrink=0.8)
        
        # Contour lines on gradient
        ax2.contour(grid_x, grid_y, magnitude, levels=10, 
                    colors='white', linewidths=0.5, alpha=0.3)
        
        ax2.set_xlabel('X Position (meters)')
        ax2.set_ylabel('Y Position (meters)')
        ax2.set_title('Gradient Magnitude\n(Bright = rapid signal change)', 
                     fontsize=12, fontweight='bold')
        
        # Add statistics
        stats_text = (f"Max Gradient: {magnitude.max():.2f} dB/m\n"
                     f"Mean Gradient: {magnitude.mean():.2f} dB/m\n"
                     f"Signal Range: {grid_z.max() - grid_z.min():.0f} dB")
        fig.text(0.5, 0.01, stats_text, ha='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def plot_coverage_prediction(self,
                                 ap_position: Tuple[float, float],
                                 grid_x: np.ndarray,
                                 grid_y: np.ndarray,
                                 tx_power_dbm: float = 20,
                                 freq_mhz: float = 2412,
                                 antenna_gain: float = 2.0,
                                 rx_sensitivity: float = -85,
                                 title: str = "WiFi Coverage Prediction",
                                 filename: Optional[str] = None) -> str:
        """
        Plot predicted coverage area based on path loss model.
        Menampilkan area coverage yang diprediksi berdasarkan model propagasi.
        
        Args:
            ap_position: (x, y) position of access point
            grid_x: X coordinates grid
            grid_y: Y coordinates grid
            tx_power_dbm: Transmitter power in dBm (default: 20 dBm = 100mW)
            freq_mhz: Frequency in MHz
            antenna_gain: Antenna gain in dBi
            rx_sensitivity: Receiver sensitivity in dBm (default: -85 dBm)
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved image file
        """
        if filename is None:
            filename = f"coverage_prediction_{freq_mhz}mhz.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate distance from AP for each grid point
        distances = np.sqrt((grid_x - ap_position[0])**2 + (grid_y - ap_position[1])**2)
        
        # Calculate received signal strength
        # RSSI = TxPower + AntennaGain - PathLoss
        predicted_rssi = np.zeros_like(distances)
        
        for i in range(distances.shape[0]):
            for j in range(distances.shape[1]):
                d = distances[i, j]
                if d > 0:
                    path_loss = self.log_distance_path_loss(d, path_loss_exponent=3.0)
                    predicted_rssi[i, j] = tx_power_dbm + antenna_gain - path_loss
                else:
                    predicted_rssi[i, j] = tx_power_dbm + antenna_gain
        
        # Clip to reasonable range
        predicted_rssi = np.clip(predicted_rssi, -100, -20)
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot predicted coverage
        contour = ax.contourf(grid_x, grid_y, predicted_rssi, levels=50,
                              cmap='RdYlBu_r', alpha=0.85)
        
        # Add contour lines at key thresholds
        thresholds = [-80, -70, -60, -50]
        cs = ax.contour(grid_x, grid_y, predicted_rssi, 
                       levels=thresholds, colors='black', linewidths=0.5, alpha=0.3)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%.0f dBm')
        
        # Mark AP position
        ax.plot(ap_position[0], ap_position[1], '^', color='red', 
               markersize=15, zorder=10, label=f'AP ({tx_power_dbm} dBm)')
        
        # Draw coverage rings
        for radius, color, label in [(10, '#00e676', '10m'), 
                                     (25, '#ffea00', '25m'),
                                     (50, '#ff9100', '50m')]:
            circle = plt.Circle(ap_position, radius, fill=False, 
                              color=color, linestyle='--', linewidth=1.5, alpha=0.7)
            ax.add_patch(circle)
            # Find RSSI at this distance
            d = radius
            if d > 0:
                pl = self.log_distance_path_loss(d, path_loss_exponent=3.0)
                rssi_at_dist = tx_power_dbm + antenna_gain - pl
                ax.text(ap_position[0] + radius, ap_position[1], 
                       f'{radius}m (~{rssi_at_dist:.0f} dBm)',
                       fontsize=8, color=color, fontweight='bold',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        # Colorbar
        cbar = plt.colorbar(contour, ax=ax, label='Predicted RSSI (dBm)', shrink=0.8)
        
        # Highlight coverage boundary (where RSSI = rx_sensitivity)
        cs2 = ax.contour(grid_x, grid_y, predicted_rssi, 
                        levels=[rx_sensitivity], 
                        colors='red', linewidths=2, linestyles='--')
        ax.clabel(cs2, inline=True, fontsize=10, fmt=[f'Coverage Edge ({rx_sensitivity} dBm)'])
        
        ax.set_xlabel('X Position (meters)')
        ax.set_ylabel('Y Position (meters)')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.legend(fontsize=10)
        
        # Add info box
        info_text = (f"TX Power: {tx_power_dbm} dBm\n"
                    f"Antenna Gain: {antenna_gain} dBi\n"
                    f"Frequency: {freq_mhz/1000:.1f} GHz\n"
                    f"RX Sensitivity: {rx_sensitivity} dBm\n"
                    f"Model: Log-Distance (n=3.0)")
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def plot_multi_ap_overlay(self,
                              grid_x: np.ndarray,
                              grid_y: np.ndarray,
                              ap_positions: List[Tuple[float, float]],
                              ap_names: List[str],
                              ap_powers: List[float],
                              freq_mhz: float = 2412,
                              title: str = "Multi-AP Signal Overlay",
                              filename: Optional[str] = None) -> str:
        """
        Plot multiple access points overlaid on same map.
        Menampilkan beberapa AP sekaligus dengan warna berbeda.
        
        Args:
            grid_x: X coordinates grid
            grid_y: Y coordinates grid
            ap_positions: List of (x, y) positions for each AP
            ap_names: List of AP names/SSIDs
            ap_powers: List of TX powers in dBm for each AP
            freq_mhz: Frequency in MHz
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved image file
        """
        if filename is None:
            filename = f"multi_ap_overlay_{len(ap_positions)}aps.png"
        filepath = os.path.join(self.output_dir, filename)
        
        n_aps = len(ap_positions)
        colors = plt.cm.tab10(np.linspace(0, 1, n_aps))
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Calculate and plot coverage for each AP
        for i, (pos, name, power) in enumerate(zip(ap_positions, ap_names, ap_powers)):
            distances = np.sqrt((grid_x - pos[0])**2 + (grid_y - pos[1])**2)
            predicted = np.zeros_like(distances)
            
            for ii in range(distances.shape[0]):
                for jj in range(distances.shape[1]):
                    d = distances[ii, jj]
                    if d > 0:
                        pl = self.log_distance_path_loss(d, path_loss_exponent=3.0)
                        predicted[ii, jj] = power + 2.0 - pl
                    else:
                        predicted[ii, jj] = power + 2.0
            
            predicted = np.clip(predicted, -100, -20)
            
            # Plot contour for this AP
            ax.contour(grid_x, grid_y, predicted, levels=[-80, -70, -60, -50],
                      colors=[colors[i]], linewidths=1, alpha=0.5)
            
            # Mark AP position
            ax.plot(pos[0], pos[1], 'o', color=colors[i], 
                   markersize=12, zorder=10, label=f'{name} ({power} dBm)')
            
            # Add AP name label
            ax.text(pos[0], pos[1] + 2, name, ha='center', fontsize=9,
                   fontweight='bold', color=colors[i],
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('X Position (meters)')
        ax.set_ylabel('Y Position (meters)')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.legend(fontsize=9, loc='upper right')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def estimate_signal_at_point(self, 
                                 ap_position: Tuple[float, float],
                                 point: Tuple[float, float],
                                 tx_power_dbm: float = 20,
                                 freq_mhz: float = 2412,
                                 antenna_gain: float = 2.0,
                                 model: str = 'log_distance') -> Dict:
        """
        Estimate signal strength at a given point from an AP.
        
        Args:
            ap_position: (x, y) position of AP
            point: (x, y) position to estimate
            tx_power_dbm: Transmitter power in dBm
            freq_mhz: Frequency in MHz
            antenna_gain: Antenna gain in dBi
            model: Path loss model ('fspl', 'log_distance', 'itu', 'two_ray')
            
        Returns:
            Dictionary with estimation results
        """
        distance = np.sqrt((point[0] - ap_position[0])**2 + 
                          (point[1] - ap_position[1])**2)
        
        if distance <= 0:
            return {
                'distance_m': 0,
                'path_loss_db': 0,
                'estimated_rssi': tx_power_dbm + antenna_gain,
                'model': model
            }
        
        if model == 'fspl':
            path_loss = self.free_space_path_loss(freq_mhz, distance)
        elif model == 'itu':
            path_loss = self.itu_indoor_path_loss(distance, freq_mhz)
        elif model == 'two_ray':
            path_loss = self.two_ray_path_loss(distance, freq_mhz)
        else:  # log_distance
            path_loss = self.log_distance_path_loss(distance)
        
        estimated_rssi = tx_power_dbm + antenna_gain - path_loss
        
        return {
            'distance_m': distance,
            'path_loss_db': path_loss,
            'estimated_rssi': estimated_rssi,
            'model': model,
            'signal_quality': self._rssi_to_quality(estimated_rssi)
        }
    
    @staticmethod
    def _rssi_to_quality(rssi: float) -> str:
        """Convert RSSI to quality description."""
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
