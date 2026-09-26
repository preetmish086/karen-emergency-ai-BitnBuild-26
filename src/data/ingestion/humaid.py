"""
HumAID dataset ingestion module.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Union

class HumAIDIngestor:
    """
    Ingestor for HumAID dataset.
    Reads train.jsonl, dev.jsonl, and test.jsonl files,
    preserves original split and class_label provenance metadata.
    """

    def __init__(self, base_dir: Union[str, Path] = "temp_humaid"):
        self.base_dir = Path(base_dir)

    def load_raw_records(self) -> List[Dict[str, Any]]:
        """
        Loads all HumAID records from train.jsonl, dev.jsonl, and test.jsonl.
        """
        if not self.base_dir.exists():
            raise FileNotFoundError(f"HumAID directory not found at: {self.base_dir}")

        records: List[Dict[str, Any]] = []
        splits = ["train.jsonl", "dev.jsonl", "test.jsonl"]

        for split_file in splits:
            file_path = self.base_dir / split_file
            if not file_path.exists():
                continue

            split_name = split_file.replace(".jsonl", "")
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    raw_text = str(item.get("tweet_text", "")).strip()
                    label = str(item.get("class_label", "")).strip()

                    if not raw_text:
                        continue

                    record = {
                        "text": raw_text,
                        "source": "humaid",
                        "source_split": split_name,
                        "source_label": label,
                        "is_synthetic": False
                    }
                    records.append(record)

        return records

def load_humaid(base_dir: Union[str, Path] = "temp_humaid") -> List[Dict[str, Any]]:
    ingestor = HumAIDIngestor(base_dir=base_dir)
    return ingestor.load_raw_records()
