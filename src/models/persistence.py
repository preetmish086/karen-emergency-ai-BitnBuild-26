"""
Model Persistence Module.
Saves and loads trained baseline ML model artifacts.
"""
import os
from pathlib import Path
from typing import Any, Dict, Union
import joblib

class ModelPersistence:
    """
    Handles saving and loading of baseline ML model artifacts.
    """

    @classmethod
    def save_model(
        cls,
        model: Any,
        filepath: Union[str, Path] = "models/baseline_model.joblib",
        metadata: Dict[str, Any] = None
    ) -> Path:
        """
        Saves trained model and optional metadata dict to filepath.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        artifact = {
            "model": model,
            "version": "1.0.0",
            "model_type": type(model).__name__,
            "metadata": metadata or {}
        }

        joblib.dump(artifact, path, compress=3)
        return path

    @classmethod
    def load_model(cls, filepath: Union[str, Path] = "models/baseline_model.joblib") -> Any:
        """
        Loads trained model artifact from filepath.
        Returns model instance.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found at: {path}")

        artifact = joblib.load(path)
        if isinstance(artifact, dict) and "model" in artifact:
            return artifact["model"]
        return artifact
