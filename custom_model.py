"""Custom model class for direct Hugging Face model support."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from smolagents.models import Model


class DirectTransformersModel(Model):
    """Direct Transformers model without SmolAgents auto-detection."""
    
    def __init__(self, model_id: str = "microsoft/phi-3-medium-4k-instruct", device: str = None, quantize: bool = True):
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
        
        # Use 8-bit quantization to reduce memory footprint (CUDA only)
        kwargs = {
            "trust_remote_code": True,
        }
        
        if quantize and self.device == "cuda":
            # 8-bit quantization for CUDA
            try:
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_8bit_compute_dtype=torch.float16,
                )
                kwargs["quantization_config"] = quantization_config
                print("Using 8-bit quantization")
            except Exception as e:
                print(f"Quantization failed: {e}, falling back to float16")
                kwargs["torch_dtype"] = torch.float16
        else:
            # For CPU, use float32 (no quantization)
            kwargs["torch_dtype"] = torch.float32
            if self.device == "cpu":
                print("Using float32 on CPU (slower but works)")
        
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
        if self.device == "cpu":
            self.model.to(self.device)
        print(f"Model loaded successfully on {self.device}")
    
    def __call__(self, prompt: str, stop_sequences: list[str] | None = None, **kwargs) -> str:
        """Generate text from prompt.
        
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
