"""
Data loading module for Karen's Ear emergency reports.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple
from src.data.validator import SchemaValidator

class DataLoader:
    """
    Modular DataLoader designed to ingest emergency report datasets from JSON files.
    Allows easy replacement of dataset paths (e.g. sample vs production datasets).
    """

    def __init__(self, filepath: Union[str, Path] = "data/sample/sample_reports.json"):
        self.filepath = Path(filepath)

    def load_raw_data(self) -> List[Dict[str, Any]]:
        """Loads JSON report array from specified filepath."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Data file not found at: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON array of report objects, got {type(data).__name__}")

        return data

    def load_and_validate(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Loads report records and validates them against DATA_SCHEMA.md.
        Returns tuple of (records, validation_summary_dict).
        """
        records = self.load_raw_data()
        validation_report = SchemaValidator.validate_dataset(records)
        return records, validation_report
