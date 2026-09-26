"""Unit tests for PriorityEngine."""

import pytest
from src.priority.engine import PriorityEngine, calculate_priority
from src.schema import SeverityLevel, ActionabilityLevel


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
