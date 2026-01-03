"""
Helper functions for MarketPulse
"""

import uuid
from datetime import datetime
import logging

def generate_uuid():
    """Generate a UUID for data records"""
    return str(uuid.uuid4())

def format_timestamp(timestamp=None):
    """Format timestamp for consistent use across the application"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.isoformat()

def setup_logging(name, level=logging.INFO):
    """Set up logging for modules"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

def validate_symbol(symbol):
    """Validate stock symbol format"""
    if not symbol or not isinstance(symbol, str):
        return False
    # Basic validation: 1-5 uppercase letters
    return symbol.isalpha() and 1 <= len(symbol) <= 5 and symbol.isupper()

def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def moving_average(data, window_size):
    """Calculate moving average of data"""
    if len(data) < window_size:
        return []
    return [sum(data[i:i+window_size])/window_size for i in range(len(data)-window_size+1)]

def normalize_data(data):
    """Normalize data to range [0, 1]"""
    if not data:
        return []
    min_val = min(data)
    max_val = max(data)
    if min_val == max_val:
        return [0.0 for _ in data]
    return [(x - min_val) / (max_val - min_val) for x in data]