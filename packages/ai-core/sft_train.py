"""
Generic NexusAI SFT trainer — shared by Core-02/03/04 (and reusable for
Core-01 under a separately named run).

Response-only loss: only assistant content tokens + assistant EOS are
supervised (labels pre-shifted by serialize_conversation). Uses explicit
CrossEntropyLoss(ignore_index=-100) because the model's internal loss path
only ignores pad_id. Batches with zero supervised tokens are SKIPPED.
Attention masks mask padded KEY positions.

Saves versioned checkpoint + .sha256 provenance. Resumable via --resume.

Usage (local CPU smoke or Colab GPU):
    python sft_train.py --core core03 --data-dir data/core03_math \
        --out models/checkpoints_core03_sft_v1 --epochs 3 --batch-size 8
"""
import argparse
import json
import os
import sys
import time

AI_CORE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from nexus_core import build_model, save_checkpoint, load_checkpoint_strict, get_config
from core01.sft_dataset import ChatSFTDataset, collate, batch_has_supervision
from core01.tokenizer_interface import create_default_tokenizer


def set_seed(seed):
    import random
    random.seed(seed)
    torch.manual_seed(seed)


def evaluate_loss(model, loader, device):
    model.eval()
    total, count = 0.0, 0
    with torch.no_grad():
        for batch in loader:
            if not batch_has_supervision(batch["labels"]):
                continue
            ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attn = batch["attention_mask"].to(device)
            logits = model(ids, attention_mask=attn)
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)), labels.view(-1),
                ignore_index=-100)
            n = (labels != -100).sum().item()
            total += loss.item() * n
            count += n
    model.train()
    return total / max(count, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", required=True, choices=["core02", "core03", "core04", "core01"])
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", required=True, help="checkpoint output path (.pt)")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--max-len", type=int, default=512)
    ap.add_argument("--max-steps", type=int, default=0, help="0 = unlimited")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--resume", default="")
    args = ap.parse_args()

    set_seed(args.seed)
    device = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
    print(f"[sft_train] core={args.core} device={device} torch={torch.__version__}")

    config = get_config(args.core)
    config.max_len = args.max_len
    model, config = build_model(args.core, config=config, device=device)

    tokenizer = create_default_tokenizer(config)

    train_ds = ChatSFTDataset(os.path.join(args.data_dir, "train.jsonl"), tokenizer, args.max_len)
    val_ds = ChatSFTDataset(os.path.join(args.data_dir, "validation.jsonl"), tokenizer, args.max_len)
    train_ld = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                          collate_fn=lambda b: collate(b, tokenizer.pad_id),
                          drop_last=False)
    val_ld = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                        collate_fn=lambda b: collate(b, tokenizer.pad_id))
    print(f"[sft_train] train={len(train_ds)} val={len(val_ds)} params={model.count_parameters():,}")

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    start_step = 0
    if args.resume and os.path.exists(args.resume):
        ckpt = torch.load(args.resume, map_location=device, weights_only=True)
        load_checkpoint_strict(model, args.resume, map_location=device)
        if "optimizer_state_dict" in ckpt:
            opt.load_state_dict(ckpt["optimizer_state_dict"])
        start_step = ckpt.get("global_step", 0)
        print(f"[sft_train] resumed from {args.resume} step={start_step}")

    model.train()
    step = start_step
    t0 = time.time()
    run = {"core": args.core, "args": vars(args), "history": []}
    stop = False
    for epoch in range(args.epochs):
        if stop:
            break
        for batch in train_ld:
            if not batch_has_supervision(batch["labels"]):
                continue
            ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attn = batch["attention_mask"].to(device)
            logits = model(ids, attention_mask=attn)
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)), labels.view(-1),
                ignore_index=-100)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            if step % 20 == 0:
                print(f"[sft_train] epoch={epoch} step={step} loss={loss.item():.4f} "
                      f"elapsed={time.time()-t0:.0f}s", flush=True)
            if args.max_steps and step - start_step >= args.max_steps:
                stop = True
                break
        vl = evaluate_loss(model, val_ld, device)
        run["history"].append({"epoch": epoch, "step": step, "val_loss": vl})
        print(f"[sft_train] epoch={epoch} done step={step} val_loss={vl:.4f}", flush=True)

    meta = save_checkpoint(model, config, args.out,
                           extra={"training": run, "global_step": step,
                                  "dataset": os.path.basename(args.data_dir)})
    print(f"[sft_train] saved {meta['path']} sha256={meta['sha256'][:16]}... "
          f"params={model.count_parameters():,} steps={step}")


if __name__ == "__main__":
    main()
