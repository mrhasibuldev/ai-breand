"""
Model Evaluator

Honest evaluation suite for model capabilities.
"""

import torch
import time
import json
from typing import Dict, List, Any
from tokenizer.tokenizer import SimpleTokenizer
from neural.transformer import SmallTransformer
from inference.generator import TextGenerator


class ModelEvaluator:
    """
    Honest model evaluator.
    """

    def __init__(self, model: SmallTransformer, tokenizer: SimpleTokenizer):
        """
        Initialize evaluator.

        Args:
            model: Trained model
            tokenizer: Tokenizer instance
        """
        self.model = model
        self.tokenizer = tokenizer
        self.generator = TextGenerator(model, tokenizer, device="cpu")
        self.results = {}

    def test_basic_generation(self) -> Dict[str, Any]:
        """Test basic language generation"""
        print("\n" + "=" * 60)
        print("TEST: Basic Language Generation")
        print("=" * 60)

        prompts = [
            "The sky is",
            "I love",
            "Hello",
            "What is"
        ]

        results = []
        for prompt in prompts:
            try:
                generated = self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=20,
                    temperature=0.8,
                    do_sample=True
                )
                results.append({
                    "prompt": prompt,
                    "generated": generated,
                    "success": True
                })
                print(f"Prompt: '{prompt}' -> '{generated}'")
            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
                print(f"Prompt: '{prompt}' -> ERROR: {e}")

        self.results["basic_generation"] = results
        return results

    def test_unseen_prompts(self) -> Dict[str, Any]:
        """Test with prompts not in training data"""
        print("\n" + "=" * 60)
        print("TEST: Unseen Prompts (Generalization)")
        print("=" * 60)

        # These should NOT be in the synthetic dataset
        unseen_prompts = [
            "The weather today is",
            "Can you help me with",
            "What is the meaning of",
            "I want to learn about",
            "Tell me a story about"
        ]

        results = []
        for prompt in unseen_prompts:
            try:
                generated = self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=15,
                    temperature=0.8,
                    do_sample=True
                )
                results.append({
                    "prompt": prompt,
                    "generated": generated,
                    "success": True
                })
                print(f"Prompt: '{prompt}' -> '{generated}'")
            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
                print(f"Prompt: '{prompt}' -> ERROR: {e}")

        self.results["unseen_prompts"] = results
        return results

    def test_question_answering(self) -> Dict[str, Any]:
        """Test question answering capability"""
        print("\n" + "=" * 60)
        print("TEST: Question Answering")
        print("=" * 60)

        questions = [
            "What is the capital of France?",
            "What is water made of?",
            "What is gravity?",
            "What is a computer?",
            "What is artificial intelligence?"
        ]

        results = []
        for question in questions:
            try:
                answer = self.generator.generate(
                    prompt=question,
                    max_new_tokens=20,
                    temperature=0.7,
                    do_sample=True
                )
                results.append({
                    "question": question,
                    "answer": answer,
                    "success": True
                })
                print(f"Q: '{question}' -> A: '{answer}'")
            except Exception as e:
                results.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
                print(f"Q: '{question}' -> ERROR: {e}")

        self.results["question_answering"] = results
        return results

    def test_multi_turn_conversation(self) -> Dict[str, Any]:
        """Test multi-turn conversation capability"""
        print("\n" + "=" * 60)
        print("TEST: Multi-turn Conversation")
        print("=" * 60)

        # Simulate a conversation
        conversation = [
            "Hello",
            "How are you?",
            "What can you do?"
        ]

        results = []
        context = ""

        for i, user_message in enumerate(conversation):
            try:
                prompt = context + user_message if context else user_message
                response = self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=15,
                    temperature=0.8,
                    do_sample=True
                )
                results.append({
                    "turn": i + 1,
                    "user": user_message,
                    "assistant": response,
                    "success": True
                })
                print(f"Turn {i+1}: User: '{user_message}' -> Assistant: '{response}'")
                context = prompt + " " + response + " "
            except Exception as e:
                results.append({
                    "turn": i + 1,
                    "user": user_message,
                    "error": str(e),
                    "success": False
                })
                print(f"Turn {i+1}: User: '{user_message}' -> ERROR: {e}")

        self.results["multi_turn_conversation"] = results
        return results

    def test_context_retention(self) -> Dict[str, Any]:
        """Test if model retains context from previous turns"""
        print("\n" + "=" * 60)
        print("TEST: Context Retention")
        print("=" * 60)

        # Test if model remembers information from earlier in the prompt
        prompt = "My name is Alice. I live in Paris. What is my name?"
        try:
            response = self.generator.generate(
                prompt=prompt,
                max_new_tokens=15,
                temperature=0.7,
                do_sample=True
            )
            result = {
                "prompt": prompt,
                "response": response,
                "contains_name": "Alice" in response,
                "success": True
            }
            print(f"Prompt: '{prompt}'")
            print(f"Response: '{response}'")
            print(f"Contains 'Alice': {result['contains_name']}")
        except Exception as e:
            result = {
                "prompt": prompt,
                "error": str(e),
                "success": False
            }
            print(f"ERROR: {e}")

        self.results["context_retention"] = result
        return result

    def test_repetition_detection(self) -> Dict[str, Any]:
        """Detect if model just repeats input"""
        print("\n" + "=" * 60)
        print("TEST: Repetition Detection")
        print("=" * 60)

        prompts = [
            "The sky is blue",
            "I love programming",
            "Hello world"
        ]

        repetition_count = 0
        total_tests = len(prompts)

        results = []
        for prompt in prompts:
            try:
                generated = self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=10,
                    temperature=0.8,
                    do_sample=True
                )
                is_repetition = generated.lower() == prompt.lower()
                if is_repetition:
                    repetition_count += 1

                results.append({
                    "prompt": prompt,
                    "generated": generated,
                    "is_repetition": is_repetition,
                    "success": True
                })
                print(f"Prompt: '{prompt}' -> '{generated}' (Repetition: {is_repetition})")
            except Exception as e:
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
                print(f"ERROR: {e}")

        repetition_rate = repetition_count / total_tests if total_tests > 0 else 0

        summary = {
            "results": results,
            "repetition_count": repetition_count,
            "total_tests": total_tests,
            "repetition_rate": repetition_rate
        }

        print(f"\nRepetition Rate: {repetition_rate:.2%}")

        self.results["repetition_detection"] = summary
        return summary

    def test_unknown_question_handling(self) -> Dict[str, Any]:
        """Test how model handles unknown/invalid questions"""
        print("\n" + "=" * 60)
        print("TEST: Unknown Question Handling")
        print("=" * 60)

        unknown_questions = [
            "What is the meaning of life?",
            "Who invented the internet?",
            "What is the stock price of Apple?",
            "What is quantum entanglement?"
        ]

        results = []
        for question in unknown_questions:
            try:
                answer = self.generator.generate(
                    prompt=question,
                    max_new_tokens=15,
                    temperature=0.7,
                    do_sample=True
                )
                results.append({
                    "question": question,
                    "answer": answer,
                    "success": True
                })
                print(f"Q: '{question}' -> A: '{answer}'")
            except Exception as e:
                results.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
                print(f"ERROR: {e}")

        self.results["unknown_questions"] = results
        return results

    def test_invalid_input_handling(self) -> Dict[str, Any]:
        """Test how model handles invalid input"""
        print("\n" + "=" * 60)
        print("TEST: Invalid Input Handling")
        print("=" * 60)

        invalid_inputs = [
            "",  # Empty string
            "   ",  # Only spaces
            "!!!@@@###",  # Only special characters
            "a" * 1000,  # Very long string
        ]

        results = []
        for invalid_input in invalid_inputs:
            try:
                generated = self.generator.generate(
                    prompt=invalid_input,
                    max_new_tokens=10,
                    temperature=0.8,
                    do_sample=True
                )
                results.append({
                    "input": invalid_input[:50] + "..." if len(invalid_input) > 50 else invalid_input,
                    "generated": generated,
                    "success": True
                })
                print(f"Input: '{invalid_input[:50]}...' -> '{generated}'")
            except Exception as e:
                results.append({
                    "input": invalid_input[:50] + "..." if len(invalid_input) > 50 else invalid_input,
                    "error": str(e),
                    "success": False
                })
                print(f"Input: '{invalid_input[:50]}...' -> ERROR: {e}")

        self.results["invalid_input"] = results
        return results

    def test_inference_latency(self) -> Dict[str, Any]:
        """Test inference latency"""
        print("\n" + "=" * 60)
        print("TEST: Inference Latency")
        print("=" * 60)

        prompt = "The sky is"
        latencies = []

        for i in range(10):
            start_time = time.time()
            try:
                generated = self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=20,
                    temperature=0.8,
                    do_sample=True
                )
                latency = (time.time() - start_time) * 1000  # ms
                latencies.append(latency)
                print(f"Run {i+1}: {latency:.2f}ms")
            except Exception as e:
                print(f"Run {i+1}: ERROR: {e}")

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)

            summary = {
                "avg_latency_ms": avg_latency,
                "min_latency_ms": min_latency,
                "max_latency_ms": max_latency,
                "runs": len(latencies)
            }

            print(f"\nAverage: {avg_latency:.2f}ms")
            print(f"Min: {min_latency:.2f}ms")
            print(f"Max: {max_latency:.2f}ms")

            self.results["inference_latency"] = summary
            return summary
        else:
            return {"error": "All runs failed"}

    def test_cpu_memory_usage(self) -> Dict[str, Any]:
        """Test CPU memory usage during inference"""
        print("\n" + "=" * 60)
        print("TEST: CPU Memory Usage")
        print("=" * 60)

        try:
            import psutil
            process = psutil.Process()

            # Baseline memory
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
            print(f"Memory before inference: {mem_before:.2f} MB")

            # Run inference
            prompt = "The sky is"
            for _ in range(5):
                self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=20,
                    temperature=0.8,
                    do_sample=True
                )

            # Memory after
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            print(f"Memory after inference: {mem_after:.2f} MB")

            summary = {
                "memory_before_mb": mem_before,
                "memory_after_mb": mem_after,
                "memory_increase_mb": mem_after - mem_before
            }

            print(f"Memory increase: {summary['memory_increase_mb']:.2f} MB")

            self.results["memory_usage"] = summary
            return summary

        except Exception as e:
            print(f"ERROR: {e}")
            return {"error": str(e)}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all evaluation tests"""
        print("=" * 60)
        print("RUNNING ALL EVALUATION TESTS")
        print("=" * 60)

        self.test_basic_generation()
        self.test_unseen_prompts()
        self.test_question_answering()
        self.test_multi_turn_conversation()
        self.test_context_retention()
        self.test_repetition_detection()
        self.test_unknown_question_handling()
        self.test_invalid_input_handling()
        self.test_inference_latency()
        self.test_cpu_memory_usage()

        return self.results

    def save_results(self, path: str):
        """Save evaluation results to file"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {path}")
