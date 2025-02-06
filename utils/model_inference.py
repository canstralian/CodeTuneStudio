import torch
from accelerate import init_empty_weights
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelInference:
    """Handle large model inference using Accelerate library"""
    
    def __init__(self, model_name: str, device_map: str = "auto"):
        self.model_name = model_name
        self.device_map = device_map
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None

    def initialize_model(self) -> None:
        """Initialize model with empty weights"""
        try:
            logger.info(f"Initializing empty model: {self.model_name}")
            with init_empty_weights():
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16
                )
            logger.info("Empty model initialization successful")
        except Exception as e:
            logger.error(f"Error initializing empty model: {str(e)}")
            raise

    def load_model_weights(self, weights_path: str) -> None:
        """Load pre-trained weights into the model"""
        try:
            logger.info(f"Loading model weights from: {weights_path}")
            if self.model is None:
                raise ValueError("Model not initialized. Call initialize_model first.")
            
            state_dict = torch.load(weights_path, map_location="cpu")
            self.model.load_state_dict(state_dict)
            logger.info("Model weights loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model weights: {str(e)}")
            raise

    def load_pretrained(self) -> None:
        """Load pre-trained model using device map for efficient distribution"""
        try:
            logger.info(f"Loading pre-trained model: {self.model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=self.device_map,
                torch_dtype=torch.float16
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("Pre-trained model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading pre-trained model: {str(e)}")
            raise

    def generate_text(self, prompt: str, 
                     max_length: int = 100,
                     generation_config: Optional[Dict[str, Any]] = None) -> str:
        """Generate text using the loaded model"""
        try:
            if self.model is None or self.tokenizer is None:
                raise ValueError("Model or tokenizer not initialized")

            # Set default generation config if none provided
            if generation_config is None:
                generation_config = {
                    "max_length": max_length,
                    "num_beams": 4,
                    "temperature": 0.7,
                    "no_repeat_ngram_size": 2
                }

            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_config)
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Clean up model resources"""
        try:
            if self.model is not None:
                del self.model
            if self.tokenizer is not None:
                del self.tokenizer
            torch.cuda.empty_cache()
            logger.info("Model resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up resources: {str(e)}")
            raise
