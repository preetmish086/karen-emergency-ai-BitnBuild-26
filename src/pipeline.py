import json

from src.relevance.relevance_model import RelevanceModel
from src.priority.emergency_priority import rank_reports


RELEVANCE_MODEL_PATH = "models/relevance_model.pkl"

INPUT_PATH = "data/sample/test_classification.json"
OUTPUT_PATH = "data/sample/final_output.json"


def main():

    print("Loading relevance model...")

    relevance_model = RelevanceModel()
    relevance_model.load(RELEVANCE_MODEL_PATH)

    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        reports = json.load(file)

    if isinstance(reports, dict):
        reports = reports.get("reports", [])

    print(f"Reports received: {len(reports)}")

    relevant_reports = []
    rejected_reports = []

    print("\n===== RELEVANCE FILTER =====\n")

    for report in reports:

        text = report.get("text", "")

        relevance = relevance_model.predict_one(text)

        report["relevance"] = relevance

        if relevance["relevance_level"] == "low":
            rejected_reports.append(report)
        else:
            relevant_reports.append(report)

    print(f"Relevant reports: {len(relevant_reports)}")
    print(f"Rejected reports: {len(rejected_reports)}")

    print("\n===== PRIORITY + RANKING =====\n")

    ranked_reports = rank_reports(
        relevant_reports
    )

    final_output = {
        "total_reports": len(reports),
        "relevant_reports": len(relevant_reports),
        "rejected_reports": len(rejected_reports),
        "ranked_emergencies": ranked_reports,
        "rejected": rejected_reports
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("===== TOP EMERGENCIES =====\n")

    for report in ranked_reports[:10]:

        relevance = report.get(
            "relevance",
            {}
        )

        print(
            f"#{report['rank']} | "
            f"{report['incident_type'].upper()} | "
            f"Priority: {report['priority']} | "
            f"Relevance: "
            f"{relevance.get('relevance_level', 'N/A').upper()} | "
            f"Credibility: {report['credibility']} | "
            f"Corroboration: {report['corroboration_score']} | "
            f"Actionability: {report['actionability']} | "
            f"Location: {report['location']}"
        )

    print(
        f"\nFinal output saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()