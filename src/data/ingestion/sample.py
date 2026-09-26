"""
Sample dataset ingestion module for sample_reports.json.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Union

class SampleIngestor:
    """
    Ingestor for repository sample reports JSON file.
    """

    def __init__(self, filepath: Union[str, Path] = "data/sample/sample_reports.json"):
        self.filepath = Path(filepath)

    def load_raw_records(self) -> List[Dict[str, Any]]:
        """
        Loads sample_reports.json records.
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f"Sample file not found at: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        records: List[Dict[str, Any]] = []
        for r in data:
            if not isinstance(r, dict):
                continue
            records.append({
                "report_id": r.get("report_id"),
                "text": r.get("text", ""),
                "incident_type": r.get("incident_type", "unknown"),
                "source": "sample",
                "source_event": "sample",
                "source_label": r.get("incident_type", "unknown"),
                "is_synthetic": False
            })

        return records

def load_sample(filepath: Union[str, Path] = "data/sample/sample_reports.json") -> List[Dict[str, Any]]:
    ingestor = SampleIngestor(filepath=filepath)
    return ingestor.load_raw_records()
