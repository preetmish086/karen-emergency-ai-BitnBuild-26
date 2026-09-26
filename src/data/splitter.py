"""
Leakage-Safe Dataset Splitting Module.
Splits real data into Train, Validation, and Test sets using stratified splitting.
Injects synthetic data ONLY into the Training set.
"""
import random
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
from src.data.synthetic import SyntheticAugmenter

class DatasetSplitter:
    """
    Splits dataset while strictly isolating real validation and test sets from synthetic data.
    """

    @classmethod
    def split_real_dataset(
        cls,
        real_records: List[Dict[str, Any]],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Stratified split of real dataset into train, val, and test splits.
        """
        random.seed(seed)

        # Group real records by incident_type
        by_class: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for rec in real_records:
            inc_type = rec.get("incident_type", "other")
            by_class[inc_type].append(rec)

        real_train: List[Dict[str, Any]] = []
        real_val: List[Dict[str, Any]] = []
        real_test: List[Dict[str, Any]] = []

        for inc_type, items in by_class.items():
            items_shuffled = list(items)
            random.shuffle(items_shuffled)
            n = len(items_shuffled)

            if n < 3:
                # If too few instances for 3-way split, put most in train, 1 in val/test if possible
                if n == 1:
                    real_train.extend(items_shuffled)
                elif n == 2:
                    real_train.append(items_shuffled[0])
                    real_val.append(items_shuffled[1])
            else:
                n_train = int(n * train_ratio)
                n_val = int(n * val_ratio)
                if n_val == 0 and n >= 5:
                    n_val = 1
                n_test = n - n_train - n_val
                if n_test <= 0:
                    n_test = 1
                    n_train = max(1, n_train - 1)

                real_train.extend(items_shuffled[:n_train])
                real_val.extend(items_shuffled[n_train:n_train + n_val])
                real_test.extend(items_shuffled[n_train + n_val:])

        return real_train, real_val, real_test

    @classmethod
    def create_splits(
        cls,
        all_records: List[Dict[str, Any]],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        enable_synthetic_aug: bool = True,
        augmentation_ratio: float = 0.15,
        seed: int = 42
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Full split creation:
        1. Separates real vs synthetic records.
        2. Performs stratified split on real records into real_train, real_val, real_test.
        3. Appends synthetic data ONLY to real_train -> final_train.
        4. Returns (final_train, real_val, real_test, split_stats).
        """
        real_records = [r for r in all_records if not r.get("is_synthetic", False)]
        pre_existing_synthetic = [r for r in all_records if r.get("is_synthetic", False)]

        real_train, real_val, real_test = cls.split_real_dataset(
            real_records, train_ratio=train_ratio, val_ratio=val_ratio, test_ratio=test_ratio, seed=seed
        )

        final_train = list(real_train) + pre_existing_synthetic
        syn_stats = {"synthetic_added_count": len(pre_existing_synthetic)}

        if enable_synthetic_aug:
            final_train, syn_stats = SyntheticAugmenter.augment_training_set(
                final_train, augmentation_ratio=augmentation_ratio, seed=seed
            )

        split_stats = {
            "total_records_input": len(all_records),
            "real_records_total": len(real_records),
            "real_train_count": len(real_train),
            "real_val_count": len(real_val),
            "real_test_count": len(real_test),
            "final_train_count": len(final_train),
            "synthetic_in_train_count": syn_stats.get("synthetic_added_count", 0) + len(pre_existing_synthetic),
            "synthetic_in_val_count": sum(1 for r in real_val if r.get("is_synthetic")),
            "synthetic_in_test_count": sum(1 for r in real_test if r.get("is_synthetic")),
            "train_class_dist": dict(Counter([r.get("incident_type") for r in final_train])),
            "val_class_dist": dict(Counter([r.get("incident_type") for r in real_val])),
            "test_class_dist": dict(Counter([r.get("incident_type") for r in real_test]))
        }

        return final_train, real_val, real_test, split_stats
