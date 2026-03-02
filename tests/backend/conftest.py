import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add backend source to path so imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "backend"))

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
