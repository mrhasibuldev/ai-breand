"""
NexusAI Core-01 Pretraining Driver

Top-level, configuration-driven entry point for Core-01 pretraining.

Wires together the existing tested components without modifying them:
  - text loading (.txt line-delimited or .jsonl with a text field)
  - document-level train/validation split (no leakage into packing)
  - PackedTextDataset (fixed-length token packing, minimal padding)
  - PretrainingEngine (AMP, gradient accumulation, atomic checkpoints,
    RNG-state resume, SFT gate untouched)

This module only *prepares and runs* training when explicitly invoked.
It does not start training on import.
"""

import argparse
import json
import os
import random
import sys
import time
from typing import List, Optional

import numpy as np
import torch
from torch.utils.data import DataLoader

ai_core_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(ai_core_dir), "models")
for p in (ai_core_dir, models_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from nexusai_core_01.config.model_config import NexusAICore01Config
from .transformer import NexusAICore01
from .dataset import DatasetLoader, PackedTextDataset
from .tokenizer_interface import NexusAITokenizer
from .training import PretrainingEngine, resolve_device


class _MaxStepsReached(Exception):
    """Internal control-flow exception used to stop training cleanly."""


def load_texts(path: str, text_field: str = "text") -> List[str]:
    """
    Load documents from a corpus file.

    Supported formats:
      - .jsonl : one JSON object per line; uses ``text_field`` (default "text")
      - .json  : a JSON list of strings or of objects with ``text_field``
      - other  : line-delimited plain text (empty lines skipped)
    """
    ext = os.path.splitext(path)[1].lower()
    texts: List[str] = []

    if ext == ".jsonl":
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if isinstance(obj, dict):
                    t = obj.get(text_field)
                    if isinstance(t, str) and t.strip():
                        texts.append(t.strip())
                elif isinstance(obj, str) and obj.strip():
                    texts.append(obj.strip())
    elif ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    t = item.get(text_field)
                    if isinstance(t, str) and t.strip():
                        texts.append(t.strip())
                elif isinstance(item, str) and item.strip():
                    texts.append(item.strip())
        else:
            raise ValueError(f"JSON file must contain a list: {path}")
    else:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    texts.append(line)

    return texts


def build_config(args: argparse.Namespace) -> NexusAICore01Config:
    """Build model/training config, applying CLI overrides."""
    config = NexusAICore01Config()
    overrides = {
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "grad_clip": args.grad_clip,
        "warmup_steps": args.warmup_steps,
        "precision": args.precision,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "checkpoint_interval_steps": args.checkpoint_interval,
        "eval_interval_steps": args.eval_interval,
        "device": args.device,
        "random_seed": args.seed,
        "tokenizer_path": args.tokenizer or "",
        "resume_checkpoint": args.resume or "",
    }
    for key, value in overrides.items():
        if value is not None:
            setattr(config, key, value)
    return config


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="NexusAI Core-01 pretraining driver (packed sequences)."
    )
    # Data
    p.add_argument("--train-file", required=True,
                   help="Train corpus: .txt (line-delimited), .jsonl, or .json")
    p.add_argument("--val-file", default=None,
                   help="Optional separate validation corpus (same formats). "
                        "If omitted, --val-fraction of train docs is held out.")
    p.add_argument("--val-fraction", type=float, default=0.01,
                   help="Fraction of documents held out for validation "
                        "when --val-file is not given (document-level split).")
    p.add_argument("--text-field", default="text",
                   help="JSON field containing text for .json/.jsonl inputs")
    # Model/tokenizer
    p.add_argument("--tokenizer", default=None,
                   help="Path to sp_bpe_8k.model (else config.tokenizer_path)")
    # Runtime
    p.add_argument("--output-dir", required=True,
                   help="Directory for checkpoints and token cache")
    p.add_argument("--device", default="auto",
                   help="'auto' | 'cpu' | 'cuda' | 'cuda:N'")
    p.add_argument("--precision", default="fp16",
                   choices=["fp32", "fp16", "bf16"])
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--max-steps", type=int, default=0,
                   help="Stop after N optimizer steps (0 = no limit)")
    # Optimization
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--gradient-accumulation-steps", type=int, default=None)
    p.add_argument("--learning-rate", type=float, default=None)
    p.add_argument("--weight-decay", type=float, default=None)
    p.add_argument("--grad-clip", type=float, default=None)
    p.add_argument("--warmup-steps", type=int, default=None)
    # Checkpointing / eval / logging
    p.add_argument("--checkpoint-interval", type=int, default=None,
                   help="Save checkpoint every N optimizer steps")
    p.add_argument("--eval-interval", type=int, default=None,
                   help="Run validation every N optimizer steps (0=off)")
    p.add_argument("--log-interval", type=int, default=50,
                   help="Log training loss every N optimizer steps")
    p.add_argument("--resume", default=None,
                   help="Checkpoint filename inside --output-dir to resume from")
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.epochs < 1:
        print("ERROR: --epochs must be >= 1")
        return 2
    t_start = time.time()

    config = build_config(args)
    device = resolve_device(config.device)
    config.device = device

    # Seed ALL RNGs before model init and any randomized data operations.
    # On resume, engine.load_checkpoint() later restores the checkpoint's
    # captured RNG state, overwriting these seeds — correct ordering.
    seed = config.random_seed
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    print(f"seed={seed} applied to python/numpy/torch"
          + ("/cuda" if torch.cuda.is_available() else ""))

    resolved_tokenizer = (
        args.tokenizer
        or config.tokenizer_path
        or os.path.join(
            ai_core_dir, "..", "data", "experimental", "phase9_2",
            "tokenizers", "bpe_8k", "sp_bpe_8k.model"
        )
    )

    print("=" * 60)
    print("NexusAI Core-01 Pretraining Driver")
    print("=" * 60)
    print(f"device={device} precision={config.precision} "
          f"batch_size={config.batch_size} "
          f"accum={config.gradient_accumulation_steps} "
          f"lr={config.learning_rate} warmup={config.warmup_steps}")
    print(f"train_file={args.train_file}")
    print(f"output_dir={args.output_dir}")

    # ---- Data ----
    train_texts = load_texts(args.train_file, args.text_field)
    if not train_texts:
        print("ERROR: no texts loaded from train file")
        return 2
    print(f"loaded {len(train_texts)} training documents")

    loader = DatasetLoader(config)
    if args.val_file:
        val_texts = load_texts(args.val_file, args.text_field)
        if not val_texts:
            print("ERROR: no texts loaded from val file")
            return 2
        print(f"loaded {len(val_texts)} validation documents (separate file)")
    else:
        frac = min(max(args.val_fraction, 0.0), 0.5)
        train_texts, val_texts, _ = loader.split_dataset(
            train_texts, train_ratio=1.0 - frac, val_ratio=frac,
            test_ratio=0.0, random_seed=config.random_seed
        )
        print(f"document-level split: {len(train_texts)} train / "
              f"{len(val_texts)} val (fraction={frac})")

    tokenizer = NexusAITokenizer(resolved_tokenizer, config)
    os.makedirs(args.output_dir, exist_ok=True)

    train_ds = PackedTextDataset(
        train_texts, tokenizer, max_len=config.max_len,
        pad_id=config.pad_id,
        token_cache_path=os.path.join(args.output_dir, "train_tokens.npy")
    )
    val_ds = PackedTextDataset(
        val_texts, tokenizer, max_len=config.max_len,
        pad_id=config.pad_id,
        token_cache_path=os.path.join(args.output_dir, "val_tokens.npy")
    ) if val_texts else None

    print(f"train blocks={len(train_ds)} tokens={train_ds.num_tokens} "
          f"pad_tokens={train_ds.padding_token_count}")
    if val_ds is not None:
        print(f"val   blocks={len(val_ds)} tokens={val_ds.num_tokens} "
              f"pad_tokens={val_ds.padding_token_count}")

    train_loader = DataLoader(
        train_ds, batch_size=config.batch_size, shuffle=True,
        num_workers=0, drop_last=True
    )
    if len(train_loader) == 0:
        print("ERROR: train set produced 0 batches "
              f"({len(train_ds)} blocks, batch_size={config.batch_size}, "
              "drop_last=True). Increase data or reduce batch_size.")
        return 2
    val_loader = DataLoader(
        val_ds, batch_size=config.batch_size, shuffle=False,
        num_workers=0
    ) if val_ds is not None else None

    # ---- Model + engine ----
    model = NexusAICore01(config).to(device)
    n_params = model.count_parameters()
    print(f"model parameters={n_params:,} device={device}")

    engine = PretrainingEngine(
        model, config, checkpoint_dir=args.output_dir,
        tokenizer_path=resolved_tokenizer
    )
    est_steps = max(1, len(train_loader) * args.epochs //
                    max(1, config.gradient_accumulation_steps))
    engine.setup_scheduler(est_steps)

    state = {"last_train_loss": float("nan"), "last_val_loss": float("nan"),
             "log_loss_sum": 0.0, "log_loss_n": 0}

    def on_step(eng, epoch, step, batch_idx, loss_value):
        state["log_loss_sum"] += loss_value
        state["log_loss_n"] += 1
        if step % args.log_interval == 0:
            avg = state["log_loss_sum"] / max(1, state["log_loss_n"])
            print(f"[step {step}] epoch={epoch} loss={avg:.4f} "
                  f"elapsed={time.time()-t_start:.0f}s", flush=True)
            state["log_loss_sum"] = 0.0
            state["log_loss_n"] = 0

        do_eval = (args.eval_interval and args.eval_interval > 0
                   and step % args.eval_interval == 0 and val_loader is not None)
        do_ckpt = (config.checkpoint_interval_steps > 0
                   and step % config.checkpoint_interval_steps == 0)

        if do_eval or do_ckpt:
            vl = float("nan")
            if do_eval:
                vl = eng.validate(val_loader, device=device)
                eng.model.train()  # restore train mode after eval
                state["last_val_loss"] = vl
                print(f"[step {step}] val_loss={vl:.4f}", flush=True)
            if do_ckpt:
                path = eng.save_checkpoint(
                    epoch=epoch, train_loss=state["last_train_loss"],
                    val_loss=state["last_val_loss"],
                    filename=f"checkpoint_step{step}.pt"
                )
                print(f"[step {step}] checkpoint -> {path}", flush=True)

        if args.max_steps and step >= args.max_steps:
            raise _MaxStepsReached()

    # ---- Resume ----
    if args.resume:
        engine.load_checkpoint(args.resume)
        print(f"resumed from checkpoint: {args.resume} "
              f"(step={engine.current_step})")

    # ---- Train ----
    interrupted = False
    try:
        for epoch in range(engine.current_epoch, args.epochs):
            engine.current_epoch = epoch
            print(f"--- epoch {epoch + 1}/{args.epochs} "
                  f"({len(train_loader)} micro-batches) ---", flush=True)
            loss = engine.train_epoch(train_loader, device=device,
                                      on_step=on_step)
            state["last_train_loss"] = loss
            print(f"epoch {epoch + 1} train_loss={loss:.4f}", flush=True)

            if val_loader is not None:
                vl = engine.validate(val_loader, device=device)
                engine.model.train()
                state["last_val_loss"] = vl
                print(f"epoch {epoch + 1} val_loss={vl:.4f}", flush=True)

            path = engine.save_checkpoint(
                epoch=epoch + 1, train_loss=loss,
                val_loss=state["last_val_loss"],
                filename="checkpoint_last.pt"
            )
            print(f"epoch {epoch + 1} checkpoint -> {path}", flush=True)

        # All configured epochs completed successfully -> final checkpoint
        # marked PRETRAINING_COMPLETED (SFT gate will accept it).
        path = engine.save_checkpoint(
            epoch=args.epochs, train_loss=state["last_train_loss"],
            val_loss=state["last_val_loss"],
            filename="checkpoint_final.pt", finalize=True
        )
        print(f"pretraining objective complete -> {path} "
              f"(status=PRETRAINING_COMPLETED)", flush=True)
    except _MaxStepsReached:
        # --max-steps IS the explicitly configured objective when set, so
        # reaching it counts as successful completion.
        print(f"max_steps={args.max_steps} reached; saving final checkpoint",
              flush=True)
        engine.save_checkpoint(
            epoch=engine.current_epoch,
            train_loss=state["last_train_loss"],
            val_loss=state["last_val_loss"],
            filename="checkpoint_maxsteps.pt", finalize=True
        )
    except KeyboardInterrupt:
        interrupted = True
        print("interrupted; saving emergency checkpoint "
              "(status remains PRETRAINING_IN_PROGRESS)", flush=True)
        engine.save_checkpoint(
            epoch=engine.current_epoch,
            train_loss=state["last_train_loss"],
            val_loss=state["last_val_loss"],
            filename="checkpoint_interrupted.pt", finalize=False
        )
    except Exception as exc:
        # Unexpected failure: save a NON-final checkpoint for forensics,
        # never mark completed, then re-raise.
        print(f"unexpected error: {exc}; saving non-final checkpoint",
              flush=True)
        try:
            engine.save_checkpoint(
                epoch=engine.current_epoch,
                train_loss=state["last_train_loss"],
                val_loss=state["last_val_loss"],
                filename="checkpoint_error.pt", finalize=False
            )
        except Exception:
            pass
        raise

    elapsed = time.time() - t_start
    print("=" * 60)
    print(f"done. elapsed={elapsed:.0f}s "
          f"steps={engine.current_step} "
          f"interrupted={interrupted}")
    print(f"model_status -> checkpoint metadata reflects training state; "
          f"verify before any downstream use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
