"""
Baseline incident classification model for Karen's Ear.

Implements the abstract BaselineModelInterface using a simple, standard NLP
baseline: TF-IDF features over report text feeding a Multinomial Naive Bayes
classifier. The vectorizer and classifier are composed in a single scikit-learn
Pipeline so feature extraction stays coupled to the fitted model and cannot leak
between training and inference.
"""
from typing import List, Dict, Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score

from src.data.preprocessor import TextPreprocessor
from src.models.baseline_interface import BaselineModelInterface


class BaselineModel(BaselineModelInterface):
    """
    TF-IDF + Multinomial Naive Bayes baseline for predicting 'incident_type'
    from emergency report text.

    Both the vectorizer and classifier are injectable so the baseline can be
    swapped or tuned without changing callers.
    """

    def __init__(
        self,
        vectorizer: Optional[Any] = None,
        classifier: Optional[Any] = None,
    ):
        self.vectorizer = vectorizer if vectorizer is not None else TfidfVectorizer(ngram_range=(1, 2))
        self.classifier = classifier if classifier is not None else MultinomialNB(alpha=0.3)
        self.pipeline = Pipeline([
            ("tfidf", self.vectorizer),
            ("clf", self.classifier),
        ])
        self.classes_: List[str] = []

    def _clean(self, X: List[str]) -> List[str]:
        """Applies the shared data-pipeline text cleaning to raw report texts."""
        return [TextPreprocessor.clean_text(x) for x in X]

    def fit(self, X: List[str], y: List[str]) -> "BaselineModel":
        """
        Fit the baseline classifier on text features X and target classes y.
        """
        clean_X = self._clean(X)
        self.pipeline.fit(clean_X, y)
        self.classes_ = list(self.pipeline.named_steps["clf"].classes_)
        return self

    def predict(self, X: List[str]) -> List[str]:
        """
        Predict incident_type for input text reports X.
        """
        clean_X = self._clean(X)
        return [str(pred) for pred in self.pipeline.predict(clean_X)]

    def predict_proba(self, X: List[str]) -> np.ndarray:
        """
        Return per-class probabilities for input text reports X, columns ordered
        to match self.classes_.
        """
        clean_X = self._clean(X)
        return self.pipeline.predict_proba(clean_X)

    def evaluate(self, X: List[str], y: List[str]) -> Dict[str, float]:
        """
        Evaluate classification metrics (accuracy, macro F1, weighted F1).
        """
        predictions = self.predict(X)
        return {
            "accuracy": float(accuracy_score(y, predictions)),
            "macro_f1": float(f1_score(y, predictions, average="macro", zero_division=0)),
            "weighted_f1": float(f1_score(y, predictions, average="weighted", zero_division=0)),
            "num_samples": len(y),
        }
