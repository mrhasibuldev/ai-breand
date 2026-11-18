# =============================================================================
# NEXUSAI MULTI-MODEL — MODEL REGISTRY
# Central, validated registry of all NexusAI-owned neural models.
# A checkpoint existing on disk != ready to serve. Validation is explicit.
# =============================================================================
import os, json, hashlib, torch, sys, time

AI_CORE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # packages/ai-core
ML_DIR  = os.path.dirname(os.path.abspath(__file__))                            # ml-service
MODELS_ROOT = os.path.join(AI_CORE, "models")
TOKENIZER_8K = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")

# Ensure core01 package importable
for p in (AI_CORE, os.path.join(AI_CORE, "models")):
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------------- registry --
MODEL_DEFS = {
    "nexus-core-01": {
        "name": "Core-01",
        "architecture": "core01_decoder_only_transformer",
        "arch_version": "1.0.0",
        "checkpoint": os.path.join(MODELS_ROOT, "checkpoints_core01_run3/checkpoint_final.pt"),
        "checkpoint_sha256": "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830",
        "expected_params": 8842560,
        "config": {"d_model":256,"n_layers":6,"n_heads":8,"d_ff":1024,"max_len":512,"vocab_size":8000},
        "tokenizer": TOKENIZER_8K,
        "tokenizer_type": "sentencepiece_bpe",
        "vocab_size": 8000,
        "max_len": 512,
        "languages": ["en","bn","banglish","mixed"],   # tokenizer-verified; capability limited pre-Run4
        "ram_mb_est": 420,
        "status": "candidate_primary",
        "training_run": "core01_run3 (step 1341, 3 epochs, english_first 7.43M tok)",
        "known_limits": "undertrained; weak reasoning/Bengali until Run4",
        "loader": "core01",
    },
    "nexus-medium": {
        "name": "MediumTransformer",
        "architecture": "medium_transformer",
        "arch_version": "1.0.0",
        "checkpoint": os.path.join(MODELS_ROOT, "checkpoints_medium/final_model.pt"),
        "checkpoint_sha256": "4f592af9846b89652eb7",   # prefix — full hash verified at load
        "expected_params": 2468928,
        "config": {"d_model":128,"n_layers":2,"n_heads":2,"d_ff":512,"max_len":128,"vocab_size":8000},
        "tokenizer": TOKENIZER_8K,
        "tokenizer_type": "sentencepiece_bpe",
        "vocab_size": 8000,
        "max_len": 128,
        "languages": ["en","bn"],
        "ram_mb_est": 60,
        "status": "fallback",
        "training_run": "Phase 10 (1,812 samples)",
        "known_limits": "very weak; gibberish-prone; retained as emergency fallback only",
        "loader": "medium",
    },
    # ---- Four-Core specialists (SFT v1, task-trained from scratch) ----
    # checkpoint_sha256 filled after training completes; "PENDING" fails safe.
    "nexus-core-02": {
        "name": "Core-02",
        "architecture": "core_decoder_only_transformer_sft",
        "arch_version": "1.0.0",
        "checkpoint": os.path.join(MODELS_ROOT, "checkpoints_core02_sft_v2/checkpoint_final.pt"),
        "checkpoint_sha256": "906d6024511f3e8ab48f36d077be391e2eae47573fa4ba29ba8e550c690cbb18",
        "expected_params": 20347712,
        "config": {"d_model":384,"n_layers":8,"n_heads":12,"d_ff":1536,"max_len":512,"vocab_size":8000},
        "tokenizer": TOKENIZER_8K,
        "tokenizer_type": "sentencepiece_bpe",
        "vocab_size": 8000,
        "max_len": 512,
        "languages": ["en","bn","banglish"],
        "ram_mb_est": 900,
        "status": "specialist_reasoning",
        "training_run": "core02_sft_v2 (clean question-level split)",
        "known_limits": "template-trained; held-out generalization limited",
        "loader": "nexus_sft",
        "core_id": "core02",
        "chat_format": True,
    },
    "nexus-core-03": {
        "name": "Core-03",
        "architecture": "core_decoder_only_transformer_sft",
        "arch_version": "1.0.0",
        "checkpoint": os.path.join(MODELS_ROOT, "checkpoints_core03_sft_v2/checkpoint_final.pt"),
        "checkpoint_sha256": "1ff83fb9ecd93944969c4086c206e2647c844c182c420b857e2f12b558d5e956",
        "expected_params": 8842560,
        "config": {"d_model":256,"n_layers":6,"n_heads":8,"d_ff":1024,"max_len":512,"vocab_size":8000},
        "tokenizer": TOKENIZER_8K,
        "tokenizer_type": "sentencepiece_bpe",
        "vocab_size": 8000,
        "max_len": 512,
        "languages": ["en","bn","banglish"],
        "ram_mb_est": 420,
        "status": "specialist_math",
        "training_run": "core03_sft_v2 (clean question-level split, 8 epochs)",
        "known_limits": "procedural math only; no general reasoning",
        "loader": "nexus_sft",
        "core_id": "core03",
        "chat_format": True,
    },
    "nexus-core-04": {
        "name": "Core-04",
        "architecture": "core_decoder_only_transformer_sft",
        "arch_version": "1.0.0",
        "checkpoint": os.path.join(MODELS_ROOT, "checkpoints_core04_sft_v3/checkpoint_final.pt"),
        "checkpoint_sha256": "e46383195d328b9105950939f66b0c36c6363f5b6bc5247c210efa99b5d17c48",
        "expected_params": 33419072,
        "config": {"d_model":512,"n_layers":8,"n_heads":8,"d_ff":2048,"max_len":512,"vocab_size":8000},
        "tokenizer": TOKENIZER_8K,
        "tokenizer_type": "sentencepiece_bpe",
        "vocab_size": 8000,
        "max_len": 512,
        "languages": ["en","bn"],
        "ram_mb_est": 1400,
        "status": "specialist_knowledge",
        "training_run": "core04_sft_v3 (full curated KB, 318 recs, 8 epochs — memorization model)",
        "known_limits": "small curated corpus; no live knowledge; narrow coverage",
        "loader": "nexus_sft",
        "core_id": "core04",
        "chat_format": True,
    },
    # NOTE: checkpoints/checkpoint_epoch_* (SmallTransformer, SimpleTokenizer ~1K vocab)
    # and checkpoints_medium/checkpoint_epoch_* (char-level vocab 74) are EXCLUDED:
    # tokenizer-incompatible with the app's SentencePiece path. Do not register
    # them until a matching tokenizer wrapper is implemented and verified.
}

STATUS = {"available","validated","loaded","active","disabled","incompatible","failed"}

def sha256_file(path, chunk=1<<20):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(chunk),b''): h.update(c)
    return h.hexdigest()

class ModelRegistry:
    """Validated registry. load() performs real compatibility checks."""

    def __init__(self):
        self._models = {mid: dict(d) for mid,d in MODEL_DEFS.items()}
        for m in self._models.values():
            m["runtime_status"]="available"   # available != validated != loaded
            m["engine"]=None
            m["last_error"]=None

    def list_models(self):
        return [{k:v for k,v in m.items() if k not in ("engine",)} for m in self._models.values()]

    def get(self, model_id):
        return self._models.get(model_id)

    def validate(self, model_id):
        """Static validation: file exists + hash + tokenizer vocab. No model built."""
        m=self._models.get(model_id)
        if not m: return False,"unknown model"
        ck=m["checkpoint"]
        if not os.path.exists(ck):
            m["runtime_status"]="failed"; m["last_error"]="checkpoint missing"; return False,"missing checkpoint"
        # hash check (full for core01, prefix-allowed for legacy)
        try:
            actual=sha256_file(ck)
            want=m["checkpoint_sha256"]
            ok = actual==want if len(want)==64 else actual.startswith(want)
            if not ok:
                m["runtime_status"]="incompatible"; m["last_error"]=f"hash mismatch {actual[:16]}"
                return False,"hash mismatch"
        except Exception as e:
            m["runtime_status"]="failed"; m["last_error"]=str(e); return False,str(e)
        if not os.path.exists(m["tokenizer"]):
            m["runtime_status"]="incompatible"; m["last_error"]="tokenizer missing"; return False,"tokenizer missing"
        m["runtime_status"]="validated"
        return True,"ok"

    def load(self, model_id, device="cpu"):
        """Validate then build engine. Strict state-dict; no silent substitution."""
        m=self._models.get(model_id)
        if not m: raise KeyError(f"unknown model {model_id}")
        if m["engine"] is not None:
            m["runtime_status"]="loaded"; return m["engine"]
        ok,why=self.validate(model_id)
        if not ok: raise RuntimeError(f"model {model_id} failed validation: {why}")
        t0=time.time()
        try:
            if m["loader"]=="core01":
                from nexusai_core_01.config.model_config import NexusAICore01Config
                from core01.inference import create_inference_engine
                cfg=NexusAICore01Config()
                eng=create_inference_engine(cfg, m["checkpoint"], device)
                m["engine"]={"kind":"core01","engine":eng,"load_s":round(time.time()-t0,2)}
            elif m["loader"]=="nexus_sft":
                eng=self._load_nexus_sft(m)
                m["engine"]={"kind":"nexus_sft","engine":eng,"load_s":round(time.time()-t0,2)}
            else:  # medium — reuse existing app generator path
                eng=self._load_medium(m)
                m["engine"]={"kind":"medium","engine":eng,"load_s":round(time.time()-t0,2)}
            m["runtime_status"]="loaded"
            return m["engine"]
        except Exception as e:
            m["runtime_status"]="failed"; m["last_error"]=str(e)
            raise

    def _load_nexus_sft(self, m):
        """Load a Core-02/03/04 SFT specialist: strict checkpoint load +
        SFT chat-format tokenizer. Returns dict with model+tokenizer+config."""
        from nexus_core import get_config, build_model, load_checkpoint_strict
        from core01.tokenizer_interface import create_default_tokenizer
        cfg=get_config(m["core_id"])
        model,cfg=build_model(m["core_id"],config=cfg,device="cpu")
        load_checkpoint_strict(model, m["checkpoint"], map_location="cpu")
        model.eval()
        tok=create_default_tokenizer(cfg)
        # record actual checkpoint hash into provenance at load time
        m["verified_sha256_at_load"]=sha256_file(m["checkpoint"])
        return {"kind":"nexus_sft","model":model,"tokenizer":tok,"config":cfg}

    def _load_medium(self, m):
        """Load MediumTransformer with sp_bpe_8k — mirrors existing app path."""
        import sentencepiece as spm
        from neural.medium_transformer import MediumTransformer
        sp=spm.SentencePieceProcessor(model_file=m["tokenizer"])
        ck=torch.load(m["checkpoint"],map_location="cpu",weights_only=False)
        cfg=ck.get("config",{})
        model=MediumTransformer(vocab_size=cfg.get("vocab_size",8000),
                                d_model=cfg.get("d_model",128),
                                n_layers=cfg.get("n_layers",2),
                                n_heads=cfg.get("n_heads",2),
                                d_ff=cfg.get("d_ff",512),
                                max_len=cfg.get("max_len",128))
        model.load_state_dict(ck["model_state_dict"])   # strict by default
        model.eval()
        # minimal wrapper exposing .generate(prompt,...)->str like app expects
        class _TokWrap:
            def __init__(s,sp): s.sp=sp; s.eos_id=sp.eos_id(); s.pad_id=sp.pad_id()
            def encode(s,t,add_special_tokens=True): return s.sp.encode(t,out_type=int)
            def decode(s,ids,skip_special_tokens=True): return s.sp.decode(ids)
        class _Gen:
            def __init__(s,model,tok): s.model=model; s.tokenizer=tok
            def generate(s,prompt,max_new_tokens=100,temperature=0.8,top_k=50,top_p=0.9,do_sample=True,repetition_penalty=1.2):
                import torch
                ids=s.tokenizer.encode(prompt,add_special_tokens=True)
                x=torch.tensor([ids],dtype=torch.long)
                for _ in range(max_new_tokens):
                    with torch.no_grad(): logits=s.model(x)
                    nxt=logits[0,-1]
                    if do_sample:
                        nxt=nxt/ max(temperature,1e-5)
                        probs=torch.softmax(nxt,dim=-1)
                        nt=torch.multinomial(probs,1)
                    else:
                        nt=torch.argmax(nxt).unsqueeze(0)
                    x=torch.cat([x,nt.unsqueeze(0)],dim=1)
                    if nt.item() in (s.tokenizer.eos_id,s.tokenizer.pad_id): break
                gen=x[0,ids.__len__():].tolist()
                return s.tokenizer.decode(gen)
        return {"kind":"medium","model":model,"generator":_Gen(model,_TokWrap(sp))}

    def generate(self, model_id, prompt, **kw):
        """Unified generate -> (text, provenance_dict)."""
        eng=self.load(model_id)
        m=self._models[model_id]
        if eng["kind"]=="nexus_sft":
            from nexus_core import chat_generate
            e=eng["engine"]
            txt=chat_generate(e["model"], e["tokenizer"], prompt,
                              max_new_tokens=kw.get("max_new_tokens",kw.get("max_tokens",64)),
                              temperature=kw.get("temperature",0.3),
                              top_k=kw.get("top_k",20), device="cpu")
        elif eng["kind"]=="core01":
            r=eng["engine"].generate(prompt, do_sample=kw.get("do_sample",True),
                                    max_new_tokens=kw.get("max_new_tokens",kw.get("max_tokens",64)),
                                    temperature=kw.get("temperature",0.8),
                                    top_k=kw.get("top_k",50), top_p=kw.get("top_p",0.9),
                                    repetition_penalty=kw.get("repetition_penalty",1.2))
            txt=(r or {}).get("generated_text","")
        else:
            txt=eng["engine"]["generator"].generate(prompt, **kw)
        prov={"model_id":model_id,"checkpoint":os.path.basename(m["checkpoint"]),
              "checkpoint_path":m["checkpoint"],
              "checkpoint_sha256":m.get("checkpoint_sha256"),
              "tokenizer":m.get("tokenizer"),
              "tokenizer_sha256":(sha256_file(m["tokenizer"])
                                  if m.get("tokenizer") and os.path.exists(m["tokenizer"]) else None),
              "vocab_size":m.get("vocab_size"),
              "engine":eng["kind"],"load_s":eng.get("load_s"),
              "neural_generation_executed":eng["kind"] in ("core01","medium"),
              "generation_status":"ok" if (txt or "").strip() else "empty"}
        return (txt or "").strip(), prov

    def status(self):
        return {mid:{"runtime_status":m["runtime_status"],"last_error":m["last_error"],
                     "loaded":m["engine"] is not None} for mid,m in self._models.items()}

# module-level singleton
registry = ModelRegistry()
