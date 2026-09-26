from abc import ABC, abstractmethod
try:
    from role2.src.schemas.output_schema import (
        CredibilityAssessment,
        IncidentInfo,
        PeopleAffected,
        InformationCompleteness,
        LocationMetadata
    )
except (ImportError, ModuleNotFoundError):
    from src.schemas.output_schema import (
        CredibilityAssessment,
        IncidentInfo,
        PeopleAffected,
        InformationCompleteness,
        LocationMetadata
    )


class BaseCredibilityScorer(ABC):
    """
    Abstract base class for emergency report credibility scoring.
    Enforces explainable component signals.
    """

    @abstractmethod
    def score_credibility(
        self,
        text: str,
        incident: IncidentInfo,
        people: PeopleAffected,
        completeness: InformationCompleteness,
        location: LocationMetadata
    ) -> CredibilityAssessment:
        """
        Computes overall credibility score [0, 1] and factor decomposition dictionary.
        """
        pass
