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
        
        # Backup existing checkpoint if it exists
        if os.path.exists(checkpoint_path):
            backup_path = checkpoint_path + ".backup"
            os.rename(checkpoint_path, backup_path)
        
        # Save new checkpoint
        torch.save(checkpoint.__dict__, checkpoint_path)
        
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
        
        data = torch.load(checkpoint_path, map_location="cpu")
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
        checkpoint_dir: str
    ):
        self.model = model
        self.config = config
        self.checkpoint_manager = CheckpointManager(checkpoint_dir, config.model_name)
        
        # Setup optimizer
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # Setup learning rate scheduler (linear warmup)
        self.scheduler = None  # Will be initialized if warmup is used
        
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
        device: str = "cpu"
    ) -> float:
        """
        Train for one epoch.
        
        Args:
            train_loader: Training data loader
            device: Device to train on
        
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            targets = batch["targets"].to(device)
            
            # Forward pass
            loss = self.model(input_ids, targets)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            if self.config.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.grad_clip)
            
            # Optimizer step
            self.optimizer.step()
            
            if self.scheduler is not None:
                self.scheduler.step()
            
            self.current_step += 1
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / num_batches
    
    def validate(
        self,
        val_loader: DataLoader,
        device: str = "cpu"
    ) -> float:
        """
        Validate model.
        
        Args:
            val_loader: Validation data loader
            device: Device to validate on
        
        Returns:
            Average validation loss
        """
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                targets = batch["targets"].to(device)
                
                loss = self.model(input_ids, targets)
                
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
        """
        Save training checkpoint.
        
        Args:
            epoch: Current epoch
            train_loss: Training loss
            val_loss: Validation loss
            filename: Checkpoint filename
        
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
            model_status=ModelStatus.PRETRAINING_IN_PROGRESS.value
        )
        
        return self.checkpoint_manager.save_checkpoint(checkpoint, filename)
    
    def load_checkpoint(self, filename: str = "checkpoint.pt") -> None:
        """
        Load training checkpoint.
        
        Args:
            filename: Checkpoint filename
        """
        checkpoint = self.checkpoint_manager.load_checkpoint(filename)
        
        self.model.load_state_dict(checkpoint.model_state_dict)
        self.optimizer.load_state_dict(checkpoint.optimizer_state_dict)
        
        if checkpoint.scheduler_state_dict and self.scheduler is not None:
            self.scheduler.load_state_dict(checkpoint.scheduler_state_dict)
        
        self.current_epoch = checkpoint.epoch
        self.current_step = checkpoint.step
        self.train_losses = checkpoint.config.get("train_losses", [])
        self.val_losses = checkpoint.config.get("val_losses", [])


class InstructionTuningEngine:
    """
    Instruction fine-tuning engine for NexusAI Core-01.
    
    Separate from pretraining to avoid confusion.
    """
    
    def __init__(
        self,
        model: NexusAICore01,
        config: NexusAICore01Config,
        checkpoint_dir: str
    ):
        self.model = model
        self.config = config
        self.checkpoint_manager = CheckpointManager(
            os.path.join(checkpoint_dir, "instruction_tuning"),
            config.model_name
        )
        
        # Setup optimizer (usually lower LR for fine-tuning)
        self.optimizer = AdamW(
            model.parameters(),
            lr=config.learning_rate * 0.1,  # 10x lower LR for fine-tuning
            weight_decay=config.weight_decay
        )
        
        self.current_epoch = 0
        self.current_step = 0
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        device: str = "cpu"
    ) -> float:
        """
        Train for one epoch on instruction data.
        
        Args:
            train_loader: Training data loader
            device: Device to train on
        
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            targets = batch["targets"].to(device)
            
            loss = self.model(input_ids, targets)
            
            self.optimizer.zero_grad()
            loss.backward()
            
            if self.config.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.grad_clip)
            
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
            model_status=ModelStatus.INSTRUCTION_TUNING_IN_PROGRESS.value
        )
        
        return self.checkpoint_manager.save_checkpoint(checkpoint, filename)


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
