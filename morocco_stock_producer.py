"""
Morocco Stock Market Data Producer
Integrates with scraping scripts from the files folder
Publishes real-time stock data to Kafka
"""

import sys
import os
import json
import logging
from datetime import datetime
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Add files directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files'))

# Import scrapers from files folder
try:
    from stock_scraper import (
        StockQuote,
        BMCECapitalScraper,
        BPNetScraper,
        CasablancaBourseScraper,
        aggregate_stock_data
    )
    from news_scraper import NewsAggregator, NewsArticle
    from analysis import calculate_technical_indicators, TechnicalIndicators
    from helpers import normalize_ticker
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import scrapers: {e}")
    SCRAPERS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MoroccoStockProducer:
    """
    Producer for Morocco stock market data
    Uses scrapers from files folder to collect data and publish to Kafka
    """

    def __init__(
        self,
        kafka_servers=['localhost:9092'],
        stock_topic='morocco-stock-prices',
        news_topic='morocco-financial-news',
        use_selenium=False
    ):
        self.kafka_servers = kafka_servers
        self.stock_topic = stock_topic
        self.news_topic = news_topic
        self.use_selenium = use_selenium

        # Initialize Kafka producer
        self.producer = None
        self._connect_kafka()

        # Initialize scrapers if available
        self.scrapers = []
        if SCRAPERS_AVAILABLE:
            self._initialize_scrapers()

        # Initialize news aggregator
        self.news_aggregator = None
        if SCRAPERS_AVAILABLE:
            self._initialize_news_aggregator()

        # Track last update times
        self.last_stock_update = {}
        self.last_news_update = datetime.now()

    def _connect_kafka(self):
        """Connect to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda v: v.encode('utf-8') if v else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Connected to Kafka: {self.kafka_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.producer = None

    def _initialize_scrapers(self):
        """Initialize stock scrapers"""
        try:
            # BMCE Capital scraper
            logger.info("Initializing BMCE Capital scraper...")
            bmce_scraper = BMCECapitalScraper()
            self.scrapers.append(('BMCE', bmce_scraper))

            # BPNet scraper
            logger.info("Initializing BPNet scraper...")
            bpnet_scraper = BPNetScraper()
            self.scrapers.append(('BPNet', bpnet_scraper))

            # Casablanca Bourse scraper (with optional Selenium)
            if self.use_selenium:
                logger.info("Initializing Casablanca Bourse scraper with Selenium...")
                casablanca_scraper = CasablancaBourseScraper(use_selenium=True)
                self.scrapers.append(('Casablanca', casablanca_scraper))

            logger.info(f"Initialized {len(self.scrapers)} stock scrapers")

        except Exception as e:
            logger.error(f"Error initializing scrapers: {e}")

    def _initialize_news_aggregator(self):
        """Initialize news aggregator"""
        try:
            from settings import NEWS_SOURCES, KEYWORDS

            self.news_aggregator = NewsAggregator(
                sources=NEWS_SOURCES,
                keywords=KEYWORDS
            )
            logger.info("Initialized news aggregator")

        except Exception as e:
            logger.error(f"Error initializing news aggregator: {e}")

    def scrape_stocks(self):
        """Scrape stock data from all sources"""
        all_quotes = []

        for source_name, scraper in self.scrapers:
            try:
                logger.info(f"Scraping {source_name}...")
                quotes = scraper.scrape()

                if quotes:
                    logger.info(f"Retrieved {len(quotes)} quotes from {source_name}")
                    all_quotes.extend([(source_name, quote) for quote in quotes])
                else:
                    logger.warning(f"No quotes from {source_name}")

            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue

        return all_quotes

    def aggregate_stock_data(self, quotes_with_sources):
        """Aggregate stock data from multiple sources"""
        if not SCRAPERS_AVAILABLE or not quotes_with_sources:
            return {}

        # Group by ticker
        ticker_data = {}

        for source, quote in quotes_with_sources:
            ticker = quote.ticker

            if ticker not in ticker_data:
                ticker_data[ticker] = []

            ticker_data[ticker].append({
                'source': source,
                'quote': quote
            })

        # Aggregate using priority (Casablanca > BMCE > BPNet)
        source_priority = {'Casablanca': 3, 'BMCE': 2, 'BPNet': 1}

        aggregated = {}

        for ticker, data_list in ticker_data.items():
            # Sort by priority
            data_list.sort(key=lambda x: source_priority.get(x['source'], 0), reverse=True)

            # Use highest priority source as base
            best = data_list[0]['quote']

            # Fill in missing data from other sources
            for item in data_list[1:]:
                quote = item['quote']

                if not best.last_price and quote.last_price:
                    best.last_price = quote.last_price
                if not best.volume and quote.volume:
                    best.volume = quote.volume
                if not best.market_cap and quote.market_cap:
                    best.market_cap = quote.market_cap

            aggregated[ticker] = best

        return aggregated

    def publish_stock_data(self, stock_data):
        """Publish stock data to Kafka"""
        if not self.producer:
            logger.warning("Kafka producer not available")
            return

        published_count = 0

        for ticker, quote in stock_data.items():
            try:
                # Convert to dict
                data = {
                    'symbol': ticker,
                    'timestamp': datetime.now().isoformat(),
                    'price': quote.last_price,
                    'open': quote.open_price,
                    'high': quote.high_price,
                    'low': quote.low_price,
                    'close': quote.close_price,
                    'volume': quote.volume,
                    'change': quote.change,
                    'change_percent': quote.change_percent,
                    'market_cap': quote.market_cap,
                    'company_name': quote.company_name,
                    'sector': quote.sector
                }

                # Publish to Kafka
                future = self.producer.send(
                    self.stock_topic,
                    key=ticker,
                    value=data
                )

                # Wait for acknowledgment
                record_metadata = future.get(timeout=10)
                published_count += 1

                logger.debug(
                    f"Published {ticker}: ${quote.last_price} "
                    f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})"
                )

                # Track update time
                self.last_stock_update[ticker] = datetime.now()

            except KafkaError as e:
                logger.error(f"Kafka error publishing {ticker}: {e}")
            except Exception as e:
                logger.error(f"Error publishing {ticker}: {e}")

        logger.info(f"Published {published_count}/{len(stock_data)} stock quotes to Kafka")

    def scrape_news(self):
        """Scrape financial news"""
        if not self.news_aggregator:
            logger.warning("News aggregator not available")
            return []

        try:
            logger.info("Scraping financial news...")
            articles = self.news_aggregator.aggregate_news(max_articles=50)

            logger.info(f"Retrieved {len(articles)} news articles")
            return articles

        except Exception as e:
            logger.error(f"Error scraping news: {e}")
            return []

    def publish_news(self, articles):
        """Publish news articles to Kafka"""
        if not self.producer or not articles:
            return

        published_count = 0

        for article in articles:
            try:
                # Convert to dict
                data = {
                    'title': article.title,
                    'url': article.url,
                    'source': article.source,
                    'published_date': article.published_date.isoformat() if article.published_date else None,
                    'content': article.content,
                    'relevance_score': article.relevance_score,
                    'matched_keywords': article.matched_keywords,
                    'timestamp': datetime.now().isoformat()
                }

                # Publish to Kafka
                future = self.producer.send(
                    self.news_topic,
                    key=article.source,
                    value=data
                )

                future.get(timeout=10)
                published_count += 1

            except Exception as e:
                logger.error(f"Error publishing news: {e}")

        logger.info(f"Published {published_count}/{len(articles)} news articles to Kafka")
        self.last_news_update = datetime.now()

    def run_once(self):
        """Run one cycle of scraping and publishing"""
        logger.info("=" * 60)
        logger.info("Starting data collection cycle...")
        logger.info("=" * 60)

        # Scrape stocks
        if SCRAPERS_AVAILABLE and self.scrapers:
            quotes_with_sources = self.scrape_stocks()

            if quotes_with_sources:
                # Aggregate data
                stock_data = self.aggregate_stock_data(quotes_with_sources)

                if stock_data:
                    logger.info(f"Aggregated data for {len(stock_data)} stocks")

                    # Publish to Kafka
                    self.publish_stock_data(stock_data)
                else:
                    logger.warning("No stock data after aggregation")
            else:
                logger.warning("No stock quotes retrieved")
        else:
            logger.warning("Stock scrapers not available")

        # Scrape news (less frequently)
        time_since_news = (datetime.now() - self.last_news_update).total_seconds()

        if time_since_news > 300:  # 5 minutes
            articles = self.scrape_news()

            if articles:
                self.publish_news(articles)

    def run_continuous(self, interval_seconds=60):
        """Run continuously with specified interval"""
        logger.info(f"Starting continuous data collection (interval: {interval_seconds}s)")

        cycle_count = 0

        try:
            while True:
                cycle_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Cycle #{cycle_count}")
                logger.info(f"{'='*60}\n")

                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"Error in cycle: {e}")

                logger.info(f"Waiting {interval_seconds} seconds until next cycle...")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
            self.shutdown()

    def shutdown(self):
        """Shutdown producer"""
        if self.producer:
            logger.info("Flushing remaining messages...")
            self.producer.flush()
            self.producer.close()
            logger.info("Producer closed")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Morocco Stock Market Data Producer')
    parser.add_argument(
        '--kafka-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers (comma-separated)'
    )
    parser.add_argument(
        '--stock-topic',
        default='morocco-stock-prices',
        help='Kafka topic for stock prices'
    )
    parser.add_argument(
        '--news-topic',
        default='morocco-financial-news',
        help='Kafka topic for news'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Scraping interval in seconds'
    )
    parser.add_argument(
        '--use-selenium',
        action='store_true',
        help='Use Selenium for JavaScript-rendered pages'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )

    args = parser.parse_args()

    # Parse Kafka servers
    kafka_servers = args.kafka_servers.split(',')

    # Create producer
    producer = MoroccoStockProducer(
        kafka_servers=kafka_servers,
        stock_topic=args.stock_topic,
        news_topic=args.news_topic,
        use_selenium=args.use_selenium
    )

    # Run
    if args.once:
        producer.run_once()
    else:
        producer.run_continuous(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
