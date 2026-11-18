# NexusAI — বাংলা ডেভেলপমেন্ট গাইড

> এই গাইডটি নতুন ডেভেলপারদের জন্য — বাংলায় setup, model architecture, dataset, training এবং বর্তমান status ব্যাখ্যা করা হয়েছে। টেকনিক্যাল term-গুলো English-এই রাখা হয়েছে যাতে command copy-paste করা যায় এবং আসল documentation-এর সাথে মেলে।

---

## ১. NexusAI কী?

NexusAI হলো একটি independent AI project — এর **নিজস্ব** Transformer model, **নিজস্ব** trained weights, **নিজস্ব** tokenizer এবং **নিজস্ব** inference engine আছে। এটি OpenAI/Gemini-র মতো কোনো external AI service ব্যবহার করে না — সব neural text আমাদের model-ই তৈরি করে।

**মূল নীতি:**
- কোনো third-party AI API নেই।
- Deterministic handler (যেমন greeting) আলাদাভাবে label করা হয় — কখনো neural output-এর ভান করা হয় না।
- প্রতিটি claim-এর পেছনে reproducible test বা benchmark report আছে।

## ২. বর্তমান status (সৎ মূল্যায়ন)

| Core | কাজ | মান |
|---|---|---|
| Core-01 (8.8M) | base language model | undertrained — chat prompt-এ অনেক সময় খালি উত্তর |
| Core-02 (20.3M) | reasoning specialist | template-bound — প্রায় সব প্রশ্নে একই response |
| Core-03 (8.8M) | math specialist | শুধু number দেয়; held-out math accuracy ~৯% |
| Core-04 (33.4M) | knowledge specialist | ছোট memorized KB — ভালো কিন্তু narrow |

**মূল কথা:** model-গুলো technically কাজ করে (checkpoint load + neural generation verified), কিন্তু এখনো conversational quality সেখানে নেই।

## ৩. Setup (সহজে)

```bash
git clone https://github.com/mrhasibuldev/ai-breand.git
cd ai-breand
pnpm install
cd packages/ai-core/ml-service
python -m venv .venv
.venv\Scripts\activate          # Windows-এ
pip install -r requirements.txt
# ফিরে গিয়ে .env.example থেকে .env বানান
cd ../../..
pnpm dev        # web:3000 + api:4000
pnpm dev:ml     # ML service:8000
```

Verify: `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`

## ৪. Model কীভাবে কাজ করে?

- **Transformer**: `packages/ai-core/core01/transformer.py` — একটি shared decoder-only architecture। চারটি core-এর architecture একই, কিন্তু config আর weights আলাদা।
- **Tokenizer**: SentencePiece BPE, ৮০০০ vocabulary — English, Bengali, Banglish supported (Banglish-এ fragmentation আছে)।
- **Router**: `model_router.py` — ভাষা detect করে, intent classify করে, সঠিক core-এ পাঠায়।
- **Checkpoint**: `.pt` file — model-এর weights + training state; প্রতিটির SHA-256 আছে।

## ৫. Dataset

- `data/core02_reasoning`, `core03_math`, `core04_knowledge` — প্রতিটিতে `train/validation/test.jsonl` + manifest + checksums।
- `data/unified_conversational/v1–v4` — সাধারণ conversational dataset।
- **V5 এখনো তৈরি হয়নি** — Core-05 training-এর blocker এটাই।

## ৬. Training (শুধু documentation — এখনো কোনো training এই release-এ হয়নি)

- **Pretraining**: raw text দিয়ে next-token prediction (`pretraining_driver.py`)।
- **SFT**: conversation data দিয়ে fine-tuning; শুধু assistant-এর অংশে loss count হয় (`sft_dataset.py`)।
- GPU training Colab-এ হয় (`docs/notebooks/`); authorization gate আছে।
- কোনো checkpoint overwrite করা যাবে না — নতুন versioned folder-এ save হয়।

## ৭. Test চালানো

```bash
python packages/ai-core/evaluation/verify_four_core_generation.py --models nexus-core-01,nexus-core-02,nexus-core-03,nexus-core-04,nexus-medium
python packages/ai-core/evaluation/four_core_test_suite.py
python packages/ai-core/tests/four_core/test_generation_repairs.py
```

## ৮. সীমাবদ্ধতা (সৎ)

- কোনো model এখনো ভালো chatbot নয় — Core-03 math-এ ~৯% সঠিক, Core-02 template response দেয়, Core-01 undertrained, Core-04 শুধু memorized fact দেয়।
- Bengali output: Core-04 ছাড়া বাকি model-গুলোতে বাংলা মানসিক conversation দুর্বল।
- Banglish-এ tokenizer fragmentation — যেমন "Programming" ভেঙে "Pro gr am ming" হয়।
- CPU-only inference — GPU নেই; KV cache নেই তাই বড় context-এ ধীর।

## ৯. পরের কাজ (roadmap)

1. Dataset V5 তৈরি করা (approved next mission)।
2. Core-01-কে SFT করা যাতে chat prompt ঠিকভাবে বোঝে।
3. Core-02/03/04 dataset de-duplicate করে retrain।
4. Core-05 (≈৪৫M params) — V5 ready হলে।

---

*এই document-টি Markdown-এ render হবে। টেকনিক্যাল term-গুলো intentionally English-এ রাখা হয়েছে যাতে command copy-paste করা যায় এবংofficial nomenclature-এর সাথে মেলে।*
