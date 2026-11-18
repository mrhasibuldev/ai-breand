"""Dataset discovery, integrity, tokenizer-compat checks."""
import os, json, hashlib
from dataclasses import dataclass, field

@dataclass
class DatasetReport:
    path: str = ""
    exists: bool = False
    size: int = 0
    sha256: str = ""
    records: int = 0
    malformed: int = 0
    empty_text: int = 0
    manifest_ok: bool = False
    errors: list = field(default_factory=list)

def inspect_jsonl(path: str, expected_sha: str = None,
                  expected_records: int = None,
                  max_scan: int = None) -> DatasetReport:
    r = DatasetReport(path=path)
    if not os.path.exists(path):
        r.errors.append("dataset not found"); return r
    r.exists = True
    r.size = os.path.getsize(path)
    if expected_sha:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for c in iter(lambda: f.read(1 << 22), b""):
                h.update(c)
        r.sha256 = h.hexdigest()
        if r.sha256 != expected_sha:
            r.errors.append("sha256 mismatch")
    n = bad = empty = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            n += 1
            if max_scan and n > max_scan:
                break
            try:
                rec = json.loads(line)
                if not isinstance(rec, dict) or not str(rec.get("text", "")).strip():
                    empty += 1
            except Exception:
                bad += 1
    r.records = n; r.malformed = bad; r.empty_text = empty
    if expected_records is not None and n != expected_records:
        r.errors.append(f"record count {n} != expected {expected_records}")
    if bad or empty:
        r.errors.append(f"malformed={bad} empty={empty}")
    return r
