-- MarketPulse Cassandra Schema Initialization
-- This script creates the keyspace and tables for the MarketPulse application

-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS market_pulse
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE market_pulse;

-- Stock prices table (time-series data)
CREATE TABLE IF NOT EXISTS stock_prices (
    symbol text,
    timestamp timestamp,
    price_open decimal,
    price_high decimal,
    price_low decimal,
    price_close decimal,
    volume bigint,
    rolling_avg decimal,
    rolling_std decimal,
    z_score decimal,
    is_anomaly boolean,
    source text,
    PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy'}
  AND default_time_to_live = 7776000;  -- 90 days

-- Financial news table
CREATE TABLE IF NOT EXISTS financial_news (
    news_id uuid,
    timestamp timestamp,
    symbol text,
    title text,
    url text,
    source text,
    content text,
    sentiment_score decimal,
    sentiment_label text,
    relevance_score decimal,
    matched_keywords list<text>,
    PRIMARY KEY (symbol, timestamp, news_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND default_time_to_live = 7776000;  -- 90 days

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    symbol text,
    timestamp timestamp,
    prediction_id uuid,
    model_type text,
    predicted_price decimal,
    confidence decimal,
    lower_bound decimal,
    upper_bound decimal,
    horizon_days int,
    features map<text, decimal>,
    PRIMARY KEY (symbol, timestamp, prediction_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND default_time_to_live = 2592000;  -- 30 days

-- Anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    anomaly_id uuid,
    symbol text,
    timestamp timestamp,
    anomaly_type text,
    severity text,
    description text,
    z_score decimal,
    price decimal,
    expected_price decimal,
    deviation_percent decimal,
    PRIMARY KEY (symbol, timestamp, anomaly_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND default_time_to_live = 15552000;  -- 180 days

-- Sentiment analysis table
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    symbol text,
    timestamp timestamp,
    sentiment_id uuid,
    sentiment_score decimal,
    sentiment_label text,
    news_count int,
    positive_count int,
    negative_count int,
    neutral_count int,
    avg_relevance decimal,
    PRIMARY KEY (symbol, timestamp, sentiment_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND default_time_to_live = 7776000;  -- 90 days

-- Multimodal analysis table
CREATE TABLE IF NOT EXISTS multimodal_analysis (
    symbol text,
    price_timestamp timestamp,
    news_timestamp timestamp,
    analysis_id uuid,
    price_close decimal,
    price_change_percent decimal,
    sentiment_score decimal,
    headline text,
    anomaly_signal text,
    correlation_score decimal,
    PRIMARY KEY (symbol, price_timestamp, analysis_id)
) WITH CLUSTERING ORDER BY (price_timestamp DESC)
  AND default_time_to_live = 7776000;  -- 90 days

-- Model performance tracking
CREATE TABLE IF NOT EXISTS model_performance (
    model_type text,
    symbol text,
    evaluation_date timestamp,
    metrics map<text, decimal>,
    predictions_count int,
    PRIMARY KEY (model_type, symbol, evaluation_date)
) WITH CLUSTERING ORDER BY (evaluation_date DESC);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_news_source ON financial_news (source);
CREATE INDEX IF NOT EXISTS idx_anomaly_type ON anomalies (anomaly_type);
CREATE INDEX IF NOT EXISTS idx_anomaly_severity ON anomalies (severity);
CREATE INDEX IF NOT EXISTS idx_prediction_model ON predictions (model_type);
CREATE INDEX IF NOT EXISTS idx_sentiment_label ON sentiment_analysis (sentiment_label);

-- Display created tables
DESCRIBE TABLES;
