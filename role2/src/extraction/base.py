from abc import ABC, abstractmethod
from src.schemas.output_schema import PeopleAffected


class BaseEntityExtractor(ABC):
    """
    Abstract base class for emergency entity and casualty extraction.
    Enforces strict non-hallucination contract.
    """

    @abstractmethod
    def extract_people(self, text: str) -> PeopleAffected:
        """
        Extracts explicit count of affected, injured, dead, missing, trapped, rescued, evacuated people.
        Returns explicit None for any category not explicitly mentioned.
        """
        pass
