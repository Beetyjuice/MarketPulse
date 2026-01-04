"""
Kafka configuration settings
"""

# Kafka connection settings - can be string or list
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']

# Kafka topics
KAFKA_PRICE_TOPIC = 'stock-prices'
KAFKA_NEWS_TOPIC = 'financial-news'
KAFKA_ANOMALY_TOPIC = 'anomalies'
