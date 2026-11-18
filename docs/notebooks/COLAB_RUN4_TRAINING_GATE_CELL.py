# =============================================================================
# NEXUSAI CORE-01 RUN4 — TRAINING AUTHORIZATION GATE CELL (v1.0)
# Runs AFTER preflight. Writes an authorization marker ONLY if the user types
# the exact phrase. The training cell refuses to run without this marker.
# This cell itself NEVER starts training.
# =============================================================================
import os, json, glob
from datetime import datetime, timezone

REQUIRED_PHRASE = "START NEXUSAI CORE-01 TRAINING"
REPORTS = "/content/drive/MyDrive/NexusAI/reports/run4"
AUTH_FILE = os.path.join(REPORTS, "TRAINING_AUTHORIZATION.json")

print("[GATE_VERSION] RUN4_TRAINING_GATE_V1_0")

if not os.path.isdir(REPORTS):
    print("[BLOCKED] reports/run4 not found — run upload + preflight cells first.")
    raise SystemExit(1)

# latest preflight report must exist and not be BLOCKED
reports = sorted(glob.glob(os.path.join(REPORTS, "RUN4_PREFLIGHT_*.json")))
if not reports:
    print("[BLOCKED] no preflight report found — run Cell 14 (preflight) first.")
    raise SystemExit(1)
latest = reports[-1]
try:
    rep = json.load(open(latest, encoding="utf-8"))
except Exception as e:
    print(f"[BLOCKED] cannot parse preflight report {latest}: {e}")
    raise SystemExit(1)
status = rep.get("status", "UNKNOWN")
print(f"preflight report: {os.path.basename(latest)}")
print(f"preflight status : {status}")
print(f"training flags   : started={rep.get('TRAINING_STARTED')} "
      f"authorized={rep.get('TRAINING_AUTHORIZED')}")
if "BLOCKED" in str(status).upper():
    print("[BLOCKED] preflight status is BLOCKED — fix failures before authorizing.")
    raise SystemExit(1)

phrase = input("Type EXACTLY: START NEXUSAI CORE-01 TRAINING\n> ")
if phrase.strip() != REQUIRED_PHRASE:
    print("[REJECTED] phrase did not match exactly. No authorization written.")
    raise SystemExit(1)

auth = {
    "authorized": True,
    "phrase": REQUIRED_PHRASE,
    "authorized_utc": datetime.now(timezone.utc).isoformat(),
    "preflight_report": os.path.basename(latest),
    "preflight_status": status,
    "note": "Authorizes ONE Run4 training execution via COLAB_RUN4_TRAIN_CELL.py",
}
os.makedirs(REPORTS, exist_ok=True)
tmp = AUTH_FILE + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(auth, f, indent=1)
os.replace(tmp, AUTH_FILE)
print("[AUTHORIZED] marker written:", AUTH_FILE)
print("Next: run the Run4 training cell MANUALLY. This gate does not start it.")
