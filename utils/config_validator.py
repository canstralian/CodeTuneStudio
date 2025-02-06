def validate_config(config):
    """
    Validate training configuration parameters
    """
    errors = []
    
    if config["batch_size"] > 128:
        errors.append("Batch size must be <= 128")
        
    if config["learning_rate"] > 1e-2:
        errors.append("Learning rate must be <= 0.01")
        
    if config["max_seq_length"] > 512:
        errors.append("Maximum sequence length must be <= 512")
        
    if config["epochs"] > 100:
        errors.append("Number of epochs must be <= 100")
        
    return errors
