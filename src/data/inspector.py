"""
Dataset inspection module for Karen's Ear emergency reports.
"""
from typing import List, Dict, Any
from collections import Counter

class DatasetInspector:
    """
    Utility module for auditing dataset statistics:
    - Number of records
    - Class distribution (incident_type)
    - Missing / fallback values
    - Duplicate report IDs & duplicate report texts
    """

    @staticmethod
    def inspect(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_records = len(records)

        # 1. Class distribution for target variable 'incident_type'
        incident_types = [
            r.get("incident_type", "missing") if isinstance(r, dict) else "invalid_record"
            for r in records
        ]
        class_distribution = dict(Counter(incident_types))

        # 2. Missing/fallback value counts
        missing_values = {
            "report_id": sum(1 for r in records if not isinstance(r, dict) or not r.get("report_id")),
            "text": sum(1 for r in records if not isinstance(r, dict) or not r.get("text")),
            "incident_type": sum(
                1 for r in records if not isinstance(r, dict) or not r.get("incident_type") or r.get("incident_type") == "unknown"
            ),
            "location": sum(1 for r in records if not isinstance(r, dict) or r.get("location") is None),
            "severity": sum(1 for r in records if not isinstance(r, dict) or not r.get("severity")),
            "actionability": sum(1 for r in records if not isinstance(r, dict) or not r.get("actionability")),
            "credibility": sum(1 for r in records if not isinstance(r, dict) or r.get("credibility") is None),
            "priority": sum(1 for r in records if not isinstance(r, dict) or r.get("priority") is None),
        }

        # 3. Duplicate checks
        report_ids = [r.get("report_id") for r in records if isinstance(r, dict) and r.get("report_id")]
        texts = [r.get("text", "").strip().lower() for r in records if isinstance(r, dict) and r.get("text")]

        duplicate_report_ids = [item for item, count in Counter(report_ids).items() if count > 1]
        duplicate_texts = [item for item, count in Counter(texts).items() if count > 1]

        return {
            "num_records": total_records,
            "class_distribution": class_distribution,
            "missing_values": missing_values,
            "duplicates": {
                "duplicate_report_ids_count": len(duplicate_report_ids),
                "duplicate_texts_count": len(duplicate_texts),
                "duplicate_report_ids": duplicate_report_ids,
                "duplicate_texts": duplicate_texts,
            }
        }
