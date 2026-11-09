# NEXUSAI ENGLISH DATA EXPANSION REPORT

## Added
- **TinyStories** (`roneneldan/TinyStories`, MIT): 60,000 stories / 58.9MB → `data/raw_english/tinystories/tinystories.jsonl`, sha256 `3f4ea528…`
- Streamed subset (cap 200MB/60K docs); full corpus is ~2GB+ — expandable later

## Excluded (documented)
- `alpaca_data.json` (52,002 pairs): GPT-3.5-generated → independence violation, NOT used
- NC-licensed sets: excluded

## Existing (already in corpus)
- english_first train: 61,960 docs / 7.2M tokens
- dolly-15k, gsm8k cleaned: inside english_first

## English total in Run4 corpus: ~17M tokens (121,960 docs)
