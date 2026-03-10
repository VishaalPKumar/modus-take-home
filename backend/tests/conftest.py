import pytest
from fastapi.testclient import TestClient

from app.data.provider import MockDataProvider
from app.main import app
from app.service import ValuationService


@pytest.fixture
def service():
    return ValuationService(MockDataProvider())


@pytest.fixture
def client():
    return TestClient(app)
