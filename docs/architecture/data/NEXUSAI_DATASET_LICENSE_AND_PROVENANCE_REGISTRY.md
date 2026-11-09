# NEXUSAI DATASET LICENSE & PROVENANCE REGISTRY

| Dataset | Source | License | Commercial | Status | Records | Tokens | Used in |
|---|---|---|---|---|---|---|---|
| Bangla Wikipedia | sagorsarker/bangla-wikipedia | MIT tag; content CC BY-SA 3.0 | attribution+SA | APPROVED w/ attribution | 171,674 raw / 168,962 clean | 112.9M | run4 corpus (45K sample) |
| Sangraha BN | ai4bharat/sangraha | CC BY 4.0 | yes | APPROVED (partial) | 9,206 / 9,172 | 7.7M | run4 corpus (9K) |
| BongChat | lumatic-ai/BongChat-v1-253k | MIT | yes | APPROVED | 252,622 avail / 150K dl / 113,446 clean | 25.4M raw / 13.4M clean | run4 corpus (30K) |
| BanglaCoRe-5000 | Maruf204949/BanglaCoRe-5000 | CC BY 4.0 (card) | — | GATED 401 | 0 | — | none |
| TinyStories | roneneldan/TinyStories | MIT | yes | APPROVED | 60,000 | ~16.5M | run4 corpus |
| english_first | internal mix (dolly Apache-2.0, gsm8k MIT, own corpora) | mixed | yes | APPROVED | 63,876 | 7.43M | runs 1–3 + run4 |
| reasoning_v1 | nexusai-authored-deterministic | own | yes | APPROVED | 3,411 train + 300 test | ~0.6M×3 | run4 corpus |
| love_emotion_* | self-authored | nexusai | yes | APPROVED | 69 | tiny | not yet |
| phase9_1 BN chat/sft | spedrox-sac MIT / worldjit Apache-2.0 | yes | APPROVED | 741 | <0.1M | not yet |
| phase9_2 corpus/bengali.txt | unknown | — | HOLD | — | — | excluded |
| alpaca_data.json | tatsu-lab/stanford_alpaca | "Apache-2.0" meta | — | EXCLUDED | 52,002 | ~8M | NOT used — GPT-3.5-generated, independence violation |
| BanglaRQA / PROSHNO / bengalichat | various | CC BY-NC | no | EXCLUDED | — | — | non-commercial only |
| REVEAL-Bangla | khondoker/reveal-bangla | CC BY-ND 4.0 | no | EXCLUDED | — | — | no-derivatives |

## Policy
- Repo license tag ≠ blanket clearance; underlying content licenses tracked per record (`license` field in every cleaned record).
- NC datasets excluded unless owner approves commercial restriction.
- AI-generated data (alpaca) excluded under independence rule.
