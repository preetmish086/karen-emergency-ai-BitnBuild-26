"""Karen's Ear — Fast, Modular Emergency Dispatch API.

Provides endpoints for ingesting citizen emergency reports, calculating priority scores,
and serving prioritized queues to authority dispatchers.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
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

app = FastAPI(
    title="Karen's Ear Emergency AI API",
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

SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample" / "sample_reports.json"


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
        "message": "Karen's Ear Emergency AI Backend API is online.",
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
    """Ingest an incoming emergency report, calculate priority score, and store in memory."""
    # Auto-generate ID if not provided
    report_id = payload.report_id or f"R{len(REPORTS_DB) + 1:03d}"

    # Auto-infer incident type if unknown or omitted
    inferred = infer_metadata_fallback(payload.text)
    incident_type = payload.incident_type
    if not incident_type or incident_type == IncidentType.UNKNOWN:
        incident_type = inferred["incident_type"]

    severity = payload.severity or inferred["severity"]
    actionability = payload.actionability or ActionabilityLevel.MEDIUM
    credibility = payload.credibility if payload.credibility is not None else 0.75

    # Task 1: Calculate priority score via Priority Engine
    priority = calculate_priority(
        severity=severity.value if hasattr(severity, "value") else str(severity),
        actionability=actionability.value if hasattr(actionability, "value") else str(actionability),
        credibility=credibility,
    )

    report = EmergencyReport(
        report_id=report_id,
        text=payload.text,
        incident_type=incident_type,
        location=payload.location,
        severity=severity,
        actionability=actionability,
        credibility=credibility,
        priority=priority,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status="pending",
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
