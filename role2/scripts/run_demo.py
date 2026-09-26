import os
import sys
import json

# Ensure role2 path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.process_report import EmergencyReportPipeline


def main():
    print("==================================================")
    print("ROLE 2: NLP + Incident Understanding + Credibility")
    print("==================================================\n")

    sample_file = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "sample_reports.json")
    with open(sample_file, "r") as f:
        reports = json.load(f)

    pipeline = EmergencyReportPipeline()

    for idx, report_data in enumerate(reports, 1):
        print(f"--- Processing Report {idx}/{len(reports)}: {report_data['report_id']} ---")
        output = pipeline.process(report_data)
        print(json.dumps(output.model_dump(), indent=2))
        print("-" * 50)


if __name__ == "__main__":
    main()
