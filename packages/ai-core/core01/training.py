"""
NexusAI Core-01 Training Infrastructure

Provides pretraining and instruction fine-tuning pipelines for NexusAI Core-01.
This code creates the training infrastructure but does NOT execute training.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
import os
import time
import random
import numpy as np
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import sys

# Add models directory to path for config import
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(ai_core_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
from .transformer import NexusAICore01
from .dataset import DatasetLoader
from .tokenizer_interface import NexusAITokenizer


def get_rng_state() -> Dict[str, Any]:
    """Capture Python, NumPy, and PyTorch RNG states for reproducible resume."""
    state = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch_cpu": torch.random.get_rng_state(),
    }
    if torch.cuda.is_available():
        state["torch_cuda"] = torch.cuda.get_rng_state_all()
    return state


def set_rng_state(state: Dict[str, Any]) -> None:
    """Restore RNG states captured by get_rng_state(). Missing keys are skipped."""
    if "python" in state:
        random.setstate(state["python"])
    if "numpy" in state:
        np.random.set_state(state["numpy"])
    if "torch_cpu" in state:
        torch.random.set_rng_state(state["torch_cpu"])
    if "torch_cuda" in state and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["torch_cuda"])


def resolve_device(device: str = "cpu") -> str:
    """
    Resolve a device string.

    Args:
        device: 'cpu' (literal CPU), 'auto' (cuda if available else cpu),
                or 'cuda[:N]' (cuda if available else cpu fallback)

    Returns:
        Resolved device string usable with tensor .to()
    """
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if device.startswith("cuda") and not torch.cuda.is_available():
        return "cpu"
    return device


def resolve_amp_dtype(precision: str, device: str) -> Optional[torch.dtype]:
    """
    Resolve the autocast dtype for a given precision setting.

    Args:
        precision: 'fp32', 'fp16', or 'bf16'
        device: Resolved device string

    Returns:
        torch.bfloat16 / torch.float16 for AMP, or None for FP32/no-AMP.
        BF16 requires CUDA compute capability >= 8.0 (Ampere+); FP16 works on
        any CUDA device with GradScaler. On CPU both fall back to FP32.
    """
    if device == "cpu" or precision == "fp32":
        return None
    if not device.startswith("cuda"):
        return None
    if precision == "bf16":
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16  # graceful fallback for pre-Ampere GPUs
    if precision == "fp16":
        return torch.float16
    return None


@dataclass
class TrainingCheckpoint:
    """Training checkpoint data"""
    model_state_dict: Dict[str, Any]
    optimizer_state_dict: Dict[str, Any]
    scheduler_state_dict: Optional[Dict[str, Any]] = None
    epoch: int = 0
    step: int = 0
    train_loss: float = 0.0
    val_loss: float = 0.0
    config: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    model_status: str = ModelStatus.UNTRAINED.value
    rng_state: Optional[Dict[str, Any]] = None
    tokenizer_path: str = ""
    grad_scaler_state_dict: Optional[Dict[str, Any]] = None


class CheckpointManager:
    """
    Safe checkpoint management for NexusAI Core-01.
    
    Uses separate directory from legacy model.
    """
    
    def __init__(self, checkpoint_dir: str, model_name: str = "nexusai-core-01"):
        self.checkpoint_dir = checkpoint_dir
        self.model_name = model_name
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(
        self,
        checkpoint: TrainingCheckpoint,
        filename: str = "checkpoint.pt"
    ) -> str:
        """
        Save checkpoint safely.
        
        Args:
            checkpoint: TrainingCheckpoint instance
            filename: Checkpoint filename
        
        Returns:
            Full path to saved checkpoint
        """
        from datetime import datetime
        checkpoint.timestamp = datetime.now().isoformat()
        
        checkpoint_path = os.path.join(self.checkpoint_dir, filename)
        
        # Backup existing checkpoint if it exists — use a non-destructive COPY
        # (not rename) so a failed save can never destroy the last good file.
        if os.path.exists(checkpoint_path):
            backup_path = checkpoint_path + ".backup"
            import shutil
            shutil.copy2(checkpoint_path, backup_path)

        # Save new checkpoint atomically: write to temp file, then rename.
        # os.replace overwrites the destination atomically on the same volume,
        # so a crash mid-write leaves either the old or the new file intact.
        tmp_path = checkpoint_path + ".tmp"
        torch.save(checkpoint.__dict__, tmp_path)
        os.replace(tmp_path, checkpoint_path)

        return checkpoint_path
    
    def load_checkpoint(self, filename: str = "checkpoint.pt") -> TrainingCheckpoint:
        """
        Load checkpoint.
        
        Args:
            filename: Checkpoint filename
        
        Returns:
            TrainingCheckpoint instance
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, filename)
        
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        # weights_only=False is required because checkpoints contain NumPy RNG
        # state and optimizer state dicts, which are not in the safe-globals
        # allowlist. These are self-produced artifacts, never third-party files.
        data = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        return TrainingCheckpoint(**data)
    
    def list_checkpoints(self) -> List[str]:
        """List all checkpoints in directory"""
        checkpoints = []
        for file in os.listdir(self.checkpoint_dir):
            if file.endswith(".pt") and not file.endswith(".backup"):
                checkpoints.append(file)
        return sorted(checkpoints)


class PretrainingEngine:
    """
    Pretraining engine for NexusAI Core-01.
    
    Implements next-token prediction pretraining with AdamW optimizer.
    """
    
    def __init__(
        self,
        model: NexusAICore01,
        config: NexusAICore01Config,
        checkpoint_dir: str,
        tokenizer_path: Optional[str] = None
    ):
        self.model = model
        self.config = config
        self.checkpoint_manager = CheckpointManager(checkpoint_dir, config.model_name)

        # Tokenizer provenance: explicit arg wins, else config value
        self.tokenizer_path = (
            tokenizer_path
            if tokenizer_path is not None
            else getattr(config, "tokenizer_path", "") or ""
        )

        # Setup optimizer
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # Setup learning rate scheduler (linear warmup)
        self.scheduler = None  # Will be initialized if warmup is used
        
        # Resolve device once; reuse for AMP decision and training
        self.device = resolve_device(config.device)

        # Mixed precision setup
        self.amp_dtype = resolve_amp_dtype(config.precision, self.device)
        self.use_amp = self.amp_dtype is not None
        # GradScaler is only needed for FP16 (loss scaling); BF16 does not need it
        self.scaler = (
            torch.amp.GradScaler("cuda")
            if self.use_amp and self.amp_dtype == torch.float16
            else None
        )

        # Gradient accumulation
        self.grad_accum_steps = max(1, config.gradient_accumulation_steps)

        # Training state
        self.current_epoch = 0
        self.current_step = 0
        self.train_losses = []
        self.val_losses = []
    
    def setup_scheduler(self, num_training_steps: int):
        """Setup learning rate scheduler with warmup"""
        def lr_lambda(current_step: int):
            if current_step < self.config.warmup_steps:
                return float(current_step) / float(max(1, self.config.warmup_steps))
            return 1.0
        
        self.scheduler = LambdaLR(self.optimizer, lr_lambda)
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        device: Optional[str] = None,
        on_step: Optional[Any] = None
    ) -> float:
        """
        Train for one epoch with optional AMP and gradient accumulation.

        Gradient accumulation: gradients from `gradient_accumulation_steps`
        micro-batches are summed (scaled by 1/N inside backward via loss/N)
        before a single optimizer step. The effective batch size is
        `config.batch_size * gradient_accumulation_steps`.

        Args:
            train_loader: Training data loader (micro-batches)
            device: Device to train on; defaults to config.device resolved
            on_step: Optional callback invoked after each optimizer step as
                ``on_step(engine, epoch, optimizer_step, micro_batch_idx,
                loss_value)``. May raise an exception to abort the epoch
                early (e.g. a max-steps limit); the exception propagates.

        Returns:
            Average training loss (per micro-batch)
        """
        device = device or self.device
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        accum_steps = self.grad_accum_steps
        num_batches_total = len(train_loader)

        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            targets = batch["targets"].to(device)

            is_accum_step = (batch_idx + 1) % accum_steps != 0
            is_last_batch = batch_idx == num_batches_total - 1

            # Clear gradients only at the start of each accumulation group
            if batch_idx % accum_steps == 0:
                self.optimizer.zero_grad(set_to_none=True)

            # Actual number of micro-batches in THIS accumulation group.
            # The final group may be smaller than accum_steps; dividing by the
            # true group size gives mathematically correct gradient averaging.
            group_start = (batch_idx // accum_steps) * accum_steps
            group_end = min(group_start + accum_steps, num_batches_total)
            group_size = group_end - group_start

            # Forward pass (AMP autocast when enabled)
            if self.use_amp:
                with torch.autocast(
                    device_type="cuda" if device.startswith("cuda") else "cpu",
                    dtype=self.amp_dtype,
                    enabled=device.startswith("cuda")
                ):
                    loss = self.model(input_ids, targets)
            else:
                loss = self.model(input_ids, targets)

            # Scale loss so accumulated gradients equal the true group mean
            scaled_loss = loss / group_size

            # Backward pass (with GradScaler for FP16)
            if self.scaler is not None:
                self.scaler.scale(scaled_loss).backward()
            else:
                scaled_loss.backward()

            # Optimizer step only on accumulation boundaries or final batch
            if not is_accum_step or is_last_batch:
                if self.scaler is not None:
                    if self.config.grad_clip > 0:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(), self.config.grad_clip
                        )
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    if self.config.grad_clip > 0:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(), self.config.grad_clip
                        )
                    self.optimizer.step()

                if self.scheduler is not None:
                    self.scheduler.step()

                self.current_step += 1

                if on_step is not None:
                    on_step(
                        self, self.current_epoch, self.current_step,
                        batch_idx, loss.item()
                    )

            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches

    def validate(
        self,
        val_loader: DataLoader,
        device: Optional[str] = None
    ) -> float:
        """
        Validate model.
        
        Args:
            val_loader: Validation data loader
            device: Device to validate on
        
        Returns:
            Average validation loss
        """
        device = device or self.device
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                targets = batch["targets"].to(device)
                
                if self.use_amp:
                    with torch.autocast(
                        device_type="cuda" if device.startswith("cuda") else "cpu",
                        dtype=self.amp_dtype,
                        enabled=device.startswith("cuda")
                    ):
                        loss = self.model(input_ids, targets)
                else:
                    loss = self.model(input_ids, targets)
                
                total_loss += loss.item()
                num_batches += 1
        
        return total_loss / num_batches
    
    def save_checkpoint(
        self,
        epoch: int,
        train_loss: float,
        val_loss: float,
        filename: str = "checkpoint.pt",
        finalize: bool = False
    ) -> str:
        """
        Save training checkpoint.

        Args:
            epoch: Current epoch
            train_loss: Training loss
            val_loss: Validation loss
            filename: Checkpoint filename
            finalize: If True, mark the checkpoint PRETRAINING_COMPLETED.
                Must only be used when the configured pretraining objective
                genuinely finished (all epochs done, or an explicitly
                configured max-step budget reached). Never set this on
                interruption or failure paths.

        Returns:
            Path to saved checkpoint
        """
        checkpoint = TrainingCheckpoint(
            model_state_dict=self.model.state_dict(),
            optimizer_state_dict=self.optimizer.state_dict(),
            scheduler_state_dict=self.scheduler.state_dict() if self.scheduler else None,
            epoch=epoch,
            step=self.current_step,
            train_loss=train_loss,
            val_loss=val_loss,
            config=self.config.to_dict(),
            model_status=(
                ModelStatus.PRETRAINING_COMPLETED.value if finalize
                else ModelStatus.PRETRAINING_IN_PROGRESS.value
            ),
            rng_state=get_rng_state(),
            tokenizer_path=self.tokenizer_path,
            grad_scaler_state_dict=(
                self.scaler.state_dict() if self.scaler is not None else None
            )
        )

        return self.checkpoint_manager.save_checkpoint(checkpoint, filename)
    
    def load_checkpoint(self, filename: str = "checkpoint.pt") -> None:
        """
        Load training checkpoint and restore RNG states when present.
        
        Args:
            filename: Checkpoint filename
        """
        checkpoint = self.checkpoint_manager.load_checkpoint(filename)

        if not getattr(checkpoint, "tokenizer_path", ""):
            print(
                "Warning: checkpoint has no tokenizer_path; "
                "tokenizer provenance unavailable. Ensure the correct "
                "SentencePiece model is used before inference."
            )

        self.model.load_state_dict(checkpoint.model_state_dict)
        self.optimizer.load_state_dict(checkpoint.optimizer_state_dict)

        if checkpoint.scheduler_state_dict and self.scheduler is not None:
            self.scheduler.load_state_dict(checkpoint.scheduler_state_dict)

        if checkpoint.rng_state:
            set_rng_state(checkpoint.rng_state)

        # GradScaler state: absent in checkpoints saved before Phase 5.1 —
        # skip silently so legacy checkpoints remain loadable.
        scaler_state = getattr(checkpoint, "grad_scaler_state_dict", None)
        if scaler_state and self.scaler is not None:
            self.scaler.load_state_dict(scaler_state)

        self.current_epoch = checkpoint.epoch
        self.current_step = checkpoint.step
        self.train_losses = checkpoint.config.get("train_losses", [])
        self.val_losses = checkpoint.config.get("val_losses", [])


# Model statuses that prove a checkpoint contains actually-trained weights.
# UNTRAINED / RANDOMLY_INITIALIZED / PRETRAINING_IN_PROGRESS are rejected:
# the first two are random init, the third means pretraining never finished.
PRETRAINED_STATUSES = {
    ModelStatus.PRETRAINING_COMPLETED.value,
    ModelStatus.INSTRUCTION_TUNING_IN_PROGRESS.value,
    ModelStatus.INSTRUCTION_TUNING_COMPLETED.value,
    ModelStatus.PRODUCTION_READY.value,
}

# Architecture fields that must match between checkpoint config and current
# config, otherwise the state dict cannot belong to this model.
ARCHITECTURE_FIELDS = ("vocab_size", "d_model", "n_layers", "n_heads", "d_ff", "max_len")


def validate_pretrained_checkpoint(
    checkpoint_path: str,
    config: NexusAICore01Config
) -> Dict[str, Any]:
    """
    Validate that a checkpoint file represents a genuinely pretrained
    NexusAI Core-01 model that is safe to use as an SFT starting point.

    Checks (any failure raises ValueError with an actionable message):
      1. File exists and is readable.
      2. Contains a model_state_dict with tensor weights.
      3. model_status is a completed-training status (not UNTRAINED etc.).
      4. Checkpoint config metadata exists and architecture fields match.
      5. Special-token IDs are compatible.

    Args:
        checkpoint_path: Path to the .pt checkpoint file.
        config: Current model configuration to validate against.

    Returns:
        The loaded checkpoint dict.

    Raises:
        ValueError: If the checkpoint fails any validation.
        FileNotFoundError: If the file does not exist.
    """
    if not checkpoint_path:
        raise ValueError(
            "SFT requires an explicit pretrained checkpoint path. "
            "Pass pretrained_checkpoint='path/to/pretrained.pt' to "
            "InstructionTuningEngine. Refusing to start SFT from random weights."
        )
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"Pretrained checkpoint not found: {checkpoint_path}"
        )

    # Trusted self-produced checkpoint only — never point this at foreign files.
    data = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid checkpoint format in {checkpoint_path}: expected dict."
        )

    model_state = data.get("model_state_dict")
    if not isinstance(model_state, dict) or not model_state:
        raise ValueError(
            f"Checkpoint {checkpoint_path} has no model_state_dict."
        )
    if not any(torch.is_tensor(v) for v in model_state.values()):
        raise ValueError(
            f"Checkpoint {checkpoint_path} model_state_dict contains no tensors."
        )

    # Status gate: must prove completed training, not random init.
    status = data.get("model_status", "")
    if status not in PRETRAINED_STATUSES:
        raise ValueError(
            f"Checkpoint {checkpoint_path} is not pretrained "
            f"(model_status={status!r}). SFT requires a checkpoint with "
            f"status one of {sorted(PRETRAINED_STATUSES)}."
        )

    # Metadata gate: config must exist and architecture must match.
    ckpt_config = data.get("config") or {}
    if not ckpt_config:
        raise ValueError(
            f"Checkpoint {checkpoint_path} lacks config metadata; "
            "cannot verify architecture compatibility. Rejected under the "
            "strict-metadata policy (old checkpoints without config are unsafe)."
        )
    mismatches = []
    for field in ARCHITECTURE_FIELDS:
        ckpt_val = ckpt_config.get(field)
        cur_val = getattr(config, field, None)
        if ckpt_val is not None and cur_val is not None and ckpt_val != cur_val:
            mismatches.append(f"{field}: ckpt={ckpt_val} vs config={cur_val}")
    if mismatches:
        raise ValueError(
            f"Checkpoint {checkpoint_path} architecture mismatch: "
            + "; ".join(mismatches)
        )

    # Special-token compatibility (only checked when both sides declare them).
    for tok_field in ("pad_id", "unk_id", "bos_id", "eos_id"):
        ckpt_val = ckpt_config.get(tok_field)
        cur_val = getattr(config, tok_field, None)
        if ckpt_val is not None and cur_val is not None and ckpt_val != cur_val:
            raise ValueError(
                f"Checkpoint {checkpoint_path} tokenizer special-token "
                f"mismatch: {tok_field} ckpt={ckpt_val} vs config={cur_val}"
            )

    # Tokenizer vocabulary compatibility: checkpoint tokenizer_path (if any)
    # is informational; vocab_size equality is enforced via config above.
    return data


class InstructionTuningEngine:
    """
    Instruction fine-tuning engine for NexusAI Core-01.
    
    Separate from pretraining to avoid confusion.
    CODE-ENFORCED GATE: requires a validated pretrained checkpoint; random
    initialization is rejected before any SFT training can occur.
    """
    
    def __init__(
        self,
        model: NexusAICore01,
        config: NexusAICore01Config,
        checkpoint_dir: str,
        tokenizer_path: Optional[str] = None,
        pretrained_checkpoint: Optional[str] = None
    ):
        # Gate: validate and load pretrained weights BEFORE building optimizer.
        if pretrained_checkpoint is None:
            raise ValueError(
                "InstructionTuningEngine requires pretrained_checkpoint="
                "'path/to/pretrained.pt'. SFT on random weights is not allowed."
            )
        ckpt_data = validate_pretrained_checkpoint(
            pretrained_checkpoint, config
        )
        # Load pretrained weights into the model (strict: catches any
        # architecture mismatch the config check might have missed).
        model.load_state_dict(ckpt_data["model_state_dict"], strict=True)

        self.model = model
        self.config = config
        self.pretrained_checkpoint = pretrained_checkpoint
        self.checkpoint_manager = CheckpointManager(
            os.path.join(checkpoint_dir, "instruction_tuning"),
            config.model_name
        )

        self.tokenizer_path = (
            tokenizer_path
            if tokenizer_path is not None
            else getattr(config, "tokenizer_path", "") or ""
        )
        
        # Setup optimizer (usually lower LR for fine-tuning)
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.learning_rate * 0.1,  # 10x lower LR for fine-tuning
            weight_decay=config.weight_decay
        )

        # Mixed precision + device (same rules as PretrainingEngine)
        self.device = resolve_device(config.device)
        self.amp_dtype = resolve_amp_dtype(config.precision, self.device)
        self.use_amp = self.amp_dtype is not None
        self.scaler = (
            torch.amp.GradScaler("cuda")
            if self.use_amp and self.amp_dtype == torch.float16
            else None
        )
        self.grad_accum_steps = max(1, config.gradient_accumulation_steps)

        self.current_epoch = 0
        self.current_step = 0

    def train_epoch(
        self,
        train_loader: DataLoader,
        device: Optional[str] = None
    ) -> float:
        """
        Train for one epoch on instruction data.
        
        Supports the same AMP and gradient accumulation as pretraining.
        
        Args:
            train_loader: Training data loader
            device: Device to train on
        
        Returns:
            Average training loss
        """
        device = device or self.device
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        accum_steps = self.grad_accum_steps
        num_batches_total = len(train_loader)

        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            targets = batch["targets"].to(device)

            is_accum_step = (batch_idx + 1) % accum_steps != 0
            is_last_batch = batch_idx == num_batches_total - 1

            if batch_idx % accum_steps == 0:
                self.optimizer.zero_grad(set_to_none=True)

            # Actual group size for correct gradient averaging
            group_start = (batch_idx // accum_steps) * accum_steps
            group_end = min(group_start + accum_steps, num_batches_total)
            group_size = group_end - group_start

            if self.use_amp:
                with torch.autocast(
                    device_type="cuda" if device.startswith("cuda") else "cpu",
                    dtype=self.amp_dtype,
                    enabled=device.startswith("cuda")
                ):
                    loss = self.model(input_ids, targets)
            else:
                loss = self.model(input_ids, targets)

            scaled_loss = loss / group_size

            if self.scaler is not None:
                self.scaler.scale(scaled_loss).backward()
            else:
                scaled_loss.backward()

            if not is_accum_step or is_last_batch:
                if self.scaler is not None:
                    if self.config.grad_clip > 0:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(), self.config.grad_clip
                        )
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    if self.config.grad_clip > 0:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(), self.config.grad_clip
                        )
                    self.optimizer.step()

                self.current_step += 1

            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches
    
    def save_checkpoint(
        self,
        epoch: int,
        train_loss: float,
        val_loss: float,
        filename: str = "checkpoint.pt"
    ) -> str:
        """Save instruction tuning checkpoint"""
        checkpoint = TrainingCheckpoint(
            model_state_dict=self.model.state_dict(),
            optimizer_state_dict=self.optimizer.state_dict(),
            epoch=epoch,
            step=self.current_step,
            train_loss=train_loss,
            val_loss=val_loss,
            config=self.config.to_dict(),
            model_status=ModelStatus.INSTRUCTION_TUNING_IN_PROGRESS.value,
            rng_state=get_rng_state(),
            tokenizer_path=self.tokenizer_path,
            grad_scaler_state_dict=(
                self.scaler.state_dict() if self.scaler is not None else None
            )
        )

        return self.checkpoint_manager.save_checkpoint(checkpoint, filename)

    def load_checkpoint(self, filename: str = "checkpoint.pt") -> None:
        """Load instruction tuning checkpoint and restore RNG states."""
        checkpoint = self.checkpoint_manager.load_checkpoint(filename)

        if not getattr(checkpoint, "tokenizer_path", ""):
            print(
                "Warning: checkpoint has no tokenizer_path; "
                "tokenizer provenance unavailable."
            )

        self.model.load_state_dict(checkpoint.model_state_dict)
        self.optimizer.load_state_dict(checkpoint.optimizer_state_dict)

        scaler_state = getattr(checkpoint, "grad_scaler_state_dict", None)
        if scaler_state and self.scaler is not None:
            self.scaler.load_state_dict(scaler_state)

        if checkpoint.rng_state:
            set_rng_state(checkpoint.rng_state)

        self.current_epoch = checkpoint.epoch
        self.current_step = checkpoint.step


if __name__ == "__main__":
    # Test training engine initialization (no actual training)
    config = NexusAICore01Config()
    model = NexusAICore01(config)
    
    checkpoint_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "models",
        "nexusai-core-01",
        "checkpoints"
    )
    
    engine = PretrainingEngine(model, config, checkpoint_dir)
    
    print(f"Training engine initialized")
    print(f"Model parameters: {model.count_parameters():,}")
    print(f"Checkpoint directory: {checkpoint_dir}")
    print(f"Model status: {config.model_status.value}")
