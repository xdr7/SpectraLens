"""
Data Collector Module
======================
Merekam posisi (x, y) dan kekuatan sinyal (RSSI) untuk pemetaan WiFi.
Mendukung input manual, file CSV, dan integrasi dengan WiFi scanner.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import csv
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json


class DataPoint:
    """
    Represents a single WiFi signal measurement at a specific position.
    
    Attributes:
        x (float): X coordinate in meters
        y (float): Y coordinate in meters
        rssi (int): Signal strength in dBm
        ssid (str): WiFi network name
        bssid (str): Access point MAC address
        timestamp (str): Time of measurement
        note (str): Optional note about this measurement
    """
    
    def __init__(self, x: float, y: float, rssi: int, 
                 ssid: str = "Unknown", bssid: str = "N/A",
                 timestamp: Optional[str] = None, note: str = ""):
        self.x = x
        self.y = y
        self.rssi = rssi
        self.ssid = ssid
        self.bssid = bssid
        self.timestamp = timestamp or datetime.now().isoformat()
        self.note = note
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'x': self.x,
            'y': self.y,
            'rssi': self.rssi,
            'ssid': self.ssid,
            'bssid': self.bssid,
            'timestamp': self.timestamp,
            'note': self.note
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DataPoint':
        """Create DataPoint from dictionary."""
        return cls(
            x=float(data['x']),
            y=float(data['y']),
            rssi=int(data['rssi']),
            ssid=data.get('ssid', 'Unknown'),
            bssid=data.get('bssid', 'N/A'),
            timestamp=data.get('timestamp'),
            note=data.get('note', '')
        )
    
    def __repr__(self) -> str:
        return f"DataPoint(x={self.x:.2f}, y={self.y:.2f}, rssi={self.rssi}, ssid={self.ssid})"


class DataCollector:
    """
    Collects and manages WiFi signal measurement data points.
    Supports multiple input methods and export formats.
    """
    
    def __init__(self):
        self.data_points: List[DataPoint] = []
        self.session_name: str = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_point(self, x: float, y: float, rssi: int, 
                  ssid: str = "Unknown", bssid: str = "N/A",
                  note: str = "") -> DataPoint:
        """
        Add a single measurement data point.
        
        Args:
            x: X coordinate in meters
            y: Y coordinate in meters
            rssi: Signal strength in dBm
            ssid: WiFi network name
            bssid: Access point MAC address
            note: Optional note
            
        Returns:
            The created DataPoint object
        """
        point = DataPoint(x, y, rssi, ssid, bssid, note=note)
        self.data_points.append(point)
        return point
    
    def add_points_batch(self, points: List[DataPoint]):
        """Add multiple data points at once."""
        self.data_points.extend(points)
    
    def load_from_csv(self, filepath: str) -> int:
        """
        Load measurement data from CSV file.
        
        Expected CSV columns: x, y, rssi (optional: ssid, bssid, note)
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Number of data points loaded
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        count = 0
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    point = DataPoint(
                        x=float(row['x']),
                        y=float(row['y']),
                        rssi=int(row['rssi']),
                        ssid=row.get('ssid', 'Unknown'),
                        bssid=row.get('bssid', 'N/A'),
                        note=row.get('note', '')
                    )
                    self.data_points.append(point)
                    count += 1
                except (KeyError, ValueError) as e:
                    print(f"[!] Skipping invalid row: {row} - {e}")
        
        return count
    
    def load_from_json(self, filepath: str) -> int:
        """
        Load measurement data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Number of data points loaded
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        points_data = data if isinstance(data, list) else data.get('points', [])
        
        count = 0
        for item in points_data:
            try:
                point = DataPoint.from_dict(item)
                self.data_points.append(point)
                count += 1
            except (KeyError, ValueError) as e:
                print(f"[!] Skipping invalid data point: {item} - {e}")
        
        return count
    
    def export_to_csv(self, filepath: str):
        """
        Export collected data to CSV file.
        
        Args:
            filepath: Output CSV file path
        """
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            fieldnames = ['x', 'y', 'rssi', 'ssid', 'bssid', 'timestamp', 'note']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for point in self.data_points:
                writer.writerow(point.to_dict())
        
        print(f"[+] Exported {len(self.data_points)} points to {filepath}")
    
    def export_to_json(self, filepath: str):
        """
        Export collected data to JSON file.
        
        Args:
            filepath: Output JSON file path
        """
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        output = {
            'session': self.session_name,
            'created': datetime.now().isoformat(),
            'total_points': len(self.data_points),
            'points': [p.to_dict() for p in self.data_points]
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"[+] Exported {len(self.data_points)} points to {filepath}")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about collected data.
        
        Returns:
            Dictionary with statistical information
        """
        if not self.data_points:
            return {'count': 0}
        
        rssi_values = [p.rssi for p in self.data_points]
        
        return {
            'count': len(self.data_points),
            'rssi_min': min(rssi_values),
            'rssi_max': max(rssi_values),
            'rssi_avg': sum(rssi_values) / len(rssi_values),
            'x_range': (min(p.x for p in self.data_points), max(p.x for p in self.data_points)),
            'y_range': (min(p.y for p in self.data_points), max(p.y for p in self.data_points)),
            'unique_ssids': list(set(p.ssid for p in self.data_points))
        }
    
    def clear(self):
        """Clear all collected data points."""
        self.data_points.clear()
    
    def get_points_for_interpolation(self) -> Tuple[List[Tuple[float, float]], List[int]]:
        """
        Get data formatted for interpolation algorithms.
        
        Returns:
            Tuple of (points list [(x,y),...], rssi values list)
        """
        points = [(p.x, p.y) for p in self.data_points]
        values = [p.rssi for p in self.data_points]
        return points, values
    
    def __len__(self) -> int:
        return len(self.data_points)
    
    def __iter__(self):
        return iter(self.data_points)
