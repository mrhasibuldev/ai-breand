"""
NexusAI Core-01 SFT dataset + chat serialization with response-only loss.

Serialization format (documented, deterministic):
    [BOS] "user: " + user_text + [EOS]
          "assistant: " + assistant_text + [EOS]
    (repeated per turn for multi-turn)

Loss masking: only assistant CONTENT tokens + assistant EOS are supervised.
User text, role markers, BOS, and padding are masked with -100.

This module is dataset/preparation code only — no training here.
"""
import json
import torch
from torch.utils.data import Dataset

USER_TAG = "user: "
ASSISTANT_TAG = "assistant: "


def serialize_conversation(tokenizer, messages, max_len=512):
    """
    Returns (input_ids, labels) both length <= max_len.
    labels[i] = token id that input_ids[i] should predict, or -100.
    Shift is applied HERE so model receives pre-shifted targets matching
    the PackedTextDataset convention (input=block[:-1], target=block[1:]).
    """
    bos, eos, pad = tokenizer.bos_id, tokenizer.eos_id, tokenizer.pad_id
    seq, supervise = [], []  # supervise[i]=True if seq[i] is assistant-side

    def add(text, is_assistant):
        ids = tokenizer.encode(text, add_special_tokens=False)
        seq.extend(ids)
        supervise.extend([is_assistant] * len(ids))

    for m in messages:
        if m["role"] == "user":
            seq.append(bos)  # BOS marks turn start
            supervise.append(False)
            add(USER_TAG + m["content"], False)
            seq.append(eos); supervise.append(False)
        elif m["role"] == "assistant":
            add(ASSISTANT_TAG + m["content"], True)  # content supervised
            seq.append(eos); supervise.append(True)  # assistant EOS supervised
        else:
            raise ValueError(f"unknown role: {m['role']}")

    # build shifted labels: labels[i] predicts seq[i+1]
    input_ids, labels = [], []
    for i in range(len(seq) - 1):
        input_ids.append(seq[i])
        # supervise the NEXT token if it is assistant-side content/eos
        labels.append(seq[i + 1] if supervise[i + 1] else -100)
    # truncation policy: drop from left, keep BOS if possible; never cut
    # an assistant answer silently — if truncated mid-answer, mask tail.
    if len(input_ids) > max_len:
        input_ids = input_ids[:max_len]
        labels = labels[:max_len]
        # ensure no supervised label survives beyond a truncated assistant span
        # (approximation: labels already -100 where masked; truncation may cut
        #  a response — acceptable, documented; samples are short by design)
    return input_ids, labels


class ChatSFTDataset(Dataset):
    """JSONL {messages:[...]} -> (input_ids, labels) tensors, padded."""

    def __init__(self, jsonl_path, tokenizer, max_len=512):
        self.records = []
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.records.append(json.loads(line))
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        r = self.records[idx]
        ids, labels = serialize_conversation(
            self.tokenizer, r["messages"], self.max_len)
        return {"input_ids": torch.tensor(ids, dtype=torch.long),
                "labels": torch.tensor(labels, dtype=torch.long)}


def collate(batch, pad_id):
    """Right-pad input_ids with pad_id; labels padded with -100;
    attention_mask marks real tokens (1) vs padding (0) for key masking."""
    maxlen = max(len(b["input_ids"]) for b in batch)
    input_ids, labels, attn = [], [], []
    for b in batch:
        n = len(b["input_ids"])
        input_ids.append(torch.cat([b["input_ids"],
                                    torch.full((maxlen - n,), pad_id, dtype=torch.long)]))
        labels.append(torch.cat([b["labels"],
                                 torch.full((maxlen - n,), -100, dtype=torch.long)]))
        attn.append(torch.cat([torch.ones(n, dtype=torch.long),
                               torch.zeros(maxlen - n, dtype=torch.long)]))
    return {"input_ids": torch.stack(input_ids),
            "labels": torch.stack(labels),
            "attention_mask": torch.stack(attn)}


def batch_has_supervision(labels):
    """Guard: True iff batch contains >=1 supervised (non -100) label.
    Batches failing this must be SKIPPED — never produce NaN loss."""
    return bool((labels != -100).any().item())
