"""
NexusAI Core-01 Evaluation Framework

Provides model evaluation and testing infrastructure for NexusAI Core-01.
"""

import torch
import sys
import os
import tempfile
from typing import Dict, Any, List

# Add models directory to path for config import
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(ai_core_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from nexusai_core_01.config.model_config import NexusAICore01Config
from .transformer import NexusAICore01
from .tokenizer_interface import NexusAITokenizer, create_default_tokenizer
from .training import CheckpointManager, TrainingCheckpoint


class ModelEvaluator:
    """
    Model evaluator for NexusAI Core-01.
    
    Performs architecture tests, parameter verification, and basic functionality tests.
    """
    
    def __init__(self, config: NexusAICore01Config):
        self.config = config
        self.results = {}
    
    def test_parameter_count(self, model: NexusAICore01) -> Dict[str, Any]:
        """
        Test parameter count matches configuration.
        
        Args:
            model: Model instance
        
        Returns:
            Test results
        """
        actual_params = model.count_parameters()
        estimated_params = self.config.estimated_parameter_count()
        
        self.results["parameter_count"] = {
            "actual": actual_params,
            "estimated": estimated_params,
            "match": actual_params == estimated_params,
            "difference": abs(actual_params - estimated_params),
            "passed": actual_params == estimated_params
        }
        
        return self.results["parameter_count"]
    
    def test_tensor_shapes(self, model: NexusAICore01) -> Dict[str, Any]:
        """
        Test tensor shapes are correct.
        
        Args:
            model: Model instance
        
        Returns:
            Test results
        """
        batch_size = 2
        seq_len = 32
        
        input_ids = torch.randint(0, self.config.vocab_size, (batch_size, seq_len))
        
        try:
            logits = model(input_ids)
            
            expected_shape = (batch_size, seq_len, self.config.vocab_size)
            actual_shape = logits.shape
            
            self.results["tensor_shapes"] = {
                "input_shape": input_ids.shape,
                "output_shape": actual_shape,
                "expected_shape": expected_shape,
                "match": actual_shape == expected_shape,
                "passed": actual_shape == expected_shape
            }
        except Exception as e:
            self.results["tensor_shapes"] = {
                "error": str(e),
                "passed": False
            }
        
        return self.results["tensor_shapes"]
    
    def test_causal_mask(self, model: NexusAICore01) -> Dict[str, Any]:
        """
        Test causal masking is correct.
        
        Args:
            model: Model instance
        
        Returns:
            Test results
        """
        seq_len = 10
        device = torch.device("cpu")
        
        mask = model.generate_causal_mask(seq_len, device)
        
        # Check that lower triangle is 1, upper is 0
        lower_triangle = torch.tril(torch.ones(seq_len, seq_len))
        match = torch.all(mask == lower_triangle).item()
        
        self.results["causal_mask"] = {
            "seq_len": seq_len,
            "mask_shape": mask.shape,
            "correct_lower_triangle": match,
            "passed": match
        }
        
        return self.results["causal_mask"]
    
    def test_forward_pass(self, model: NexusAICore01) -> Dict[str, Any]:
        """
        Test forward pass works correctly.
        
        Args:
            model: Model instance
        
        Returns:
            Test results
        """
        batch_size = 2
        seq_len = 32
        
        input_ids = torch.randint(0, self.config.vocab_size, (batch_size, seq_len))
        targets = torch.randint(0, self.config.vocab_size, (batch_size, seq_len))
        
        try:
            # Test logits only
            logits = model(input_ids)
            self.results["forward_pass_logits"] = {
                "output_shape": logits.shape,
                "passed": True
            }
            
            # Test loss calculation
            loss = model(input_ids, targets)
            self.results["forward_pass_loss"] = {
                "loss_value": loss.item(),
                "is_finite": torch.isfinite(loss).item(),
                "passed": torch.isfinite(loss).item()
            }
        except Exception as e:
            self.results["forward_pass"] = {
                "error": str(e),
                "passed": False
            }
        
        return self.results.get("forward_pass_loss", self.results.get("forward_pass_logits", {}))
    
    def test_tokenizer_compatibility(self, tokenizer: NexusAITokenizer) -> Dict[str, Any]:
        """
        Test tokenizer compatibility with model configuration.
        
        Args:
            tokenizer: Tokenizer instance
        
        Returns:
            Test results
        """
        vocab_size = tokenizer.get_vocab_size()
        special_tokens = tokenizer.get_special_tokens()
        
        self.results["tokenizer_compatibility"] = {
            "vocab_size_match": vocab_size == self.config.vocab_size,
            "tokenizer_vocab_size": vocab_size,
            "config_vocab_size": self.config.vocab_size,
            "special_tokens": special_tokens,
            "config_special_tokens": {
                "pad_id": self.config.pad_id,
                "unk_id": self.config.unk_id,
                "bos_id": self.config.bos_id,
                "eos_id": self.config.eos_id
            },
            "passed": vocab_size == self.config.vocab_size
        }
        
        return self.results["tokenizer_compatibility"]
    
    def test_checkpoint_save_load(self, model: NexusAICore01) -> Dict[str, Any]:
        """
        Test checkpoint save and load using temporary directory.
        
        Args:
            model: Model instance
        
        Returns:
            Test results
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Create checkpoint manager
                checkpoint_manager = CheckpointManager(temp_dir, "test")
                
                # Create dummy checkpoint
                checkpoint = TrainingCheckpoint(
                    model_state_dict=model.state_dict(),
                    optimizer_state_dict={},
                    epoch=0,
                    step=0,
                    train_loss=1.0,
                    val_loss=1.0,
                    config=self.config.to_dict(),
                    model_status=self.config.model_status.value
                )
                
                # Save
                saved_path = checkpoint_manager.save_checkpoint(checkpoint, "test_checkpoint.pt")
                
                # Load
                loaded_checkpoint = checkpoint_manager.load_checkpoint("test_checkpoint.pt")
                
                # Verify
                loaded_params = loaded_checkpoint.model_state_dict
                original_params = checkpoint.model_state_dict
                
                match = all(
                    torch.allclose(v1, v2)
                    for v1, v2 in zip(loaded_params.values(), original_params.values())
                )
                
                self.results["checkpoint_save_load"] = {
                    "saved_path": saved_path,
                    "checkpoint_loaded": True,
                    "parameters_match": match,
                    "passed": match
                }
            except Exception as e:
                self.results["checkpoint_save_load"] = {
                    "error": str(e),
                    "passed": False
                }
        
        return self.results["checkpoint_save_load"]
    
    def test_generation_interface(self, model: NexusAICore01, tokenizer: NexusAITokenizer) -> Dict[str, Any]:
        """
        Test generation interface works.
        
        Args:
            model: Model instance
            tokenizer: Tokenizer instance
        
        Returns:
            Test results
        """
        from .inference import InferenceEngine
        
        try:
            engine = InferenceEngine(model, tokenizer, self.config, device="cpu")
            
            # Test generation (should return warning for untrained model)
            result = engine.generate("test prompt", max_new_tokens=5)
            
            self.results["generation_interface"] = {
                "has_warning": result.get("warning") is not None,
                "has_message": result.get("message") is not None,
                "model_status": result.get("model_status"),
                "generated_text": result.get("generated_text", ""),
                "passed": result.get("model_status") in ["UNTRAINED", "RANDOMLY_INITIALIZED"]
            }
        except Exception as e:
            self.results["generation_interface"] = {
                "error": str(e),
                "passed": False
            }
        
        return self.results["generation_interface"]
    
    def test_device_compatibility(self, model: NexusAICore01) -> Dict[str, Any]:
        """
        Test device compatibility.
        
        Args:
            model: Model instance
        
        Returns:
            Test results
        """
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            try:
                model_cuda = model.to("cuda")
                input_ids = torch.randint(0, self.config.vocab_size, (1, 10)).to("cuda")
                logits = model_cuda(input_ids)
                
                self.results["device_compatibility"] = {
                    "cuda_available": True,
                    "cuda_works": True,
                    "current_device": str(next(model_cuda.parameters()).device),
                    "passed": True
                }
                
                # Move back to CPU
                model_cuda.to("cpu")
            except Exception as e:
                self.results["device_compatibility"] = {
                    "cuda_available": True,
                    "cuda_works": False,
                    "error": str(e),
                    "passed": False
                }
        else:
            self.results["device_compatibility"] = {
                "cuda_available": False,
                "cpu_works": True,
                "current_device": str(next(model.parameters()).device),
                "passed": True
            }
        
        return self.results["device_compatibility"]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all evaluation tests.
        
        Returns:
            All test results
        """
        print("Running NexusAI Core-01 evaluation tests...")
        
        # Create model and tokenizer
        model = NexusAICore01(self.config)
        tokenizer = create_default_tokenizer(self.config)
        
        # Run tests
        print("  Testing parameter count...")
        self.test_parameter_count(model)
        
        print("  Testing tensor shapes...")
        self.test_tensor_shapes(model)
        
        print("  Testing causal mask...")
        self.test_causal_mask(model)
        
        print("  Testing forward pass...")
        self.test_forward_pass(model)
        
        print("  Testing tokenizer compatibility...")
        self.test_tokenizer_compatibility(tokenizer)
        
        print("  Testing checkpoint save/load...")
        self.test_checkpoint_save_load(model)
        
        print("  Testing generation interface...")
        self.test_generation_interface(model, tokenizer)
        
        print("  Testing device compatibility...")
        self.test_device_compatibility(model)
        
        # Summary
        passed = sum(1 for r in self.results.values() if r.get("passed", False))
        total = len(self.results)
        
        print(f"\nTest summary: {passed}/{total} tests passed")
        
        self.results["summary"] = {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": passed / total if total > 0 else 0
        }
        
        return self.results


if __name__ == "__main__":
    # Run evaluation tests
    config = NexusAICore01Config()
    evaluator = ModelEvaluator(config)
    
    results = evaluator.run_all_tests()
    
    print("\nDetailed results:")
    for test_name, result in results.items():
        if test_name != "summary":
            print(f"  {test_name}: {result}")
    
    print(f"\nSummary: {results['summary']}")
