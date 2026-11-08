# NexusAI Core-01 — GPU Smoke Test করার সম্পূর্ণ গাইড (সহজ বাংলা)

এই গাইডে **কিছুই programming knowledge লাগবে না**। শুধু click + paste।

## আপনার কাছে যা লাগবে

`exports\NEXUSAI_COLAB_USER_PACKAGE\` ফোল্ডারের ভিতরে ৪টা file:

| File | কীসের |
|---|---|
| `COLAB_SMOKE_TEST_CELL.py` | smoke test cell (পুরোটা copy করে Colab-এ paste) |
| `transformer.py` | repaired model file (Colab-এ upload) |
| `TRANSFER_MANIFEST.json` | SHA-256 hashes (verify করতে) |
| `SMOKE_TEST_README.md` | quick info |

---

## Step A — File গুলো খুঁজে নিন

File Explorer-এ যান:
```
C:\Users\Nusaiba\Desktop\Ai Breand\exports\NEXUSAI_COLAB_USER_PACKAGE\
```
এই ফোল্ডারটাই আপনার **package** — 여기 থেকে file upload করবেন।

## Step B — Google Colab খুলুন

1. Browser-এ যান: **https://colab.research.google.com**
2. Google account দিয়ে login করুন
3. **File → Upload notebook** → আগের `NexusAI_Core01_Google_Colab_Training.ipynb` select করুন
   (অথবা blank notebook-ও চলবে — smoke cell আলাদা)

## Step C — GPU select করুন

1. উপরে **Runtime** menu-তে click
2. **Change runtime type**
3. **Hardware accelerator** → **T4 GPU** select
4. **Save**

## Step D — Repo clone করুন (একবার)

নতুন cell-এ এটা paste করে run করুন (Shift+Enter):

```python
import subprocess
subprocess.run(["git","clone","--depth","1",
 "https://github.com/mrhasibuldev/ai-breand.git","/content/nexusai"], check=True)
print("clone done")
```

## Step E — Repaired transformer.py upload করুন

এটা **সবচেয়ে গুরুত্বপূর্ণ step** — পুরনো file-এ bug আছে, repaired file লাগবেই।

নতুন cell-এ:

```python
from google.colab import files
import shutil, hashlib, os
up = files.upload()   # এখানে transformer.py select করুন
src = list(up.keys())[0]
dst = "/content/nexusai/packages/ai-core/core01/transformer.py"
if os.path.exists(dst):
    shutil.copy2(dst, dst + ".pre_repair_backup")   # backup
shutil.copy(src, dst)
h = hashlib.sha256(open(dst,'rb').read()).hexdigest()
print("installed sha256:", h)
print("expected        : c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc")
print("MATCH:", h == "c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc")
s = open(dst, encoding='utf-8').read()
print("mask fix present:", "pad = attention_mask[:, None, :]" in s)
```

**যা দেখবেন:**
- `MATCH: True` → ঠিক আছে ✅
- `MATCH: False` বা `mask fix present: False` → **STOP** — ভুল file upload হয়েছে, আমাকে বলুন ❌

## Step F — Drive mount করুন

```python
from google.colab import drive
drive.mount("/content/drive")
```
Popup-এ **Connect** click করুন (Google permission)।

## Step G — Smoke test cell চালান

1. `COLAB_SMOKE_TEST_CELL.py` file-টা **Notepad-এ open** করুন
2. **Ctrl+A** (সব select) → **Ctrl+C** (copy)
3. Colab-এ **নতুন cell** add করুন (+ Code)
4. **Ctrl+V** paste
5. **Shift+Enter** run

Cell নিজেই stage A→H পর্যন্ত সব check করবে। ~৫–১০ মিনিট লাগতে পারে।

## Step H — Result দেখুন

শেষে এইরকম দেখাবেন:
```
===== SMOKE TEST PASSED =====
peak VRAM bs2x256: x.xx GB
```
অথবা `FAILED` + error message।

**Report file location:** Google Drive → `MyDrive/NexusAI/audit_reports/` → `core01_smoke_<time>.json`

## Step I — Report পাঠান

Cell-এর সব output (বিশেষ করে শেষের `===== SMOKE TEST =====` অংশ + কোনো FAIL line)
এখানে paste করুন। আমি verify করে বলব full training-এর জন্য ready কিনা।

---

## জরুরি নিয়ম

- ❌ Full training cell চালাবেন না (আলাদা approval লাগবে)
- ❌ 100M dataset বানাবেন না এখন
- ❌ কোনো file delete করবেন না
- ✅ কোনো error এলে output paste করুন, আমি বলব
