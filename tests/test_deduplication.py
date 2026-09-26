"""
Unit tests for Deduplicator.
"""
import unittest
from src.data.deduplication import Deduplicator

class TestDeduplicator(unittest.TestCase):

    def test_deduplicate(self):
        records = [
            {"report_id": "R1", "text": "Fire near the station!"},
            {"report_id": "R2", "text": "fire near the station!   "}, # duplicate after normalization
            {"report_id": "R3", "text": "Flood near the river"}
        ]
        deduped, stats = Deduplicator.deduplicate(records)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(stats["records_before"], 3)
        self.assertEqual(stats["records_removed"], 1)
        self.assertEqual(stats["records_remaining"], 2)

if __name__ == "__main__":
    unittest.main()
