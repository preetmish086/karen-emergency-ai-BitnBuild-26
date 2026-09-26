import json

from src.priority.emergency_priority import rank_reports


INPUT_PATH = "data/sample/test_classification.json"
OUTPUT_PATH = "data/priority_output.json"


def main():

    print("Loading emergency reports...")

    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        reports = json.load(file)

    # Support both:
    # [ {...}, {...} ]
    #
    # and:
    # { "reports": [ {...}, {...} ] }

    if isinstance(reports, dict):
        reports = reports.get("reports", [])

    print(f"Reports received: {len(reports)}")

    ranked_reports = rank_reports(reports)

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            ranked_reports,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n===== TOP PRIORITY EMERGENCIES =====\n")

    for report in ranked_reports[:10]:

        print(
            f"Rank #{report['rank']} | "
            f"{report['incident_type'].upper()} | "
            f"Priority: {report['priority']} | "
            f"Credibility: {report['credibility']} | "
            f"Actionability: {report['actionability']} | "
            f"Location: {report['location']}"
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()