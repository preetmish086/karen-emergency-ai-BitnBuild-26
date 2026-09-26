"""
Unit tests for Baseline ML Classifier models.
"""
import unittest
from src.models.baseline_classifier import TFIDFLogisticRegressionBaseline, TFIDFNaiveBayesBaseline

class TestBaselineModel(unittest.TestCase):

    def setUp(self):
        self.X_train = [
            "Huge explosion near central market with injured people",
            "Smoke and fire coming from residential house",
            "Car accident on highway blocking traffic",
            "Flash flood waters rising rapidly near river",
            "Building structure collapsed trapping residents"
        ]
        self.y_train = ["explosion", "fire", "accident", "flood", "collapse"]

        self.X_test = [
            "Heavy smoke and flames from house fire",
            "Vehicle crash on highway"
        ]
        self.y_test = ["fire", "accident"]

    def test_logistic_regression_baseline(self):
        model = TFIDFLogisticRegressionBaseline(C=1.0)
        model.fit(self.X_train, self.y_train)
        self.assertTrue(model.is_fitted)

        preds = model.predict(self.X_test)
        self.assertEqual(len(preds), 2)

        conf_preds = model.predict_confidence(self.X_test)
        self.assertEqual(len(conf_preds), 2)
        self.assertIsInstance(conf_preds[0][1], float)

        metrics = model.evaluate(self.X_test, self.y_test)
        self.assertIn("accuracy", metrics)
        self.assertIn("macro_f1", metrics)

    def test_naive_bayes_baseline(self):
        model = TFIDFNaiveBayesBaseline(alpha=1.0)
        model.fit(self.X_train, self.y_train)
        self.assertTrue(model.is_fitted)

        preds = model.predict(self.X_test)
        self.assertEqual(len(preds), 2)

if __name__ == "__main__":
    unittest.main()
