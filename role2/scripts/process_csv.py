import os
import sys
import json
import pandas as pd

# Ensure role2 path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.process_report import EmergencyReportPipeline


def process_csv_dataset(csv_path: str, max_rows: int = 10):
    print(f"==================================================")
    print(f"PROCESSING CSV DATASET: {os.path.basename(csv_path)}")
    print(f"==================================================\n")

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"Total rows in dataset: {len(df)}")
    print(f"Columns: {list(df.columns)}\n")

    pipeline = EmergencyReportPipeline(csv_dataset_path=csv_path)

    processed_count = 0
    for idx, row in df.head(max_rows).iterrows():
        report_input = {
            "report_id": str(row.get("report_id", f"R{idx:05d}")),
            "text": str(row.get("text", "")),
            "location": str(row["location"]) if "location" in row and pd.notna(row["location"]) else None,
            "latitude": float(row["latitude"]) if "latitude" in row and pd.notna(row["latitude"]) else None,
            "longitude": float(row["longitude"]) if "longitude" in row and pd.notna(row["longitude"]) else None,
        }

        output = pipeline.process(report_input)
        processed_count += 1

        print(f"--- Sample {processed_count}/{max_rows}: {output.report_id} ---")
        print(json.dumps(output.model_dump(), indent=2))
        print("-" * 50)

    print(f"\nSuccessfully processed {processed_count} sample reports from {os.path.basename(csv_path)}!")


def main():
    default_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "nyc_emergency_reports_clean.csv"))
    csv_file = sys.argv[1] if len(sys.argv) > 1 else default_csv
    process_csv_dataset(csv_file, max_rows=5)


if __name__ == "__main__":
    main()
