import pytest
from core.app import app
from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    client = TestClient(app)
    yield client