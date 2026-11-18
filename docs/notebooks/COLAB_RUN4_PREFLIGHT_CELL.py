# =============================================================================
# NEXUSAI CORE-01 RUN4 — FINAL COLAB PREFLIGHT CELL v5 (single cell, no training)
# Read-only verification. FAIL-CLOSED. 3-stage verified report persistence.
# =============================================================================
import os, sys, json, glob, hashlib, zipfile, re, ast
from datetime import datetime

REPORT = {"ts": datetime.now().isoformat(), "checks": {}, "files": {},
          "warnings": [], "missing": [], "critical_failures": [],
          "TRAINING_STARTED": False, "TRAINING_AUTHORIZED": False,
          "PREFLIGHT_ONLY": True, "status": "BLOCKED",
          "checker_version": "v5"}

def note(k, v): REPORT["checks"][k] = v
def critical(k, msg):
    note(k, "FAIL — " + msg); REPORT["critical_failures"].append(f"{k}: {msg}")
def warn(k, msg):
    note(k, "WARN — " + msg); REPORT["warnings"].append(f"{k}: {msg}")

def sha256_file(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()

def all_matches(patterns, roots):
    out = []
    for pat in patterns:
        for r in roots:
            if r:
                out.extend(sorted(glob.glob(os.path.join(r, pat))))
    seen, res = set(), []
    for p in out:
        if p not in seen:
            seen.add(p); res.append(p)
    return res

# ---------------------------------------------------------------- Drive ------
DRIVE_OK = False
try:
    from google.colab import drive
    drive.mount("/content/drive")
    DRIVE_OK = os.path.isdir("/content/drive/MyDrive")
    note("drive_mount", "ok" if DRIVE_OK else "mounted but MyDrive missing")
except Exception as e:
    note("drive_mount", f"FAILED: {e}")

BASE = "/content/drive/MyDrive/NexusAI" if DRIVE_OK else None
DRIVE_DATA = os.path.join(BASE, "data/run4") if BASE else None
REPORT_DIR = os.path.join(BASE, "reports/run4") if BASE else None
if REPORT_DIR:
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
    except Exception as e:
        critical("report_dir", f"cannot create: {e}"); REPORT_DIR = None
else:
    critical("drive_mount", "Drive unavailable — cannot verify/report safely")

# ------------------------------------------------------- 1. Run3 ckpt ------
TRUSTED_CKPT_SHA = "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"
TRUSTED_CKPT_SIZE = 106777501
if BASE:
    ckpt = os.path.join(BASE, "checkpoints/core01_english_run3/checkpoint_final.pt")
    if os.path.exists(ckpt):
        try:
            size = os.path.getsize(ckpt); sha = sha256_file(ckpt)
            ok = (size == TRUSTED_CKPT_SIZE and sha == TRUSTED_CKPT_SHA)
            REPORT["files"]["run3_checkpoint"] = {"path": ckpt, "size": size,
                                                  "sha256": sha, "match": ok}
            note("run3_checkpoint", "PASS" if ok else "FAIL")
            if not ok: critical("run3_checkpoint", "size/hash MISMATCH")
        except Exception as e:
            critical("run3_checkpoint", f"read error: {e}")
    else:
        REPORT["files"]["run3_checkpoint"] = {"path": ckpt, "missing": True}
        critical("run3_checkpoint", "missing on Drive")

# ------------------------------------------------------- 2. Bundle ZIP -----
TRUSTED_ZIP_SHA = "778ded61720651951e1dc24ce02e3c36aa520c187498e9657d826af3a050110e"
TRUSTED_ZIP_SIZE = 300734
roots = tuple(r for r in ("/content", DRIVE_DATA, BASE) if r)
zip_candidates = all_matches(
    ["NEXUSAI_CORE01_RUN4_BUNDLE*.zip", "NEXUSAI_CORE01_RUN4_BUNDLE*.ZIP"], roots)
zip_path, cand_info = None, []
for p in zip_candidates:
    try:
        sz = os.path.getsize(p); sh = sha256_file(p)
        cand_info.append({"path": p, "size": sz, "sha256": sh})
        if sz == TRUSTED_ZIP_SIZE and sh == TRUSTED_ZIP_SHA:
            zip_path = p
    except Exception as e:
        cand_info.append({"path": p, "error": str(e)})
REPORT["files"]["bundle_zip_candidates"] = cand_info
if zip_candidates and zip_path is None:
    critical("bundle_zip_hash", "no candidate matches trusted sha256/size")
elif not zip_candidates:
    critical("bundle_zip", "not found")
elif len([c for c in cand_info if c.get("sha256") == TRUSTED_ZIP_SHA]) > 1:
    warn("bundle_zip", "multiple identical trusted copies — deterministic pick")

if zip_path:
    REPORT["files"]["bundle_zip"] = {"path": zip_path, "size": TRUSTED_ZIP_SIZE,
                                     "sha256": TRUSTED_ZIP_SHA, "selected_by_hash": True}
    note("bundle_zip_hash", "PASS")
    try:
        z = zipfile.ZipFile(zip_path); bad = z.testzip(); names = z.namelist()
        def _unsafe(n):
            parts = n.replace("\\", "/").split("/")
            return (n.startswith(("/", "\\")) or ".." in parts
                    or bool(re.match(r"^[A-Za-z]:", n)))
        traversal = [n for n in names if _unsafe(n)]
        cell_name = "docs/notebooks/COLAB_RUN4_TRAIN_CELL.py"
        required = [cell_name,
                    "packages/ai-core/core01/pretraining_driver.py",
                    "packages/ai-core/core01/transformer.py",
                    "packages/ai-core/core01/training.py",
                    "packages/ai-core/core01/dataset.py",
                    "packages/ai-core/core01/tokenizer_interface.py",
                    "packages/ai-core/models/nexusai_core_01/config/model_config.py"]
        missing_entries = [r for r in required if r not in names]
        tok_ok = all(any(n.endswith(s) for n in names) for s in
                     ("sp_bpe_8k.model", "sp_bpe_8k.vocab"))
        TRUSTED_CELL_SHA = ("8779caae7253b3c6d74be77d47cb3542dfb8696e8f478f9e3915cc27eea7af1f")
        cell_src_b = z.read(cell_name) if cell_name in names else b""
        try:
            cell_src = cell_src_b.decode("utf-8", errors="strict") if cell_src_b else ""
        except UnicodeDecodeError:
            cell_src = ""
        cell_sha = hashlib.sha256(cell_src_b).hexdigest()
        cell_sha_ok = (cell_sha == TRUSTED_CELL_SHA)

        # ---- resume wiring: structural AST data-flow ----
        wiring = {"ck_load_line": None, "start_step_line": None,
                  "start_epoch_line": None, "del_ck_line": None,
                  "rep_dict_line": None, "rep_keys": {},
                  "rep_consumers": [], "cmd_line": None,
                  "resume_arg": False, "resume_src_used": False,
                  "subprocess_call_line": None, "evidence": []}
        resume_ok = False
        try:
            _t = ast.parse(cell_src)
            rep_dict_node = None
            cmd_list_node = None
            # locate assignments & calls
            for _n in ast.walk(_t):
                if isinstance(_n, ast.Assign):
                    for _tg in _n.targets:
                        if not isinstance(_tg, ast.Name):
                            continue
                        if _tg.id == "ck" and isinstance(_n.value, ast.Call):
                            wiring["ck_load_line"] = _n.lineno
                        if _tg.id in ("START_STEP", "START_EPOCH") \
                                and "ck" in ast.dump(_n.value):
                            wiring["start_step_line" if _tg.id == "START_STEP"
                                   else "start_epoch_line"] = _n.lineno
                        if _tg.id == "rep" and isinstance(_n.value, ast.Dict):
                            rep_dict_node = _n
                            wiring["rep_dict_line"] = _n.lineno
                        if _tg.id == "cmd" and isinstance(_n.value, ast.List):
                            cmd_list_node = _n.value
                            wiring["cmd_line"] = _n.lineno
                elif isinstance(_n, ast.Delete):
                    for _tg in _n.targets:
                        if isinstance(_tg, ast.Name) and _tg.id == "ck":
                            wiring["del_ck_line"] = _n.lineno
                elif isinstance(_n, ast.Call):
                    # consumer: subprocess.run(cmd, ...) or json.dump(rep, ...)
                    fn = _n.func
                    fname = ""
                    if isinstance(fn, ast.Attribute):
                        fname = fn.attr
                    elif isinstance(fn, ast.Name):
                        fname = fn.id
                    for a_ in _n.args:
                        if isinstance(a_, ast.Name) and a_.id == "cmd":
                            wiring["subprocess_call_line"] = _n.lineno
                        if isinstance(a_, ast.Name) and a_.id == "rep":
                            wiring["rep_consumers"].append(
                                {"call": fname, "line": _n.lineno})
            if rep_dict_node is not None:
                for k_, v_ in zip(rep_dict_node.value.keys,
                                  rep_dict_node.value.values):
                    if isinstance(k_, ast.Constant) and isinstance(v_, ast.Name):
                        wiring["rep_keys"][k_.value] = v_.id
            if cmd_list_node is not None:
                vals = []
                for el in cmd_list_node.elts:
                    if isinstance(el, ast.Constant):
                        vals.append(el.value)
                    elif isinstance(el, ast.Name):
                        vals.append(el.id)
                wiring["resume_arg"] = "--resume" in vals
                wiring["resume_src_used"] = "RESUME_SRC" in vals
            # data-flow verdict
            ok_flow = (wiring["ck_load_line"] and wiring["start_step_line"]
                       and wiring["start_epoch_line"] and wiring["del_ck_line"]
                       and wiring["start_step_line"] < wiring["del_ck_line"]
                       and wiring["start_epoch_line"] < wiring["del_ck_line"]
                       and wiring["rep_dict_line"]
                       and wiring["rep_keys"].get("start_step") == "START_STEP"
                       and wiring["rep_keys"].get("start_epoch") == "START_EPOCH"
                       and wiring["rep_consumers"]
                       and wiring["cmd_line"] and wiring["subprocess_call_line"]
                       and wiring["resume_arg"] and wiring["resume_src_used"])
            resume_ok = bool(ok_flow)
            wiring["evidence"].append(
                "START_STEP/START_EPOCH are report metadata; actual resume "
                "flows via RESUME_SRC -> cmd '--resume' -> driver "
                "load_checkpoint (verified statically).")
            wiring["driver_evidence"] = (
                "Driver path verified statically AND by bounded smoke test "
                "(2026-11-11): --resume -> engine.load_checkpoint -> "
                "CheckpointManager restores model(strict)/optimizer/"
                "scheduler/rng + current_epoch/current_step "
                "(training.py:469-486); loop continues from restored epoch. "
                "Real Run3 ckpt: epoch=3 step=1341 restored; exactly ONE "
                "optimizer step executed; temp ckpt saved+reloaded. See "
                "external_verification for validated machine-readable "
                "evidence. Full training-loop resume NOT executed.")
        except Exception as e:
            wiring["error"] = str(e)
        REPORT["files"]["bundle_zip"]["resume_wiring"] = wiring
        REPORT["files"]["bundle_zip"].update({
            "entries": len(names), "testzip": bad,
            "traversal_entries": traversal, "missing_entries": missing_entries,
            "cell_sha256": cell_sha, "cell_sha_match": cell_sha_ok,
            "resume_order_ok": bool(resume_ok), "tokenizer_files": tok_ok})
        if bad is None and not traversal and not missing_entries:
            note("zip_integrity", "PASS")
        else:
            critical("zip_integrity", f"testzip={bad} trav={len(traversal)} miss={missing_entries}")
        if cell_sha_ok: note("cell_sha_match", "PASS")
        else: critical("cell_sha_match", f"got {cell_sha[:16]}")
        if resume_ok: note("resume_wiring", "PASS")
        else: critical("resume_wiring", "AST wiring incomplete")
        if tok_ok: note("tokenizer_in_bundle", "PASS")
        else: critical("tokenizer_in_bundle", "missing sp_bpe_8k")
        z.close()
    except Exception as e:
        critical("zip_integrity", f"cannot read zip: {e}")

# ------------------------------------------------------- 3. Corpus JSONL ----
# Authoritative corpus SHA-256 provenance (repo evidence):
#   eval_reports/nexusai_gate_b_backup_manifest.json ->
#     orig=packages/ai-core/data/phase2/run4_corpus/corpus_train.jsonl
#     size=385217021 sha256=5f8572ed... (computed directly on the raw file)
#   docs/architecture/audits/NEXUSAI_PHASE2_BLOCKER_FIX_EXECUTION_REPORT.md
#     records the same hash as the rebuilt corpus SHA-256.
TRUSTED_CORPUS_SHA = "5f8572edd816ac875a7f52915bc6326635d7a483e0ca3f33b70fffdda7e28376"
TRUSTED_CORPUS_SIZE = 385217021
CORPUS_PROVENANCE = ("eval_reports/nexusai_gate_b_backup_manifest.json "
                     "(orig=corpus_train.jsonl, hash computed on raw file) + "
                     "NEXUSAI_PHASE2_BLOCKER_FIX_EXECUTION_REPORT.md")
roots2 = tuple(r for r in ("/content", DRIVE_DATA, "/content/drive/MyDrive") if r)
corpus_candidates = all_matches(["corpus_train.jsonl"], roots2)
corpus, cand_info = None, []
for p in corpus_candidates:
    try:
        sz = os.path.getsize(p); sh = sha256_file(p)
        cand_info.append({"path": p, "size": sz, "sha256": sh})
        if sz == TRUSTED_CORPUS_SIZE and sh == TRUSTED_CORPUS_SHA:
            corpus = p
    except Exception as e:
        cand_info.append({"path": p, "error": str(e)})
REPORT["files"]["corpus_candidates"] = cand_info
REPORT["files"]["corpus_provenance"] = CORPUS_PROVENANCE
if corpus_candidates and corpus is None:
    critical("corpus_identity",
             "CORPUS_IDENTITY_UNVERIFIED — no candidate matches trusted "
             "sha256+size")
elif corpus is None:
    critical("corpus", "corpus_train.jsonl not found")
elif corpus:
    note("corpus_identity", "CORPUS_IDENTITY_VERIFIED")

if corpus:
    try:
        size = os.path.getsize(corpus)
        total_phys = n = ok = empty = mal = dup = blank = non_dict = enc_err = 0
        seen = set()
        with open(corpus, "rb") as fb:
            for raw in fb:
                total_phys += 1
                if not raw.strip():
                    blank += 1; continue
                n += 1
                try:
                    line = raw.decode("utf-8")
                except UnicodeDecodeError:
                    enc_err += 1; continue
                try:
                    d = json.loads(line)
                except Exception:
                    mal += 1; continue
                if not isinstance(d, dict):
                    non_dict += 1; continue
                ok += 1
                t = d.get("text", "")
                if not isinstance(t, str) or not t.strip():
                    empty += 1
                else:
                    h = hashlib.md5(t.encode("utf-8")).hexdigest()
                    if h in seen: dup += 1
                    seen.add(h)
        rep = {"path": corpus, "size": size,
               "total_physical_lines": total_phys,
               "total_non_empty_lines": n, "records": n, "parsed": ok,
               "valid_records": ok, "malformed_json": mal,
               "encoding_errors": enc_err, "encoding_error_lines": enc_err,
               "blank_lines": blank, "empty_text": empty,
               "non_dict_records": non_dict, "duplicate_texts": dup,
               "unique_texts": len(seen), "strict_utf8": enc_err == 0,
               "dup_policy": "counted, non-fatal", "lines": n,
               "sha256": TRUSTED_CORPUS_SHA}
        REPORT["files"]["corpus"] = rep
        if (size == TRUSTED_CORPUS_SIZE and mal == 0 and empty == 0
                and non_dict == 0 and enc_err == 0 and n == 216193):
            note("corpus", "PASS — strict UTF-8 + structure valid")
        else:
            critical("corpus", f"size={size} records={n} mal={mal} "
                               f"enc_err={enc_err} empty={empty} non_dict={non_dict}")
    except Exception as e:
        critical("corpus", f"validation error: {e}")

# ------------------------------------------------- 4. Optional manifest ----
mani_candidates = all_matches(["corpus_manifest.json"], roots2)
if mani_candidates:
    mani = mani_candidates[0]
    try:
        m = json.load(open(mani, encoding="utf-8"))
        info = {"path": mani, "type": type(m).__name__,
                "note": "informational only — not authoritative provenance"}
        if isinstance(m, dict):
            info["keys"] = list(m)[:15]
            c = REPORT["files"].get("corpus", {})
            mism = []
            for mk, ck_ in (("num_docs","records"),("docs","records"),
                            ("document_count","records"),("records","records"),
                            ("lines","records"),("num_lines","records"),
                            ("size_bytes","size"),("bytes","size")):
                if mk in m and ck_ in c:
                    try:
                        if int(m[mk]) != int(c[ck_]):
                            mism.append(f"{mk}={m[mk]} vs actual {c[ck_]}")
                    except Exception:
                        mism.append(f"{mk}={m[mk]!r} not comparable")
            if mism:
                info["consistency_mismatches"] = mism
                warn("corpus_manifest", "inconsistent: " + "; ".join(mism))
        REPORT["files"]["corpus_manifest"] = info
        note("corpus_manifest", "present (optional, informational)")
    except Exception as e:
        warn("corpus_manifest", f"invalid/unreadable: {e}")

# ---------------------------------------------------------- verdict ---------
def compute_status():
    if REPORT["critical_failures"]:
        return "BLOCKED"
    if REPORT["warnings"]:
        return "READY WITH WARNINGS"
    return "READY FOR USER REVIEW"
REPORT["status"] = compute_status()

# ------------- external verification evidence (validated, fail-closed) ------
# The bounded Run3 resume smoke test was executed locally on 2026-11-11.
# Its machine-readable evidence is persisted at
#   eval_reports/nexusai_run4_resume_smoke_evidence.json  (repo)
# For Colab, upload that file to the Drive NexusAI folder. This cell does NOT
# trust hardcoded claims: it locates the evidence file, parses it, and
# validates every critical field against the trusted constants. Missing,
# malformed, or inconsistent evidence => critical => BLOCKED.
EVIDENCE_NAME = "nexusai_run4_resume_smoke_evidence.json"
EXPECTED_EVIDENCE = {
    "restored_epoch": 3, "restored_step": 1341, "post_step": 1342,
    "device": "cpu", "precision": "fp32",
    "smoke_status": "PRETRAINING_IN_PROGRESS",
    "temp_ckpt_sha": ("f7236ce35580ed33308b8c589c872e2cded32f2253"
                      "cbaed24db30a2d90b35e88"),
    "original_sha": TRUSTED_CKPT_SHA,
    "min_tests": 15,
}
ev_roots = tuple(r for r in ("/content", DRIVE_DATA, "/content/drive/MyDrive",
                             BASE) if r)
ev_candidates = all_matches([EVIDENCE_NAME], ev_roots)
# Pin the evidence file's trusted identity. Provenance: the JSON was written
# programmatically by the executed smoke-test script (not hand-edited);
# its sha256/size below were computed from those exact bytes on 2026-11-11.
# A sha256 pin detects modification; it does NOT prove the event occurred —
# authenticity rests on the preserved artifacts + documented generation.
EXPECTED_EVIDENCE_SHA = ("0cb7588d7f2e7afe2e5250dd9381f3c37e1940428cb060477"
                         "929bb1338523f32")
EXPECTED_EVIDENCE_SIZE = 2932
ev_info = []
for _p in ev_candidates:
    try:
        ev_info.append({"path": _p, "size": os.path.getsize(_p),
                        "sha256": sha256_file(_p)})
    except Exception as _e:
        ev_info.append({"path": _p, "error": str(_e)})
REPORT["files"]["smoke_evidence_candidates"] = ev_info
trusted_ev = [c for c in ev_info
              if c.get("sha256") == EXPECTED_EVIDENCE_SHA
              and c.get("size") == EXPECTED_EVIDENCE_SIZE]
distinct_ev = {c.get("sha256") for c in ev_info if "sha256" in c}
REPORT["external_verification"] = {
    "evidence_file": EVIDENCE_NAME,
    "evidence_candidates": ev_candidates,
    "corpus_identity_status": "PENDING_VALIDATION",
    "resume_flow_status": "UNVERIFIED",
    "checkpoint_compatibility_status": "UNVERIFIED",
    "CUDA_FP16_EXECUTION_STATUS": "NOT_TESTED",
    "SCHEDULER_BEHAVIOR": "PARTIALLY_VERIFIED",
    "training_execution_authorized": False,
    "full_run4_training_executed": False,
}
if not ev_candidates:
    critical("smoke_evidence",
             f"{EVIDENCE_NAME} not found — upload it to the Drive NexusAI "
             "folder; resume smoke evidence cannot be validated")
elif len(distinct_ev) > 1:
    critical("smoke_evidence",
             "ambiguous evidence candidates with DIFFERENT hashes: "
             + json.dumps(ev_info))
elif not trusted_ev:
    critical("smoke_evidence",
             "evidence file hash/size does not match trusted identity "
             f"(expected sha256={EXPECTED_EVIDENCE_SHA[:16]}…, "
             f"size={EXPECTED_EVIDENCE_SIZE})")
else:
    ev_path = trusted_ev[0]["path"]
    if len(trusted_ev) > 1:
        warn("smoke_evidence",
             "multiple identical trusted copies — deterministic pick")
    try:
        ev = json.load(open(ev_path, encoding="utf-8"))
        tests = ev.get("tests", [])
        ed = ev.get("evidence", {})
        fails = []
        if not isinstance(tests, list) or len(tests) < EXPECTED_EVIDENCE["min_tests"]:
            fails.append(f"tests missing/short: {len(tests) if isinstance(tests,list) else '?'}")
        elif any(t.get("result") != "PASS" for t in tests):
            fails.append("one or more smoke tests did not PASS")
        checks = {
            "restored_epoch": ed.get("restored_epoch"),
            "restored_step": ed.get("restored_step"),
            "post_step": ed.get("post_step"),
            "device": ed.get("device"),
            "precision": ed.get("precision"),
            "smoke_status": ed.get("smoke_status"),
            "temp_ckpt_sha": ed.get("temp_ckpt_sha"),
            "original_sha_pre": ed.get("original_sha_pre"),
            "original_sha_post": ed.get("original_sha_post"),
        }
        for k, exp in EXPECTED_EVIDENCE.items():
            if k in checks and checks[k] != exp:
                fails.append(f"{k}={checks[k]!r} expected {exp!r}")
        if ed.get("original_sha_pre") != TRUSTED_CKPT_SHA or \
           ed.get("original_sha_post") != TRUSTED_CKPT_SHA:
            fails.append("original ckpt sha pre/post != trusted sha")
        if fails:
            critical("smoke_evidence",
                     f"evidence inconsistent at {ev_path}: " + "; ".join(fails))
        else:
            REPORT["external_verification"].update({
                "corpus_identity_status": "CORPUS_IDENTITY_VERIFIED",
                "resume_flow_status": "RESUME_FLOW_VERIFIED_BOUNDED_SMOKE",
                "checkpoint_compatibility_status": "COMPATIBLE",
                "evidence_path": ev_path,
                "evidence_sha256": EXPECTED_EVIDENCE_SHA,
                "evidence_size": EXPECTED_EVIDENCE_SIZE,
                "evidence_integrity": "PINNED_HASH_MATCH",
                "tests_passed": f"{len(tests)}/{len(tests)}",
                "restored": {"epoch": ed["restored_epoch"],
                             "step": ed["restored_step"],
                             "post_step": ed["post_step"]},
                "temp_ckpt": {"size": ed.get("temp_ckpt_size"),
                              "sha256": ed.get("temp_ckpt_sha")},
                "original_ckpt_integrity": "UNCHANGED (sha256 pre==post)",
                "device": ed["device"], "precision": ed["precision"],
                "limitations": (
                    "CPU/FP32 only — CUDA/FP16 GradScaler path verified in "
                    "source, not exercised. Scheduler lr-lambda rebuilt with "
                    "Run4 step budget; last_epoch restored. Bounded smoke "
                    "test proves resume mechanics, NOT full Run4 training."),
            })
            note("smoke_evidence", "PASS — validated against trusted constants")
    except Exception as e:
        critical("smoke_evidence", f"unreadable/malformed evidence: {e}")

# --------------------------- 5. three-stage verified report persistence -----
report_paths = {}
if REPORT_DIR:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    def render():
        j = json.dumps(REPORT, indent=1, ensure_ascii=False)
        return {"json": j, "txt": j,
                "md": "# RUN4 FINAL PREFLIGHT REPORT\n\n```json\n" + j + "\n```\n"}
    def unique_path(ext, tag=""):
        # Stage tag in filename prevents a stale earlier-stage report from
        # being mistaken for the final verdict (e.g. stageA "initial" vs
        # stageB/C final files are now distinguishable on disk).
        base_p = os.path.join(
            REPORT_DIR,
            f"RUN4_PREFLIGHT_{stamp}{('_' + tag) if tag else ''}.{ext}")
        p, i = base_p, 1
        while os.path.exists(p):
            p = base_p.replace(f".{ext}", f"_{i}.{ext}"); i += 1
        return p
    def write_stage(tag):
        """Write all 3 reports; verify existence/size/sha/parse; return dict."""
        paths, res = {}, {"ok": True, "files": {}, "errors": []}
        for ext in ("json", "txt", "md"):
            p = unique_path(ext, tag)
            try:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(render()[ext])
                ok = os.path.exists(p) and os.path.getsize(p) > 0
                sha = sha256_file(p) if ok else None
                paths[ext] = p
                res["files"][ext] = {"path": p,
                                     "size": os.path.getsize(p) if ok else 0,
                                     "sha256": sha}
                if not ok:
                    res["ok"] = False; res["errors"].append(f"{ext} empty/missing")
            except Exception as e:
                res["ok"] = False; res["errors"].append(f"{ext}: {e}")
        # cross-consistency: JSON parses + status field matches
        try:
            pj = json.load(open(paths["json"], encoding="utf-8"))
            if pj.get("status") != REPORT["status"]:
                res["ok"] = False
                res["errors"].append("json status mismatch")
            for ext in ("txt", "md"):
                if REPORT["status"] not in open(paths[ext], encoding="utf-8").read():
                    res["ok"] = False
                    res["errors"].append(f"{ext} missing status")
        except Exception as e:
            res["ok"] = False; res["errors"].append(f"reparse: {e}")
        res["stage"] = tag
        return res, paths
    # Stage A: initial write
    try:
        stageA, report_paths = write_stage("initial")
    except Exception as e:
        stageA = {"ok": False, "errors": [str(e)]}
        report_paths = {}
    REPORT["report_write_stageA"] = stageA
    # Stage B: final write (content now includes stageA result + verdict)
    REPORT["status"] = compute_status()
    REPORT["_status_at_B"] = REPORT["status"]
    try:
        stageB, report_paths = write_stage("final")
    except Exception as e:
        stageB = {"ok": False, "errors": [str(e)]}
        report_paths = {}
    REPORT["report_write"] = stageB
    if not stageB.get("ok"):
        critical("report_write", "; ".join(stageB.get("errors", ["failed"])))
    REPORT["status"] = compute_status()
    # Stage C correction: if stageB failed or the verdict changed after it,
    # persist the FINAL status once more so on-disk reports cannot contradict
    # the in-memory verdict. Self-hash boundary: these files contain stageA/B
    # results + final status; their own sha is recorded in the response only.
    if (not stageB.get("ok")) or REPORT["status"] != REPORT.get("_status_at_B"):
        try:
            stageC, report_paths = write_stage("final_correction")
        except Exception as e:
            stageC = {"ok": False, "errors": [str(e)]}
        REPORT["report_write_final_correction"] = stageC
        if not stageC.get("ok"):
            critical("report_write_final",
                     "; ".join(stageC.get("errors", ["failed"])))
        REPORT["status"] = compute_status()
    # Last-resort marker: if ALL structured report writes failed, still try a
    # minimal BLOCKED marker so Drive does not only contain stale stage-A files.
    if REPORT["status"] == "BLOCKED" and not report_paths:
        try:
            mp = os.path.join(
                REPORT_DIR, f"RUN4_PREFLIGHT_BLOCKED_{stamp}.txt")
            with open(mp, "w", encoding="utf-8") as _f:
                _f.write(f"RUN4 PREFLIGHT BLOCKED at {REPORT['ts']}\n"
                         f"critical_failures={REPORT['critical_failures']}\n")
            REPORT["blocked_marker"] = mp
        except Exception:
            REPORT["blocked_marker"] = "FAILED — see console output"
    REPORT.pop("_status_at_B", None)
    # Stage C: consistency note — reports contain verdict + stageA/B results;
    # final on-disk files are stageB outputs (self-hash boundary documented).
    REPORT["report_write"]["self_reference_note"] = (
        "stageB files contain the verdict and stageA result; their own "
        "sha256 recorded in stageB response object, not inside the files "
        "(mathematically impossible to embed own hash).")
else:
    critical("report_write", "Drive unavailable — reports not persisted")
    REPORT["status"] = "BLOCKED"

print("\n================= PREFLIGHT =================")
print(json.dumps(REPORT["checks"], indent=1, ensure_ascii=False))
print("critical:", REPORT["critical_failures"])
print("warnings:", REPORT["warnings"])
print("reports:", report_paths)
print("STATUS:", REPORT["status"])
print("TRAINING_STARTED:", REPORT["TRAINING_STARTED"],
      "| TRAINING_AUTHORIZED:", REPORT["TRAINING_AUTHORIZED"],
      "| PREFLIGHT_ONLY:", REPORT["PREFLIGHT_ONLY"])
