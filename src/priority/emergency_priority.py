from src import relevance


SEVERITY_MAP = {
    "fire": 1.00,
    "explosion": 1.00,
    "collapse": 1.00,
    "flood": 0.85,
    "medical": 0.85,
    "accident": 0.80,
    "crime": 0.75,
    "other": 0.50
}


def location_specificity(location):
    location = str(location).lower()

    score = 0.0

    if any(word in location for word in [
        "street", "avenue", "road", "plaza", "boulevard"
    ]):
        score += 0.40

    if "floor" in location:
        score += 0.25

    if "room" in location:
        score += 0.25

    if "building" in location or "block" in location:
        score += 0.10

    return min(score, 1.0)


def calculate_severity(incident_type):
    return SEVERITY_MAP.get(
        str(incident_type).lower().strip(),
        0.50
    )


def calculate_corroboration(report_count):
    """
    location_report_count represents reports
    within the current reporting window.
    """

    try:
        report_count = int(report_count)
    except (TypeError, ValueError):
        report_count = 1

    if report_count <= 1:
        return 0.0
    elif report_count == 2:
        return 0.50
    elif report_count == 3:
        return 0.70
    elif report_count == 4:
        return 0.85
    else:
        return 1.0


def calculate_actionability(
    severity,
    credibility,
    corroboration_score,
    location_score,
    people=None,
    information=None
):
    actionability = (
        0.40 * severity
        + 0.25 * credibility
        + 0.20 * corroboration_score
        + 0.15 * location_score
    )

    if people:
        values = [
            people.get("total_affected"),
            people.get("injured"),
            people.get("dead"),
            people.get("trapped"),
            people.get("missing")
        ]

        if any(value not in [None, 0] for value in values):
            actionability += 0.10

    return min(actionability, 1.0)


def calculate_priority(
    severity,
    actionability,
    credibility,
    corroboration_score,
    location_score,
    incident_confidence,
    relevance_score
):
    priority = (
        0.30 * severity
        + 0.20 * actionability
        + 0.15 * credibility
        + 0.10 * corroboration_score
        + 0.05 * location_score
        + 0.05 * incident_confidence
        + 0.15 * relevance_score
    )

    return round(
        min(priority, 1.0),
        3
    )


def process_report(report):

    incident = report.get("incident", {})
    credibility_data = report.get("credibility", {})
    location = report.get("location", {})
    people = report.get("people", {})
    information = report.get("information", {})
    relevance = report.get("relevance", {})

    relevance_score = float(
        relevance.get("relevance_score", 0.0)
    )

    incident_type = incident.get("type", "other")

    incident_confidence = float(
        incident.get("confidence", 0.0)
    )

    credibility = float(
        credibility_data.get("score", 0.0)
    )

    location_text = location.get(
        "text_location",
        ""
    )

    report_count = location.get(
        "location_report_count",
        1
    )

    corroboration_score = calculate_corroboration(
        report_count
    )

    severity = calculate_severity(
        incident_type
    )

    location_score = location_specificity(
        location_text
    )

    actionability = calculate_actionability(
        severity=severity,
        credibility=credibility,
        corroboration_score=corroboration_score,
        location_score=location_score,
        people=people,
        information=information
    )

    priority = calculate_priority(
        severity=severity,
        actionability=actionability,
        credibility=credibility,
        corroboration_score=corroboration_score,
        location_score=location_score,
        incident_confidence=incident_confidence,
        relevance_score=relevance_score
    )

    return {
        "report_id": report.get("report_id"),
        "text": report.get("text"),

        "relevance": report.get("relevance"),
        "relevance_score": round(relevance_score, 3),

        "incident_type": incident_type,
        "incident_confidence": round(incident_confidence, 3),

        "location": location_text,
        "location_report_count": report_count,

        "credibility": round(credibility, 3),
        "corroboration_score": round(corroboration_score, 3),
        "severity": round(severity, 3),
        "location_score": round(location_score, 3),
        "actionability": round(actionability, 3),
        "priority": priority
    }


def rank_reports(reports):

    processed = [
        process_report(report)
        for report in reports
    ]

    processed.sort(
        key=lambda x: x["priority"],
        reverse=True
    )

    for rank, report in enumerate(
        processed,
        start=1
    ):
        report["rank"] = rank

    return processed