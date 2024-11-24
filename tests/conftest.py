import pytest
from main import app
from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    client = TestClient(app)
    yield client