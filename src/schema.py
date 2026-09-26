"""Data schema models for Karen's Ear emergency reports."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class IncidentType(str, Enum):
    FIRE = "fire"
    EXPLOSION = "explosion"
    ACCIDENT = "accident"
    MEDICAL = "medical"
    COLLAPSE = "collapse"
    FLOOD = "flood"
    CRIME = "crime"
    MISSING_PERSON = "missing_person"
    UNKNOWN = "unknown"
    OTHER = "other"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionabilityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EmergencyReport(BaseModel):
    """Full emergency report strictly following project data schema."""

    report_id: str
    text: str
    incident_type: IncidentType = IncidentType.UNKNOWN
    location: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.MEDIUM
    actionability: ActionabilityLevel = ActionabilityLevel.MEDIUM
    credibility: float = Field(default=0.75, ge=0.0, le=1.0)
    priority: float = Field(..., ge=0.0, le=1.0)

    # Geolocation and dispatcher tracking fields
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gps_xy: Optional[str] = None
    status: Optional[str] = "pending"
    dispatch_status: Optional[str] = "pending"
    dispatched_unit: Optional[str] = None
    affected_count: Optional[int] = None
    injured_count: Optional[int] = None
    credibility_factors: Optional[dict] = None

    @field_validator("credibility", "priority")
    @classmethod
    def round_scores(cls, v: float) -> float:
        return round(float(v), 4)


class IngestReportPayload(BaseModel):
    """Payload for POST /ingest endpoint."""

    report_id: Optional[str] = None
    text: str
    incident_type: Optional[IncidentType] = None
    location: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    actionability: Optional[ActionabilityLevel] = None
    credibility: Optional[float] = Field(default=0.75, ge=0.0, le=1.0)
    priority: Optional[float] = None
    gps_xy: Optional[str] = None

    # Geolocation transmitted by the user's GPS
    latitude: Optional[float] = None
    longitude: Optional[float] = None
