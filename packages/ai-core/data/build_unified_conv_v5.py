"""Build unified trilingual conversational SFT dataset v5 (Core-05 foundation).

v5 = curated v4 carryover (math capped <=25%) + large procedural+authored
expansion targeting V5 spec: bn35/en30/banglish20/mixed10 language balance,
300+ multi-turn (6/8/10/12-turn depths), 150+ reasoning, 150+ decision,
dedicated uncertainty/clarification/self-correction, math diversity caps.

All content is human-authored or project-procedural. NO external AI.
Output: data/unified_conversational/v5/
"""
import json, os, random, hashlib, re
from collections import Counter, defaultdict

SEED = 42
random.seed(SEED)
BASE = os.path.join(os.path.dirname(__file__), "unified_conversational")
OUT = os.path.join(BASE, "v5")
V4 = os.path.join(BASE, "v4")

recs, QUAR = [], []
BN = re.compile(r'[ঀ-৿]')
BG = re.compile(r'\b(ki|koto|ache|nei|bolun|dao|kivabe|keno|korbo|lagbe|bhalo|khub|bhai|vai|hocche|gechi|chai|kore|toiri|bolchi|dekhchi|jacchi|ashchi|parbo|dorkar|sahajjo|korchi|jaccho|achchi|dekhbo|sikhbo|porbo)\b', re.I)

def h(s): return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)
def detect(u):
    if BN.search(u): return "bn"
    if BG.search(u): return "banglish"
    if re.search(r'[a-zA-Z]', u): return "en"
    return "bn"

def add(cat, lang, messages, group, caps=None, source="authored", family=None):
    rid = f"v5:{cat}:{lang}:{len(recs)}"
    recs.append({"sample_id": rid, "id": rid, "lang": lang,
        "category": cat, "task": cat, "capabilities": caps or [],
        "suitable_cores": sorted({"core05","core01","core02","core03","core04"} &
            set(c for c in (caps or []) if c.startswith("core")) or ["core05"]),
        "scenario_family": family, "conversation_depth": len(messages)//2,
        "difficulty": "medium", "conversation_id": group,
        "messages": [{"role": r, "content": c} for r, c in messages],
        "split_group": group,
        "provenance": {"builder": "build_unified_conv_v5.py", "seed": SEED,
                       "source": source, "authorship":
                       "human_authored" if source=="authored" else "procedural"},
        "quality": {"status": "approved", "review_method": "rule_based",
                    "human_reviewed": False}})

def qa(cat, lang, u, a, caps=None, source="authored", family=None):
    add(cat, lang, [("user",u),("assistant",a)], f"g{h(u+a)%900000}", caps, source, family)

# ================= 1. V4 CARRYOVER (curated) =================
# Keep all v4 non-math/logic; cap math+logic so total math <= ~22% of corpus.
MATH_CAP = 550
v4_math, v4_other = [], []
for split in ("train","validation","test"):
    for line in open(os.path.join(V4,f"{split}.jsonl"),encoding="utf-8"):
        r=json.loads(line)
        r["split_group"]=r.get("split_group") or f"v4{h(r['sample_id'])%90000}"
        r.setdefault("capabilities",[])
        r.setdefault("suitable_cores",["core05"])
        r.setdefault("conversation_depth",len(r["messages"])//2)
        r.setdefault("scenario_family",None)
        r["provenance"]={**r.get("provenance",{}),"source":"v4_carryover"}
        (v4_math if r["category"] in ("math","logic") else v4_other).append(r)
v4_math.sort(key=lambda r: h(r["sample_id"]))
kept_math=v4_math[:MATH_CAP]
for r in v4_other+kept_math: recs.append(r)
print(f"v4 carryover: {len(v4_other)} non-math + {len(kept_math)}/{len(v4_math)} math")

S=[]
def seed(cat,lang,u,a,caps=None,family=None): S.append((cat,lang,u,a,caps,family))
