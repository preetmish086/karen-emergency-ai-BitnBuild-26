import os
import sys
import json
import time
import pandas as pd

# Ensure role2 path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline.process_report import EmergencyReportPipeline


def export_all_reports(csv_path: str, output_json_path: str):
    print("==================================================")
    print("BATCH PROCESSING ENTIRE DATASET FOR ROLE 2 OUTPUT")
    print("==================================================\n")

    if not os.path.exists(csv_path):
        print(f"Error: Dataset CSV file not found at {csv_path}")
        return

    print(f"Loading dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"Total rows to process: {total_rows}\n")

    start_time = time.time()
    pipeline = EmergencyReportPipeline(csv_dataset_path=csv_path)

    processed_list = []

    for idx, row in df.iterrows():
        report_input = {
            "report_id": str(row.get("report_id", f"R{idx:05d}")),
            "text": str(row.get("text", "")),
            "location": str(row["location"]) if "location" in row and pd.notna(row["location"]) else None,
            "latitude": float(row["latitude"]) if "latitude" in row and pd.notna(row["latitude"]) else None,
            "longitude": float(row["longitude"]) if "longitude" in row and pd.notna(row["longitude"]) else None,
        }

        output = pipeline.process(report_input)
        processed_list.append(output.model_dump())

        if (idx + 1) % 2000 == 0 or (idx + 1) == total_rows:
            elapsed = time.time() - start_time
            print(f"Progress: {idx + 1}/{total_rows} reports processed ({elapsed:.2f}s elapsed)...")

    # Save to JSON file
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(processed_list, f, indent=2)

    total_time = time.time() - start_time
    file_size_mb = os.path.getsize(output_json_path) / (1024 * 1024)

    print("\n==================================================")
    print("BATCH EXPORT COMPLETED SUCCESSFULLY!")
    print("==================================================")
    print(f"Total Reports Processed: {len(processed_list)}")
    print(f"Execution Time: {total_time:.2f} seconds")
    print(f"Output JSON File: {output_json_path}")
    print(f"File Size: {file_size_mb:.2f} MB\n")


def main():
    default_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "nyc_emergency_reports_clean.csv"))
    default_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "role2_processed_output.json"))

    csv_file = sys.argv[1] if len(sys.argv) > 1 else default_csv
    out_file = sys.argv[2] if len(sys.argv) > 2 else default_out

    export_all_reports(csv_file, out_file)


if __name__ == "__main__":
    main()
