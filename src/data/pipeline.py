"""
Complete Data Pipeline Orchestrator for Karen's Ear.
Runs Ingestion -> Mapping -> Preprocessing -> Deduplication -> Audit -> Splitting -> Synthetic Augmentation -> Audit -> Export.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple

from src.data.ingestion.crisislex import load_crisislex
from src.data.ingestion.humaid import load_humaid
from src.data.ingestion.sample import load_sample
from src.data.mapping import LabelMapper
from src.data.preprocessor import TextPreprocessor
from src.data.deduplication import Deduplicator
from src.data.splitter import DatasetSplitter
from src.data.auditor import DatasetAuditor

class DataPipeline:
    """
    End-to-End reproducible data pipeline.
    """

    def __init__(
        self,
        crisislex_dir: Union[str, Path] = "temp_crisislex/data/CrisisLexT26",
        humaid_dir: Union[str, Path] = "temp_humaid",
        sample_path: Union[str, Path] = "data/sample/sample_reports.json",
        output_dir: Union[str, Path] = "data/processed"
    ):
        self.crisislex_dir = Path(crisislex_dir)
        self.humaid_dir = Path(humaid_dir)
        self.sample_path = Path(sample_path)
        self.output_dir = Path(output_dir)

    def run_pipeline(
        self,
        max_samples_per_source: int = 15000,
        enable_synthetic_aug: bool = True,
        augmentation_ratio: float = 0.15,
        seed: int = 42
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes end-to-end dataset pipeline.
        Returns (train_records, val_records, test_records, audit_summary).
        """
        print("=== Step 1: Raw Data Ingestion ===")
        all_raw_records: List[Dict[str, Any]] = []

        if self.crisislex_dir.exists():
            c_recs = load_crisislex(self.crisislex_dir)
            if max_samples_per_source and len(c_recs) > max_samples_per_source:
                c_recs = c_recs[:max_samples_per_source]
            all_raw_records.extend(c_recs)
            print(f"Loaded {len(c_recs)} records from CrisisLex.")

        if self.humaid_dir.exists():
            h_recs = load_humaid(self.humaid_dir)
            if max_samples_per_source and len(h_recs) > max_samples_per_source:
                h_recs = h_recs[:max_samples_per_source]
            all_raw_records.extend(h_recs)
            print(f"Loaded {len(h_recs)} records from HumAID.")

        if self.sample_path.exists():
            s_recs = load_sample(self.sample_path)
            all_raw_records.extend(s_recs)
            print(f"Loaded {len(s_recs)} records from sample_reports.json.")

        print(f"Total raw ingested records: {len(all_raw_records)}")

        print("\n=== Step 2: Centralized Label Mapping ===")
        mapped_records, map_stats = LabelMapper.apply_mapping(all_raw_records)
        print(f"Label mapping completed across {len(mapped_records)} records.")

        print("\n=== Step 3: Text Preprocessing ===")
        preprocessed_records = TextPreprocessor.preprocess_records(mapped_records)
        print(f"Preprocessing completed. Active text records: {len(preprocessed_records)}")

        print("\n=== Step 4: Deduplication ===")
        deduped_records, dedup_stats = Deduplicator.deduplicate(preprocessed_records)
        print(f"Deduplication completed. Remaining unique records: {dedup_stats['records_remaining']} (Removed {dedup_stats['records_removed']})")

        print("\n=== Step 5: Dataset Splitting & Synthetic Augmentation ===")
        train_recs, val_recs, test_recs, split_stats = DatasetSplitter.create_splits(
            deduped_records,
            train_ratio=0.70,
            val_ratio=0.15,
            test_ratio=0.15,
            enable_synthetic_aug=enable_synthetic_aug,
            augmentation_ratio=augmentation_ratio,
            seed=seed
        )

        print(f"Splits created: Train={len(train_recs)}, Val={len(val_recs)}, Test={len(test_recs)}")

        print("\n=== Step 6: Automated Quality & Leakage Audit ===")
        audit_summary = DatasetAuditor.audit_splits(train_recs, val_recs, test_recs, strict=True)
        print("Dataset quality and zero leakage audit passed successfully!")

        print("\n=== Step 7: Exporting Processed Datasets ===")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(self.output_dir / "train.json", "w", encoding="utf-8") as f:
            json.dump(train_recs, f, indent=2)

        with open(self.output_dir / "val.json", "w", encoding="utf-8") as f:
            json.dump(val_recs, f, indent=2)

        with open(self.output_dir / "test.json", "w", encoding="utf-8") as f:
            json.dump(test_recs, f, indent=2)

        full_audit = {
            "deduplication_stats": dedup_stats,
            "split_stats": split_stats,
            "audit_summary": audit_summary
        }
        with open(self.output_dir / "audit_report.json", "w", encoding="utf-8") as f:
            json.dump(full_audit, f, indent=2)

        print(f"Saved processed dataset splits to: {self.output_dir}")

        return train_recs, val_recs, test_recs, full_audit
