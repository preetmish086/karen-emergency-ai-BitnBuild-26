"""
Unit tests for ModelPersistence and EmergencyClassifier inference interface.
"""
import unittest
from pathlib import Path
from src.models.baseline_classifier import TFIDFLogisticRegressionBaseline
from src.models.persistence import ModelPersistence
from src.models.inference import EmergencyClassifier

class TestPersistenceAndInference(unittest.TestCase):

    def setUp(self):
        self.test_model_path = Path("models/test_baseline_model.joblib")
        self.X = ["Fire near downtown", "Explosion at factory", "Road accident"]
        self.y = ["fire", "explosion", "accident"]

        self.model = TFIDFLogisticRegressionBaseline()
        self.model.fit(self.X, self.y)

    def tearDown(self):
        if self.test_model_path.exists():
            self.test_model_path.unlink()

    def test_save_and_load_model(self):
        saved_path = ModelPersistence.save_model(self.model, filepath=self.test_model_path)
        self.assertTrue(saved_path.exists())

        loaded_model = ModelPersistence.load_model(saved_path)
        self.assertTrue(loaded_model.is_fitted)

        preds = loaded_model.predict(["Fire near downtown"])
        self.assertEqual(preds[0], "fire")

    def test_emergency_classifier_inference_interface(self):
        ModelPersistence.save_model(self.model, filepath=self.test_model_path)
        classifier = EmergencyClassifier(model_path=self.test_model_path)

        res = classifier.predict_incident("Smoke and fire reported downtown")
        self.assertIn("incident_type", res)
        self.assertIn("confidence", res)
        self.assertEqual(res["incident_type"], "fire")
        self.assertGreater(res["confidence"], 0.0)

        batch_res = classifier.predict_batch(["Explosion at factory", "Car accident"])
        self.assertEqual(len(batch_res), 2)
        self.assertEqual(batch_res[0]["incident_type"], "explosion")
        self.assertEqual(batch_res[1]["incident_type"], "accident")

if __name__ == "__main__":
    unittest.main()
