"""
Training pipeline for the Emergency Relevance Model.
"""

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from src.relevance.relevance_model import RelevanceModel


def train_relevance_model(
    dataset_path,
    model_path
):

    print("Loading dataset...")

    df = pd.read_csv(
        dataset_path
    )

    print(
        f"Total samples: {len(df)}"
    )

    texts = df[
        "text"
    ].tolist()

    labels = df[
        "relevant"
    ].astype(str).tolist()

    print("\nClass distribution:")

    print(
        df[
            "relevant"
        ].value_counts()
    )

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )

    print(
        f"\nTraining samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    model = RelevanceModel()

    model.train(
        X_train,
        y_train
    )

    print("\nModel trained successfully.")

    # Predictions on both training and testing data
    train_predictions, _ = model.predict(X_train)
    test_predictions, _ = model.predict(X_test)

    print("\n===== TRAIN vs TEST EVALUATION =====")

    train_accuracy = accuracy_score(
        y_train,
        train_predictions
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions
    )

    train_precision = precision_score(
        y_train,
        train_predictions,
        average="macro",
        zero_division=0
    )

    test_precision = precision_score(
        y_test,
        test_predictions,
        average="macro",
        zero_division=0
    )

    train_recall = recall_score(
        y_train,
        train_predictions,
        average="macro",
        zero_division=0
    )

    test_recall = recall_score(
        y_test,
        test_predictions,
        average="macro",
        zero_division=0
    )

    train_f1 = f1_score(
        y_train,
        train_predictions,
        average="macro",
        zero_division=0
    )

    test_f1 = f1_score(
        y_test,
        test_predictions,
        average="macro",
        zero_division=0
    )

    print(f"\n{'Metric':<15} {'Train':<10} {'Test':<10} {'Gap':<10}")
    print("-" * 45)

    print(
        f"{'Accuracy':<15} "
        f"{train_accuracy:<10.4f} "
        f"{test_accuracy:<10.4f} "
        f"{train_accuracy - test_accuracy:<10.4f}"
    )

    print(
        f"{'Precision':<15} "
        f"{train_precision:<10.4f} "
        f"{test_precision:<10.4f} "
        f"{train_precision - test_precision:<10.4f}"
    )

    print(
        f"{'Recall':<15} "
        f"{train_recall:<10.4f} "
        f"{test_recall:<10.4f} "
        f"{train_recall - test_recall:<10.4f}"
    )

    print(
        f"{'Macro F1':<15} "
        f"{train_f1:<10.4f} "
        f"{test_f1:<10.4f} "
        f"{train_f1 - test_f1:<10.4f}"
    )

    print("\n===== TEST CLASSIFICATION REPORT =====")

    print(
        classification_report(
            y_test,
            test_predictions,
            zero_division=0
        )
    )

    model.save(
        model_path
    )

    print(
        f"\nModel saved to: {model_path}"
    )


if __name__ == "__main__":

    train_relevance_model(
        dataset_path="data/relevance_demo.csv",
        model_path="models/relevance_model.pkl"
    )