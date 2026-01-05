"""
Configuration for Kafka connections
"""

KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_PRICE_TOPIC = 'stock_prices'
KAFKA_NEWS_TOPIC = 'financial_news'
KAFKA_PREDICTION_TOPIC = 'predictions'
KAFKA_ANOMALY_TOPIC = 'anomalies'

# Consumer group for processors
KAFKA_CONSUMER_GROUP = 'market_pulse_processor'