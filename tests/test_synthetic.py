"""
Unit tests for SyntheticAugmenter.
"""
import unittest
from src.data.synthetic import SyntheticAugmenter

class TestSyntheticAugmenter(unittest.TestCase):

    def test_generate_synthetic_samples(self):
        targets = {"medical": 5, "missing_person": 3}
        syn = SyntheticAugmenter.generate_synthetic_samples(targets, seed=42)
        self.assertEqual(len(syn), 8)
        for s in syn:
            self.assertTrue(s["is_synthetic"])
            self.assertEqual(s["source"], "synthetic")

    def test_augment_training_set(self):
        real_train = [
            {"report_id": f"R{i}", "text": "Fire report text", "incident_type": "fire", "is_synthetic": False}
            for i in range(20)
        ]
        augmented, stats = SyntheticAugmenter.augment_training_set(real_train, augmentation_ratio=0.2, seed=42)
        self.assertGreater(len(augmented), len(real_train))
        self.assertEqual(stats["real_train_count"], 20)

if __name__ == "__main__":
    unittest.main()
