"""
Unit tests for centralized LabelMapper.
"""
import unittest
from src.data.mapping import LabelMapper, CANONICAL_INCIDENT_TYPES

class TestLabelMapper(unittest.TestCase):

    def test_canonical_incident_types(self):
        expected_types = {"fire", "explosion", "accident", "medical", "collapse", "flood", "crime", "missing_person", "unknown", "other"}
        self.assertEqual(CANONICAL_INCIDENT_TYPES, expected_types)

    def test_high_confidence_event_mapping(self):
        rec_wildfire = {"source": "crisislex", "source_event": "2012_Colorado_wildfires", "text": "Smoke over the hills"}
        inc, reason = LabelMapper.map_record(rec_wildfire)
        self.assertEqual(inc, "fire")

        rec_bombing = {"source": "crisislex", "source_event": "2013_Boston_bombings", "text": "Loud noise downtown"}
        inc, reason = LabelMapper.map_record(rec_bombing)
        self.assertEqual(inc, "explosion")

        rec_crash = {"source": "crisislex", "source_event": "2013_Spain_train_crash", "text": "Carriage derailed"}
        inc, reason = LabelMapper.map_record(rec_crash)
        self.assertEqual(inc, "accident")

    def test_keyword_evidence_overrides(self):
        rec_med = {"source": "humaid", "source_label": "other_relevant_information", "text": "Send an ambulance immediately to the scene!"}
        inc, reason = LabelMapper.map_record(rec_med)
        self.assertEqual(inc, "medical")

        rec_missing = {"source": "humaid", "source_label": "other_relevant_information", "text": "Missing person report: child lost near central park"}
        inc, reason = LabelMapper.map_record(rec_missing)
        self.assertEqual(inc, "missing_person")

    def test_apply_mapping(self):
        records = [
            {"source": "crisislex", "source_event": "2013_Savar_building_collapse", "text": "Building fell down"},
            {"source": "sample", "incident_type": "flood", "text": "High water"}
        ]
        mapped, stats = LabelMapper.apply_mapping(records)
        self.assertEqual(mapped[0]["incident_type"], "collapse")
        self.assertEqual(mapped[1]["incident_type"], "flood")

if __name__ == "__main__":
    unittest.main()
