"""
Phase 9.3 - Expanded Test Suite

Creates comprehensive test cases for Bengali, English, and Mixed-language text.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_1_DIR = DATA_DIR / "experimental" / "phase9_1"
PHASE9_3_DIR = DATA_DIR / "experimental" / "phase9_3"
TESTS_DIR = PHASE9_3_DIR / "tests"

# Create directories
TESTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.3 - Expanded Test Suite")
print("="*60)

# Load Phase 9.1 corpus for real examples
phase9_1_corpus = PHASE9_1_DIR / "cleaned" / "combined_cleaned.jsonl"
real_examples = []

with open(phase9_1_corpus, 'r', encoding='utf-8') as f:
    for line in f:
        record = json.loads(line.strip())
        real_examples.append(record['text'])

print(f"\nLoaded {len(real_examples)} real examples from Phase 9.1")

# Expanded Bengali test cases (100+)
bengali_tests = [
    # Basic conversation
    "তুমি কেমন আছো?",
    "আমি ভালো আছি।",
    "আপনার নাম কী?",
    "আমার নাম নুসাইবা।",
    "কোথায় থাকেন?",
    "আমি ঢাকায় থাকি।",
    
    # Questions
    "বাংলাদেশের রাজধানী কোথায়?",
    "তুমি কি আমাকে সাহায্য করতে পারবে?",
    "এটি কীভাবে কাজ করে?",
    "কখন শুরু হবে?",
    
    # Long sentences
    "আমি একটি নতুন কৃত্রিম বুদ্ধিমত্তা তৈরি করছি যা বাংলা এবং ইংরেজি উভয় ভাষায় কথা বলতে পারবে।",
    "বাংলা ভাষার শব্দের গঠন এবং উচ্চারণ অন্যান্য ভাষার থেকে সম্পূর্ণ আলাদা।",
    
    # Punctuation
    "আজকের আবহাওয়া খুব সুন্দর।",
    "আমি বই পড়তে ভালোবাসি।",
    "বাংলাদেশ স্বাধীনতা দিবস ২৬ মার্চ।",
    
    # With numerals
    "পানি জীবনের জন্য অত্যন্ত গুরুত্বপূর্ণ।",
    "শিক্ষা জাতির উন্নতির চাবিক।",
    "১৯৭১ সালে বাংলাদেশ স্বাধীন হয়।",
    
    # Real corpus examples (sampled)
] + real_examples[:50]

# Expanded English test cases (50+)
english_tests = [
    "Hello, how are you?",
    "I am doing well.",
    "What is your name?",
    "My name is Nusaiba.",
    "Where do you live?",
    "I live in Dhaka.",
    "I want to build an advanced AI Brain.",
    "The capital of Bangladesh is Dhaka.",
    "Artificial intelligence is transforming the world.",
    "Today's weather is very beautiful.",
    "Can you help me create a study plan?",
    "Bangladesh Independence Day is March 26.",
    "Water is essential for life.",
    "Education is the key to national progress.",
    "I love reading books.",
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is a subset of artificial intelligence.",
    "Python is a popular programming language.",
    "The model achieved 98% accuracy on the test set.",
    "We need to optimize the training pipeline.",
    "The data preprocessing step is crucial.",
    "Deep learning requires large datasets.",
    "Neural networks consist of multiple layers.",
    "The attention mechanism revolutionized NLP.",
    "Transformers are the foundation of modern AI.",
    "The learning rate determines step size.",
    "Gradient descent optimizes the loss function.",
    "Regularization prevents overfitting.",
    "Batch normalization stabilizes training.",
    "The embedding layer represents words as vectors.",
    "The vocabulary size affects model complexity.",
    "Context length limits input sequence size.",
    "The model checkpoint is saved to disk.",
    "Inference time depends on model size.",
    "GPU acceleration speeds up training.",
    "The tokenizer splits text into tokens.",
    "UNK tokens represent unknown words.",
    "The special tokens include PAD, BOS, and EOS.",
    "The beam search improves generation quality.",
    "Temperature controls randomness in output.",
    "Top-k sampling limits token choices.",
    "The evaluation metrics measure performance.",
    "Cross-validation tests model generalization.",
    "The hyperparameters need tuning.",
    "The learning rate scheduler adjusts dynamically.",
    "Early stopping prevents overtraining.",
    "The model architecture is crucial.",
    "The training dataset must be diverse.",
    "The validation set tunes hyperparameters.",
    "The test set provides final evaluation.",
    "The model should generalize well."
]

# Expanded Mixed-language test cases (50+)
mixed_tests = [
    "Hello, তুমি কেমন আছো?",
    "আমি NexusAI তৈরি করছি, an AI assistant.",
    "Explain machine learning বাংলায়।",
    "আমাকে একটি study plan তৈরি করে দাও।",
    "Today is sunny, আজকের আবহাওয়া সুন্দর।",
    "I want to learn বাংলা ভাষা।",
    "আমি computer science পড়ছি।",
    "The model accuracy is 98%, এটি খুব ভালো।",
    "আমি ঢাকা university থেকে পাস করেছি।",
    "Python একটি popular programming language।",
    "আমি machine learning শিখতে চাই।",
    "The dataset contains 10,000 samples, এটি যথেষ্ট নয়।",
    "আমি artificial intelligence research করছি।",
    "The training time is 2 hours, এটি দীর্ঘ।",
    "আমি GPU চাই for faster training।",
    "The model size is 378 KB, এটি ছোট।",
    "আমি neural network তৈরি করছি।",
    "The tokenizer uses BPE algorithm, এটি efficient।",
    "আমি transformer architecture ব্যবহার করছি।",
    "The vocabulary size is 8,000, এটি appropriate।",
    "আমি attention mechanism যোগ করছি।",
    "The embedding dimension is 64, এটি small।",
    "আমি multi-head attention ব্যবহার করছি।",
    "The context length is 64 tokens, এটি short।",
    "আমি layer normalization যোগ করছি।",
    "The dropout rate is 0.1, এটি standard।",
    "আমি gradient clipping ব্যবহার করছি।",
    "The learning rate is 0.001, এটি reasonable।",
    "আমি Adam optimizer ব্যবহার করছি।",
    "The batch size is 32, এটি common।",
    "আমি data augmentation করছি।",
    "The validation split is 10%, এটি typical।",
    "আমি early stopping ব্যবহার করছি।",
    "The patience is 5 epochs, এটি sensible।",
    "আমি model checkpoint saving করছি।",
    "The save frequency is every epoch, এটি frequent।",
    "আমি logging করছি for monitoring।",
    "The tensorboard helps visualization, এটি useful।",
    "আমি hyperparameter tuning করছি।",
    "The grid search is exhaustive, এটি slow।",
    "আমি random search ব্যবহার করছি।",
    "The Bayesian optimization is efficient, এটি smart।",
    "আমি cross-validation করছি।",
    "The k-fold is 5, এটি balanced।",
    "আমি stratified sampling ব্যবহার করছি।",
    "The class imbalance is handled, এটি important।",
    "আমি precision recall গণনা করছি।",
    "The F1 score is harmonic mean, এটি robust।",
    "আমি ROC curve প্লট করছি।",
    "The AUC is 0.95, এটি excellent।",
    "আমি confusion matrix বিশ্লেষণ করছি।",
    "The true positives are high, এটি good।"
]

print(f"\nTest suite size:")
print(f"  Bengali: {len(bengali_tests)}")
print(f"  English: {len(english_tests)}")
print(f"  Mixed: {len(mixed_tests)}")

# Save test suites
test_suite = {
    "created_timestamp": datetime.now().isoformat(),
    "bengali_tests": bengali_tests,
    "english_tests": english_tests,
    "mixed_tests": mixed_tests
}

test_suite_path = TESTS_DIR / "expanded_test_suite.json"
with open(test_suite_path, 'w', encoding='utf-8') as f:
    json.dump(test_suite, f, indent=2, ensure_ascii=False)

print(f"\nTest suite saved: {test_suite_path}")

print("\n" + "="*60)
print("EXPANDED TEST SUITE COMPLETE")
print("="*60)
