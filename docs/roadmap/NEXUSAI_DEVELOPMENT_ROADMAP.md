# NexusAI — Development Roadmap

States: ✅ implemented & verified · ⚠️ partial · 🚫 blocked · 📋 planned

## Stage 1 — Repository & project stabilization ✅ (complete 2026-11)
- [x] Full forensic audit + stabilization (CSRF, context bounds, provenance, session preservation, timeouts)
- [x] Vitest infrastructure repair — 203/203
- [x] Python suites — 44/44 + 13/13
- [x] Git LFS delivery of all five cores
- [x] Secret-safe GitHub backup policy
- [x] Professional README + audit documentation

## Stage 2 — AI Core verification ✅ (complete)
- [x] All 5 registered cores strict-load with SHA-256 provenance
- [x] Measured param counts; tokenizer compatibility verified
- [x] Live neural generation proven (core-04, 4.6 s CPU)
- [x] Router/deterministic/tool/fallback paths labeled honestly
- [x] 21-prompt trilingual evaluation baseline (`eval_reports/final_quality_eval.json`)

## Stage 3 — Own model quality improvement 📋 (next major phase — NOT started)
- [ ] Deduplicate SFT datasets (core-02 60%, core-03 18% exact duplicates — documented defect)
- [ ] Bengali generation quality (currently honest fallback dominates)
- [ ] English semantic correctness (guard now filters obvious mismatches; real relevance needs model capability)
- [ ] Banglish understanding (tokenizer fragmentation documented)
- [ ] Larger/better architectures within CPU budget; KV-cache decoding; quantized inference
- [ ] Expanded trilingual reasoning SFT data; rejection-sampling against safety guard
- [ ] Repeatable eval harness gating every training run

## Stage 4 — Advanced AI Brain 📋
- [ ] Multi-turn context in generation path
- [ ] Consent-based memory runtime
- [ ] Multi-step reasoning / self-correction
- [ ] Tool orchestration beyond math
- [ ] Voice, multimodal, public developer API

## Stage 5 — Long-term vision 📋
Independent AGI research platform: owned data, owned weights, owned evals — no external AI dependencies at any layer.

## Known blockers
- 🚫 Neon isolated test DB → authenticated write-path E2E unverified
- ⚠️ Host RAM/disk constraints limit local load testing
