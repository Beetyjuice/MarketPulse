"""
Enhanced LSTM model with Bidirectional layers, Attention mechanism, and advanced features
Supports multi-feature training and confidence interval predictions
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, LSTM, Bidirectional, Dense, Dropout,
    Layer, Attention, Concatenate, BatchNormalization,
    MultiHeadAttention
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
)
import yfinance as yf
import logging
import os
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttentionLayer(Layer):
    """Custom Attention Layer for time series"""

    def __init__(self, units=128, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W = self.add_weight(
            shape=(input_shape[-1], self.units),
            initializer='glorot_uniform',
            trainable=True,
            name='attention_W'
        )
        self.b = self.add_weight(
            shape=(self.units,),
            initializer='zeros',
            trainable=True,
            name='attention_b'
        )
        self.u = self.add_weight(
            shape=(self.units,),
            initializer='glorot_uniform',
            trainable=True,
            name='attention_u'
        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        # Calculate attention scores
        uit = tf.nn.tanh(tf.tensordot(x, self.W, axes=1) + self.b)
        ait = tf.tensordot(uit, self.u, axes=1)
        ait = tf.nn.softmax(ait, axis=1)

        # Apply attention weights
        weighted_input = x * tf.expand_dims(ait, -1)
        output = tf.reduce_sum(weighted_input, axis=1)

        return output

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config


class EnhancedLSTMTrainer:
    """
    Enhanced LSTM model trainer with advanced features:
    - Bidirectional LSTM
    - Attention mechanism
    - Multi-feature input
    - Confidence intervals
    - Advanced callbacks
    """

    def __init__(
        self,
        symbol,
        sequence_length=60,
        features=['Close', 'Open', 'High', 'Low', 'Volume'],
        use_technical_indicators=True,
        model_type='attention'  # 'simple', 'bidirectional', 'attention', 'multihead'
    ):
        self.symbol = symbol
        self.sequence_length = sequence_length
        self.features = features
        self.use_technical_indicators = use_technical_indicators
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.history = None

    def calculate_technical_indicators(self, data):
        """Calculate technical indicators"""
        df = data.copy()

        # Simple Moving Averages
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()

        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

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

        # ATR (Average True Range)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()

        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()

        # Price momentum
        df['Momentum'] = df['Close'] - df['Close'].shift(10)

        # Rate of Change
        df['ROC'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100

        # Drop NaN values
        df = df.dropna()

        return df

    def fetch_data(self, period="2y"):
        """Fetch historical stock data"""
        logger.info(f"Fetching data for {self.symbol}")
        stock = yf.Ticker(self.symbol)
        data = stock.history(period=period)

        if self.use_technical_indicators:
            data = self.calculate_technical_indicators(data)
            # Add technical indicators to features
            self.features.extend([
                'SMA_10', 'SMA_30', 'EMA_12', 'EMA_26', 'MACD', 'MACD_Signal',
                'RSI', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'ATR',
                'Volume_SMA', 'Momentum', 'ROC'
            ])
            # Remove duplicates
            self.features = list(dict.fromkeys(self.features))

        return data

    def prepare_data(self, data, train_split=0.8):
        """Prepare data for LSTM training"""
        # Select features
        df = data[self.features].copy()

        # Scale the data
        scaled_data = self.scaler.fit_transform(df)

        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i, 0])  # Using Close price as target

        X, y = np.array(X), np.array(y)

        # Split into train and test sets
        split_idx = int(train_split * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        logger.info(f"Feature dimension: {X_train.shape[-1]}")

        return X_train, X_test, y_train, y_test

    def build_simple_lstm(self, input_shape):
        """Build simple LSTM model (baseline)"""
        inputs = Input(shape=input_shape)

        x = LSTM(100, return_sequences=True)(inputs)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        x = LSTM(100, return_sequences=True)(x)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        x = LSTM(50)(x)
        x = Dropout(0.2)(x)

        outputs = Dense(1)(x)

        model = Model(inputs=inputs, outputs=outputs)
        return model

    def build_bidirectional_lstm(self, input_shape):
        """Build Bidirectional LSTM model"""
        inputs = Input(shape=input_shape)

        x = Bidirectional(LSTM(128, return_sequences=True))(inputs)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        x = Bidirectional(LSTM(64, return_sequences=True))(x)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        x = Bidirectional(LSTM(32))(x)
        x = Dropout(0.2)(x)

        outputs = Dense(1)(x)

        model = Model(inputs=inputs, outputs=outputs)
        return model

    def build_attention_lstm(self, input_shape):
        """Build LSTM with custom Attention mechanism"""
        inputs = Input(shape=input_shape)

        # First Bidirectional LSTM layer
        x = Bidirectional(LSTM(128, return_sequences=True))(inputs)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        # Second Bidirectional LSTM layer
        x = Bidirectional(LSTM(64, return_sequences=True))(x)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        # Apply custom attention
        attention_output = AttentionLayer(units=128)(x)

        # Dense layers
        x = Dense(64, activation='relu')(attention_output)
        x = Dropout(0.2)(x)

        outputs = Dense(1)(x)

        model = Model(inputs=inputs, outputs=outputs)
        return model

    def build_multihead_attention_lstm(self, input_shape):
        """Build LSTM with Multi-Head Attention"""
        inputs = Input(shape=input_shape)

        # Bidirectional LSTM layers
        x = Bidirectional(LSTM(128, return_sequences=True))(inputs)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        # Multi-Head Attention
        attention_output = MultiHeadAttention(
            num_heads=4,
            key_dim=32,
            dropout=0.2
        )(x, x)

        # Residual connection
        x = Concatenate()([x, attention_output])

        # Another LSTM layer
        x = Bidirectional(LSTM(64, return_sequences=True))(x)
        x = Dropout(0.3)(x)

        # Global pooling
        x = tf.keras.layers.GlobalAveragePooling1D()(x)

        # Dense layers
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)

        outputs = Dense(1)(x)

        model = Model(inputs=inputs, outputs=outputs)
        return model

    def build_model(self, input_shape):
        """Build model based on selected type"""
        logger.info(f"Building {self.model_type} model...")

        if self.model_type == 'simple':
            model = self.build_simple_lstm(input_shape)
        elif self.model_type == 'bidirectional':
            model = self.build_bidirectional_lstm(input_shape)
        elif self.model_type == 'attention':
            model = self.build_attention_lstm(input_shape)
        elif self.model_type == 'multihead':
            model = self.build_multihead_attention_lstm(input_shape)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        # Compile with advanced optimizer
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        model.compile(
            optimizer=optimizer,
            loss='huber',  # More robust to outliers than MSE
            metrics=['mae', 'mse']
        )

        logger.info(f"Model built with {model.count_params():,} parameters")
        return model

    def get_callbacks(self, model_dir):
        """Get training callbacks"""
        callbacks = [
            # Early stopping
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),

            # Reduce learning rate on plateau
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            ),

            # Model checkpoint
            ModelCheckpoint(
                filepath=os.path.join(model_dir, f'best_model_{self.symbol}_{self.model_type}.h5'),
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            ),

            # TensorBoard
            TensorBoard(
                log_dir=os.path.join(model_dir, 'logs', f'{self.symbol}_{self.model_type}_{datetime.now().strftime("%Y%m%d-%H%M%S")}'),
                histogram_freq=1
            )
        ]

        return callbacks

    def train(self, X_train, y_train, epochs=100, batch_size=32, validation_split=0.15):
        """Train the LSTM model"""
        logger.info(f"Training {self.model_type} LSTM model...")

        # Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self.build_model(input_shape)

        # Print model summary
        self.model.summary()

        # Create model directory
        model_dir = "models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        # Get callbacks
        callbacks = self.get_callbacks(model_dir)

        # Train the model
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )

        return self.history

    def predict_with_confidence(self, X, n_iterations=100):
        """
        Predict with confidence intervals using Monte Carlo Dropout
        """
        # Enable dropout during prediction
        predictions = []

        for _ in range(n_iterations):
            # Make predictions with dropout enabled
            pred = self.model(X, training=True)
            predictions.append(pred.numpy())

        predictions = np.array(predictions)

        # Calculate mean and confidence intervals
        mean_prediction = predictions.mean(axis=0)
        std_prediction = predictions.std(axis=0)

        # 95% confidence interval
        lower_bound = mean_prediction - 1.96 * std_prediction
        upper_bound = mean_prediction + 1.96 * std_prediction

        return {
            'mean': mean_prediction.flatten(),
            'std': std_prediction.flatten(),
            'lower_95': lower_bound.flatten(),
            'upper_95': upper_bound.flatten()
        }

    def evaluate(self, X_test, y_test):
        """Evaluate the model with comprehensive metrics"""
        # Standard prediction
        predictions = self.model.predict(X_test)

        # Get confidence intervals
        conf_predictions = self.predict_with_confidence(X_test, n_iterations=50)

        # Inverse transform predictions and actual values
        # Create dummy array for inverse transform
        dummy_cols = np.zeros((predictions.shape[0], len(self.features) - 1))
        pred_full = np.concatenate([predictions, dummy_cols], axis=1)
        y_test_full = np.concatenate([y_test.reshape(-1, 1), dummy_cols], axis=1)

        pred_actual = self.scaler.inverse_transform(pred_full)[:, 0]
        y_test_actual = self.scaler.inverse_transform(y_test_full)[:, 0]

        # Calculate metrics
        mse = mean_squared_error(y_test_actual, pred_actual)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_actual, pred_actual)
        r2 = r2_score(y_test_actual, pred_actual)

        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_test_actual - pred_actual) / y_test_actual)) * 100

        # Directional Accuracy (up/down prediction)
        y_diff = np.diff(y_test_actual)
        pred_diff = np.diff(pred_actual)
        directional_accuracy = np.mean((y_diff * pred_diff) > 0) * 100

        metrics = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'mape': float(mape),
            'directional_accuracy': float(directional_accuracy)
        }

        logger.info(f"\n{'='*60}")
        logger.info(f"Model Evaluation Metrics for {self.symbol} ({self.model_type})")
        logger.info(f"{'='*60}")
        logger.info(f"MSE:                    {mse:.4f}")
        logger.info(f"RMSE:                   {rmse:.4f}")
        logger.info(f"MAE:                    {mae:.4f}")
        logger.info(f"R² Score:               {r2:.4f}")
        logger.info(f"MAPE:                   {mape:.2f}%")
        logger.info(f"Directional Accuracy:   {directional_accuracy:.2f}%")
        logger.info(f"{'='*60}\n")

        return metrics, conf_predictions

    def save_model(self, filepath=None):
        """Save the trained model and scaler"""
        if filepath is None:
            filepath = f"models/{self.model_type}_model_{self.symbol}.h5"

        self.model.save(filepath)

        # Save scaler
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        # Save configuration
        config = {
            'symbol': self.symbol,
            'sequence_length': self.sequence_length,
            'features': self.features,
            'model_type': self.model_type,
            'use_technical_indicators': self.use_technical_indicators
        }
        config_path = filepath.replace('.h5', '_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        logger.info(f"Model saved to {filepath}")
        logger.info(f"Scaler saved to {scaler_path}")
        logger.info(f"Config saved to {config_path}")

    def run(self, epochs=100, batch_size=32):
        """Run the complete training pipeline"""
        # Fetch data
        data = self.fetch_data()

        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(data)

        # Train model
        history = self.train(X_train, y_train, epochs=epochs, batch_size=batch_size)

        # Evaluate model
        metrics, conf_predictions = self.evaluate(X_test, y_test)

        # Save model
        self.save_model()

        # Save metrics
        metrics_path = f"models/{self.model_type}_metrics_{self.symbol}.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=4)

        return history, metrics


if __name__ == "__main__":
    # Example usage - train multiple model types for comparison
    symbols = ["AAPL", "GOOGL"]
    model_types = ['simple', 'bidirectional', 'attention', 'multihead']

    results = {}

    for symbol in symbols:
        results[symbol] = {}

        for model_type in model_types:
            logger.info(f"\n{'#'*80}")
            logger.info(f"Training {model_type.upper()} model for {symbol}")
            logger.info(f"{'#'*80}\n")

            trainer = EnhancedLSTMTrainer(
                symbol=symbol,
                sequence_length=60,
                use_technical_indicators=True,
                model_type=model_type
            )

            history, metrics = trainer.run(epochs=50, batch_size=32)
            results[symbol][model_type] = metrics

    # Save comparison results
    with open('models/model_comparison.json', 'w') as f:
        json.dump(results, f, indent=4)

    logger.info("\n" + "="*80)
    logger.info("Training completed for all models!")
    logger.info("="*80)
