"""
Producer for stock price data
"""

import json
import time
import yfinance as yf
from confluent_kafka import Producer
from datetime import datetime
import logging

from config.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_PRICE_TOPIC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceProducer:
    def __init__(self):
        # confluent_kafka expects a string, not a list
        bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS[0] if isinstance(KAFKA_BOOTSTRAP_SERVERS, list) else KAFKA_BOOTSTRAP_SERVERS
        
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers
        })

    def delivery_report(self, err, msg):
        """Callback for message delivery reports"""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def fetch_stock_data(self, symbol):
        """Fetch current stock data for a given symbol"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d", interval="1m")

            if not hist.empty:
                latest = hist.iloc[-1]
                return {
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat(),
                    "price_open": float(latest['Open']),
                    "price_high": float(latest['High']),
                    "price_low": float(latest['Low']),
                    "price_close": float(latest['Close']),
                    "volume": int(latest['Volume'])
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def send_price_data(self, symbol):
        """Send stock price data to Kafka"""
        data = self.fetch_stock_data(symbol)
        if data:
            try:
                # confluent_kafka uses produce() not send()
                # and requires bytes for the value
                self.producer.produce(
                    KAFKA_PRICE_TOPIC,
                    value=json.dumps(data).encode('utf-8'),
                    callback=self.delivery_report
                )
                self.producer.flush()
                logger.info(f"Sent price data for {symbol}: {data}")
                return True
            except Exception as e:
                logger.error(f"Error sending data to Kafka: {e}")
                return False
        return False

    def run(self, symbols, interval=60):
        """Run the price producer continuously"""
        logger.info(f"Starting price producer for symbols: {symbols}")
        while True:
            for symbol in symbols:
                self.send_price_data(symbol)
                time.sleep(1)  # Small delay between symbols
            time.sleep(interval)  # Wait before next batch

if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]  # Default symbols
    producer = PriceProducer()

    try:
        # For testing, just send one batch
        for symbol in symbols:
            producer.send_price_data(symbol)
            time.sleep(2)  # Delay between symbols
    except KeyboardInterrupt:
        logger.info("Stopping price producer...")
    finally:
        producer.producer.flush()
        logger.info("Producer closed")
