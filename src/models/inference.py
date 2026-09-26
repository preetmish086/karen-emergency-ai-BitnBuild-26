"""
Role 1 Clean Inference Interface for Emergency Incident Classification.
Designed for downstream integration by R2 (Clustering) and R3 (Priority & Dashboard) teams.

Example Usage:
--------------
from src.models.inference import EmergencyClassifier

classifier = EmergencyClassifier()
result = classifier.predict_incident("Huge fire breaking out near downtown area!")
# Output: {"incident_type": "fire", "confidence": 0.94}
"""
from pathlib import Path
from typing import Dict, Any, List, Union
from src.models.persistence import ModelPersistence
from src.data.preprocessor import TextPreprocessor

DEFAULT_MODEL_PATH = "models/baseline_model.joblib"

class EmergencyClassifier:
    """
    Role 1 Public Inference Interface.
    Classifies raw text emergency reports into canonical incident_type values with confidence score.
    Does NOT modify downstream fields (severity, actionability, credibility, priority, location).
    """

    def __init__(self, model_path: Union[str, Path] = DEFAULT_MODEL_PATH):
        self.model_path = Path(model_path)
        self.model = None
        self._load_if_available()

    def _load_if_available(self):
        """Loads model from disk if available."""
        if self.model_path.exists():
            self.model = ModelPersistence.load_model(self.model_path)

    def predict_incident(self, text: str) -> Dict[str, Any]:
        """
        Classifies single emergency report text string.
        Returns dictionary with canonical incident_type and confidence score.
        """
        cleaned_text = TextPreprocessor.clean_text(text)
        if not cleaned_text:
            return {"incident_type": "unknown", "confidence": 0.0}

        if self.model is None or not getattr(self.model, "is_fitted", False):
            # Fallback heuristic prediction if model file is not present
            return {"incident_type": "other", "confidence": 0.50}

        conf_preds = self.model.predict_confidence([cleaned_text])
        best_type, confidence = conf_preds[0]

        return {
            "incident_type": best_type,
            "confidence": round(float(confidence), 4)
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Classifies a list of emergency report text strings.
        """
        return [self.predict_incident(t) for t in texts]
