"""
Feature preparation for the emergency priority model.

Converts structured emergency information into numerical
features that can be used by an ML model.
"""

# Severity mapping
SEVERITY_MAP = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
    "critical": 1.00
}

# Actionability mapping
ACTIONABILITY_MAP = {
    "low": 0.25,
    "medium": 0.50,
    "high": 1.00
}


def severity_to_score(severity):
    """Convert severity category to numerical score."""
    return SEVERITY_MAP.get(str(severity).lower(), 0.0)


def actionability_to_score(actionability):
    """Convert actionability category to numerical score."""
    return ACTIONABILITY_MAP.get(
        str(actionability).lower(),
        0.0
    )


def normalize_corroboration_count(
    report_count,
    max_reports=5
):
    """
    Convert corroboration count to a 0-1 score.

    1 report  -> 0.20
    2 reports -> 0.40
    ...
    5+ reports -> 1.00
    """

    try:
        report_count = int(report_count)
    except (TypeError, ValueError):
        return 0.0

    if report_count <= 0:
        return 0.0

    return min(report_count / max_reports, 1.0)


def extract_features(
    severity,
    actionability,
    credibility,
    report_count
):
    """
    Convert emergency information into numerical features.

    Returns:
        list: [severity, actionability, credibility, corroboration]
    """

    severity_score = severity_to_score(severity)

    actionability_score = actionability_to_score(
        actionability
    )

    try:
        credibility_score = float(credibility)
    except (TypeError, ValueError):
        credibility_score = 0.0

    credibility_score = max(
        0.0,
        min(credibility_score, 1.0)
    )

    corroboration_score = normalize_corroboration_count(
        report_count
    )

    return [
        severity_score,
        actionability_score,
        credibility_score,
        corroboration_score
    ]