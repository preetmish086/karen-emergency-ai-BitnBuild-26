import re
from typing import Dict
try:
    from role2.src.schemas.output_schema import (
        CredibilityAssessment,
        IncidentInfo,
        PeopleAffected,
        InformationCompleteness,
        LocationMetadata,
        IncidentCategory
    )
    from role2.src.credibility.base import BaseCredibilityScorer
except (ImportError, ModuleNotFoundError):
    from src.schemas.output_schema import (
        CredibilityAssessment,
        IncidentInfo,
        PeopleAffected,
        InformationCompleteness,
        LocationMetadata,
        IncidentCategory
    )
    from src.credibility.base import BaseCredibilityScorer


class CredibilityScorer(BaseCredibilityScorer):
    """
    Explainable Credibility Assessor for emergency reports.
    Computes a overall credibility score in range [0, 1] using weighted component signals.

    Features requested by user:
    1. Location Density Consensus Boost: Higher credibility when multiple reports arrive from the same location.
    2. Casualty Reporting Bonus: Higher credibility signal when reporter explicitly details affected/injured people count.
    """

    FIRST_PERSON_MARKERS = [
        r"\bi\b", r"\bmy\b", r"\bme\b", r"\bwe\b", r"\bour\b", r"\bi saw\b", r"\bi witnessed\b",
        r"\bi noticed\b", r"\bi am\b", r"\bmy building\b", r"\bmy house\b", r"\bin front of me\b"
    ]

    TEMPORAL_MARKERS = [
        r"\bjust\b", r"\bnow\b", r"\bright now\b", r"\bthis morning\b", r"\bago\b",
        r"\bbroke out\b", r"\bis happening\b", r"\bcurrently\b", r"\b5 mins ago\b"
    ]

    def score_credibility(
        self,
        text: str,
        incident: IncidentInfo,
        people: PeopleAffected,
        completeness: InformationCompleteness,
        location: LocationMetadata
    ) -> CredibilityAssessment:
        clean_text = text.lower().strip()
        words = clean_text.split()
        word_count = len(words)

        # 1. First Person Observation Signal (weight 0.20)
        first_person_score = 0.50
        has_fp_marker = any(re.search(pattern, clean_text) for pattern in self.FIRST_PERSON_MARKERS)
        if has_fp_marker:
            first_person_score = 0.95
        elif word_count >= 4 and incident.type != IncidentCategory.UNKNOWN:
            first_person_score = 0.75

        # 2. Specificity Signal (weight 0.15)
        has_loc = location.has_gps or bool(location.text_location and location.text_location.strip())
        has_num = bool(re.search(r"\d+", clean_text))
        spec_base = 0.40
        if location.has_gps:
            spec_base += 0.35
        elif location.text_location:
            spec_base += 0.25
        if has_num:
            spec_base += 0.15
        if word_count >= 6:
            spec_base += 0.10
        specificity_score = min(1.0, spec_base)

        # 3. Coherence Signal (weight 0.15)
        coherence_score = 1.00
        if word_count < 3:
            coherence_score = 0.50
        if re.search(r"(.)\1{4,}", clean_text) or len(set(clean_text.replace(" ", ""))) < 4:
            coherence_score = 0.10

        # 4. Actionability Signal (weight 0.15)
        if incident.type == IncidentCategory.UNKNOWN:
            actionability_score = 0.30
        elif incident.type == IncidentCategory.OTHER:
            actionability_score = 0.50
        else:
            actionability_score = 0.95 if has_loc else 0.75

        # 5. Casualty Detail Reporting Signal (weight 0.10)
        # USER REQUEST: Gives bonus signal when reporter mentions affected/injured/dead count!
        has_casualty_count = any(
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
        casualty_reporting_signal = 1.00 if has_casualty_count else 0.50

        # 6. Location Density Consensus Signal (weight 0.15)
        # USER REQUEST: Higher credibility when multiple reports arrive from the same location!
        count = location.location_report_count
        if count >= 3:
            location_density_score = 1.00
        elif count == 2:
            location_density_score = 0.85
        else:
            location_density_score = 0.60

        # 7. Internal Consistency Signal (weight 0.10)
        consistency_score = 1.00
        if people.total_affected is not None:
            if people.injured is not None and people.injured > people.total_affected:
                consistency_score = 0.30
            if people.dead is not None and people.dead > people.total_affected:
                consistency_score = 0.30

        # 8. Information Completeness Factor
        info_completeness_factor = completeness.completeness_score

        # Weighted Credibility Score Aggregation (weights sum to 1.00)
        final_score = (
            0.20 * first_person_score +
            0.15 * specificity_score +
            0.15 * coherence_score +
            0.15 * actionability_score +
            0.10 * casualty_reporting_signal +
            0.15 * location_density_score +
            0.10 * consistency_score
        )

        final_score = round(min(1.0, max(0.0, final_score)), 2)

        factors: Dict[str, float] = {
            "first_person_observation": round(first_person_score, 2),
            "specificity": round(specificity_score, 2),
            "coherence": round(coherence_score, 2),
            "actionability": round(actionability_score, 2),
            "casualty_reporting_signal": round(casualty_reporting_signal, 2),
            "location_density": round(location_density_score, 2),
            "internal_consistency": round(consistency_score, 2),
            "information_completeness": round(info_completeness_factor, 2),
        }

        return CredibilityAssessment(score=final_score, factors=factors)
