import json
import sys
from collections import Counter

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

data_file = "experimental/phase10/datasets/train.json"
with open(data_file, encoding='utf-8') as f:
    data = json.load(f)

print(f"Total samples: {len(data)}")

# Check for duplicates
texts = [item.get('text', '') for item in data]
duplicates = len(texts) - len(set(texts))
print(f"Duplicate samples: {duplicates}")

# Check for empty or invalid
empty_count = sum(1 for t in texts if not t or t.strip() == '')
print(f"Empty samples: {empty_count}")

# Check text lengths
lengths = [len(t) for t in texts]
print(f"Average length: {sum(lengths)/len(lengths):.1f}")
print(f"Min length: {min(lengths)}")
print(f"Max length: {max(lengths)}")

# Language analysis
bengali = 0
english = 0
mixed = 0
math = 0

for item in data:
    text = item.get('text', '')
    has_bengali = any('আ' <= c <= 'য়' for c in text)
    has_english = any('a' <= c <= 'z' or 'A' <= c <= 'Z' for c in text)
    has_math = any(c in ['=', '+', '-', '*', '/', '<', '>', '<<', '>>'] for c in text)

    if has_bengali and has_english:
        mixed += 1
    elif has_bengali:
        bengali += 1
    elif has_english:
        english += 1

    if has_math:
        math += 1

print(f"\nLanguage breakdown:")
print(f"Bengali: {bengali} ({bengali/len(data)*100:.1f}%)")
print(f"English: {english} ({english/len(data)*100:.1f}%)")
print(f"Mixed: {mixed} ({mixed/len(data)*100:.1f}%)")
print(f"Math content: {math} ({math/len(data)*100:.1f}%)")

# Check token distribution
all_tokens = []
for item in data:
    all_tokens.extend(item.get('tokens', []))

print(f"\nToken statistics:")
print(f"Total tokens: {len(all_tokens)}")
print(f"Unique tokens: {len(set(all_tokens))}")
print(f"Average tokens per sample: {len(all_tokens)/len(data):.1f}")

# Show some samples
print(f"\nSample 1 (Bengali):")
print(data[0].get('text', ''))
print(f"Tokens: {data[0].get('tokens', [])[:10]}...")

print(f"\nSample 2 (English/Math):")
print(data[1].get('text', ''))
print(f"Tokens: {data[1].get('tokens', [])[:10]}...")
