"""
Database module for Morocco Market Scraper
SQLite-based storage for stocks, news, and historical data
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json
import logging
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


class MarketDatabase:
    """SQLite database for storing market data"""
    
    def __init__(self, db_path: str = "data/morocco_market.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Stocks table - current quotes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    name TEXT NOT NULL,
                    isin TEXT,
                    sector TEXT,
                    price REAL,
                    variation_pct REAL,
                    variation_abs REAL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    previous_close REAL,
                    volume INTEGER,
                    turnover REAL,
                    vwap REAL,
                    bid_price REAL,
                    ask_price REAL,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ticker, DATE(timestamp))
                )
            """)
            
            # Stock history table - historical quotes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date DATE NOT NULL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    turnover REAL,
                    UNIQUE(ticker, date)
                )
            """)
            
            # Indices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    variation_pct REAL,
                    variation_abs REAL,
                    open_value REAL,
                    high_value REAL,
                    low_value REAL,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, DATE(timestamp))
                )
            """)
            
            # News table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    published_date DATETIME,
                    summary TEXT,
                    content TEXT,
                    author TEXT,
                    category TEXT,
                    tags TEXT,
                    relevance_score REAL DEFAULT 0,
                    matched_keywords TEXT,
                    language TEXT DEFAULT 'fr',
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_read INTEGER DEFAULT 0
                )
            """)
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    ticker TEXT,
                    condition TEXT,
                    threshold REAL,
                    message TEXT,
                    is_triggered INTEGER DEFAULT 0,
                    triggered_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Scrape logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrape_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    scrape_type TEXT NOT NULL,
                    items_count INTEGER,
                    status TEXT,
                    error_message TEXT,
                    duration_seconds REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for faster queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_ticker ON stocks(ticker)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_timestamp ON stocks(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_relevance ON news(relevance_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_source ON news(source)")
            
            logger.info("Database initialized successfully")
    
    # =========================================================================
    # Stock Operations
    # =========================================================================
    
    def insert_stock(self, stock_data: Dict) -> int:
        """Insert or update stock quote"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO stocks 
                (ticker, name, isin, sector, price, variation_pct, variation_abs,
                 open_price, high_price, low_price, close_price, previous_close,
                 volume, turnover, vwap, bid_price, ask_price, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock_data.get('ticker'),
                stock_data.get('name'),
                stock_data.get('isin'),
                stock_data.get('sector'),
                stock_data.get('price'),
                stock_data.get('variation_pct'),
                stock_data.get('variation_abs'),
                stock_data.get('open'),
                stock_data.get('high'),
                stock_data.get('low'),
                stock_data.get('close'),
                stock_data.get('previous_close'),
                stock_data.get('volume'),
                stock_data.get('turnover'),
                stock_data.get('vwap'),
                stock_data.get('bid'),
                stock_data.get('ask'),
                stock_data.get('source'),
                stock_data.get('timestamp', datetime.now().isoformat())
            ))
            
            return cursor.lastrowid
    
    def insert_stocks_batch(self, stocks: List[Dict]) -> int:
        """Insert multiple stock quotes"""
        count = 0
        for stock in stocks:
            try:
                self.insert_stock(stock)
                count += 1
            except Exception as e:
                logger.error(f"Error inserting stock {stock.get('ticker')}: {e}")
        return count
    
    def get_latest_stocks(self) -> List[Dict]:
        """Get latest quote for all stocks"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stocks s
                WHERE timestamp = (
                    SELECT MAX(timestamp) FROM stocks WHERE ticker = s.ticker
                )
                ORDER BY ticker
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stock_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get latest quote for specific stock"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stocks 
                WHERE ticker = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (ticker,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_stock_history(self, ticker: str, days: int = 30) -> List[Dict]:
        """Get historical data for a stock"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stocks 
                WHERE ticker = ? 
                AND timestamp >= datetime('now', ?)
                ORDER BY timestamp ASC
            """, (ticker, f'-{days} days'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """Get top gaining stocks"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stocks s
                WHERE timestamp = (SELECT MAX(timestamp) FROM stocks WHERE ticker = s.ticker)
                AND variation_pct IS NOT NULL
                ORDER BY variation_pct DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """Get top losing stocks"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stocks s
                WHERE timestamp = (SELECT MAX(timestamp) FROM stocks WHERE ticker = s.ticker)
                AND variation_pct IS NOT NULL
                ORDER BY variation_pct ASC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_most_active(self, limit: int = 10) -> List[Dict]:
        """Get most actively traded stocks by volume"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM stocks s
                WHERE timestamp = (SELECT MAX(timestamp) FROM stocks WHERE ticker = s.ticker)
                AND volume IS NOT NULL
                ORDER BY volume DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # Index Operations
    # =========================================================================
    
    def insert_index(self, index_data: Dict) -> int:
        """Insert or update market index"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO indices
                (name, value, variation_pct, variation_abs, open_value, 
                 high_value, low_value, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                index_data.get('name'),
                index_data.get('value'),
                index_data.get('variation_pct'),
                index_data.get('variation_abs'),
                index_data.get('open'),
                index_data.get('high'),
                index_data.get('low'),
                index_data.get('source'),
                index_data.get('timestamp', datetime.now().isoformat())
            ))
            
            return cursor.lastrowid
    
    def get_latest_indices(self) -> List[Dict]:
        """Get latest values for all indices"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM indices i
                WHERE timestamp = (
                    SELECT MAX(timestamp) FROM indices WHERE name = i.name
                )
                ORDER BY name
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # News Operations
    # =========================================================================
    
    def insert_news(self, article_data: Dict) -> int:
        """Insert news article"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO news
                    (hash_id, title, url, source, published_date, summary, content,
                     author, category, tags, relevance_score, matched_keywords, 
                     language, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data.get('hash_id'),
                    article_data.get('title'),
                    article_data.get('url'),
                    article_data.get('source'),
                    article_data.get('published_date'),
                    article_data.get('summary'),
                    article_data.get('content'),
                    article_data.get('author'),
                    article_data.get('category'),
                    json.dumps(article_data.get('tags', [])),
                    article_data.get('relevance_score', 0),
                    json.dumps(article_data.get('matched_keywords', [])),
                    article_data.get('language', 'fr'),
                    article_data.get('scraped_at', datetime.now().isoformat())
                ))
                
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Article already exists
                return 0
    
    def insert_news_batch(self, articles: List[Dict]) -> Tuple[int, int]:
        """Insert multiple news articles"""
        inserted = 0
        duplicates = 0
        
        for article in articles:
            result = self.insert_news(article)
            if result > 0:
                inserted += 1
            else:
                duplicates += 1
        
        return inserted, duplicates
    
    def get_news(self, limit: int = 50, offset: int = 0, 
                 min_relevance: float = 0.0,
                 source: str = None,
                 category: str = None) -> List[Dict]:
        """Get news articles with filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM news WHERE relevance_score >= ?"
            params = [min_relevance]
            
            if source:
                query += " AND source = ?"
                params.append(source)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY published_date DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                article = dict(row)
                article['tags'] = json.loads(article.get('tags', '[]'))
                article['matched_keywords'] = json.loads(article.get('matched_keywords', '[]'))
                results.append(article)
            
            return results
    
    def get_news_by_company(self, company_name: str, limit: int = 20) -> List[Dict]:
        """Get news mentioning a specific company"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM news 
                WHERE (title LIKE ? OR summary LIKE ? OR content LIKE ?)
                ORDER BY published_date DESC
                LIMIT ?
            """, (f'%{company_name}%', f'%{company_name}%', f'%{company_name}%', limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def search_news(self, query: str, limit: int = 50) -> List[Dict]:
        """Search news by keyword"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM news 
                WHERE title LIKE ? OR summary LIKE ? OR content LIKE ?
                ORDER BY relevance_score DESC, published_date DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # Alert Operations
    # =========================================================================
    
    def create_alert(self, alert_type: str, ticker: str = None,
                    condition: str = None, threshold: float = None,
                    message: str = None) -> int:
        """Create a new price alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alerts (type, ticker, condition, threshold, message)
                VALUES (?, ?, ?, ?, ?)
            """, (alert_type, ticker, condition, threshold, message))
            
            return cursor.lastrowid
    
    def check_alerts(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check and trigger alerts based on current prices"""
        triggered = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM alerts WHERE is_triggered = 0
            """)
            
            for alert in cursor.fetchall():
                alert = dict(alert)
                ticker = alert.get('ticker')
                
                if ticker and ticker in current_prices:
                    price = current_prices[ticker]
                    condition = alert.get('condition')
                    threshold = alert.get('threshold')
                    
                    should_trigger = False
                    if condition == 'above' and price > threshold:
                        should_trigger = True
                    elif condition == 'below' and price < threshold:
                        should_trigger = True
                    
                    if should_trigger:
                        cursor.execute("""
                            UPDATE alerts 
                            SET is_triggered = 1, triggered_at = ?
                            WHERE id = ?
                        """, (datetime.now().isoformat(), alert['id']))
                        
                        alert['current_price'] = price
                        triggered.append(alert)
        
        return triggered
    
    # =========================================================================
    # Logging Operations
    # =========================================================================
    
    def log_scrape(self, source: str, scrape_type: str, 
                   items_count: int = 0, status: str = "success",
                   error_message: str = None, duration: float = None):
        """Log a scrape operation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scrape_logs
                (source, scrape_type, items_count, status, error_message, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (source, scrape_type, items_count, status, error_message, duration))
    
    def get_scrape_stats(self, days: int = 7) -> Dict:
        """Get scraping statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    source,
                    COUNT(*) as total_scrapes,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(items_count) as total_items,
                    AVG(duration_seconds) as avg_duration
                FROM scrape_logs
                WHERE timestamp >= datetime('now', ?)
                GROUP BY source
            """, (f'-{days} days',))
            
            return {row['source']: dict(row) for row in cursor.fetchall()}
    
    # =========================================================================
    # Export Operations
    # =========================================================================
    
    def export_stocks_csv(self, filepath: str):
        """Export stocks to CSV"""
        import csv
        
        stocks = self.get_latest_stocks()
        
        if not stocks:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=stocks[0].keys())
            writer.writeheader()
            writer.writerows(stocks)
        
        logger.info(f"Exported {len(stocks)} stocks to {filepath}")
    
    def export_news_csv(self, filepath: str, limit: int = 1000):
        """Export news to CSV"""
        import csv
        
        news = self.get_news(limit=limit)
        
        if not news:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=news[0].keys())
            writer.writeheader()
            writer.writerows(news)
        
        logger.info(f"Exported {len(news)} news articles to {filepath}")


if __name__ == "__main__":
    # Test database operations
    print("Testing Market Database...")
    
    db = MarketDatabase("data/test_market.db")
    
    # Test stock insertion
    test_stock = {
        "ticker": "ATW",
        "name": "Attijariwafa Bank",
        "price": 744.90,
        "variation_pct": 2.03,
        "volume": 10000,
        "source": "test"
    }
    
    stock_id = db.insert_stock(test_stock)
    print(f"Inserted stock with ID: {stock_id}")
    
    # Test retrieval
    stock = db.get_stock_by_ticker("ATW")
    print(f"Retrieved stock: {stock}")
    
    # Test news insertion
    test_news = {
        "hash_id": "test123",
        "title": "Test Article",
        "url": "https://example.com/test",
        "source": "Test Source",
        "relevance_score": 75.0,
        "matched_keywords": ["bourse", "attijariwafa"]
    }
    
    news_id = db.insert_news(test_news)
    print(f"Inserted news with ID: {news_id}")
    
    print("\nDatabase test completed successfully!")
