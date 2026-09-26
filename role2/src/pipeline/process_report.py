import os
import pandas as pd
from typing import Union, Dict, Any, Optional

try:
    from role2.src.schemas.input_schema import EmergencyReportInput
    from role2.src.schemas.output_schema import Role2OutputSchema, LocationMetadata
    from role2.src.preprocessing.text_preprocessor import TextPreprocessor
    from role2.src.classification.incident_classifier import IncidentClassifier
    from role2.src.extraction.entity_extractor import EntityExtractor
    from role2.src.extraction.location_extractor import LocationExtractor
    from role2.src.extraction.location_tracker import LocationReportTracker
    from role2.src.extraction.completeness_evaluator import CompletenessEvaluator
    from role2.src.credibility.credibility_scorer import CredibilityScorer
except (ImportError, ModuleNotFoundError):
    from src.schemas.input_schema import EmergencyReportInput
    from src.schemas.output_schema import Role2OutputSchema, LocationMetadata
    from src.preprocessing.text_preprocessor import TextPreprocessor
    from src.classification.incident_classifier import IncidentClassifier
    from src.extraction.entity_extractor import EntityExtractor
    from src.extraction.location_extractor import LocationExtractor
    from src.extraction.location_tracker import LocationReportTracker
    from src.extraction.completeness_evaluator import CompletenessEvaluator
    from src.credibility.credibility_scorer import CredibilityScorer


class EmergencyReportPipeline:
    """
    Role 2 Core Pipeline:
    Coordinates NLP Preprocessing, Incident Classification, Entity Extraction,
    Location Extraction (GPS & Textual/Manual Location), Spatio-Temporal Location Density Tracking,
    Information Completeness Evaluation, and Credibility Scoring.
    """

    def __init__(
        self,
        preprocessor: TextPreprocessor = None,
        classifier: IncidentClassifier = None,
        extractor: EntityExtractor = None,
        location_extractor: LocationExtractor = None,
        location_tracker: LocationReportTracker = None,
        completeness_evaluator: CompletenessEvaluator = None,
        credibility_scorer: CredibilityScorer = None,
        csv_dataset_path: Optional[str] = None,
        window_minutes: int = 30,
    ):
        self.preprocessor = preprocessor or TextPreprocessor()
        self.classifier = classifier or IncidentClassifier(csv_dataset_path=csv_dataset_path)
        self.extractor = extractor or EntityExtractor(self.preprocessor)
        self.location_extractor = location_extractor or LocationExtractor()
        self.location_tracker = location_tracker or LocationReportTracker(window_minutes=window_minutes)
        self.completeness_evaluator = completeness_evaluator or CompletenessEvaluator()
        self.credibility_scorer = credibility_scorer or CredibilityScorer()

        # If CSV path provided or found, build location density index automatically
        target_csv = csv_dataset_path or self.classifier.csv_dataset_path
        if target_csv and os.path.exists(target_csv):
            try:
                df = pd.read_csv(target_csv)
                self.location_tracker.build_from_dataframe(df)
            except Exception:
                pass

    def process(self, report_input: Union[EmergencyReportInput, Dict[str, Any]]) -> Role2OutputSchema:
        """
        Process a single emergency report and produce structured output for downstream systems.
        """
        if isinstance(report_input, dict):
            report = EmergencyReportInput(**report_input)
        else:
            report = report_input

        # 1. Text Preprocessing
        clean_text = self.preprocessor.preprocess(report.text)

        # 2. Incident Classification
        incident_info = self.classifier.classify(clean_text)

        # 3. Affected People & Entity Extraction (No Hallucination)
        people_affected = self.extractor.extract_people(clean_text)

        # 4. Location Processing (GPS optional + Textual/Manual Location fallback)
        has_gps = (report.latitude is not None) and (report.longitude is not None)
        extracted_text_loc = self.location_extractor.extract_location_text(
            text=report.text,
            input_location_metadata=report.location
        )

        # 5. Spatio-Temporal Location Density / Multi-report Count Tracking (Same location + Same time window)
        if report.location_report_count is not None:
            location_count = report.location_report_count
        else:
            location_count = self.location_tracker.register_report(
                text_loc=extracted_text_loc,
                lat=report.latitude,
                lon=report.longitude,
                timestamp_str=report.timestamp
            )

        location = LocationMetadata(
            latitude=report.latitude,
            longitude=report.longitude,
            text_location=extracted_text_loc,
            has_gps=has_gps,
            location_report_count=location_count
        )

        # 6. Information Completeness Evaluation
        info_completeness = self.completeness_evaluator.evaluate(
            text=clean_text,
            incident=incident_info,
            people=people_affected,
            location=location
        )

        # 7. Credibility Assessment (with spatio-temporal location density & casualty reporting signals)
        credibility_info = self.credibility_scorer.score_credibility(
            text=clean_text,
            incident=incident_info,
            people=people_affected,
            completeness=info_completeness,
            location=location
        )

        # 8. Construct Final Role 2 Output Schema
        output = Role2OutputSchema(
            report_id=report.report_id,
            text=report.text,
            incident=incident_info,
            people=people_affected,
            information=info_completeness,
            credibility=credibility_info,
            location=location,
            timestamp=report.timestamp
        )

        return output
