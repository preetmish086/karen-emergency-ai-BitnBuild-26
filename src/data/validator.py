"""
Schema validation module adhering to DATA_SCHEMA.md.
"""
from typing import Dict, Any, List, Tuple

ALLOWED_INCIDENT_TYPES = {
    "fire",
    "explosion",
    "accident",
    "medical",
    "collapse",
    "flood",
    "crime",
    "missing_person",
    "unknown",
    "other"
}

ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}
ALLOWED_ACTIONABILITIES = {"low", "medium", "high"}

REQUIRED_FIELDS = {
    "report_id": str,
    "text": str,
    "incident_type": str,
    "severity": str,
    "actionability": str,
    "credibility": (int, float),
    "priority": (int, float)
}

class SchemaValidator:
    """Validates emergency report records against repository DATA_SCHEMA.md."""

    @staticmethod
    def validate_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates a single report record dictionary.
        Returns (is_valid, list_of_error_strings).
        """
        errors: List[str] = []

        if not isinstance(record, dict):
            return False, ["Record is not a dictionary/object"]

        # Check required fields presence and types
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in record:
                errors.append(f"Missing required field: '{field}'")
            elif not isinstance(record[field], expected_type):
                errors.append(f"Field '{field}' expected type {expected_type}, got {type(record[field]).__name__}")

        # Location field validation (string or None allowed)
        if "location" in record:
            loc = record["location"]
            if loc is not None and not isinstance(loc, str):
                errors.append(f"Field 'location' must be string or None, got {type(loc).__name__}")
        else:
            errors.append("Missing field: 'location'")

        # Categorical allowed values validation
        if "incident_type" in record and isinstance(record["incident_type"], str):
            if record["incident_type"] not in ALLOWED_INCIDENT_TYPES:
                errors.append(f"Invalid incident_type: '{record['incident_type']}'. Allowed: {sorted(list(ALLOWED_INCIDENT_TYPES))}")

        if "severity" in record and isinstance(record["severity"], str):
            if record["severity"] not in ALLOWED_SEVERITIES:
                errors.append(f"Invalid severity: '{record['severity']}'. Allowed: {sorted(list(ALLOWED_SEVERITIES))}")

        if "actionability" in record and isinstance(record["actionability"], str):
            if record["actionability"] not in ALLOWED_ACTIONABILITIES:
                errors.append(f"Invalid actionability: '{record['actionability']}'. Allowed: {sorted(list(ALLOWED_ACTIONABILITIES))}")

        # Numeric score range validation (0.0 to 1.0)
        if "credibility" in record and isinstance(record["credibility"], (int, float)):
            cred = float(record["credibility"])
            if not (0.0 <= cred <= 1.0):
                errors.append(f"credibility out of range [0.0, 1.0]: {cred}")

        if "priority" in record and isinstance(record["priority"], (int, float)):
            prio = float(record["priority"])
            if not (0.0 <= prio <= 1.0):
                errors.append(f"priority out of range [0.0, 1.0]: {prio}")

        return len(errors) == 0, errors

    @classmethod
    def validate_dataset(cls, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates an entire dataset array of report records.
        """
        if not isinstance(dataset, list):
            raise ValueError(f"Dataset must be a list of records, got {type(dataset).__name__}")

        total = len(dataset)
        valid_count = 0
        invalid_records = []

        for idx, record in enumerate(dataset):
            is_valid, errors = cls.validate_record(record)
            if is_valid:
                valid_count += 1
            else:
                invalid_records.append({
                    "index": idx,
                    "report_id": record.get("report_id", "N/A") if isinstance(record, dict) else "N/A",
                    "errors": errors
                })

        return {
            "total_records": total,
            "valid_records": valid_count,
            "invalid_records_count": len(invalid_records),
            "is_all_valid": valid_count == total,
            "invalid_details": invalid_records
        }
