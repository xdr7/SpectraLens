"""
Real-time WiFi Signal Visualization
=====================================
Menampilkan visualisasi realtime dari hasil scan WiFi.
Menggunakan matplotlib untuk bar chart dan radar chart.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import List, Dict, Optional
import time


class RealtimeVisualizer:
    """
    Real-time WiFi signal visualizer.
    Menampilkan bar chart sinyal WiFi yang di-refresh secara periodik.
    """
    
    def __init__(self, interval: int = 3):
        """
        Initialize realtime visualizer.
        
        Args:
            interval: Refresh interval in seconds (default: 3)
        """
        self.interval = interval
        self.fig, (self.ax_bar, self.ax_radar) = plt.subplots(
            1, 2, figsize=(14, 6),
            gridspec_kw={'width_ratios': [2, 1]}
        )
        self.fig.suptitle('SpectraLens - WiFi Signal Realtime Monitor', 
                          fontsize=14, fontweight='bold')
        self.scanner = None
        self._running = True
        
        # Connect close event
        self.fig.canvas.mpl_connect('close_event', self._on_close)
    
    def _on_close(self, event):
        """Handle window close event."""
        self._running = False
    
    def _get_networks(self) -> List[Dict]:
        """Get networks from scanner."""
        if self.scanner is None:
            from scanner.wifi_scanner import WiFiScanner
            self.scanner = WiFiScanner()
        
        try:
            return self.scanner.scan()
        except Exception as e:
            print(f"[!] Scan error: {e}")
            return []
    
    def _update(self, frame):
        """Update animation frame."""
        networks = self._get_networks()
        
        if not networks:
            return self.ax_bar, self.ax_radar
        
        # Clear axes
        self.ax_bar.clear()
        self.ax_radar.clear()
        
        # --- Bar Chart ---
        ssids = [net['ssid'][:20] for net in networks]  # Truncate long names
        rssis = [net['rssi'] for net in networks]
        channels = [net['channel'] for net in networks]
        colors = self._get_signal_colors(rssis)
        
        bars = self.ax_bar.barh(range(len(ssids)), rssis, color=colors, edgecolor='white')
        self.ax_bar.set_yticks(range(len(ssids)))
        self.ax_bar.set_yticklabels(ssids, fontsize=9)
        self.ax_bar.set_xlabel('Signal Strength (dBm)', fontsize=10)
        self.ax_bar.set_title('WiFi Networks Signal Strength', fontsize=12, fontweight='bold')
        self.ax_bar.invert_yaxis()
        
        # Add value labels on bars
        for i, (rssi, ch) in enumerate(zip(rssis, channels)):
            label = f'{rssi} dBm | Ch {ch}'
            self.ax_bar.text(rssi + 0.5, i, label, va='center', fontsize=8)
        
        # Set x-axis limits
        min_rssi = min(rssis) - 10 if rssis else -100
        max_rssi = max(rssis) + 10 if rssis else -30
        self.ax_bar.set_xlim(min_rssi, max_rssi + 5)
        
        # Add grid
        self.ax_bar.grid(axis='x', alpha=0.3, linestyle='--')
        
        # --- Radar Chart (Channel Distribution) ---
        if channels:
            channel_counts = {}
            for ch in channels:
                if ch > 0:
                    channel_counts[ch] = channel_counts.get(ch, 0) + 1
            
            if channel_counts:
                ch_labels = list(channel_counts.keys())
                ch_values = list(channel_counts.values())
                
                # Create radar chart
                angles = np.linspace(0, 2 * np.pi, len(ch_labels), endpoint=False).tolist()
                ch_values += ch_values[:1]
                angles += angles[:1]
                ch_labels_str = [f'Ch {ch}' for ch in ch_labels]
                ch_labels_str += ch_labels_str[:1]
                
                self.ax_radar.plot(angles, ch_values, 'o-', linewidth=2, color='#00b4d8')
                self.ax_radar.fill(angles, ch_values, alpha=0.25, color='#00b4d8')
                self.ax_radar.set_xticks(angles[:-1])
                self.ax_radar.set_xticklabels(ch_labels_str, fontsize=8)
                self.ax_radar.set_title('Channel Distribution', fontsize=12, fontweight='bold')
                self.ax_radar.set_ylim(0, max(ch_values) + 1)
        
        # Add timestamp
        self.fig.text(0.5, 0.01, f'Last updated: {time.strftime("%H:%M:%S")}', 
                     ha='center', fontsize=9, style='italic')
        
        return self.ax_bar, self.ax_radar
    
    def _get_signal_colors(self, rssis: List[int]) -> List[str]:
        """Get colors based on signal strength."""
        colors = []
        for rssi in rssis:
            if rssi >= -50:
                colors.append('#00e676')  # Green - Excellent
            elif rssi >= -65:
                colors.append('#76ff03')  # Light green - Good
            elif rssi >= -75:
                colors.append('#ffea00')  # Yellow - Fair
            elif rssi >= -85:
                colors.append('#ff9100')  # Orange - Weak
            else:
                colors.append('#ff1744')  # Red - Very weak
        return colors
    
    def start(self):
        """Start realtime visualization."""
        print("[*] Starting realtime WiFi monitor...")
        print("[*] Close the window to stop.")
        print(f"[*] Refresh interval: {self.interval}s")
        print()
        
        ani = animation.FuncAnimation(
            self.fig, self._update, 
            interval=self.interval * 1000,
            blit=False,
            cache_frame_data=False
        )
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
        
        print("[*] Realtime monitor stopped.")


class SimpleBarVisualizer:
    """
    Simple terminal-based bar chart visualization.
    Tidak perlu GUI - langsung di terminal.
    """
    
    def __init__(self):
        self.scanner = None
    
    def _get_networks(self) -> List[Dict]:
        """Get networks from scanner."""
        if self.scanner is None:
            from scanner.wifi_scanner import WiFiScanner
            self.scanner = WiFiScanner()
        
        try:
            return self.scanner.scan()
        except Exception as e:
            print(f"[!] Scan error: {e}")
            return []
    
    def _signal_to_ascii(self, rssi: int, width: int = 30) -> str:
        """Convert RSSI to ASCII bar."""
        # RSSI range: -30 (strong) to -100 (weak)
        normalized = max(0, min(100, (rssi + 100) * 100 // 70))
        filled = int(normalized * width // 100)
        bar = '#' * filled + '-' * (width - filled)
        return bar
    
    def _signal_color(self, rssi: int) -> str:
        """Get ANSI color code for signal strength."""
        if rssi >= -50:
            return '\033[92m'  # Green
        elif rssi >= -65:
            return '\033[92m'  # Green
        elif rssi >= -75:
            return '\033[93m'  # Yellow
        elif rssi >= -85:
            return '\033[91m'  # Red
        else:
            return '\033[91m'  # Red
    
    def display(self, count: int = 1, interval: int = 3):
        """
        Display realtime bar chart in terminal.
        
        Args:
            count: Number of scans to perform (0 = infinite)
            interval: Seconds between scans
        """
        import time
        
        scan_count = 0
        try:
            while count == 0 or scan_count < count:
                scan_count += 1
                
                # Clear screen
                print('\033[2J\033[H', end='')
                
                # Print header
                print('\033[1;36m+------------------------------------------------------------+')
                print('|        SpectraLens - WiFi Signal Monitor (Realtime)       |')
                print('+------------------------------------------------------------+\033[0m')
                print()
                
                networks = self._get_networks()
                
                if not networks:
                    print('\033[93m[!] No WiFi networks found.\033[0m')
                else:
                    print(f'\033[92m[+] Found {len(networks)} networks:\033[0m')
                    print()
                    
                    for i, net in enumerate(networks, 1):
                        ssid = net['ssid'][:25].ljust(25)
                        rssi = net['rssi']
                        channel = net['channel']
                        bar = self._signal_to_ascii(rssi)
                        color = self._signal_color(rssi)
                        
                        print(f' {i:2d}. {ssid} {color}{bar}\033[0m {rssi:4d} dBm | Ch {channel}')
                    
                    print()
                    print(f' Scan #{scan_count} | {time.strftime("%H:%M:%S")} | Press Ctrl+C to stop')
                
                if count != 0 and scan_count >= count:
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print()
            print('\n[*] Monitor stopped.')
