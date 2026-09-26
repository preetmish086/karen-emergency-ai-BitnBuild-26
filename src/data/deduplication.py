"""
Deduplication Module for Karen's Ear data pipeline.
"""
from typing import List, Dict, Any, Tuple
from collections import OrderedDict
from src.data.preprocessor import TextPreprocessor

class Deduplicator:
    """
    Deduplicates emergency report records using normalized text.
    Preserves first occurrence of each unique report text.
    """

    @classmethod
    def deduplicate(cls, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Deduplicates list of record dicts based on normalized text.
        Returns (deduplicated_records, deduplication_summary_stats).
        """
        records_before = len(records)
        seen_texts = set()
        deduped_records: List[Dict[str, Any]] = []

        for rec in records:
            if not isinstance(rec, dict):
                continue

            raw_text = rec.get("text", "")
            norm_text = TextPreprocessor.clean_text(raw_text)

            if not norm_text:
                continue

            if norm_text in seen_texts:
                continue

            seen_texts.add(norm_text)
            deduped_records.append(rec)

        records_remaining = len(deduped_records)
        records_removed = records_before - records_remaining

        stats = {
            "records_before": records_before,
            "records_removed": records_removed,
            "records_remaining": records_remaining
        }

        return deduped_records, stats
