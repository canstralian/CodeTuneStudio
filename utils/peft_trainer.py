from typing import Dict, Optional, Union, Any
import torch
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    PeftModel,
    prepare_model_for_kbit_training
)
from transformers import PreTrainedModel
import logging
from contextlib import contextmanager

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PEFTTrainer:
    """
    Handle Parameter-Efficient Fine-Tuning (PEFT) operations with enhanced error handling
    and resource management.
    """

    def __init__(self, 
                 model: PreTrainedModel,
                 peft_config: Optional[Dict[str, Any]] = None,
                 device: Optional[str] = None):
        """
        Initialize PEFT trainer with improved configuration options

        Args:
            model: Base model to apply PEFT
            peft_config: Configuration for PEFT setup
            device: Target device for training ('cpu', 'cuda', or None for auto-detection)
        """
        self.base_model = model
        self.peft_config = peft_config or self.get_default_peft_config()
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.peft_model: Optional[PeftModel] = None

        logger.info(f"Initializing PEFT trainer on device: {self.device}")

    def get_default_peft_config(self) -> Dict[str, Any]:
        """
        Get default LoRA configuration with optimized parameters

        Returns:
            Dictionary containing default PEFT configuration
        """
        return {
            "r": 16,  # Rank of update matrices
            "lora_alpha": 32,  # Alpha parameter for LoRA scaling
            "target_modules": ["q_proj", "v_proj"],  # Which modules to apply PEFT
            "lora_dropout": 0.05,
            "bias": "none",
            "task_type": TaskType.CAUSAL_LM
        }

    @contextmanager
    def model_context(self):
        """Context manager for proper model cleanup"""
        try:
            yield
        finally:
            if self.peft_model:
                self.cleanup()

    def validate_config(self) -> None:
        """Validate PEFT configuration parameters"""
        required_keys = ["r", "lora_alpha", "target_modules", "task_type"]
        for key in required_keys:
            if key not in self.peft_config:
                raise ValueError(f"Missing required configuration key: {key}")

    def prepare_for_training(self) -> None:
        """
        Prepare model for PEFT training with enhanced error handling
        and resource management
        """
        try:
            logger.info("Preparing model for PEFT training")
            self.validate_config()

            # Prepare for 8-bit training if using quantization
            if getattr(self.base_model, "is_quantized", False):
                self.base_model = prepare_model_for_kbit_training(
                    self.base_model,
                    use_gradient_checkpointing=True
                )

            # Create LoRA config with validated parameters
            lora_config = LoraConfig(
                r=self.peft_config["r"],
                lora_alpha=self.peft_config["lora_alpha"],
                target_modules=self.peft_config["target_modules"],
                lora_dropout=self.peft_config["lora_dropout"],
                bias=self.peft_config["bias"],
                task_type=self.peft_config["task_type"]
            )

            # Get PEFT model with proper device placement
            self.peft_model = get_peft_model(self.base_model, lora_config)
            self.peft_model.to(self.device)

            self.print_trainable_parameters()
            logger.info("Model prepared for PEFT training successfully")

        except Exception as e:
            logger.error(f"Error preparing model for PEFT: {str(e)}")
            self.cleanup()
            raise

    def print_trainable_parameters(self) -> None:
        """Print information about trainable parameters with enhanced details"""
        try:
            if self.peft_model is None:
                raise ValueError("PEFT model not initialized")

            trainable_params = 0
            all_param = 0

            for name, param in self.peft_model.named_parameters():
                num_params = param.numel()
                all_param += num_params
                if param.requires_grad:
                    trainable_params += num_params
                    logger.debug(f"Trainable parameter: {name} ({num_params:,d} params)")

            logger.info(
                f"trainable params: {trainable_params:,d} || "
                f"all params: {all_param:,d} || "
                f"trainable%: {100 * trainable_params / all_param:.2f}%"
            )
        except Exception as e:
            logger.error(f"Error analyzing trainable parameters: {str(e)}")
            raise

    def save_peft_model(self, save_path: str) -> None:
        """
        Save PEFT model adapter weights with proper error handling

        Args:
            save_path: Path to save the model
        """
        try:
            if self.peft_model is None:
                raise ValueError("PEFT model not initialized")

            logger.info(f"Saving PEFT model to {save_path}")
            self.peft_model.save_pretrained(save_path)
            logger.info("PEFT model saved successfully")
        except Exception as e:
            logger.error(f"Error saving PEFT model: {str(e)}")
            raise

    def load_peft_model(self, load_path: str) -> None:
        """
        Load PEFT model adapter weights with validation

        Args:
            load_path: Path to load the model from
        """
        try:
            logger.info(f"Loading PEFT model from {load_path}")
            if self.base_model is None:
                raise ValueError("Base model not initialized")

            self.peft_model = PeftModel.from_pretrained(
                self.base_model,
                load_path,
                device_map=self.device
            )
            logger.info("PEFT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading PEFT model: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Clean up resources and free memory"""
        try:
            if self.peft_model is not None:
                self.peft_model.cpu()
                del self.peft_model
                torch.cuda.empty_cache()
                self.peft_model = None
                logger.info("PEFT model resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")