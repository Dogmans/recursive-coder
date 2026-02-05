"""Custom model class for direct Hugging Face model support."""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from smolagents.models import Model
from smolagents.models import ChatMessage


class DirectTransformersModel(Model):
    """Direct Transformers model without SmolAgents auto-detection."""
    
    def __init__(self, model_id: str = "microsoft/phi-3-mini-4k-instruct", device: str = None, quantize: bool = True):
        """Initialize model and tokenizer.
        
        Args:
            model_id: Hugging Face model ID
            device: Device to load model on ("cuda", "cpu", "mps")
            quantize: Use 8-bit quantization for reduced memory (CUDA only)
        """
        self.model_id = model_id
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"Loading {model_id}...")
        print(f"Device: {self.device}, Quantize: {quantize and self.device == 'cuda'}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Use 8-bit quantization to reduce memory footprint (CUDA only)
        kwargs = {
            "trust_remote_code": True,
        }
        
        if quantize and self.device == "cuda":
            # Use device_map="auto" to split between GPU and CPU with float16
            # This automatically distributes layers to fit in available memory
            kwargs["device_map"] = "auto"
            kwargs["torch_dtype"] = torch.float16
            print("Using device_map=auto with float16 (GPU+CPU split)")
        else:
            # For CPU, use float32 (no quantization)
            kwargs["torch_dtype"] = torch.float32
            if self.device == "cpu":
                print("Using float32 on CPU (slower but works)")
        
        # Use eager attention to avoid cache compatibility issues
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            attn_implementation="eager",  # Avoid cache issues with device_map
            **kwargs
        )
        print(f"Model loaded successfully on {self.device}")
    
    def generate(self, messages: list[ChatMessage], **kwargs) -> str:
        """Generate text from messages (required by smolagents).
        
        Args:
            messages: List of ChatMessage objects
            **kwargs: Additional generation args
        
        Returns:
            Generated text
        """
        # Convert messages to prompt text
        prompt_text = ""
        for msg in messages:
            if msg.role == "user":
                prompt_text += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                prompt_text += f"Assistant: {msg.content}\n"
            elif msg.role == "system":
                prompt_text += f"System: {msg.content}\n"
        
        prompt_text += "Assistant:"
        
        # Set defaults for generation
        generation_kwargs = {
            "max_new_tokens": kwargs.get("max_new_tokens", 512),  # Reduce for faster generation
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "do_sample": kwargs.get("do_sample", True),
            "use_cache": False,  # Disable cache to avoid DynamicCache issues with device_map
        }
        
        inputs = self.tokenizer(prompt_text, return_tensors="pt")
        # Move inputs to the correct device (model may be split across devices)
        for key in inputs:
            if isinstance(inputs[key], torch.Tensor):
                inputs[key] = inputs[key].to(next(self.model.parameters()).device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **generation_kwargs)
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the output
        return result[len(prompt_text):].strip()
    
    def __call__(self, prompt: str, stop_sequences: list[str] | None = None, **kwargs) -> str:
        """Generate text from prompt (for backward compatibility).
        
        Args:
            prompt: Input prompt
            stop_sequences: List of stop sequences (not used)
            **kwargs: Additional generation args
        
        Returns:
            Generated text
        """
        # Set defaults for generation
        generation_kwargs = {
            "max_new_tokens": kwargs.get("max_new_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "do_sample": kwargs.get("do_sample", True),
        }
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **generation_kwargs)
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the output
        return result[len(prompt):].strip()
