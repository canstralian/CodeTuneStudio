```python
import logging
from datasets import load_dataset
from typing import Optional, Dict, List, Any
import os

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
            
            # Process and structure the data
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
                # Apply filters
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

    def get_training_data(self, 
                         min_score: int = 100,
                         max_samples: Optional[int] = None) -> List[str]:
        """
        Get processed data ready for model training
        
        Args:
            min_score: Minimum score threshold for quality control
            max_samples: Maximum number of samples to return
            
        Returns:
            List of processed text samples
        """
        try:
            filtered_data = self.get_filtered_data(min_score=min_score)
            texts = filtered_data['texts']
            
            if max_samples and len(texts) > max_samples:
                texts = texts[:max_samples]
            
            logger.info(f"Prepared {len(texts)} samples for training")
            return texts
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return []
```
