from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone


class EmergencyReportInput(BaseModel):
    """
    Input contract for Role 2.
    Receives raw text and optional GPS metadata, manual location text, or location report count.
    """
    report_id: str = Field(..., description="Unique identifier for the report")
    text: str = Field(..., min_length=1, description="Raw natural human-language emergency report text")
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Optional GPS latitude")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Optional GPS longitude")
    location: Optional[str] = Field(default=None, description="Optional manual location text or address from metadata/CSV")
    location_report_count: Optional[int] = Field(default=None, ge=1, description="Count of reports received from this location")
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 formatted timestamp string"
    )

    @field_validator("text")
    def validate_text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Report text cannot be empty or whitespace only.")
        return v.strip()
