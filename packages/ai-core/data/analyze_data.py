import json

data_file = "experimental/phase10/datasets/train.json"
with open(data_file, encoding='utf-8') as f:
    data = json.load(f)

print(f"Total samples: {len(data)}")

bengali = 0
english = 0
math = 0

for item in data[:100]:
    text = item.get('text', '')
    if 'আ' in text or 'ক' in text or 'ব' in text:
        bengali += 1
    else:
        english += 1
    if '=' in text or '<<' in text or '*' in text:
        math += 1

print(f"First 100 samples: Bengali={bengali}, English={english}, Math={math}")
