"""
Utility functions for Morocco Market Scraper
"""

import re
import hashlib
import unicodedata
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    return text


def parse_number(value: str, decimal_sep: str = ',') -> Optional[float]:
    """
    Parse a number string to float, handling French/European formatting
    Examples: "1 234,56" -> 1234.56, "1.234,56" -> 1234.56
    """
    if not value:
        return None
    
    try:
        # Remove whitespace and non-breaking spaces
        value = re.sub(r'[\s\u00a0]', '', str(value))
        
        # Handle French number format (1.234,56 or 1 234,56)
        if decimal_sep == ',':
            value = value.replace('.', '').replace(',', '.')
        
        # Remove any remaining non-numeric characters except . and -
        value = re.sub(r'[^\d.\-]', '', value)
        
        return float(value) if value else None
    except (ValueError, TypeError):
        return None


def parse_percentage(value: str) -> Optional[float]:
    """
    Parse percentage string to float
    Examples: "+2,34%" -> 2.34, "-1,5 %" -> -1.5
    """
    if not value:
        return None
    
    try:
        # Remove % sign and whitespace
        value = re.sub(r'[%\s]', '', str(value))
        return parse_number(value)
    except (ValueError, TypeError):
        return None


def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parse date string to datetime object
    Supports multiple French/European date formats
    """
    if not date_str:
        return None
    
    default_formats = [
        '%d/%m/%Y',
        '%d.%m.%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d.%m.%Y %H:%M:%S',
        '%d %b %Y',
        '%d %B %Y',
    ]
    
    formats = formats or default_formats
    date_str = clean_text(date_str)
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime string with time component"""
    if not dt_str:
        return None
    
    formats = [
        '%d/%m/%Y %H:%M:%S',
        '%d.%m.%Y %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d.%m.%Y %H:%M',
    ]
    
    return parse_date(dt_str, formats)


def generate_hash(content: str) -> str:
    """Generate MD5 hash of content for deduplication"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def is_market_hours() -> bool:
    """Check if current time is within Casablanca Stock Exchange hours"""
    now = datetime.now()
    # Market hours: 9:30 AM - 3:30 PM (Morocco time)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # Check if it's a weekday (Monday=0 to Friday=4)
    if now.weekday() > 4:
        return False
    
    return market_open <= now <= market_close


def format_currency(value: float, currency: str = "MAD") -> str:
    """Format number as currency"""
    if value is None:
        return "N/A"
    return f"{value:,.2f} {currency}"


def format_variation(value: float) -> str:
    """Format variation with + or - sign"""
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def extract_ticker_from_url(url: str) -> Optional[str]:
    """Extract stock ticker from various URL formats"""
    patterns = [
        r'/instruments/([A-Z]{2,5})',  # Casablanca Bourse
        r'/market/([A-Z]{2,5})',       # CDG Capital
        r'/details/(\d+),',            # BMCE (returns ID)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def calculate_change(current: float, previous: float) -> Dict[str, float]:
    """Calculate absolute and percentage change"""
    if previous is None or previous == 0:
        return {"absolute": None, "percentage": None}
    
    absolute = current - previous
    percentage = (absolute / previous) * 100
    
    return {
        "absolute": round(absolute, 2),
        "percentage": round(percentage, 2)
    }


def normalize_company_name(name: str) -> str:
    """Normalize company name for matching across sources"""
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove common suffixes
    suffixes = [' s.a.', ' sa', ' s.a', ' spa', ' sca', ' sarl']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name


def match_ticker(name: str, tickers: Dict) -> Optional[str]:
    """Try to match a company name to a ticker symbol"""
    normalized_name = normalize_company_name(name)
    
    for ticker, info in tickers.items():
        if normalize_company_name(info.get('name', '')) == normalized_name:
            return ticker
    
    # Try partial matching
    for ticker, info in tickers.items():
        company_name = normalize_company_name(info.get('name', ''))
        if normalized_name in company_name or company_name in normalized_name:
            return ticker
    
    return None


def safe_get(data: Dict, *keys, default=None) -> Any:
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff
    """
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
        
        raise last_exception
    
    return wrapper


class DataValidator:
    """Validate scraped stock data"""
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate stock price is reasonable"""
        return price is not None and 0 < price < 100000
    
    @staticmethod
    def validate_volume(volume: int) -> bool:
        """Validate trading volume"""
        return volume is not None and volume >= 0
    
    @staticmethod
    def validate_variation(variation: float) -> bool:
        """Validate daily variation (typically limited to ±10% on CSE)"""
        return variation is None or -15 <= variation <= 15
    
    @staticmethod
    def validate_stock_data(data: Dict) -> Dict[str, bool]:
        """Validate all fields in stock data"""
        return {
            "price_valid": DataValidator.validate_price(data.get("price")),
            "volume_valid": DataValidator.validate_volume(data.get("volume")),
            "variation_valid": DataValidator.validate_variation(data.get("variation")),
            "has_ticker": bool(data.get("ticker")),
            "has_timestamp": bool(data.get("timestamp"))
        }


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        import time
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()


def create_session_with_retry():
    """Create a requests session with retry logic"""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
