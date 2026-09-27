"""Unit and integration tests for emergency relevance and idiom detection."""

import pytest
from src.relevance.relevance_model import RelevanceModel
from src.relevance.idiom_detector import is_slang_or_figurative
from src.schema import IncidentType, SeverityLevel
from backend import app, ingest_report, IngestReportPayload, REPORTS_DB


@pytest.fixture(scope="module")
def relevance_model():
    model = RelevanceModel()
    model.load("models/relevance_model.pkl")
    return model


@pytest.mark.parametrize(
    "slang_text,hazard",
    [
        ("the movie i watched last night was fire", "fire"),
        ("the new album is straight fire", "fire"),
        ("this burger is the bomb", "bomb"),
        ("that concert was an absolute blast", "blast"),
        ("we had a blast at disneyland with the family", "blast"),
        ("my code crashed on production", "crash"),
        ("the server crashed right after deployment", "crash"),
        ("she was smoking hot in that dress", "smoke"),
        ("i am dying of laughter watching this video", "dying"),
        ("i had a heart attack when i saw the restaurant bill", "heart attack"),
        ("traffic on the expressway is absolute murder", "murder"),
        ("they completely killed their live performance", "kill"),
        ("the kids are shooting hoops at the community park", "shoot"),
        ("we were taking shots of tequila at the bar", "shots"),
        ("she stole my heart the moment i saw her", "stole"),
        ("these concert ticket fees are highway robbery", "robbery"),
        ("i am flooded with emails and messages this morning", "flood"),
        ("the sports team collapsed under pressure in the 4th quarter", "collapse"),
        ("the comedy show had me dying the whole time", "dying"),
        ("fire deal on sneakers at the shopping mall", "fire"),
    ]
)
def test_slang_detected_as_low_relevance(relevance_model, slang_text, hazard):
    """Ensure slang expressions with hazard words are classified as low relevance."""
    is_slang, reason = is_slang_or_figurative(slang_text)
    assert is_slang is True, f"Failed to detect slang in: '{slang_text}'"

    res = relevance_model.predict_one(slang_text)
    assert res["relevance_level"] == "low"
    assert res["is_slang_or_figurative"] is True
    assert res["relevance_score"] <= 0.20


@pytest.mark.parametrize(
    "emergency_text,expected_category",
    [
        ("Huge building fire on 42nd Street, flames and black smoke coming out!", "fire"),
        ("Severe car accident with two overturned vehicles on Brooklyn Bridge, people trapped!", "accident"),
        ("Loud explosion at the gas station near Queens Blvd, multiple injured!", "explosion"),
        ("Elderly man collapsed on the subway platform, unconscious and not breathing!", "medical"),
        ("Flash flood water rising rapidly and entering houses in Staten Island!", "flood"),
        ("Active armed robbery in progress at the jewelry store on Broadway!", "crime"),
        ("Ceiling collapsed inside the supermarket, people pinned under rubble!", "collapse"),
        ("Child is choking on food at the restaurant and turning blue, send ambulance!", "medical"),
    ]
)
def test_real_emergencies_classified_high_or_medium(relevance_model, emergency_text, expected_category):
    """Ensure authentic emergency reports maintain high/medium relevance."""
    is_slang, _ = is_slang_or_figurative(emergency_text)
    assert is_slang is False, f"Authentic emergency falsely flagged as slang: '{emergency_text}'"

    res = relevance_model.predict_one(emergency_text)
    assert res["relevance_level"] in ["medium", "high"]
    assert res["relevance_score"] >= 0.40


def test_authentic_emergency_at_entertainment_venue(relevance_model):
    """Ensure real emergencies at venues (movie theater, concert, bar) are not suppressed."""
    text = "Fire broke out at AMC movie theater on 42nd St, smoke everywhere, call 911!"
    is_slang, reason = is_slang_or_figurative(text)
    assert is_slang is False
    assert reason == "authentic_emergency_signal_present"

    res = relevance_model.predict_one(text)
    assert res["relevance_level"] in ["medium", "high"]


def test_backend_ingest_slang_assigns_zero_priority():
    """Verify backend assigns 0 priority and non_emergency status to slang input."""
    payload = IngestReportPayload(text="the movie i watched last night was fire")
    report = ingest_report(payload)
    assert report.incident_type == IncidentType.OTHER
    assert report.severity == SeverityLevel.LOW
    assert report.priority == 0.0
    assert report.status == "non_emergency"
    assert report.dispatch_status == "dismissed"
    assert report.credibility <= 0.10


def test_backend_ingest_real_emergency_assigns_high_priority():
    """Verify backend assigns proper incident type and high priority to genuine emergency."""
    payload = IngestReportPayload(
        text="Explosion reported at warehouse on 5th Avenue, 3 people trapped and injured, send help!"
    )
    report = ingest_report(payload)
    assert report.incident_type == IncidentType.EXPLOSION
    assert report.priority >= 0.70
    assert report.severity == SeverityLevel.CRITICAL
    assert report.status == "pending"


def test_backend_ingest_domestic_fireplace_dismissed():
    """Verify domestic fireplace heating reports are dismissed as non-emergency."""
    payload = IngestReportPayload(
        text="i had to put the fire on the fire place to make the place warm"
    )
    report = ingest_report(payload)
    assert report.incident_type == IncidentType.OTHER
    assert report.severity == SeverityLevel.LOW
    assert report.priority == 0.0
    assert report.status == "non_emergency"
    assert report.dispatch_status == "dismissed"
    assert report.credibility <= 0.10


def test_backend_ingest_benign_park_activity_dismissed():
    """Verify mundane non-emergency reports without hazards are dismissed."""
    payload = IngestReportPayload(
        text="i was playing in the park with my 12 year old neice"
    )
    report = ingest_report(payload)
    assert report.incident_type == IncidentType.OTHER
    assert report.severity == SeverityLevel.LOW
    assert report.priority == 0.0
    assert report.status == "non_emergency"
    assert report.dispatch_status == "dismissed"


def test_backend_ingest_movie_with_explicit_disclaimer_dismissed():
    """Verify movie description with hazard words and explicit disclaimer is dismissed with 0% priority."""
    text = "I am watching a movie about a massive fire in a warehouse where three people are trapped and injured. There is no actual emergency."
    is_slang, reason = is_slang_or_figurative(text)
    assert is_slang is True

    payload = IngestReportPayload(text=text)
    report = ingest_report(payload)
    assert report.incident_type == IncidentType.OTHER
    assert report.severity == SeverityLevel.LOW
    assert report.priority == 0.0
    assert report.status == "non_emergency"
    assert report.dispatch_status == "dismissed"
    assert report.credibility <= 0.10


def test_backend_ingest_drill_with_disclaimer_dismissed():
    """Verify emergency training drill with explicit disclaimer is dismissed with 0% priority."""
    text = "This is a fire drill in our office, two people trapped in room 402 for simulation. There is no actual emergency."
    is_slang, _ = is_slang_or_figurative(text)
    assert is_slang is True

    payload = IngestReportPayload(text=text)
    report = ingest_report(payload)
    assert report.incident_type == IncidentType.OTHER
    assert report.priority == 0.0
    assert report.status == "non_emergency"
    assert report.dispatch_status == "dismissed"


