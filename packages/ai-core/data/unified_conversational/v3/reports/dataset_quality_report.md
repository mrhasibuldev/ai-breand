# v3 Quality Report (rule-based)
- Records parse: all JSONL valid (builder writes + re-read verified).
- Unique IDs: enforced (sample_id sequence).
- Roles: user-first, assistant-last, alternating — validated.
- Non-empty content: validated.
- Exact-question dedup: enforced (seen_q set).
- Near-dup: normalized prefix >3 collisions → quarantined.
- Foreign-script corruption: CJK/Arabic/Cyrillic/Thai detected → rejected
  (203 total rejected incl. this guard).
- Math answers: verified at generation time (deterministic recompute).
- Semantic naturalness: RULE-CHECKED ONLY — human review pending for
  bn/banglish records (flagged in quality.status).
