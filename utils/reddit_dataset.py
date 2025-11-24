import logging
from typing import Optional, Dict, List, Any, Tuple
import os
import random
from datasets import load_dataset
from tqdm import tqdm
import numpy as np
from functools import lru_cache

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RedditDatasetManager:
    """
    Handle Reddit dataset operations with enhanced validation and performance optimization
    """

    def __init__(self, cache_dir: Optional[str] = None, max_cache_size: int = 1000):
        """
        Initialize Reddit dataset manager with improved caching

        Args:
            cache_dir: Optional directory for caching datasets
            max_cache_size: Maximum number of items to cache in memory
        """
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "dataset_cache")
        self.max_cache_size = max_cache_size
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"Initialized RedditDatasetManager with cache at {self.cache_dir}")

    def validate_text(self, text: str) -> bool:
        """
        Validate text content for quality control

        Args:
            text: Text content to validate

        Returns:
            Boolean indicating if text passes validation
        """
        if not isinstance(text, str):
            return False

        # Basic quality checks
        min_length = 10
        max_length = 50000
        text_length = len(text)

        return (
            text_length >= min_length
            and text_length <= max_length
            and text.strip() != ""
            and not text.isspace()
        )

    def generate_amphigory_code(self, language: str) -> str:
        """
        Generate nonsensical but syntactically valid code with improved variety

        Args:
            language: Target programming language

        Returns:
            Generated code snippet
        """
        templates = {
            "python": [
                "def dance_with_bytes(rainbow_bits):\n    return ''.join([chr((ord(b) << 2) >> 1) for b in rainbow_bits])",
                "class QuantumPancake:\n    def flip_in_time(self, syrup_waves):\n        return float('inf') if syrup_waves else None",
                "async def dream_compiler(thoughts):\n    return await sorted(thoughts, key=lambda x: hash(str(x)))",
            ],
            "javascript": [
                "function whisperToPromises(dreamState) {\n    return new Promise(resolve => setTimeout(() => resolve(undefined ?? dreamState), Infinity))}",
                "const floatingPixels = bytes => bytes.map(b => typeof b === 'number' ? String.fromCharCode(b) : '🌈')",
                "class TimeTravel {\n    static async rewind(memories) {\n        return [...memories].reverse().filter(Boolean)}",
            ],
        }

        available_templates = templates.get(language.lower(), templates["python"])
        return random.choice(available_templates)

    @lru_cache(maxsize=128)
    def augment_with_amphigory(
        self, texts: Tuple[str, ...], ratio: float = 0.1
    ) -> List[str]:
        """
        Augment dataset with nonsensical but syntactically valid code

        Args:
            texts: Tuple of text samples (converted from list for caching)
            ratio: Ratio of amphigory samples to add

        Returns:
            Augmented list of texts
        """
        if not 0 <= ratio <= 1:
            raise ValueError("Ratio must be between 0 and 1")

        augmented_texts = list(texts)
        num_amphigory = int(len(texts) * ratio)

        logger.info(f"Generating {num_amphigory} amphigory samples")

        languages = ["python", "javascript"]
        for _ in range(num_amphigory):
            language = random.choice(languages)
            amphigory = self.generate_amphigory_code(language)
            augmented_texts.append(amphigory)

        random.shuffle(augmented_texts)
        return augmented_texts

    def get_training_data(
        self,
        min_score: int = 100,
        max_samples: Optional[int] = None,
        include_amphigory: bool = True,
        amphigory_ratio: float = 0.1,
    ) -> List[str]:
        """
        Get processed data ready for model training with enhanced filtering

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
            texts = filtered_data["texts"]

            # Validate and clean texts
            texts = [text for text in texts if self.validate_text(text)]

            if max_samples and len(texts) > max_samples:
                texts = texts[:max_samples]

            if include_amphigory:
                # Convert to tuple for caching
                texts = self.augment_with_amphigory(tuple(texts), amphigory_ratio)

            logger.info(f"Prepared {len(texts)} samples for training")
            return texts

        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return []

    def load_reddit_updates_dataset(self) -> Optional[Dict[str, Any]]:
        """
        Load and process the Reddit dataset with batched processing

        Returns:
            Processed dataset dictionary or None if loading fails
        """
        try:
            logger.info("Loading Reddit BestOfRedditorUpdates dataset")
            dataset = load_dataset(
                "reddit-tools-HF/dataset-creator-reddit-bestofredditorupdates",
                cache_dir=self.cache_dir,
                split="train",
            )

            processed_data = {"texts": [], "metadata": []}

            # Process in batches for better memory efficiency
            batch_size = 1000
            for i in tqdm(range(0, len(dataset), batch_size)):
                batch = dataset[i : i + batch_size]

                processed_data["texts"].extend([item.get("text", "") for item in batch])
                processed_data["metadata"].extend(
                    [
                        {
                            "score": item.get("score"),
                            "subreddit": item.get("subreddit"),
                            "created_utc": item.get("created_utc"),
                        }
                        for item in batch
                    ]
                )

            logger.info(f"Successfully loaded {len(processed_data['texts'])} records")
            return processed_data

        except Exception as e:
            logger.error(f"Failed to load Reddit dataset: {str(e)}")
            return None

    def get_filtered_data(
        self,
        min_score: Optional[int] = None,
        date_range: Optional[Tuple[int, int]] = None,
    ) -> Dict[str, List]:
        """
        Get filtered dataset with improved validation

        Args:
            min_score: Minimum score threshold for posts
            date_range: Tuple of (start_date, end_date) in UTC timestamp format

        Returns:
            Filtered dataset dictionary
        """
        try:
            data = self.load_reddit_updates_dataset()
            if not data:
                return {"texts": [], "metadata": []}

            filtered_texts = []
            filtered_metadata = []

            # Use numpy for faster filtering
            scores = np.array([meta["score"] for meta in data["metadata"]])
            dates = np.array([meta["created_utc"] for meta in data["metadata"]])

            mask = np.ones(len(scores), dtype=bool)
            if min_score is not None:
                mask &= scores >= min_score

            if date_range:
                start_date, end_date = date_range
                mask &= (dates >= start_date) & (dates <= end_date)

            filtered_indices = np.where(mask)[0]

            filtered_texts = [data["texts"][i] for i in filtered_indices]
            filtered_metadata = [data["metadata"][i] for i in filtered_indices]

            logger.info(f"Filtered dataset contains {len(filtered_texts)} records")
            return {"texts": filtered_texts, "metadata": filtered_metadata}

        except Exception as e:
            logger.error(f"Error filtering dataset: {str(e)}")
            return {"texts": [], "metadata": []}
