"""
NexusAI Tokenizer Evaluation

Evaluates tokenizer performance for Bengali and English.
Measures vocabulary size, unknown token rate, tokenization quality.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import re


class TokenizerEvaluator:
    """Evaluates tokenizer performance on Bengali and English samples"""

    def __init__(self):
        self.results = {}

    def load_sample_texts(self, sample_dir: str = None) -> Dict[str, List[str]]:
        """Load sample texts for evaluation"""
        if sample_dir is None:
            sample_dir = Path(__file__).parent.parent / "data" / "public_datasets" / "v1.0"
        else:
            sample_dir = Path(sample_dir)
        texts = {
            "bengali": [],
            "english": [],
            "mixed": []
        }

        # Load from train.json
        train_file = sample_dir / "train.json"
        if train_file.exists():
            with open(train_file, 'r', encoding='utf-8') as f:
                samples = json.load(f)
            
            for sample in samples:
                # Detect language using Unicode ranges
                bengali_chars = sum(1 for c in sample if '\u0980' <= c <= '\u09FF')
                english_chars = sum(1 for c in sample if c.isalpha() and '\u0041' <= c <= '\u007A')
                
                if bengali_chars > 0 and english_chars > 0:
                    texts["mixed"].append(sample)
                elif bengali_chars > 0:
                    texts["bengali"].append(sample)
                elif english_chars > 0:
                    texts["english"].append(sample)

        return texts

    def evaluate_word_level_tokenizer(self, texts: Dict[str, List[str]]) -> Dict[str, any]:
        """Evaluate current word-level tokenizer"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from tokenizer import SimpleTokenizer

        tokenizer = SimpleTokenizer(vocab_size=5000)
        
        # Build vocabulary from all texts
        all_texts = texts["bengali"] + texts["english"] + texts["mixed"]
        tokenizer.build_vocab(all_texts, min_freq=1)

        results = {
            "vocab_size": tokenizer.get_vocab_size(),
            "special_tokens": {
                "PAD": 0,
                "UNK": 1,
                "BOS": 2,
                "EOS": 3
            },
            "language_metrics": {}
        }

        for lang, samples in texts.items():
            if not samples:
                continue

            total_tokens = 0
            unknown_tokens = 0
            token_counts = []

            for text in samples:
                tokens = tokenizer.encode(text, add_special_tokens=False)
                token_counts.append(len(tokens))
                total_tokens += len(tokens)
                unknown_tokens += tokens.count(tokenizer.word_to_id.get(tokenizer.UNK_TOKEN, 1))

            avg_tokens_per_sentence = sum(token_counts) / len(token_counts)
            unknown_rate = unknown_tokens / total_tokens if total_tokens > 0 else 0

            results["language_metrics"][lang] = {
                "sample_count": len(samples),
                "total_tokens": total_tokens,
                "avg_tokens_per_sentence": avg_tokens_per_sentence,
                "unknown_token_rate": unknown_rate,
                "unique_words_in_vocab": len([w for w in tokenizer.word_to_id.keys() if w not in [tokenizer.PAD_TOKEN, tokenizer.UNK_TOKEN, tokenizer.BOS_TOKEN, tokenizer.EOS_TOKEN]])
            }

        return results

    def analyze_bengali_morphology(self, texts: List[str]) -> Dict[str, any]:
        """Analyze Bengali morphology to assess subword needs"""
        if not texts:
            return {"error": "No Bengali texts provided"}

        # Count words and character patterns
        word_lengths = []
        suffix_patterns = Counter()
        total_words = 0

        for text in texts:
            words = text.split()
            for word in words:
                word_lengths.append(len(word))
                total_words += 1
                
                # Common Bengali suffixes
                if word.endswith('ে'):
                    suffix_patterns['ে'] += 1
                if word.endswith('র'):
                    suffix_patterns['র'] += 1
                if word.endswith('রা'):
                    suffix_patterns['রা'] += 1
                if word.endswith('টি'):
                    suffix_patterns['টি'] += 1

        return {
            "total_words": total_words,
            "avg_word_length": sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            "max_word_length": max(word_lengths) if word_lengths else 0,
            "common_suffixes": dict(suffix_patterns.most_common(10))
        }

    def evaluate_vocabulary_sizes(self, texts: Dict[str, List[str]], vocab_sizes: List[int]) -> Dict[str, any]:
        """Evaluate different vocabulary sizes"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from tokenizer import SimpleTokenizer

        results = {}

        for vocab_size in vocab_sizes:
            tokenizer = SimpleTokenizer(vocab_size=vocab_size)
            all_texts = texts["bengali"] + texts["english"] + texts["mixed"]
            tokenizer.build_vocab(all_texts, min_freq=1)

            unknown_rates = {}
            for lang, samples in texts.items():
                if not samples:
                    continue

                total_tokens = 0
                unknown_tokens = 0

                for text in samples:
                    tokens = tokenizer.encode(text, add_special_tokens=False)
                    total_tokens += len(tokens)
                    unknown_tokens += tokens.count(tokenizer.word_to_id.get(tokenizer.UNK_TOKEN, 1))

                unknown_rates[lang] = unknown_tokens / total_tokens if total_tokens > 0 else 0

            results[vocab_size] = {
                "actual_vocab_size": tokenizer.get_vocab_size(),
                "unknown_rates": unknown_rates
            }

        return results

    def generate_report(self, output_path: str = None):
        """Generate comprehensive tokenizer evaluation report"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent / "docs" / "ai-brain" / "tokenizer_evaluation_report.json"
        else:
            output_path = Path(output_path)

        print("[Tokenizer Evaluation] Loading sample texts...")
        texts = self.load_sample_texts()

        print(f"[Tokenizer Evaluation] Loaded samples: Bengali={len(texts['bengali'])}, English={len(texts['english'])}, Mixed={len(texts['mixed'])}")

        print("[Tokenizer Evaluation] Evaluating current word-level tokenizer...")
        word_level_results = self.evaluate_word_level_tokenizer(texts)

        print("[Tokenizer Evaluation] Analyzing Bengali morphology...")
        morphology = self.analyze_bengali_morphology(texts["bengali"])

        print("[Tokenizer Evaluation] Evaluating different vocabulary sizes...")
        vocab_size_results = self.evaluate_vocabulary_sizes(texts, [100, 500, 1000, 2000, 5000, 10000, 20000, 50000])

        report = {
            "evaluation_timestamp": "2026-11-03",
            "current_tokenizer": {
                "type": "word-level",
                "vocab_size": 74,
                "limitation": "critically small for bilingual use"
            },
            "word_level_evaluation": word_level_results,
            "bengali_morphology_analysis": morphology,
            "vocabulary_size_evaluation": vocab_size_results,
            "recommendations": {
                "current_status": "inadequate",
                "recommended_action": "replace with subword tokenizer (SentencePiece or BPE)",
                "target_vocab_size": "30000-50000",
                "rationale": "74-token vocabulary and word-level tokenization cannot handle Bengali morphology or bilingual conversation"
            }
        }

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"[Tokenizer Evaluation] Report saved to {output_path}")
        return report


if __name__ == "__main__":
    evaluator = TokenizerEvaluator()
    report = evaluator.generate_report()
    print("\n=== TOKENIZER EVALUATION SUMMARY ===")
    print(json.dumps(report["recommendations"], indent=2))
