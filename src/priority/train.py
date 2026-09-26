"""
Training pipeline for the Emergency Priority Model.
"""

import pandas as pd

from sklearn.model_selection import train_test_split

from src.priority.features import extract_features
from src.priority.priority_model import PriorityModel
from src.priority.evaluate import evaluate_model


def prepare_training_data(df):

    X = []
    y = []

    for _, row in df.iterrows():

        features = extract_features(
            severity=row["severity"],
            actionability=row["actionability"],
            credibility=row["credibility"],
            report_count=row["corroboration_count"]
        )

        X.append(features)
        y.append(float(row["priority"]))

    return X, y


def train_priority_model(
    dataset_path,
    model_path
):

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    print(f"Total samples: {len(df)}")

    X, y = prepare_training_data(df)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # Create model
    model = PriorityModel()

    # Train
    model.train(X_train, y_train)

    print("\nModel trained successfully.")

    # Evaluate
    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    print("\nEvaluation:")
    print(f"MAE  : {metrics['MAE']}")
    print(f"RMSE : {metrics['RMSE']}")
    print(f"R²   : {metrics['R2']}")

    # Save
    model.save(model_path)

    print(f"\nModel saved to: {model_path}")


if __name__ == "__main__":

    train_priority_model(
        dataset_path="data/priority_dataset_demo.csv",
        model_path="models/priority_model.pkl"
    )