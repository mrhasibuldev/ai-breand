"""
Checkpoint Management

Save and load model checkpoints.
"""

import torch
import os
from typing import Dict, Any


class CheckpointManager:
    """
    Manage model checkpoints.
    """

    def __init__(self, checkpoint_dir: str):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to save checkpoints
        """
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        loss: float,
        metadata: Dict[str, Any] = None,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Save checkpoint.

        Args:
            model: Model to save
            optimizer: Optimizer state
            epoch: Current epoch
            loss: Current loss
            metadata: Additional metadata
            config: Training configuration for reproducibility

        Returns:
            Path to saved checkpoint
        """
        checkpoint = {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch,
            "loss": loss,
            "metadata": metadata or {},
            "config": config or {}
        }

        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.pt")
        torch.save(checkpoint, checkpoint_path)

        print(f"Checkpoint saved to {checkpoint_path}")
        return checkpoint_path

    def load(self, checkpoint_path: str, model: torch.nn.Module, optimizer: torch.optim.Optimizer = None) -> Dict[str, Any]:
        """
        Load checkpoint.

        Args:
            checkpoint_path: Path to checkpoint
            model: Model to load weights into
            optimizer: Optimizer to load state into (optional)

        Returns:
            Checkpoint metadata
        """
        checkpoint = torch.load(checkpoint_path, map_location="cpu")

        model.load_state_dict(checkpoint["model_state_dict"])

        if optimizer is not None and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        print(f"Checkpoint loaded from {checkpoint_path}")

        return {
            "epoch": checkpoint.get("epoch", 0),
            "loss": checkpoint.get("loss", 0.0),
            "metadata": checkpoint.get("metadata", {})
        }

    def get_latest_checkpoint(self) -> str:
        """
        Get path to latest checkpoint.

        Returns:
            Path to latest checkpoint or None if no checkpoints exist
        """
        checkpoints = [
            f for f in os.listdir(self.checkpoint_dir)
            if f.startswith("checkpoint_epoch_") and f.endswith(".pt")
        ]

        if not checkpoints:
            return None

        # Sort by epoch number
        checkpoints.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

        return os.path.join(self.checkpoint_dir, checkpoints[-1])
