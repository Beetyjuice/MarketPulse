#!/usr/bin/env python3
"""
Morocco Stock Market Data Aggregator - Main Orchestrator
Combines stock scraping, news monitoring, and data storage
"""

import argparse
import json
import time
import signal
import sys
from datetime import datetime
from typing import Optional
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import ScraperConfig, SchedulerConfig, STOCK_TICKERS
from scrapers.stock_scraper import MarketDataAggregator, get_market_data
from news.news_scraper import NewsAggregator, NewsWatchdog, print_alert
from utils.database import MarketDatabase
from utils.helpers import is_market_hours

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/scraper.log')
    ]
)
logger = logging.getLogger(__name__)


class MarketMonitor:
    """
    Main orchestrator for market data collection and monitoring
    """
    
    def __init__(self, db_path: str = "data/morocco_market.db"):
        self.db = MarketDatabase(db_path)
        self.stock_aggregator = MarketDataAggregator()
        self.news_aggregator = NewsAggregator()
        self.scheduler_config = SchedulerConfig()
        self.is_running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received...")
        self.is_running = False
    
    def scrape_stocks(self, export_json: bool = True) -> dict:
        """
        Scrape current stock data from all sources
        """
        logger.info("Starting stock data scrape...")
        start_time = time.time()
        
        try:
            # Get data from all sources
            all_data = self.stock_aggregator.get_all_stocks()
            merged_stocks = self.stock_aggregator.get_merged_stocks()
            indices = self.stock_aggregator.get_indices()
            
            # Store in database
            stocks_inserted = 0
            for stock in merged_stocks:
                try:
                    self.db.insert_stock(stock.to_dict())
                    stocks_inserted += 1
                except Exception as e:
                    logger.warning(f"Error storing stock {stock.ticker}: {e}")
            
            # Store indices
            for index in indices:
                try:
                    self.db.insert_index(index.to_dict())
                except Exception as e:
                    logger.warning(f"Error storing index {index.name}: {e}")
            
            duration = time.time() - start_time
            
            # Log the scrape
            for source, stocks in all_data.items():
                self.db.log_scrape(
                    source=source,
                    scrape_type="stocks",
                    items_count=len(stocks),
                    status="success",
                    duration=duration
                )
            
            # Export to JSON if requested
            if export_json:
                self.stock_aggregator.export_to_json("data/market_data.json")
            
            result = {
                "status": "success",
                "stocks_count": stocks_inserted,
                "indices_count": len(indices),
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Stock scrape completed: {stocks_inserted} stocks, {len(indices)} indices in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Stock scrape failed: {e}")
            self.db.log_scrape("all", "stocks", 0, "error", str(e))
            return {"status": "error", "message": str(e)}
    
    def scrape_news(self, max_per_source: int = 10, 
                    min_relevance: float = 0.0,
                    export_json: bool = True) -> dict:
        """
        Scrape news from all configured sources
        """
        logger.info("Starting news scrape...")
        start_time = time.time()
        
        try:
            # Scrape all news sources
            articles = self.news_aggregator.scrape_all(
                max_per_source=max_per_source,
                min_relevance=min_relevance
            )
            
            # Store in database
            inserted, duplicates = self.db.insert_news_batch(
                [a.to_dict() for a in articles]
            )
            
            duration = time.time() - start_time
            
            # Log the scrape
            self.db.log_scrape(
                source="all_news",
                scrape_type="news",
                items_count=inserted,
                status="success",
                duration=duration
            )
            
            # Export to JSON if requested
            if export_json:
                self.news_aggregator.export_to_json("data/news_data.json")
            
            result = {
                "status": "success",
                "articles_total": len(articles),
                "articles_new": inserted,
                "articles_duplicate": duplicates,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"News scrape completed: {inserted} new articles ({duplicates} duplicates) in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"News scrape failed: {e}")
            self.db.log_scrape("all_news", "news", 0, "error", str(e))
            return {"status": "error", "message": str(e)}
    
    def run_once(self):
        """Run a single scrape cycle"""
        logger.info("=" * 60)
        logger.info("Starting single scrape cycle")
        logger.info("=" * 60)
        
        # Scrape stocks
        stock_result = self.scrape_stocks()
        
        # Scrape news
        news_result = self.scrape_news()
        
        return {
            "stocks": stock_result,
            "news": news_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_continuous(self, stock_interval: int = 300, 
                       news_interval: int = 900):
        """
        Run continuous monitoring
        
        Args:
            stock_interval: Seconds between stock scrapes (default 5 min)
            news_interval: Seconds between news scrapes (default 15 min)
        """
        logger.info("Starting continuous monitoring...")
        logger.info(f"Stock interval: {stock_interval}s, News interval: {news_interval}s")
        
        self.is_running = True
        last_stock_scrape = 0
        last_news_scrape = 0
        
        while self.is_running:
            current_time = time.time()
            
            # Check if we should scrape stocks
            if current_time - last_stock_scrape >= stock_interval:
                if is_market_hours():
                    self.scrape_stocks()
                else:
                    logger.info("Market closed, skipping stock scrape")
                last_stock_scrape = current_time
            
            # Check if we should scrape news
            if current_time - last_news_scrape >= news_interval:
                self.scrape_news()
                last_news_scrape = current_time
            
            # Sleep for a short interval before checking again
            time.sleep(10)
        
        logger.info("Continuous monitoring stopped")
    
    def get_market_summary(self) -> dict:
        """Get current market summary"""
        stocks = self.db.get_latest_stocks()
        indices = self.db.get_latest_indices()
        
        gainers = self.db.get_top_gainers(5)
        losers = self.db.get_top_losers(5)
        active = self.db.get_most_active(5)
        
        news = self.db.get_news(limit=10, min_relevance=30)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "market": {
                "total_stocks": len(stocks),
                "indices": indices
            },
            "top_gainers": gainers,
            "top_losers": losers,
            "most_active": active,
            "recent_news": news
        }
    
    def get_stock_info(self, ticker: str) -> dict:
        """Get detailed information for a stock"""
        stock = self.db.get_stock_by_ticker(ticker)
        history = self.db.get_stock_history(ticker, days=30)
        news = self.db.get_news_by_company(STOCK_TICKERS.get(ticker, {}).get('name', ticker))
        
        return {
            "current": stock,
            "history": history,
            "news": news[:10],
            "ticker_info": STOCK_TICKERS.get(ticker, {})
        }
    
    def export_all_data(self, output_dir: str = "data/exports"):
        """Export all data to files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export stocks
        self.db.export_stocks_csv(f"{output_dir}/stocks_{timestamp}.csv")
        
        # Export news
        self.db.export_news_csv(f"{output_dir}/news_{timestamp}.csv")
        
        # Export market summary as JSON
        summary = self.get_market_summary()
        with open(f"{output_dir}/summary_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data exported to {output_dir}")


def main():
    """Main entry point with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Morocco Stock Market Data Scraper and Monitor"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Run a single scrape")
    scrape_parser.add_argument("--stocks", action="store_true", help="Scrape stocks only")
    scrape_parser.add_argument("--news", action="store_true", help="Scrape news only")
    scrape_parser.add_argument("--export", action="store_true", help="Export to JSON")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Run continuous monitoring")
    monitor_parser.add_argument("--stock-interval", type=int, default=300,
                               help="Seconds between stock scrapes")
    monitor_parser.add_argument("--news-interval", type=int, default=900,
                               help="Seconds between news scrapes")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Get market summary")
    summary_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Stock info command
    stock_parser = subparsers.add_parser("stock", help="Get stock information")
    stock_parser.add_argument("ticker", help="Stock ticker symbol")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export all data")
    export_parser.add_argument("--output-dir", default="data/exports",
                              help="Output directory")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available tickers")
    
    args = parser.parse_args()
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    # Initialize monitor
    monitor = MarketMonitor()
    
    if args.command == "scrape":
        if args.stocks:
            result = monitor.scrape_stocks(export_json=args.export)
        elif args.news:
            result = monitor.scrape_news(export_json=args.export)
        else:
            result = monitor.run_once()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "monitor":
        monitor.run_continuous(
            stock_interval=args.stock_interval,
            news_interval=args.news_interval
        )
    
    elif args.command == "summary":
        summary = monitor.get_market_summary()
        if args.json:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 60)
            print("MOROCCO STOCK MARKET SUMMARY")
            print("=" * 60)
            print(f"Timestamp: {summary['timestamp']}")
            print(f"Total Stocks: {summary['market']['total_stocks']}")
            
            print("\n--- INDICES ---")
            for idx in summary['market']['indices']:
                print(f"  {idx['name']}: {idx['value']} ({idx.get('variation_pct', 'N/A')}%)")
            
            print("\n--- TOP GAINERS ---")
            for stock in summary['top_gainers']:
                print(f"  {stock['ticker']}: {stock['price']} MAD (+{stock['variation_pct']}%)")
            
            print("\n--- TOP LOSERS ---")
            for stock in summary['top_losers']:
                print(f"  {stock['ticker']}: {stock['price']} MAD ({stock['variation_pct']}%)")
            
            print("\n--- RECENT NEWS ---")
            for article in summary['recent_news'][:5]:
                print(f"  [{article['relevance_score']:.0f}] {article['title'][:60]}...")
    
    elif args.command == "stock":
        info = monitor.get_stock_info(args.ticker.upper())
        print(json.dumps(info, indent=2, ensure_ascii=False, default=str))
    
    elif args.command == "export":
        monitor.export_all_data(args.output_dir)
        print(f"Data exported to {args.output_dir}")
    
    elif args.command == "list":
        print("\n" + "=" * 60)
        print("AVAILABLE STOCK TICKERS")
        print("=" * 60)
        for ticker, info in sorted(STOCK_TICKERS.items()):
            print(f"  {ticker:6} - {info['name']:40} ({info['sector']})")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
