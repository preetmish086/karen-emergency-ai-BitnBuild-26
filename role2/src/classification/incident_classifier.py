import os
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

try:
    from role2.src.schemas.output_schema import IncidentCategory, IncidentInfo
    from role2.src.classification.base import BaseIncidentClassifier
    from role2.src.classification.idiom_detector import is_slang_or_figurative
except (ImportError, ModuleNotFoundError):
    from src.schemas.output_schema import IncidentCategory, IncidentInfo
    from src.classification.base import BaseIncidentClassifier
    try:
        from src.classification.idiom_detector import is_slang_or_figurative
    except (ImportError, ModuleNotFoundError):
        from src.relevance.idiom_detector import is_slang_or_figurative


class IncidentClassifier(BaseIncidentClassifier):
    """
    Hybrid Incident Classifier combining pattern-based semantic domain rules with
    a TF-IDF Naive Bayes model trained on NYC Emergency Reports dataset (8,735 samples).
    """

    KEYWORD_MAP: Dict[IncidentCategory, List[str]] = {
        IncidentCategory.ACCIDENT: [
            "accident", "crash", "car accident", "collision", "hit and run", "rollover",
            "vehicle", "highway accident", "truck crash", "pileup", "derailment", "traffic accident",
            "auto accident", "vehicle overturned"
        ],
        IncidentCategory.FIRE: [
            "fire", "blaze", "flames", "smoke", "burning", "wildfire", "house fire",
            "building fire", "fire break out", "caught fire", "fire broke out"
        ],
        IncidentCategory.FLOOD: [
            "flood", "overflowed", "water entering", "submerged", "flash flood",
            "rising water", "river overflow", "flooding", "inundated", "torrential"
        ],
        IncidentCategory.MEDICAL: [
            "unconscious", "ambulance", "heart attack", "cardiac arrest", "stroke",
            "bleeding severely", "seizure", "choking", "non-responsive", "fainted",
            "medical emergency", "passed out", "breathing difficulty", "dying", "call 108"
        ],
        IncidentCategory.EXPLOSION: [
            "explosion", "blast", "exploded", "bomb", "gas leak explosion",
            "detonated", "detonation", "pipe burst explosion", "gas leak"
        ],
        IncidentCategory.COLLAPSE: [
            "collapsed", "collapse", "structure failure", "wall fell", "roof fell",
            "rubble", "trapped under collapsed", "cave-in", "building downfall", "building collapsing"
        ],
        IncidentCategory.CRIME: [
            "stole", "stolen", "robbery", "robbed", "mugging", "assault", "shooter",
            "armed robbery", "burglary", "thief", "gunshot", "stabbed", "attacked", "crime going on"
        ],
        IncidentCategory.MISSING_PERSON: [
            "missing", "disappeared", "lost child", "wandered off", "cannot find my child",
            "missing person", "seen since", "kidnapped", "abducted"
        ],
    }

    # Baseline synthetic corpus for fallback if CSV dataset is not present
    BASELINE_TRAINING_SAMPLES: List[Tuple[str, IncidentCategory]] = [
        ("I saw a car accident on the highway and 4 vehicles collided", IncidentCategory.ACCIDENT),
        ("Major vehicle crash on main street", IncidentCategory.ACCIDENT),
        ("Hit and run accident near intersection", IncidentCategory.ACCIDENT),
        ("A severe fire broke out in my apartment building", IncidentCategory.FIRE),
        ("Flames and heavy smoke coming out of the warehouse", IncidentCategory.FIRE),
        ("Wildfire spreading rapidly towards houses", IncidentCategory.FIRE),
        ("Water is entering houses after the river overflowed", IncidentCategory.FLOOD),
        ("Flash flood warning, streets completely submerged under water", IncidentCategory.FLOOD),
        ("Heavy rain causing severe flooding everywhere", IncidentCategory.FLOOD),
        ("My friend is unconscious and needs an immediate ambulance", IncidentCategory.MEDICAL),
        ("Person having cardiac arrest and severe chest pain", IncidentCategory.MEDICAL),
        ("Someone collapsed on the floor and stopped breathing", IncidentCategory.MEDICAL),
        ("There was a huge explosion near the central market", IncidentCategory.EXPLOSION),
        ("Gas pipeline exploded causing massive blast wave", IncidentCategory.EXPLOSION),
        ("Bomb exploded near public bus stand", IncidentCategory.EXPLOSION),
        ("The building collapsed and people are trapped under rubble", IncidentCategory.COLLAPSE),
        ("Roof of the old house fell down completely", IncidentCategory.COLLAPSE),
        ("Wall collapsed onto parked cars", IncidentCategory.COLLAPSE),
        ("Someone stole my phone and wallet and ran away", IncidentCategory.CRIME),
        ("Armed robbery at the grocery store", IncidentCategory.CRIME),
        ("Person assaulted near subway entrance", IncidentCategory.CRIME),
        ("My child has been missing since this morning", IncidentCategory.MISSING_PERSON),
        ("Elderly person disappeared from home", IncidentCategory.MISSING_PERSON),
        ("Hello test testing 123", IncidentCategory.UNKNOWN),
        ("Something weird happened outside", IncidentCategory.OTHER),
        ("the movie i watched last night was fire", IncidentCategory.OTHER),
        ("this burger is the bomb", IncidentCategory.OTHER),
        ("that concert was an absolute blast", IncidentCategory.OTHER),
        ("my code crashed on production", IncidentCategory.OTHER),
        ("i am dying of laughter watching this", IncidentCategory.OTHER),
        ("the kids are shooting hoops at the park", IncidentCategory.OTHER),
        ("i am flooded with emails and assignments today", IncidentCategory.OTHER),
    ]

    def __init__(self, csv_dataset_path: Optional[str] = None):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.ml_classifier = MultinomialNB()
        self.csv_dataset_path = csv_dataset_path or self._find_default_csv()
        self._train_classifier()

    def _find_default_csv(self) -> Optional[str]:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "nyc_emergency_reports_clean.csv"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "nyc_emergency_reports_clean.csv"),
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "nyc_emergency_reports_clean.csv")
        ]
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
        return None

    def _train_classifier(self):
        texts = []
        labels = []

        # Load from CSV dataset if available
        if self.csv_dataset_path and os.path.exists(self.csv_dataset_path):
            try:
                df = pd.read_csv(self.csv_dataset_path)
                if "text" in df.columns and "label" in df.columns:
                    texts = df["text"].astype(str).tolist()
                    labels = df["label"].astype(str).tolist()
            except Exception:
                pass

        # Fallback to baseline corpus if CSV loading failed or was empty
        if not texts:
            texts = [sample[0] for sample in self.BASELINE_TRAINING_SAMPLES]
            labels = [sample[1].value for sample in self.BASELINE_TRAINING_SAMPLES]

        X = self.vectorizer.fit_transform(texts)
        self.ml_classifier.fit(X, labels)

    def classify(self, text: str) -> IncidentInfo:
        clean_text = text.lower()

        # 0. Check for slang / idioms / figurative expressions with hazard words
        is_slang, _ = is_slang_or_figurative(clean_text)
        if is_slang:
            return IncidentInfo(type=IncidentCategory.OTHER, confidence=0.88)

        # 1. Direct Pattern / Keyword Matching
        matched_scores: Dict[IncidentCategory, float] = {}
        for category, keywords in self.KEYWORD_MAP.items():
            score = 0.0
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", clean_text):
                    score += 1.5 if " " in kw else 1.0
            if score > 0:
                matched_scores[category] = score

        if matched_scores:
            best_category = max(matched_scores.items(), key=lambda x: x[1])[0]
            raw_match_score = matched_scores[best_category]
            confidence = min(0.98, 0.82 + (raw_match_score * 0.04))
            return IncidentInfo(type=best_category, confidence=round(confidence, 2))

        # 2. ML Classifier Fallback
        try:
            X_test = self.vectorizer.transform([clean_text])
            probs = self.ml_classifier.predict_proba(X_test)[0]
            classes = self.ml_classifier.classes_
            best_idx = probs.argmax()
            predicted_label = classes[best_idx]
            max_prob = probs[best_idx]

            if max_prob < 0.45:
                return IncidentInfo(type=IncidentCategory.UNKNOWN, confidence=round(float(max_prob), 2))

            try:
                category = IncidentCategory(predicted_label.lower())
            except ValueError:
                category = IncidentCategory.OTHER

            return IncidentInfo(type=category, confidence=round(float(max_prob), 2))
        except Exception:
            return IncidentInfo(type=IncidentCategory.UNKNOWN, confidence=0.40)
