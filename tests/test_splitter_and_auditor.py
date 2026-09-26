"""
Unit tests for DatasetSplitter and DatasetAuditor (Leakage & Quality checks).
"""
import unittest
from src.data.splitter import DatasetSplitter
from src.data.auditor import DatasetAuditor, DataQualityError

class TestSplitterAndAuditor(unittest.TestCase):

    def setUp(self):
        self.records = [
            {"report_id": f"R{i}", "text": f"Emergency text example {i}", "incident_type": "fire" if i % 2 == 0 else "flood", "is_synthetic": False}
            for i in range(50)
        ]

    def test_dataset_splitter_synthetic_isolation(self):
        train, val, test, stats = DatasetSplitter.create_splits(
            self.records, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, enable_synthetic_aug=True, augmentation_ratio=0.2, seed=42
        )
        self.assertEqual(stats["synthetic_in_val_count"], 0)
        self.assertEqual(stats["synthetic_in_test_count"], 0)
        self.assertGreater(stats["synthetic_in_train_count"], 0)

    def test_auditor_pass_leakage_checks(self):
        train, val, test, stats = DatasetSplitter.create_splits(
            self.records, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, enable_synthetic_aug=True, seed=42
        )
        audit_res = DatasetAuditor.audit_splits(train, val, test, strict=True)
        self.assertTrue(audit_res["leakage_checks"]["passed_leakage_checks"])

    def test_auditor_fails_on_synthetic_in_val(self):
        train = [{"report_id": "T1", "text": "Train fire", "incident_type": "fire", "is_synthetic": False}]
        val = [{"report_id": "V1", "text": "Val fire", "incident_type": "fire", "is_synthetic": True}] # Leaked synthetic record!
        test = [{"report_id": "E1", "text": "Test fire", "incident_type": "fire", "is_synthetic": False}]

        with self.assertRaises(DataQualityError):
            DatasetAuditor.audit_splits(train, val, test, strict=True)

if __name__ == "__main__":
    unittest.main()
