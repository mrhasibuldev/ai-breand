"""
Run4 infrastructure tests — checkpoint, tokenizer, repo, GPU (conditional).
Run: python packages/ai-core/tests/run4_infrastructure/test_run4_infra.py
GPU tests SKIP (not fail) on CPU-only machines.
"""
import os, sys, json, hashlib

AI_CORE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir, os.pardir))
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))
REPO = os.path.abspath(os.path.join(AI_CORE, os.pardir, os.pardir))
CKPT = os.path.join(AI_CORE, "models", "checkpoints_core01_run3",
                    "checkpoint_final.pt")
MAN = os.path.join(AI_CORE, "models", "checkpoints_core01_run3",
                   "CHECKPOINT_MANIFEST.json")
TOK = os.path.join(AI_CORE, "data", "experimental", "phase9_2",
                   "tokenizers", "bpe_8k", "sp_bpe_8k.model")
SHA = "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"
SIZE = 106777501
RESULTS = []
def t(name, fn):
    try:
        fn(); RESULTS.append((name, "PASS", "")); print("PASS", name)
    except Exception as e:
        RESULTS.append((name, "FAIL", str(e)[:200])); print("FAIL", name, e)

def skip(name, why):
    RESULTS.append((name, "SKIP", why)); print("SKIP", name, why)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()

def test_manifest():
    m = json.load(open(MAN, encoding="utf-8"))
    assert m["sha256"] == SHA and m["file_size_bytes"] == SIZE
    assert m["parameters"] == 8842560 and m["epoch"] == 3 and m["global_step"] == 1341

def test_ckpt_size_sha():
    assert os.path.getsize(CKPT) == SIZE
    assert sha256(CKPT) == SHA

def test_ckpt_structure():
    import torch
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    for k in ("model_state_dict","optimizer_state_dict",
              "scheduler_state_dict","grad_scaler_state_dict","rng_state"):
        assert k in ck, k
    assert ck["epoch"] == 3 and ck["step"] == 1341
    keys = list(ck["model_state_dict"])
    assert any(k.startswith("transformer_blocks.") for k in keys)
    assert not any("self_attn.in_proj_weight" in k for k in keys)

def test_param_count():
    import torch
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    sd = ck["model_state_dict"]
    # exclude non-param buffer positional_encoding.pe (512x256=131072)
    n = sum(v.numel() for k, v in sd.items()
            if not k.startswith("positional_encoding."))
    assert n == 8842560, n

def test_tokenizer():
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(); sp.load(TOK)
    assert sp.get_piece_size() == 8000
    assert len(sp.encode("বাংলাদেশ")) > 0
    assert len(sp.encode("Hello world")) > 0
    assert len(sp.encode("eta tumi kemon acho")) > 0  # banglish

def test_lfs_pointer():
    # staged blob must be an LFS pointer, not raw bytes
    import subprocess
    r = subprocess.run(["git", "cat-file", "-p",
        ":packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt"],
        capture_output=True, text=True, cwd=REPO)
    assert "version https://git-lfs.github.com/spec/v1" in r.stdout
    assert SHA in r.stdout

def test_gpu():
    try:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError("cuda unavailable — CPU-only env")
        x = torch.randn(256, 256, device="cuda")
        assert (x @ x).sum().item() == (x @ x).sum().item()
        free = torch.cuda.mem_get_info(0)[0] / 2**30
        assert free > 4, f"only {free:.1f}GB free"
    except RuntimeError as e:
        skip("gpu_cuda_tensor", str(e))
        return

def main():
    t("manifest_identity", test_manifest)
    t("ckpt_size_sha256", test_ckpt_size_sha)
    t("ckpt_structure_resume", test_ckpt_structure)
    t("param_count_8842560", test_param_count)
    t("tokenizer_8000_trilingual", test_tokenizer)
    t("lfs_pointer_oid", test_lfs_pointer)
    test_gpu()
    p = sum(1 for _, s, _ in RESULTS if s == "PASS")
    f = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    s = sum(1 for _, s, _ in RESULTS if s == "SKIP")
    print(f"\n{p} PASS / {f} FAIL / {s} SKIP")
    sys.exit(1 if f else 0)

if __name__ == "__main__":
    main()
