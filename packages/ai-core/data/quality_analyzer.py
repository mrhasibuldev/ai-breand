"""
Data Quality Analyzer

Autonomous system that evaluates data quality and makes decisions
about data retention and improvement.
"""

import re
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """
    Autonomous data quality analyzer that evaluates and improves data
    """

    def __init__(self):
        """Initialize quality analyzer"""
        self.quality_metrics = {
            "length_variance": 0.3,
            "vocabulary_diversity": 0.5,
            "coherence_score": 0.6,
            "uniqueness": 0.7
        }

        self.quality_history = []

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze quality of a text

        Args:
            text: Text to analyze

        Returns:
            Dictionary of quality metrics
        """
        metrics = {}

        # Length analysis
        word_count = len(text.split())
        char_count = len(text)
        metrics["word_count"] = word_count
        metrics["char_count"] = char_count
        metrics["length_score"] = min(1.0, word_count / 20.0)  # Ideal: 20+ words

        # Vocabulary diversity
        words = text.lower().split()
        unique_words = set(words)
        if len(words) > 0:
            metrics["vocab_diversity"] = len(unique_words) / len(words)
        else:
            metrics["vocab_diversity"] = 0.0

        # Coherence (sentence structure)
        sentences = re.split(r'[.!?]+', text)
        metrics["sentence_count"] = len([s for s in sentences if s.strip()])
        metrics["avg_sentence_length"] = word_count / max(1, metrics["sentence_count"])

        # Pattern quality
        metrics["has_question"] = 1.0 if '?' in text else 0.0
        metrics["has_punctuation"] = 1.0 if any(p in text for p in '.!?') else 0.0

        # Overall quality score
        metrics["overall_score"] = (
            metrics["length_score"] * 0.3 +
            metrics["vocab_diversity"] * 0.3 +
            metrics["has_punctuation"] * 0.2 +
            (1.0 - abs(metrics["avg_sentence_length"] - 15) / 15) * 0.2
        )

        return metrics

    def analyze_qa_pair(self, question: str, answer: str) -> Dict[str, Any]:
        """
        Analyze quality of a QA pair

        Args:
            question: Question text
            answer: Answer text

        Returns:
            Quality analysis
        """
        question_metrics = self.analyze_text(question)
        answer_metrics = self.analyze_text(answer)

        # Relevance check (basic)
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(question_words & answer_words) / max(1, len(question_words))

        analysis = {
            "question_metrics": question_metrics,
            "answer_metrics": answer_metrics,
            "relevance_score": overlap,
            "pair_quality": (
                question_metrics["overall_score"] * 0.4 +
                answer_metrics["overall_score"] * 0.4 +
                overlap * 0.2
            )
        }

        return analysis

    def analyze_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze quality of entire dataset

        Args:
            data: Dataset to analyze

        Returns:
            Dataset quality analysis
        """
        if not data:
            return {"error": "Empty dataset"}

        overall_scores = []
        individual_analyses = []

        for item in data:
            if "question" in item and "answer" in item:
                analysis = self.analyze_qa_pair(item["question"], item["answer"])
                overall_scores.append(analysis["pair_quality"])
                individual_analyses.append({
                    "item_id": item.get("id", "unknown"),
                    "quality": analysis["pair_quality"]
                })
            elif "text" in item:
                metrics = self.analyze_text(item["text"])
                overall_scores.append(metrics["overall_score"])
                individual_analyses.append({
                    "item_id": item.get("id", "unknown"),
                    "quality": metrics["overall_score"]
                })

        if not overall_scores:
            return {"error": "No valid items to analyze"}

        avg_quality = sum(overall_scores) / len(overall_scores)
        min_quality = min(overall_scores)
        max_quality = max(overall_scores)

        # Identify low-quality items
        threshold = avg_quality * 0.7
        low_quality = [a for a in individual_analyses if a["quality"] < threshold]

        analysis = {
            "total_items": len(data),
            "average_quality": avg_quality,
            "min_quality": min_quality,
            "max_quality": max_quality,
            "low_quality_count": len(low_quality),
            "low_quality_items": low_quality[:10],  # Top 10 worst
            "individual_analyses": individual_analyses,
            "analyzed_at": datetime.now().isoformat()
        }

        self.quality_history.append(analysis)
        return analysis

    def filter_dataset(self, data: List[Dict[str, Any]], min_quality: float = 0.5) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter dataset by quality threshold

        Args:
            data: Dataset to filter
            min_quality: Minimum quality threshold

        Returns:
            Tuple of (high_quality_data, low_quality_data)
        """
        high_quality = []
        low_quality = []

        for item in data:
            if "question" in item and "answer" in item:
                analysis = self.analyze_qa_pair(item["question"], item["answer"])
                quality = analysis["pair_quality"]
            elif "text" in item:
                metrics = self.analyze_text(item["text"])
                quality = metrics["overall_score"]
            else:
                quality = 0.0

            if quality >= min_quality:
                high_quality.append(item)
            else:
                low_quality.append(item)

        logger.info(f"Filtered dataset: {len(high_quality)} high quality, {len(low_quality)} low quality")
        return high_quality, low_quality

    def suggest_improvements(self, text: str) -> List[str]:
        """
        Suggest improvements for a text

        Args:
            text: Text to analyze

        Returns:
            List of improvement suggestions
        """
        metrics = self.analyze_text(text)
        suggestions = []

        if metrics["word_count"] < 10:
            suggestions.append("Add more detail to increase length")

        if metrics["vocab_diversity"] < 0.5:
            suggestions.append("Use more varied vocabulary")

        if metrics["has_punctuation"] == 0.0:
            suggestions.append("Add proper punctuation")

        if metrics["avg_sentence_length"] < 5:
            suggestions.append("Combine short sentences for better flow")
        elif metrics["avg_sentence_length"] > 25:
            suggestions.append("Break up long sentences for readability")

        return suggestions

    def improve_text(self, text: str) -> str:
        """
        Automatically improve text based on quality analysis

        Args:
            text: Text to improve

        Returns:
            Improved text
        """
        improvements = self.suggest_improvements(text)
        improved = text

        # Apply basic improvements
        if "Add proper punctuation" in improvements:
            if not improved.endswith(('.', '!', '?')):
                improved += "."

        # Capitalize first letter
        if improved:
            improved = improved[0].upper() + improved[1:]

        return improved


class AutonomousDecisionMaker:
    """
    Makes autonomous decisions about data retention and processing
    """

    def __init__(self, quality_analyzer: DataQualityAnalyzer):
        """
        Initialize decision maker

        Args:
            quality_analyzer: Quality analyzer instance
        """
        self.quality_analyzer = quality_analyzer
        self.decision_history = []

    def should_retain(self, data_item: Dict[str, Any], threshold: float = 0.5) -> bool:
        """
        Decide whether to retain a data item

        Args:
            data_item: Data item to evaluate
            threshold: Quality threshold

        Returns:
            Decision (True = retain, False = discard)
        """
        if "question" in item and "answer" in item:
            analysis = self.quality_analyzer.analyze_qa_pair(item["question"], item["answer"])
            quality = analysis["pair_quality"]
        elif "text" in item:
            metrics = self.quality_analyzer.analyze_text(item["text"])
            quality = metrics["overall_score"]
        else:
            quality = 0.0

        decision = quality >= threshold

        self.decision_history.append({
            "item_id": data_item.get("id", "unknown"),
            "quality": quality,
            "threshold": threshold,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })

        return decision

    def optimize_threshold(self, data: List[Dict[str, Any]]) -> float:
        """
        Automatically determine optimal quality threshold

        Args:
            data: Dataset to analyze

        Returns:
            Optimal threshold
        """
        analysis = self.quality_analyzer.analyze_dataset(data)

        if "average_quality" in analysis:
            # Set threshold at 70% of average
            threshold = analysis["average_quality"] * 0.7
            logger.info(f"Optimized threshold to {threshold:.3f}")
            return threshold

        return 0.5  # Default threshold

    def batch_process(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process batch of data with autonomous decisions

        Args:
            data: Dataset to process

        Returns:
            Processing results
        """
        # Determine optimal threshold
        threshold = self.optimize_threshold(data)

        # Filter data
        high_quality, low_quality = self.quality_analyzer.filter_dataset(data, threshold)

        # Generate improvement suggestions for low quality
        improvements = []
        for item in low_quality[:5]:  # Limit to top 5
            if "text" in item:
                suggestions = self.quality_analyzer.suggest_improvements(item["text"])
                improvements.append({
                    "item_id": item.get("id", "unknown"),
                    "suggestions": suggestions
                })

        results = {
            "threshold_used": threshold,
            "retained_count": len(high_quality),
            "discarded_count": len(low_quality),
            "improvement_suggestions": improvements,
            "processed_at": datetime.now().isoformat()
        }

        return results


if __name__ == "__main__":
    # Example usage
    analyzer = DataQualityAnalyzer()

    # Analyze sample text
    sample_text = "This is a sample text for quality analysis."
    metrics = analyzer.analyze_text(sample_text)
    print(f"Text metrics: {metrics}")

    # Analyze QA pair
    question = "What is machine learning?"
    answer = "Machine learning is a subset of AI that enables systems to learn from data."
    qa_analysis = analyzer.analyze_qa_pair(question, answer)
    print(f"QA analysis: {qa_analysis}")

    # Decision maker
    decision_maker = AutonomousDecisionMaker(analyzer)

    sample_data = [
        {"id": "1", "question": question, "answer": answer},
        {"id": "2", "text": "Short text."},
        {"id": "3", "text": "This is a much longer and more detailed text that should have better quality metrics because it contains more words and better structure."}
    ]

    results = decision_maker.batch_process(sample_data)
    print(f"Batch processing results: {results}")
