"""
Text Preprocessing and Data Leakage Prevention Module.
"""
import re
from typing import List, Dict, Any, Tuple

class TextPreprocessor:
    """
    Deterministic Text Preprocessor for emergency reports.
    Preserves emergency vocabulary while removing noisy URLs and social media artifacts.
    Guarantees zero data leakage by isolating text features X from target labels y.
    """

    # URL regex pattern
    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
    # Twitter handle pattern
    USER_HANDLE_PATTERN = re.compile(r"@\w+", re.IGNORECASE)
    # Multiple whitespace pattern
    WHITESPACE_PATTERN = re.compile(r"\s+")

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Cleans raw text string:
        - Lowercases
        - Removes URLs
        - Removes @user mentions
        - Normalizes whitespace
        """
        if not text or not isinstance(text, str):
            return ""

        # Lowercase
        text = text.lower().strip()

        # Remove URLs
        text = cls.URL_PATTERN.sub("", text)

        # Remove @user mentions
        text = cls.USER_HANDLE_PATTERN.sub("", text)

        # Remove RT prefix if present
        text = re.sub(r"^rt\s+", "", text)

        # Normalize whitespace
        text = cls.WHITESPACE_PATTERN.sub(" ", text).strip()

        return text

    @classmethod
    def preprocess_records(cls, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Preprocesses text field of all records in place (returns new list of dicts).
        Filters out records with empty text.
        """
        cleaned_records: List[Dict[str, Any]] = []

        for rec in records:
            if not isinstance(rec, dict):
                continue

            raw_text = rec.get("text", "")
            cleaned = cls.clean_text(raw_text)

            if not cleaned:
                continue

            rec_copy = dict(rec)
            rec_copy["text"] = cleaned
            cleaned_records.append(rec_copy)

        return cleaned_records

    @classmethod
    def extract_features_and_targets(
        cls, records: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """
        Extracts feature list X (cleaned text) and target list y (incident_type).
        Excludes metadata/downstream fields to strictly prevent data leakage.
        """
        X: List[str] = []
        y: List[str] = []

        for record in records:
            if not isinstance(record, dict):
                continue

            raw_text = record.get("text", "")
            cleaned = cls.clean_text(raw_text)
            if not cleaned:
                continue

            incident_type = record.get("incident_type", "other")
            if not incident_type:
                incident_type = "other"

            X.append(cleaned)
            y.append(incident_type)

        return X, y
