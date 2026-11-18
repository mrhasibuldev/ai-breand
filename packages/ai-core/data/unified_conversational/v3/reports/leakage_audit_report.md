# v3 Leakage Audit (VERIFIED)
- Split method: sha256(split_group) ordering, 90/5/5.
- Groups atomic: multi-turn scenarios + paraphrase variants share
  split_group via same base seed → cannot cross splits.
- v1/v2 records re-grouped (their original splits NOT preserved — v3 is
  a new dataset version; v1/v2 files remain frozen separately).
- Exact-question dedup across ALL records before split.
- Paraphrase variants share group → no paraphrase leakage.
- Benchmark cases authored separately, never in training data.
