import os
import logging
from typing import Optional, Dict, Any
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
from contextlib import contextmanager
import functools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DistributedTrainingError(Exception):
    """Custom exception for distributed training errors"""
    pass

def require_initialized(func):
    """Decorator to ensure distributed environment is initialized"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_initialized:
            raise DistributedTrainingError("Distributed environment not initialized")
        return func(self, *args, **kwargs)
    return wrapper

class DistributedTrainer:
    """Handle distributed training operations with enhanced error handling"""

    def __init__(self, 
                 world_size: Optional[int] = None,
                 backend: str = 'nccl'):
        """
        Initialize distributed trainer

        Args:
            world_size: Number of processes for distributed training
            backend: Distributed backend ('nccl' for GPU, 'gloo' for CPU)
        """
        self.world_size = world_size or torch.cuda.device_count()
        self.backend = backend
        self.is_initialized = False
        self.rank = None
        
        if self.world_size < 1:
            raise DistributedTrainingError("No available devices for distributed training")
        
        logger.info(f"Initializing distributed trainer with {self.world_size} processes")

    @contextmanager
    def distribute_context(self, rank: int):
        """
        Context manager for distributed process initialization

        Args:
            rank: Process rank
        """
        try:
            self.init_process(rank)
            yield
        finally:
            self.cleanup()

    def init_process(self, rank: int):
        """
        Initialize distributed process with error handling

        Args:
            rank: Process rank
        """
        try:
            os.environ['MASTER_ADDR'] = 'localhost'
            os.environ['MASTER_PORT'] = '12355'
            
            dist.init_process_group(
                backend=self.backend,
                rank=rank,
                world_size=self.world_size
            )
            
            self.rank = rank
            self.is_initialized = True
            
            # Set device for this process
            torch.cuda.set_device(rank)
            logger.info(f"Process {rank} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize process {rank}: {str(e)}")
            raise DistributedTrainingError(f"Process initialization failed: {str(e)}")

    @require_initialized
    def prepare_model(self, model: torch.nn.Module) -> DistributedDataParallel:
        """
        Prepare model for distributed training

        Args:
            model: PyTorch model to distribute

        Returns:
            Distributed model wrapper
        """
        try:
            model = model.to(self.rank)
            distributed_model = DistributedDataParallel(
                model,
                device_ids=[self.rank],
                output_device=self.rank,
                find_unused_parameters=True
            )
            return distributed_model
            
        except Exception as e:
            logger.error(f"Failed to prepare distributed model: {str(e)}")
            raise DistributedTrainingError(f"Model preparation failed: {str(e)}")

    @require_initialized
    def prepare_dataloader(self, 
                         dataloader: torch.utils.data.DataLoader
                         ) -> torch.utils.data.DataLoader:
        """
        Prepare dataloader for distributed training

        Args:
            dataloader: Original dataloader

        Returns:
            Distributed dataloader
        """
        try:
            sampler = torch.utils.data.distributed.DistributedSampler(
                dataloader.dataset,
                num_replicas=self.world_size,
                rank=self.rank
            )
            
            return torch.utils.data.DataLoader(
                dataloader.dataset,
                batch_size=dataloader.batch_size,
                sampler=sampler,
                num_workers=dataloader.num_workers,
                pin_memory=True
            )
            
        except Exception as e:
            logger.error(f"Failed to prepare distributed dataloader: {str(e)}")
            raise DistributedTrainingError(f"Dataloader preparation failed: {str(e)}")

    def cleanup(self):
        """Cleanup distributed training resources"""
        if self.is_initialized:
            try:
                dist.destroy_process_group()
                self.is_initialized = False
                self.rank = None
                logger.info("Distributed training resources cleaned up")
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")

    @staticmethod
    def get_available_devices() -> Dict[str, Any]:
        """
        Get information about available devices

        Returns:
            Dictionary containing device information
        """
        try:
            info = {
                'cuda_available': torch.cuda.is_available(),
                'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'devices': []
            }
            
            if info['cuda_available']:
                for i in range(info['device_count']):
                    device = torch.cuda.get_device_properties(i)
                    info['devices'].append({
                        'name': device.name,
                        'total_memory': device.total_memory,
                        'major': device.major,
                        'minor': device.minor
                    })
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting device information: {str(e)}")
            return {'error': str(e)}
