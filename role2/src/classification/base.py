from abc import ABC, abstractmethod
from src.schemas.output_schema import IncidentInfo


class BaseIncidentClassifier(ABC):
    """
    Abstract base class for incident classifiers.
    Allows easy swapping with fine-tuned Transformer models (e.g. RoBERTa, BERT, Zero-Shot).
    """

    @abstractmethod
    def classify(self, text: str) -> IncidentInfo:
        """
        Classify input emergency text into an IncidentInfo object containing category and confidence.
        """
        pass
