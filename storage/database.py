"""
Database Module
================
Operasi SQLite untuk menyimpan dan memuat data pengukuran WiFi.
Menyediakan penyimpanan persisten untuk session, titik data, dan metadata.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json


class Database:
    """
    SQLite database manager for SpectraLens measurement data.
    
    Menyediakan operasi CRUD untuk:
    - Session pengukuran
    - Titik data (x, y, rssi)
    - Metadata dan konfigurasi
    """
    
    def __init__(self, db_path: str = "data/spectralens.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        self.conn.execute("PRAGMA foreign_keys=ON")
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ssid TEXT,
                bssid TEXT,
                description TEXT,
                room_name TEXT DEFAULT 'Unknown Room',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Data points table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                rssi INTEGER NOT NULL,
                ssid TEXT,
                bssid TEXT,
                frequency INTEGER,
                channel INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                note TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        
        # Interpolation parameters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interpolation_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                power REAL DEFAULT 2.0,
                k_neighbors INTEGER DEFAULT 5,
                smoothing REAL DEFAULT 1e-12,
                grid_resolution INTEGER DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_data_points_session 
            ON data_points(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_data_points_coords 
            ON data_points(x, y)
        """)
        
        self.conn.commit()
    
    # --- Session Operations ---
    
    def create_session(self, name: str, ssid: str = "Unknown", 
                       bssid: str = "N/A", description: str = "",
                       room_name: str = "Unknown Room") -> int:
        """
        Create a new measurement session.
        
        Returns:
            Session ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (name, ssid, bssid, description, room_name)
            VALUES (?, ?, ?, ?, ?)
        """, (name, ssid, bssid, description, room_name))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_session(self, session_id: int) -> Optional[Dict]:
        """Get session by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_sessions(self, active_only: bool = True) -> List[Dict]:
        """Get all sessions."""
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM sessions WHERE is_active = 1 ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_session(self, session_id: int, **kwargs):
        """Update session fields."""
        allowed_fields = {'name', 'ssid', 'bssid', 'description', 'room_name', 'is_active'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [session_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE sessions SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
    
    def delete_session(self, session_id: int):
        """Delete session and all its data points."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM data_points WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM interpolation_params WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        self.conn.commit()
    
    # --- Data Points Operations ---
    
    def add_data_point(self, session_id: int, x: float, y: float, rssi: int,
                       ssid: str = None, bssid: str = None,
                       frequency: int = None, channel: int = None,
                       note: str = "") -> int:
        """
        Add a data point to a session.
        
        Returns:
            Data point ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO data_points (session_id, x, y, rssi, ssid, bssid, frequency, channel, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, x, y, rssi, ssid, bssid, frequency, channel, note))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_data_points_batch(self, session_id: int, points: List[Dict]):
        """
        Add multiple data points efficiently.
        
        Args:
            session_id: Session ID
            points: List of dicts with keys: x, y, rssi (optional: ssid, bssid, note)
        """
        cursor = self.conn.cursor()
        data = []
        for p in points:
            data.append((
                session_id,
                p['x'], p['y'], p['rssi'],
                p.get('ssid'), p.get('bssid'),
                p.get('frequency'), p.get('channel'),
                p.get('note', '')
            ))
        
        cursor.executemany("""
            INSERT INTO data_points (session_id, x, y, rssi, ssid, bssid, frequency, channel, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        self.conn.commit()
    
    def get_data_points(self, session_id: int) -> List[Dict]:
        """Get all data points for a session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM data_points 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_data_points_as_arrays(self, session_id: int) -> Tuple[List[float], List[float], List[int]]:
        """
        Get data points as separate arrays for interpolation.
        
        Returns:
            Tuple of (x_list, y_list, rssi_list)
        """
        points = self.get_data_points(session_id)
        x = [p['x'] for p in points]
        y = [p['y'] for p in points]
        rssi = [p['rssi'] for p in points]
        return x, y, rssi
    
    def delete_data_points(self, session_id: int):
        """Delete all data points for a session."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM data_points WHERE session_id = ?", (session_id,))
        self.conn.commit()
    
    # --- Interpolation Parameters ---
    
    def save_interpolation_params(self, session_id: int, power: float = 2.0,
                                   k_neighbors: int = 5, smoothing: float = 1e-12,
                                   grid_resolution: int = 50):
        """Save interpolation parameters for a session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO interpolation_params 
            (session_id, power, k_neighbors, smoothing, grid_resolution)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, power, k_neighbors, smoothing, grid_resolution))
        self.conn.commit()
    
    def get_interpolation_params(self, session_id: int) -> Optional[Dict]:
        """Get interpolation parameters for a session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM interpolation_params WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # --- Statistics ---
    
    def get_session_statistics(self, session_id: int) -> Dict:
        """Get statistics for a session."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_points,
                MIN(rssi) as rssi_min,
                MAX(rssi) as rssi_max,
                AVG(rssi) as rssi_avg,
                MIN(x) as x_min,
                MAX(x) as x_max,
                MIN(y) as y_min,
                MAX(y) as y_max
            FROM data_points WHERE session_id = ?
        """, (session_id,))
        
        stats = dict(cursor.fetchone())
        
        if stats['total_points'] and stats['total_points'] > 0:
            stats['area_m2'] = (stats['x_max'] - stats['x_min']) * \
                              (stats['y_max'] - stats['y_min'])
        
        return stats
    
    def get_all_statistics(self) -> Dict:
        """Get overall database statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total_sessions FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as total_points FROM data_points")
        total_points = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT ssid) as unique_ssids FROM data_points")
        unique_ssids = cursor.fetchone()[0]
        
        return {
            'total_sessions': total_sessions,
            'total_points': total_points,
            'unique_ssids': unique_ssids,
            'database_path': self.db_path,
            'database_size_mb': self._get_db_size()
        }
    
    def _get_db_size(self) -> float:
        """Get database file size in MB."""
        try:
            return os.path.getsize(self.db_path) / (1024 * 1024)
        except OSError:
            return 0.0
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
