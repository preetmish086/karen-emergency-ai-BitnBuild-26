"""
Unit tests for Karen's Ear data pipeline foundation.
"""
import unittest
from pathlib import Path
from src.data.loader import DataLoader
from src.data.validator import SchemaValidator
from src.data.inspector import DatasetInspector
from src.data.preprocessor import TextPreprocessor

SAMPLE_DATA_PATH = "data/sample/sample_reports.json"

class TestDataPipeline(unittest.TestCase):

    def setUp(self):
        self.loader = DataLoader(SAMPLE_DATA_PATH)

    def test_load_sample_reports(self):
        records = self.loader.load_raw_data()
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 8, "Expected 8 sample records in sample_reports.json")

    def test_schema_validation_on_sample_reports(self):
        records, report = self.loader.load_and_validate()
        self.assertTrue(report["is_all_valid"], f"Validation failed with details: {report['invalid_details']}")
        self.assertEqual(report["total_records"], 8)
        self.assertEqual(report["valid_records"], 8)
        self.assertEqual(report["invalid_records_count"], 0)

    def test_schema_validation_invalid_records(self):
        # Invalid credibility > 1.0
        invalid_record_1 = {
            "report_id": "R999",
            "text": "Invalid report test",
            "incident_type": "fire",
            "location": "test street",
            "severity": "high",
            "actionability": "high",
            "credibility": 1.5,
            "priority": 0.5
        }
        is_valid, errors = SchemaValidator.validate_record(invalid_record_1)
        self.assertFalse(is_valid)
        self.assertTrue(any("credibility out of range" in err for err in errors))

        # Invalid incident_type
        invalid_record_2 = {
            "report_id": "R998",
            "text": "Invalid incident type test",
            "incident_type": "alien_attack",
            "location": "downtown",
            "severity": "low",
            "actionability": "low",
            "credibility": 0.5,
            "priority": 0.5
        }
        is_valid, errors = SchemaValidator.validate_record(invalid_record_2)
        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid incident_type" in err for err in errors))

    def test_dataset_inspection(self):
        records = self.loader.load_raw_data()
        stats = DatasetInspector.inspect(records)
        self.assertEqual(stats["num_records"], 8)
        self.assertIn("class_distribution", stats)
        self.assertIn("missing_values", stats)
        self.assertIn("duplicates", stats)
        
        # Verify specific counts in sample dataset
        self.assertEqual(stats["missing_values"]["location"], 0)
        self.assertEqual(stats["missing_values"]["incident_type"], 1) # R005 has "unknown"
        self.assertEqual(stats["duplicates"]["duplicate_report_ids_count"], 0)

    def test_preprocessor_extraction_and_leakage_prevention(self):
        records = self.loader.load_raw_data()
        X, y = TextPreprocessor.extract_features_and_targets(records)
        
        self.assertEqual(len(X), 8)
        self.assertEqual(len(y), 8)
        
        # Verify text cleaning
        self.assertEqual(X[0], "huge explosion near the central market! several people are injured!")
        
        # Verify targets
        self.assertEqual(y[0], "explosion")
        self.assertEqual(y[4], "unknown") # R005 is "unknown"
        
        # Leakage check: X must contain only strings, no metadata dictionaries or numeric fields
        for x_item in X:
            self.assertIsInstance(x_item, str)
            self.assertNotIn("credibility", x_item)
            self.assertNotIn("priority", x_item)

    def test_modular_loader_substitution(self):
        loader = DataLoader("data/sample/sample_reports.json")
        self.assertEqual(loader.filepath, Path("data/sample/sample_reports.json"))


if __name__ == "__main__":
    unittest.main()
