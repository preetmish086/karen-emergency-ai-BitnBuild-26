"""Data models enforcing DATA_SCHEMA.md specifications for Karen's Ear."""

from enum import Enum
from typing import Optional, Literal
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


class DispatchStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class EmergencyReport(BaseModel):
    """Processed emergency report strictly matching DATA_SCHEMA.md."""

    report_id: str = Field(..., description="Unique report identifier")
    text: str = Field(..., description="Original emergency report text")
    incident_type: IncidentType = Field(default=IncidentType.UNKNOWN, description="Type of incident")
    location: Optional[str] = Field(default=None, description="Extracted location or null if uncertain")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Estimated severity")
    actionability: ActionabilityLevel = Field(default=ActionabilityLevel.MEDIUM, description="Urgency/actionability")
    credibility: float = Field(..., ge=0.0, le=1.0, description="Credibility confidence from 0.0 to 1.0")
    priority: float = Field(..., ge=0.0, le=1.0, description="Final priority score from 0.0 to 1.0")

    # Additional dispatcher operational metadata (optional, non-breaking)
    dispatch_status: DispatchStatus = Field(default=DispatchStatus.PENDING, description="Dispatcher triage state")
    dispatched_unit: Optional[str] = Field(default=None, description="e.g. Engine 4, Ambulance 2, Police Squad")
    cluster_id: Optional[str] = Field(default=None, description="Associated incident cluster ID")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp")

    @field_validator("credibility", "priority")
    @classmethod
    def round_scores(cls, v: float) -> float:
        return round(float(v), 4)


class IngestReportRequest(BaseModel):
    """Payload when creating or submitting a raw/partial emergency report."""

    text: str = Field(..., min_length=3, description="Emergency report description")
    incident_type: Optional[IncidentType] = Field(default=None, description="Optional pre-classified incident type")
    location: Optional[str] = Field(default=None, description="Optional known location")
    severity: Optional[SeverityLevel] = Field(default=None, description="Optional manual or model severity")
    actionability: Optional[ActionabilityLevel] = Field(default=None, description="Optional actionability")
    credibility: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Optional credibility score")
    cluster_size: int = Field(default=1, ge=1, description="Number of reports corroborating this incident")


class DispatchActionRequest(BaseModel):
    """Payload when dispatcher takes action on a report."""

    status: DispatchStatus
    dispatched_unit: Optional[str] = None
    notes: Optional[str] = None
