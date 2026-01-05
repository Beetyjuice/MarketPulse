"""
Prediction Service for real-time stock price predictions
Loads trained models and provides API for inference
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
import pickle
import json
import os
import logging
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service for making stock price predictions using trained models
    Supports multiple model types and ensemble predictions
    """

    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.configs = {}

    def load_model(self, symbol: str, model_type: str = 'ensemble') -> bool:
        """Load a trained model for a specific symbol"""
        try:
            if model_type == 'ensemble':
                model_path = os.path.join(self.model_dir, 'ensemble', f'ensemble_{symbol}.h5')
                scaler_path = os.path.join(self.model_dir, 'ensemble', f'scaler_{symbol}.pkl')
                config_path = os.path.join(self.model_dir, 'ensemble', f'config_{symbol}.json')
            else:
                model_path = os.path.join(self.model_dir, f'{model_type}_model_{symbol}.h5')
                scaler_path = os.path.join(self.model_dir, f'{model_type}_model_{symbol}_scaler.pkl')
                config_path = os.path.join(self.model_dir, f'{model_type}_model_{symbol}_config.json')

            # Load model
            model_key = f"{symbol}_{model_type}"

            if not os.path.exists(model_path):
                logger.warning(f"Model not found: {model_path}")
                return False

            # Load with custom objects if needed
            custom_objects = {}
            if model_type == 'attention' or model_type == 'multihead' or model_type == 'ensemble':
                # Import custom layers if needed
                pass

            self.models[model_key] = load_model(model_path, custom_objects=custom_objects, compile=False)

            # Load scaler
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers[model_key] = pickle.load(f)
            else:
                logger.warning(f"Scaler not found: {scaler_path}")
                return False

            # Load config
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.configs[model_key] = json.load(f)
            else:
                logger.warning(f"Config not found: {config_path}")
                return False

            logger.info(f"Loaded model for {symbol} ({model_type})")
            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators (same as training)"""
        df = data.copy()

        # Moving Averages
        for window in [5, 10, 20, 50]:
            df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
            df[f'EMA_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()

        # MACD
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']

        # Stochastic
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()

        # ATR
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()

        # OBV
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

        # Momentum and ROC
        for period in [5, 10, 20]:
            df[f'Momentum_{period}'] = df['Close'] - df['Close'].shift(period)
            df[f'ROC_{period}'] = ((df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)) * 100

        # Volume indicators
        df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']

        return df

    def fetch_recent_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """Fetch recent stock data"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def prepare_input(self, data: pd.DataFrame, model_key: str) -> Optional[np.ndarray]:
        """Prepare input data for prediction"""
        try:
            config = self.configs[model_key]
            sequence_length = config['sequence_length']
            features = config['features']
            use_technical_indicators = config.get('use_technical_indicators', False)

            # Calculate technical indicators if needed
            if use_technical_indicators:
                data = self.calculate_technical_indicators(data)

            # Drop NaN
            data = data.dropna()

            # Check if we have enough data
            if len(data) < sequence_length:
                logger.warning(f"Not enough data: {len(data)} < {sequence_length}")
                return None

            # Select features
            df = data[features].copy()

            # Scale data
            scaler = self.scalers[model_key]
            scaled_data = scaler.transform(df)

            # Get last sequence
            X = scaled_data[-sequence_length:]
            X = X.reshape(1, sequence_length, len(features))

            return X

        except Exception as e:
            logger.error(f"Error preparing input: {e}")
            return None

    def predict(
        self,
        symbol: str,
        model_type: str = 'ensemble',
        days_ahead: int = 1,
        with_confidence: bool = True
    ) -> Dict:
        """
        Make prediction for a symbol

        Args:
            symbol: Stock symbol
            model_type: Type of model to use
            days_ahead: Number of days to predict ahead
            with_confidence: Whether to include confidence intervals

        Returns:
            Dictionary with prediction results
        """
        model_key = f"{symbol}_{model_type}"

        # Load model if not loaded
        if model_key not in self.models:
            if not self.load_model(symbol, model_type):
                return {'error': 'Model not available'}

        # Fetch recent data
        data = self.fetch_recent_data(symbol)
        if data is None or len(data) == 0:
            return {'error': 'No data available'}

        # Prepare input
        X = self.prepare_input(data, model_key)
        if X is None:
            return {'error': 'Could not prepare input'}

        # Make prediction
        model = self.models[model_key]
        scaler = self.scalers[model_key]
        config = self.configs[model_key]

        predictions = []

        for _ in range(days_ahead):
            # Predict
            if with_confidence:
                # Monte Carlo Dropout for confidence intervals
                pred_samples = []
                for _ in range(50):
                    pred = model(X, training=True)
                    pred_samples.append(pred.numpy()[0, 0])

                pred_samples = np.array(pred_samples)
                mean_pred = pred_samples.mean()
                std_pred = pred_samples.std()

                # Inverse transform
                dummy = np.zeros((1, len(config['features'])))
                dummy[0, 0] = mean_pred
                actual_pred = scaler.inverse_transform(dummy)[0, 0]

                # Confidence intervals
                dummy_lower = dummy.copy()
                dummy_lower[0, 0] = mean_pred - 1.96 * std_pred
                lower_bound = scaler.inverse_transform(dummy_lower)[0, 0]

                dummy_upper = dummy.copy()
                dummy_upper[0, 0] = mean_pred + 1.96 * std_pred
                upper_bound = scaler.inverse_transform(dummy_upper)[0, 0]

                predictions.append({
                    'prediction': float(actual_pred),
                    'lower_95': float(lower_bound),
                    'upper_95': float(upper_bound),
                    'std': float(std_pred)
                })

            else:
                pred = model.predict(X, verbose=0)[0, 0]

                # Inverse transform
                dummy = np.zeros((1, len(config['features'])))
                dummy[0, 0] = pred
                actual_pred = scaler.inverse_transform(dummy)[0, 0]

                predictions.append({
                    'prediction': float(actual_pred)
                })

            # For multi-day prediction, append prediction to input
            # (simplified - in practice should use actual next day data)
            if days_ahead > 1:
                # This is a simplified approach
                pass

        # Get current price
        current_price = data['Close'].iloc[-1]

        # Calculate change
        predicted_price = predictions[0]['prediction']
        change = predicted_price - current_price
        change_percent = (change / current_price) * 100

        result = {
            'symbol': symbol,
            'model_type': model_type,
            'current_price': float(current_price),
            'predicted_price': predicted_price,
            'change': float(change),
            'change_percent': float(change_percent),
            'predictions': predictions,
            'timestamp': datetime.now().isoformat()
        }

        return result

    def predict_multiple_models(self, symbol: str, days_ahead: int = 1) -> Dict:
        """
        Make predictions using multiple models for comparison

        Returns predictions from all available models
        """
        model_types = ['simple', 'bidirectional', 'attention', 'multihead', 'ensemble']

        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'models': {}
        }

        for model_type in model_types:
            prediction = self.predict(symbol, model_type, days_ahead, with_confidence=True)
            if 'error' not in prediction:
                results['models'][model_type] = prediction

        # Calculate ensemble of ensembles (average of all models)
        if len(results['models']) > 0:
            all_predictions = [m['predicted_price'] for m in results['models'].values()]
            results['consensus_prediction'] = float(np.mean(all_predictions))
            results['prediction_std'] = float(np.std(all_predictions))

        return results

    def backtest(
        self,
        symbol: str,
        model_type: str = 'ensemble',
        test_days: int = 30
    ) -> Dict:
        """
        Backtest model predictions

        Args:
            symbol: Stock symbol
            model_type: Model type to test
            test_days: Number of days to backtest

        Returns:
            Backtest results with metrics
        """
        model_key = f"{symbol}_{model_type}"

        # Load model if needed
        if model_key not in self.models:
            if not self.load_model(symbol, model_type):
                return {'error': 'Model not available'}

        # Fetch historical data
        data = self.fetch_recent_data(symbol, period="6mo")
        if data is None:
            return {'error': 'No data available'}

        config = self.configs[model_key]
        sequence_length = config['sequence_length']

        # Prepare for backtesting
        if config.get('use_technical_indicators', False):
            data = self.calculate_technical_indicators(data)

        data = data.dropna()

        # Get last test_days
        test_data = data.iloc[-test_days:]
        predictions = []
        actuals = []

        model = self.models[model_key]
        scaler = self.scalers[model_key]
        features = config['features']

        for i in range(test_days):
            # Get data up to current day
            current_data = data.iloc[:-(test_days - i)]

            if len(current_data) < sequence_length:
                continue

            # Prepare input
            df = current_data[features].copy()
            scaled_data = scaler.transform(df)
            X = scaled_data[-sequence_length:].reshape(1, sequence_length, len(features))

            # Predict
            pred = model.predict(X, verbose=0)[0, 0]

            # Inverse transform
            dummy = np.zeros((1, len(features)))
            dummy[0, 0] = pred
            actual_pred = scaler.inverse_transform(dummy)[0, 0]

            predictions.append(actual_pred)
            actuals.append(test_data.iloc[i]['Close'])

        # Calculate metrics
        predictions = np.array(predictions)
        actuals = np.array(actuals)

        mse = np.mean((predictions - actuals) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - actuals))
        mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100

        # Directional accuracy
        actual_direction = np.diff(actuals) > 0
        pred_direction = np.diff(predictions) > 0
        directional_accuracy = np.mean(actual_direction == pred_direction) * 100

        results = {
            'symbol': symbol,
            'model_type': model_type,
            'test_days': test_days,
            'metrics': {
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape),
                'directional_accuracy': float(directional_accuracy)
            },
            'predictions': predictions.tolist(),
            'actuals': actuals.tolist(),
            'dates': test_data.index.strftime('%Y-%m-%d').tolist()
        }

        return results


# Example usage
if __name__ == "__main__":
    service = PredictionService()

    # Test prediction
    symbol = "AAPL"

    # Single model prediction
    result = service.predict(symbol, model_type='ensemble', days_ahead=5, with_confidence=True)
    print(json.dumps(result, indent=2))

    # Multiple models comparison
    multi_result = service.predict_multiple_models(symbol, days_ahead=1)
    print("\nMultiple Models Comparison:")
    print(json.dumps(multi_result, indent=2))

    # Backtest
    backtest_result = service.backtest(symbol, model_type='ensemble', test_days=30)
    print("\nBacktest Results:")
    print(json.dumps(backtest_result, indent=2))
