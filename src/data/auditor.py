"""
Automated Dataset Quality and Data Leakage Auditor.
"""
from typing import List, Dict, Any
from collections import Counter
from src.data.validator import SchemaValidator, ALLOWED_INCIDENT_TYPES

class DataQualityError(Exception):
    """Raised when dataset fails quality or data-leakage criteria."""
    pass

class DatasetAuditor:
    """
    Automated auditing module for Karen's Ear dataset pipeline.
    Ensures data quality, zero text leakage, and synthetic data isolation.
    """

    @classmethod
    def audit_dataset(
        cls,
        records: List[Dict[str, Any]],
        strict: bool = True
    ) -> Dict[str, Any]:
        """
        Audits a single unified dataset array.
        """
        total = len(records)
        real_count = sum(1 for r in records if not r.get("is_synthetic", False))
        syn_count = sum(1 for r in records if r.get("is_synthetic", False))

        source_dist = dict(Counter([r.get("source", "unknown") for r in records]))
        event_dist = dict(Counter([r.get("source_event", "unknown") for r in records]))
        type_dist = dict(Counter([r.get("incident_type", "unknown") for r in records]))

        empty_text_count = sum(1 for r in records if not r.get("text") or not str(r.get("text")).strip())
        invalid_type_count = sum(1 for r in records if r.get("incident_type") not in ALLOWED_INCIDENT_TYPES)

        texts = [str(r.get("text", "")).strip().lower() for r in records if r.get("text")]
        duplicate_text_count = total - len(set(texts))

        audit_report = {
            "total_records": total,
            "real_records": real_count,
            "synthetic_records": syn_count,
            "source_distribution": source_dist,
            "event_distribution": event_dist,
            "incident_type_distribution": type_dist,
            "empty_text_count": empty_text_count,
            "invalid_incident_type_count": invalid_type_count,
            "duplicate_text_count": duplicate_text_count
        }

        if strict:
            if empty_text_count > 0:
                raise DataQualityError(f"Data audit failed: Found {empty_text_count} records with empty text.")
            if invalid_type_count > 0:
                raise DataQualityError(f"Data audit failed: Found {invalid_type_count} records with invalid incident_type.")

        return audit_report

    @classmethod
    def audit_splits(
        cls,
        train_records: List[Dict[str, Any]],
        val_records: List[Dict[str, Any]],
        test_records: List[Dict[str, Any]],
        strict: bool = True
    ) -> Dict[str, Any]:
        """
        Audits train, validation, and test splits for quality and data leakage.
        """
        train_audit = cls.audit_dataset(train_records, strict=strict)
        val_audit = cls.audit_dataset(val_records, strict=strict)
        test_audit = cls.audit_dataset(test_records, strict=strict)

        # Leakage check 1: Synthetic data in validation or test sets
        syn_val = sum(1 for r in val_records if r.get("is_synthetic", False))
        syn_test = sum(1 for r in test_records if r.get("is_synthetic", False))

        # Leakage check 2: Text overlap between train, val, and test
        train_texts = {str(r.get("text", "")).strip().lower() for r in train_records if r.get("text")}
        val_texts = {str(r.get("text", "")).strip().lower() for r in val_records if r.get("text")}
        test_texts = {str(r.get("text", "")).strip().lower() for r in test_records if r.get("text")}

        train_val_overlap = len(train_texts.intersection(val_texts))
        train_test_overlap = len(train_texts.intersection(test_texts))
        val_test_overlap = len(val_texts.intersection(test_texts))

        split_audit = {
            "train": train_audit,
            "val": val_audit,
            "test": test_audit,
            "leakage_checks": {
                "synthetic_in_val_count": syn_val,
                "synthetic_in_test_count": syn_test,
                "train_val_text_overlap": train_val_overlap,
                "train_test_text_overlap": train_test_overlap,
                "val_test_text_overlap": val_test_overlap,
                "passed_leakage_checks": (
                    syn_val == 0 and syn_test == 0 and
                    train_val_overlap == 0 and train_test_overlap == 0 and val_test_overlap == 0
                )
            }
        }

        if strict:
            if syn_val > 0:
                raise DataQualityError(f"Leakage Audit Failed: {syn_val} synthetic records found in validation set.")
            if syn_test > 0:
                raise DataQualityError(f"Leakage Audit Failed: {syn_test} synthetic records found in test set.")
            if train_val_overlap > 0:
                raise DataQualityError(f"Leakage Audit Failed: {train_val_overlap} overlapping texts between train and val.")
            if train_test_overlap > 0:
                raise DataQualityError(f"Leakage Audit Failed: {train_test_overlap} overlapping texts between train and test.")

        return split_audit
