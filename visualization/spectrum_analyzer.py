"""
Spectrum Analyzer Module
=========================
Visualisasi spektrum frekuensi WiFi dalam bentuk spectrum analyzer,
waterfall spectrogram, dan channel utilization chart.

Menampilkan pancaran WiFi dalam domain frekuensi (bukan spasial)
seperti spectrum analyzer sungguhan.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import List, Dict, Optional, Tuple
from collections import deque
import time
import os


class SpectrumAnalyzer:
    """
    Spectrum Analyzer untuk visualisasi frekuensi WiFi.
    
    Menampilkan:
    1. Channel Spectrum Bar Chart - kekuatan sinyal per channel
    2. Waterfall Spectrogram - perubahan sinyal dari waktu ke waktu
    3. Channel Utilization - persentase penggunaan channel
    4. Peak Detection - puncak-puncak sinyal tertinggi
    """
    
    # WiFi channel frequencies (2.4 GHz band)
    CHANNEL_2GHZ = {
        1: 2412, 2: 2417, 3: 2422, 4: 2427, 5: 2432,
        6: 2437, 7: 2442, 8: 2447, 9: 2452, 10: 2457,
        11: 2462, 12: 2467, 13: 2472, 14: 2484
    }
    
    # WiFi channel frequencies (5 GHz band)
    CHANNEL_5GHZ = {
        36: 5180, 40: 5200, 44: 5220, 48: 5240,
        52: 5260, 56: 5280, 60: 5300, 64: 5320,
        100: 5500, 104: 5520, 108: 5540, 112: 5560,
        116: 5580, 120: 5600, 124: 5620, 128: 5640,
        132: 5660, 136: 5680, 140: 5700, 144: 5720,
        149: 5745, 153: 5765, 157: 5785, 161: 5805, 165: 5825
    }
    
    # Channel overlap matrix for 2.4 GHz (which channels overlap)
    # Channel width ~22 MHz, spacing 5 MHz -> ~4 channels overlap
    CHANNEL_OVERLAP = {
        1: [1, 2, 3, 4, 5],
        2: [1, 2, 3, 4, 5, 6],
        3: [1, 2, 3, 4, 5, 6, 7],
        4: [2, 3, 4, 5, 6, 7, 8],
        5: [3, 4, 5, 6, 7, 8, 9],
        6: [4, 5, 6, 7, 8, 9, 10],
        7: [5, 6, 7, 8, 9, 10, 11],
        8: [6, 7, 8, 9, 10, 11, 12],
        9: [7, 8, 9, 10, 11, 12, 13],
        10: [8, 9, 10, 11, 12, 13],
        11: [9, 10, 11, 12, 13],
        12: [10, 11, 12, 13],
        13: [11, 12, 13],
        14: [14]
    }
    
    def __init__(self, max_history: int = 50, figsize: Tuple[int, int] = (14, 10), dpi: int = 120):
        """
        Initialize spectrum analyzer.
        
        Args:
            max_history: Maximum number of time steps to keep in waterfall history
            figsize: Figure size
            dpi: DPI for saved images
        """
        self.max_history = max_history
        self.figsize = figsize
        self.dpi = dpi
        self.output_dir = "output"
        
        # History buffers for waterfall
        self.timestamps: List[float] = []
        self.channel_history: Dict[int, deque] = {}  # channel -> deque of RSSI values
        self.ssid_history: Dict[str, deque] = {}  # ssid -> deque of RSSI values
        
        # Last scan data
        self.last_networks: List[Dict] = []
        self.last_scan_time: float = 0
        
        # Peak detection
        self.peak_threshold: float = -75  # dBm threshold for peak detection
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def update(self, networks: List[Dict]) -> None:
        """
        Update spectrum analyzer with new scan data.
        
        Args:
            networks: List of network dictionaries from WiFiScanner
        """
        current_time = time.time()
        self.last_networks = networks
        self.last_scan_time = current_time
        self.timestamps.append(current_time)
        
        # Trim history
        if len(self.timestamps) > self.max_history:
            self.timestamps = self.timestamps[-self.max_history:]
        
        # Update channel history
        channel_rssi = {}  # channel -> list of RSSI values
        for net in networks:
            ch = net.get('channel', 0)
            rssi = net.get('rssi', -100)
            ssid = net.get('ssid', 'Unknown')
            
            if ch > 0:
                if ch not in channel_rssi:
                    channel_rssi[ch] = []
                channel_rssi[ch].append(rssi)
            
            # Update SSID history
            if ssid not in self.ssid_history:
                self.ssid_history[ssid] = deque(maxlen=self.max_history)
            self.ssid_history[ssid].append(rssi)
        
        # Average RSSI per channel and update history
        for ch, rssis in channel_rssi.items():
            avg_rssi = np.mean(rssis)
            if ch not in self.channel_history:
                self.channel_history[ch] = deque(maxlen=self.max_history)
            self.channel_history[ch].append(avg_rssi)
        
        # Ensure all channels have same history length
        max_len = max(len(h) for h in self.channel_history.values()) if self.channel_history else 0
        for ch in self.channel_history:
            while len(self.channel_history[ch]) < max_len:
                self.channel_history[ch].append(-100)  # Fill with noise floor
    
    def plot_spectrum_bar(self, 
                          title: str = "WiFi Spectrum - Channel Analysis",
                          filename: Optional[str] = None,
                          show_peaks: bool = True,
                          show_overlap: bool = True) -> str:
        """
        Generate channel spectrum bar chart.
        Menampilkan kekuatan sinyal per channel WiFi seperti spectrum analyzer.
        
        Args:
            title: Plot title
            filename: Output filename
            show_peaks: Whether to mark peak signals
            show_overlap: Whether to show channel overlap regions
            
        Returns:
            Path to saved image file
        """
        if not self.last_networks:
            return ""
        
        os.makedirs(self.output_dir, exist_ok=True)
        if filename is None:
            filename = f"spectrum_bar_{len(self.last_networks)}nets.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Separate 2.4 GHz and 5 GHz networks
        networks_2ghz = [n for n in self.last_networks if n.get('channel', 0) <= 14]
        networks_5ghz = [n for n in self.last_networks if n.get('channel', 0) > 14]
        
        fig, axes = plt.subplots(2, 1, figsize=self.figsize, 
                                 gridspec_kw={'height_ratios': [1, 1]})
        
        # --- 2.4 GHz Band ---
        ax = axes[0]
        self._plot_band_spectrum(ax, networks_2ghz, self.CHANNEL_2GHZ, 
                                "2.4 GHz Band (Ch 1-14)", show_peaks, show_overlap)
        
        # --- 5 GHz Band ---
        ax = axes[1]
        self._plot_band_spectrum(ax, networks_5ghz, self.CHANNEL_5GHZ,
                                "5 GHz Band (Ch 36-165)", show_peaks, show_overlap)
        
        # Add timestamp and stats
        stats_text = (f"Total Networks: {len(self.last_networks)} | "
                     f"2.4 GHz: {len(networks_2ghz)} | 5 GHz: {len(networks_5ghz)} | "
                     f"Updated: {time.strftime('%H:%M:%S')}")
        fig.text(0.5, 0.01, stats_text, ha='center', fontsize=9, style='italic')
        
        plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def _plot_band_spectrum(self, ax, networks: List[Dict], 
                            channel_map: Dict[int, int],
                            band_title: str,
                            show_peaks: bool,
                            show_overlap: bool):
        """Plot spectrum for a single frequency band."""
        if not networks:
            ax.text(0.5, 0.5, f"No networks found in {band_title}",
                   ha='center', va='center', fontsize=12, color='#666',
                   transform=ax.transAxes)
            ax.set_title(band_title, fontsize=12, fontweight='bold')
            ax.set_xlabel('Channel')
            ax.set_ylabel('Signal Strength (dBm)')
            return
        
        # Group networks by channel
        channel_data: Dict[int, List[Dict]] = {}
        for net in networks:
            ch = net.get('channel', 0)
            if ch in channel_map:
                if ch not in channel_data:
                    channel_data[ch] = []
                channel_data[ch].append(net)
        
        if not channel_data:
            ax.text(0.5, 0.5, f"No mapped channels in {band_title}",
                   ha='center', va='center', fontsize=12, color='#666',
                   transform=ax.transAxes)
            ax.set_title(band_title, fontsize=12, fontweight='bold')
            return
        
        # Prepare data
        channels = sorted(channel_data.keys())
        ch_indices = list(range(len(channels)))
        rssi_values = []
        ssid_labels = []
        
        for ch in channels:
            nets = channel_data[ch]
            # Use strongest RSSI for this channel
            best_rssi = max(n.get('rssi', -100) for n in nets)
            rssi_values.append(best_rssi)
            # Create label with SSID
            ssids = [n.get('ssid', '?')[:12] for n in nets]
            ssid_labels.append(f"Ch {ch}\n" + "\n".join(ssids))
        
        # Plot bars with signal strength colors
        colors = self._get_spectrum_colors(rssi_values)
        bars = ax.bar(ch_indices, rssi_values, color=colors, 
                      edgecolor='white', linewidth=0.5, alpha=0.9)
        
        # Add channel labels
        ax.set_xticks(ch_indices)
        ax.set_xticklabels([f"Ch {ch}" for ch in channels], fontsize=8, rotation=45)
        
        # Add SSID labels on bars
        for i, (ch, rssi) in enumerate(zip(channels, rssi_values)):
            nets = channel_data[ch]
            ssid_text = "\n".join([n.get('ssid', '?')[:15] for n in nets])
            ax.text(i, rssi + 0.5, ssid_text, ha='center', va='bottom',
                   fontsize=6, color='#333', fontweight='bold')
        
        # Show channel overlap regions
        if show_overlap and channel_map == self.CHANNEL_2GHZ:
            self._draw_overlap_regions(ax, channels, ch_indices, rssi_values)
        
        # Peak detection
        if show_peaks:
            self._mark_peaks(ax, channels, ch_indices, rssi_values)
        
        # Add noise floor line
        ax.axhline(y=-90, color='red', linestyle='--', alpha=0.3, linewidth=0.5)
        ax.text(len(channels)-0.5, -90, 'Noise Floor (~-90 dBm)', 
               fontsize=7, color='red', alpha=0.5, ha='right', va='bottom')
        
        # Labels
        ax.set_title(band_title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Channel')
        ax.set_ylabel('Signal Strength (dBm)')
        ax.set_ylim(min(rssi_values) - 15, max(rssi_values) + 15)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#f8f9fa')
    
    def _draw_overlap_regions(self, ax, channels, ch_indices, rssi_values):
        """Draw shaded regions showing channel overlap."""
        max_rssi = max(rssi_values) if rssi_values else -30
        y_top = max_rssi + 10
        
        # Non-overlapping channels (1, 6, 11, 14) are recommended
        non_overlap = [1, 6, 11, 14]
        
        for i, ch in enumerate(channels):
            if ch in non_overlap:
                # Highlight recommended channels
                ax.axvspan(i - 0.4, i + 0.4, alpha=0.1, color='green')
                ax.text(i, y_top, '✓', ha='center', va='bottom', 
                       fontsize=14, color='green', fontweight='bold')
    
    def _mark_peaks(self, ax, channels, ch_indices, rssi_values):
        """Mark peak signals on the spectrum."""
        if len(rssi_values) < 2:
            return
        
        # Simple peak detection: local maxima above threshold
        for i in range(1, len(rssi_values) - 1):
            if (rssi_values[i] > rssi_values[i-1] and 
                rssi_values[i] > rssi_values[i+1] and
                rssi_values[i] > self.peak_threshold):
                ax.plot(i, rssi_values[i], 'v', color='red', markersize=10, zorder=5)
                ax.text(i, rssi_values[i] + 3, f'PEAK\n{rssi_values[i]:.0f} dBm',
                       ha='center', va='bottom', fontsize=7, color='red',
                       fontweight='bold')
    
    def plot_waterfall(self,
                       title: str = "WiFi Spectrum Waterfall",
                       filename: Optional[str] = None,
                       band: str = "2.4ghz") -> str:
        """
        Generate waterfall spectrogram.
        Menampilkan perubahan sinyal dari waktu ke waktu.
        Sumbu X = channel/frekuensi, Sumbu Y = waktu, Warna = kekuatan sinyal.
        
        Args:
            title: Plot title
            filename: Output filename
            band: '2.4ghz' or '5ghz'
            
        Returns:
            Path to saved image file
        """
        if not self.channel_history:
            return ""
        
        os.makedirs(self.output_dir, exist_ok=True)
        if filename is None:
            filename = f"waterfall_{band}_{len(self.timestamps)}steps.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Filter channels by band
        if band == "2.4ghz":
            channels = sorted([ch for ch in self.channel_history.keys() if ch <= 14])
            channel_map = self.CHANNEL_2GHZ
        else:
            channels = sorted([ch for ch in self.channel_history.keys() if ch > 14])
            channel_map = self.CHANNEL_5GHZ
        
        if not channels:
            return ""
        
        # Build waterfall matrix
        # Rows = time steps, Columns = channels
        n_times = min(len(self.timestamps), 
                      max(len(self.channel_history[ch]) for ch in channels))
        n_channels = len(channels)
        
        waterfall = np.full((n_times, n_channels), -100.0)  # Fill with noise floor
        
        for t in range(n_times):
            for j, ch in enumerate(channels):
                history = list(self.channel_history[ch])
                if t < len(history):
                    waterfall[t, j] = history[-(t+1)]  # Most recent first
        
        # Create figure
        fig = plt.figure(figsize=self.figsize)
        
        # Main waterfall plot
        ax_waterfall = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        
        im = ax_waterfall.imshow(waterfall, aspect='auto', cmap='inferno',
                                 interpolation='bilinear',
                                 extent=[0, n_channels, n_times, 0],
                                 vmin=-100, vmax=-30)
        
        # Channel labels
        ax_waterfall.set_xticks(range(n_channels))
        ax_waterfall.set_xticklabels([f"Ch {ch}" for ch in channels], 
                                     fontsize=7, rotation=45)
        ax_waterfall.set_ylabel('Time Steps (most recent at top)', fontsize=10)
        ax_waterfall.set_title(f'Waterfall Spectrogram - {band.upper()}', 
                              fontsize=12, fontweight='bold')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax_waterfall, shrink=0.8, pad=0.02)
        cbar.set_label('Signal Strength (dBm)', fontsize=9)
        
        # Average signal profile at bottom
        ax_profile = plt.subplot2grid((3, 1), (2, 0))
        avg_signals = np.mean(waterfall, axis=0)
        
        colors = self._get_spectrum_colors(avg_signals.tolist())
        ax_profile.bar(range(n_channels), avg_signals, color=colors, 
                      edgecolor='white', linewidth=0.5, alpha=0.9)
        ax_profile.set_xticks(range(n_channels))
        ax_profile.set_xticklabels([f"Ch {ch}" for ch in channels], 
                                   fontsize=7, rotation=45)
        ax_profile.set_ylabel('Avg Signal (dBm)', fontsize=10)
        ax_profile.set_xlabel('Channel', fontsize=10)
        ax_profile.grid(axis='y', alpha=0.3, linestyle='--')
        ax_profile.set_facecolor('#f8f9fa')
        
        # Add timestamp
        fig.text(0.5, 0.01, f'Last updated: {time.strftime("%H:%M:%S")} | '
                           f'History: {n_times} scans', 
                ha='center', fontsize=9, style='italic')
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def plot_channel_utilization(self,
                                 title: str = "Channel Utilization Analysis",
                                 filename: Optional[str] = None) -> str:
        """
        Generate channel utilization chart.
        Menampilkan persentase penggunaan channel dan tingkat interferensi.
        
        Args:
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved image file
        """
        if not self.last_networks:
            return ""
        
        os.makedirs(self.output_dir, exist_ok=True)
        if filename is None:
            filename = f"channel_util_{len(self.last_networks)}nets.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Count networks per channel
        channel_counts = {}
        channel_rssi = {}
        for net in self.last_networks:
            ch = net.get('channel', 0)
            rssi = net.get('rssi', -100)
            if ch > 0:
                channel_counts[ch] = channel_counts.get(ch, 0) + 1
                if ch not in channel_rssi:
                    channel_rssi[ch] = []
                channel_rssi[ch].append(rssi)
        
        if not channel_counts:
            return ""
        
        channels = sorted(channel_counts.keys())
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # --- Channel Count Bar Chart ---
        counts = [channel_counts[ch] for ch in channels]
        colors = plt.cm.RdYlBu_r([c / max(counts) for c in counts])
        
        bars = ax1.bar(range(len(channels)), counts, color=colors, 
                      edgecolor='white', linewidth=0.5)
        ax1.set_xticks(range(len(channels)))
        ax1.set_xticklabels([f"Ch {ch}" for ch in channels], fontsize=9, rotation=45)
        ax1.set_ylabel('Number of Networks', fontsize=11)
        ax1.set_title('Networks per Channel', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add count labels
        for i, count in enumerate(counts):
            ax1.text(i, count + 0.1, str(count), ha='center', va='bottom', fontsize=10)
        
        # --- Interference Score ---
        # Calculate interference based on channel overlap
        interference_scores = []
        for ch in channels:
            score = 0
            if ch in self.CHANNEL_OVERLAP:
                overlapping = self.CHANNEL_OVERLAP[ch]
                for overlap_ch in overlapping:
                    score += channel_counts.get(overlap_ch, 0)
            interference_scores.append(score)
        
        colors2 = plt.cm.Reds([s / max(interference_scores) for s in interference_scores])
        
        ax2.bar(range(len(channels)), interference_scores, color=colors2,
               edgecolor='white', linewidth=0.5)
        ax2.set_xticks(range(len(channels)))
        ax2.set_xticklabels([f"Ch {ch}" for ch in channels], fontsize=9, rotation=45)
        ax2.set_ylabel('Interference Score', fontsize=11)
        ax2.set_title('Channel Interference (Overlap Weighted)', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Highlight recommended channels (1, 6, 11)
        for i, ch in enumerate(channels):
            if ch in [1, 6, 11]:
                ax2.text(i, interference_scores[i] + 0.3, '★', 
                        ha='center', fontsize=14, color='green')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def plot_polar_pattern(self,
                           title: str = "AP Signal Coverage Pattern",
                           filename: Optional[str] = None) -> str:
        """
        Generate polar/radar chart of signal coverage.
        Menampilkan pola pancaran sinyal dalam bentuk polar.
        
        Args:
            title: Plot title
            filename: Output filename
            
        Returns:
            Path to saved image file
        """
        if not self.last_networks:
            return ""
        
        os.makedirs(self.output_dir, exist_ok=True)
        if filename is None:
            filename = f"polar_pattern_{len(self.last_networks)}nets.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Take top 8 networks for readability
        top_nets = sorted(self.last_networks, 
                         key=lambda x: x.get('rssi', -100), 
                         reverse=True)[:8]
        
        n_nets = len(top_nets)
        if n_nets == 0:
            return ""
        
        # Create polar plot
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw={'projection': 'polar'})
        
        angles = np.linspace(0, 2 * np.pi, n_nets, endpoint=False).tolist()
        angles += angles[:1]  # Close the circle
        
        for i, net in enumerate(top_nets):
            rssi = net.get('rssi', -100)
            ssid = net.get('ssid', 'Unknown')[:15]
            ch = net.get('channel', 0)
            
            # Normalize RSSI from [-100, -30] to [0, 1]
            normalized = max(0.1, min(1.0, (rssi + 100) / 70))
            
            # Create a "petal" for each AP
            theta = [angles[i], angles[i] + 0.3, angles[i] + 0.6]
            radii = [0, normalized, 0]
            
            color = self._rssi_to_hex(rssi)
            ax.fill(theta, radii, alpha=0.4, color=color)
            ax.plot(theta, radii, color=color, linewidth=2)
            
            # Add label
            label_angle = angles[i] + 0.3
            ax.text(label_angle, normalized + 0.1, f"{ssid}\n{rssi} dBm\nCh {ch}",
                   ha='center', fontsize=8, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        ax.set_ylim(0, 1.3)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_facecolor('#f8f9fa')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)
        
        return filepath
    
    def get_statistics(self) -> Dict:
        """
        Get spectrum statistics.
        
        Returns:
            Dictionary with spectrum statistics
        """
        if not self.last_networks:
            return {}
        
        rssis = [n.get('rssi', -100) for n in self.last_networks]
        channels = [n.get('channel', 0) for n in self.last_networks if n.get('channel', 0) > 0]
        
        stats = {
            'total_networks': len(self.last_networks),
            'avg_rssi': np.mean(rssis),
            'min_rssi': min(rssis),
            'max_rssi': max(rssis),
            'std_rssi': np.std(rssis),
            'unique_channels': len(set(channels)),
            'channels_2ghz': len([c for c in channels if c <= 14]),
            'channels_5ghz': len([c for c in channels if c > 14]),
            'strongest_ssid': max(self.last_networks, key=lambda x: x.get('rssi', -100)).get('ssid', 'N/A'),
            'strongest_rssi': max(rssis),
            'weakest_ssid': min(self.last_networks, key=lambda x: x.get('rssi', -100)).get('ssid', 'N/A'),
            'weakest_rssi': min(rssis),
        }
        
        # Recommended channel
        if channels:
            channel_counts = {}
            for ch in channels:
                channel_counts[ch] = channel_counts.get(ch, 0) + 1
            
            # Find least used non-overlapping channel
            non_overlap = [1, 6, 11]
            best_ch = min(non_overlap, key=lambda ch: channel_counts.get(ch, 0))
            stats['recommended_channel'] = best_ch
            stats['recommended_channel_usage'] = channel_counts.get(best_ch, 0)
        
        return stats
    
    def _get_spectrum_colors(self, rssi_values: List[float]) -> List[str]:
        """Get colors for spectrum bars based on signal strength."""
        colors = []
        for rssi in rssi_values:
            if rssi >= -50:
                colors.append('#d32f2f')  # Red - Very strong
            elif rssi >= -60:
                colors.append('#f57c00')  # Orange - Strong
            elif rssi >= -70:
                colors.append('#fbc02d')  # Yellow - Good
            elif rssi >= -80:
                colors.append('#7cb342')  # Light green - Fair
            else:
                colors.append('#1565c0')  # Blue - Weak
        return colors
    
    def _rssi_to_hex(self, rssi: float) -> str:
        """Convert RSSI to hex color."""
        if rssi >= -50:
            return '#d32f2f'
        elif rssi >= -60:
            return '#f57c00'
        elif rssi >= -70:
            return '#fbc02d'
        elif rssi >= -80:
            return '#7cb342'
        else:
            return '#1565c0'
    
    def get_channel_frequency(self, channel: int) -> int:
        """Get frequency in MHz for a given channel."""
        if channel in self.CHANNEL_2GHZ:
            return self.CHANNEL_2GHZ[channel]
        elif channel in self.CHANNEL_5GHZ:
            return self.CHANNEL_5GHZ[channel]
        return 0
    
    def get_frequency_band(self, channel: int) -> str:
        """Get frequency band name for a channel."""
        if channel <= 14:
            return "2.4 GHz"
        elif channel <= 165:
            return "5 GHz"
        return "Unknown"
    
    def reset_history(self):
        """Reset all history buffers."""
        self.timestamps = []
        self.channel_history = {}
        self.ssid_history = {}
