"""
Example: Inefficient data processing code (BEFORE refactoring)

This module demonstrates common performance anti-patterns that
CodeTuneStudio's refactoring agent can identify and optimize.
"""


def process_data(data_list):
    """Process a list of data items with inefficiencies"""
    # Anti-pattern 1: Creating unnecessary lists
    result = []
    for item in data_list:
        result.append(item * 2)
    
    # Anti-pattern 2: Inefficient string concatenation
    output = ""
    for item in result:
        output = output + str(item) + ","
    
    return output


def find_duplicates(items):
    """Find duplicates using nested loops (O(n²) complexity)"""
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates


def calculate_statistics(numbers):
    """Calculate basic statistics with redundant iterations"""
    # Anti-pattern 3: Multiple passes over the same data
    total = 0
    for num in numbers:
        total += num
    mean = total / len(numbers)
    
    # Calculate variance with another full pass
    variance_sum = 0
    for num in numbers:
        variance_sum += (num - mean) ** 2
    variance = variance_sum / len(numbers)
    
    # Find min/max with yet another pass
    minimum = numbers[0]
    maximum = numbers[0]
    for num in numbers:
        if num < minimum:
            minimum = num
        if num > maximum:
            maximum = num
    
    return {
        'mean': mean,
        'variance': variance,
        'min': minimum,
        'max': maximum
    }


class DataProcessor:
    """Data processor with poor encapsulation"""
    
    def __init__(self):
        # Anti-pattern 4: Public mutable state
        self.data = []
        self.processed = False
        self.cache = {}
    
    def add_data(self, item):
        """Add data without validation"""
        self.data.append(item)
    
    def process(self):
        """Process all data"""
        # Anti-pattern 5: No error handling
        for item in self.data:
            self.cache[item] = item * 2
        self.processed = True
    
    def get_result(self, key):
        """Get processed result"""
        return self.cache[key]
