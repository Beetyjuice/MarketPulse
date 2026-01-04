"""
Training script for LSTM model to predict stock prices
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import yfinance as yf
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMModelTrainer:
    def __init__(self, symbol, sequence_length=60):
        self.symbol = symbol
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def fetch_data(self, period="2y"):
        """Fetch historical stock data"""
        logger.info(f"Fetching data for {self.symbol}")
        stock = yf.Ticker(self.symbol)
        data = stock.history(period=period)
        return data
    
    def prepare_data(self, data, feature_columns=['Close']):
        """Prepare data for LSTM training"""
        # Select features
        df = data[feature_columns].copy()
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(df)
        
        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i, 0])  # Using Close price as target
        
        X, y = np.array(X), np.array(y)
        
        # Split into train and test sets
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self):
        """Build LSTM model"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train(self, X_train, y_train, epochs=50, batch_size=32):
        """Train the LSTM model"""
        logger.info("Training LSTM model...")
        
        self.model = self.build_model()
        
        # Train the model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        predictions = self.model.predict(X_test)
        
        # Inverse transform predictions and actual values
        pred_actual = self.scaler.inverse_transform(
            np.concatenate([predictions, np.zeros((predictions.shape[0], 4))], axis=1)
        )[:, 0]
        y_test_actual = self.scaler.inverse_transform(
            np.concatenate([y_test.reshape(-1, 1), np.zeros((y_test.shape[0], 4))], axis=1)
        )[:, 0]
        
        mse = mean_squared_error(y_test_actual, pred_actual)
        mae = mean_absolute_error(y_test_actual, pred_actual)
        
        logger.info(f"Model Evaluation - MSE: {mse}, MAE: {mae}")
        return mse, mae
    
    def save_model(self, filepath):
        """Save the trained model"""
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def run(self):
        """Run the complete training pipeline"""
        # Fetch data
        data = self.fetch_data()
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(data)
        
        # Reshape for LSTM (samples, time steps, features)
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        
        # Train model
        history = self.train(X_train, y_train)
        
        # Evaluate model
        self.evaluate(X_test, y_test)
        
        # Save model
        model_dir = "models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        self.save_model(f"models/lstm_model_{self.symbol}.h5")
        
        return history

if __name__ == "__main__":
    # Example usage
    symbols = ["AAPL", "GOOGL", "MSFT"]  # Example symbols
    
    for symbol in symbols:
        logger.info(f"Training LSTM model for {symbol}")
        trainer = LSTMModelTrainer(symbol)
        trainer.run()