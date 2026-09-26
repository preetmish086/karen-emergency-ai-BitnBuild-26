"""
Unit tests for data ingestion modules.
"""
import unittest
from pathlib import Path
from src.data.ingestion.crisislex import load_crisislex
from src.data.ingestion.humaid import load_humaid
from src.data.ingestion.sample import load_sample

class TestIngestion(unittest.TestCase):

    def test_sample_ingestion(self):
        records = load_sample("data/sample/sample_reports.json")
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0]["source"], "sample")
        self.assertFalse(records[0]["is_synthetic"])

    def test_crisislex_ingestion(self):
        c_dir = Path("temp_crisislex/data/CrisisLexT26")
        if c_dir.exists():
            records = load_crisislex(c_dir)
            self.assertGreater(len(records), 0)
            self.assertEqual(records[0]["source"], "crisislex")
            self.assertEqual(records[0]["informativeness"], "Related and informative")

    def test_humaid_ingestion(self):
        h_dir = Path("temp_humaid")
        if h_dir.exists():
            records = load_humaid(h_dir)
            self.assertGreater(len(records), 0)
            self.assertEqual(records[0]["source"], "humaid")
            self.assertIn("source_split", records[0])

if __name__ == "__main__":
    unittest.main()
