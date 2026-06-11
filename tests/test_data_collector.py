"""
Tests for Data Collector Module
=================================
"""
import pytest
import os
import tempfile
import csv
import json
from scanner.data_collector import DataCollector, DataPoint


class TestDataPoint:
    """Test suite for DataPoint."""

    def test_init_basic(self):
        """Test basic DataPoint initialization."""
        dp = DataPoint(x=1.0, y=2.0, rssi=-50)
        assert dp.x == 1.0
        assert dp.y == 2.0
        assert dp.rssi == -50
        assert dp.ssid == "Unknown"
        assert dp.bssid == "N/A"
        assert dp.note == ""

    def test_init_with_all_params(self):
        """Test DataPoint with all parameters."""
        dp = DataPoint(x=1.0, y=2.0, rssi=-50,
                       ssid="TestWiFi", bssid="AA:BB:CC:DD:EE:FF",
                       note="Test point")
        assert dp.ssid == "TestWiFi"
        assert dp.bssid == "AA:BB:CC:DD:EE:FF"
        assert dp.note == "Test point"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        dp = DataPoint(x=1.0, y=2.0, rssi=-50, ssid="Test")
        d = dp.to_dict()
        assert d['x'] == 1.0
        assert d['y'] == 2.0
        assert d['rssi'] == -50
        assert d['ssid'] == "Test"
        assert 'timestamp' in d

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'x': 1.0, 'y': 2.0, 'rssi': -50,
            'ssid': 'Test', 'bssid': 'AA:BB:CC',
            'timestamp': '2024-01-01T00:00:00',
            'note': 'Test'
        }
        dp = DataPoint.from_dict(data)
        assert dp.x == 1.0
        assert dp.y == 2.0
        assert dp.rssi == -50
        assert dp.ssid == "Test"

    def test_from_dict_minimal(self):
        """Test creation from minimal dictionary."""
        data = {'x': 1.0, 'y': 2.0, 'rssi': -50}
        dp = DataPoint.from_dict(data)
        assert dp.ssid == "Unknown"
        assert dp.bssid == "N/A"

    def test_repr(self):
        """Test string representation."""
        dp = DataPoint(x=1.0, y=2.0, rssi=-50, ssid="Test")
        assert "DataPoint" in repr(dp)
        assert "Test" in repr(dp)


class TestDataCollector:
    """Test suite for DataCollector."""

    def test_init(self):
        """Test initialization."""
        dc = DataCollector()
        assert len(dc.data_points) == 0
        assert "session_" in dc.session_name

    def test_add_point(self):
        """Test adding a single point."""
        dc = DataCollector()
        dp = dc.add_point(x=1.0, y=2.0, rssi=-50)
        assert len(dc.data_points) == 1
        assert dp.x == 1.0
        assert dp.y == 2.0
        assert dp.rssi == -50

    def test_add_point_with_ssid(self):
        """Test adding point with SSID."""
        dc = DataCollector()
        dc.add_point(x=1.0, y=2.0, rssi=-50, ssid="MyWiFi")
        assert dc.data_points[0].ssid == "MyWiFi"

    def test_add_points_batch(self):
        """Test adding multiple points."""
        dc = DataCollector()
        points = [
            DataPoint(0, 0, -50),
            DataPoint(1, 0, -60),
            DataPoint(0, 1, -70),
        ]
        dc.add_points_batch(points)
        assert len(dc.data_points) == 3

    def test_clear(self):
        """Test clearing data."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)
        dc.add_point(1, 1, -60)
        assert len(dc.data_points) == 2
        dc.clear()
        assert len(dc.data_points) == 0

    def test_len(self):
        """Test __len__."""
        dc = DataCollector()
        assert len(dc) == 0
        dc.add_point(0, 0, -50)
        assert len(dc) == 1

    def test_iter(self):
        """Test iteration over data points."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)
        dc.add_point(1, 1, -60)
        points = list(dc)
        assert len(points) == 2

    def test_get_statistics_empty(self):
        """Test statistics with no data."""
        dc = DataCollector()
        stats = dc.get_statistics()
        assert stats['count'] == 0

    def test_get_statistics(self):
        """Test statistics calculation."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)
        dc.add_point(1, 0, -60)
        dc.add_point(0, 1, -70)

        stats = dc.get_statistics()
        assert stats['count'] == 3
        assert stats['rssi_min'] == -70
        assert stats['rssi_max'] == -50
        assert stats['rssi_avg'] == -60.0

    def test_get_points_for_interpolation(self):
        """Test getting points for interpolation."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)
        dc.add_point(1, 1, -60)

        points, values = dc.get_points_for_interpolation()
        assert len(points) == 2
        assert len(values) == 2
        assert points[0] == (0, 0)
        assert values[0] == -50

    def test_export_import_csv(self):
        """Test CSV export and import roundtrip."""
        dc = DataCollector()
        dc.add_point(0, 0, -50, ssid="Test1")
        dc.add_point(1, 1, -60, ssid="Test2")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name

        try:
            dc.export_to_csv(csv_path)

            # Import into new collector
            dc2 = DataCollector()
            count = dc2.load_from_csv(csv_path)
            assert count == 2
            assert dc2.data_points[0].x == 0
            assert dc2.data_points[0].rssi == -50
            assert dc2.data_points[1].ssid == "Test2"
        finally:
            os.unlink(csv_path)

    def test_export_import_json(self):
        """Test JSON export and import roundtrip."""
        dc = DataCollector()
        dc.add_point(0, 0, -50, ssid="Test1")
        dc.add_point(1, 1, -60, ssid="Test2")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        try:
            dc.export_to_json(json_path)

            # Import into new collector
            dc2 = DataCollector()
            count = dc2.load_from_json(json_path)
            assert count == 2
            assert dc2.data_points[0].x == 0
            assert dc2.data_points[0].rssi == -50
        finally:
            os.unlink(json_path)

    def test_load_csv_file_not_found(self):
        """Test loading non-existent CSV raises error."""
        dc = DataCollector()
        with pytest.raises(FileNotFoundError):
            dc.load_from_csv("nonexistent.csv")

    def test_load_json_file_not_found(self):
        """Test loading non-existent JSON raises error."""
        dc = DataCollector()
        with pytest.raises(FileNotFoundError):
            dc.load_from_json("nonexistent.json")

    def test_load_csv_invalid_rows(self):
        """Test loading CSV with invalid rows skips them."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("x,y,rssi\n")
            f.write("0,0,-50\n")
            f.write("invalid,data,-60\n")  # Invalid row
            f.write("1,1,-70\n")
            csv_path = f.name

        try:
            dc = DataCollector()
            count = dc.load_from_csv(csv_path)
            assert count == 2  # Only valid rows
        finally:
            os.unlink(csv_path)

    def test_export_creates_directory(self):
        """Test export creates directory if needed."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)

        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "nested", "test.csv")
            dc.export_to_csv(nested_path)
            assert os.path.exists(nested_path)
