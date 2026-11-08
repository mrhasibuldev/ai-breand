"""
NexusAI Core-01 Model Configuration

Centralized configuration for NexusAI Core-01 Independent Transformer Language Model.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class ModelStatus(Enum):
    """Model training and deployment status"""
    UNTRAINED = "UNTRAINED"
    RANDOMLY_INITIALIZED = "RANDOMLY_INITIALIZED"
    PRETRAINING_IN_PROGRESS = "PRETRAINING_IN_PROGRESS"
    PRETRAINING_COMPLETED = "PRETRAINING_COMPLETED"
    INSTRUCTION_TUNING_IN_PROGRESS = "INSTRUCTION_TUNING_IN_PROGRESS"
    INSTRUCTION_TUNING_COMPLETED = "INSTRUCTION_TUNING_COMPLETED"
    PRODUCTION_READY = "PRODUCTION_READY"


@dataclass
class NexusAICore01Config:
    """
    NexusAI Core-01 Model Configuration
    
    This configuration defines the architecture and behavior of NexusAI Core-01,
    the first officially independent neural language model for NexusAI.
    
    Model Identity:
    - Name: NexusAI Core-01
    - Family: NexusAI Core Series
    - Architecture: Independent Transformer Language Model
    - Origin: Built from scratch for NexusAI
    - Initial State: UNTRAINED - RANDOMLY INITIALIZED
    """
    
    # Model Identity
    model_name: str = "nexusai-core-01"
    model_family: str = "NexusAI Core Series"
    model_version: str = "1.0.0"
    architecture_type: str = "Independent Transformer Language Model"
    model_status: ModelStatus = ModelStatus.UNTRAINED
    
    # Architecture Configuration
    vocab_size: int = 8000  # Compatible with existing 8K BPE tokenizer
    d_model: int = 256  # Embedding dimension
    n_layers: int = 6  # Number of Transformer layers
    n_heads: int = 8  # Number of attention heads
    d_ff: int = 1024  # Feed-forward dimension
    max_len: int = 512  # Context length (4x legacy model)
    dropout: float = 0.1
    
    # Positional Encoding Strategy
    positional_encoding: str = "sinusoidal"  # Options: "sinusoidal", "rope"
    
    # Special Token IDs (must match tokenizer)
    pad_id: int = 0
    unk_id: int = 1
    bos_id: int = 2
    eos_id: int = 3
    
    # Weight Initialization
    weight_init_std: float = 0.02
    bias_init: float = 0.0
    
    # Inference Configuration
    max_new_tokens: int = 100
    temperature: float = 0.8
    top_k: int = 50
    top_p: float = 0.9
    repetition_penalty: float = 1.2
    
    # Training Configuration (for future use)
    batch_size: int = 4  # Micro-batch size per forward/backward
    learning_rate: float = 0.0003
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    epochs: int = 3
    warmup_steps: int = 100

    # Mixed Precision (AMP) Configuration
    # Options: "fp32" (default, safest), "fp16" (CUDA only, uses GradScaler), "bf16" (CUDA Ampere+)
    precision: str = "fp32"

    # Gradient Accumulation
    # Effective batch size = batch_size * gradient_accumulation_steps
    gradient_accumulation_steps: int = 1

    # Checkpointing cadence
    checkpoint_interval_steps: int = 500
    eval_interval_steps: int = 500

    # Resume support: path to a checkpoint file to resume from (empty = fresh start)
    resume_checkpoint: str = ""

    # Tokenizer reference: path to the SentencePiece .model file used with this
    # model. Recorded into checkpoints for provenance. Empty = unknown.
    tokenizer_path: str = ""

    # Device Configuration
    device: str = "cpu"  # Will be set to "cuda" if available
    
    # Random Seed for Reproducibility
    random_seed: int = 42
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters"""
        # Validate architecture dimensions
        assert self.d_model % self.n_heads == 0, \
            f"d_model ({self.d_model}) must be divisible by n_heads ({self.n_heads})"
        
        assert self.vocab_size > 0, "vocab_size must be positive"
        assert self.d_model > 0, "d_model must be positive"
        assert self.n_layers > 0, "n_layers must be positive"
        assert self.n_heads > 0, "n_heads must be positive"
        assert self.d_ff > 0, "d_ff must be positive"
        assert self.max_len > 0, "max_len must be positive"
        
        # Validate special token IDs
        assert self.pad_id >= 0, "pad_id must be non-negative"
        assert self.unk_id >= 0, "unk_id must be non-negative"
        assert self.bos_id >= 0, "bos_id must be non-negative"
        assert self.eos_id >= 0, "eos_id must be non-negative"
        
        # Validate that special tokens are unique
        special_tokens = {self.pad_id, self.unk_id, self.bos_id, self.eos_id}
        assert len(special_tokens) == 4, "Special token IDs must be unique"
        
        # Validate training parameters
        assert 0 < self.learning_rate < 1, "learning_rate must be between 0 and 1"
        assert self.weight_decay >= 0, "weight_decay must be non-negative"
        assert self.grad_clip > 0, "grad_clip must be positive"
        assert self.epochs > 0, "epochs must be positive"

        # Validate mixed precision
        assert self.precision in ("fp32", "fp16", "bf16"), \
            f"precision must be one of fp32/fp16/bf16, got {self.precision}"

        # Validate gradient accumulation
        assert self.gradient_accumulation_steps >= 1, \
            "gradient_accumulation_steps must be >= 1"
        assert self.batch_size >= 1, "batch_size must be >= 1"
        assert self.checkpoint_interval_steps >= 1, \
            "checkpoint_interval_steps must be >= 1"
        assert self.eval_interval_steps >= 1, \
            "eval_interval_steps must be >= 1"
    
    def estimated_parameter_count(self) -> int:
        """
        Estimate total parameter count based on configuration.
        
        Returns:
            Estimated number of trainable parameters
        """
        # Token embedding: vocab_size * d_model
        token_emb = self.vocab_size * self.d_model
        
        # Positional encoding: max_len * d_model (not registered as parameters in implementation)
        pos_emb = 0  # Positional encoding uses buffer, not parameters
        
        # Per layer parameters
        # Attention: 4 * (d_model * d_model) + 4 * d_model (Q, K, V, O projections + biases)
        attn_per_layer = 4 * (self.d_model * self.d_model) + 4 * self.d_model
        
        # FFN: 2 linear layers + biases (d_ff bias for layer1, d_model bias for layer2)
        ffn_per_layer = 2 * (self.d_model * self.d_ff) + self.d_ff + self.d_model
        
        # LayerNorm: 2 * 2 * d_model (2 LayerNorms per layer, each with weight and bias)
        ln_per_layer = 2 * 2 * self.d_model
        
        # Total per layer
        per_layer = attn_per_layer + ffn_per_layer + ln_per_layer
        
        # All layers
        all_layers = self.n_layers * per_layer
        
        # Output layer: d_model * vocab_size + vocab_size
        output_layer = self.d_model * self.vocab_size + self.vocab_size
        
        total = token_emb + pos_emb + all_layers + output_layer
        return total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "model_name": self.model_name,
            "model_family": self.model_family,
            "model_version": self.model_version,
            "architecture_type": self.architecture_type,
            "model_status": self.model_status.value,
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
            "n_layers": self.n_layers,
            "n_heads": self.n_heads,
            "d_ff": self.d_ff,
            "max_len": self.max_len,
            "dropout": self.dropout,
            "positional_encoding": self.positional_encoding,
            "pad_id": self.pad_id,
            "unk_id": self.unk_id,
            "bos_id": self.bos_id,
            "eos_id": self.eos_id,
            "weight_init_std": self.weight_init_std,
            "bias_init": self.bias_init,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "grad_clip": self.grad_clip,
            "epochs": self.epochs,
            "warmup_steps": self.warmup_steps,
            "precision": self.precision,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "effective_batch_size": self.batch_size * self.gradient_accumulation_steps,
            "checkpoint_interval_steps": self.checkpoint_interval_steps,
            "eval_interval_steps": self.eval_interval_steps,
            "resume_checkpoint": self.resume_checkpoint,
            "tokenizer_path": self.tokenizer_path,
            "device": self.device,
            "random_seed": self.random_seed,
            "estimated_parameters": self.estimated_parameter_count()
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "NexusAICore01Config":
        """Create configuration from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})


# Default configuration instance
DEFAULT_CONFIG = NexusAICore01Config()
