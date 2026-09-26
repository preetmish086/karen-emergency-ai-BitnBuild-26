"""
Centralized Label Mapping Module.
Adheres strictly to project canonical incident_type values in DATA_SCHEMA.md.
"""
import re
from typing import Dict, Any, Tuple, Optional, List

CANONICAL_INCIDENT_TYPES = {
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

# High-confidence CrisisLex Event to Canonical Mapping
CRISISLEX_EVENT_MAP: Dict[str, str] = {
    "2012_Colorado_wildfires": "fire",
    "2013_Australia_bushfire": "fire",
    "2013_Brazil_nightclub_fire": "fire",
    "2013_Boston_bombings": "explosion",
    "2013_West_Texas_explosion": "explosion",
    "2012_Venezuela_refinery": "explosion",
    "2013_Glasgow_helicopter_crash": "accident",
    "2013_Lac_Megantic_train_crash": "accident",
    "2013_NY_train_crash": "accident",
    "2013_Spain_train_crash": "accident",
    "2013_LA_airport_shootings": "crime",
    "2013_Savar_building_collapse": "collapse",
    "2012_Philipinnes_floods": "flood",
    "2013_Alberta_floods": "flood",
    "2013_Colorado_floods": "flood",
    "2013_Manila_floods": "flood",
    "2013_Queensland_floods": "flood",
    "2013_Sardinia_floods": "flood",
    "2013_Russia_meteor": "other",
    "2013_Singapore_haze": "other",
}

# Regex pattern matchers for text-level incident evidence
FIRE_KW = re.compile(r"\b(wildfire|bushfire|blaze|firefighters|flames|house fire|building fire|fire truck)\b", re.IGNORECASE)
EXPLOSION_KW = re.compile(r"\b(explosion|detonated|blast|bombing|exploded|refinery explosion)\b", re.IGNORECASE)
ACCIDENT_KW = re.compile(r"\b(helicopter crash|train crash|plane crash|car crash|derailment|collision|traffic accident|vehicle crash)\b", re.IGNORECASE)
COLLAPSE_KW = re.compile(r"\b(building collapse|structure collapse|bridge collapse|collapsed building|rubble|trapped under debris)\b", re.IGNORECASE)
FLOOD_KW = re.compile(r"\b(flash flood|flooding|inundated|submerged|overflow|drowning|rising water|floodwaters)\b", re.IGNORECASE)
CRIME_KW = re.compile(r"\b(shooting|active shooter|gunfire|stabbed|armed robbery|assaulted|hostage|terrorist attack)\b", re.IGNORECASE)
MEDICAL_KW = re.compile(r"\b(ambulance|hospitalized|paramedic|triage|resuscitation|bleeding|severe injuries|cardiac arrest|trauma team|first responders|medical aid)\b", re.IGNORECASE)
MISSING_KW = re.compile(r"\b(missing person|missing child|disappeared|have you seen|search for missing|whereabouts of)\b", re.IGNORECASE)

class LabelMapper:
    """
    Centralized, auditable label mapping utility.
    Maps raw records from CrisisLex, HumAID, or Sample sources to canonical incident_type.
    """

    @classmethod
    def map_record(cls, record: Dict[str, Any]) -> Tuple[str, str]:
        """
        Maps a record dictionary to (canonical_incident_type, mapping_reason).
        Returns canonical type string and rationale.
        """
        source = record.get("source", "")
        text = record.get("text", "")
        existing_type = record.get("incident_type")

        # 1. Sample dataset check
        if source == "sample" and existing_type in CANONICAL_INCIDENT_TYPES:
            return existing_type, "sample_direct_canonical"

        # 2. Synthetic dataset check
        if record.get("is_synthetic") and existing_type in CANONICAL_INCIDENT_TYPES:
            return existing_type, "synthetic_direct_canonical"

        # 3. High-priority text-level keyword evidence check across all sources
        if MISSING_KW.search(text):
            return "missing_person", "text_keyword_missing_person"
        if MEDICAL_KW.search(text):
            return "medical", "text_keyword_medical"
        if CRIME_KW.search(text):
            return "crime", "text_keyword_crime"
        if COLLAPSE_KW.search(text):
            return "collapse", "text_keyword_collapse"
        if EXPLOSION_KW.search(text):
            return "explosion", "text_keyword_explosion"
        if FIRE_KW.search(text):
            return "fire", "text_keyword_fire"
        if ACCIDENT_KW.search(text):
            return "accident", "text_keyword_accident"
        if FLOOD_KW.search(text):
            return "flood", "text_keyword_flood"

        # 4. CrisisLex event-level high-confidence mapping
        if source == "crisislex":
            source_event = record.get("source_event", "")
            if source_event in CRISISLEX_EVENT_MAP:
                return CRISISLEX_EVENT_MAP[source_event], f"crisislex_event_{source_event}"

        # 5. HumAID specific label mapping rules
        if source == "humaid":
            h_label = record.get("source_label", "")
            if h_label == "missing_or_found_people":
                return "missing_person", "humaid_label_missing_or_found_people"
            elif h_label == "injured_or_dead_people":
                return "medical", "humaid_label_injured_or_dead_people"
            elif h_label in ("infrastructure_and_utility_damage", "displaced_people_and_evacuations", "rescue_volunteering_or_donation_effort", "requests_or_urgent_needs"):
                return "other", f"humaid_generic_{h_label}"
            elif h_label in ("not_humanitarian", "sympathy_and_support", "other_relevant_information"):
                return "other", f"humaid_non_incident_{h_label}"

        # 6. Fallback
        return "other", "default_fallback_other"

    @classmethod
    def apply_mapping(cls, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Applies mapping to a list of records.
        Appends 'incident_type' and 'mapping_reason' fields.
        Returns mapped records and summary count of reasons.
        """
        mapped_records: List[Dict[str, Any]] = []
        mapping_stats: Dict[str, int] = {}

        for rec in records:
            rec_copy = dict(rec)
            canonical_type, reason = cls.map_record(rec_copy)
            rec_copy["incident_type"] = canonical_type
            rec_copy["mapping_reason"] = reason

            mapped_records.append(rec_copy)
            mapping_stats[reason] = mapping_stats.get(reason, 0) + 1

        return mapped_records, mapping_stats
