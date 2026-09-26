from src.priority.priority_model import PriorityModel
from src.priority.ranker import rank_emergencies


MODEL_PATH = "models/priority_model.pkl"


def main():

    # Load trained model
    model = PriorityModel()
    model.load(MODEL_PATH)

    emergencies = [

        {
            "report_id": "R001",
            "text": "Huge fire near railway station, people trapped",
            "incident_type": "fire",
            "location": "Railway Station",
            "severity": "critical",
            "actionability": "high",
            "credibility": 0.95,
            "corroboration_count": 4
        },

        {
            "report_id": "R002",
            "text": "Minor flooding near market",
            "incident_type": "flood",
            "location": "Market Road",
            "severity": "medium",
            "actionability": "medium",
            "credibility": 0.80,
            "corroboration_count": 2
        },

        {
            "report_id": "R003",
            "text": "Explosion reported near station",
            "incident_type": "explosion",
            "location": "Railway Station",
            "severity": "critical",
            "actionability": "high",
            "credibility": 0.85,
            "corroboration_count": 3
        }
    ]

    ranked = rank_emergencies(
        emergencies,
        model
    )

    print("\n===== EMERGENCY RANKING =====\n")

    for index, report in enumerate(
        ranked,
        start=1
    ):

        print(
            f"{index}. "
            f"{report['incident_type'].upper()} "
            f"@ {report['location']} "
            f"→ Priority: {report['priority']:.3f}"
        )


def test_rank_emergencies_with_trained_model():
    model = PriorityModel()
    model.load(MODEL_PATH)

    emergencies = [
        {
            "report_id": "R001",
            "text": "Huge fire near railway station, people trapped",
            "incident_type": "fire",
            "location": "Railway Station",
            "severity": "critical",
            "actionability": "high",
            "credibility": 0.95,
            "corroboration_count": 4
        },
        {
            "report_id": "R002",
            "text": "Minor flooding near market",
            "incident_type": "flood",
            "location": "Market Road",
            "severity": "medium",
            "actionability": "medium",
            "credibility": 0.80,
            "corroboration_count": 2
        }
    ]

    ranked = rank_emergencies(emergencies, model)
    assert len(ranked) == 2
    assert ranked[0]["report_id"] == "R001"
    assert ranked[0]["priority"] >= ranked[1]["priority"]


if __name__ == "__main__":
    main()