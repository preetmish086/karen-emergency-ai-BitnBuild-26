"""
TF-IDF + Logistic Regression relevance model
for emergency reports.

The model produces three relevance levels:

HIGH
UNCERTAIN
LOW

A keyword safety net prevents unusual emergency
wording from being silently discarded.
"""

import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.relevance.preprocess import (
    clean_text,
    contains_emergency_signal,
    has_context_exclusion
)


class RelevanceModel:
    """
    Emergency report relevance classifier.
    """

    LEVELS = [
        "low",
        "uncertain",
        "high"
    ]

    def __init__(self):

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True
        )

        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42
        )

        self.is_trained = False

    def train(self, texts, labels):
        """
        Train the multiclass relevance model.

        labels should contain:
            low
            uncertain
            high
        """

        cleaned_texts = [
            clean_text(text)
            for text in texts
        ]

        X = self.vectorizer.fit_transform(
            cleaned_texts
        )

        self.model.fit(
            X,
            labels
        )

        self.is_trained = True

    def predict(self, texts):
        """
        Predict relevance levels.

        Returns:
            predictions,
            probabilities
        """

        if not self.is_trained:
            raise ValueError(
                "Relevance model has not been trained yet."
            )

        cleaned_texts = [
            clean_text(text)
            for text in texts
        ]

        X = self.vectorizer.transform(
            cleaned_texts
        )

        predictions = self.model.predict(X)

        probabilities = self.model.predict_proba(X)

        return predictions, probabilities

    def predict_one(self, text):
        """
        Predict relevance for one report.

        Returns:
            ML prediction,
            ML confidence,
            final relevance level,
            emergency keyword signal.
        """

        if not self.is_trained:
            raise ValueError(
                "Relevance model has not been trained yet."
            )

        prediction, probabilities = self.predict(
            [text]
        )

        pred_val = str(prediction[0]).lower().strip()
        if pred_val in ["1", "high"]:
            ml_level = "high"
        elif pred_val in ["medium"]:
            ml_level = "medium"
        else:
            ml_level = "low"

        classes = list(
            self.model.classes_
        )

        probability_map = {
            str(label): float(probability)
            for label, probability in zip(
                classes,
                probabilities[0]
            )
        }

        ml_confidence = max(
            probability_map.values()
        )

        emergency_signal = contains_emergency_signal(
            text
        )

        excluded_context = has_context_exclusion(
            text
        )

        final_level = self._apply_safety_net(
            ml_level=ml_level,
            emergency_signal=emergency_signal,
            excluded_context=excluded_context,
            probability_map=probability_map
        )

        return {
            "relevance_level": final_level,
            "ml_level": ml_level,
            "ml_confidence": round(
                ml_confidence,
                3
            ),
            "emergency_signal": emergency_signal,
            "relevance_score": round(
                self._calculate_score(
                    probability_map
                ),
                3
            )
        }

    def _calculate_score(self, probability_map):
        high_probability = probability_map.get("1", 0.0)
        low_probability = probability_map.get("0", 0.0)

        return (
            0.9 * high_probability
            + 0.1 * low_probability
        )

    def _apply_safety_net(
        self,
        ml_level,
        emergency_signal,
        excluded_context,
        probability_map
    ):
        """
        Prevent potentially important emergency reports
        from being silently classified as LOW.

        Strong emergency wording can raise LOW -> UNCERTAIN.

        It does NOT automatically raise a report to HIGH.
        """

        if (
            emergency_signal
            and ml_level == "low"
            and not excluded_context
        ):
            return "uncertain"

        return ml_level

    def save(self, filepath):
        """
        Save the trained model.
        """

        if not self.is_trained:
            raise ValueError(
                "Cannot save an untrained model."
            )

        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "model": self.model
            },
            filepath
        )

    def load(self, filepath):
        """
        Load a previously trained model.
        """

        saved = joblib.load(
            filepath
        )

        self.vectorizer = saved[
            "vectorizer"
        ]

        self.model = saved[
            "model"
        ]

        self.is_trained = True