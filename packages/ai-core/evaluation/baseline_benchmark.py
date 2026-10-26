"""
Baseline Benchmark for NexusAI Brain

Measures current capability before improvements.
"""

import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, List, Any
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class BaselineBenchmark:
    """Baseline benchmark suite for NexusAI Brain"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.results = []
    
    def run_test(self, question: str, conversation_id: str) -> Dict[str, Any]:
        """Run a single test question"""
        try:
            start_time = time.time()
            
            # Prepare request
            data = json.dumps({
                "message": question,
                "conversation_id": conversation_id
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.api_url}/orchestrate",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    "question": question,
                    "response": response_data.get("response", ""),
                    "latency_ms": latency_ms,
                    "intent": response_data.get("intent", ""),
                    "response_source": response_data.get("response_source", ""),
                    "language": response_data.get("language", ""),
                    "success": True
                }
        except urllib.error.HTTPError as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "question": question,
                "response": f"HTTP {e.code}",
                "latency_ms": latency_ms,
                "success": False
            }
        except Exception as e:
            return {
                "question": question,
                "response": f"Error: {str(e)}",
                "latency_ms": 0,
                "success": False
            }
    
    def categorize_response(self, response: str, expected_source: str) -> str:
        """Categorize response quality"""
        if not response or len(response) < 3:
            return "EMPTY"
        
        # Check for fallback message
        if "দুঃখিত" in response and "পর্যাপ্ত পরিমাণ ডেটা" in response:
            return "FALLBACK"
        
        # Check if it's from deterministic handler
        if expected_source == "DETERMINISTIC_HANDLER":
            return "DETERMINISTIC"
        
        # Check for repetition
        words = response.lower().split()
        if len(set(words)) < len(words) * 0.5:
            return "REPETITIVE"
        
        return "GENERATED"
    
    def run_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        
        print("=" * 60)
        print("NEXUSAI BRAIN - BASELINE BENCHMARK")
        print("=" * 60)
        
        # Test categories
        test_cases = {
            "greetings": [
                "Hello",
                "Hi there",
                "Good morning",
                "What is your name?",
                "How are you?"
            ],
            "general_knowledge": [
                "What is the capital of Japan?",
                "What is photosynthesis?",
                "What is the speed of light?",
                "What is DNA?",
                "What is gravity?"
            ],
            "instruction_following": [
                "Give me three examples of fruits",
                "Explain photosynthesis simply",
                "Compare cats and dogs",
                "Summarize this: The sky is blue."
            ],
            "reasoning": [
                "Which is larger: 10 or 100?",
                "If I have 2 apples and get 3 more, how many do I have?",
                "What is 5 times 5?"
            ],
            "context": [
                "My name is Alex",
                "What is my name?"
            ],
            "bengali": [
                "হ্যালো",
                "তোমার নাম কী?",
                "কেমন আছো?"
            ],
            "banglish": [
                "Hello tumi kemon acho?",
                "Ami ki korte pari?"
            ],
            "unknown": [
                "What is the meaning of X7Z-99?",
                "Who invented the quantum frobnicator?"
            ]
        }
        
        results = {
            "total_tests": 0,
            "successful": 0,
            "failed": 0,
            "categories": {},
            "latency_ms": [],
            "response_sources": {},
            "response_quality": {
                "deterministic": 0,
                "generated": 0,
                "fallback": 0,
                "empty": 0,
                "repetitive": 0
            }
        }
        
        category_id = 0
        for category, questions in test_cases.items():
            print(f"\n[{category.upper()}]")
            category_results = []
            
            for i, question in enumerate(questions):
                conv_id = f"baseline_{category}_{i}"
                result = self.run_test(question, conv_id)
                category_results.append(result)
                
                results["total_tests"] += 1
                if result["success"]:
                    results["successful"] += 1
                    results["latency_ms"].append(result["latency_ms"])
                    
                    # Track response source
                    source = result["response_source"]
                    results["response_sources"][source] = results["response_sources"].get(source, 0) + 1
                    
                    # Categorize quality
                    quality = self.categorize_response(result["response"], source)
                    results["response_quality"][quality] = results["response_quality"].get(quality, 0) + 1
                    
                    print(f"  Q: {question[:50]}...")
                    print(f"  A: {result['response'][:60]}...")
                    print(f"  Source: {source}, Quality: {quality}, Latency: {result['latency_ms']:.1f}ms")
                else:
                    results["failed"] += 1
                    print(f"  Q: {question[:50]}... - FAILED: {result['response']}")
            
            results["categories"][category] = {
                "total": len(questions),
                "successful": len([r for r in category_results if r["success"]]),
                "failed": len([r for r in category_results if not r["success"]])
            }
        
        # Calculate statistics
        if results["latency_ms"]:
            results["avg_latency_ms"] = sum(results["latency_ms"]) / len(results["latency_ms"])
            results["min_latency_ms"] = min(results["latency_ms"])
            results["max_latency_ms"] = max(results["latency_ms"])
        else:
            results["avg_latency_ms"] = 0
            results["min_latency_ms"] = 0
            results["max_latency_ms"] = 0
        
        results["success_rate"] = (results["successful"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary"""
        print("\n" + "=" * 60)
        print("BASELINE BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful: {results['successful']} ({results['success_rate']:.1f}%)")
        print(f"Failed: {results['failed']}")
        print(f"\nLatency:")
        print(f"  Average: {results['avg_latency_ms']:.1f}ms")
        print(f"  Min: {results['min_latency_ms']:.1f}ms")
        print(f"  Max: {results['max_latency_ms']:.1f}ms")
        
        print(f"\nResponse Sources:")
        for source, count in results["response_sources"].items():
            print(f"  {source}: {count}")
        
        print(f"\nResponse Quality:")
        for quality, count in results["response_quality"].items():
            print(f"  {quality}: {count}")
        
        print(f"\nCategory Breakdown:")
        for category, stats in results["categories"].items():
            print(f"  {category}: {stats['successful']}/{stats['total']} successful")
        
        print("=" * 60)
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save benchmark results to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    benchmark = BaselineBenchmark()
    results = benchmark.run_benchmark_suite()
    benchmark.print_summary(results)
    
    # Save results
    output_dir = Path(__file__).parent.parent / "evaluation_results"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "baseline_benchmark_results.json"
    benchmark.save_results(results, str(output_path))
