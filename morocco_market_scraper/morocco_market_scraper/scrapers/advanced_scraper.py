"""
Advanced Casablanca Stock Exchange Scraper
Attempts multiple data extraction methods including:
- Direct HTML parsing
- JSON API endpoints discovery
- XHR request interception patterns
- Mobile API endpoints
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import json
import re
import time
import logging
from urllib.parse import urljoin, urlparse, parse_qs

import sys
sys.path.append('..')
from utils.helpers import clean_text, parse_number, parse_percentage, create_session_with_retry

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    """Complete market snapshot"""
    timestamp: datetime
    masi_value: float
    masi_variation: float
    madex_value: float
    madex_variation: float
    total_volume: float
    total_turnover: float
    stocks_up: int
    stocks_down: int
    stocks_unchanged: int
    source: str


class CasablancaBourseAdvancedScraper:
    """
    Advanced scraper for Casablanca Stock Exchange
    Tries multiple methods to extract data
    """
    
    # Known API endpoints and patterns
    ENDPOINTS = {
        "main": "https://www.casablanca-bourse.com",
        "api_base": "https://www.casablanca-bourse.com/api",
        "live_market": "https://www.casablanca-bourse.com/fr/live-market/overview",
        "instruments": "https://www.casablanca-bourse.com/fr/live-market/instruments",
        
        # Potential API endpoints (to be discovered)
        "api_market": "/api/market",
        "api_quotes": "/api/quotes",
        "api_instruments": "/api/instruments",
        "api_indices": "/api/indices",
        
        # Alternative data sources
        "mobile_api": "https://mobile.casablanca-bourse.com/api",
    }
    
    # Known XHR patterns from Next.js apps
    NEXTJS_DATA_PATTERNS = [
        r'__NEXT_DATA__\s*=\s*({.+?})\s*</script>',
        r'"props"\s*:\s*({.+?})\s*,\s*"page"',
        r'window\.__NUXT__\s*=\s*({.+?})\s*</script>',
    ]
    
    def __init__(self):
        self.session = create_session_with_retry()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Referer': 'https://www.casablanca-bourse.com/',
        })
        self._discovered_endpoints = []
    
    def _extract_nextjs_data(self, html: str) -> Optional[Dict]:
        """Extract data from Next.js __NEXT_DATA__ script"""
        for pattern in self.NEXTJS_DATA_PATTERNS:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        return None
    
    def _discover_api_endpoints(self, html: str) -> List[str]:
        """Discover API endpoints from page source"""
        endpoints = []
        
        # Look for API URLs in scripts
        api_patterns = [
            r'["\'](/api/[^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if '/api/' in match or 'market' in match.lower():
                    endpoints.append(match)
        
        return list(set(endpoints))
    
    def _try_api_endpoint(self, endpoint: str) -> Optional[Dict]:
        """Try to fetch data from an API endpoint"""
        try:
            if not endpoint.startswith('http'):
                endpoint = urljoin(self.ENDPOINTS['main'], endpoint)
            
            response = self.session.get(endpoint, timeout=10)
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return None
        except Exception as e:
            logger.debug(f"API endpoint {endpoint} failed: {e}")
        return None
    
    def scrape_overview(self) -> Tuple[Optional[MarketSnapshot], List[Dict]]:
        """
        Scrape market overview using multiple methods
        Returns: (market_snapshot, list_of_stocks)
        """
        stocks = []
        snapshot = None
        
        # Method 1: Try direct HTML parsing
        try:
            response = self.session.get(self.ENDPOINTS['live_market'], timeout=15)
            if response.status_code == 200:
                html = response.text
                
                # Try to extract Next.js data
                nextjs_data = self._extract_nextjs_data(html)
                if nextjs_data:
                    logger.info("Found Next.js data, extracting market info...")
                    stocks, snapshot = self._parse_nextjs_data(nextjs_data)
                
                # Discover and try API endpoints
                discovered = self._discover_api_endpoints(html)
                self._discovered_endpoints.extend(discovered)
                logger.info(f"Discovered {len(discovered)} potential API endpoints")
                
                # If no Next.js data, try HTML parsing
                if not stocks:
                    stocks = self._parse_html_stocks(html)
        except Exception as e:
            logger.error(f"Overview scrape failed: {e}")
        
        # Method 2: Try discovered API endpoints
        if not stocks:
            for endpoint in self._discovered_endpoints:
                data = self._try_api_endpoint(endpoint)
                if data and isinstance(data, (list, dict)):
                    stocks = self._parse_api_response(data)
                    if stocks:
                        break
        
        # Method 3: Try common API patterns
        if not stocks:
            common_apis = [
                '/api/market/overview',
                '/api/v1/quotes',
                '/api/v1/market',
                '/_next/data/market.json',
            ]
            for api in common_apis:
                data = self._try_api_endpoint(api)
                if data:
                    stocks = self._parse_api_response(data)
                    if stocks:
                        break
        
        return snapshot, stocks
    
    def _parse_nextjs_data(self, data: Dict) -> Tuple[List[Dict], Optional[MarketSnapshot]]:
        """Parse Next.js embedded data structure"""
        stocks = []
        snapshot = None
        
        # Navigate the props structure
        props = data.get('props', {})
        page_props = props.get('pageProps', {})
        
        # Look for market data in various locations
        possible_keys = ['marketData', 'stocks', 'instruments', 'quotes', 'data']
        
        for key in possible_keys:
            if key in page_props:
                raw_data = page_props[key]
                if isinstance(raw_data, list):
                    for item in raw_data:
                        stock = self._normalize_stock_data(item)
                        if stock:
                            stocks.append(stock)
                elif isinstance(raw_data, dict):
                    if 'items' in raw_data:
                        for item in raw_data['items']:
                            stock = self._normalize_stock_data(item)
                            if stock:
                                stocks.append(stock)
        
        # Extract index data
        if 'indices' in page_props or 'masi' in str(page_props).lower():
            snapshot = self._extract_snapshot(page_props)
        
        return stocks, snapshot
    
    def _normalize_stock_data(self, raw: Dict) -> Optional[Dict]:
        """Normalize stock data from various formats"""
        if not raw:
            return None
        
        # Common field mappings
        field_mappings = {
            'ticker': ['ticker', 'symbol', 'code', 'isin', 'instrument'],
            'name': ['name', 'libelle', 'label', 'companyName', 'instrumentName'],
            'price': ['price', 'last', 'cours', 'lastPrice', 'currentPrice', 'close'],
            'variation': ['variation', 'change', 'var', 'changePercent', 'pctChange'],
            'volume': ['volume', 'qty', 'quantity', 'tradedVolume'],
            'high': ['high', 'dayHigh', 'haut', 'plusHaut'],
            'low': ['low', 'dayLow', 'bas', 'plusBas'],
            'open': ['open', 'ouverture', 'openPrice'],
        }
        
        normalized = {}
        
        for target_field, source_fields in field_mappings.items():
            for source in source_fields:
                # Try direct match
                if source in raw:
                    normalized[target_field] = raw[source]
                    break
                # Try case-insensitive match
                for key in raw:
                    if key.lower() == source.lower():
                        normalized[target_field] = raw[key]
                        break
        
        if 'ticker' in normalized or 'name' in normalized:
            normalized['source'] = 'casablanca_bourse'
            normalized['timestamp'] = datetime.now().isoformat()
            return normalized
        
        return None
    
    def _parse_html_stocks(self, html: str) -> List[Dict]:
        """Parse stocks from HTML tables/elements"""
        stocks = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for stock tables
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            headers = []
            
            # Get headers
            header_row = table.find('tr')
            if header_row:
                headers = [clean_text(th.text).lower() for th in header_row.find_all(['th', 'td'])]
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 3:
                    stock = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            header = headers[i]
                            value = clean_text(cell.text)
                            
                            if 'nom' in header or 'name' in header or 'valeur' in header:
                                stock['name'] = value
                            elif 'cours' in header or 'price' in header:
                                stock['price'] = parse_number(value)
                            elif 'var' in header:
                                stock['variation'] = parse_percentage(value)
                            elif 'volume' in header:
                                stock['volume'] = parse_number(value)
                    
                    if stock.get('name') or stock.get('price'):
                        stock['source'] = 'casablanca_bourse_html'
                        stocks.append(stock)
        
        # Look for stock cards/divs
        stock_cards = soup.find_all(class_=re.compile(r'stock|instrument|quote', re.I))
        for card in stock_cards:
            stock = self._parse_stock_card(card)
            if stock:
                stocks.append(stock)
        
        return stocks
    
    def _parse_stock_card(self, element) -> Optional[Dict]:
        """Parse a stock card/div element"""
        stock = {}
        
        # Extract text and look for patterns
        text = element.get_text()
        
        # Price pattern
        price_match = re.search(r'(\d+[.,]\d{2})\s*(?:MAD|DH)?', text)
        if price_match:
            stock['price'] = parse_number(price_match.group(1))
        
        # Variation pattern
        var_match = re.search(r'([+-]?\d+[.,]\d{1,2})\s*%', text)
        if var_match:
            stock['variation'] = parse_percentage(var_match.group(1))
        
        # Name - usually in a heading or specific class
        name_elem = element.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'name|title', re.I))
        if name_elem:
            stock['name'] = clean_text(name_elem.text)
        
        if stock.get('name') or stock.get('price'):
            stock['source'] = 'casablanca_bourse_card'
            return stock
        
        return None
    
    def _parse_api_response(self, data: Any) -> List[Dict]:
        """Parse API response data"""
        stocks = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    stock = self._normalize_stock_data(item)
                    if stock:
                        stocks.append(stock)
        elif isinstance(data, dict):
            # Look for array data in the response
            for key in ['data', 'items', 'stocks', 'instruments', 'quotes', 'results']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        stock = self._normalize_stock_data(item)
                        if stock:
                            stocks.append(stock)
        
        return stocks
    
    def _extract_snapshot(self, data: Dict) -> Optional[MarketSnapshot]:
        """Extract market snapshot from data"""
        try:
            # Look for MASI/MADEX values
            masi = None
            madex = None
            
            for key, value in data.items():
                key_lower = key.lower()
                if 'masi' in key_lower:
                    if isinstance(value, dict):
                        masi = value.get('value') or value.get('last')
                    else:
                        masi = value
                elif 'madex' in key_lower:
                    if isinstance(value, dict):
                        madex = value.get('value') or value.get('last')
                    else:
                        madex = value
            
            if masi:
                return MarketSnapshot(
                    timestamp=datetime.now(),
                    masi_value=float(masi) if masi else 0,
                    masi_variation=0,
                    madex_value=float(madex) if madex else 0,
                    madex_variation=0,
                    total_volume=0,
                    total_turnover=0,
                    stocks_up=0,
                    stocks_down=0,
                    stocks_unchanged=0,
                    source='casablanca_bourse'
                )
        except Exception as e:
            logger.error(f"Error extracting snapshot: {e}")
        
        return None
    
    def get_instrument_details(self, ticker: str) -> Optional[Dict]:
        """Get detailed information for a specific instrument"""
        url = f"{self.ENDPOINTS['instruments']}/{ticker}"
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                # Try Next.js data extraction
                nextjs_data = self._extract_nextjs_data(response.text)
                if nextjs_data:
                    return self._parse_instrument_details(nextjs_data, ticker)
                
                # Try HTML parsing
                return self._parse_instrument_html(response.text, ticker)
        except Exception as e:
            logger.error(f"Error getting instrument {ticker}: {e}")
        
        return None
    
    def _parse_instrument_details(self, data: Dict, ticker: str) -> Dict:
        """Parse instrument details from Next.js data"""
        props = data.get('props', {}).get('pageProps', {})
        
        instrument = props.get('instrument', {})
        if not instrument:
            # Try to find instrument data
            for key in props:
                if isinstance(props[key], dict) and 'ticker' in str(props[key]):
                    instrument = props[key]
                    break
        
        return self._normalize_stock_data(instrument) or {'ticker': ticker}
    
    def _parse_instrument_html(self, html: str, ticker: str) -> Dict:
        """Parse instrument details from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        details = {'ticker': ticker, 'source': 'casablanca_bourse'}
        
        # Look for data in definition lists, tables, or key-value pairs
        dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            for dt, dd in zip(dts, dds):
                key = clean_text(dt.text).lower()
                value = clean_text(dd.text)
                
                if 'cours' in key or 'price' in key:
                    details['price'] = parse_number(value)
                elif 'variation' in key:
                    details['variation'] = parse_percentage(value)
                elif 'volume' in key:
                    details['volume'] = parse_number(value)
                elif 'ouverture' in key or 'open' in key:
                    details['open'] = parse_number(value)
                elif 'haut' in key or 'high' in key:
                    details['high'] = parse_number(value)
                elif 'bas' in key or 'low' in key:
                    details['low'] = parse_number(value)
        
        return details


class BMCEApiScraper:
    """
    BMCE Capital Bourse API-style scraper
    Attempts to find and use JSON/API endpoints
    """
    
    BASE_URL = "https://www.bmcecapitalbourse.com"
    
    # Stock IDs for direct access (from uploaded documents)
    KNOWN_STOCK_IDS = {
        "CAP": "150349775",  # Cash Plus
        "ATW": "11884",       # Attijariwafa
        "BCP": "11512",       # BCP
        "IAM": "11488",       # Maroc Telecom
        "LHM": "12163",       # LafargeHolcim
        # Add more as discovered
    }
    
    def __init__(self):
        self.session = create_session_with_retry()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })
    
    def get_stock_list_page(self) -> List[Dict]:
        """Get full stock list from the listing page"""
        url = f"{self.BASE_URL}/bkbbourse/lists/TK"
        params = {'q': 'AE31180F8E3BE20E762758E81EDC1204'}
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return self._parse_stock_list(response.text)
        except Exception as e:
            logger.error(f"Error fetching BMCE stock list: {e}")
        
        return []
    
    def _parse_stock_list(self, html: str) -> List[Dict]:
        """Parse the stock listing page"""
        stocks = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find stock table rows
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    link = row.find('a')
                    if link and '/details/' in link.get('href', ''):
                        # Extract stock ID from URL
                        href = link.get('href')
                        id_match = re.search(r'/details/(\d+)', href)
                        stock_id = id_match.group(1) if id_match else None
                        
                        name = clean_text(link.text)
                        price = parse_number(cells[1].text) if len(cells) > 1 else None
                        variation = parse_percentage(cells[2].text) if len(cells) > 2 else None
                        
                        if name and price:
                            stocks.append({
                                'name': name,
                                'price': price,
                                'variation': variation,
                                'stock_id': stock_id,
                                'source': 'bmce_capital'
                            })
        
        return stocks
    
    def get_stock_detail(self, stock_id: str) -> Optional[Dict]:
        """Get detailed stock information"""
        url = f"{self.BASE_URL}/bkbbourse/details/{stock_id},102,608"
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return self._parse_stock_detail(response.text, stock_id)
        except Exception as e:
            logger.error(f"Error fetching stock {stock_id}: {e}")
        
        return None
    
    def _parse_stock_detail(self, html: str, stock_id: str) -> Dict:
        """Parse detailed stock page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        detail = {
            'stock_id': stock_id,
            'source': 'bmce_capital',
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract name from title
        title = soup.find('h1')
        if title:
            detail['name'] = clean_text(title.text).replace('FICHE ', '')
        
        # Find all key-value pairs in tables
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    key = clean_text(cells[0].text).lower()
                    value = clean_text(cells[1].text)
                    
                    if 'cours' in key and 'var' not in key:
                        detail['price'] = parse_number(value)
                    elif 'variation' in key:
                        detail['variation'] = parse_percentage(value)
                    elif 'ouverture' in key:
                        detail['open'] = parse_number(value)
                    elif 'haut' in key:
                        detail['high'] = parse_number(value)
                    elif 'bas' in key:
                        detail['low'] = parse_number(value)
                    elif 'veille' in key:
                        detail['previous_close'] = parse_number(value)
                    elif 'quantité' in key:
                        detail['volume'] = int(parse_number(value) or 0)
                    elif 'volume' in key and 'mad' in value.lower():
                        detail['turnover'] = parse_number(value.replace('M', '').replace('K', ''))
                    elif 'vwap' in key:
                        detail['vwap'] = parse_number(value)
        
        # Extract order book
        detail['order_book'] = self._extract_order_book(soup)
        
        # Extract last transactions
        detail['last_trades'] = self._extract_last_trades(soup)
        
        return detail
    
    def _extract_order_book(self, soup: BeautifulSoup) -> Dict:
        """Extract order book data"""
        order_book = {'bids': [], 'asks': []}
        
        # Look for order book section
        carnet = soup.find(text=re.compile(r'carnet', re.I))
        if carnet:
            table = carnet.find_next('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        # Bid side (left)
                        bid_qty = parse_number(cells[1].text)
                        bid_price = parse_number(cells[2].text)
                        if bid_price:
                            order_book['bids'].append({
                                'price': bid_price,
                                'quantity': int(bid_qty or 0)
                            })
                        
                        # Ask side (right)
                        ask_price = parse_number(cells[3].text)
                        ask_qty = parse_number(cells[4].text)
                        if ask_price:
                            order_book['asks'].append({
                                'price': ask_price,
                                'quantity': int(ask_qty or 0)
                            })
        
        return order_book
    
    def _extract_last_trades(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract last trades"""
        trades = []
        
        # Look for trades section
        transactions = soup.find(text=re.compile(r'transaction|trade', re.I))
        if transactions:
            table = transactions.find_next('table')
            if table:
                rows = table.find_all('tr')[1:]
                for row in rows[:10]:  # Last 10 trades
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        trades.append({
                            'time': clean_text(cells[0].text),
                            'price': parse_number(cells[1].text),
                            'quantity': int(parse_number(cells[2].text) or 0)
                        })
        
        return trades


if __name__ == "__main__":
    # Test the advanced scrapers
    print("Testing Advanced Casablanca Bourse Scraper...")
    
    scraper = CasablancaBourseAdvancedScraper()
    snapshot, stocks = scraper.scrape_overview()
    
    print(f"Found {len(stocks)} stocks")
    if snapshot:
        print(f"MASI: {snapshot.masi_value}")
    
    print("\nTesting BMCE API Scraper...")
    bmce = BMCEApiScraper()
    bmce_stocks = bmce.get_stock_list_page()
    print(f"Found {len(bmce_stocks)} stocks from BMCE")
