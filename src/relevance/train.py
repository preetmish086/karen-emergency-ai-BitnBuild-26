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
        "relevance_level"
    ].astype(str).tolist()

    print("\nClass distribution:")

    print(
        df[
            "relevance_level"
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

    print(
        "\nModel trained successfully."
    )

    predictions, _ = model.predict(
        X_test
    )

    print("\nEvaluation:")

    print(
        f"Accuracy       : "
        f"{accuracy_score(y_test, predictions):.4f}"
    )

    print(
        f"Macro Precision: "
        f"{precision_score(y_test, predictions, average='macro', zero_division=0):.4f}"
    )

    print(
        f"Macro Recall   : "
        f"{recall_score(y_test, predictions, average='macro', zero_division=0):.4f}"
    )

    print(
        f"Macro F1       : "
        f"{f1_score(y_test, predictions, average='macro', zero_division=0):.4f}"
    )

    print("\nDetailed report:")

    print(
        classification_report(
            y_test,
            predictions,
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