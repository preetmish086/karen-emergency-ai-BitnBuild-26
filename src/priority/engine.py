"""Priority Engine for Karen's Ear emergency triage."""

from typing import Union, Dict, Any

SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "low": 0.25,
}

ACTIONABILITY_WEIGHTS = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.2,
}


def calculate_priority(
    severity: Union[str, Any],
    actionability: Union[str, Any],
    credibility: float,
    cluster_size: int = 1,
) -> float:
    """Calculates the final priority score (0.0 to 1.0) using the exact formula:

    (0.45 * severity_weight) + (0.35 * actionability_weight) + (0.20 * credibility)
    """
    sev_key = str(severity).split(".")[-1].lower().strip()
    act_key = str(actionability).split(".")[-1].lower().strip()

    sev_weight = SEVERITY_WEIGHTS.get(sev_key, 0.5)
    act_weight = ACTIONABILITY_WEIGHTS.get(act_key, 0.6)

    # Ensure credibility is bounded between 0.0 and 1.0
    cred = max(0.0, min(1.0, float(credibility)))

    raw_score = (0.45 * sev_weight) + (0.35 * act_weight) + (0.20 * cred)

    # Corroboration bonus if multiple reports exist in cluster
    if cluster_size > 1:
        raw_score += min(0.05, (cluster_size - 1) * 0.015)

    # Return clamped, rounded float
    return round(max(0.0, min(1.0, raw_score)), 4)


class PriorityEngine:
    @staticmethod
    def calculate(
        severity: Union[str, Any],
        actionability: Union[str, Any],
        credibility: float,
        cluster_size: int = 1,
    ) -> float:
        return calculate_priority(severity, actionability, credibility, cluster_size)

    @staticmethod
    def explain(
        severity: Union[str, Any],
        actionability: Union[str, Any],
        credibility: float,
        cluster_size: int = 1,
    ) -> Dict[str, Any]:
        p = calculate_priority(severity, actionability, credibility, cluster_size)
        return {
            "final_priority": p,
            "components": {
                "severity": str(severity),
                "actionability": str(actionability),
                "credibility": credibility,
                "cluster_size": cluster_size,
            },
            "recommendation": "IMMEDIATE_DISPATCH" if p >= 0.8 else "MONITOR",
        }
