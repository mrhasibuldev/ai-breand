"""
Test actual inference using the running ML service.
"""

import requests
import json

ML_SERVICE_URL = "http://127.0.0.1:8000"

print("=" * 80)
print("NEXUSAI REAL INFERENCE TEST")
print("=" * 80)

# Test 1: Health check
print("\n[TEST 1] Health Check")
try:
    response = requests.get(f"{ML_SERVICE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 2: Model status
print("\n[TEST 2] Model Status")
try:
    response = requests.get(f"{ML_SERVICE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 3: Bengali inference
print("\n[TEST 3] Bengali Inference")
bengali_payload = {
    "message": "তুমি কে?",
    "language": "bengali",
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.9,
    "max_new_tokens": 50
}
try:
    response = requests.post(f"{ML_SERVICE_URL}/orchestrate", json=bengali_payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response source: {result.get('source', 'UNKNOWN')}")
    print(f"Response: {result.get('response', 'NO RESPONSE')}")
    print(f"Generated tokens: {result.get('generated_tokens', 'N/A')}")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 4: English inference
print("\n[TEST 4] English Inference")
english_payload = {
    "message": "What is your name?",
    "language": "english",
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.9,
    "max_new_tokens": 50
}
try:
    response = requests.post(f"{ML_SERVICE_URL}/orchestrate", json=english_payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response source: {result.get('source', 'UNKNOWN')}")
    print(f"Response: {result.get('response', 'NO RESPONSE')}")
    print(f"Generated tokens: {result.get('generated_tokens', 'N/A')}")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 5: Empty input
print("\n[TEST 5] Empty Input")
empty_payload = {
    "message": "",
    "language": "english",
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.9,
    "max_new_tokens": 50
}
try:
    response = requests.post(f"{ML_SERVICE_URL}/orchestrate", json=empty_payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response source: {result.get('source', 'UNKNOWN')}")
    print(f"Response: {result.get('response', 'NO RESPONSE')}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 80)
print("INFERENCE TEST COMPLETE")
print("=" * 80)
