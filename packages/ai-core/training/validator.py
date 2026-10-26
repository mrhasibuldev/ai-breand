"""
Training Pipeline Validator

Validate datasets, check for leakage, and ensure reproducibility.
"""

import json
import sys
import os
from typing import List, Set, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset import load_json_dataset


class DatasetValidator:
    """
    Validate training datasets and check for issues.
    """

    def __init__(self, train_path: str, val_path: str):
        """
        Initialize validator.

        Args:
            train_path: Path to training data
            val_path: Path to validation data
        """
        self.train_path = train_path
        self.val_path = val_path
        self.validation_results = {}

    def check_data_leakage(self) -> Dict[str, Any]:
        """
        Check for data leakage between train and validation sets.

        Returns:
            Leakage report
        """
        print("\n" + "=" * 60)
        print("CHECKING DATA LEAKAGE")
        print("=" * 60)

        train_texts = load_json_dataset(self.train_path)
        val_texts = load_json_dataset(self.val_path)

        # Convert to sets for comparison
        train_set = set(train_texts)
        val_set = set(val_texts)

        # Check for exact matches
        leakage = train_set.intersection(val_set)

        # Check for partial matches (substring)
        partial_leakage = []
        for val_text in val_texts:
            for train_text in train_texts:
                if val_text in train_text or train_text in val_text:
                    if val_text != train_text:  # Not exact match
                        partial_leakage.append({
                            "val": val_text,
                            "train": train_text
                        })

        report = {
            "train_samples": len(train_texts),
            "val_samples": len(val_texts),
            "exact_leakage_count": len(leakage),
            "exact_leakage_samples": list(leakage),
            "partial_leakage_count": len(partial_leakage),
            "partial_leakage_samples": partial_leakage[:10]  # First 10
        }

        print(f"Train samples: {report['train_samples']}")
        print(f"Validation samples: {report['val_samples']}")
        print(f"Exact leakage: {report['exact_leakage_count']}")
        print(f"Partial leakage: {report['partial_leakage_count']}")

        if report['exact_leakage_count'] > 0:
            print("[WARNING] Exact data leakage detected!")
        if report['partial_leakage_count'] > 0:
            print("[WARNING] Partial data leakage detected!")

        self.validation_results["data_leakage"] = report
        return report

    def check_data_quality(self) -> Dict[str, Any]:
        """
        Check data quality issues.

        Returns:
            Quality report
        """
        print("\n" + "=" * 60)
        print("CHECKING DATA QUALITY")
        print("=" * 60)

        train_texts = load_json_dataset(self.train_path)
        val_texts = load_json_dataset(self.val_path)

        all_texts = train_texts + val_texts

        # Check for empty strings
        empty_count = sum(1 for text in all_texts if not text or text.strip() == "")

        # Check for very short strings
        short_count = sum(1 for text in all_texts if len(text) < 10)

        # Check for very long strings
        long_count = sum(1 for text in all_texts if len(text) > 500)

        # Check for duplicates within each set
        train_duplicates = len(train_texts) - len(set(train_texts))
        val_duplicates = len(val_texts) - len(set(val_texts))

        report = {
            "total_samples": len(all_texts),
            "empty_strings": empty_count,
            "very_short_strings": short_count,
            "very_long_strings": long_count,
            "train_duplicates": train_duplicates,
            "val_duplicates": val_duplicates
        }

        print(f"Total samples: {report['total_samples']}")
        print(f"Empty strings: {report['empty_strings']}")
        print(f"Very short (<10 chars): {report['very_short_strings']}")
        print(f"Very long (>500 chars): {report['very_long_strings']}")
        print(f"Train duplicates: {report['train_duplicates']}")
        print(f"Val duplicates: {report['val_duplicates']}")

        if report['empty_strings'] > 0:
            print("[WARNING] Empty strings found!")
        if report['train_duplicates'] > 0:
            print("[WARNING] Duplicates in training set!")

        self.validation_results["data_quality"] = report
        return report

    def check_dataset_balance(self) -> Dict[str, Any]:
        """
        Check dataset balance and distribution.

        Returns:
            Balance report
        """
        print("\n" + "=" * 60)
        print("CHECKING DATASET BALANCE")
        print("=" * 60)

        train_texts = load_json_dataset(self.train_path)
        val_texts = load_json_dataset(self.val_path)

        # Calculate length distribution
        train_lengths = [len(text) for text in train_texts]
        val_lengths = [len(text) for text in val_texts]

        report = {
            "train_count": len(train_texts),
            "val_count": len(val_texts),
            "train_ratio": len(train_texts) / (len(train_texts) + len(val_texts)),
            "val_ratio": len(val_texts) / (len(train_texts) + len(val_texts)),
            "avg_train_length": sum(train_lengths) / len(train_lengths) if train_lengths else 0,
            "avg_val_length": sum(val_lengths) / len(val_lengths) if val_lengths else 0,
            "min_train_length": min(train_lengths) if train_lengths else 0,
            "max_train_length": max(train_lengths) if train_lengths else 0,
            "min_val_length": min(val_lengths) if val_lengths else 0,
            "max_val_length": max(val_lengths) if val_lengths else 0
        }

        print(f"Train ratio: {report['train_ratio']:.2%}")
        print(f"Val ratio: {report['val_ratio']:.2%}")
        print(f"Avg train length: {report['avg_train_length']:.2f}")
        print(f"Avg val length: {report['avg_val_length']:.2f}")

        # Check if ratio is close to 80/20
        if 0.75 < report['train_ratio'] < 0.85:
            print("[OK] Train/val ratio is reasonable (~80/20)")
        else:
            print(f"[WARNING] Train/val ratio is {report['train_ratio']:.2%} (expected ~80/20)")

        self.validation_results["dataset_balance"] = report
        return report

    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("=" * 60)
        print("RUNNING DATASET VALIDATIONS")
        print("=" * 60)

        self.check_data_leakage()
        self.check_data_quality()
        self.check_dataset_balance()

        return self.validation_results

    def save_report(self, path: str):
        """Save validation report"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        print(f"\nValidation report saved to {path}")
