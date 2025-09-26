import argilla as rg
from datasets import Dataset
import logging
from typing import Optional, Dict, Any, List
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArgillaDatasetManager:
    """Handle Argilla dataset operations for model fine-tuning"""

    def __init__(
        self,
        workspace: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Argilla dataset manager

        Args:
            workspace: Argilla workspace name
            api_url: Argilla API URL
            api_key: Argilla API key
        """
        self.workspace = workspace or os.getenv("ARGILLA_WORKSPACE")
        self._init_argilla(api_url, api_key)

    def _init_argilla(self, api_url: Optional[str], api_key: Optional[str]) -> None:
        """Initialize Argilla client"""
        try:
            # Using the new login method instead of init
            rg.login(
                api_url=api_url
                or os.getenv("ARGILLA_API_URL", "https://api.argilla.io"),
                api_key=api_key or os.getenv("ARGILLA_API_KEY"),
                workspace=self.workspace,
            )
            logger.info("Argilla client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Argilla client: {str(e)}")
            raise

    def list_datasets(self) -> List[str]:
        """List available datasets in the workspace"""
        try:
            # Using the new method to list datasets
            datasets = rg.get_datasets()
            return [ds.name for ds in datasets]
        except Exception as e:
            logger.error(f"Failed to list datasets: {str(e)}")
            raise

    def load_dataset(
        self,
        dataset_name: str,
        query: Optional[str] = None,
        filter_by: Optional[Dict[str, Any]] = None,
    ) -> Dataset:
        """
        Load and prepare an Argilla dataset for fine-tuning

        Args:
            dataset_name: Name of the dataset in Argilla
            query: Optional query to filter records
            filter_by: Optional dictionary of filters

        Returns:
            HuggingFace dataset object
        """
        try:
            # Load dataset from Argilla using the new method
            dataset = rg.get_dataset(
                name=dataset_name, query=query, filter_by=filter_by
            )

            # Convert to HuggingFace dataset format
            hf_dataset = Dataset.from_dict(
                {
                    "text": [record.text for record in dataset],
                    "label": [
                        record.annotation
                        for record in dataset
                        if hasattr(record, "annotation")
                    ],
                    "metadata": [
                        record.metadata
                        for record in dataset
                        if hasattr(record, "metadata")
                    ],
                }
            )

            logger.info(
                f"Successfully loaded dataset '{dataset_name}' with {len(hf_dataset)} records"
            )
            return hf_dataset

        except Exception as e:
            logger.error(f"Failed to load dataset '{dataset_name}': {str(e)}")
            raise

    def prepare_for_training(
        self, dataset: Dataset, text_column: str = "text", label_column: str = "label"
    ) -> Dataset:
        """
        Prepare dataset for training by ensuring proper format

        Args:
            dataset: HuggingFace dataset object
            text_column: Name of the column containing input text
            label_column: Name of the column containing labels/code

        Returns:
            Processed dataset ready for training
        """
        try:
            # Ensure required columns exist
            if text_column not in dataset.column_names:
                raise ValueError(f"Dataset missing required column: {text_column}")
            if label_column not in dataset.column_names:
                raise ValueError(f"Dataset missing required column: {label_column}")

            # Remove any rows with missing values
            dataset = dataset.filter(
                lambda x: x[text_column] is not None and x[label_column] is not None
            )

            logger.info(
                f"Dataset prepared for training with {len(dataset)} valid examples"
            )
            return dataset

        except Exception as e:
            logger.error(f"Failed to prepare dataset for training: {str(e)}")
            raise
