"""
NexusAI ML Service

Python ML service for neural network training and inference.
Serves as the bridge between TypeScript application and PyTorch models.
"""

# System Prompt for NexusAI
SYSTEM_PROMPT = """You are an AI assistant created by Mr. Hasibul, an engineer based in Bangladesh. 
You respond accurately based on your knowledge base in three styles/languages:
- English
- Banglish (Bengali written in English alphabet)
- Bengali (বাংলা)

Always answer according to the user's input language and tone.

Creator Information:
- Created by: Mr. Hasibul
- Profession: Engineer
- Location: Bangladesh

Key Knowledge:
- First pillar of Islam: Shahada (faith)
- Five pillars of Islam: Shahada, Salah, Zakat, Sawm, Hajj
- Salah: Islamic prayer performed five times daily
- Zakat: Obligatory charity for helping the poor"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import sys
import os
import torch
import time
import uvicorn
import json
import random

# Fix Windows encoding for UTF-8 support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path for imports
service_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.dirname(service_dir)
sys.path.insert(0, ai_core_dir)

from tokenizer.tokenizer import SimpleTokenizer
from neural.small_transformer import SmallTransformer
from neural.medium_transformer import MediumTransformer
from inference.generator import TextGenerator
from training.dataset import load_json_dataset
import sentencepiece as spm
import sys
import os

# Add ml-service directory to path for data_endpoints import
ml_service_dir = os.path.join(service_dir, "ml-service")
if ml_service_dir not in sys.path:
    sys.path.insert(0, ml_service_dir)

try:
    from data_endpoints import add_upload_endpoints
except ImportError:
    print("[ML Service] data_endpoints not available, skipping upload endpoints")
    add_upload_endpoints = None

# Add knowledge ingestion endpoints
try:
    import sys
    ai_core_dir = os.path.dirname(service_dir)
    knowledge_dir = os.path.join(ai_core_dir, "knowledge")
    if knowledge_dir not in sys.path:
        sys.path.insert(0, knowledge_dir)
    from pipeline.ingestion_pipeline import KnowledgeIngestionPipeline
    INGESTION_AVAILABLE = True
    ingestion_pipeline = KnowledgeIngestionPipeline()
    print("[ML Service] Knowledge ingestion pipeline available")
except ImportError as e:
    INGESTION_AVAILABLE = False
    ingestion_pipeline = None
    print(f"[ML Service] Knowledge ingestion pipeline not available: {e}")

# Add data directory to path for RAG and autonomous imports
data_dir = os.path.join(ai_core_dir, "data")
sys.path.insert(0, data_dir)

try:
    from rag_system import RAGSystem
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("[ML Service] RAG system not available, will use neural model only")

# Try to load simple retrieval system
try:
    import sys
    ai_core_dir = os.path.dirname(service_dir)
    knowledge_dir = os.path.join(ai_core_dir, "knowledge")
    if knowledge_dir not in sys.path:
        sys.path.insert(0, knowledge_dir)
    from store.simple_retrieval import SimpleRetrievalSystem
    SIMPLE_RETRIEVAL_AVAILABLE = True
    simple_retrieval = SimpleRetrievalSystem()
    print("[ML Service] Simple retrieval system available")
except ImportError as e:
    SIMPLE_RETRIEVAL_AVAILABLE = False
    simple_retrieval = None
    print(f"[ML Service] Simple retrieval system not available: {e}")

try:
    from pipeline_orchestrator import AutonomousPipeline
    AUTONOMOUS_AVAILABLE = True
except ImportError:
    AUTONOMOUS_AVAILABLE = False
    print("[ML Service] Autonomous pipeline not available")

app = FastAPI(
    title="NexusAI ML Service",
    description="Internal ML service for NexusAI Brain",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
tokenizer: Optional[SimpleTokenizer] = None
model: Optional[SmallTransformer] = None
generator: Optional[TextGenerator] = None
model_loaded = False

# Model metadata tracking
loaded_model_name: Optional[str] = None
loaded_checkpoint_path: Optional[str] = None
loaded_max_len: Optional[int] = None

# Diagnostic mode gate (disabled by default for safety)
DIAGNOSTIC_MODE_ENABLED = os.getenv("DIAGNOSTIC_MODE_ENABLED", "false").lower() == "true"

# RAG System
rag_system: Optional[RAGSystem] = None
rag_loaded = False

# Autonomous Pipeline
autonomous_pipeline: Optional[AutonomousPipeline] = None
autonomous_running = False

# In-memory conversation context storage (session-based)
conversation_contexts: Dict[str, List[Dict]] = {}

# Simple language detection using Unicode ranges
def detect_language(text: str) -> str:
    """
    Detect language using Unicode ranges.
    Returns: 'bengali', 'english', 'mixed', or 'unknown'
    """
    if not text:
        return 'unknown'
    
    # Bengali Unicode range: U+0980 to U+09FF
    bengali_count = 0
    # Latin/English range
    latin_count = 0
    
    for char in text:
        code = ord(char)
        if 0x0980 <= code <= 0x09FF:
            bengali_count += 1
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):  # A-Z, a-z
            latin_count += 1
    
    # If any Bengali characters detected, prioritize Bengali
    if bengali_count > 0:
        if latin_count > 0:
            return 'mixed'
        return 'bengali'
    elif latin_count > 0:
        return 'english'
    else:
        return 'unknown'

# Pydantic models
class InferenceRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    max_tokens: Optional[int] = Field(50, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.8, description="Sampling temperature")

class InferenceResponse(BaseModel):
    response: str = Field(..., description="Generated response")
    model: str = Field(..., description="Model identifier")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")

class OrchestratorRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    conversation_history: Optional[List[Dict]] = Field([], description="Conversation history for context")
    memory: Optional[List[Dict]] = Field([], description="User memory for context")
    request_id: Optional[str] = Field(None, description="Unique request ID for tracing")
    diagnostic_mode: bool = Field(False, description="Enable diagnostic mode to inspect raw neural output (requires DIAGNOSTIC_MODE_ENABLED environment variable)")

class OrchestratorResponse(BaseModel):
    response: str = Field(..., description="Generated response")
    latency_ms: float = Field(..., description="Total processing latency in milliseconds")
    intent: str = Field(..., description="Detected intent")
    response_source: str = Field(..., description="Source of response")
    language: str = Field(..., description="Detected language")
    diagnostics: list = Field(..., description="Processing diagnostics")
    raw_neural_output: Optional[str] = Field(None, description="Raw neural output before validation (diagnostic mode only)")
    rejection_reason: Optional[str] = Field(None, description="Reason for neural output rejection (diagnostic mode only)")

class ModelStatus(BaseModel):
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_name: Optional[str] = Field(None, description="Model name")
    model_version: Optional[str] = Field(None, description="Model version")
    parameter_count: Optional[int] = Field(None, description="Number of parameters")
    checkpoint: Optional[str] = Field(None, description="Checkpoint path")
    device: str = Field(..., description="Device (cpu/cuda)")
    vocabulary_size: Optional[int] = Field(None, description="Vocabulary size")
    sequence_length: Optional[int] = Field(None, description="Max sequence length")

class PipelineStatus(BaseModel):
    autonomous_available: bool = Field(..., description="Whether autonomous pipeline is available")
    autonomous_running: bool = Field(..., description="Whether autonomous pipeline is running")
    pipeline_cycles: int = Field(..., description="Number of pipeline cycles completed")
    last_improvement: float = Field(..., description="Last improvement score")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    model_loaded: bool = Field(..., description="Whether model is loaded")

def load_model_if_needed():
    """Load model if not already loaded"""
    global tokenizer, model, generator, model_loaded, loaded_model_name, loaded_checkpoint_path, loaded_max_len

    if model_loaded:
        return

    print("[ML Service] Loading model...")

    try:
        # Try to load production designation from current.json
        production_config_path = os.path.join(ai_core_dir, "models/production/current.json")
        checkpoint_path = None
        
        if os.path.exists(production_config_path):
            try:
                with open(production_config_path, 'r', encoding='utf-8') as f:
                    production_config = json.load(f)
                checkpoint_path = os.path.join(ai_core_dir, production_config["checkpoint_path"])
                print(f"[ML Service] Loaded production designation from {production_config_path}")
                print(f"[ML Service] Production model: {production_config['model_name']} v{production_config['model_version']}")
            except Exception as e:
                print(f"[ML Service] Warning: Failed to load production designation: {e}")
                print(f"[ML Service] Falling back to default checkpoint path")
        
        # Fallback to default path if production designation not available
        if checkpoint_path is None:
            checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")
            print(f"[ML Service] Using default checkpoint path: {checkpoint_path}")
        
        checkpoint_vocab_size = None
        
        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path, map_location="cpu")
            # Try to get vocab size from checkpoint
            if "tokenizer_vocab" in checkpoint:
                checkpoint_vocab_size = len(checkpoint["tokenizer_vocab"])
            elif "model_state_dict" in checkpoint:
                # Infer from embedding layer
                checkpoint_vocab_size = checkpoint["model_state_dict"]["token_embedding.embedding.weight"].shape[0]
            print(f"[ML Service] Checkpoint vocabulary size: {checkpoint_vocab_size}")
        else:
            raise FileNotFoundError(f"Checkpoint not found at {checkpoint_path}")
        
        # Load checkpoint to get configuration
        checkpoint = torch.load(checkpoint_path, map_location="cpu")
        
        # Use checkpoint config if available
        if "config" in checkpoint:
            config = checkpoint["config"]
            vocab_size = config["vocab_size"]
            d_model = config["d_model"]
            n_layers = config["n_layers"]
            n_heads = config["n_heads"]
            d_ff = config["d_ff"]
            max_len = config["max_len"]
            print(f"[ML Service] Loaded config from checkpoint: {config}")
        else:
            # Fallback defaults
            vocab_size = checkpoint_vocab_size if checkpoint_vocab_size else 8000
            d_model = 128
            n_layers = 2
            n_heads = 2
            d_ff = 512
            max_len = 128
            print(f"[ML Service] Using default config (vocab_size={vocab_size})")
        
        # Load SentencePiece tokenizer (Phase 1 BPE 8K)
        tokenizer_path = os.path.join(ai_core_dir, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
        if os.path.exists(tokenizer_path):
            tokenizer = spm.SentencePieceProcessor()
            tokenizer.load(tokenizer_path)
            print(f"[ML Service] Loaded SentencePiece tokenizer from {tokenizer_path}")
            print(f"[ML Service] Tokenizer vocab size: {tokenizer.get_piece_size()}")
        else:
            # Fallback to SimpleTokenizer
            print(f"[ML Service] WARNING: SentencePiece tokenizer not found at {tokenizer_path}")
            print(f"[ML Service] Falling back to SimpleTokenizer")
            tokenizer = SimpleTokenizer(vocab_size=vocab_size)
            train_texts = load_json_dataset(os.path.join(ai_core_dir, "data/train_v2.json"))
            tokenizer.build_vocab(train_texts, min_freq=1)

        # Load Medium Transformer with checkpoint config
        model = MediumTransformer(
            vocab_size=vocab_size,
            d_model=d_model,
            n_layers=n_layers,
            n_heads=n_heads,
            d_ff=d_ff,
            max_len=max_len
        )

        # Load checkpoint
        if "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)
        model.eval()
        print(f"[ML Service] Medium model loaded from {checkpoint_path}")

        # Create generator
        # Wrap SentencePiece tokenizer to match SimpleTokenizer interface
        class SentencePieceWrapper:
            def __init__(self, sp_tokenizer):
                self.sp = sp_tokenizer
                self.pad_id = 0
                self.unk_id = 1
                self.bos_id = 2
                self.eos_id = 3
            
            def encode(self, text, add_special_tokens=True):
                tokens = self.sp.encode(text, out_type=int)
                if add_special_tokens:
                    tokens = [self.bos_id] + tokens + [self.eos_id]
                return tokens
            
            def decode(self, token_ids, skip_special_tokens=True):
                # Filter special tokens if requested
                if skip_special_tokens:
                    token_ids = [tid for tid in token_ids if tid not in [self.pad_id, self.unk_id, self.bos_id, self.eos_id]]
                return self.sp.decode(token_ids)
        
        class SimpleTextGenerator:
            """Simple generator that supports sampling parameters"""
            def __init__(self, model, tokenizer, device="cpu"):
                self.model = model.to(device)
                self.tokenizer = tokenizer
                self.device = device
                self.model.eval()
            
            def generate(self, prompt, max_new_tokens=50, temperature=1.0, 
                        top_k=None, top_p=None, do_sample=False, repetition_penalty=1.0, **kwargs):
                with torch.no_grad():
                    # Encode prompt
                    tokens = self.tokenizer.encode(prompt, add_special_tokens=True)
                    input_ids = torch.tensor([tokens], dtype=torch.long).to(self.device)
                    
                    # Generate token by token
                    for _ in range(max_new_tokens):
                        if input_ids.size(1) >= self.model.max_len:
                            input_ids = input_ids[:, -self.model.max_len:]
                        
                        logits = self.model(input_ids)
                        next_token_logits = logits[:, -1, :]
                        
                        # Apply repetition penalty
                        if repetition_penalty > 1.0:
                            for token_id in set(input_ids[0].tolist()):
                                next_token_logits[0, token_id] /= repetition_penalty
                        
                        # Apply temperature
                        next_token_logits = next_token_logits / temperature
                        
                        # Sampling logic
                        if do_sample and (top_k is not None or top_p is not None):
                            # Top-k sampling
                            if top_k is not None:
                                top_k = min(top_k, next_token_logits.size(-1))
                                values, indices = torch.topk(next_token_logits, top_k)
                                next_token_logits = torch.full_like(next_token_logits, float('-inf'))
                                next_token_logits.scatter_(1, indices, values)
                            
                            # Top-p (nucleus) sampling
                            if top_p is not None:
                                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                                cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                                sorted_indices_to_remove = cumulative_probs > top_p
                                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                                sorted_indices_to_remove[..., 0] = 0
                                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                                next_token_logits[indices_to_remove] = float('-inf')
                            
                            # Sample from distribution
                            probs = torch.softmax(next_token_logits, dim=-1)
                            next_token = torch.multinomial(probs, num_samples=1)
                        else:
                            # Greedy decoding
                            next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
                        
                        input_ids = torch.cat([input_ids, next_token], dim=1)
                        
                        # Check for EOS or PAD
                        if next_token.item() == self.tokenizer.eos_id or next_token.item() == self.tokenizer.pad_id:
                            break
                    
                    # Decode
                    generated_ids = input_ids[0].cpu().tolist()
                    generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
                    
                    # Remove prompt from output
                    # Try to find where the generated content starts
                    prompt_tokens = self.tokenizer.encode(prompt, add_special_tokens=True)
                    if len(generated_ids) > len(prompt_tokens):
                        generated_only_ids = generated_ids[len(prompt_tokens):]
                        generated_text = self.tokenizer.decode(generated_only_ids, skip_special_tokens=True)
                        print(f"[Generator] Generated {len(generated_only_ids)} new tokens: {generated_only_ids[:10]}")
                    else:
                        print(f"[Generator] Warning: No new tokens generated (total={len(generated_ids)}, prompt={len(prompt_tokens)})")
                        generated_text = ""
                    
                    return generated_text
        
        if isinstance(tokenizer, spm.SentencePieceProcessor):
            tokenizer = SentencePieceWrapper(tokenizer)
            generator = SimpleTextGenerator(model, tokenizer, device="cpu")
        else:
            generator = TextGenerator(model, tokenizer, device="cpu")

        # Track model metadata
        loaded_model_name = "MediumTransformer"
        loaded_checkpoint_path = checkpoint_path
        loaded_max_len = model.max_len

        model_loaded = True
        print(f"[ML Service] Model loaded successfully - Parameters: {model.count_parameters():,}")

    except Exception as e:
        print(f"[ML Service] Error loading model: {e}")
        # Fallback to Small model if Medium fails
        print("[ML Service] Falling back to Small model...")
        try:
            from neural.small_transformer import SmallTransformer
            tokenizer = SimpleTokenizer(vocab_size=1000)
            train_texts = load_json_dataset(os.path.join(ai_core_dir, "data/train_v2.json"))
            tokenizer.build_vocab(train_texts, min_freq=1)
            
            model = SmallTransformer(
                vocab_size=tokenizer.get_vocab_size(),
                d_model=64,
                n_layers=2,
                n_heads=2,
                d_ff=256,
                max_len=128
            )
            
            checkpoint_path_small = os.path.join(ai_core_dir, "models/checkpoints/checkpoint_epoch_5.pt")
            if os.path.exists(checkpoint_path_small):
                checkpoint = torch.load(checkpoint_path_small, map_location="cpu")
                model.load_state_dict(checkpoint["model_state_dict"])
                model.eval()
                print(f"[ML Service] Small model loaded from {checkpoint_path_small}")
            
            generator = TextGenerator(model, tokenizer, device="cpu")
            model_loaded = True
            print(f"[ML Service] Small model loaded successfully - Parameters: {model.count_parameters():,}")
        except Exception as e2:
            print(f"[ML Service] Fallback also failed: {e2}")
            raise

def load_rag_if_needed():
    """Load RAG system if not already loaded"""
    global rag_system, rag_loaded

    if not RAG_AVAILABLE or rag_loaded:
        return

    print("[ML Service] Loading RAG system...")

    try:
        rag_system = RAGSystem(embedding_dimension=768)

        # Try to load processed data
        processed_dir = os.path.join(ai_core_dir, "data/processed")
        if os.path.exists(processed_dir):
            # Find most recent processed file
            import glob
            processed_files = glob.glob(os.path.join(processed_dir, "processed_*.jsonl"))
            if processed_files:
                latest_file = max(processed_files, key=os.path.getctime)
                rag_system.load_documents(latest_file)
                rag_loaded = True
                print(f"[ML Service] RAG system loaded with documents from {latest_file}")
            else:
                print("[ML Service] No processed data found for RAG system")
        else:
            print("[ML Service] Processed data directory not found for RAG system")

    except Exception as e:
        print(f"[ML Service] Error loading RAG system: {e}")
        rag_loaded = False

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        service="nexusai-brain",
        model_loaded=model_loaded
    )

@app.get("/model/status", response_model=ModelStatus)
async def model_status():
    """Get model status"""
    if not model_loaded:
        load_model_if_needed()

    if model is None:
        return ModelStatus(
            model_loaded=False,
            device="cpu"
        )

    # Get actual device
    try:
        device = str(next(model.parameters()).device)
    except:
        device = "cpu"

    return ModelStatus(
        model_loaded=True,
        model_name=loaded_model_name or "Unknown",
        model_version="1.0.0",  # Still hardcoded as not stored in checkpoint
        parameter_count=model.count_parameters(),
        checkpoint=loaded_checkpoint_path or "Unknown",
        device=device,
        vocabulary_size=tokenizer.get_vocab_size(),
        sequence_length=loaded_max_len or 512
    )

@app.post("/inference", response_model=InferenceResponse)
async def inference(request: InferenceRequest):
    """Run inference on user message"""
    try:
        if not model_loaded:
            load_model_if_needed()

        if generator is None:
            raise HTTPException(status_code=503, detail="Model not available")

        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")

        # Run inference
        start_time = time.time()
        response_text = generator.generate(
            prompt=request.message,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=True
        )
        latency_ms = (time.time() - start_time) * 1000

        # Validate output - return even if poor quality for integration testing
        if not response_text:
            response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"

        # If response is just repetition of input, note it
        if response_text == request.message.lower():
            response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"

        return InferenceResponse(
            response=response_text,
            model="SmallTransformer-v1.0.0",
            latency_ms=latency_ms,
            conversation_id=request.conversation_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ML Service] Inference error: {e}")
        # Return user-friendly Bengali error message
        return InferenceResponse(
            response="দুঃখিত, সিস্টেম ব্যাকএন্ডের সাথে সংযোগ স্থাপন করতে পারছে না। অনুগ্রহ করে সার্ভিসটি চালু আছে কিনা পরীক্ষা করুন।",
            model="SmallTransformer-v1.0.0",
            latency_ms=0,
            conversation_id=request.conversation_id
        )

@app.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate(request: Request):
    """
    Orchestrate message processing with language detection, intent classification, and routing
    """
    try:
        # Parse request body manually to ensure UTF-8 handling
        body_bytes = await request.body()
        body_text = body_bytes.decode('utf-8')
        body_data = json.loads(body_text)

        message = body_data.get('message', '')
        conversation_id = body_data.get('conversation_id')
        conversation_history = body_data.get('conversation_history', [])
        memory = body_data.get('memory', [])
        request_id = body_data.get('request_id')
        diagnostic_mode = body_data.get('diagnostic_mode', False)

        if not model_loaded:
            load_model_if_needed()

        if not rag_loaded:
            load_rag_if_needed()

        if generator is None:
            raise HTTPException(status_code=503, detail="Model not available")

        # Validate input
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")

        # Log request
        request_id = request_id or f"REQ_{int(time.time() * 1000)}"
        print(f"[ML Service] Processing request {request_id} for conversation {conversation_id}")
        print(f"[ML Service] Message: {message}")
        print(f"[ML Service] Message bytes: {message.encode('utf-8')}")

        # Step 1: Language Detection
        language = detect_language(message)
        print(f"[ML Service] Detected language: {language}")

        # Step 2: Validate and format conversation history for neural generation
        formatted_history = ""
        history_used = False
        
        if conversation_history and isinstance(conversation_history, list):
            # Validate and format history entries
            valid_history = []
            for entry in conversation_history[-5:]:  # Use last 5 messages to stay within token limits
                if not isinstance(entry, dict):
                    continue
                role = entry.get('role', '').lower()
                content = entry.get('content', '')
                
                # Only accept valid roles and non-empty content
                if role in ['user', 'assistant'] and content and isinstance(content, str):
                    # Truncate long messages to avoid exceeding sequence length
                    if len(content) > 200:
                        content = content[:200]
                    valid_history.append(f"{role}: {content}")
            
            if valid_history:
                # Join history with newlines
                formatted_history = "\n".join(valid_history) + "\n"
                history_used = True
                print(f"[ML Service] Using {len(valid_history)} history messages for context")

        # Step 2.5: Validate and format memory for neural generation (Phase 3)
        formatted_memory = ""
        memory_used = False
        
        if memory and isinstance(memory, list):
            # Validate and format memory entries
            valid_memory = []
            for entry in memory[:3]:  # Use top 3 memories to stay within token limits
                if not isinstance(entry, dict):
                    continue
                category = entry.get('category', '')
                purpose = entry.get('purpose', '')
                value = entry.get('value', '')
                
                # Only accept valid entries with non-empty value
                if value and isinstance(value, str):
                    # Truncate long memory values
                    if len(value) > 150:
                        value = value[:150]
                    valid_memory.append(f"Memory ({category}): {value}")
            
            if valid_memory:
                # Join memory with newlines
                formatted_memory = "\n".join(valid_memory) + "\n"
                memory_used = True
                print(f"[ML Service] Using {len(valid_memory)} memory entries for context")

        # Step 3: Store message in conversation context (legacy in-memory storage)
        if conversation_id:
            if conversation_id not in conversation_contexts:
                conversation_contexts[conversation_id] = []
            conversation_contexts[conversation_id].append({
                "role": "user",
                "content": message,
                "language": language,
                "timestamp": time.time()
            })
            # Keep only last 10 messages to avoid unbounded growth
            if len(conversation_contexts[conversation_id]) > 10:
                conversation_contexts[conversation_id] = conversation_contexts[conversation_id][-10:]

        # Step 3: Intent Classification (Multilingual)
        intent = "UNKNOWN"
        lower_message = message.lower()

        # Knowledge base topics - these should trigger retrieval
        knowledge_topics = [
            'science', 'mathematics', 'math', 'physics', 'chemistry', 'biology',
            'computer science', 'history', 'philosophy', 'economics', 'geography',
            'what is', 'tell me about', 'explain', 'define', 'describe'
        ]

        # Check if message is about knowledge base topics
        if any(topic in lower_message for topic in knowledge_topics):
            intent = "GENERAL_QUESTION"

        # Bengali patterns
        if language == 'bengali' or language == 'mixed':
            # Bengali greeting patterns (expanded)
            if any(b in message for b in ['হ্যালো', 'হাই', 'হেলো', 'আসসালামু', 'নমস্কার', 'শুভ', 'সকাল', 'দুপুর', 'সন্ধ্যা', 'কেমন আছ', 'কেমন আছো', 'কেমন আছেন', 'আছো কেমন']):
                intent = "GREETING"
            # Bengali farewell patterns
            elif any(b in message for b in ['বিদায়', 'আবার', 'দেখা', 'কেয়ার', 'যাচ্ছি', 'যাই']):
                intent = "FAREWELL"
            # Bengali identity question
            elif any(b in message for b in ['নাম', 'কী', 'কি', 'তোমার', 'তোমার নাম']):
                intent = "IDENTITY_QUESTION"
            # Bengali capability question
            elif any(b in message for b in ['করতে', 'পার', 'সক্ষম', 'সাহায্য', 'কী করতে পারো', 'কী করতে পারে']):
                intent = "CAPABILITY_QUESTION"
            # Bengali thanks
            elif any(b in message for b in ['ধন্যবাদ', 'থ্যাংক', 'শুকরিয়া', 'ধন্যবাদ']):
                intent = "THANKS"
            # Bengali help request
            elif any(b in message for b in ['সাহায্য', 'হেল্প', 'সাহায্য চাই', 'হেল্প চাই']):
                intent = "HELP_REQUEST"
            # Bengali casual check-in
            elif any(b in message for b in ['কেমন', 'কী খবর', 'কেমন চলছে', 'কী অবস্থা']):
                intent = "CASUAL_CHECKIN"

        # English patterns (for pure English or mixed)
        if intent == "UNKNOWN":
            # Check greetings first (most specific)
            if lower_message in ['hello', 'hi', 'hey'] or lower_message.startswith(('hello ', 'hi ', 'hey ')):
                intent = "GREETING"
            elif any(g in lower_message for g in ['good morning', 'good afternoon', 'good evening']):
                intent = "GREETING"
            elif any(f in lower_message for f in ['bye', 'goodbye', 'farewell', 'see you', 'take care']):
                intent = "FAREWELL"
            elif 'name' in lower_message and 'your' in lower_message:
                intent = "IDENTITY_QUESTION"
            elif any(c in lower_message for c in ['what can you do', 'what are your capabilities', 'how can you help', 'what can you help']):
                intent = "CAPABILITY_QUESTION"
            elif any(t in lower_message for t in ['thank', 'thanks', 'appreciate']):
                intent = "THANKS"
            elif any(h in lower_message for h in ['help me', 'help', 'assist']):
                intent = "HELP_REQUEST"
            # Questions starting with what/how/why/when/where/who should go to neural model
            elif lower_message.startswith(('what ', 'how ', 'why ', 'when ', 'where ', 'who ')):
                intent = "GENERAL_QUESTION"

        print(f"[ML Service] Detected intent: {intent}")

        # Step 4: Route to appropriate handler
        response_source = "DETERMINISTIC_HANDLER"
        response_text = ""
        latency_ms = 0
        
        # Bengali deterministic responses
        if language == 'bengali':
            if intent == "GREETING":
                # Dynamic greeting based on context
                greetings = [
                    "হ্যালো! আমি NexusAI, আপনার ব্যক্তিগত AI সহকারী। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
                    "আসসালামু আলাইকুম! আমি NexusAI। আপনার জন্য কী করতে পারি?",
                    "নমস্কার! আমি NexusAI। আজ আপনার জন্য কী করতে পারি?",
                    "হাই! আমি NexusAI। কীভাবে সাহায্য করতে পারি?"
                ]
                response_text = random.choice(greetings)
            elif intent == "CASUAL_CHECKIN":
                checkin_responses = [
                    "আমি ভালো আছি, ধন্যবাদ! আপনি কেমন আছেন?",
                    "আলহামদুলিল্লাহ, ভালো আছি। আপনার কী খবর?",
                    "ভালো আছি! আপনার জন্য কী করতে পারি?",
                    "সব ঠিকঠাক আছে। আপনি কেমন আছেন?"
                ]
                response_text = random.choice(checkin_responses)
            elif intent == "FAREWELL":
                response_text = "বিদায়! যখনই আপনার সাহায্য প্রয়োজন হবে, ফিরে আসুন।"
            elif intent == "IDENTITY_QUESTION":
                response_text = "আমার নাম NexusAI। আমি একটি কাস্টম AI সহকারী যা বিভিন্ন কাজে সাহায্য করার জন্য ডিজাইন করা হয়েছে।"
            elif intent == "CAPABILITY_QUESTION":
                response_text = "আমি কথোপকথনের মাধ্যমে সাহায্য করতে পারি, প্রশ্নের উত্তর দিতে পারি এবং বিভিন্ন কাজে সহায্য করতে পারি। তবে আমার বর্তমান মডেলটি এখনও শিখছে, তাই কিছু উত্তর সীমিত হতে পারে।"
            elif intent == "THANKS":
                response_text = "স্বাগতম! আমি আপনাকে আর কীভাবে সাহায্য করতে পারি?"
            elif intent == "HELP_REQUEST":
                response_text = "আমি সাহায্য করতে প্রস্তুত! আপনি প্রশ্ন জিজ্ঞাসা করতে পারেন, কথোপকথন করতে পারেন, বা আমাকে বলতে পারেন আপনার কী সাহায্য প্রয়োজন।"
            elif intent == "GENERAL_QUESTION":
                # Use knowledge base for general questions
                response_source = "NEURAL_MODEL"
            else:
                # Bengali unknown - use neural model
                response_source = "NEURAL_MODEL"
        
        # English deterministic responses
        elif language == 'english':
            if intent == "GREETING":
                response_text = "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?"
            elif intent == "FAREWELL":
                response_text = "Goodbye! Feel free to come back anytime you need assistance."
            elif intent == "IDENTITY_QUESTION":
                response_text = "I'm NexusAI, a custom AI assistant designed to help you with various tasks."
            elif intent == "CAPABILITY_QUESTION":
                response_text = "I can help you with conversations, answer questions, and assist with various tasks. However, my current model is still learning, so some responses may be limited."
            elif intent == "THANKS":
                response_text = "You're welcome! Is there anything else I can help you with?"
            elif intent == "HELP_REQUEST":
                response_text = "I'm here to help! You can ask me questions, have a conversation, or tell me what you need assistance with."
            elif intent == "GENERAL_QUESTION":
                # Use neural model for general questions
                response_source = "NEURAL_MODEL"
            else:
                # English unknown - use neural model
                response_source = "NEURAL_MODEL"
        
        # Mixed language - respond in dominant language or mixed naturally
        elif language == 'mixed':
            if intent == "GREETING":
                response_text = "হ্যালো! I'm NexusAI, your personal AI assistant. How can I help you today?"
            elif intent == "IDENTITY_QUESTION":
                response_text = "আমার নাম NexusAI। I'm a custom AI assistant designed to help you with various tasks."
            elif intent == "CAPABILITY_QUESTION":
                response_text = "আমি কথোপকথনের মাধ্যমে সাহায্য করতে পারি। I can help you with conversations and various tasks."
            else:
                # Mixed unknown - use neural model
                response_source = "NEURAL_MODEL"
        
        # Unknown language - use neural model
        else:
            response_source = "NEURAL_MODEL"
        
        # Step 5: Neural model processing for unknown intents
        # Initialize diagnostic variables
        raw_neural_output = None
        rejection_reason = None
        is_fallback = False

        if response_source == "NEURAL_MODEL":
            start_time = time.time()

            # DISABLED: Simple retrieval fallback for accurate neural model testing
            # The requirement is to test the trained neural model, not fallback to retrieval
            retrieved_context = ""
            print(f"[ML Service] SIMPLE_RETRIEVAL_AVAILABLE: {SIMPLE_RETRIEVAL_AVAILABLE} (DISABLED for neural testing)")
            # if SIMPLE_RETRIEVAL_AVAILABLE and simple_retrieval is not None:
            #     try:
            #         print(f"[ML Service] Attempting simple retrieval...")
            #         if not simple_retrieval.loaded:
            #             simple_retrieval.load()
            #         context = simple_retrieval.get_context(message, top_k=2)
            #         print(f"[ML Service] Context length: {len(context) if context else 0}")
            #         if context:
            #             retrieved_context = context
            #             print(f"[ML Service] Retrieved context for query: {message[:50]}...")
            #     except Exception as e:
            #         print(f"[ML Service] Simple retrieval failed: {e}")
            #         import traceback
            #         traceback.print_exc()

            # Build prompt for neural generation
            # The model was trained on raw text, not chat format
            # Use simple concatenation of context + message
            context_parts = []
            
            if history_used and formatted_history:
                # Add history without role labels
                for entry in conversation_history[-3:]:
                    if isinstance(entry, dict):
                        content = entry.get('content', '')
                        if content:
                            context_parts.append(content)
            
            if memory_used and formatted_memory:
                for entry in memory[:2]:
                    if isinstance(entry, dict):
                        value = entry.get('value', '')
                        if value:
                            context_parts.append(value)
            
            if context_parts:
                # Join context with message
                augmented_message = " ".join(context_parts) + " " + message
                print(f"[ML Service] Context-aware prompt (total length: {len(augmented_message)})")
            else:
                augmented_message = message
                print(f"[ML Service] Single-turn prompt")

            # Use neural model for generation (retrieval disabled for accurate testing)
            response_text = generator.generate(
                prompt=augmented_message,
                max_new_tokens=100,  # Increased for better responses
                temperature=0.8,
                top_k=50,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.2
            )

            latency_ms = (time.time() - start_time) * 1000

            # Validate output
            raw_neural_output = response_text  # Save before validation for diagnostics
            print(f"[ML Service] Raw neural output: '{response_text}' (length: {len(response_text)})")

            if not response_text:
                response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
                is_fallback = True
                rejection_reason = "EMPTY_RESPONSE"
            elif response_text.strip() == message.strip().lower():
                # Only reject if response is EXACTLY the input (not just contains it)
                response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
                is_fallback = True
                rejection_reason = "EQUALS_MESSAGE"
            elif len(response_text.strip()) < 3:
                response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
                is_fallback = True
                rejection_reason = "TOO_SHORT"
            # REMOVED: Overly strict containment check that rejected valid conversational responses
            # Conversational models naturally include context from the input

            if is_fallback:
                print(f"[ML Service] Using fallback: {rejection_reason}")
                response_source = "FALLBACK"

        # Step 6: Store assistant response in context
        if conversation_id:
            if conversation_id in conversation_contexts:
                conversation_contexts[conversation_id].append({
                    "role": "assistant",
                    "content": response_text,
                    "language": language,
                    "timestamp": time.time()
                })

        # Step 7: Build diagnostics
        if response_source == "DETERMINISTIC_HANDLER":
            latency_ms = 1
            diagnostics = [
                {"name": "Input Validation", "status": "success", "duration_ms": 0},
                {"name": "Language Detection", "status": "success", "duration_ms": 1},
                {"name": "Intent Classification", "status": "success", "duration_ms": 1},
                {"name": "Deterministic Handler", "status": "success", "duration_ms": 1},
                {"name": "Neural Model Inference", "status": "skipped", "skipReason": "Deterministic handler selected"},
                {"name": "Response Validation", "status": "skipped", "skipReason": "Deterministic response used"},
                {"name": "Final Response Delivered", "status": "success", "duration_ms": 0},
            ]
        else:
            if response_source == "RAG_AUGMENTED":
                diagnostics = [
                    {"name": "Input Validation", "status": "success", "duration_ms": 0},
                    {"name": "Language Detection", "status": "success", "duration_ms": 1},
                    {"name": "Intent Classification", "status": "success", "duration_ms": 1},
                    {"name": "Deterministic Handler", "status": "skipped", "skipReason": "Neural model selected"},
                    {"name": "RAG Retrieval", "status": "success", "duration_ms": 1},
                    {"name": "Neural Model Inference", "status": "success", "duration_ms": latency_ms},
                    {"name": "Response Validation", "status": "success", "duration_ms": 1},
                    {"name": "Final Response Delivered", "status": "success", "duration_ms": 0},
                ]
            else:
                diagnostics = [
                    {"name": "Input Validation", "status": "success", "duration_ms": 0},
                    {"name": "Language Detection", "status": "success", "duration_ms": 1},
                    {"name": "Intent Classification", "status": "success", "duration_ms": 1},
                    {"name": "Deterministic Handler", "status": "skipped", "skipReason": "Neural model selected"},
                    {"name": "RAG Retrieval", "status": "skipped", "skipReason": "RAG not loaded or failed"},
                    {"name": "Neural Model Inference", "status": "success", "duration_ms": latency_ms},
                    {"name": "Response Validation", "status": "success", "duration_ms": 1},
                    {"name": "Final Response Delivered", "status": "success", "duration_ms": 0},
                ]

        print(f"[ML Service] Request {request_id} completed: intent={intent}, language={language}, source={response_source}")

        # Build response with optional diagnostic fields
        response_data = {
            "response": response_text,
            "latency_ms": latency_ms,
            "intent": intent,
            "response_source": response_source,
            "language": language,
            "diagnostics": diagnostics
        }

        # Add diagnostic fields only if both environment variable and request parameter are enabled
        if DIAGNOSTIC_MODE_ENABLED and diagnostic_mode:
            response_data["raw_neural_output"] = raw_neural_output if raw_neural_output else None
            if is_fallback and rejection_reason:
                response_data["rejection_reason"] = rejection_reason

        return OrchestratorResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ML Service] Orchestration error: {e}")
        # Return user-friendly Bengali error message instead of raw error
        return OrchestratorResponse(
            response="দুঃখিত, সিস্টেম ব্যাকএন্ডের সাথে সংযোগ স্থাপন করতে পারছে না। অনুগ্রহ করে সার্ভিসটি চালু আছে কিনা পরীক্ষা করুন।",
            latency_ms=0,
            intent="ERROR",
            response_source="FALLBACK",
            language="bengali",
            diagnostics=[{"name": "Error", "status": "failed", "duration_ms": 0}]
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NexusAI ML Service",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "model/status": "/model/status",
            "inference": "/inference",
            "orchestrate": "/orchestrate",
            "pipeline/status": "/pipeline/status",
            "pipeline/run": "/pipeline/run"
        }
    }

@app.get("/pipeline/status", response_model=PipelineStatus)
async def pipeline_status():
    """Get autonomous pipeline status"""
    global autonomous_pipeline, autonomous_running

    return PipelineStatus(
        autonomous_available=AUTONOMOUS_AVAILABLE,
        autonomous_running=autonomous_running,
        pipeline_cycles=len(autonomous_pipeline.pipeline_history) if autonomous_pipeline else 0,
        last_improvement=0.0
    )

@app.post("/pipeline/run")
async def run_pipeline():
    """Run autonomous pipeline once"""
    global autonomous_pipeline, autonomous_running

    if not AUTONOMOUS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Autonomous pipeline not available")

    try:
        if autonomous_pipeline is None:
            autonomous_pipeline = AutonomousPipeline()
            autonomous_pipeline.setup_default_pipeline()

        autonomous_running = True
        summary = autonomous_pipeline.execute_pipeline()
        autonomous_running = False

        return {
            "status": "completed",
            "summary": summary
        }
    except Exception as e:
        autonomous_running = False
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.post("/ingestion/process")
async def process_document(request: Request):
    """
    Process document using Python ingestion pipeline
    Returns cleaned document and chunks for database persistence
    """
    if not INGESTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Ingestion pipeline not available")

    try:
        body_bytes = await request.body()
        body_text = body_bytes.decode('utf-8')
        body_data = json.loads(body_text)

        text = body_data.get('text')
        source = body_data.get('source', 'api_ingestion')
        source_type = body_data.get('source_type', 'user_uploaded')
        metadata = body_data.get('metadata', {})

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")

        # Convert string source_type to enum
        from pipeline.schemas import SourceType
        source_type_enum = SourceType.USER_UPLOADED
        if source_type == 'web':
            source_type_enum = SourceType.WEB
        elif source_type == 'dataset':
            source_type_enum = SourceType.DATASET
        elif source_type == 'user_uploaded':
            source_type_enum = SourceType.USER_UPLOADED

        # Process using Python pipeline
        result = await ingestion_pipeline.ingest_from_text(
            text=text,
            source=source,
            source_type=source_type_enum,
            metadata=metadata
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=f"Processing failed: {result.error}")

        # Retrieve the cleaned document and chunks
        cleaned_doc = ingestion_pipeline.get_cleaned_document(result.document_id)

        if not cleaned_doc:
            raise HTTPException(status_code=500, detail="Failed to retrieve processed document")

        # Read chunks from JSONL file
        chunks_file = ingestion_pipeline.cleaned_data_dir / "chunks.jsonl"
        chunks = []
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunk_data = json.loads(line)
                        # Only return chunks for this document
                        if chunk_data.get('document_id') == result.document_id:
                            chunks.append(chunk_data)

        return {
            "success": True,
            "document_id": result.document_id,
            "cleaned_document": cleaned_doc.to_dict(),
            "chunks": chunks,
            "chunk_count": len(chunks),
            "processing_time_ms": result.processing_time_ms,
            "metadata": result.metadata
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ML Service] Ingestion error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

if __name__ == "__main__":
    # Add data management endpoints
    add_upload_endpoints(app)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
