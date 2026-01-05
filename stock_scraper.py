"""
Stock Market Scraper for Casablanca Stock Exchange
Scrapes data from multiple sources: BMCE Capital, BPNet, CDG Capital, Casablanca Bourse
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import re
import time
import logging
from abc import ABC, abstractmethod

import sys
sys.path.append('..')
from utils.helpers import (
    clean_text, parse_number, parse_percentage, parse_datetime,
    create_session_with_retry, RateLimiter, DataValidator, logger
)
from config.settings import STOCK_SOURCES, STOCK_TICKERS, ScraperConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StockQuote:
    """Data class for stock quote information"""
    ticker: str
    name: str
    price: float
    variation_pct: Optional[float] = None
    variation_abs: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    previous_close: Optional[float] = None
    volume: Optional[int] = None
    turnover: Optional[float] = None  # Volume in MAD
    vwap: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    isin: Optional[str] = None
    sector: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "ticker": self.ticker,
            "name": self.name,
            "price": self.price,
            "variation_pct": self.variation_pct,
            "variation_abs": self.variation_abs,
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "previous_close": self.previous_close,
            "volume": self.volume,
            "turnover": self.turnover,
            "vwap": self.vwap,
            "bid": self.bid_price,
            "ask": self.ask_price,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "isin": self.isin,
            "sector": self.sector
        }


@dataclass
class OrderBookEntry:
    """Data class for order book entries"""
    price: float
    quantity: int
    num_orders: int
    side: str  # 'bid' or 'ask'


@dataclass
class MarketIndex:
    """Data class for market indices"""
    name: str
    value: float
    variation_pct: Optional[float] = None
    variation_abs: Optional[float] = None
    open_value: Optional[float] = None
    high_value: Optional[float] = None
    low_value: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "variation_pct": self.variation_pct,
            "variation_abs": self.variation_abs,
            "open": self.open_value,
            "high": self.high_value,
            "low": self.low_value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source
        }


class BaseScraper(ABC):
    """Base class for stock market scrapers"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.session = create_session_with_retry()
        self.session.headers.update(self.config.headers)
        self.session.headers['User-Agent'] = self.config.user_agent
        self.rate_limiter = RateLimiter(1.0 / self.config.rate_limit_delay)
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        self.rate_limiter.wait()
        
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _fetch_json(self, url: str) -> Optional[Dict]:
        """Fetch JSON data from an API endpoint"""
        self.rate_limiter.wait()
        
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching JSON from {url}: {e}")
            return None
    
    @abstractmethod
    def get_all_stocks(self) -> List[StockQuote]:
        """Fetch all stock quotes"""
        pass
    
    @abstractmethod
    def get_stock_detail(self, ticker: str) -> Optional[StockQuote]:
        """Fetch detailed information for a single stock"""
        pass
    
    @abstractmethod
    def get_indices(self) -> List[MarketIndex]:
        """Fetch market indices"""
        pass


class BMCECapitalScraper(BaseScraper):
    """Scraper for BMCE Capital Bourse website"""
    
    SOURCE_NAME = "BMCE Capital Bourse"
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = STOCK_SOURCES["bmce_capital"]["base_url"]
    
    def get_all_stocks(self) -> List[StockQuote]:
        """Fetch all stock quotes from BMCE Capital"""
        stocks = []
        
        # First, get the home page to extract palmarès data
        url = STOCK_SOURCES["bmce_capital"]["home_url"]
        soup = self._fetch_page(url)
        
        if not soup:
            logger.error("Failed to fetch BMCE Capital home page")
            return stocks
        
        # Extract top gainers and losers from palmarès tables
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        # Extract stock link and data
                        link = row.find('a')
                        if link:
                            name = clean_text(link.text)
                            price_text = clean_text(cells[1].text) if len(cells) > 1 else None
                            var_text = clean_text(cells[2].text) if len(cells) > 2 else None
                            
                            price = parse_number(price_text)
                            variation = parse_percentage(var_text)
                            
                            if price and name:
                                # Try to match ticker from known list
                                ticker = self._match_ticker(name)
                                
                                stock = StockQuote(
                                    ticker=ticker or name[:5].upper(),
                                    name=name,
                                    price=price,
                                    variation_pct=variation,
                                    source=self.SOURCE_NAME,
                                    timestamp=datetime.now()
                                )
                                stocks.append(stock)
                    except Exception as e:
                        logger.warning(f"Error parsing row: {e}")
        
        return stocks
    
    def _match_ticker(self, name: str) -> Optional[str]:
        """Match company name to ticker symbol"""
        name_lower = name.lower()
        for ticker, info in STOCK_TICKERS.items():
            if info['name'].lower() in name_lower or name_lower in info['name'].lower():
                return ticker
        return None
    
    def get_stock_detail(self, stock_id: str) -> Optional[StockQuote]:
        """
        Fetch detailed stock information
        stock_id: The numeric ID used in BMCE URLs (e.g., 150349775 for Cash Plus)
        """
        url = f"{self.base_url}/bkbbourse/details/{stock_id},102,608"
        soup = self._fetch_page(url)
        
        if not soup:
            return None
        
        try:
            # Extract stock name from page title
            title = soup.find('h1')
            name = clean_text(title.text) if title else "Unknown"
            name = name.replace("FICHE ", "")
            
            # Extract cotation data
            data = {}
            
            # Find cotation table
            cotation_tables = soup.find_all('table')
            for table in cotation_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = clean_text(cells[0].text).lower()
                        value = clean_text(cells[1].text)
                        
                        if 'cours' in key and 'var' not in key:
                            data['price'] = parse_number(value)
                        elif 'variation' in key:
                            data['variation'] = parse_percentage(value)
                        elif 'ouverture' in key:
                            data['open'] = parse_number(value)
                        elif 'haut' in key:
                            data['high'] = parse_number(value)
                        elif 'bas' in key:
                            data['low'] = parse_number(value)
                        elif 'veille' in key:
                            data['previous_close'] = parse_number(value)
                        elif 'quantité' in key or 'quantite' in key:
                            data['volume'] = int(parse_number(value) or 0)
                        elif 'volume' in key:
                            data['turnover'] = parse_number(value)
                        elif 'vwap' in key:
                            data['vwap'] = parse_number(value)
            
            # Extract date/time
            datetime_text = soup.find(text=re.compile(r'\d{2}\.\d{2}\.\d{4}'))
            timestamp = parse_datetime(datetime_text) if datetime_text else datetime.now()
            
            if data.get('price'):
                return StockQuote(
                    ticker=self._match_ticker(name) or stock_id,
                    name=name,
                    price=data['price'],
                    variation_pct=data.get('variation'),
                    open_price=data.get('open'),
                    high_price=data.get('high'),
                    low_price=data.get('low'),
                    previous_close=data.get('previous_close'),
                    volume=data.get('volume'),
                    turnover=data.get('turnover'),
                    vwap=data.get('vwap'),
                    timestamp=timestamp,
                    source=self.SOURCE_NAME
                )
        except Exception as e:
            logger.error(f"Error parsing stock detail: {e}")
        
        return None
    
    def get_indices(self) -> List[MarketIndex]:
        """Fetch market indices from BMCE Capital"""
        indices = []
        
        url = f"{self.base_url}/bkbbourse/indices"
        soup = self._fetch_page(url)
        
        if not soup:
            return indices
        
        # Extract MASI data from home page
        home_soup = self._fetch_page(STOCK_SOURCES["bmce_capital"]["home_url"])
        if home_soup:
            # Look for MASI in the cotations section
            masi_section = home_soup.find(text=re.compile(r'MASI|Intraday'))
            if masi_section:
                parent = masi_section.find_parent('div')
                if parent:
                    # Extract MASI value and variation
                    text = clean_text(parent.text)
                    var_match = re.search(r'([+-]?\d+[,.]?\d*)\s*%', text)
                    value_match = re.search(r'(\d{1,2}[\s,.]?\d{3}[,.]?\d{0,2})', text)
                    
                    if value_match:
                        masi = MarketIndex(
                            name="MASI",
                            value=parse_number(value_match.group(1)) or 0,
                            variation_pct=parse_percentage(var_match.group(1)) if var_match else None,
                            source=self.SOURCE_NAME
                        )
                        indices.append(masi)
        
        return indices
    
    def get_order_book(self, stock_id: str) -> Dict[str, List[OrderBookEntry]]:
        """Extract order book data for a stock"""
        url = f"{self.base_url}/bkbbourse/details/{stock_id},102,608"
        soup = self._fetch_page(url)
        
        order_book = {"bids": [], "asks": []}
        
        if not soup:
            return order_book
        
        # Find order book tables (Carnet d'ordres)
        tables = soup.find_all('table')
        
        for table in tables:
            header = table.find_previous('h2') or table.find_previous('h3')
            if header and 'carnet' in clean_text(header.text).lower():
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        try:
                            # Parse bid side (left) or ask side (right) based on column position
                            if cells[0].text.strip():  # Bid side
                                entry = OrderBookEntry(
                                    price=parse_number(cells[2].text) or 0,
                                    quantity=int(parse_number(cells[1].text) or 0),
                                    num_orders=int(parse_number(cells[0].text) or 0),
                                    side='bid'
                                )
                                order_book["bids"].append(entry)
                        except Exception:
                            pass
        
        return order_book


class BPNetScraper(BaseScraper):
    """Scraper for Banque Populaire BPNet stock prices"""
    
    SOURCE_NAME = "BPNet - Banque Populaire"
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = STOCK_SOURCES["bpnet"]["base_url"]
    
    def get_all_stocks(self) -> List[StockQuote]:
        """Fetch all stock quotes from BPNet"""
        stocks = []
        
        url = STOCK_SOURCES["bpnet"]["stock_price_url"]
        soup = self._fetch_page(url)
        
        if not soup:
            logger.error("Failed to fetch BPNet stock prices")
            return stocks
        
        # Find the main stock table
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            # Check if this is the stock table (should have headers)
            headers = table.find_all('th')
            if not headers:
                continue
            
            # Parse header to understand column structure
            header_texts = [clean_text(h.text).lower() for h in headers]
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if len(cells) >= 4:
                    try:
                        name = clean_text(cells[0].text)
                        
                        # Skip derivative instruments and attribution rights
                        if any(skip in name.lower() for skip in ['droit', 'attribution', 'da ', 'opv']):
                            continue
                        
                        price = parse_number(cells[1].text)
                        variation = parse_number(cells[2].text)
                        high = parse_number(cells[3].text) if len(cells) > 3 else None
                        low = parse_number(cells[4].text) if len(cells) > 4 else None
                        high_year = parse_number(cells[5].text) if len(cells) > 5 else None
                        low_year = parse_number(cells[6].text) if len(cells) > 6 else None
                        
                        if price and name:
                            ticker = self._match_ticker(name)
                            
                            stock = StockQuote(
                                ticker=ticker or name[:5].upper().replace(' ', ''),
                                name=name,
                                price=price,
                                variation_pct=variation,
                                high_price=high,
                                low_price=low,
                                source=self.SOURCE_NAME,
                                timestamp=datetime.now()
                            )
                            stocks.append(stock)
                    except Exception as e:
                        logger.warning(f"Error parsing BPNet row: {e}")
        
        # Remove duplicates based on name
        seen_names = set()
        unique_stocks = []
        for stock in stocks:
            normalized_name = stock.name.lower().strip()
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_stocks.append(stock)
        
        return unique_stocks
    
    def _match_ticker(self, name: str) -> Optional[str]:
        """Match company name to ticker symbol"""
        name_lower = name.lower()
        
        # Direct name matching
        for ticker, info in STOCK_TICKERS.items():
            if info['name'].lower() == name_lower:
                return ticker
            if info['name'].lower() in name_lower or name_lower in info['name'].lower():
                return ticker
        
        # Partial matching with keywords
        name_words = set(name_lower.split())
        best_match = None
        best_score = 0
        
        for ticker, info in STOCK_TICKERS.items():
            ticker_words = set(info['name'].lower().split())
            common_words = name_words & ticker_words
            score = len(common_words)
            if score > best_score and score >= 1:
                best_score = score
                best_match = ticker
        
        return best_match
    
    def get_stock_detail(self, ticker: str) -> Optional[StockQuote]:
        """BPNet doesn't have individual stock pages - get from list"""
        stocks = self.get_all_stocks()
        for stock in stocks:
            if stock.ticker == ticker:
                return stock
        return None
    
    def get_indices(self) -> List[MarketIndex]:
        """BPNet doesn't show indices - return empty list"""
        return []


class CasablancaBourseScraper(BaseScraper):
    """Scraper for official Casablanca Bourse website (requires JavaScript rendering)"""
    
    SOURCE_NAME = "Bourse de Casablanca"
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = STOCK_SOURCES["casablanca_bourse"]["base_url"]
        self._selenium_driver = None
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver for JavaScript-rendered pages"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(f'user-agent={self.config.user_agent}')
            
            self._selenium_driver = webdriver.Chrome(options=options)
            return True
        except Exception as e:
            logger.warning(f"Selenium not available: {e}. Using fallback parsing.")
            return False
    
    def _fetch_page_js(self, url: str, wait_time: int = 5) -> Optional[BeautifulSoup]:
        """Fetch page with JavaScript rendering using Selenium"""
        if not self._selenium_driver and not self._init_selenium():
            return self._fetch_page(url)  # Fallback to regular request
        
        try:
            self._selenium_driver.get(url)
            time.sleep(wait_time)  # Wait for JavaScript to load
            html = self._selenium_driver.page_source
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching with Selenium: {e}")
            return None
    
    def get_all_stocks(self) -> List[StockQuote]:
        """
        Fetch all stock quotes from Casablanca Bourse
        Note: This site requires JavaScript - using alternative data extraction
        """
        stocks = []
        
        # Try to extract from HTML/JSON embedded in page
        url = STOCK_SOURCES["casablanca_bourse"]["overview_url"]
        soup = self._fetch_page_js(url) if self._selenium_driver else self._fetch_page(url)
        
        if soup:
            # Look for embedded JSON data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and '__NEXT_DATA__' in (script.string or ''):
                    try:
                        # Extract Next.js embedded data
                        json_match = re.search(r'__NEXT_DATA__\s*=\s*({.+?})\s*;?', script.string)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            # Parse the data structure to extract stocks
                            # Structure depends on actual page implementation
                            pass
                    except json.JSONDecodeError:
                        pass
        
        return stocks
    
    def get_stock_detail(self, ticker: str) -> Optional[StockQuote]:
        """Fetch detailed information for a single stock"""
        url = STOCK_SOURCES["casablanca_bourse"]["instrument_url"].format(ticker=ticker)
        soup = self._fetch_page_js(url) if self._selenium_driver else self._fetch_page(url)
        
        if not soup:
            return None
        
        # Extract data from the page
        # Implementation depends on page structure
        return None
    
    def get_indices(self) -> List[MarketIndex]:
        """Fetch market indices"""
        return []
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if self._selenium_driver:
            try:
                self._selenium_driver.quit()
            except:
                pass


class MarketDataAggregator:
    """Aggregates data from multiple scrapers and provides unified interface"""
    
    def __init__(self):
        config = ScraperConfig()
        self.scrapers = {
            "bmce": BMCECapitalScraper(config),
            "bpnet": BPNetScraper(config),
            # "casablanca": CasablancaBourseScraper(config),  # Requires Selenium
        }
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_all_stocks(self, sources: List[str] = None) -> Dict[str, List[StockQuote]]:
        """
        Fetch stocks from specified sources or all sources
        Returns dict with source as key and list of quotes as value
        """
        sources = sources or list(self.scrapers.keys())
        results = {}
        
        for source in sources:
            if source in self.scrapers:
                try:
                    logger.info(f"Fetching stocks from {source}...")
                    stocks = self.scrapers[source].get_all_stocks()
                    results[source] = stocks
                    logger.info(f"Got {len(stocks)} stocks from {source}")
                except Exception as e:
                    logger.error(f"Error fetching from {source}: {e}")
                    results[source] = []
        
        return results
    
    def get_merged_stocks(self) -> List[StockQuote]:
        """
        Get merged list of stocks with data from best available source
        Prefers more detailed sources over less detailed ones
        """
        all_data = self.get_all_stocks()
        
        # Merge stocks by ticker
        merged = {}
        source_priority = ["bpnet", "bmce", "casablanca"]  # Order of preference
        
        for source in reversed(source_priority):  # Lower priority first
            if source in all_data:
                for stock in all_data[source]:
                    merged[stock.ticker] = stock
        
        return list(merged.values())
    
    def get_stock(self, ticker: str) -> Optional[StockQuote]:
        """Get stock quote from first available source"""
        for name, scraper in self.scrapers.items():
            try:
                stock = scraper.get_stock_detail(ticker)
                if stock:
                    return stock
            except Exception as e:
                logger.warning(f"Error getting {ticker} from {name}: {e}")
        
        return None
    
    def get_indices(self) -> List[MarketIndex]:
        """Get market indices from all sources"""
        indices = []
        for name, scraper in self.scrapers.items():
            try:
                source_indices = scraper.get_indices()
                indices.extend(source_indices)
            except Exception as e:
                logger.warning(f"Error getting indices from {name}: {e}")
        
        return indices
    
    def export_to_json(self, filepath: str):
        """Export all current data to JSON file"""
        stocks = self.get_merged_stocks()
        indices = self.get_indices()
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "stocks": [s.to_dict() for s in stocks],
            "indices": [i.to_dict() for i in indices],
            "metadata": {
                "num_stocks": len(stocks),
                "num_indices": len(indices),
                "sources": list(self.scrapers.keys())
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported data to {filepath}")
        return data


# Convenience function for quick access
def get_market_data() -> Dict:
    """Quick function to get current market data"""
    aggregator = MarketDataAggregator()
    return {
        "stocks": [s.to_dict() for s in aggregator.get_merged_stocks()],
        "indices": [i.to_dict() for i in aggregator.get_indices()],
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Test the scrapers
    print("=" * 60)
    print("Testing Morocco Stock Market Scrapers")
    print("=" * 60)
    
    aggregator = MarketDataAggregator()
    
    # Test BPNet scraper
    print("\n--- BPNet Scraper ---")
    bpnet_stocks = aggregator.scrapers["bpnet"].get_all_stocks()
    print(f"Found {len(bpnet_stocks)} stocks")
    for stock in bpnet_stocks[:5]:
        print(f"  {stock.ticker}: {stock.name} - {stock.price} MAD ({stock.variation_pct}%)")
    
    # Test BMCE scraper
    print("\n--- BMCE Capital Scraper ---")
    bmce_stocks = aggregator.scrapers["bmce"].get_all_stocks()
    print(f"Found {len(bmce_stocks)} stocks")
    
    # Get indices
    print("\n--- Market Indices ---")
    indices = aggregator.get_indices()
    for idx in indices:
        print(f"  {idx.name}: {idx.value} ({idx.variation_pct}%)")
    
    # Export to JSON
    print("\n--- Exporting to JSON ---")
    aggregator.export_to_json("data/market_data.json")
