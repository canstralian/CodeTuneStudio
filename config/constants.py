"""
Configuration constants for CodeTuneStudio.

This module centralizes all magic numbers and hardcoded values
to improve maintainability and make configuration changes easier.
"""

# Database Connection Pool Configuration
DATABASE_POOL_CONFIG = {
    "pool_size": 10,  # Number of connections to maintain in the pool
    "max_overflow": 20,  # Max additional connections beyond pool_size
    "pool_timeout": 30,  # Seconds to wait for available connection
    "pool_recycle": 1800,  # Seconds before recycling connections (30 minutes)
}

# Distributed Training Configuration
DISTRIBUTED_TRAINING_CONFIG = {
    "master_addr": "localhost",  # Master node address for distributed training
    "master_port": "12355",  # Port for inter-process communication
    "backend": "nccl",  # Communication backend (nccl for GPU, gloo for CPU)
}

# Training Parameter Constraints
PARAMETER_CONSTRAINTS = {
    "batch_size": {
        "min": 1,
        "max": 128,
        "default": 16,
        "step": 1,
    },
    "learning_rate": {
        "min": 1e-6,
        "max": 1e-2,
        "default": 2e-5,
        "format": "%.2e",  # Scientific notation format
    },
    "epochs": {
        "min": 1,
        "max": 100,
        "default": 3,
        "step": 1,
    },
    "max_seq_length": {
        "min": 32,
        "max": 4096,
        "default": 512,
        "step": 32,
    },
    "warmup_steps": {
        "min": 0,
        "max": 10000,
        "default": 100,
        "step": 10,
    },
}

# Text Validation Configuration
TEXT_VALIDATION_CONFIG = {
    "min_length": 10,  # Minimum text length in characters
    "max_length": 50000,  # Maximum text length in characters
    "batch_size": 1000,  # Batch size for text processing
}

# Model Quantization Options
QUANTIZATION_CONFIG = {
    "bits_options": [4, 8, 16],  # Supported quantization bit depths
    "default_bits": 8,
    "compute_dtype": "float16",  # Default compute dtype for quantization
}

# LoRA Configuration Defaults
LORA_CONFIG = {
    "r": 8,  # LoRA attention dimension
    "alpha": 16,  # LoRA alpha parameter
    "dropout": 0.05,  # LoRA dropout rate
    "target_modules": ["q_proj", "v_proj"],  # Default target modules
}

# Cache Configuration
CACHE_CONFIG = {
    "lru_maxsize": 32,  # Max size for LRU caches
    "streamlit_ttl": 60,  # Streamlit cache TTL in seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
}

# UI Configuration
UI_CONFIG = {
    "page_title": "ML Model Fine-tuning",
    "page_icon": "🤖",
    "layout": "wide",
    "sidebar_state": "expanded",
}

# File Upload Limits
FILE_UPLOAD_CONFIG = {
    "max_file_size_mb": 200,  # Maximum file upload size in MB
    "allowed_extensions": [".pt", ".bin", ".safetensors"],
}

# Dataset Configuration
DATASET_CONFIG = {
    "preview_rows": 5,  # Number of rows to show in dataset preview
    "max_datasets_display": 100,  # Max datasets to display in selector
}
