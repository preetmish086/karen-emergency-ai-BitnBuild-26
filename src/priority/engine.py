"""Priority calculation engine for Karen's Ear emergency dispatch."""

from typing import Dict, Any, Union
from src.schema import SeverityLevel, ActionabilityLevel


class PriorityEngine:
    """Calculates prioritized dispatch score based on severity, actionability,

    credibility, and incident cluster corroboration.
    """

    SEVERITY_WEIGHTS = {
        SeverityLevel.CRITICAL: 1.0,
        SeverityLevel.HIGH: 0.75,
        SeverityLevel.MEDIUM: 0.45,
        SeverityLevel.LOW: 0.20,
    }

    ACTIONABILITY_WEIGHTS = {
        ActionabilityLevel.HIGH: 1.0,
        ActionabilityLevel.MEDIUM: 0.60,
        ActionabilityLevel.LOW: 0.25,
    }

    # Weight distribution summing to 1.0
    W_SEVERITY = 0.45
    W_ACTIONABILITY = 0.25
    W_CREDIBILITY = 0.22
    W_CORROBORATION = 0.08

    @classmethod
    def calculate(
        cls,
        severity: Union[SeverityLevel, str],
        actionability: Union[ActionabilityLevel, str],
        credibility: float,
        cluster_size: int = 1,
    ) -> float:
        """Calculate a composite priority score strictly between 0.0 and 1.0.

        Args:
            severity: Severity level (critical, high, medium, low)
            actionability: Actionability level (high, medium, low)
            credibility: Float confidence score in [0.0, 1.0]
            cluster_size: Number of corroborating reports in the incident cluster

        Returns:
            Normalized float priority score in [0.0, 1.0]
        """
        if isinstance(severity, SeverityLevel):
            sev_key = severity
        else:
            sev_key = SeverityLevel(str(severity).split(".")[-1].lower())

        if isinstance(actionability, ActionabilityLevel):
            act_key = actionability
        else:
            act_key = ActionabilityLevel(str(actionability).split(".")[-1].lower())

        sev_score = cls.SEVERITY_WEIGHTS.get(sev_key, 0.45)
        act_score = cls.ACTIONABILITY_WEIGHTS.get(act_key, 0.50)
        cred_score = max(0.0, min(1.0, float(credibility)))

        # Corroboration factor: dimishing returns as more independent reports confirm the incident
        # 1 report = 0.0 corroboration bonus; 5+ reports = 1.0 max corroboration
        corrob_score = min(1.0, max(0.0, (cluster_size - 1) / 4.0))

        raw_priority = (
            cls.W_SEVERITY * sev_score
            + cls.W_ACTIONABILITY * act_score
            + cls.W_CREDIBILITY * cred_score
            + cls.W_CORROBORATION * corrob_score
        )

        # Baseline offset calibration to ensure high-severity actionable reports are prioritized
        # and minor reports remain appropriately low
        calibrated = raw_priority + 0.03

        # Clamp strictly between 0.0 and 1.0
        final_priority = max(0.0, min(1.0, calibrated))
        return round(final_priority, 2)

    @classmethod
    def explain(
        cls,
        severity: Union[SeverityLevel, str],
        actionability: Union[ActionabilityLevel, str],
        credibility: float,
        cluster_size: int = 1,
    ) -> Dict[str, Any]:
        """Provides an explainable breakdown of the priority score for 911 dispatchers."""
        if isinstance(severity, SeverityLevel):
            sev_key = severity
        else:
            sev_key = SeverityLevel(str(severity).split(".")[-1].lower())

        if isinstance(actionability, ActionabilityLevel):
            act_key = actionability
        else:
            act_key = ActionabilityLevel(str(actionability).split(".")[-1].lower())

        sev_score = cls.SEVERITY_WEIGHTS.get(sev_key, 0.45)
        act_score = cls.ACTIONABILITY_WEIGHTS.get(act_key, 0.50)
        cred_score = max(0.0, min(1.0, float(credibility)))
        corrob_score = min(1.0, max(0.0, (cluster_size - 1) / 4.0))

        final_priority = cls.calculate(severity, actionability, credibility, cluster_size)

        return {
            "final_priority": final_priority,
            "components": {
                "severity": {
                    "level": sev_key.value,
                    "normalized": sev_score,
                    "contribution": round(sev_score * cls.W_SEVERITY, 3),
                },
                "actionability": {
                    "level": act_key.value,
                    "normalized": act_score,
                    "contribution": round(act_score * cls.W_ACTIONABILITY, 3),
                },
                "credibility": {
                    "score": cred_score,
                    "contribution": round(cred_score * cls.W_CREDIBILITY, 3),
                },
                "corroboration": {
                    "cluster_size": cluster_size,
                    "contribution": round(corrob_score * cls.W_CORROBORATION, 3),
                },
            },
            "recommendation": (
                "IMMEDIATE_DISPATCH"
                if final_priority >= 0.85
                else "EXPEDITE"
                if final_priority >= 0.70
                else "ROUTINE_QUEUE"
                if final_priority >= 0.45
                else "MONITOR_ONLY"
            ),
        }


def calculate_priority(
    severity: Union[SeverityLevel, str],
    actionability: Union[ActionabilityLevel, str],
    credibility: float,
    cluster_size: int = 1,
) -> float:
    """Convenience helper to calculate priority score."""
    return PriorityEngine.calculate(severity, actionability, credibility, cluster_size)
