"""
Ranks emergency incidents according to predicted priority.
"""

from src.priority.features import extract_features


def rank_emergencies(reports, priority_model):
    """
    Predict priority for every emergency and rank them.

    Args:
        reports: list of emergency dictionaries
        priority_model: trained PriorityModel

    Returns:
        list of reports sorted by priority descending
    """

    ranked_reports = []

    for report in reports:

        features = extract_features(
            severity=report["severity"],
            actionability=report["actionability"],
            credibility=report["credibility"],
            report_count=report.get(
                "corroboration_count",
                1
            )
        )

        priority = priority_model.predict(
            [features]
        )[0]

        updated_report = report.copy()

        updated_report["priority"] = round(
            priority,
            3
        )

        ranked_reports.append(updated_report)

    ranked_reports.sort(
        key=lambda report: report["priority"],
        reverse=True
    )

    return ranked_reports