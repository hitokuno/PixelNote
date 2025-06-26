import pytest
from fastapi.testclient import TestClient
from app.main import app

# Ensure SQLite tables exist before running the tests
import scripts.init_sqlite

@pytest.fixture
def client():
    return TestClient(app)
