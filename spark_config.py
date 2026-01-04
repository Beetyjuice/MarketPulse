"""
Configuration for Spark connections
"""

SPARK_APP_NAME = "MarketPulse"
SPARK_MASTER_URL = "local[*]"  # Use local mode with all cores, or "spark://spark-master:7077" for cluster
SPARK_CASSANDRA_CONNECTION_HOST = "localhost"  # or "cassandra" if running in Docker
SPARK_CASSANDRA_CONNECTION_PORT = "9042"

# Spark configuration options
SPARK_CONFIG = {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.cassandra.connection.host": SPARK_CASSANDRA_CONNECTION_HOST,
    "spark.cassandra.connection.port": SPARK_CASSANDRA_CONNECTION_PORT,
}