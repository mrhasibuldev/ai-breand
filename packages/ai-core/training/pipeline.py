"""
Training Pipeline

Main training loop and optimization logic.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Optional
from .dataset import TextDataset
from .checkpoint import CheckpointManager


class TrainingPipeline:
    """
    Training pipeline for neural network training.
    """

    def __init__(
        self,
        model: nn.Module,
        tokenizer,
        checkpoint_dir: str = "models/checkpoints",
        device: str = "cpu"
    ):
        """
        Initialize training pipeline.

        Args:
            model: Model to train
            tokenizer: Tokenizer instance
            checkpoint_dir: Directory for checkpoints
            device: Device to train on
        """
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.checkpoint_manager = CheckpointManager(checkpoint_dir)

    def train(
        self,
        train_dataset: TextDataset,
        val_dataset: TextDataset,
        epochs: int = 10,
        batch_size: int = 8,
        learning_rate: float = 0.001,
        weight_decay: float = 0.01,
        grad_clip: float = 1.0,
        checkpoint_freq: int = 1,
        resume_from: Optional[str] = None,
        save_config: bool = True
    ) -> Dict[str, float]:
        """
        Train the model.

        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            weight_decay: Weight decay for regularization
            grad_clip: Gradient clipping threshold
            checkpoint_freq: Save checkpoint every N epochs
            resume_from: Path to checkpoint to resume from
            save_config: Whether to save training configuration

        Returns:
            Training metrics
        """
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        # Setup optimizer
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )

        # Save training configuration for reproducibility
        training_config = {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
            "grad_clip": grad_clip,
            "vocab_size": self.tokenizer.get_vocab_size(),
            "model_params": self.model.count_parameters()
        }

        start_epoch = 0

        # Resume from checkpoint if specified
        if resume_from:
            metadata = self.checkpoint_manager.load(resume_from, self.model, optimizer)
            start_epoch = metadata["epoch"] + 1
            print(f"Resuming from epoch {start_epoch}")

        # Training loop
        train_losses = []
        val_losses = []

        for epoch in range(start_epoch, epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")

            # Train
            train_loss = self._train_epoch(train_loader, optimizer, grad_clip)
            train_losses.append(train_loss)

            # Validate
            val_loss = self._validate_epoch(val_loader)
            val_losses.append(val_loss)

            print(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

            # Save checkpoint
            if (epoch + 1) % checkpoint_freq == 0:
                self.checkpoint_manager.save(
                    self.model,
                    optimizer,
                    epoch + 1,
                    val_loss,
                    metadata={
                        "train_loss": train_loss,
                        "val_loss": val_loss
                    },
                    config=training_config if save_config else None
                )

        return {
            "final_train_loss": train_losses[-1],
            "final_val_loss": val_losses[-1],
            "train_losses": train_losses,
            "val_losses": val_losses
        }

    def _train_epoch(
        self,
        train_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        grad_clip: float
    ) -> float:
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            optimizer: Optimizer
            grad_clip: Gradient clipping threshold

        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        for batch in train_loader:
            # Move to device
            input_ids = batch["input_ids"].to(self.device)
            targets = batch["targets"].to(self.device)

            # Forward pass
            optimizer.zero_grad()
            loss = self.model(input_ids, targets)

            # Backward pass
            loss.backward()

            # Gradient clipping
            if grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), grad_clip)

            # Optimizer step
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches

    def _validate_epoch(self, val_loader: DataLoader) -> float:
        """
        Validate for one epoch.

        Args:
            val_loader: Validation data loader

        Returns:
            Average validation loss
        """
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in val_loader:
                # Move to device
                input_ids = batch["input_ids"].to(self.device)
                targets = batch["targets"].to(self.device)

                # Forward pass
                loss = self.model(input_ids, targets)

                total_loss += loss.item()
                num_batches += 1

        return total_loss / num_batches
