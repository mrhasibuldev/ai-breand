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
                "message": f"Model status is {self.config.model_status.value}. Output will be random and meaningless.",
                "model_status": self.config.model_status.value
            }
        
        # Encode prompt
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens or self.config.max_new_tokens,
                temperature=temperature or self.config.temperature,
                top_k=top_k if top_k is not None else self.config.top_k,
                top_p=top_p if top_p is not None else self.config.top_p,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty or self.config.repetition_penalty
            )
        
        # Decode
        generated_ids = generated_ids[0].cpu().tolist()
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Remove prompt from response
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return {
            "generated_text": generated_text,
            "model_status": self.config.model_status.value,
            "warning": None
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
