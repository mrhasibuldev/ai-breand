"""
NexusAI Core-01 — English Corpus Preparation Script (Phase 6.1)

Prepares a bounded English pretraining corpus from a LOCAL Parquet file
(e.g. a FineWeb sample-10BT shard) for NexusAI Core-01.

Hard guarantees:
  - NEVER downloads anything. Local file paths only; missing file -> error.
  - NEVER uses GPU.
  - Token counts use the REAL Core-01 SentencePiece tokenizer
    (sp_bpe_8k, vocab 8,000) via NexusAITokenizer — not GPT-2 estimates.
  - Document-level train/validation split BEFORE packing (no leakage).
  - Exact deduplication via SHA-256 over normalized text.
  - Provenance manifest with real hashes only (no fabricated values).
  - Resume-safe at row-group boundaries with fingerprint validation.

Output (in --output-dir):
  english_train.jsonl   {"text": ..., "ntok": ...}   (driver-compatible)
  english_val.jsonl     {"text": ..., "ntok": ...}
  accepted_spool.jsonl  intermediate accepted docs (kept for audit/resume)
  dedup_hashes.txt      SHA-256 hashes of accepted normalized texts
  prep_state.json       resume state (row-group boundaries + fingerprints)
  manifest.json         provenance + statistics
  preparation_report.md human-readable summary
  deduplication_report.json dedup statistics

Driver compatibility: pretraining_driver.load_texts() accepts .jsonl with
a "text" field, so outputs feed directly into PackedTextDataset via:
  python -m core01.pretraining_driver --train-file english_train.jsonl ...
"""

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import unicodedata
from typing import Optional

SCRIPT_VERSION = "6.1.0"

# ---------------------------------------------------------------------------
# Path setup so core01 imports work both from repo and from the Kaggle package
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_AI_CORE = os.path.dirname(_HERE)                      # packages/ai-core
_MODELS = os.path.join(_AI_CORE, "models")
# Kaggle package layout: <pkg>/core01/..., <pkg>/models/..., <pkg>/data/...
_PKG_ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "data" else None
for _p in (_AI_CORE, _MODELS):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import pyarrow.parquet as pq
except ImportError:
    pq = None

# Load NexusAITokenizer WITHOUT importing the core01 package __init__ (which
# pulls in torch). tokenizer_interface.py only needs sentencepiece + the
# model config, so corpus prep can run torch-free on CPU.
import importlib.util as _ilu

def _load_tokenizer_interface():
    candidates = [
        os.path.join(_AI_CORE, "core01", "tokenizer_interface.py"),
        # Kaggle package layout: <pkg>/core01/tokenizer_interface.py
        os.path.join(os.environ.get("NEXUSAI_PACKAGE_ROOT", ""),
                     "core01", "tokenizer_interface.py"),
    ]
    path = next((c for c in candidates if c and os.path.isfile(c)), None)
    if path is None:
        raise ImportError("tokenizer_interface.py not found")
    spec = _ilu.spec_from_file_location("nexusai_tok_iface", path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_tok_mod = _load_tokenizer_interface()
NexusAITokenizer = _tok_mod.NexusAITokenizer

# Model config is stdlib-only (dataclasses/enum) — import normally.
try:
    from nexusai_core_01.config.model_config import NexusAICore01Config
except ImportError:
    _pkg = os.environ.get("NEXUSAI_PACKAGE_ROOT", "")
    if _pkg and os.path.join(_pkg, "models") not in sys.path:
        sys.path.insert(0, os.path.join(_pkg, "models"))
    from nexusai_core_01.config.model_config import NexusAICore01Config


# ---------------------------------------------------------------------------
# Cleaning
# ---------------------------------------------------------------------------
_WS_RUN = re.compile(r"[ \t]+")
_NL_RUN = re.compile(r"\n{3,}")
_TAG = re.compile(r"<[^>]{1,200}>")
_HEX_GARBAGE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffd]")


def clean_text(text: str) -> Optional[str]:
    """Conservative deterministic cleaning. Returns None to reject."""
    if not isinstance(text, str):
        return None
    t = unicodedata.normalize("NFC", text)
    if not t.strip():
        return None
    # strip residual HTML-ish tags (conservative: only well-formed short tags)
    t = _TAG.sub(" ", t)
    # remove control chars / replacement chars
    t = _HEX_GARBAGE.sub("", t)
    if not t.strip():
        return None
    # whitespace normalization: collapse spaces/tabs, cap blank-line runs
    t = _WS_RUN.sub(" ", t)
    t = _NL_RUN.sub("\n\n", t)
    t = t.strip()
    if not t:
        return None
    return t


def quality_reject(text: str, min_chars: int, max_chars: int) -> Optional[str]:
    """Return rejection reason or None."""
    n = len(text)
    if n < min_chars:
        return "too_short"
    if n > max_chars:
        return "too_long"
    # spam heuristics (documented limitations: heuristic, not linguistic)
    sample = text[:5000]
    letters = sum(c.isalpha() for c in sample)
    if letters / max(1, len(sample)) < 0.55:      # mostly non-letters -> junk
        return "low_letter_ratio"
    if "lorem ipsum" in sample.lower():
        return "lorem_ipsum"
    return None


# ---------------------------------------------------------------------------
# Fingerprinting / provenance helpers
# ---------------------------------------------------------------------------
def sha256_file(path: str, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def config_fingerprint(args, tok_sha: str, src_sha: str) -> str:
    payload = {
        "version": SCRIPT_VERSION,
        "target_tokens": args.target_tokens,
        "buffer_fraction": args.buffer_fraction,
        "val_fraction": args.val_fraction,
        "seed": args.seed,
        "min_chars": args.min_chars,
        "max_chars": args.max_chars,
        "english_filter": args.english_filter,
        "source_sha256": src_sha,
        "tokenizer_sha256": tok_sha,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------
def iter_parquet_texts(parquet_path: str, columns=("text",),
                       skip_row_groups=None):
    """Yield (row_group_index, doc_index_in_group, text) incrementally.
    Row groups in skip_row_groups are skipped WITHOUT being read."""
    pf = pq.ParquetFile(parquet_path)
    avail = set(pf.schema_arrow.names)
    use_cols = [c for c in columns if c in avail]
    if "text" not in use_cols:
        raise ValueError(f"Parquet file has no 'text' column. Columns: {sorted(avail)}")
    skip = skip_row_groups or set()
    for rg in range(pf.metadata.num_row_groups):
        if rg in skip:
            continue
        table = pf.read_row_group(rg, columns=use_cols)
        col = table.column("text").to_pylist()
        for i, val in enumerate(col):
            yield rg, i, val


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="NexusAI Core-01 English corpus preparation (local Parquet only)."
    )
    ap.add_argument("--input-parquet", required=True,
                    help="Local .parquet file (e.g. FineWeb shard). NO download performed.")
    ap.add_argument("--tokenizer", required=True,
                    help="Path to sp_bpe_8k.model")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--target-tokens", type=int, default=100_000_000)
    ap.add_argument("--buffer-fraction", type=float, default=0.005,
                    help="Accept up to target*(1+buffer); default 0.5%%")
    ap.add_argument("--val-fraction", type=float, default=0.015)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--min-chars", type=int, default=200)
    ap.add_argument("--max-chars", type=int, default=200_000)
    ap.add_argument("--english-filter", default="heuristic",
                    choices=["heuristic", "off"],
                    help="heuristic=light quality gates; off=accept all non-empty")
    ap.add_argument("--max-docs", type=int, default=0,
                    help="Stop after N source docs (testing/dry-run aid; 0=unlimited)")
    ap.add_argument("--max-row-groups", type=int, default=0,
                    help="Process at most N row groups (0=all)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Process a small sample; write NOTHING to output-dir")
    ap.add_argument("--overwrite", action="store_true",
                    help="Allow overwriting an existing prepared output dir")
    ap.add_argument("--resume", action="store_true",
                    help="Resume from prep_state.json in output-dir")
    ap.add_argument("--source-name", default="fineweb",
                    help="Provenance label for manifest")
    ap.add_argument("--source-config", default="sample-10BT",
                    help="Provenance label for manifest (e.g. sample-10BT)")
    ap.add_argument("--source-license", default="ODC-By-1.0",
                    help="Provenance license string for manifest")
    args = ap.parse_args(argv)

    t0 = time.time()

    # ---------- preflight ----------
    if pq is None:
        print("ERROR: pyarrow is required. Install with: pip install pyarrow")
        return 2
    if not os.path.isfile(args.input_parquet):
        print(f"ERROR: input parquet not found: {args.input_parquet}")
        return 2
    if not os.path.isfile(args.tokenizer):
        print(f"ERROR: tokenizer not found: {args.tokenizer}")
        return 2

    cfg = NexusAICore01Config()
    tokenizer = NexusAITokenizer(args.tokenizer, cfg)
    vocab = tokenizer.get_vocab_size()
    if vocab != cfg.vocab_size:
        print(f"ERROR: tokenizer vocab {vocab} != expected {cfg.vocab_size}")
        return 2

    out = args.output_dir
    outputs_exist = os.path.isdir(out) and any(
        f in os.listdir(out)
        for f in ("english_train.jsonl", "english_val.jsonl", "accepted_spool.jsonl")
    )
    if outputs_exist and not args.overwrite and not args.resume:
        print(f"ERROR: output dir already contains prepared data: {out}")
        print("Use --overwrite to replace, or --resume to continue.")
        return 2

    spool_path = os.path.join(out, "accepted_spool.jsonl")
    hashes_path = os.path.join(out, "dedup_hashes.txt")
    state_path = os.path.join(out, "prep_state.json")

    # fingerprints
    print("hashing source parquet (one-time cost)...", flush=True)
    src_sha = sha256_file(args.input_parquet)
    tok_sha = sha256_file(args.tokenizer)
    fp = config_fingerprint(args, tok_sha, src_sha)

    # ---------- resume state ----------
    done_row_groups = set()
    stats = {"inspected": 0, "accepted": 0, "rejected_clean": 0,
             "rejected_quality": 0, "duplicates": 0, "accepted_tokens": 0}
    resumed = False

    if args.resume and os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                st = json.load(f)
            if st.get("fingerprint") != fp:
                print("ERROR: resume state fingerprint mismatch "
                      "(source/tokenizer/config changed). Start fresh or "
                      "use a different --output-dir.")
                return 2
            done_row_groups = set(st.get("completed_row_groups", []))
            # restore cumulative counters; accepted/accepted_tokens are then
            # rebuilt authoritatively from the spool below
            for k in ("inspected", "rejected_clean", "rejected_quality",
                      "duplicates"):
                stats[k] = int(st.get("stats", {}).get(k, 0))
            # rebuild counters from spool (authoritative record of accepted docs)
            if os.path.exists(spool_path):
                with open(spool_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            rec = json.loads(line)
                            stats["accepted"] += 1
                            stats["accepted_tokens"] += int(rec.get("ntok", 0))
            resumed = True
            print(f"RESUME: {len(done_row_groups)} row groups already done; "
                  f"{stats['accepted']:,} docs / {stats['accepted_tokens']:,} tokens in spool")
        except Exception as e:
            print(f"ERROR: corrupt resume state ({e}). Refusing to resume.")
            return 2

    seen_hashes = set()
    if os.path.exists(hashes_path):
        with open(hashes_path, "r", encoding="utf-8") as f:
            for line in f:
                h = line.strip()
                if h:
                    seen_hashes.add(h)

    target_budget = int(args.target_tokens * (1.0 + args.buffer_fraction))
    print(f"target={args.target_tokens:,} budget={target_budget:,} "
          f"(buffer {args.buffer_fraction*100:.1f}%)")

    # ---------- dry-run early path (writes NOTHING, not even the dir) ----------
    if args.dry_run:
        sample_limit = args.max_docs or 2000
        n_acc = n_rej = n_dup = n_tok = 0
        for rg, di, raw in iter_parquet_texts(args.input_parquet):
            if args.max_row_groups and rg >= args.max_row_groups:
                break
            stats["inspected"] += 1
            t = clean_text(raw if isinstance(raw, str) else "")
            if t is None:
                n_rej += 1
                continue
            if args.english_filter == "heuristic":
                r = quality_reject(t, args.min_chars, args.max_chars)
                if r:
                    n_rej += 1
                    continue
            h = sha256_text(t)
            if h in seen_hashes:
                n_dup += 1
                continue
            n_tok += len(tokenizer.encode(t, add_special_tokens=False))
            n_acc += 1
            if n_acc >= sample_limit:
                break
        print(f"DRY-RUN: inspected={stats['inspected']} would_accept={n_acc} "
              f"would_reject={n_rej} would_dup={n_dup} est_tokens={n_tok:,}")
        print("DRY-RUN: no files written.")
        return 0

    # ---------- main processing loop ----------
    os.makedirs(out, exist_ok=True)
    spool_f = open(spool_path, "a", encoding="utf-8")
    hashes_f = open(hashes_path, "a", encoding="utf-8")
    prev_rg = None
    completed_rgs = set(done_row_groups)
    exhausted = True
    stop = False

    for rg, di, raw in iter_parquet_texts(args.input_parquet,
                                          skip_row_groups=completed_rgs):
        if rg != prev_rg:
            # previous row group fully consumed -> mark complete + checkpoint
            if prev_rg is not None and prev_rg not in completed_rgs:
                completed_rgs.add(prev_rg)
                _save_state(state_path, fp, sorted(completed_rgs), stats)
            prev_rg = rg
        if args.max_row_groups and rg >= args.max_row_groups:
            exhausted = False
            break
        if args.max_docs and stats["inspected"] >= args.max_docs:
            exhausted = False
            break
        if stop:
            exhausted = False
            break
        stats["inspected"] += 1

        text = clean_text(raw if isinstance(raw, str) else "")
        if text is None:
            stats["rejected_clean"] += 1
            continue
        if args.english_filter == "heuristic":
            reason = quality_reject(text, args.min_chars, args.max_chars)
            if reason:
                stats["rejected_quality"] += 1
                continue
        else:
            if len(text) < args.min_chars or len(text) > args.max_chars:
                stats["rejected_quality"] += 1
                continue

        h = sha256_text(text)
        if h in seen_hashes:
            stats["duplicates"] += 1
            continue

        # token count: raw SentencePiece pieces, NO BOS/EOS.
        # PackedTextDataset adds BOS/EOS later (~2 tokens/doc overhead).
        ntok = len(tokenizer.encode(text, add_special_tokens=False))
        if stats["accepted_tokens"] + ntok > target_budget:
            stop = True   # do not split documents; stop cleanly
            continue

        spool_f.write(json.dumps({"text": text, "ntok": ntok},
                                 ensure_ascii=False) + "\n")
        hashes_f.write(h + "\n")
        seen_hashes.add(h)
        stats["accepted"] += 1
        stats["accepted_tokens"] += ntok

        if stats["inspected"] % 5000 == 0:
            print(f"  inspected={stats['inspected']:,} accepted={stats['accepted']:,} "
                  f"tokens={stats['accepted_tokens']:,} dups={stats['duplicates']:,}",
                  flush=True)

    spool_f.close()
    hashes_f.close()

    # A row group is "complete" only when the iterator moved PAST it.
    # - exhausted=True (loop ended naturally): the last seen group was fully read.
    # - break on limit/stop: the last seen group may be partial -> NOT marked;
    #   on resume it is re-scanned and already-written docs are dedup-skipped.
    if prev_rg is not None and exhausted and prev_rg not in completed_rgs:
        completed_rgs.add(prev_rg)
    pf = pq.ParquetFile(args.input_parquet)
    n_rgs = pf.metadata.num_row_groups
    _save_state(state_path, fp, sorted(completed_rgs), stats,
                complete=(exhausted and len(completed_rgs) >= n_rgs))

    print(f"processing done in {time.time()-t0:.0f}s: "
          f"inspected={stats['inspected']:,} accepted={stats['accepted']:,} "
          f"tokens={stats['accepted_tokens']:,}")

    # ---------- split + final outputs ----------
    if stats["accepted"] == 0:
        print("ERROR: no documents accepted; nothing to write.")
        return 2

    n_docs = stats["accepted"]
    n_val = max(1, int(round(n_docs * args.val_fraction))) if n_docs > 10 else 0
    n_val = min(n_val, n_docs - 1) if n_docs > 1 else 0

    # deterministic index selection via seeded shuffle of range(n_docs)
    idx = list(range(n_docs))
    random.Random(args.seed).shuffle(idx)
    val_idx = set(idx[:n_val])

    train_path = os.path.join(out, "english_train.jsonl")
    val_path = os.path.join(out, "english_val.jsonl")
    tr_n = va_n = tr_tok = va_tok = 0
    with open(spool_path, "r", encoding="utf-8") as fin, \
         open(train_path, "w", encoding="utf-8") as ftr, \
         open(val_path, "w", encoding="utf-8") as fva:
        for i, line in enumerate(fin):
            if not line.strip():
                continue
            if i in val_idx:
                fva.write(line); va_n += 1
                va_tok += json.loads(line).get("ntok", 0)
            else:
                ftr.write(line); tr_n += 1
                tr_tok += json.loads(line).get("ntok", 0)

    # ---------- manifest + reports ----------
    manifest = {
        "dataset_name": "english_corpus_core01",
        "source": {
            "name": args.source_name,
            "config": args.source_config,
            "local_file": os.path.abspath(args.input_parquet),
            "file_name": os.path.basename(args.input_parquet),
            "sha256": src_sha,
            "shard_identifier": os.path.basename(args.input_parquet),
            "license": args.source_license,
            "commoncrawl_terms": "https://commoncrawl.org/terms-of-use",
            "attribution": f"{args.source_name} by Hugging Face (ODC-By 1.0)",
        },
        "tokenizer": {
            "file": os.path.abspath(args.tokenizer),
            "file_name": os.path.basename(args.tokenizer),
            "sha256": tok_sha,
            "vocab_size": vocab,
            "count_method": "raw SentencePiece pieces, no BOS/EOS "
                            "(PackedTextDataset adds BOS/EOS at pack time)",
        },
        "target": {
            "target_tokens": args.target_tokens,
            "buffer_fraction": args.buffer_fraction,
            "budget_tokens": target_budget,
            "actual_accepted_tokens": stats["accepted_tokens"],
            "overshoot_tokens": max(0, stats["accepted_tokens"] - args.target_tokens),
            "undershoot_tokens": max(0, args.target_tokens - stats["accepted_tokens"]),
        },
        "documents": {
            "inspected": stats["inspected"],
            "accepted": stats["accepted"],
            "rejected_cleaning": stats["rejected_clean"],
            "rejected_quality": stats["rejected_quality"],
            "duplicates": stats["duplicates"],
        },
        "split": {
            "method": "document-level seeded shuffle before packing",
            "seed": args.seed,
            "val_fraction": args.val_fraction,
            "train_docs": tr_n, "val_docs": va_n,
            "train_tokens": tr_tok, "val_tokens": va_tok,
            "leakage": "none — disjoint document sets",
        },
        "cleaning": {
            "nfc": True, "whitespace_collapse": True,
            "html_tag_strip": "conservative", "control_chars": "removed",
            "min_chars": args.min_chars, "max_chars": args.max_chars,
            "english_filter": args.english_filter,
            "english_filter_note": "heuristic quality gates only; NOT a "
                                   "linguistic language-ID guarantee",
        },
        "dedup": {"method": "exact SHA-256 over normalized text",
                  "near_dup": "not performed (source already MinHash-deduped upstream)"},
        "script": {"name": "prepare_english_corpus.py", "version": SCRIPT_VERSION},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "outputs": {},
    }
    for name in ("english_train.jsonl", "english_val.jsonl", "accepted_spool.jsonl",
                 "dedup_hashes.txt"):
        p = os.path.join(out, name)
        if os.path.exists(p):
            manifest["outputs"][name] = {"sha256": sha256_file(p),
                                         "bytes": os.path.getsize(p)}
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)

    dedup_report = {
        "inspected": stats["inspected"], "accepted": stats["accepted"],
        "duplicates": stats["duplicates"],
        "duplicate_rate": stats["duplicates"] / max(1, stats["inspected"]),
    }
    with open(os.path.join(out, "deduplication_report.json"), "w", encoding="utf-8") as f:
        json.dump(dedup_report, f, indent=1)

    with open(os.path.join(out, "preparation_report.md"), "w", encoding="utf-8") as f:
        f.write(f"""# English Corpus Preparation Report
- Source: {args.source_name}/{args.source_config} ({os.path.basename(args.input_parquet)})
- Tokenizer: {os.path.basename(args.tokenizer)} (vocab {vocab})
- Target: {args.target_tokens:,} tokens (budget {target_budget:,})
- Accepted: {stats['accepted_tokens']:,} tokens in {stats['accepted']:,} docs
- Overshoot: {max(0, stats['accepted_tokens']-args.target_tokens):,} / Undershoot: {max(0, args.target_tokens-stats['accepted_tokens']):,}
- Inspected: {stats['inspected']:,} | rejected(clean)={stats['rejected_clean']:,} rejected(quality)={stats['rejected_quality']:,} duplicates={stats['duplicates']:,}
- Split: train={tr_n:,} docs/{tr_tok:,} tok, val={va_n:,} docs/{va_tok:,} tok (seed={args.seed})
- Elapsed: {time.time()-t0:.0f}s
""")

    print(f"outputs -> {out}")
    print(f"train={tr_n:,} docs/{tr_tok:,} tok  val={va_n:,} docs/{va_tok:,} tok")
    print(f"actual/target = {stats['accepted_tokens']/args.target_tokens:.4f}")
    return 0


def _save_state(path, fingerprint, done_rgs, stats, complete=False):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({
            "fingerprint": fingerprint,
            "completed_row_groups": done_rgs,
            "stats": stats,
            "complete": complete,
            "version": SCRIPT_VERSION,
        }, f)
    os.replace(tmp, path)


if __name__ == "__main__":
    sys.exit(main())
