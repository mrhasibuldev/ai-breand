"""
NexusAI Core-01 Inference Engine

Provides text generation and inference capabilities for NexusAI Core-01.
"""

import torch
import sys
import os
from typing import Optional, Dict, Any

# Add models directory to path for config import
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(ai_core_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
from .transformer import NexusAICore01
from .tokenizer_interface import NexusAITokenizer


class InferenceEngine:
    """
    Inference engine for NexusAI Core-01.
    
    Provides text generation with proper model state warnings.
    """
    
    def __init__(
        self,
        model: NexusAICore01,
        tokenizer: NexusAITokenizer,
        config: NexusAICore01Config,
        device: str = "cpu"
    ):
        """
        Initialize inference engine.
        
        Args:
            model: NexusAI Core-01 model
            tokenizer: Tokenizer instance
            config: Model configuration
            device: Device to run inference on
        """
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.config = config
        self.device = device
        self.model.eval()
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        do_sample: bool = True,
        repetition_penalty: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of new tokens
            temperature: Sampling temperature
            top_k: Top-k sampling
            top_p: Top-p sampling
            do_sample: Whether to sample
            repetition_penalty: Repetition penalty
        
        Returns:
            Dictionary with generated text and metadata
        """
        # Check model status (handle both enum and string values)
        status_value = (
            self.config.model_status.value
            if isinstance(self.config.model_status, ModelStatus)
            else str(self.config.model_status)
        )
        if status_value in [ModelStatus.UNTRAINED.value, ModelStatus.RANDOMLY_INITIALIZED.value]:
            return {
                "generated_text": "",
                "warning": "MODEL_STATUS_UNTRAINED_OR_RANDOM",
                "message": f"Model status is {status_value}. Output will be random and meaningless.",
                "model_status": status_value
            }
        
        # Encode prompt. Training convention (PackedTextDataset):
        # [BOS] + content + [EOS] per document. An unfinished user prompt is
        # NOT a complete document, so we prepend BOS but do NOT append EOS —
        # appending EOS would tell the model the document already ended.
        content_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        input_ids = [self.tokenizer.bos_id] + content_ids
        # Respect max_len: keep BOS + most recent tokens
        max_len = getattr(self.config, "max_len", 512)
        if len(input_ids) > max_len:
            input_ids = [self.tokenizer.bos_id] + input_ids[-(max_len - 1):]
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        prompt_len = input_ids.shape[1]
        
        # Generate
        with torch.inference_mode():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens if max_new_tokens is not None else self.config.max_new_tokens,
                temperature=temperature if temperature is not None else self.config.temperature,
                top_k=top_k if top_k is not None else self.config.top_k,
                top_p=top_p if top_p is not None else self.config.top_p,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty if repetition_penalty is not None else self.config.repetition_penalty
            )
        
        # Extract ONLY newly generated tokens (model.generate returns the
        # full sequence including the prompt) and decode just those.
        new_ids = generated_ids[0, prompt_len:].cpu().tolist()
        generated_text = self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        
        return {
            "generated_text": generated_text,
            "model_status": (
                self.config.model_status.value
                if isinstance(self.config.model_status, ModelStatus)
                else str(self.config.model_status)
            ),
            "warning": None if generated_text else "EMPTY_GENERATION"
        }
    
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """
        Load model from checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        from .training import CheckpointManager
        
        checkpoint_dir = os.path.dirname(checkpoint_path)
        checkpoint_manager = CheckpointManager(checkpoint_dir)
        
        checkpoint = checkpoint_manager.load_checkpoint(os.path.basename(checkpoint_path))
        
        self.model.load_state_dict(checkpoint.model_state_dict)
        
        # Update config status
        self.config.model_status = ModelStatus(checkpoint.model_status)
        
        print(f"Model loaded from {checkpoint_path}")
        print(f"Model status: {self.config.model_status.value}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return self.model.get_model_info()


def create_inference_engine(
    config: NexusAICore01Config,
    checkpoint_path: Optional[str] = None,
    device: str = "cpu"
) -> InferenceEngine:
    """
    Create inference engine.
    
    Args:
        config: Model configuration
        checkpoint_path: Optional path to checkpoint
        device: Device to run on
    
    Returns:
        InferenceEngine instance
    """
    # Create model
    model = NexusAICore01(config)
    
    # Load checkpoint if provided
    if checkpoint_path and os.path.exists(checkpoint_path):
        # Temporarily create engine to load checkpoint
        from .tokenizer_interface import create_default_tokenizer
        tokenizer = create_default_tokenizer(config)
        engine = InferenceEngine(model, tokenizer, config, device)
        engine.load_checkpoint(checkpoint_path)
        return engine
    
    # Create tokenizer
    from .tokenizer_interface import create_default_tokenizer
    tokenizer = create_default_tokenizer(config)
    
    # Create engine
    engine = InferenceEngine(model, tokenizer, config, device)
    
    return engine


if __name__ == "__main__":
    # Test inference engine
    config = NexusAICore01Config()
    engine = create_inference_engine(config, device="cpu")
    
    print(f"Model info: {engine.get_model_info()}")
    
    # Test generation (should return warning for untrained model)
    result = engine.generate("What is your name?")
    print(f"\nGeneration result: {result}")
