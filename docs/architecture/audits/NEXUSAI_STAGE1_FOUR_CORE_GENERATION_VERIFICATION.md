# NexusAI Stage-1 — Four-Core Generation Verification

**Date:** 2025 (mission session) · **Device:** CPU only (torch 2.14.1+cpu, no CUDA) · **HEAD:** `cb289fb`

## Method

Reproducible script: `packages/ai-core/evaluation/verify_four_core_generation.py`

```
python packages/ai-core/evaluation/verify_four_core_generation.py \
    --models nexus-core-01,nexus-core-02,nexus-core-03,nexus-core-04,nexus-medium \
    --max-new-tokens 48 \
    --out eval_reports/stage1_four_core_generation.json
```

For every model registered in `packages/ai-core/ml-service/model_registry.py`:

1. `registry.validate()` — checkpoint exists + SHA-256 + tokenizer present.
2. `registry.load(device="cpu")` — engine construction.
3. Independent strict `load_state_dict(strict=True)` — missing/unexpected keys counted.
4. Parameter count vs registry `expected_params`.
5. Tokenizer special-token IDs (pad/bos/eos) and vocab size.
6. 24-prompt matrix (6 categories × en/bn/banglish/mixed), greedy decoding (`do_sample=False`, `top_k=1`), `max_new_tokens=48`.
7. Per-generation latency, mechanical quality flags, UTF-8 JSON output.

No external AI APIs, no deterministic handlers, no fallback substitution. Generated text comes only from the registered checkpoint weights.

## Strict-loading results

| Model | Registry validate (SHA-256) | Strict load | Missing/Unexpected keys | Params (actual) | Params (expected) | Match |
|---|---|---|---|---|---|---|
| nexus-core-01 | PASS | PASS* | 0 / 0 | 8,842,560 | 8,842,560 | YES |
| nexus-core-02 | PASS | PASS | 0 / 0 | 20,347,712 | 20,347,712 | YES |
| nexus-core-03 | PASS | PASS | 0 / 0 | 8,842,560 | 8,842,560 | YES |
| nexus-core-04 | PASS | PASS | 0 / 0 | 33,419,072 | 33,419,072 | YES |
| nexus-medium | PASS | PASS | 0 / 0 | 2,452,544 | 2,468,928 | **NO (−16,384)** |

\* Core-01 Run3 checkpoint contains numpy-serialized metadata, so `torch.load(weights_only=True)` fails; `weights_only=False` was required for the trusted local checkpoint. State-dict strictness (`strict=True`) still verified: 0 missing, 0 unexpected keys. Checkpoint SHA-256 matches the pinned registry value.

## Generation results (mechanical)

| Model | Non-empty outputs | Exceptions | Notes |
|---|---|---|---|
| nexus-core-01 | 16 / 24 | 0 | 8 EMPTY_OUTPUT (immediate EOS, ~0.02 s) |
| nexus-core-02 | 24 / 24 | 0 | Near-identical template text for most prompts |
| nexus-core-03 | 24 / 24 | 0 | Bare numbers for every prompt |
| nexus-core-04 | 24 / 24 | 0 | Bengali/English KB-style sentences |
| nexus-medium | 4 / 24 | 0 | Repetitive Bengali fragments / immediate EOS |

Latency (avg per 48-token generation, CPU): core-01 0.44 s, core-02 0.51 s, core-03 0.13 s, core-04 1.18 s, medium 0.02 s (mostly EOS-terminated).

## Real output samples (verbatim, UTF-8 preserved in JSON)

### nexus-core-01 (8.84M, Run3 pretrained LM — PRETRAINING_COMPLETED, loss ≈4.43)

- `Hello! How are you today?` → **EMPTY** (first sampled token = EOS id 3; verified at logit level: EOS logit 10.48 > all others)
- `What is artificial intelligence?` → `The term is the most important to be a model that is a machine of the magneticism. It is a model that is a mod…`
- `তুমি কেমন আছো?` → `The first person is a total of 10 + 3 = <<10+10=15>>15 students. #### 20`
- `What is 15 plus 27?` → `The total number of turtles in the second year, which is 3/4 = <<3*3=15>>15 years old. …`

Character: English document-continuation word salad with math-corpus artifacts (`<<…>>`, `####`). Prompt language largely ignored.

### nexus-core-02 (20.35M, SFT "reasoning")

- `Hello! How are you today?` → `1. Boil water. 2. Add tea leaves.`
- `What is artificial intelligence?` → `1. Boil water.`
- `If all cats are animals and Tom is a cat, is Tom an animal?` → `No, {a} studies.`
- `What is 15 plus 27?` → `1. Boil water. 2. Add tea leaves.`

Character: template/slot-fill collapse — a handful of memorized SFT response patterns regardless of prompt.

### nexus-core-03 (8.84M, SFT "mathematics")

- `Hello! How are you today?` → `15.`
- `What is artificial intelligence?` → `15.`
- `What is 15 plus 27?` → `22.` (incorrect; correct = 42)
- `তুমি কেমন আছো?` → `83.`

Character: emits a bare number for every input. Correct format for math answers, but no question understanding; non-math prompts are not rejected.

### nexus-core-04 (33.42M, SFT "knowledge" — memorization model, 318 curated records)

- `What is artificial intelligence?` → `Artificial intelligence is the simulation of human intelligence by machines, especially computers.`
- `কৃত্রিম বুদ্ধিমত্তা কী?` → `কৃত্রিম বুদ্ধিমত্তা হলো মেশিন, বিশেষ করে কম্পিউটারের মাধ্যমে মানব বুদ্ধিমত্তার অনুকরণ।`
- `Hello! How are you today?` → `আগ্নেয়গিরি হলো এমন একটি খোলা অংশ দিয়ে lava, ছাই ও গ্যাস বেরিয়ে আসে।`
- `What is 15 plus 27?` → `Gravity is the force that carries genetic instructions in living organisms.`

Character: best semantic quality of the four — fluent Bengali/English KB sentences — but prompt-insensitive (nearest-neighbor recall over a small curated corpus); occasional script mixing.

### nexus-medium (2.45M legacy fallback)

- Most prompts → EMPTY (immediate EOS) or repetitive Bengali fragment, e.g. `আমি অনলাইন কোর্স এবং নতুন_probe…` loop.
- Consistent with registry label: "very weak; gibberish-prone; emergency fallback only".

## Quality assessment (honest)

| Model | Mechanical generation | Semantic quality | Verdict |
|---|---|---|---|
| core-01 | PARTIALLY VERIFIED (16/24 non-empty) | Gibberish/word-salad; prompt-insensitive; English-biased | PARTIALLY VERIFIED |
| core-02 | VERIFIED (24/24 text) | Template collapse; prompt ignored | PARTIALLY VERIFIED |
| core-03 | VERIFIED (24/24 text) | Number-only outputs; math answer wrong on tested item | PARTIALLY VERIFIED |
| core-04 | VERIFIED (24/24 text) | Fluent but prompt-insensitive memorization | PARTIALLY VERIFIED |
| medium | PARTIALLY VERIFIED (4/24) | Repetitive gibberish | PARTIALLY VERIFIED (fallback-only) |

**No model demonstrated genuine conversational ability.** All produce neural text from their own weights (provenance verified: `neural_generation_executed` path, no external calls), but none is a working general chatbot. Core-04 is the strongest within its narrow memorized domain; core-03 produces correctly formatted but unreliable math; core-01 is an undertrained base LM awaiting SFT; core-02 is template-bound.

## Machine-readable report

`eval_reports/stage1_four_core_generation.json` — full prompts, outputs, token counts, latencies, provenance, strict-load metadata, memory samples. Bengali text stored as raw UTF-8 (`ensure_ascii=False`); console output was ASCII-escaped for display only — JSON content is identical to raw model output.

## Not performed

No checkpoint/tokenizer/config modification, no training, no Git commit/push.
