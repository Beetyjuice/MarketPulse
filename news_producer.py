"""
Producer for financial news data
"""

import json
import time
from kafka import KafkaProducer
from datetime import datetime
import logging
import random
import pandas as pd
import os

from config.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_NEWS_TOPIC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Try to load news data from CSV (simulating Kaggle dataset)
        self.news_data = self.load_news_from_csv()
        if not self.news_data:
            # Fallback to sample data if CSV not available
            self.news_data = self.generate_sample_news()

    def load_news_from_csv(self):
        """Load news data from CSV file (simulating Kaggle financial news dataset)"""
        csv_path = "data/raw/news_data.csv"
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                # Assuming the CSV has columns: 'symbol', 'headline', 'content', 'timestamp'
                if 'headline' in df.columns and 'symbol' in df.columns:
                    logger.info(f"Loaded {len(df)} news articles from {csv_path}")
                    return df.to_dict('records')
                else:
                    logger.warning(f"CSV file {csv_path} doesn't have required columns")
                    return []
            except Exception as e:
                logger.error(f"Error loading news data from CSV: {e}")
                return []
        else:
            logger.info(f"CSV file {csv_path} not found, using sample data")
            return []

    def generate_sample_news(self):
        """Generate sample financial news data if CSV not available"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NFLX", "NVDA"]
        headlines = [
            "Market Rises on Strong Earnings Reports",
            "Tech Stocks Fall Amid Regulatory Concerns",
            "Federal Reserve Signals Possible Rate Changes",
            "Oil Prices Surge Following Supply Disruption",
            "Major Bank Reports Record Quarterly Profits",
            "Cryptocurrency Market Shows Volatility",
            "Unemployment Rate Drops to Multi-Year Low",
            "Housing Market Shows Signs of Cooling",
            "Global Trade Tensions Impact Export Stocks",
            "Renewable Energy Sector Sees Investment Boom",
            "AI Boom Drives Tech Stock Valuations",
            "Supply Chain Issues Affect Manufacturing Stocks",
            "Consumer Spending Exceeds Expectations",
            "Energy Sector Benefits from Price Increases",
            "Healthcare Stocks Rally on New Drug Approval"
        ]

        news_data = []
        for i in range(50):  # Generate 50 sample news items
            news_data.append({
                'symbol': random.choice(symbols),
                'headline': random.choice(headlines),
                'content': f"Analysis of market impact for {random.choice(symbols)} following recent news. Experts provide insights on potential market movements.",
                'timestamp': datetime.now().isoformat()
            })

        logger.info("Generated 50 sample news articles")
        return news_data

    def generate_news_data(self, symbol):
        """Generate financial news data for a given symbol from available data"""
        # Filter news for the specific symbol
        symbol_news = [item for item in self.news_data if item.get('symbol', '').upper() == symbol.upper()]

        if symbol_news:
            # Pick a random news item for this symbol
            news_item = random.choice(symbol_news)
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "headline": news_item.get('headline', f"News about {symbol}"),
                "content": news_item.get('content', f"Content about {symbol}")
            }
        else:
            # Fallback to generic news if no specific symbol news available
            headlines = [
                f"{symbol} Reports Strong Earnings",
                f"Regulatory Concerns Impact {symbol} Stock",
                f"{symbol} Announces Major Partnership",
                f"Market Analysts Upgrade {symbol} Rating",
                f"{symbol} Faces Supply Chain Challenges"
            ]
            headline = random.choice(headlines)
            content = f"Analysis of {symbol} stock following recent market trends. {headline.lower()} has impacted the sector significantly."

            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "headline": headline,
                "content": content
            }

    def send_news_data(self, symbol):
        """Send news data to Kafka"""
        data = self.generate_news_data(symbol)
        try:
            self.producer.send(KAFKA_NEWS_TOPIC, value=data)
            self.producer.flush()
            logger.info(f"Sent news data for {symbol}: {data['headline']}")
            return True
        except Exception as e:
            logger.error(f"Error sending news data to Kafka: {e}")
            return False

    def run(self, symbols, interval=120):
        """Run the news producer continuously"""
        logger.info(f"Starting news producer for symbols: {symbols}")
        while True:
            for symbol in symbols:
                self.send_news_data(symbol)
                time.sleep(1)  # Small delay between symbols
            time.sleep(interval)  # Wait before next batch

if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]  # Default symbols
    producer = NewsProducer()

    try:
        # For testing, just send one batch
        for symbol in symbols:
            producer.send_news_data(symbol)
            time.sleep(2)  # Delay between symbols
    except KeyboardInterrupt:
        logger.info("Stopping news producer...")
    finally:
        producer.producer.close()