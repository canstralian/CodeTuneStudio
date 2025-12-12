import logging
import os
from typing import Any

import argilla as rg
from datasets import Dataset

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArgillaDatasetManager:
    """Handle Argilla dataset operations for model fine-tuning using Argilla 2.x API"""

    def __init__(
        self,
        workspace: str | None = None,
        api_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize Argilla dataset manager

        Args:
            workspace: Argilla workspace name
            api_url: Argilla API URL (default: http://localhost:6900)
            api_key: Argilla API key
        """
        self.workspace = workspace or os.getenv("ARGILLA_WORKSPACE", "default")
        self._init_argilla(api_url, api_key)

    def _init_argilla(self, api_url: str | None, api_key: str | None) -> None:
        """Initialize Argilla client using Argilla 2.x API"""
        try:
            # Initialize Argilla 2.x client
            self.client = rg.Argilla(
                api_url=api_url
                or os.getenv("ARGILLA_API_URL", "http://localhost:6900"),
                api_key=api_key or os.getenv("ARGILLA_API_KEY"),
            )
            logger.info("Argilla client initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize Argilla client: {e!s}")
            raise

    def list_datasets(self) -> list[str]:
        """List available datasets in the workspace using Argilla 2.x API"""
        try:
            # Get datasets from the client's datasets collection
            datasets_list = list(self.client.datasets)
            return [ds.name for ds in datasets_list]
        except Exception as e:
            logger.exception(f"Failed to list datasets: {e!s}")
            return []  # Return empty list on error instead of raising

    def load_dataset(
        self,
        dataset_name: str,
        query: str | None = None,
        filter_by: dict[str, Any] | None = None,
    ) -> Dataset:
        """
        Load and prepare an Argilla dataset for fine-tuning using Argilla 2.x API

        Args:
            dataset_name: Name of the dataset in Argilla
            query: Optional query to filter records (for future use)
            filter_by: Optional dictionary of filters (for future use)

        Returns:
            HuggingFace dataset object
        """
        try:
            # Load dataset from Argilla 2.x client
            # Access dataset by name from the datasets collection
            argilla_dataset = None
            for ds in self.client.datasets:
                if ds.name == dataset_name:
                    argilla_dataset = ds
                    break
            
            if not argilla_dataset:
                raise ValueError(f"Dataset '{dataset_name}' not found")
            
            # Fetch all records from the dataset
            records = list(argilla_dataset.records)
            
            # Convert to HuggingFace dataset format
            # Extract text fields and responses from records
            dataset_dict = {
                "text": [],
                "label": [],
                "metadata": [],
            }
            
            for record in records:
                # Get the text from the first text field
                text_fields = [f.value for f in record.fields if hasattr(f, 'value')]
                dataset_dict["text"].append(text_fields[0] if text_fields else "")
                
                # Get responses/annotations if available
                responses = record.responses if hasattr(record, 'responses') else []
                # Safely extract values from first response
                label_value = None
                if responses and len(responses) > 0:
                    label_value = getattr(responses[0], 'values', None)
                dataset_dict["label"].append(label_value)
                
                # Get metadata if available
                dataset_dict["metadata"].append(
                    record.metadata if hasattr(record, 'metadata') else {}
                )
            
            hf_dataset = Dataset.from_dict(dataset_dict)

            logger.info(
                f"Successfully loaded dataset '{dataset_name}' with "
                f"{len(hf_dataset)} records"
            )
            return hf_dataset

        except Exception as e:
            logger.exception(f"Failed to load dataset '{dataset_name}': {e!s}")
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
                msg = f"Dataset missing required column: {text_column}"
                raise ValueError(msg)
            if label_column not in dataset.column_names:
                msg = f"Dataset missing required column: {label_column}"
                raise ValueError(msg)

            # Remove any rows with missing values
            dataset = dataset.filter(
                lambda x: x[text_column] is not None and x[label_column] is not None
            )

            logger.info(
                f"Dataset prepared for training with {len(dataset)} valid examples"
            )
            return dataset

        except Exception as e:
            logger.exception(f"Failed to prepare dataset for training: {e!s}")
            raise
