import numpy as np


def mock_training_step():
    """
    Generate mock training metrics and convert to native Python types
    """
    # Generate random values and convert to native Python float
    train_loss = float(2 * np.exp(-0.1 * np.random.rand()))
    eval_loss = float(train_loss + 0.1 * np.random.randn())
    return train_loss, eval_loss
