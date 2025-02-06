import torch
from accelerate import init_empty_weights
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer,
    LogitsProcessorList,
    MinLengthLogitsProcessor,
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper
)
from transformers.generation import GenerationConfig
from typing import Optional, Dict, Any, List, Union, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelInference:
    """Handle large model inference using Accelerate library with enhanced logits processing"""

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

    def get_default_logits_processors(self, 
                                    min_length: int = 10,
                                    temperature: float = 0.7,
                                    top_k: int = 50,
                                    top_p: float = 0.9) -> LogitsProcessorList:
        """Get default set of logits processors for controlled generation"""
        try:
            processors = LogitsProcessorList()

            # Add minimum length constraint
            if min_length > 0:
                processors.append(MinLengthLogitsProcessor(min_length))

            # Add temperature sampling
            if temperature != 1.0:
                processors.append(TemperatureLogitsWarper(temperature))

            # Add top-k sampling
            if top_k > 0:
                processors.append(TopKLogitsWarper(top_k))

            # Add top-p sampling
            if top_p < 1.0:
                processors.append(TopPLogitsWarper(top_p))

            return processors
        except Exception as e:
            logger.error(f"Error creating logits processors: {str(e)}")
            raise

    def generate_text(self, 
                     prompt: str,
                     max_length: int = 100,
                     generation_config: Optional[Dict[str, Any]] = None,
                     logits_processors: Optional[List] = None,
                     return_full_output: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Generate text using the loaded model with enhanced control and output options

        Args:
            prompt: Input text to generate from
            max_length: Maximum length of generated text
            generation_config: Configuration for text generation
            logits_processors: List of logits processors for controlling generation
            return_full_output: If True, returns full generation output object

        Returns:
            Either generated text string or full generation output dictionary
        """
        try:
            if self.model is None or self.tokenizer is None:
                raise ValueError("Model or tokenizer not initialized")

            # Set default generation config if none provided
            if generation_config is None:
                generation_config = GenerationConfig(
                    max_length=max_length,
                    num_beams=4,
                    temperature=0.7,
                    no_repeat_ngram_size=2,
                    min_length=10,
                    top_k=50,
                    top_p=0.9,
                    return_dict_in_generate=return_full_output,
                    output_scores=return_full_output,
                    output_attentions=return_full_output,
                    output_hidden_states=return_full_output
                )

            # Initialize default logits processors if none provided
            if logits_processors is None:
                logits_processors = self.get_default_logits_processors(
                    min_length=generation_config.min_length,
                    temperature=generation_config.temperature,
                    top_k=generation_config.top_k,
                    top_p=generation_config.top_p
                )

            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            # Generate text with logits processors
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    generation_config=generation_config,
                    logits_processor=logits_processors
                )

            if not return_full_output:
                return self.tokenizer.decode(
                    outputs[0] if isinstance(outputs, torch.Tensor) else outputs.sequences[0],
                    skip_special_tokens=True
                )
            return outputs

        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
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