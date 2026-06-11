"""
Integration Tests for SpectraLens
===================================
Tests the full pipeline: data collection → interpolation → visualization.
"""
import pytest
import numpy as np
import os
import tempfile
from interpolation.idw import IDWInterpolator
from interpolation.grid_builder import GridBuilder
from scanner.data_collector import DataCollector
from storage.database import Database


class TestDataToInterpolationPipeline:
    """Test pipeline from data collection to interpolation."""

    def test_collect_to_interpolate(self):
        """Test collecting data and interpolating."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)
        dc.add_point(2, 0, -60)
        dc.add_point(0, 2, -70)
        dc.add_point(2, 2, -80)
        dc.add_point(1, 1, -65)

        points, values = dc.get_points_for_interpolation()
        points_array = np.array(points)
        values_array = np.array(values)

        interp = IDWInterpolator(power=2, k=3)
        interp.fit(points_array, values_array)

        gb = GridBuilder(points_array)
        grid_x, grid_y = gb.create_grid(resolution=10)

        result = interp.interpolate(grid_x, grid_y)
        assert result.shape == (10, 10)
        assert not np.any(np.isnan(result))
        assert np.all(result >= -100) and np.all(result <= -30)

    def test_collect_to_interpolate_single_point(self):
        """Test pipeline with single data point."""
        dc = DataCollector()
        dc.add_point(0, 0, -50)

        points, values = dc.get_points_for_interpolation()
        interp = IDWInterpolator()
        interp.fit(np.array(points), np.array(values))

        result = interp.interpolate_point(0, 0)
        assert abs(result - (-50)) < 1.0

    def test_multiple_ssid_collection(self):
        """Test collecting data with multiple SSIDs."""
        dc = DataCollector()
        dc.add_point(0, 0, -50, ssid="WiFi-2.4G")
        dc.add_point(1, 1, -60, ssid="WiFi-5G")
        dc.add_point(2, 2, -70, ssid="WiFi-2.4G")

        stats = dc.get_statistics()
        assert stats['count'] == 3
        assert stats['rssi_avg'] == -60.0


class TestDatabaseToInterpolationPipeline:
    """Test pipeline from database to interpolation."""

    @pytest.fixture
    def db_with_data(self):
        """Create database with sample data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        db = Database(db_path)
        session_id = db.create_session(
            name="Integration Test",
            ssid="TestWiFi",
            room_name="Test Room"
        )

        points_data = [
            {'x': 0, 'y': 0, 'rssi': -50},
            {'x': 2, 'y': 0, 'rssi': -60},
            {'x': 0, 'y': 2, 'rssi': -70},
            {'x': 2, 'y': 2, 'rssi': -80},
            {'x': 1, 'y': 1, 'rssi': -65},
        ]
        db.add_data_points_batch(session_id, points_data)

        yield db, session_id

        db.close()
        os.unlink(db_path)

    def test_db_to_interpolation(self, db_with_data):
        """Test loading from DB and interpolating."""
        db, session_id = db_with_data

        x, y, rssi = db.get_data_points_as_arrays(session_id)
        points = np.column_stack([x, y])
        values = np.array(rssi)

        interp = IDWInterpolator(power=2, k=3)
        interp.fit(points, values)

        gb = GridBuilder(points)
        grid_x, grid_y = gb.create_grid(resolution=20)

        result = interp.interpolate(grid_x, grid_y)
        assert result.shape == (20, 20)
        assert not np.any(np.isnan(result))

    def test_db_statistics_and_interpolation(self, db_with_data):
        """Test DB statistics match interpolation input."""
        db, session_id = db_with_data

        stats = db.get_session_statistics(session_id)
        assert stats['total_points'] == 5

        x, y, rssi = db.get_data_points_as_arrays(session_id)
        assert len(x) == stats['total_points']
        assert min(rssi) == stats['rssi_min']
        assert max(rssi) == stats['rssi_max']


class TestFullPipeline:
    """Test complete SpectraLens pipeline."""

    def test_full_pipeline(self):
        """Test complete pipeline: collect → save → load → interpolate."""
        # Step 1: Collect data
        dc = DataCollector()
        dc.add_point(0, 0, -50, ssid="TestNet")
        dc.add_point(1, 0, -60, ssid="TestNet")
        dc.add_point(0, 1, -70, ssid="TestNet")
        dc.add_point(1, 1, -80, ssid="TestNet")

        assert len(dc) == 4

        # Step 2: Save to database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            db = Database(db_path)
            session_id = db.create_session(
                name="Full Pipeline Test",
                ssid="TestNet"
            )

            points_for_db = [
                {'x': p.x, 'y': p.y, 'rssi': p.rssi, 'ssid': p.ssid}
                for p in dc.data_points
            ]
            db.add_data_points_batch(session_id, points_for_db)

            # Step 3: Load from database
            x, y, rssi = db.get_data_points_as_arrays(session_id)
            assert len(x) == 4

            # Step 4: Interpolate
            points = np.column_stack([x, y])
            values = np.array(rssi)

            interp = IDWInterpolator(power=2, k=3)
            interp.fit(points, values)

            gb = GridBuilder(points)
            grid_x, grid_y = gb.create_grid(resolution=15)

            result = interp.interpolate(grid_x, grid_y)
            assert result.shape == (15, 15)
            assert not np.any(np.isnan(result))

            # Step 5: Verify interpolation quality
            # At known points, interpolation should be close to original
            for i in range(len(points)):
                px, py = points[i]
                expected = values[i]
                actual = interp.interpolate_point(px, py)
                assert abs(actual - expected) < 1.0

        finally:
            db.close()
            os.unlink(db_path)

    def test_pipeline_with_csv_export_import(self):
        """Test pipeline with CSV export/import."""
        # Collect data
        dc1 = DataCollector()
        dc1.add_point(0, 0, -50)
        dc1.add_point(1, 1, -60)

        # Export to CSV
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_path = f.name

        try:
            dc1.export_to_csv(csv_path)

            # Import into new collector
            dc2 = DataCollector()
            dc2.load_from_csv(csv_path)
            assert len(dc2) == 2

            # Interpolate from imported data
            points, values = dc2.get_points_for_interpolation()
            interp = IDWInterpolator()
            interp.fit(np.array(points), np.array(values))

            result = interp.interpolate_point(0.5, 0.5)
            assert not np.isnan(result)
            assert np.isfinite(result)

        finally:
            os.unlink(csv_path)
