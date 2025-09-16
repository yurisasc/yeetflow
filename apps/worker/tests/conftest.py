import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Add the parent directory to Python path so we can import the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.constants import API_V1_PREFIX
from app.db import seed_test_data


# Set up any test-wide fixtures here if needed


class BaseTestClass:
    """Base test class with common utilities for API testing."""

    API_PREFIX = API_V1_PREFIX

    def setup_method(self):
        """Set up test client before each test."""
        # Use a temporary database file for each test to avoid locking issues
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db.name}'
        
        # Seed test data
        seed_test_data()
        
        # Mock the Steel service using the common utility
        self.steel_patcher = mock_steel_service()
        self.client = TestClient(app)

    def teardown_method(self):
        """Clean up after each test."""
        self.steel_patcher.stop()
        # Clean up temporary database file
        try:
            os.unlink(self.temp_db.name)
        except (OSError, FileNotFoundError):
            pass


def mock_steel_service():
    """Mock the Steel service to avoid hitting API limits during tests."""
    mock_session_data = {
        "id": "test-session-123",
        "createdAt": "2025-09-16T02:11:28.027Z",
        "status": "live",
        "sessionViewerUrl": "https://app.steel.dev/sessions/test-session-123",
        "websocketUrl": "wss://api.steel.dev/sessions/test-session-123/ws",
        "debugUrl": "https://debug.steel.dev/sessions/test-session-123",
    }

    patcher = patch("app.routers.runs.SteelService")
    mock_service_class = patcher.start()

    mock_service_instance = MagicMock()
    mock_service_instance.create_session = AsyncMock(return_value=mock_session_data)
    mock_service_class.return_value = mock_service_instance

    return patcher
