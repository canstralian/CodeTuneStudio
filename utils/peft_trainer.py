import torch
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    PeftModel,
    prepare_model_for_kbit_training
)
from transformers import PreTrainedModel
from typing import Dict, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PEFTTrainer:
    """Handle Parameter-Efficient Fine-Tuning (PEFT) operations"""

    def __init__(self, 
                 model: PreTrainedModel,
                 peft_config: Optional[Dict] = None):
        """
        Initialize PEFT trainer with a base model

        Args:
            model: Base model to apply PEFT
            peft_config: Configuration for PEFT setup
        """
        self.base_model = model
        self.peft_config = peft_config or self.get_default_peft_config()
        self.peft_model: Optional[PeftModel] = None

    def get_default_peft_config(self) -> Dict:
        """Get default LoRA configuration"""
        return {
            "r": 16,  # Rank of update matrices
            "lora_alpha": 32,  # Alpha parameter for LoRA scaling
            "target_modules": ["q_proj", "v_proj"],  # Which modules to apply PEFT
            "lora_dropout": 0.05,
            "bias": "none",
            "task_type": TaskType.CAUSAL_LM
        }

    def prepare_for_training(self) -> None:
        """Prepare model for PEFT training"""
        try:
            logger.info("Preparing model for PEFT training")
            
            # Prepare for 8-bit training if using quantization
            if getattr(self.base_model, "is_quantized", False):
                self.base_model = prepare_model_for_kbit_training(self.base_model)
            
            # Create LoRA config
            lora_config = LoraConfig(
                r=self.peft_config["r"],
                lora_alpha=self.peft_config["lora_alpha"],
                target_modules=self.peft_config["target_modules"],
                lora_dropout=self.peft_config["lora_dropout"],
                bias=self.peft_config["bias"],
                task_type=self.peft_config["task_type"]
            )

            # Get PEFT model
            self.peft_model = get_peft_model(self.base_model, lora_config)
            
            # Print trainable parameters info
            self.print_trainable_parameters()
            
            logger.info("Model prepared for PEFT training successfully")
        except Exception as e:
            logger.error(f"Error preparing model for PEFT: {str(e)}")
            raise

    def print_trainable_parameters(self) -> None:
        """Print information about trainable parameters"""
        try:
            if self.peft_model is None:
                raise ValueError("PEFT model not initialized")
                
            trainable_params = 0
            all_param = 0
            
            for _, param in self.peft_model.named_parameters():
                num_params = param.numel()
                all_param += num_params
                if param.requires_grad:
                    trainable_params += num_params
                    
            logger.info(
                f"trainable params: {trainable_params:,d} || "
                f"all params: {all_param:,d} || "
                f"trainable%: {100 * trainable_params / all_param:.2f}%"
            )
        except Exception as e:
            logger.error(f"Error printing trainable parameters: {str(e)}")
            raise

    def save_peft_model(self, save_path: str) -> None:
        """Save PEFT model adapter weights"""
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
        """Load PEFT model adapter weights"""
        try:
            logger.info(f"Loading PEFT model from {load_path}")
            if self.base_model is None:
                raise ValueError("Base model not initialized")
                
            self.peft_model = PeftModel.from_pretrained(
                self.base_model,
                load_path
            )
            logger.info("PEFT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading PEFT model: {str(e)}")
            raise
