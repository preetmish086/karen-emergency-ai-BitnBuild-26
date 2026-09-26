from src.priority.priority_model import calculate_priority
from src.priority.ranker import rank_emergencies


# Test one emergency
score = calculate_priority(
    severity="critical",
    actionability="high",
    credibility=0.85,
    report_count=4
)

print("Priority Score:", score)


# Test multiple emergencies
reports = [
    {
        "report_id": "R001",
        "text": "Explosion near railway station, people injured",
        "incident_type": "explosion",
        "location": "Railway Station",
        "severity": "critical",
        "actionability": "high",
        "credibility": 0.85,
        "report_count": 4
    },
    {
        "report_id": "R002",
        "text": "Minor water leakage reported",
        "incident_type": "flood",
        "location": "Market Road",
        "severity": "low",
        "actionability": "low",
        "credibility": 0.70,
        "report_count": 1
    },
    {
        "report_id": "R003",
        "text": "Large fire near residential area",
        "incident_type": "fire",
        "location": "Sector 5",
        "severity": "high",
        "actionability": "high",
        "credibility": 0.90,
        "report_count": 3
    }
]


ranked = rank_emergencies(reports)

for report in ranked:
    print(
        report["report_id"],
        "->",
        report["priority"]
    )