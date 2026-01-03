"""
Data loading utilities for MarketPulse: Real-Time Sentiment & Price Anomaly Detection System
"""

import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta
import os
import numpy as np
from scipy import stats

from utils.helpers import setup_logging

logger = setup_logging(__name__)

class DataLoader:
    def __init__(self):
        pass

    def load_stock_data(self, symbol, period="1y", interval="1d"):
        """
        Load stock data using yfinance
        """
        try:
            logger.info(f"Loading stock data for {symbol} with period {period} and interval {interval}")
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)

            # Reset index to make date a column
            data = data.reset_index()
            data.rename(columns={'Date': 'timestamp', 'Open': 'open', 'High': 'high',
                                'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)

            # Add symbol column
            data['symbol'] = symbol

            # Calculate technical indicators for anomaly detection
            data = self.calculate_technical_indicators(data)

            logger.info(f"Loaded {len(data)} records for {symbol}")
            return data
        except Exception as e:
            logger.error(f"Error loading stock data for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_technical_indicators(self, data):
        """
        Calculate technical indicators for anomaly detection
        """
        # Calculate rolling statistics for anomaly detection
        data['rolling_avg'] = data['close'].rolling(window=30, min_periods=1).mean()
        data['rolling_std'] = data['close'].rolling(window=30, min_periods=1).std()

        # Calculate z-score for anomaly detection
        data['z_score'] = (data['close'] - data['rolling_avg']) / data['rolling_std']

        # Flag potential anomalies (z-score > 2 or < -2)
        data['is_anomaly'] = (data['z_score'].abs() > 2.0)

        # Calculate additional indicators
        data['price_change_pct'] = data['close'].pct_change()
        data['volatility'] = data['price_change_pct'].rolling(window=10).std()

        return data

    def detect_anomalies(self, data, method='z_score', threshold=2.0):
        """
        Detect anomalies in stock data using various methods
        """
        anomalies = pd.DataFrame()

        if method == 'z_score':
            # Z-score based anomaly detection
            rolling_avg = data['close'].rolling(window=30, min_periods=1).mean()
            rolling_std = data['close'].rolling(window=30, min_periods=1).std()
            z_scores = (data['close'] - rolling_avg) / rolling_std

            anomalies = data[z_scores.abs() > threshold].copy()
            anomalies['anomaly_type'] = 'z_score_anomaly'
            anomalies['anomaly_score'] = z_scores[anomalies.index]

        elif method == 'iqr':
            # IQR based anomaly detection
            Q1 = data['close'].quantile(0.25)
            Q3 = data['close'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            anomalies = data[(data['close'] < lower_bound) | (data['close'] > upper_bound)].copy()
            anomalies['anomaly_type'] = 'iqr_anomaly'

        elif method == 'modified_z_score':
            # Modified Z-score using median and MAD
            median = data['close'].median()
            mad = np.median(np.abs(data['close'] - median))
            modified_z_scores = 0.6745 * (data['close'] - median) / mad

            anomalies = data[modified_z_scores.abs() > threshold].copy()
            anomalies['anomaly_type'] = 'modified_z_score_anomaly'
            anomalies['anomaly_score'] = modified_z_scores[anomalies.index]

        return anomalies

    def load_news_data(self, symbols, days=30):
        """
        Load news data (placeholder - in real implementation, connect to news API)
        """
        logger.info(f"Loading news data for symbols: {symbols}")

        # This is a placeholder implementation
        # In a real system, you would connect to a financial news API
        import random
        from datetime import datetime, timedelta

        # Sample financial news headlines with sentiment
        positive_headlines = [
            "Company Reports Strong Quarterly Earnings",
            "Tech Giant Announces Breakthrough Innovation",
            "Market Shows Robust Growth Amid Economic Uncertainty",
            "Major Acquisition Expected to Boost Stock",
            "New Product Launch Exceeds Expectations"
        ]

        negative_headlines = [
            "Stock Plunges Amid Regulatory Concerns",
            "Company Misses Earnings Expectations",
            "Market Volatility Increases Significantly",
            "Major Losses Reported by Industry Leader",
            "Economic Indicators Point to Recession"
        ]

        neutral_headlines = [
            "Company Announces Leadership Changes",
            "Industry Report Shows Mixed Results",
            "Market Opens Flat Today",
            "Quarterly Results in Line with Expectations",
            "Company Updates Business Strategy"
        ]

        news_data = []
        for symbol in symbols:
            for i in range(days):
                date = datetime.now() - timedelta(days=i)

                # Randomly select a headline type
                rand = random.random()
                if rand < 0.3:  # 30% chance of positive
                    headline = random.choice(positive_headlines)
                    sentiment_score = random.uniform(0.5, 1.0)
                elif rand < 0.6:  # 30% chance of negative
                    headline = random.choice(negative_headlines)
                    sentiment_score = random.uniform(-1.0, -0.5)
                else:  # 40% chance of neutral
                    headline = random.choice(neutral_headlines)
                    sentiment_score = random.uniform(-0.3, 0.3)

                news_data.append({
                    'timestamp': date,
                    'symbol': symbol,
                    'headline': f'{symbol}: {headline}',
                    'content': f'Detailed news content for {symbol} regarding: {headline}. Market analysts provide insights.',
                    'sentiment_score': sentiment_score,
                    'sentiment_label': 'positive' if sentiment_score > 0.1 else 'negative' if sentiment_score < -0.1 else 'neutral'
                })

        return pd.DataFrame(news_data)

    def load_from_csv(self, file_path):
        """
        Load data from CSV file
        """
        try:
            logger.info(f"Loading data from CSV: {file_path}")
            if os.path.exists(file_path):
                data = pd.read_csv(file_path)
                logger.info(f"Loaded {len(data)} records from {file_path}")

                # Calculate technical indicators if loading stock data
                if 'close' in data.columns:
                    data = self.calculate_technical_indicators(data)

                return data
            else:
                logger.warning(f"File does not exist: {file_path}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return pd.DataFrame()

    def save_to_csv(self, data, file_path):
        """
        Save data to CSV file
        """
        try:
            logger.info(f"Saving data to CSV: {file_path}")
            data.to_csv(file_path, index=False)
            logger.info(f"Saved {len(data)} records to {file_path}")
        except Exception as e:
            logger.error(f"Error saving CSV file {file_path}: {e}")

    def load_from_database(self, connection, query):
        """
        Load data from database (placeholder)
        """
        try:
            logger.info(f"Loading data from database with query: {query[:50]}...")
            # In a real implementation, execute the query against the database
            # For now, return empty DataFrame
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            return pd.DataFrame()

# Singleton instance
data_loader = DataLoader()