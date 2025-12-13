"""
Example: Optimized data processing code (AFTER refactoring)

This module demonstrates the improvements made by CodeTuneStudio's
refactoring agent, addressing performance, readability, and maintainability.
"""
from typing import Dict, List, Optional, Set


def process_data(data_list: List[int]) -> str:
    """
    Process a list of data items efficiently using list comprehension.
    
    Args:
        data_list: List of integers to process
        
    Returns:
        Comma-separated string of processed values
        
    Optimization: Uses list comprehension and str.join() instead of
    inefficient string concatenation in loops.
    """
    # Optimization 1: List comprehension + join (O(n) vs O(n²))
    processed = [item * 2 for item in data_list]
    return ",".join(str(item) for item in processed)


def find_duplicates(items: List[int]) -> List[int]:
    """
    Find duplicates efficiently using set operations (O(n) complexity).
    
    Args:
        items: List of integers to check for duplicates
        
    Returns:
        List of duplicate values found
        
    Optimization: Uses set for O(1) lookups instead of O(n²) nested loops.
    """
    # Optimization 2: Set-based duplicate detection (O(n) vs O(n²))
    seen: Set[int] = set()
    duplicates: Set[int] = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)


def calculate_statistics(numbers: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics in a single pass through the data.
    
    Args:
        numbers: List of numbers to analyze
        
    Returns:
        Dictionary containing mean, variance, min, and max
        
    Raises:
        ValueError: If the input list is empty
        
    Optimization: Single-pass algorithm reduces time complexity from O(3n) to O(n).
    """
    # Optimization 3: Single-pass statistics calculation
    if not numbers:
        raise ValueError("Cannot calculate statistics on empty list")
    
    # Calculate all statistics in one pass
    total = 0.0
    sum_squares = 0.0
    minimum = numbers[0]
    maximum = numbers[0]
    
    for num in numbers:
        total += num
        sum_squares += num * num
        minimum = min(minimum, num)
        maximum = max(maximum, num)
    
    n = len(numbers)
    mean = total / n
    variance = (sum_squares / n) - (mean * mean)
    
    return {
        'mean': mean,
        'variance': variance,
        'min': minimum,
        'max': maximum
    }


class DataProcessor:
    """
    Data processor with improved encapsulation and error handling.
    
    Improvements:
    - Private attributes to prevent external mutation
    - Input validation
    - Proper error handling
    - Type hints for clarity
    """
    
    def __init__(self) -> None:
        """Initialize the processor with empty state."""
        # Improvement 4: Private attributes for better encapsulation
        self._data: List[int] = []
        self._processed: bool = False
        self._cache: Dict[int, int] = {}
    
    def add_data(self, item: int) -> None:
        """
        Add data with validation.
        
        Args:
            item: Integer value to add
            
        Raises:
            TypeError: If item is not an integer
            ValueError: If attempting to add data after processing
        """
        # Improvement 5: Input validation
        if not isinstance(item, int):
            raise TypeError(f"Expected int, got {type(item).__name__}")
        
        if self._processed:
            raise ValueError("Cannot add data after processing")
        
        self._data.append(item)
    
    def process(self) -> None:
        """
        Process all data with error handling.
        
        Raises:
            RuntimeError: If processing fails
        """
        # Improvement 6: Error handling and validation
        if not self._data:
            raise ValueError("No data to process")
        
        try:
            self._cache = {item: item * 2 for item in self._data}
            self._processed = True
        except Exception as e:
            raise RuntimeError(f"Processing failed: {e}") from e
    
    def get_result(self, key: int) -> Optional[int]:
        """
        Get processed result safely.
        
        Args:
            key: The key to lookup
            
        Returns:
            Processed value or None if key not found
            
        Raises:
            RuntimeError: If results not yet processed
        """
        if not self._processed:
            raise RuntimeError("Data not yet processed. Call process() first.")
        
        return self._cache.get(key)
    
    @property
    def is_processed(self) -> bool:
        """Check if data has been processed."""
        return self._processed
    
    @property
    def data_count(self) -> int:
        """Get the count of data items."""
        return len(self._data)
