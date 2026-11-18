# Run4 Generation Benchmark — STATUS: BLOCKED LOCALLY

Run4 checkpoint exists only on Google Drive (`/content/drive/MyDrive/NEXUSAI_RUN4/`).
Not accessible from this machine → cannot hash-verify, strict-load, or
generate locally. This is an environment blocker, not a failure.

## Tokenizer provenance — RESOLVED
Local `sp_bpe_8k.model` sha256 =
`2fcc6a87c9ded27d1f8ad6c2dc0ff747ca4dc52db68ffde9a6e229b2cd3d8052`
— EXACT match to reported Run4 tokenizer hash. Run3's stale path pointed
to the same filename; the packaged tokenizer IS the shared tokenizer.
**Fair Run3/Run4 comparison is NOT blocked on tokenizer grounds.**

## Benchmark vehicle (ready)
`docs/notebooks/COLAB_RUN4_VERIFY_BENCHMARK_CELL.py` — verifies both ckpt
hashes, strict-loads, runs 18-prompt suite × greedy+sampling via the
fixed InferenceEngine, preserves all outputs, re-hashes after.
Run it in Colab; results → `/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT/`.

## Run4 decision rule (pre-registered)
Switch registry to Run4 ONLY IF: sha matches `761a5b14…` AND strict load
passes AND benchmark shows equal/better empty-rate and qualitatively
better outputs vs Run3. Otherwise keep Run3 active, report why.
