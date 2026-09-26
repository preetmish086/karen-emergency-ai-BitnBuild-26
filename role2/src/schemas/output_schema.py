from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum


class IncidentCategory(str, Enum):
    ACCIDENT = "accident"
    FIRE = "fire"
    FLOOD = "flood"
    MEDICAL = "medical"
    EXPLOSION = "explosion"
    COLLAPSE = "collapse"
    CRIME = "crime"
    MISSING_PERSON = "missing_person"
    OTHER = "other"
    UNKNOWN = "unknown"


class IncidentInfo(BaseModel):
    type: IncidentCategory = Field(..., description="Classified emergency category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score [0, 1]")


class PeopleAffected(BaseModel):
    """
    Extracted count of people affected.
    CRITICAL RULE: Null/None indicates no explicit count was stated in the report text.
    Must never be hallucinatory defaulted to zero or assumed counts.
    """
    total_affected: Optional[int] = Field(default=None, ge=0, description="Explicitly reported total affected count")
    injured: Optional[int] = Field(default=None, ge=0, description="Explicitly reported injured count")
    dead: Optional[int] = Field(default=None, ge=0, description="Explicitly reported deceased count")
    missing: Optional[int] = Field(default=None, ge=0, description="Explicitly reported missing count")
    trapped: Optional[int] = Field(default=None, ge=0, description="Explicitly reported trapped count")
    rescued: Optional[int] = Field(default=None, ge=0, description="Explicitly reported rescued count")
    evacuated: Optional[int] = Field(default=None, ge=0, description="Explicitly reported evacuated count")


class InformationCompleteness(BaseModel):
    has_casualty_information: bool = Field(..., description="True if any casualty/affected count was explicitly stated")
    has_affected_count: bool = Field(..., description="True if total affected count was stated")
    has_injury_information: bool = Field(..., description="True if injury/death info was explicitly stated")
    has_location_information: bool = Field(..., description="True if GPS or manual/textual location is available")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Overall report information completeness score [0, 1]")


class CredibilityAssessment(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Overall report credibility score [0, 1]")
    factors: Dict[str, float] = Field(..., description="Decomposed component credibility signals for explainability")


class LocationMetadata(BaseModel):
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="GPS latitude (optional)")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="GPS longitude (optional)")
    text_location: Optional[str] = Field(default=None, description="Extracted textual or manually provided location/address")
    has_gps: bool = Field(..., description="True if valid GPS coordinates are present")
    location_report_count: int = Field(default=1, ge=1, description="Number of reports received from this location/area")


class Role2OutputSchema(BaseModel):
    """
    Clean structured JSON output contract for Role 2.
    Ready for downstream consumption by Role 3 (clustering) & Role 4 (priority ranking).
    """
    report_id: str
    text: str
    incident: IncidentInfo
    people: PeopleAffected
    information: InformationCompleteness
    credibility: CredibilityAssessment
    location: LocationMetadata
    timestamp: str
