"""
WiFi Scanner Module
====================
Membaca RSSI dari adapter WiFi menggunakan pywifiscan.
Mendeteksi jaringan WiFi di sekitar dan mengembalikan data sinyal.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import sys
import platform
from typing import List, Dict, Optional


class WiFiScanner:
    """
    WiFi scanner that detects nearby networks and reads RSSI values.
    
    Uses pywifiscan library which works on Windows, Linux, and macOS.
    Falls back to platform-specific commands if pywifiscan is not available.
    """
    
    def __init__(self):
        self.os_name = platform.system().lower()
        self._scanner = None
        self._initialize_scanner()
    
    def _initialize_scanner(self):
        """Initialize the appropriate WiFi scanner backend."""
        try:
            # Try pywifiscan first (cross-platform)
            from pywifiscan import WiFiScan
            self._scanner = WiFiScan()
            self._backend = "pywifiscan"
        except ImportError:
            # Fallback: try platform-specific methods
            self._backend = self._detect_fallback()
    
    def _detect_fallback(self) -> str:
        """Detect available fallback scanning method based on OS."""
        if self.os_name == 'windows':
            # Try using Windows Native Wifi API via subprocess
            try:
                import subprocess
                result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return "netsh"
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        elif self.os_name == 'linux':
            try:
                import subprocess
                result = subprocess.run(['iwlist', 'scan'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return "iwlist"
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        elif self.os_name == 'darwin':  # macOS
            try:
                import subprocess
                result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return "airport"
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        
        return "none"
    
    def scan(self) -> List[Dict]:
        """
        Scan for WiFi networks and return list of networks with signal data.
        
        Returns:
            List of dictionaries containing:
                - ssid (str): Network name
                - bssid (str): MAC address of access point
                - rssi (int): Signal strength in dBm
                - channel (int): WiFi channel
                - frequency (int): Frequency in MHz
        """
        if self._backend == "pywifiscan":
            return self._scan_pywifiscan()
        elif self._backend == "netsh":
            return self._scan_netsh()
        elif self._backend == "iwlist":
            return self._scan_iwlist()
        elif self._backend == "airport":
            return self._scan_airport()
        else:
            print("[!] No WiFi scanner backend available.")
            print("[!] Install pywifiscan: pip install pywifiscan")
            return []
    
    def _scan_pywifiscan(self) -> List[Dict]:
        """Scan using pywifiscan library."""
        networks = []
        try:
            results = self._scanner.scan()
            for net in results:
                networks.append({
                    'ssid': net.get('ssid', 'Hidden Network'),
                    'bssid': net.get('bssid', 'N/A'),
                    'rssi': net.get('rssi', 0),
                    'channel': net.get('channel', 0),
                    'frequency': self._channel_to_freq(net.get('channel', 0))
                })
        except Exception as e:
            print(f"[!] pywifiscan scan error: {e}")
        
        # Sort by signal strength (strongest first)
        networks.sort(key=lambda x: x['rssi'], reverse=True)
        return networks
    
    def _scan_netsh(self) -> List[Dict]:
        """Scan using Windows netsh command."""
        import subprocess
        import re
        
        networks = []
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode != 0:
                return networks
            
            output = result.stdout
            
            # Parse netsh output
            current_ssid = None
            current_bssid = 'N/A'
            current_channel = 0
            current_signal = None
            
            for line in output.split('\n'):
                line = line.strip()
                
                ssid_match = re.match(r'^SSID\s+\d+\s*:\s*(.+)$', line)
                if ssid_match:
                    current_ssid = ssid_match.group(1).strip()
                    current_bssid = 'N/A'
                    current_channel = 0
                    current_signal = None
                    continue
                
                bssid_match = re.match(r'^BSSID\s+\d+\s*:\s*(.+)$', line)
                if bssid_match and current_ssid:
                    current_bssid = bssid_match.group(1).strip()
                    continue
                
                signal_match = re.match(r'^Signal\s*:\s*(\d+)%', line)
                if signal_match and current_ssid:
                    percent = int(signal_match.group(1))
                    current_signal = self._percent_to_dbm(percent)
                    continue
                
                channel_match = re.match(r'^Channel\s*:\s*(\d+)', line)
                if channel_match and current_ssid:
                    current_channel = int(channel_match.group(1))
                    continue
                
                # Check for "Other rates" line (indicates end of BSSID block)
                other_rates_match = re.match(r'^Other rates', line)
                if other_rates_match and current_ssid and current_signal is not None:
                    networks.append({
                        'ssid': current_ssid,
                        'bssid': current_bssid,
                        'rssi': current_signal,
                        'channel': current_channel,
                        'frequency': self._channel_to_freq(current_channel)
                    })
                    current_signal = None  # Reset for next BSSID
                    
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"[!] netsh scan error: {e}")
        
        # Remove duplicates by SSID (keep strongest signal)
        seen = {}
        for net in networks:
            ssid = net['ssid']
            if ssid not in seen or net['rssi'] > seen[ssid]['rssi']:
                seen[ssid] = net
        
        networks = list(seen.values())
        networks.sort(key=lambda x: x['rssi'], reverse=True)
        return networks
    
    def _scan_iwlist(self) -> List[Dict]:
        """Scan using Linux iwlist command."""
        import subprocess
        import re
        
        networks = []
        try:
            result = subprocess.run(
                ['iwlist', 'scan'],
                capture_output=True, text=True, timeout=15, 
                # May need sudo
            )
            
            if result.returncode != 0:
                return networks
            
            output = result.stdout
            current_cell = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'ESSID:' in line:
                    essid_match = re.search(r'ESSID:"(.+)"', line)
                    current_cell['ssid'] = essid_match.group(1) if essid_match else 'Hidden'
                
                elif 'Address:' in line:
                    addr_match = re.search(r'Address:\s*([0-9A-Fa-f:]+)', line)
                    if addr_match:
                        current_cell['bssid'] = addr_match.group(1)
                
                elif 'Signal level=' in line:
                    signal_match = re.search(r'Signal level=(-?\d+)', line)
                    if signal_match:
                        current_cell['rssi'] = int(signal_match.group(1))
                
                elif 'Channel:' in line:
                    ch_match = re.search(r'Channel:(\d+)', line)
                    if ch_match:
                        current_cell['channel'] = int(ch_match.group(1))
                
                elif line.startswith('Cell ') or line == '':
                    if current_cell.get('ssid'):
                        current_cell.setdefault('rssi', -100)
                        current_cell.setdefault('channel', 0)
                        current_cell.setdefault('bssid', 'N/A')
                        current_cell['frequency'] = self._channel_to_freq(current_cell['channel'])
                        networks.append(current_cell.copy())
                    current_cell = {}
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"[!] iwlist scan error: {e}")
        
        networks.sort(key=lambda x: x['rssi'], reverse=True)
        return networks
    
    def _scan_airport(self) -> List[Dict]:
        """Scan using macOS airport command."""
        import subprocess
        import re
        
        networks = []
        try:
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode != 0:
                return networks
            
            output = result.stdout
            lines = output.strip().split('\n')
            
            if len(lines) < 2:
                return networks
            
            # Parse airport output (SSID, BSSID, RSSI, CHANNEL, HT, CC, SECURITY)
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 3:
                    # RSSI is typically the third column
                    try:
                        rssi = int(parts[2])
                        networks.append({
                            'ssid': parts[0],
                            'bssid': parts[1] if len(parts) > 1 else 'N/A',
                            'rssi': rssi,
                            'channel': int(parts[3]) if len(parts) > 3 else 0,
                            'frequency': 0
                        })
                    except ValueError:
                        continue
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"[!] airport scan error: {e}")
        
        networks.sort(key=lambda x: x['rssi'], reverse=True)
        return networks
    
    @staticmethod
    def _channel_to_freq(channel: int) -> int:
        """Convert WiFi channel to frequency in MHz."""
        if 1 <= channel <= 14:
            return 2412 + (channel - 1) * 5
        elif 36 <= channel <= 165:
            return 5180 + (channel - 36) * 5
        return 0
    
    @staticmethod
    def _percent_to_dbm(percent: int) -> int:
        """Convert signal percentage to approximate dBm value."""
        # Rough conversion: 0% = -100dBm, 100% = -30dBm
        return int(-100 + (percent * 0.7))
    
    def get_backend_name(self) -> str:
        """Get the name of the active scanning backend."""
        backends = {
            "pywifiscan": "pywifiscan (cross-platform)",
            "netsh": "Windows netsh",
            "iwlist": "Linux iwlist",
            "airport": "macOS airport",
            "none": "No backend available"
        }
        return backends.get(self._backend, "Unknown")
