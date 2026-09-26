"""
Model Evaluation Metrics Module.
Calculates Accuracy, Precision, Recall, Macro/Weighted F1, Per-class breakdown, and Confusion Matrix.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

class ModelEvaluator:
    """
    Evaluation utility for baseline multiclass incident classification models.
    """

    @classmethod
    def evaluate_predictions(
        cls,
        y_true: List[str],
        y_pred: List[str],
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Computes classification metrics for predicted y_pred against y_true.
        """
        if not y_true or not y_pred:
            raise ValueError("y_true and y_pred cannot be empty")

        if labels is None:
            labels = sorted(list(set(y_true).union(set(y_pred))))

        acc = float(accuracy_score(y_true, y_pred))

        # Macro metrics
        macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average="macro", zero_division=0
        )

        # Weighted metrics
        w_p, w_r, w_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average="weighted", zero_division=0
        )

        # Per-class metrics
        p_class, r_class, f1_class, supp_class = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average=None, zero_division=0
        )

        per_class_metrics: Dict[str, Dict[str, float]] = {}
        for idx, lbl in enumerate(labels):
            per_class_metrics[lbl] = {
                "precision": float(p_class[idx]),
                "recall": float(r_class[idx]),
                "f1_score": float(f1_class[idx]),
                "support": int(supp_class[idx])
            }

        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred, labels=labels)

        return {
            "accuracy": float(acc),
            "macro_precision": float(macro_p),
            "macro_recall": float(macro_r),
            "macro_f1": float(macro_f1),
            "weighted_precision": float(w_p),
            "weighted_recall": float(w_r),
            "weighted_f1": float(w_f1),
            "labels": labels,
            "per_class_metrics": per_class_metrics,
            "confusion_matrix": cm.tolist()
        }
