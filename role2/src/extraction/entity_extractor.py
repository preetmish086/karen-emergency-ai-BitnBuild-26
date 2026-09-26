import re
from typing import Optional, Dict

try:
    from role2.src.schemas.output_schema import PeopleAffected
    from role2.src.extraction.base import BaseEntityExtractor
    from role2.src.preprocessing.text_preprocessor import TextPreprocessor
except (ImportError, ModuleNotFoundError):
    from src.schemas.output_schema import PeopleAffected
    from src.extraction.base import BaseEntityExtractor
    from src.preprocessing.text_preprocessor import TextPreprocessor


class EntityExtractor(BaseEntityExtractor):
    """
    Pattern-based entity and casualty extractor.
    Enforces the CRITICAL NO-HALLUCINATION RULE:
    Returns explicit None for any unstated casualty information.
    """

    def __init__(self, preprocessor: Optional[TextPreprocessor] = None):
        self.preprocessor = preprocessor or TextPreprocessor()

    def extract_people(self, text: str) -> PeopleAffected:
        if not text or not text.strip():
            return PeopleAffected()

        # Step 1: Normalize number words to digits for pattern matching
        normalized_text = self.preprocessor.normalize_number_words(text)

        injured_count = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+(?:people\s+)?(?:were\s+)?(?:injured|hurt|wounded)",
                r"(?:injured|hurt|wounded)\s+(\d+)",
                r"(\d+)\s+(?:others\s+)?(?:were\s+)?injured",
                r"(\d+)\s+injuries"
            ]
        )

        dead_count = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+(?:people\s+)?(?:were\s+)?(?:killed|dead|died|fatalities)",
                r"(?:killed|dead)\s+(\d+)",
                r"(\d+)\s+fatalities",
                r"(\d+)\s+person\s+died",
                r"(\d+)\s+people\s+died"
            ]
        )

        missing_count = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+(?:people\s+)?(?:are\s+|were\s+)?missing",
                r"missing\s+(\d+)"
            ]
        )

        trapped_count = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+(?:people\s+)?(?:are\s+|were\s+)?trapped",
                r"trapped\s+(\d+)"
            ]
        )

        rescued_count = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+(?:people\s+)?(?:were\s+)?rescued",
                r"rescued\s+(\d+)"
            ]
        )

        evacuated_count = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+(?:people\s+)?(?:were\s+)?evacuated",
                r"evacuated\s+(\d+)"
            ]
        )

        # Explicit total affected phrase check (e.g. "4 people were injured", "total of 5 victims")
        explicit_total = self._extract_category_count(
            normalized_text,
            patterns=[
                r"(\d+)\s+people\s+(?:were\s+)?(?:affected|involved|injured)",
                r"total\s+of\s+(\d+)\s+(?:people|victims|affected)",
                r"(\d+)\s+victims"
            ]
        )

        # Calculate logical total_affected if missing explicit statement
        total_affected = explicit_total

        if total_affected is None:
            counts = [c for c in [injured_count, dead_count, missing_count, trapped_count] if c is not None]
            if counts:
                total_affected = sum(counts)

        return PeopleAffected(
            total_affected=total_affected,
            injured=injured_count,
            dead=dead_count,
            missing=missing_count,
            trapped=trapped_count,
            rescued=rescued_count,
            evacuated=evacuated_count
        )

    def _extract_category_count(self, text: str, patterns: list) -> Optional[int]:
        """
        Scans normalized text against regex patterns to extract an explicit integer count.
        Returns None if no matching explicit number is found.
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    count = int(match.group(1))
                    return count
                except (IndexError, ValueError):
                    continue
        return None
