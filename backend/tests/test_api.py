import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_get_methodologies(client):
    resp = client.get("/api/methodologies")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    names = {m["id"] for m in data}
    assert names == {"comps", "dcf", "last_round"}


def test_post_valuation_comps(client):
    resp = client.post("/api/valuations", json={
        "company_name": "TestCo",
        "sector": "technology",
        "methodologies": ["comps"],
        "comps_input": {"revenue": 10000000},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["company_name"] == "TestCo"
    assert len(data["results"]) == 1
    assert data["results"][0]["methodology"] == "comps"
    assert data["results"][0]["estimated_value"] > 0


def test_post_valuation_all_methods(client):
    resp = client.post("/api/valuations", json={
        "company_name": "MultiCo",
        "sector": "technology",
        "methodologies": ["comps", "dcf", "last_round"],
        "comps_input": {"revenue": 10000000},
        "dcf_input": {"revenue": 10000000},
        "last_round_input": {
            "post_money_valuation": 50000000,
            "round_date": "2024-06-01",
        },
    })
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 3


def test_post_valuation_missing_input(client):
    resp = client.post("/api/valuations", json={
        "company_name": "BadCo",
        "sector": "technology",
        "methodologies": ["comps"],
    })
    assert resp.status_code == 422  # Pydantic model validation


def test_post_sensitivity_dcf(client):
    resp = client.post("/api/sensitivity", json={
        "methodology": "dcf",
        "dcf_input": {"revenue": 10000000},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["methodology"] == "dcf"
    assert data["base_estimated_value"] > 0
    assert len(data["data_points"]) > 0
    assert "discount_rate" in data["varied_parameters"]


def test_get_sectors(client):
    resp = client.get("/api/sectors")
    assert resp.status_code == 200
    data = resp.json()
    assert "technology" in data


def test_export_pdf_returns_pdf(client):
    # Create a valuation first
    create_resp = client.post("/api/valuations", json={
        "company_name": "PdfTestCo",
        "sector": "technology",
        "methodologies": ["comps"],
        "comps_input": {"revenue": 10000000},
    })
    assert create_resp.status_code == 200
    report_id = create_resp.json()["id"]

    resp = client.get(f"/api/valuations/{report_id}/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


def test_export_pdf_not_found(client):
    resp = client.get("/api/valuations/nonexistent-id/export")
    assert resp.status_code == 404
