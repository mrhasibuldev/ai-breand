"""
NexusAI Core-01 Package

NexusAI Core-01: Independent Transformer Language Model
Built from scratch for NexusAI.

Model Status: UNTRAINED - RANDOMLY INITIALIZED
"""

from .transformer import NexusAICore01
from .tokenizer_interface import NexusAITokenizer, create_default_tokenizer
from .dataset import (
    TextDataset,
    TokenizedDataset,
    DatasetLoader,
    InstructionDataset
)
from .training import (
    PretrainingEngine,
    InstructionTuningEngine,
    CheckpointManager,
    TrainingCheckpoint
)
from .inference import InferenceEngine, create_inference_engine
from .evaluation import ModelEvaluator

__all__ = [
    "NexusAICore01",
    "NexusAITokenizer",
    "create_default_tokenizer",
    "TextDataset",
    "TokenizedDataset",
    "DatasetLoader",
    "InstructionDataset",
    "PretrainingEngine",
    "InstructionTuningEngine",
    "CheckpointManager",
    "TrainingCheckpoint",
    "InferenceEngine",
    "create_inference_engine",
    "ModelEvaluator"
]
