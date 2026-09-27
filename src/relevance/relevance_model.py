"""
TF-IDF + Logistic Regression relevance model
for emergency reports.

Labels:
    0 = irrelevant
    1 = relevant

Output levels:
    LOW
    MEDIUM
    HIGH
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

    def __init__(self):

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True
        )

        self.model = LogisticRegression(
            max_iter=2000,
            random_state=42
        )

        self.is_trained = False

    def train(self, texts, labels):

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

        if not self.is_trained:
            raise ValueError(
                "Relevance model has not been trained yet."
            )

        predictions, probabilities = self.predict(
            [text]
        )

        pred_raw = str(predictions[0]).strip()
        try:
            ml_label = int(pred_raw)
        except ValueError:
            ml_label = 1 if pred_raw.lower() in ["high", "medium"] else 0

        classes = list(self.model.classes_)

        probability_map = {
            str(label): float(probability)
            for label, probability in zip(
                classes,
                probabilities[0]
            )
        }

        relevance_score = probability_map.get(
            "1",
            0.0
        )

        ml_confidence = max(
            probability_map.values()
        )

        emergency_signal = contains_emergency_signal(
            text
        )

        excluded_context = has_context_exclusion(
            text
        )

        relevance_level = self._get_level(
            relevance_score,
            emergency_signal,
            excluded_context
        )

        return {
            "relevance_level": relevance_level,
            "ml_level": (
                "high"
                if ml_label == 1
                else "low"
            ),
            "ml_prediction": ml_label,
            "ml_confidence": round(
                ml_confidence,
                3
            ),
            "relevance_score": round(
                relevance_score,
                3
            ),
            "emergency_signal": emergency_signal,
            "excluded_context": excluded_context
        }

    def _get_level(
        self,
        relevance_score,
        emergency_signal,
        excluded_context
    ):

        if relevance_score >= 0.75:
            level = "high"

        elif relevance_score >= 0.40:
            level = "medium"

        else:
            level = "low"

        # Safety net:
        # an emergency keyword can prevent
        # an important report from being discarded.
        if (
            level == "low"
            and emergency_signal
            and not excluded_context
        ):
            level = "medium"

        return level

    def save(self, filepath):

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

        saved = joblib.load(filepath)

        self.vectorizer = saved["vectorizer"]
        self.model = saved["model"]

        self.is_trained = True