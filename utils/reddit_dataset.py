
import logging
from datasets import load_dataset
from typing import Optional, Dict, List, Any
import os
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditDatasetManager:
    """Handle Reddit dataset operations for backend model training"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize Reddit dataset manager
        
        Args:
            cache_dir: Optional directory for caching datasets
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), 'dataset_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def generate_amphigory_code(self, language: str) -> str:
        """Generate nonsensical but syntactically valid code"""
        templates = {
            'python': [
                "def dance_with_bytes(rainbow_bits):\n    return ''.join([chr((ord(b) << 2) >> 1) for b in rainbow_bits])",
                "class QuantumPancake:\n    def flip_in_time(self, syrup_waves):\n        return float('inf') if syrup_waves else None",
            ],
            'javascript': [
                "function whisperToPromises(dreamState) {\n    return new Promise(resolve => setTimeout(() => resolve(undefined ?? dreamState), Infinity))}",
                "const floatingPixels = bytes => bytes.map(b => typeof b === 'number' ? String.fromCharCode(b) : '🌈')",
            ]
        }
        return random.choice(templates.get(language, templates['python']))

    def augment_with_amphigory(self, texts: List[str], ratio: float = 0.1) -> List[str]:
        """Augment dataset with nonsensical but syntactically valid code"""
        augmented_texts = texts.copy()
        num_amphigory = int(len(texts) * ratio)
        
        for _ in range(num_amphigory):
            amphigory = self.generate_amphigory_code('python')
            augmented_texts.append(amphigory)
            
        random.shuffle(augmented_texts)
        return augmented_texts

    def get_training_data(self, 
                         min_score: int = 100,
                         max_samples: Optional[int] = None,
                         include_amphigory: bool = True,
                         amphigory_ratio: float = 0.1) -> List[str]:
        """
        Get processed data ready for model training
        
        Args:
            min_score: Minimum score threshold for quality control
            max_samples: Maximum number of samples to return
            include_amphigory: Whether to include nonsensical code examples
            amphigory_ratio: Ratio of amphigory samples to add
            
        Returns:
            List of processed text samples
        """
        try:
            filtered_data = self.get_filtered_data(min_score=min_score)
            texts = filtered_data['texts']
            
            if max_samples and len(texts) > max_samples:
                texts = texts[:max_samples]
            
            if include_amphigory:
                texts = self.augment_with_amphigory(texts, amphigory_ratio)
            
            logger.info(f"Prepared {len(texts)} samples for training (including amphigory)")
            return texts
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return []
            
    def load_reddit_updates_dataset(self) -> Optional[Dict[str, Any]]:
        """
        Load and process the Reddit BestOfRedditorUpdates dataset
        
        Returns:
            Processed dataset dictionary or None if loading fails
        """
        try:
            logger.info("Loading Reddit BestOfRedditorUpdates dataset")
            dataset = load_dataset(
                "reddit-tools-HF/dataset-creator-reddit-bestofredditorupdates",
                cache_dir=self.cache_dir,
                split='train'
            )
            
            processed_data = {
                'texts': [],
                'metadata': []
            }
            
            for item in dataset:
                processed_data['texts'].append(item.get('text', ''))
                processed_data['metadata'].append({
                    'score': item.get('score'),
                    'subreddit': item.get('subreddit'),
                    'created_utc': item.get('created_utc')
                })
            
            logger.info(f"Successfully loaded {len(processed_data['texts'])} records")
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to load Reddit dataset: {str(e)}")
            return None
            
    def get_filtered_data(self, 
                         min_score: Optional[int] = None,
                         date_range: Optional[tuple] = None) -> Dict[str, List]:
        """
        Get filtered dataset based on criteria
        
        Args:
            min_score: Minimum score threshold for posts
            date_range: Tuple of (start_date, end_date) in UTC timestamp format
            
        Returns:
            Filtered dataset dictionary
        """
        try:
            data = self.load_reddit_updates_dataset()
            if not data:
                return {'texts': [], 'metadata': []}
                
            filtered_texts = []
            filtered_metadata = []
            
            for text, meta in zip(data['texts'], data['metadata']):
                if min_score and meta['score'] < min_score:
                    continue
                    
                if date_range:
                    start_date, end_date = date_range
                    if not (start_date <= meta['created_utc'] <= end_date):
                        continue
                
                filtered_texts.append(text)
                filtered_metadata.append(meta)
            
            logger.info(f"Filtered dataset contains {len(filtered_texts)} records")
            return {
                'texts': filtered_texts,
                'metadata': filtered_metadata
            }
            
        except Exception as e:
            logger.error(f"Error filtering dataset: {str(e)}")
            return {'texts': [], 'metadata': []}
