import re
from typing import Optional
from src.schemas.output_schema import InformationCompleteness, PeopleAffected, IncidentInfo, LocationMetadata


class CompletenessEvaluator:
    """
    Evaluates report information completeness separately from credibility.
    Produces structured availability flags (including optional GPS & manual location) and completeness_score [0, 1].
    """

    def evaluate(
        self,
        text: str,
        incident: IncidentInfo,
        people: PeopleAffected,
        location: LocationMetadata
    ) -> InformationCompleteness:
        clean_text = text.lower()

        # Casualty flags
        has_casualty_info = any(
            val is not None for val in [
                people.total_affected,
                people.injured,
                people.dead,
                people.missing,
                people.trapped,
                people.rescued,
                people.evacuated
            ]
        )
        has_affected_cnt = people.total_affected is not None
        has_injury_info = (people.injured is not None) or (people.dead is not None)

        # Location flag: True if valid GPS coordinates OR manual/extracted text location exists
        has_location_info = location.has_gps or bool(location.text_location and location.text_location.strip())

        # Completeness scoring components
        # 1. Base incident description presence (0.30)
        incident_present_score = 0.30 if incident.type.value not in ["unknown", "other"] else 0.15

        # 2. Location availability score (0.25) - full score if GPS, partial if text location
        if location.has_gps:
            location_score = 0.25
        elif location.text_location:
            location_score = 0.20
        else:
            location_score = 0.0

        # 3. Temporal context mention (0.10)
        temporal_indicators = ["just now", "right now", "ago", "this morning", "today", "currently", "happening"]
        has_temp_mention = any(re.search(r"\b" + re.escape(ind) + r"\b", clean_text) for ind in temporal_indicators)
        temporal_score = 0.10 if has_temp_mention else 0.0

        # 4. Casualty details presence (0.20)
        casualty_score = 0.20 if has_casualty_info else 0.0

        # 5. Text descriptive richness (0.15)
        word_count = len(text.split())
        richness_score = 0.15 if word_count >= 6 else (0.10 if word_count >= 3 else 0.05)

        total_completeness = incident_present_score + location_score + temporal_score + casualty_score + richness_score
        completeness_score = round(min(1.0, max(0.0, total_completeness)), 2)

        return InformationCompleteness(
            has_casualty_information=has_casualty_info,
            has_affected_count=has_affected_cnt,
            has_injury_information=has_injury_info,
            has_location_information=has_location_info,
            completeness_score=completeness_score
        )
