import numpy as np

def mock_training_step():
    """
    Generate mock training metrics
    """
    train_loss = 2 * np.exp(-0.1 * np.random.rand())
    eval_loss = train_loss + 0.1 * np.random.randn()
    return train_loss, eval_loss
