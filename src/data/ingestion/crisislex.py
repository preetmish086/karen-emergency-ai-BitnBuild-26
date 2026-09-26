"""
CrisisLexT26 dataset ingestion module.
"""
import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Union
import pandas as pd

class CrisisLexIngestor:
    """
    Ingestor for CrisisLexT26 dataset.
    Reads labeled CSV files across 26 crisis event directories,
    applies quality filtering for 'Related and informative' records,
    and preserves original provenance metadata.
    """

    def __init__(self, base_dir: Union[str, Path] = "temp_crisislex/data/CrisisLexT26"):
        self.base_dir = Path(base_dir)

    def load_raw_records(self, informativeness_filter: str = "Related and informative") -> List[Dict[str, Any]]:
        """
        Loads and filters CrisisLexT26 records.
        """
        if not self.base_dir.exists():
            raise FileNotFoundError(f"CrisisLex directory not found at: {self.base_dir}")

        csv_files = glob.glob(str(self.base_dir / "*" / "*_labeled.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No labeled CSV files found under: {self.base_dir}")

        records: List[Dict[str, Any]] = []

        for csv_path in sorted(csv_files):
            event_name = os.path.basename(os.path.dirname(csv_path))
            try:
                df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
            except Exception:
                try:
                    df = pd.read_csv(csv_path, encoding="latin1", on_bad_lines="skip")
                except Exception as e:
                    print(f"Warning: Could not read CSV file {csv_path}: {e}")
                    continue

            # Clean column names by stripping leading/trailing whitespace
            df.columns = [c.strip() for c in df.columns]

            text_col = "Tweet Text" if "Tweet Text" in df.columns else None
            info_col = "Informativeness" if "Informativeness" in df.columns else None
            source_col = "Information Source" if "Information Source" in df.columns else None
            type_col = "Information Type" if "Information Type" in df.columns else None

            if not text_col:
                continue

            for _, row in df.iterrows():
                raw_text = str(row[text_col]).strip() if pd.notna(row[text_col]) else ""
                if not raw_text or raw_text.lower() == "nan":
                    continue

                info_val = str(row[info_col]).strip() if info_col and pd.notna(row[info_col]) else ""

                # Quality filtering rule: prioritize 'Related and informative'
                if informativeness_filter and info_val != informativeness_filter:
                    continue

                source_val = str(row[source_col]).strip() if source_col and pd.notna(row[source_col]) else "Unknown"
                type_val = str(row[type_col]).strip() if type_col and pd.notna(row[type_col]) else "Unknown"

                record = {
                    "text": raw_text,
                    "source": "crisislex",
                    "source_event": event_name,
                    "source_label": info_val,
                    "information_source": source_val,
                    "information_type": type_val,
                    "informativeness": info_val,
                    "is_synthetic": False
                }
                records.append(record)

        return records

def load_crisislex(base_dir: Union[str, Path] = "temp_crisislex/data/CrisisLexT26") -> List[Dict[str, Any]]:
    ingestor = CrisisLexIngestor(base_dir=base_dir)
    return ingestor.load_raw_records()
