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


def test_raw_csv_logging():
    from src.api.main import CSV_PATH
    import csv

    payload = {
        "gps_xy": "40.7128, -74.0060",
        "location": "Auto-resolved via GPS",
        "text": "Test emergency distress call for CSV verification!",
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 201
    assert CSV_PATH.exists()

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) >= 2
        assert reader[0] == ["time", "gps_xy", "location", "text"]
        last_row = reader[-1]
        assert last_row[1] == "40.7128, -74.0060"
        assert last_row[2] == "Auto-resolved via GPS"
        assert last_row[3] == "Test emergency distress call for CSV verification!"
