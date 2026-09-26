"""
Training / evaluation entrypoint for the baseline incident classification model.

Runnable from the repository root as either:
    python -m src.models.train_baseline
    python src/models/train_baseline.py

Loads the sample dataset, reports class distribution, performs a leave-one-out
evaluation (robust on very small data), then fits a final model on all records
and prints example predictions. No model artifacts are persisted.
"""
from collections import Counter
from typing import List, Tuple

from sklearn.metrics import accuracy_score, f1_score

from src.data.loader import DataLoader
from src.data.preprocessor import TextPreprocessor
from src.models.baseline_model import BaselineModel


def load_features_and_targets() -> Tuple[List[str], List[str]]:
    """Loads and validates the dataset, then extracts (X, y)."""
    loader = DataLoader()
    records, validation_report = loader.load_and_validate()

    if not validation_report["is_all_valid"]:
        print("Warning: dataset contains invalid records:")
        for detail in validation_report["invalid_details"]:
            print(f"  - record {detail['index']} ({detail['report_id']}): {detail['errors']}")

    return TextPreprocessor.extract_features_and_targets(records)


def leave_one_out_evaluation(X: List[str], y: List[str]) -> Tuple[float, float]:
    """
    Manual leave-one-out evaluation.

    Chosen over a stratified split / cross-validation because the sample dataset
    is tiny (8 records across 6 classes, several with a single example), which
    makes stratified folds impossible and split-based scores unreliable.
    """
    predictions: List[str] = []
    truths: List[str] = []

    for i in range(len(X)):
        X_train = X[:i] + X[i + 1:]
        y_train = y[:i] + y[i + 1:]

        model = BaselineModel().fit(X_train, y_train)
        predictions.append(model.predict([X[i]])[0])
        truths.append(y[i])

    accuracy = accuracy_score(truths, predictions)
    macro_f1 = f1_score(truths, predictions, average="macro", zero_division=0)
    return float(accuracy), float(macro_f1)


def main() -> None:
    X, y = load_features_and_targets()

    print("Karen's Ear - Baseline incident classifier (TF-IDF + MultinomialNB)")
    print("=" * 68)
    print(f"Records loaded: {len(X)}")
    print(f"Class distribution: {dict(Counter(y))}")
    print()

    loo_accuracy, loo_macro_f1 = leave_one_out_evaluation(X, y)
    print("Leave-one-out evaluation:")
    print(f"  Accuracy : {loo_accuracy:.3f}")
    print(f"  Macro F1 : {loo_macro_f1:.3f}")
    print("  Note: the sample dataset is far too small for a meaningful score.")
    print()

    final_model = BaselineModel().fit(X, y)
    metrics = final_model.evaluate(X, y)
    print("Final model fit on all records (training-set metrics):")
    print(f"  Accuracy    : {metrics['accuracy']:.3f}")
    print(f"  Macro F1    : {metrics['macro_f1']:.3f}")
    print(f"  Weighted F1 : {metrics['weighted_f1']:.3f}")
    print()

    print("Example predictions:")
    examples = [
        "Explosion reported near the central market, people injured",
        "Smoke pouring out of a building on Station Road",
        "Water levels rising fast near the riverside",
        "Something loud happened downtown, not sure what",
    ]
    for text in examples:
        prediction = final_model.predict([text])[0]
        print(f"  {prediction:<10} <- {text}")


if __name__ == "__main__":
    main()
