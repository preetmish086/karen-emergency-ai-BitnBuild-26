import os
import sys
import json

# Ensure role2 path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.process_report import EmergencyReportPipeline


def test_custom_inputs():
    print("==================================================")
    print("ROLE 2: LIVE EMERGENCY REPORT INTELLIGENCE DEMO")
    print("==================================================\n")

    pipeline = EmergencyReportPipeline(window_minutes=30)

    test_reports = [
        {
            "report_id": "TEST_LIVE_01",
            "text": "I saw a car accident and 4 people were injured near Times Square.",
            "location": "Times Square, NYC",
            "timestamp": "2026-09-27T09:00:00Z"
        },
        {
            "report_id": "TEST_LIVE_02",
            "text": "There is a massive vehicle crash near Times Square, send help fast!",
            "location": "Times Square, NYC",
            "timestamp": "2026-09-27T09:10:00Z"  # Same location + Same 30-min time window -> Density Boost!
        },
        {
            "report_id": "TEST_LIVE_03",
            "text": "Fire broke out in my building.",  # Fire report without casualties -> No Hallucination!
            "location": "29-27 41st Avenue, Long Island City",
            "timestamp": "2026-09-27T14:00:00Z"
        },
        {
            "report_id": "TEST_LIVE_04",
            "text": "Someone stole my phone near Times Square",  # Crime report 12 hours later -> Time window reset!
            "location": "Times Square, NYC",
            "timestamp": "2026-09-27T21:00:00Z"
        }
    ]

    for idx, report_data in enumerate(test_reports, 1):
        print(f"--- Processing Input {idx}/{len(test_reports)} ---")
        print(f"Raw Input Text: '{report_data['text']}'")
        print(f"Location Metadata: {report_data.get('location')}")
        print(f"Timestamp: {report_data['timestamp']}")

        output = pipeline.process(report_data)
        print("\nStructured Role 2 Output JSON:")
        print(json.dumps(output.model_dump(), indent=2))
        print("=" * 60 + "\n")


if __name__ == "__main__":
    test_custom_inputs()
