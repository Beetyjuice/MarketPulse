"""
Configuration for Cassandra connections
"""

CASSANDRA_HOST = "localhost"  # or "cassandra" if running in Docker
CASSANDRA_PORT = 9042
CASSANDRA_KEYSPACE = "market_pulse"

# Table names
PRICES_TABLE = "stock_prices"
NEWS_TABLE = "financial_news"
PREDICTIONS_TABLE = "predictions"
SENTIMENT_TABLE = "sentiment_analysis"
ANOMALIES_TABLE = "anomalies"
MULTIMODAL_ANALYSIS_TABLE = "multimodal_analysis"

# Cassandra schema
CASSANDRA_SCHEMA = f"""
CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};

USE {CASSANDRA_KEYSPACE};

CREATE TABLE IF NOT EXISTS {PRICES_TABLE} (
    id UUID,
    symbol TEXT,
    timestamp TIMESTAMP,
    price_open DECIMAL,
    price_high DECIMAL,
    price_low DECIMAL,
    price_close DECIMAL,
    volume BIGINT,
    rolling_avg DECIMAL,
    rolling_std DECIMAL,
    z_score FLOAT,
    is_anomaly BOOLEAN,
    PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS {NEWS_TABLE} (
    id UUID,
    symbol TEXT,
    timestamp TIMESTAMP,
    headline TEXT,
    content TEXT,
    sentiment_score FLOAT,
    sentiment_label TEXT,
    PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS {PREDICTIONS_TABLE} (
    id UUID,
    symbol TEXT,
    timestamp TIMESTAMP,
    predicted_price DECIMAL,
    confidence FLOAT,
    PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS {SENTIMENT_TABLE} (
    id UUID,
    symbol TEXT,
    timestamp TIMESTAMP,
    sentiment_score FLOAT,
    sentiment_label TEXT,
    PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS {ANOMALIES_TABLE} (
    id UUID,
    symbol TEXT,
    timestamp TIMESTAMP,
    anomaly_type TEXT,
    description TEXT,
    severity TEXT,
    PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS {MULTIMODAL_ANALYSIS_TABLE} (
    id UUID,
    symbol TEXT,
    price_timestamp TIMESTAMP,
    news_timestamp TIMESTAMP,
    price_close DECIMAL,
    headline TEXT,
    content TEXT,
    sentiment_score FLOAT,
    anomaly_signal TEXT,
    PRIMARY KEY (symbol, price_timestamp)
) WITH CLUSTERING ORDER BY (price_timestamp DESC);
"""