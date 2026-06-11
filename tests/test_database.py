"""
Tests for Database Module
===========================
"""
import pytest
import os
import tempfile
from storage.database import Database


class TestDatabase:
    """Test suite for Database."""

    @pytest.fixture
    def db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        db = Database(db_path)
        yield db
        db.close()
        os.unlink(db_path)

    def test_init(self, db):
        """Test database initialization."""
        assert os.path.exists(db.db_path)
        # Verify tables exist
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'sessions' in tables
        assert 'data_points' in tables
        assert 'interpolation_params' in tables

    # --- Session Tests ---

    def test_create_session(self, db):
        """Test creating a session."""
        session_id = db.create_session(
            name="Test Session",
            ssid="TestWiFi",
            bssid="AA:BB:CC:DD:EE:FF",
            description="Test description",
            room_name="Lab 1"
        )
        assert session_id > 0

    def test_get_session(self, db):
        """Test getting a session by ID."""
        session_id = db.create_session(name="Test Session")
        session = db.get_session(session_id)
        assert session is not None
        assert session['name'] == "Test Session"
        assert session['is_active'] == 1

    def test_get_session_not_found(self, db):
        """Test getting non-existent session."""
        session = db.get_session(9999)
        assert session is None

    def test_get_all_sessions(self, db):
        """Test getting all sessions."""
        db.create_session(name="Session 1")
        db.create_session(name="Session 2")
        sessions = db.get_all_sessions()
        assert len(sessions) >= 2

    def test_get_all_sessions_inactive(self, db):
        """Test getting inactive sessions."""
        s1 = db.create_session(name="Active Session")
        s2 = db.create_session(name="Inactive Session")
        db.update_session(s2, is_active=False)

        active = db.get_all_sessions(active_only=True)
        all_sessions = db.get_all_sessions(active_only=False)

        assert len(active) < len(all_sessions)

    def test_update_session(self, db):
        """Test updating a session."""
        session_id = db.create_session(name="Original")
        db.update_session(session_id, name="Updated", room_name="New Room")
        session = db.get_session(session_id)
        assert session['name'] == "Updated"
        assert session['room_name'] == "New Room"

    def test_delete_session(self, db):
        """Test deleting a session."""
        session_id = db.create_session(name="To Delete")
        db.add_data_point(session_id, 0, 0, -50)
        db.delete_session(session_id)
        assert db.get_session(session_id) is None
        # Data points should be cascade deleted
        points = db.get_data_points(session_id)
        assert len(points) == 0

    # --- Data Points Tests ---

    def test_add_data_point(self, db):
        """Test adding a data point."""
        session_id = db.create_session(name="Test")
        point_id = db.add_data_point(
            session_id, x=1.0, y=2.0, rssi=-50,
            ssid="TestWiFi", bssid="AA:BB:CC",
            frequency=2412, channel=6
        )
        assert point_id > 0

    def test_add_data_points_batch(self, db):
        """Test batch adding data points."""
        session_id = db.create_session(name="Test")
        points = [
            {'x': 0, 'y': 0, 'rssi': -50, 'ssid': 'WiFi1'},
            {'x': 1, 'y': 0, 'rssi': -60, 'ssid': 'WiFi1'},
            {'x': 0, 'y': 1, 'rssi': -70, 'ssid': 'WiFi2'},
        ]
        db.add_data_points_batch(session_id, points)
        retrieved = db.get_data_points(session_id)
        assert len(retrieved) == 3

    def test_get_data_points(self, db):
        """Test retrieving data points."""
        session_id = db.create_session(name="Test")
        db.add_data_point(session_id, 0, 0, -50)
        db.add_data_point(session_id, 1, 1, -60)

        points = db.get_data_points(session_id)
        assert len(points) == 2
        assert points[0]['rssi'] == -50

    def test_get_data_points_as_arrays(self, db):
        """Test getting data points as arrays."""
        session_id = db.create_session(name="Test")
        db.add_data_point(session_id, 0, 0, -50)
        db.add_data_point(session_id, 1, 1, -60)

        x, y, rssi = db.get_data_points_as_arrays(session_id)
        assert len(x) == 2
        assert len(y) == 2
        assert len(rssi) == 2
        assert rssi == [-50, -60]

    def test_delete_data_points(self, db):
        """Test deleting data points for a session."""
        session_id = db.create_session(name="Test")
        db.add_data_point(session_id, 0, 0, -50)
        db.add_data_point(session_id, 1, 1, -60)

        db.delete_data_points(session_id)
        points = db.get_data_points(session_id)
        assert len(points) == 0

    # --- Interpolation Params Tests ---

    def test_save_interpolation_params(self, db):
        """Test saving interpolation parameters."""
        session_id = db.create_session(name="Test")
        db.save_interpolation_params(
            session_id, power=3.0, k_neighbors=10,
            smoothing=1e-10, grid_resolution=100
        )
        params = db.get_interpolation_params(session_id)
        assert params is not None
        assert params['power'] == 3.0
        assert params['k_neighbors'] == 10

    def test_get_interpolation_params_not_found(self, db):
        """Test getting interpolation params for session without them."""
        session_id = db.create_session(name="Test")
        params = db.get_interpolation_params(session_id)
        assert params is None

    # --- Statistics Tests ---

    def test_get_session_statistics(self, db):
        """Test session statistics."""
        session_id = db.create_session(name="Test")
        db.add_data_point(session_id, 0, 0, -50)
        db.add_data_point(session_id, 1, 0, -60)
        db.add_data_point(session_id, 0, 1, -70)

        stats = db.get_session_statistics(session_id)
        assert stats['total_points'] == 3
        assert stats['rssi_min'] == -70
        assert stats['rssi_max'] == -50
        assert stats['rssi_avg'] == -60.0

    def test_get_session_statistics_empty(self, db):
        """Test statistics for session with no data."""
        session_id = db.create_session(name="Empty")
        stats = db.get_session_statistics(session_id)
        assert stats['total_points'] == 0

    def test_get_all_statistics(self, db):
        """Test overall database statistics."""
        s1 = db.create_session(name="Session 1")
        s2 = db.create_session(name="Session 2")
        db.add_data_point(s1, 0, 0, -50)
        db.add_data_point(s2, 1, 1, -60)

        stats = db.get_all_statistics()
        assert stats['total_sessions'] >= 2
        assert stats['total_points'] >= 2

    def test_context_manager(self):
        """Test database context manager."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            with Database(db_path) as db:
                session_id = db.create_session(name="Context Test")
                assert session_id > 0
            # Connection should be closed after context
        finally:
            os.unlink(db_path)

    def test_multiple_sessions(self, db):
        """Test multiple sessions don't interfere."""
        s1 = db.create_session(name="Session 1")
        s2 = db.create_session(name="Session 2")

        db.add_data_point(s1, 0, 0, -50)
        db.add_data_point(s2, 1, 1, -60)

        p1 = db.get_data_points(s1)
        p2 = db.get_data_points(s2)

        assert len(p1) == 1
        assert len(p2) == 1
        assert p1[0]['rssi'] == -50
        assert p2[0]['rssi'] == -60
