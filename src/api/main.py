"""Karen's Ear — AI Emergency Dispatch Assistant REST API.

Serves priority-ranked emergency reports, live ingestion, dispatcher actions,
and incident statistics for the frontend dashboard.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from src.schema import (
    EmergencyReport,
    IncidentType,
    SeverityLevel,
    ActionabilityLevel,
    DispatchStatus,
    IngestReportRequest,
    DispatchActionRequest,
)
from src.priority.engine import PriorityEngine

app = FastAPI(
    title="Karen's Ear — Emergency Dispatch Assistant API",
    description="Intelligent prioritization and dispatch triage API for chaotic emergency reports.",
    version="1.0.0",
)

# Enable CORS for frontend dashboard development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for reports
REPORTS_DB: Dict[str, EmergencyReport] = {}

SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample" / "sample_reports.json"


def infer_report_metadata(text: str) -> Dict[str, any]:
    """Lightweight heuristic parser used for live demo ingestion.

    Extracts incident type, location, severity, and credibility before Member 1's NLP model is loaded.
    """
    lower = text.lower()

    # Incident type keyword mapping
    incident_type = IncidentType.UNKNOWN
    if any(k in lower for k in ["fire", "smoke", "blaze", "burning", "flames"]):
        incident_type = IncidentType.FIRE
    elif any(k in lower for k in ["explosion", "blast", "bomb", "detonation"]):
        incident_type = IncidentType.EXPLOSION
    elif any(k in lower for k in ["accident", "crash", "collision", "overturned", "traffic blocked"]):
        incident_type = IncidentType.ACCIDENT
    elif any(k in lower for k in ["collapse", "collapsed", "cave-in", "rubble", "trapped"]):
        incident_type = IncidentType.COLLAPSE
    elif any(k in lower for k in ["flood", "water rising", "submerged", "drowning"]):
        incident_type = IncidentType.FLOOD
    elif any(k in lower for k in ["gunshot", "shooting", "robbery", "assault", "crime", "stolen", "attacker"]):
        incident_type = IncidentType.CRIME
    elif any(k in lower for k in ["cardiac", "stroke", "unconscious", "bleeding", "ambulance", "medical"]):
        incident_type = IncidentType.MEDICAL
    elif any(k in lower for k in ["missing", "lost child"]):
        incident_type = IncidentType.MISSING_PERSON

    # Location extraction heuristic (e.g., "near X", "at X", "on X")
    location = None
    loc_match = re.search(r"(?:near|at|on|around)\s+(the\s+)?([A-Za-z0-9\s\-]+?)(?:[.,!]|(?:\s+with|\s+and|\s+several|\s+please|\s+traffic|\s+people|$))", text, re.IGNORECASE)
    if loc_match:
        cand = loc_match.group(2).strip()
        if len(cand) >= 3 and cand.lower() not in ["the", "a", "an", "some"]:
            location = cand

    # Severity determination
    if any(k in lower for k in ["critical", "several injured", "multiple people injured", "trapped", "dying", "unconscious", "explosion"]):
        severity = SeverityLevel.CRITICAL
    elif any(k in lower for k in ["high", "smoke", "blocked", "heavy", "fire", "crash", "rising rapidly"]):
        severity = SeverityLevel.HIGH
    elif any(k in lower for k in ["loud noise", "not sure", "minor", "small"]):
        severity = SeverityLevel.MEDIUM
    else:
        severity = SeverityLevel.MEDIUM

    # Actionability determination
    if any(k in lower for k in ["please send", "ambulance", "help", "trapped", "blocked", "injured", "immediate"]):
        actionability = ActionabilityLevel.HIGH
    elif any(k in lower for k in ["not sure", "can't see", "maybe", "noise"]):
        actionability = ActionabilityLevel.MEDIUM
    else:
        actionability = ActionabilityLevel.MEDIUM

    # Credibility heuristic: specific details & location increase credibility
    credibility = 0.50
    if location:
        credibility += 0.20
    if any(k in lower for k in ["several", "two people", "multiple", "clear", "smoke coming from"]):
        credibility += 0.15
    if any(k in lower for k in ["not sure", "can't see", "i think", "somewhere"]):
        credibility -= 0.25
    credibility = max(0.20, min(0.95, round(credibility, 2)))

    return {
        "incident_type": incident_type,
        "location": location,
        "severity": severity,
        "actionability": actionability,
        "credibility": credibility,
    }


def load_initial_data() -> None:
    """Load sample reports from DATA_SCHEMA-compliant JSON file."""
    REPORTS_DB.clear()
    if SAMPLE_DATA_PATH.exists():
        with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
            for idx, item in enumerate(raw_list):
                # Ensure priority is present or calculated
                if "priority" not in item:
                    item["priority"] = PriorityEngine.calculate(
                        item.get("severity", SeverityLevel.MEDIUM),
                        item.get("actionability", ActionabilityLevel.MEDIUM),
                        item.get("credibility", 0.70),
                    )
                report = EmergencyReport(
                    **item,
                    dispatch_status=DispatchStatus.PENDING,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                REPORTS_DB[report.report_id] = report
    print(f"Loaded {len(REPORTS_DB)} emergency reports into memory.")


# Initialize store on startup
load_initial_data()


@app.get("/", tags=["Root"])
def root_info():
    """API overview and operational status."""
    return {
        "system": "Karen's Ear Emergency AI",
        "role": "Priority Engine + Dispatch API",
        "status": "operational",
        "reports_loaded": len(REPORTS_DB),
        "docs_url": "/docs",
    }


@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_reports": len(REPORTS_DB),
    }


@app.get("/api/reports", response_model=List[EmergencyReport], tags=["Reports"])
def list_reports(
    incident_type: Optional[IncidentType] = None,
    severity: Optional[SeverityLevel] = None,
    status: Optional[DispatchStatus] = None,
    min_priority: Optional[float] = Query(None, ge=0.0, le=1.0),
    search: Optional[str] = None,
):
    """Retrieve all reports, filtered and sorted by priority descending."""
    results = list(REPORTS_DB.values())

    if incident_type:
        results = [r for r in results if r.incident_type == incident_type]
    if severity:
        results = [r for r in results if r.severity == severity]
    if status:
        results = [r for r in results if r.dispatch_status == status]
    if min_priority is not None:
        results = [r for r in results if r.priority >= min_priority]
    if search:
        s_lower = search.lower()
        results = [
            r for r in results
            if s_lower in r.text.lower() or (r.location and s_lower in r.location.lower())
        ]

    # Sort primarily by priority descending
    results.sort(key=lambda r: r.priority, reverse=True)
    return results


@app.get("/api/reports/{report_id}", response_model=EmergencyReport, tags=["Reports"])
def get_report(report_id: str):
    """Retrieve details for a single emergency report."""
    if report_id not in REPORTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found.",
        )
    return REPORTS_DB[report_id]


@app.get("/api/reports/{report_id}/explain", tags=["Priority"])
def explain_report_priority(report_id: str):
    """Get full explainable AI breakdown of priority calculation for dispatchers."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    r = REPORTS_DB[report_id]
    explanation = PriorityEngine.explain(
        severity=r.severity,
        actionability=r.actionability,
        credibility=r.credibility,
        cluster_size=1,
    )
    explanation["report_id"] = report_id
    explanation["incident_type"] = r.incident_type
    explanation["location"] = r.location
    return explanation


@app.post("/api/reports", response_model=EmergencyReport, status_code=status.HTTP_201_CREATED, tags=["Reports"])
def ingest_report(payload: IngestReportRequest):
    """Ingest a new incoming emergency report.

    Calculates priority and stores it in memory.
    """
    inferred = infer_report_metadata(payload.text)

    # Use explicitly supplied fields or fall back to inferred heuristics
    incident_type = payload.incident_type or inferred["incident_type"]
    location = payload.location or inferred["location"]
    severity = payload.severity or inferred["severity"]
    actionability = payload.actionability or inferred["actionability"]
    credibility = payload.credibility if payload.credibility is not None else inferred["credibility"]

    # Calculate final priority score
    priority = PriorityEngine.calculate(
        severity=severity,
        actionability=actionability,
        credibility=credibility,
        cluster_size=payload.cluster_size,
    )

    # Generate sequential report ID
    new_num = len(REPORTS_DB) + 1
    new_id = f"R{new_num:03d}"

    report = EmergencyReport(
        report_id=new_id,
        text=payload.text,
        incident_type=incident_type,
        location=location,
        severity=severity,
        actionability=actionability,
        credibility=credibility,
        priority=priority,
        dispatch_status=DispatchStatus.PENDING,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    REPORTS_DB[new_id] = report
    return report


@app.patch("/api/reports/{report_id}/dispatch", response_model=EmergencyReport, tags=["Dispatch"])
def update_dispatch_status(report_id: str, action: DispatchActionRequest):
    """Update dispatch triage status (pending, dispatched, resolved, dismissed)."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

    report = REPORTS_DB[report_id]
    report.dispatch_status = action.status
    if action.dispatched_unit:
        report.dispatched_unit = action.dispatched_unit

    REPORTS_DB[report_id] = report
    return report


@app.post("/api/reports/reset", tags=["System"])
def reset_to_sample_data():
    """Reset the database to the default sample dataset (useful for hackathon demos)."""
    load_initial_data()
    return {"status": "reset_successful", "total_reports": len(REPORTS_DB)}


@app.get("/api/stats", tags=["Analytics"])
def get_dispatch_statistics():
    """Aggregated operational metrics for dispatcher KPIs and charts."""
    reports = list(REPORTS_DB.values())
    if not reports:
        return {
            "total_reports": 0,
            "critical_count": 0,
            "pending_dispatch": 0,
            "dispatched_count": 0,
            "resolved_count": 0,
            "average_priority": 0.0,
            "by_incident_type": {},
        }

    critical_count = sum(1 for r in reports if r.severity == SeverityLevel.CRITICAL)
    pending_count = sum(1 for r in reports if r.dispatch_status == DispatchStatus.PENDING)
    dispatched_count = sum(1 for r in reports if r.dispatch_status == DispatchStatus.DISPATCHED)
    resolved_count = sum(1 for r in reports if r.dispatch_status == DispatchStatus.RESOLVED)
    avg_priority = round(sum(r.priority for r in reports) / len(reports), 2)

    by_type: Dict[str, int] = {}
    for r in reports:
        by_type[r.incident_type.value] = by_type.get(r.incident_type.value, 0) + 1

    return {
        "total_reports": len(reports),
        "critical_count": critical_count,
        "pending_dispatch": pending_count,
        "dispatched_count": dispatched_count,
        "resolved_count": resolved_count,
        "average_priority": avg_priority,
        "by_incident_type": by_type,
    }
