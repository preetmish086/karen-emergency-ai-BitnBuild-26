"""SpidyCAD Backend API & Data Ingestion Engine.

Implements:
1. Raw CSV logging logic in raw_emergencies.csv with exact headers: time, gps_xy, location, text
2. /ingest endpoint generating timestamp via datetime.now().strftime("%Y-%m-%d %H:%M:%S")
3. Extracting gps_xy, location, and text from payload and appending to raw_emergencies.csv
4. Priority triage scoring and prioritized incident queues for SpidyCAD HUD
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from src.schema import (
    EmergencyReport,
    IngestReportPayload,
    IncidentType,
    SeverityLevel,
    ActionabilityLevel,
)
from src.priority.engine import calculate_priority

# Initialize Role 2 NLP & Credibility Pipeline
try:
    from role2.src.pipeline.process_report import EmergencyReportPipeline
    nlp_pipeline = EmergencyReportPipeline()
except Exception:
    nlp_pipeline = None

app = FastAPI(
    title="SpidyCAD Emergency AI API",
    description="Emergency dispatch ingestion and prioritization backend.",
    version="1.0.0",
)

# Enable CORS for frontend interfaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for reports
REPORTS_DB: Dict[str, EmergencyReport] = {}

WORKSPACE_ROOT = Path(__file__).resolve().parent
SAMPLE_DATA_PATH = WORKSPACE_ROOT / "data" / "sample" / "sample_reports.json"
CSV_PATH = WORKSPACE_ROOT / "raw_emergencies.csv"

# NYC Coordinates for landmark & borough auto-resolution
NYC_COORDINATES = {
    "times square": (40.7580, -73.9855),
    "midtown": (40.7549, -73.9840),
    "downtown": (40.7128, -74.0060),
    "financial district": (40.7075, -74.0090),
    "wall street": (40.7075, -74.0090),
    "grand central": (40.7527, -73.9772),
    "central market": (40.7527, -73.9772),
    "station road": (40.7516, -73.9755),
    "penn station": (40.7505, -73.9934),
    "penn plaza": (40.7505, -73.9934),
    "chelsea": (40.7465, -74.0014),
    "highway": (40.7680, -73.9980),
    "riverside": (40.7480, -74.0080),
    "brooklyn": (40.6782, -73.9442),
    "brooklyn bridge": (40.7061, -73.9969),
    "manhattan bridge": (40.7081, -73.9941),
    "williamsburg": (40.7081, -73.9571),
    "dumbo": (40.7033, -73.9881),
    "queens": (40.7282, -73.7949),
    "queens blvd": (40.7282, -73.8820),
    "long island city": (40.7447, -73.9485),
    "lic plaza": (40.7505, -73.9372),
    "astoria": (40.7644, -73.9235),
    "flushing": (40.7674, -73.8331),
    "manhattan": (40.7831, -73.9712),
    "harlem": (40.8116, -73.9465),
    "central park": (40.7851, -73.9683),
    "bronx": (40.8448, -73.8648),
    "staten island": (40.5795, -74.1502),
    "greenwich village": (40.7336, -74.0027),
    "east village": (40.7265, -73.9815),
    "soho": (40.7233, -74.0030),
    "tribeca": (40.7163, -74.0086),
    "fdr drive": (40.7308, -73.9734),
    "broadway": (40.7590, -73.9845),
    "atlantic avenue": (40.6845, -73.9780),
    "park avenue": (40.7587, -73.9738),
    "bus stand": (40.7570, -73.9900),
    "market": (40.7520, -73.9770),
    "subway": (40.7580, -73.9855),
    "jfk": (40.6413, -73.7781),
    "laguardia": (40.7769, -73.8740),
}


def log_raw_emergency(time_str: str, gps_xy: str, location: str, text: str) -> None:
    """Append a raw emergency record to raw_emergencies.csv with exact headers:
    time, gps_xy, location, text
    """
    file_exists = CSV_PATH.exists()
    is_empty = file_exists and CSV_PATH.stat().st_size == 0

    sanitized_text = text.replace('\n', ' ').replace('\r', ' ').strip()

    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists or is_empty:
            writer.writerow(["time", "gps_xy", "location", "text"])
        writer.writerow([time_str, gps_xy, location, sanitized_text])


def infer_metadata_fallback(text: str) -> dict:
    """Fallback keyword heuristic to identify incident type if not provided."""
    lower = text.lower()
    inc = IncidentType.UNKNOWN
    if any(k in lower for k in ["fire", "smoke", "blaze", "burning", "flames"]):
        inc = IncidentType.FIRE
    elif any(k in lower for k in ["explosion", "blast", "bomb", "detonation"]):
        inc = IncidentType.EXPLOSION
    elif any(k in lower for k in ["accident", "crash", "collision", "overturned"]):
        inc = IncidentType.ACCIDENT
    elif any(k in lower for k in ["collapse", "collapsed", "cave-in", "rubble", "trapped"]):
        inc = IncidentType.COLLAPSE
    elif any(k in lower for k in ["flood", "water rising", "submerged"]):
        inc = IncidentType.FLOOD
    elif any(k in lower for k in ["gunshot", "shooting", "robbery", "assault", "crime"]):
        inc = IncidentType.CRIME
    elif any(k in lower for k in ["cardiac", "stroke", "unconscious", "bleeding", "ambulance", "medical"]):
        inc = IncidentType.MEDICAL
    elif any(k in lower for k in ["missing", "lost child"]):
        inc = IncidentType.MISSING_PERSON

    sev = SeverityLevel.CRITICAL if any(k in lower for k in ["critical", "injured", "trapped", "explosion", "dying"]) else SeverityLevel.MEDIUM
    return {"incident_type": inc, "severity": sev}


def load_initial_reports():
    """Seed in-memory database from sample reports if available."""
    REPORTS_DB.clear()
    if SAMPLE_DATA_PATH.exists():
        with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            for item in raw_data:
                # Calculate priority if missing
                if "priority" not in item:
                    item["priority"] = calculate_priority(
                        severity=item.get("severity", "medium"),
                        actionability=item.get("actionability", "medium"),
                        credibility=item.get("credibility", 0.75),
                    )
                report = EmergencyReport(**item)
                REPORTS_DB[report.report_id] = report


load_initial_reports()
load_initial_data = load_initial_reports


@app.get("/", tags=["System"])
def root():
    return {
        "message": "SpidyCAD Emergency AI Backend API is online.",
        "endpoints": {
            "reports": "/reports",
            "ingest": "/ingest",
            "health": "/health",
            "interactive_docs": "/docs",
        },
        "frontend_dashboard_url": "http://localhost:8501",
    }


@app.get("/reports", response_model=List[EmergencyReport], tags=["Reports"])
@app.get("/api/reports", response_model=List[EmergencyReport], tags=["Reports"])
def get_reports(
    incident_type: Optional[IncidentType] = None,
    severity: Optional[SeverityLevel] = None,
):
    """Returns all stored reports sorted by priority in descending order (highest first)."""
    reports = list(REPORTS_DB.values())
    if incident_type:
        reports = [r for r in reports if r.incident_type == incident_type]
    if severity:
        reports = [r for r in reports if r.severity == severity]

    # Sort strictly by priority descending
    reports.sort(key=lambda r: r.priority, reverse=True)
    return reports


@app.post("/ingest", response_model=EmergencyReport, status_code=status.HTTP_201_CREATED, tags=["Ingest"])
@app.post("/api/reports", response_model=EmergencyReport, status_code=status.HTTP_201_CREATED, tags=["Ingest"])
def ingest_report(payload: IngestReportPayload):
    """Ingest an incoming emergency report, log to raw CSV, calculate priority score, and store in memory."""
    # 1. Generate time using datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Extract gps_xy, location, and text from the payload
    gps_xy = payload.gps_xy if payload.gps_xy is not None else "None"
    location = payload.location if payload.location is not None else "None"
    text = payload.text

    sanitized_text = text.replace('\n', ' ').replace('\r', ' ').strip()

    # 3. Append to raw_emergencies.csv
    log_raw_emergency(report_time, gps_xy, location, sanitized_text)

    # Auto-generate ID if not provided
    report_id = payload.report_id or f"R{len(REPORTS_DB) + 1:03d}"

    # Derive coordinates from gps_xy or landmark fallback
    lat = payload.latitude
    lon = payload.longitude
    if (lat is None or lon is None) and gps_xy and gps_xy != "None":
        try:
            parts = [float(p.strip()) for p in gps_xy.split(",")]
            if len(parts) == 2:
                lat, lon = parts[0], parts[1]
        except (ValueError, TypeError):
            pass

    if (lat is None or lon is None) and location and location != "None":
        for landmark, (l_lat, l_lon) in NYC_COORDINATES.items():
            if landmark.lower() in location.lower():
                lat, lon = l_lat, l_lon
                break

    # If coordinates are still unresolved, check if payload text mentions any NYC landmarks
    if lat is None or lon is None:
        for landmark, (l_lat, l_lon) in NYC_COORDINATES.items():
            if landmark.lower() in payload.text.lower():
                lat, lon = l_lat, l_lon
                if not location or location == "None":
                    location = landmark.title()
                break

    # Default fallback coordinates (Midtown Manhattan) to ensure radar grid always maps pins
    if lat is None or lon is None:
        lat, lon = 40.7549, -73.9840
        if not location or location == "None":
            location = "Midtown Manhattan"

    # Format gps_xy string if originally empty
    if gps_xy == "None" or not gps_xy:
        gps_xy = f"{lat:.4f}, {lon:.4f}"

    # Run Role 2 NLP pipeline for automated incident classification, entity extraction & credibility
    role2_result = None
    if nlp_pipeline is not None:
        try:
            role2_result = nlp_pipeline.process({
                "report_id": report_id,
                "text": payload.text,
                "latitude": lat,
                "longitude": lon,
            })
        except Exception:
            role2_result = None

    # Auto-infer incident type if unknown or omitted
    inferred = infer_metadata_fallback(payload.text)
    incident_type = payload.incident_type
    if not incident_type or incident_type == IncidentType.UNKNOWN:
        if role2_result and role2_result.incident and role2_result.incident.type:
            try:
                incident_type = IncidentType(role2_result.incident.type.value)
            except (ValueError, AttributeError):
                incident_type = inferred["incident_type"]
        else:
            incident_type = inferred["incident_type"]

    severity = payload.severity or inferred["severity"]
    actionability = payload.actionability or ActionabilityLevel.MEDIUM

    # Credibility assessment
    if payload.credibility is not None and payload.credibility != 0.75:
        credibility = payload.credibility
    elif role2_result and role2_result.credibility:
        credibility = round(float(role2_result.credibility.score), 4)
    else:
        credibility = payload.credibility if payload.credibility is not None else 0.75

    # Extract casualty counts from Role 2 if detected
    affected_count = None
    injured_count = None
    cred_factors = None
    if role2_result:
        if role2_result.people:
            affected_count = role2_result.people.total_affected
            injured_count = role2_result.people.injured
            if (injured_count and injured_count > 0) or (affected_count and affected_count > 0):
                if not payload.actionability:
                    actionability = ActionabilityLevel.HIGH
                if not payload.severity:
                    severity = SeverityLevel.CRITICAL
        if role2_result.credibility and hasattr(role2_result.credibility, "factors"):
            cred_factors = role2_result.credibility.factors.model_dump() if hasattr(role2_result.credibility.factors, "model_dump") else dict(role2_result.credibility.factors)

    # Calculate priority score via Priority Engine
    priority = calculate_priority(
        severity=severity.value if hasattr(severity, "value") else str(severity),
        actionability=actionability.value if hasattr(actionability, "value") else str(actionability),
        credibility=credibility,
    )

    report = EmergencyReport(
        report_id=report_id,
        text=payload.text,
        incident_type=incident_type,
        location=payload.location if payload.location and payload.location != "None" else None,
        severity=severity,
        actionability=actionability,
        credibility=credibility,
        priority=priority,
        latitude=lat,
        longitude=lon,
        gps_xy=gps_xy if gps_xy != "None" else None,
        status="pending",
        dispatch_status="pending",
        affected_count=affected_count,
        injured_count=injured_count,
        credibility_factors=cred_factors,
    )

    REPORTS_DB[report_id] = report
    return report


@app.patch("/api/reports/{report_id}/dispatch", response_model=EmergencyReport, tags=["Dispatch"])
def dispatch_report(report_id: str, payload: dict):
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    r = REPORTS_DB[report_id]
    st = payload.get("status", "dispatched")
    r.status = st
    r.dispatch_status = st
    if "dispatched_unit" in payload:
        r.dispatched_unit = payload["dispatched_unit"]
    return r


@app.get("/api/stats", tags=["Analytics"])
def get_stats():
    reports = list(REPORTS_DB.values())
    return {
        "total_reports": len(reports),
        "critical_count": sum(1 for r in reports if r.severity == SeverityLevel.CRITICAL),
        "by_incident_type": {inc.value: sum(1 for r in reports if r.incident_type == inc) for inc in IncidentType},
    }


@app.post("/api/reports/reset", tags=["System"])
def reset_reports():
    """Reset database to initial sample records."""
    load_initial_reports()
    return {"status": "success", "count": len(REPORTS_DB)}


@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"])
def health():
    return {"status": "healthy", "total_reports": len(REPORTS_DB)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
