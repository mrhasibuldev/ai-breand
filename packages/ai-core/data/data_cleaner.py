"""
Data Cleaning Pipeline

Cleans and preprocesses text data for training.
Handles: deduplication, normalization, filtering, quality checks.
"""

import re
import json
import sys
from typing import List, Set
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class DataCleaner:
    """Clean and preprocess text data"""
    
    def __init__(self):
        self.seen_texts: Set[str] = set()
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text: whitespace, punctuation, encoding
        """
        # Normalize Unicode
        text = text.strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters except newlines
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text
    
    def filter_short_text(self, text: str, min_length: int = 10) -> bool:
        """Filter out very short texts"""
        return len(text.strip()) >= min_length
    
    def filter_long_text(self, text: str, max_length: int = 1000) -> bool:
        """Filter out very long texts"""
        return len(text.strip()) <= max_length
    
    def filter_special_chars(self, text: str, max_ratio: float = 0.5) -> bool:
        """
        Filter texts with too many special characters
        """
        if not text:
            return False
        
        special_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
        ratio = special_count / len(text)
        
        return ratio <= max_ratio
    
    def deduplicate(self, texts: List[str]) -> List[str]:
        """
        Remove duplicate texts
        """
        unique_texts = []
        for text in texts:
            normalized = self.normalize_text(text)
            if normalized not in self.seen_texts:
                self.seen_texts.add(normalized)
                unique_texts.append(text)
        
        removed = len(texts) - len(unique_texts)
        print(f"[Cleaner] Removed {removed} duplicates")
        
        return unique_texts
    
    def clean_dataset(
        self,
        texts: List[str],
        min_length: int = 10,
        max_length: int = 1000,
        deduplicate: bool = True
    ) -> List[str]:
        """
        Full cleaning pipeline
        """
        print(f"[Cleaner] Starting with {len(texts)} samples")
        
        # Step 1: Normalize
        texts = [self.normalize_text(t) for t in texts]
        print(f"[Cleaner] After normalization: {len(texts)}")
        
        # Step 2: Filter by length
        texts = [t for t in texts if self.filter_short_text(t, min_length)]
        texts = [t for t in texts if self.filter_long_text(t, max_length)]
        print(f"[Cleaner] After length filtering: {len(texts)}")
        
        # Step 3: Filter special characters
        texts = [t for t in texts if self.filter_special_chars(t)]
        print(f"[Cleaner] After special char filtering: {len(texts)}")
        
        # Step 4: Deduplicate
        if deduplicate:
            texts = self.deduplicate(texts)
        
        print(f"[Cleaner] Final count: {len(texts)} samples")
        
        return texts
    
    def create_conversational_pairs(
        self,
        texts: List[str],
        window_size: int = 2
    ) -> List[dict]:
        """
        Create Q&A pairs from sequential texts
        This is a simple heuristic for conversational data
        """
        pairs = []
        
        for i in range(len(texts) - window_size):
            pairs.append({
                "question": texts[i],
                "answer": texts[i + 1]
            })
        
        print(f"[Cleaner] Created {len(pairs)} conversational pairs")
        
        return pairs


def main():
    """Test the cleaning pipeline"""
    
    # Load version 1.0 dataset (use absolute path)
    script_dir = Path(__file__).parent
    data_dir = script_dir / "public_datasets" / "v1.0"
    
    with open(data_dir / "train.json", 'r', encoding='utf-8') as f:
        train_texts = json.load(f)
    
    # Clean the data
    cleaner = DataCleaner()
    cleaned_texts = cleaner.clean_dataset(
        train_texts,
        min_length=5,
        max_length=500,
        deduplicate=True
    )
    
    # Create conversational pairs
    pairs = cleaner.create_conversational_pairs(cleaned_texts)
    
    # Save cleaned data
    output_dir = script_dir / "public_datasets" / "v1.0_cleaned"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "train_cleaned.json", 'w', encoding='utf-8') as f:
        json.dump(cleaned_texts, f, ensure_ascii=False, indent=2)
    
    with open(output_dir / "conversational_pairs.json", 'w', encoding='utf-8') as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved cleaned data to {output_dir}")


if __name__ == "__main__":
    main()
