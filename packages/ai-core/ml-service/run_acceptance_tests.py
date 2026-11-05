"""
Phase 1 Final Acceptance Tests
Run 20 tests to verify neural inference
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:8000"

test_inputs = [
    # Bengali
    "তুমি কে?",
    "আমার নাম কী?",
    "আজকের আবহাওয়া সম্পর্কে বলো।",
    "আমি নতুন কিছু শিখতে চাই।",
    "বাংলাদেশ কোথায়?",
    "ঢাকা কি?",
    "ভালো আছ?",
    "ধন্যবাদ",
    "বিদায়",
    "সাহায্য চাই",
    # English
    "Who are you?",
    "What is your name?",
    "How are you?",
    "Thank you",
    "Goodbye",
    "Help me",
    "What is the capital of Bangladesh?",
    "Explain how a neural network learns",
    "Hello",
    "What can you do?"
]

results = []

for i, message in enumerate(test_inputs, 1):
    try:
        start = time.time()
        data = json.dumps({"message": message, "conversation_id": f"acceptance_test_{i}"}).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/orchestrate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            elapsed = (time.time() - start) * 1000
            
            results.append({
                "test": i,
                "input": message,
                "response": response_data.get("response", ""),
                "source": response_data.get("response_source", ""),
                "intent": response_data.get("intent", ""),
                "language": response_data.get("language", ""),
                "latency_ms": elapsed,
                "status": "success"
            })
    except Exception as e:
        results.append({
            "test": i,
            "input": message,
            "response": str(e),
            "source": "ERROR",
            "status": "exception"
        })
    
    time.sleep(0.5)  # Brief pause between requests

# Print results
print("=" * 100)
print("PHASE 1 ACCEPTANCE TEST RESULTS")
print("=" * 100)

neural_count = 0
fallback_count = 0
deterministic_count = 0
error_count = 0

for r in results:
    print(f"\nTest {r['test']}: {r['input']}")
    print(f"  Response: {r['response'][:100]}...")
    print(f"  Source: {r['source']}")
    print(f"  Intent: {r.get('intent', 'N/A')}")
    print(f"  Language: {r.get('language', 'N/A')}")
    print(f"  Latency: {r.get('latency_ms', 0):.2f}ms")
    
    if r['source'] == "NEURAL_MODEL":
        neural_count += 1
    elif r['source'] == "FALLBACK":
        fallback_count += 1
    elif r['source'] == "DETERMINISTIC_HANDLER":
        deterministic_count += 1
    else:
        error_count += 1

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total tests: {len(results)}")
print(f"NEURAL_MODEL: {neural_count}")
print(f"FALLBACK: {fallback_count}")
print(f"DETERMINISTIC_HANDLER: {deterministic_count}")
print(f"ERROR: {error_count}")

# Save to file
with open("acceptance_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nResults saved to acceptance_test_results.json")
