import os
import pytest

# Set test DB path before any app imports trigger DB connection
if not os.environ.get("SQLITE_DB_PATH"):
    os.environ["SQLITE_DB_PATH"] = "data/sqlite/pixelnote_test.sqlite3"
os.environ.setdefault("DB_BACKEND", "sqlite")

from fastapi.testclient import TestClient
from app.main import app

# Ensure SQLite tables exist before running the tests
import scripts.init_sqlite

@pytest.fixture
def client():
    return TestClient(app)
