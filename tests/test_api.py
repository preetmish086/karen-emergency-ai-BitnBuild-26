"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from src.api.main import app, load_initial_data

client = TestClient(app)


def setup_function():
    """Reset database before each test."""
    load_initial_data()


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_reports"] > 0


def test_list_reports():
    response = client.get("/api/reports")
    assert response.status_code == 200
    reports = response.json()
    assert len(reports) == 8
    # Ensure sorted by priority descending
    priorities = [r["priority"] for r in reports]
    assert priorities == sorted(priorities, reverse=True)


def test_filter_reports():
    response = client.get("/api/reports?incident_type=fire")
    assert response.status_code == 200
    reports = response.json()
    assert len(reports) >= 1
    assert all(r["incident_type"] == "fire" for r in reports)


def test_ingest_report_auto_infer():
    payload = {
        "text": "Severe building explosion near Grand Central station, multiple people injured!"
    }
    response = client.post("/api/reports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["incident_type"] == "explosion"
    assert data["severity"] == "critical"
    assert data["priority"] >= 0.80
    assert data["report_id"].startswith("R")


def test_dispatch_action():
    response = client.patch(
        "/api/reports/R001/dispatch",
        json={"status": "dispatched", "dispatched_unit": "Engine 7"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["dispatch_status"] == "dispatched"
    assert data["dispatched_unit"] == "Engine 7"


def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_reports"] >= 8
    assert "critical_count" in stats
    assert "by_incident_type" in stats
