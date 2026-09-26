"""
Master Execution Pipeline for Role 1 — Data + Baseline ML.
Executes end-to-end dataset generation, auditing, baseline model training, evaluation, persistence, and inference testing.
"""
import sys
import json
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.data.pipeline import DataPipeline
from src.data.preprocessor import TextPreprocessor
from src.models.baseline_classifier import TFIDFLogisticRegressionBaseline, TFIDFNaiveBayesBaseline
from src.models.persistence import ModelPersistence
from src.models.inference import EmergencyClassifier

def run():
    print("============================================================")
    print("KAREN'S EAR — ROLE 1 COMPLETE PIPELINE EXECUTION")
    print("============================================================\n")

    # Step 1: Run Data Pipeline
    dp = DataPipeline()
    train_recs, val_recs, test_recs, audit_summary = dp.run_pipeline(
        max_samples_per_source=15000,
        enable_synthetic_aug=True,
        augmentation_ratio=0.15,
        seed=42
    )

    X_train, y_train = TextPreprocessor.extract_features_and_targets(train_recs)
    X_val, y_val = TextPreprocessor.extract_features_and_targets(val_recs)
    X_test, y_test = TextPreprocessor.extract_features_and_targets(test_recs)

    print(f"\nExtracted Feature Shapes:")
    print(f"Train samples: {len(X_train)} | Val samples: {len(X_val)} | Test samples: {len(X_test)}")

    # Step 2: Model Training & Validation Selection
    print("\n=== Step 8: Baseline Model Training & Validation ===")

    print("\nTraining Primary Baseline Model: TF-IDF + Logistic Regression...")
    model_lr = TFIDFLogisticRegressionBaseline(C=1.0, max_iter=1000, random_state=42)
    model_lr.fit(X_train, y_train)
    val_eval_lr = model_lr.evaluate(X_val, y_val)
    print(f"Logistic Regression Validation Accuracy: {val_eval_lr['accuracy']:.4f} | Macro F1: {val_eval_lr['macro_f1']:.4f}")

    print("\nTraining Secondary Baseline Model: TF-IDF + Multinomial Naive Bayes...")
    model_nb = TFIDFNaiveBayesBaseline(alpha=1.0)
    model_nb.fit(X_train, y_train)
    val_eval_nb = model_nb.evaluate(X_val, y_val)
    print(f"Naive Bayes Validation Accuracy: {val_eval_nb['accuracy']:.4f} | Macro F1: {val_eval_nb['macro_f1']:.4f}")

    # Model Selection based on Validation Macro F1
    if val_eval_lr["macro_f1"] >= val_eval_nb["macro_f1"]:
        best_model = model_lr
        best_name = "TF-IDF + Logistic Regression"
        best_val_eval = val_eval_lr
    else:
        best_model = model_nb
        best_name = "TF-IDF + Multinomial Naive Bayes"
        best_val_eval = val_eval_nb

    print(f"\n--> Selected Best Model based on Validation Macro F1: {best_name}")

    # Step 3: Final Test Set Evaluation
    print("\n=== Step 9: Final Evaluation on Held-out Real Test Set ===")
    test_eval = best_model.evaluate(X_test, y_test)
    print(f"Test Accuracy:          {test_eval['accuracy']:.4f}")
    print(f"Test Macro Precision:   {test_eval['macro_precision']:.4f}")
    print(f"Test Macro Recall:      {test_eval['macro_recall']:.4f}")
    print(f"Test Macro F1:          {test_eval['macro_f1']:.4f}")
    print(f"Test Weighted F1:       {test_eval['weighted_f1']:.4f}")

    print("\nPer-Class Test Metrics:")
    for cls_name, m in test_eval["per_class_metrics"].items():
        print(f"  - {cls_name:15s} | Prec: {m['precision']:.4f} | Rec: {m['recall']:.4f} | F1: {m['f1_score']:.4f} | Support: {m['support']}")

    # Step 4: Model Persistence
    print("\n=== Step 10: Model Persistence ===")
    model_path = ModelPersistence.save_model(
        best_model,
        filepath="models/baseline_model.joblib",
        metadata={
            "best_name": best_name,
            "val_metrics": best_val_eval,
            "test_metrics": test_eval
        }
    )
    print(f"Model saved successfully to: {model_path}")

    # Step 5: Test Inference Interface
    print("\n=== Step 11: Testing Role 1 Public Inference Interface ===")
    classifier = EmergencyClassifier(model_path=model_path)
    sample_queries = [
        "Huge explosion near the central market! Several people are injured!",
        "Smoke coming from a building near Station Road, fire trucks needed!",
        "There has been a multi-car accident on the highway. Traffic completely blocked.",
        "Water rising rapidly near the riverside area, flooding homes!",
        "Building collapsed near the bus stand! People trapped under rubble."
    ]

    for q in sample_queries:
        res = classifier.predict_incident(q)
        print(f"Query: '{q[:50]}...' -> Predicted: {res['incident_type']} (Confidence: {res['confidence']:.4f})")

    print("\n============================================================")
    print("ROLE 1 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("============================================================")

if __name__ == "__main__":
    run()
