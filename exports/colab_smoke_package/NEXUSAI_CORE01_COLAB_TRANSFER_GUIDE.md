# NexusAI Core-01 — Colab Transfer Guide (GPU Smoke Test)

**Why manual transfer?** The attention-mask repair + notebook fixes are **uncommitted** — `git clone`/`git pull` on Colab will NOT get them. You must upload the repaired `transformer.py` once.

## Files in this package (`exports/colab_smoke_package/`)

| File | Purpose |
|---|---|
| `transformer.py` | repaired Core-01 model (attention-mask fix) |
| `COLAB_SMOKE_TEST_CELL.py` | the one consolidated smoke-test cell |
| `NEXUSAI_CORE01_COLAB_TRANSFER_MANIFEST.json` | SHA-256 hashes for verification |

## Step-by-step (beginner)

### 1. Open Colab and clone the repo (if not already)

```python
import subprocess
subprocess.run(["git","clone","--depth","1",
                "https://github.com/mrhasibuldev/ai-breand.git","/content/nexusai"], check=True)
```

### 2. Upload the repaired transformer.py

In a Colab cell:

```python
from google.colab import files
import shutil, hashlib, os
up = files.upload()   # <-- select exports/colab_smoke_package/transformer.py
src = list(up.keys())[0]
dst = "/content/nexusai/packages/ai-core/core01/transformer.py"
# backup existing first
if os.path.exists(dst):
    shutil.copy2(dst, dst + ".pre_repair_backup")
shutil.copy(src, dst)
h = hashlib.sha256(open(dst,'rb').read()).hexdigest()
print("installed sha256:", h)
print("expected      : c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc")
print("match:", h == "c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc")
# verify fix marker
s = open(dst, encoding='utf-8').read()
print("mask fix present:", "pad = attention_mask[:, None, :]" in s)
```

**If sha does NOT match or marker missing → STOP, do not run smoke.**

### 3. Mount Drive (for checkpoints + report)

```python
from google.colab import drive
drive.mount("/content/drive")
```

### 4. Run the smoke cell

Open `COLAB_SMOKE_TEST_CELL.py`, copy ALL of it, paste into a new Colab cell, run.

It performs stages A→H and writes a timestamped report to
`/content/drive/MyDrive/NexusAI/audit_reports/`.

### 5. Send me the output

Copy the final `===== SMOKE TEST ... =====` block + any FAIL lines + the report
JSON path. I will verify and tell you whether full training can be approved.

## What the smoke test does NOT do

- No 100M corpus, no real dataset, no full training
- Max 2 optimizer steps via driver + resume test
- Synthetic 300-doc JSONL generated in a temp dir (deleted with session)
