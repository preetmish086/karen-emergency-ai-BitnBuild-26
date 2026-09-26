"""Unit tests for PriorityEngine and emergency priority pipeline."""

import pytest
from src.priority.engine import PriorityEngine, calculate_priority
from src.schema import SeverityLevel, ActionabilityLevel
from src.priority.emergency_priority import (
    calculate_priority as calc_emergency_priority,
    calculate_severity,
    calculate_corroboration,
    location_specificity,
    calculate_actionability,
    process_report,
    rank_reports,
)


def test_priority_critical_highest():
    """Critical severity with high actionability and high credibility should score > 0.90."""
    p = calculate_priority(
        severity=SeverityLevel.CRITICAL,
        actionability=ActionabilityLevel.HIGH,
        credibility=0.90,
        cluster_size=1,
    )
    assert 0.90 <= p <= 1.0


def test_priority_low_minor():
    """Low severity with low actionability should produce a low priority score."""
    p = calculate_priority(
        severity=SeverityLevel.LOW,
        actionability=ActionabilityLevel.LOW,
        credibility=0.40,
        cluster_size=1,
    )
    assert p < 0.40


def test_priority_corroboration_boost():
    """Incident with multiple corroborating reports should receive a higher priority score."""
    p_single = calculate_priority(
        severity=SeverityLevel.HIGH,
        actionability=ActionabilityLevel.MEDIUM,
        credibility=0.70,
        cluster_size=1,
    )
    p_clustered = calculate_priority(
        severity=SeverityLevel.HIGH,
        actionability=ActionabilityLevel.MEDIUM,
        credibility=0.70,
        cluster_size=4,
    )
    assert p_clustered > p_single


def test_priority_boundary_clamping():
    """Priority must always strictly remain within [0.0, 1.0]."""
    p_max = calculate_priority(SeverityLevel.CRITICAL, ActionabilityLevel.HIGH, 1.0, cluster_size=10)
    assert p_max <= 1.0

    p_min = calculate_priority(SeverityLevel.LOW, ActionabilityLevel.LOW, 0.0, cluster_size=1)
    assert p_min >= 0.0


def test_explainability_structure():
    """Explanation output should contain component contributions and a recommendation."""
    explanation = PriorityEngine.explain(
        severity=SeverityLevel.CRITICAL,
        actionability=ActionabilityLevel.HIGH,
        credibility=0.85,
        cluster_size=2,
    )
    assert "final_priority" in explanation
    assert "components" in explanation
    assert "recommendation" in explanation
    assert explanation["recommendation"] == "IMMEDIATE_DISPATCH"


def test_emergency_priority_pipeline_calculation():
    """Tests the emergency priority calculation formulas."""
    sev = calculate_severity("fire")
    assert sev == 1.00

    corrob = calculate_corroboration(4)
    assert corrob == 0.85

    loc_score = location_specificity("Sector 5 Market Road floor 2")
    assert loc_score > 0.0

    act = calculate_actionability(
        severity=sev,
        credibility=0.9,
        corroboration_score=corrob,
        location_score=loc_score,
        people={"total_affected": 3}
    )
    assert 0.0 <= act <= 1.0

    prio = calc_emergency_priority(
        severity=sev,
        actionability=act,
        credibility=0.9,
        corroboration_score=corrob,
        location_score=loc_score,
        incident_confidence=0.95
    )
    assert 0.0 <= prio <= 1.0


def test_emergency_ranking_reports():
    """Tests ranking a batch of emergency reports."""
    sample_reports = [
        {
            "report_id": "R001",
            "text": "Explosion near railway station, people injured",
            "incident": {"type": "explosion", "confidence": 0.95},
            "credibility": {"score": 0.85},
            "location": {"text_location": "Railway Station Road", "location_report_count": 4},
            "people": {"injured": 3}
        },
        {
            "report_id": "R002",
            "text": "Minor water leakage reported",
            "incident": {"type": "flood", "confidence": 0.50},
            "credibility": {"score": 0.40},
            "location": {"text_location": "Market Road", "location_report_count": 1},
            "people": {}
        }
    ]
    ranked = rank_reports(sample_reports)
    assert len(ranked) == 2
    assert ranked[0]["report_id"] == "R001"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
    assert ranked[0]["priority"] >= ranked[1]["priority"]
