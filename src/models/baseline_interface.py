"""
Abstract Baseline Model Interface.
Enforces decoupling between dataset pipeline and future ML model implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaselineModelInterface(ABC):
    """
    Abstract contract for baseline incident classification models.
    No model training is performed in this interface.
    """

    @abstractmethod
    def fit(self, X: List[str], y: List[str]) -> "BaselineModelInterface":
        """
        Fit the baseline classifier on text features X and target classes y.
        """
        pass

    @abstractmethod
    def predict(self, X: List[str]) -> List[str]:
        """
        Predict incident_type for input text reports X.
        """
        pass

    @abstractmethod
    def evaluate(self, X: List[str], y: List[str]) -> Dict[str, float]:
        """
        Evaluate classification metrics (accuracy, macro F1, etc.).
        """
        pass
