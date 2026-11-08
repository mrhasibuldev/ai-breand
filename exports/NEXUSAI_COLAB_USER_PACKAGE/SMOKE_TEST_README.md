# NexusAI Core-01 — Colab GPU Smoke Test
#hanger ✅ এই ফাইলটা হলো আপনার **একটাই** consolidated smoke-test cell।
#
# **কী করা হবে:**
#   Stage A: GPU/CUDA check
#   Stage B: transformer.py ঠিক আছে কিনা verify (SHA-256)
#   Stage C: model load + 8,842,560 params check
#   Stage D: FP16 forward+backward+optimizer (bs2×256)
#   Stage E: attention mask test
#   Stage F: ২ step-এর real driver run → checkpoint
#   Stage G: resume test (+1 step)
#   Stage H: cleanup + report
#
# **Report save হবে:** Google Drive → NexusAI/audit_reports/
#
# ⚠️ এটা শুধু smoke test — full training না। Synthetic data only.
# ⚠️ আগে transformer.py upload + SHA verify করা বাধ্যতামূলক (guide দেখুন)।
