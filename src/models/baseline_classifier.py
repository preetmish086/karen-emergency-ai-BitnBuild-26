"""
Baseline ML Model Implementations.
Provides TF-IDF + Logistic Regression and TF-IDF + Multinomial Naive Bayes models
inheriting from BaselineModelInterface.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

from src.models.baseline_interface import BaselineModelInterface
from src.models.evaluator import ModelEvaluator
from src.data.preprocessor import TextPreprocessor

class TFIDFLogisticRegressionBaseline(BaselineModelInterface):
    """
    Primary Baseline ML Classifier: TF-IDF + Logistic Regression.
    """

    def __init__(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        max_features: int = 10000,
        sublinear_tf: bool = True,
        C: float = 1.0,
        max_iter: int = 1000,
        random_state: int = 42
    ):
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.sublinear_tf = sublinear_tf
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state

        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            sublinear_tf=self.sublinear_tf
        )
        self.classifier = LogisticRegression(
            C=self.C,
            max_iter=self.max_iter,
            random_state=self.random_state
        )
        self.is_fitted = False
        self.classes_: List[str] = []

    def fit(self, X: List[str], y: List[str]) -> "TFIDFLogisticRegressionBaseline":
        """Fits vectorizer and classifier on text features X and labels y."""
        X_clean = [TextPreprocessor.clean_text(x) for x in X]
        X_vec = self.vectorizer.fit_transform(X_clean)
        self.classifier.fit(X_vec, y)
        self.classes_ = list(self.classifier.classes_)
        self.is_fitted = True
        return self

    def predict(self, X: List[str]) -> List[str]:
        """Predicts incident_type targets for input texts X."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting.")
        X_clean = [TextPreprocessor.clean_text(x) for x in X]
        X_vec = self.vectorizer.transform(X_clean)
        preds = self.classifier.predict(X_vec)
        return list(preds)

    def predict_confidence(self, X: List[str]) -> List[Tuple[str, float]]:
        """Predicts (incident_type, confidence_score) for input texts X."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting.")
        X_clean = [TextPreprocessor.clean_text(x) for x in X]
        X_vec = self.vectorizer.transform(X_clean)
        probs = self.classifier.predict_proba(X_vec)
        
        results: List[Tuple[str, float]] = []
        for row in probs:
            best_idx = int(np.argmax(row))
            best_class = self.classes_[best_idx]
            confidence = float(row[best_idx])
            results.append((best_class, confidence))
            
        return results

    def evaluate(self, X: List[str], y: List[str]) -> Dict[str, Any]:
        """Evaluates classification performance on given evaluation set."""
        preds = self.predict(X)
        return ModelEvaluator.evaluate_predictions(y, preds, labels=self.classes_)


class TFIDFNaiveBayesBaseline(BaselineModelInterface):
    """
    Secondary Baseline ML Classifier: TF-IDF + Multinomial Naive Bayes.
    """

    def __init__(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        max_features: int = 10000,
        sublinear_tf: bool = True,
        alpha: float = 1.0
    ):
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.sublinear_tf = sublinear_tf
        self.alpha = alpha

        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            sublinear_tf=self.sublinear_tf
        )
        self.classifier = MultinomialNB(alpha=self.alpha)
        self.is_fitted = False
        self.classes_: List[str] = []

    def fit(self, X: List[str], y: List[str]) -> "TFIDFNaiveBayesBaseline":
        X_clean = [TextPreprocessor.clean_text(x) for x in X]
        X_vec = self.vectorizer.fit_transform(X_clean)
        self.classifier.fit(X_vec, y)
        self.classes_ = list(self.classifier.classes_)
        self.is_fitted = True
        return self

    def predict(self, X: List[str]) -> List[str]:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting.")
        X_clean = [TextPreprocessor.clean_text(x) for x in X]
        X_vec = self.vectorizer.transform(X_clean)
        preds = self.classifier.predict(X_vec)
        return list(preds)

    def predict_confidence(self, X: List[str]) -> List[Tuple[str, float]]:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting.")
        X_clean = [TextPreprocessor.clean_text(x) for x in X]
        X_vec = self.vectorizer.transform(X_clean)
        probs = self.classifier.predict_proba(X_vec)
        
        results: List[Tuple[str, float]] = []
        for row in probs:
            best_idx = int(np.argmax(row))
            best_class = self.classes_[best_idx]
            confidence = float(row[best_idx])
            results.append((best_class, confidence))
            
        return results

    def evaluate(self, X: List[str], y: List[str]) -> Dict[str, Any]:
        preds = self.predict(X)
        return ModelEvaluator.evaluate_predictions(y, preds, labels=self.classes_)
