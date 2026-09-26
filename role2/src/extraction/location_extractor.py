import re
from typing import Optional


class LocationExtractor:
    """
    Extracts manual / textual location mentions from input report text or metadata.
    Handles fallback when authoritative GPS coordinates are absent or optional.
    """

    LOCATION_PREPOSITIONS = [
        r"\b(?:near|at|on|outside|inside|in front of|opposite|behind|near the)\s+([A-Z0-9][A-Za-z0-9\s,\.-]{2,45})"
    ]

    ADDRESS_PATTERNS = [
        r"\b\d+[\w\s-]*\s+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Plaza|Parkway|Pkwy|Tower|Complex|Building|Pl|Drive|Dr)\b[\w\s,]*",
        r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*(?:Manhattan|Brooklyn|Queens|The Bronx|Staten Island)\b",
        r"\b(?:Times Square|Penn Plaza|Central Market|Eighth Avenue Tower|LIC Plaza|MetroTech Center|Atlantic Terminal|Queens Plaza Complex)\b"
    ]

    def extract_location_text(self, text: str, input_location_metadata: Optional[str] = None) -> Optional[str]:
        """
        Extracts textual location description.
        Prioritizes explicit manual location metadata (e.g. from CSV), followed by textual extraction from report text.
        """
        # 1. Use manual location metadata if explicitly provided (e.g., from CSV column)
        if input_location_metadata and input_location_metadata.strip():
            return input_location_metadata.strip()

        if not text:
            return None

        # 2. Match explicit address / landmark patterns in text
        for pattern in self.ADDRESS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        # 3. Match prepositional location phrases ("near Times Square", "at the bank on Main Road")
        for pattern in self.LOCATION_PREPOSITIONS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                loc = match.group(1).strip()
                # Clean trailing punctuation or non-location words
                loc = re.split(r"\b(?:please|and|there|we|i|help|send|with|is|were)\b", loc, flags=re.IGNORECASE)[0]
                loc = loc.strip(" ,.!?")
                if len(loc) >= 3:
                    return loc

        return None
