"""
Test script for NexusAI Core-01 evaluation
"""

import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import os

# Add ai-core and models to path
ai_core_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(ai_core_dir, "models")
if ai_core_dir not in sys.path:
    sys.path.insert(0, ai_core_dir)
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from core01.evaluation import ModelEvaluator
from nexusai_core_01.config.model_config import NexusAICore01Config

# Run evaluation
config = NexusAICore01Config()
evaluator = ModelEvaluator(config)

results = evaluator.run_all_tests()

print("\nDetailed results:")
for test_name, result in results.items():
    if test_name != "summary":
        print(f"  {test_name}: {result}")

print(f"\nSummary: {results['summary']}")
