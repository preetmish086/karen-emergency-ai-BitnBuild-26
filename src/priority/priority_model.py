"""
ML-based Emergency Priority Model.

The model predicts a continuous priority score between 0 and 1.
"""

import joblib

from sklearn.ensemble import RandomForestRegressor

from src.priority.features import extract_features


class PriorityModel:
    """
    Machine-learning model for emergency priority scoring.
    """

    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

        self.is_trained = False

    def train(self, X, y):
        """
        Train the priority model.

        X = input features
        y = labelled priority scores
        """

        self.model.fit(X, y)

        self.is_trained = True

    def predict(self, X):
        """
        Predict priority scores.

        Returns:
            list of priority scores between 0 and 1.
        """

        if not self.is_trained:
            raise ValueError(
                "Priority model has not been trained yet."
            )

        predictions = self.model.predict(X)

        # Keep scores inside 0-1
        predictions = [
            max(0.0, min(float(score), 1.0))
            for score in predictions
        ]

        return predictions

    def predict_emergency(
        self,
        severity,
        actionability,
        credibility,
        report_count
    ):
        """
        Predict priority for one emergency.
        """

        features = extract_features(
            severity=severity,
            actionability=actionability,
            credibility=credibility,
            report_count=report_count
        )

        score = self.predict([features])[0]

        return round(score, 3)

    def save(self, filepath):
        """Save trained model to disk."""

        if not self.is_trained:
            raise ValueError(
                "Cannot save an untrained model."
            )

        joblib.dump(self.model, filepath)

    def load(self, filepath):
        """Load a previously trained model."""

        self.model = joblib.load(filepath)
        self.is_trained = True