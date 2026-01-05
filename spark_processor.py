"""
Spark processor for MarketPulse: Real-Time Sentiment & Price Anomaly Detection System
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import logging
from datetime import datetime
import json

from config.spark_config import SPARK_APP_NAME, SPARK_MASTER_URL, SPARK_CONFIG
from config.cassandra_config import CASSANDRA_HOST, CASSANDRA_KEYSPACE
from config.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_PRICE_TOPIC, KAFKA_NEWS_TOPIC, KAFKA_PREDICTION_TOPIC

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkProcessor:
    def __init__(self):
        # Initialize Spark session with Cassandra configuration
        self.spark = SparkSession.builder \
            .appName(SPARK_APP_NAME) \
            .master(SPARK_MASTER_URL) \
            .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
            .config("spark.sql.extensions", "com.datastax.spark.connector.CassandraSparkExtensions") \
            .config("spark.sql.catalog.cassandra", "com.datastax.spark.connector.datasource.CassandraCatalog") \
            .getOrCreate()

        # Define schemas for Kafka messages
        self.price_schema = StructType([
            StructField("symbol", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("price_open", DoubleType(), True),
            StructField("price_high", DoubleType(), True),
            StructField("price_low", DoubleType(), True),
            StructField("price_close", DoubleType(), True),
            StructField("volume", LongType(), True)
        ])

        self.news_schema = StructType([
            StructField("symbol", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("headline", StringType(), True),
            StructField("content", StringType(), True)
        ])

    def process_price_data_with_anomaly_detection(self):
        """Process stock price data from Kafka with anomaly detection"""
        logger.info("Starting to process price data from Kafka with anomaly detection...")

        # Read price data from Kafka
        price_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", ",".join(KAFKA_BOOTSTRAP_SERVERS)) \
            .option("subscribe", KAFKA_PRICE_TOPIC) \
            .option("startingOffsets", "latest") \
            .load() \
            .select(
                from_json(col("value").cast("string"), self.price_schema).alias("data")
            ).select("data.*")

        # Convert timestamp string to timestamp type
        price_df = price_df.withColumn("timestamp", to_timestamp(col("timestamp")))

        # Calculate rolling averages for anomaly detection
        windowSpec = Window.partitionBy("symbol").orderBy("timestamp").rowsBetween(-29, 0)  # 30-day rolling window

        price_df = price_df.withColumn("rolling_avg", avg("price_close").over(windowSpec)) \
                          .withColumn("rolling_std", stddev("price_close").over(windowSpec))

        # Calculate z-score for anomaly detection
        price_df = price_df.withColumn("z_score",
                                      when(col("rolling_std") != 0,
                                           abs(col("price_close") - col("rolling_avg")) / col("rolling_std"))
                                      .otherwise(0))

        # Flag anomalies (z-score > 2 indicates potential anomaly)
        price_df = price_df.withColumn("is_anomaly", col("z_score") > 2.0)

        # Write to Cassandra
        price_query = price_df.writeStream \
            .outputMode("append") \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="stock_prices", keyspace=CASSANDRA_KEYSPACE) \
            .option("checkpointLocation", "/tmp/checkpoint_price") \
            .start()

        # Filter anomalies and send to prediction topic
        anomalies_df = price_df.filter(col("is_anomaly") == True)

        anomaly_query = anomalies_df.writeStream \
            .outputMode("append") \
            .format("kafka") \
            .option("kafka.bootstrap.servers", ",".join(KAFKA_BOOTSTRAP_SERVERS)) \
            .option("topic", KAFKA_PREDICTION_TOPIC) \
            .option("checkpointLocation", "/tmp/checkpoint_anomaly") \
            .start()

        return price_query, anomaly_query

    def process_news_data_with_sentiment(self):
        """Process news data from Kafka with sentiment analysis placeholder"""
        logger.info("Starting to process news data from Kafka with sentiment analysis...")

        # Read news data from Kafka
        news_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", ",".join(KAFKA_BOOTSTRAP_SERVERS)) \
            .option("subscribe", KAFKA_NEWS_TOPIC) \
            .option("startingOffsets", "latest") \
            .load() \
            .select(
                from_json(col("value").cast("string"), self.news_schema).alias("data")
            ).select("data.*")

        # Convert timestamp string to timestamp type
        news_df = news_df.withColumn("timestamp", to_timestamp(col("timestamp")))

        # Placeholder for sentiment analysis (in a real system, you would apply a UDF with a pre-trained model)
        # For now, we'll simulate sentiment scores based on keywords in headlines
        news_df = news_df.withColumn("sentiment_score",
                                    when(col("headline").contains("rise") | col("headline").contains("up") |
                                         col("headline").contains("gain") | col("headline").contains("positive"),
                                         lit(0.8))
                                    .when(col("headline").contains("fall") | col("headline").contains("down") |
                                          col("headline").contains("loss") | col("headline").contains("negative"),
                                          lit(-0.8))
                                    .otherwise(lit(0.0)))

        news_df = news_df.withColumn("sentiment_label",
                                    when(col("sentiment_score") > 0.5, lit("positive"))
                                    .when(col("sentiment_score") < -0.5, lit("negative"))
                                    .otherwise(lit("neutral")))

        # Write to Cassandra
        news_query = news_df.writeStream \
            .outputMode("append") \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="financial_news", keyspace=CASSANDRA_KEYSPACE) \
            .option("checkpointLocation", "/tmp/checkpoint_news") \
            .start()

        return news_query

    def join_streams_for_multimodal_analysis(self):
        """Join price and news streams for multimodal analysis"""
        logger.info("Starting multimodal analysis by joining price and news streams...")

        # Read price data
        price_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", ",".join(KAFKA_BOOTSTRAP_SERVERS)) \
            .option("subscribe", KAFKA_PRICE_TOPIC) \
            .option("startingOffsets", "latest") \
            .load() \
            .select(
                from_json(col("value").cast("string"), self.price_schema).alias("data")
            ).select("data.*")

        # Read news data
        news_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", ",".join(KAFKA_BOOTSTRAP_SERVERS)) \
            .option("subscribe", KAFKA_NEWS_TOPIC) \
            .option("startingOffsets", "latest") \
            .load() \
            .select(
                from_json(col("value").cast("string"), self.news_schema).alias("data")
            ).select("data.*")

        # Convert timestamps
        price_df = price_df.withColumn("timestamp", to_timestamp(col("timestamp")))
        news_df = news_df.withColumn("timestamp", to_timestamp(col("timestamp")))

        # Join streams based on symbol and time window (e.g., news within 1 hour of price change)
        joined_df = price_df.join(
            news_df,
            (price_df.symbol == news_df.symbol) &
            (news_df.timestamp >= price_df.timestamp - expr("interval 1 hour")) &
            (news_df.timestamp <= price_df.timestamp + expr("interval 1 hour")),
            "inner"
        ).select(
            price_df.symbol,
            price_df.timestamp.alias("price_timestamp"),
            news_df.timestamp.alias("news_timestamp"),
            price_df.price_close,
            news_df.headline,
            news_df.content,
            news_df.sentiment_score if "sentiment_score" in news_df.columns else lit(0.0).alias("sentiment_score")
        )

        # Perform multimodal analysis - detect when negative sentiment aligns with price drops
        multimodal_df = joined_df.withColumn("anomaly_signal",
                                           when(
                                               (col("sentiment_score") < -0.5) &
                                               ((col("price_close") - lag("price_close", 1).over(
                                                   Window.partitionBy("symbol").orderBy("price_timestamp")
                                               )) / lag("price_close", 1).over(
                                                   Window.partitionBy("symbol").orderBy("price_timestamp")
                                               ) * 100 < -2.0),  # Price drop > 2%
                                               lit("NEGATIVE_SENTIMENT_PRICE_DROP")
                                           ).otherwise(lit("NORMAL")))

        # Write multimodal analysis results to Cassandra
        multimodal_query = multimodal_df.writeStream \
            .outputMode("append") \
            .format("org.apache.spark.sql.cassandra") \
            .options(table="multimodal_analysis", keyspace=CASSANDRA_KEYSPACE) \
            .option("checkpointLocation", "/tmp/checkpoint_multimodal") \
            .start()

        return multimodal_query

    def run(self):
        """Run the Spark processor with all components"""
        logger.info("Starting MarketPulse Spark processor with anomaly detection...")

        # Start processing price data with anomaly detection
        price_query, anomaly_query = self.process_price_data_with_anomaly_detection()

        # Start processing news data with sentiment
        news_query = self.process_news_data_with_sentiment()

        # Start multimodal analysis
        multimodal_query = self.join_streams_for_multimodal_analysis()

        # Wait for termination
        try:
            # Wait for all queries to terminate
            price_query.awaitTermination()
            news_query.awaitTermination()
            multimodal_query.awaitTermination()
            anomaly_query.awaitTermination()
        except KeyboardInterrupt:
            logger.info("Stopping Spark processor...")
            price_query.stop()
            news_query.stop()
            multimodal_query.stop()
            anomaly_query.stop()

if __name__ == "__main__":
    processor = SparkProcessor()
    processor.run()