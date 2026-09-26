"""
Unit tests for TextPreprocessor and Data Leakage Prevention.
"""
import unittest
from src.data.preprocessor import TextPreprocessor

class TestTextPreprocessor(unittest.TestCase):

    def test_clean_text(self):
        raw = "RT @user Check out http://example.com for Emergency Fire info!!!   "
        cleaned = TextPreprocessor.clean_text(raw)
        self.assertEqual(cleaned, "check out for emergency fire info!!!")

    def test_extract_features_and_targets_leakage_protection(self):
        records = [
            {
                "report_id": "R001",
                "text": "Huge explosion near market",
                "incident_type": "explosion",
                "severity": "critical",
                "actionability": "high",
                "credibility": 0.95,
                "priority": 0.99,
                "location": "market"
            }
        ]
        X, y = TextPreprocessor.extract_features_and_targets(records)
        self.assertEqual(X, ["huge explosion near market"])
        self.assertEqual(y, ["explosion"])

        # Verify no metadata values leaked into X
        for x_item in X:
            self.assertNotIn("0.95", x_item)
            self.assertNotIn("critical", x_item)

if __name__ == "__main__":
    unittest.main()
