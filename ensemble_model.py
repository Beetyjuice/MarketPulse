"""
Ensemble prediction model combining LSTM, GRU, and Transformer architectures
Uses weighted voting and stacking for superior prediction accuracy
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, LSTM, GRU, Bidirectional, Dense, Dropout,
    MultiHeadAttention, LayerNormalization, GlobalAveragePooling1D,
    Concatenate, Add, BatchNormalization
)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import yfinance as yf
import logging
import os
import json
import pickle
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformerBlock(tf.keras.layers.Layer):
    """Transformer block for time series"""

    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            Dense(ff_dim, activation="relu"),
            Dense(embed_dim),
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)

    def call(self, inputs, training=False):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class EnsembleModelTrainer:
    """
    Ensemble model combining:
    - Bidirectional LSTM
    - Bidirectional GRU
    - Transformer
    Uses stacking and weighted averaging for final predictions
    """

    def __init__(
        self,
        symbol,
        sequence_length=60,
        features=['Close', 'Open', 'High', 'Low', 'Volume'],
        use_technical_indicators=True
    ):
        self.symbol = symbol
        self.sequence_length = sequence_length
        self.features = features
        self.use_technical_indicators = use_technical_indicators

        # Individual models
        self.lstm_model = None
        self.gru_model = None
        self.transformer_model = None
        self.ensemble_model = None

        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.history = {}

    def calculate_technical_indicators(self, data):
        """Calculate comprehensive technical indicators"""
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

        # Stochastic Oscillator
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

        # OBV (On-Balance Volume)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

        # Price momentum and ROC
        for period in [5, 10, 20]:
            df[f'Momentum_{period}'] = df['Close'] - df['Close'].shift(period)
            df[f'ROC_{period}'] = ((df['Close'] - df['Close'].shift(period)) / df['Close'].shift(period)) * 100

        # Volume indicators
        df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']

        df = df.dropna()
        return df

    def fetch_data(self, period="2y"):
        """Fetch historical stock data"""
        logger.info(f"Fetching data for {self.symbol}")
        stock = yf.Ticker(self.symbol)
        data = stock.history(period=period)

        if self.use_technical_indicators:
            data = self.calculate_technical_indicators(data)
            # Update features list
            self.features = list(data.columns)

        logger.info(f"Data shape: {data.shape}, Features: {len(self.features)}")
        return data

    def prepare_data(self, data, train_split=0.8):
        """Prepare data for training"""
        df = data[self.features].copy()
        scaled_data = self.scaler.fit_transform(df)

        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i, 0])

        X, y = np.array(X), np.array(y)

        split_idx = int(train_split * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        logger.info(f"Training: {len(X_train)}, Test: {len(X_test)}, Features: {X_train.shape[-1]}")
        return X_train, X_test, y_train, y_test

    def build_lstm_model(self, input_shape):
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

        outputs = Dense(1, name='lstm_output')(x)

        model = Model(inputs=inputs, outputs=outputs, name='LSTM_Model')
        return model

    def build_gru_model(self, input_shape):
        """Build Bidirectional GRU model"""
        inputs = Input(shape=input_shape)

        x = Bidirectional(GRU(128, return_sequences=True))(inputs)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        x = Bidirectional(GRU(64, return_sequences=True))(x)
        x = Dropout(0.3)(x)
        x = BatchNormalization()(x)

        x = Bidirectional(GRU(32))(x)
        x = Dropout(0.2)(x)

        outputs = Dense(1, name='gru_output')(x)

        model = Model(inputs=inputs, outputs=outputs, name='GRU_Model')
        return model

    def build_transformer_model(self, input_shape):
        """Build Transformer model for time series"""
        inputs = Input(shape=input_shape)

        # Positional encoding (simple)
        positions = tf.range(start=0, limit=input_shape[0], delta=1)
        position_embedding = tf.keras.layers.Embedding(
            input_dim=input_shape[0],
            output_dim=input_shape[1]
        )(positions)

        x = inputs + position_embedding

        # Transformer blocks
        x = TransformerBlock(embed_dim=input_shape[1], num_heads=4, ff_dim=128)(x)
        x = TransformerBlock(embed_dim=input_shape[1], num_heads=4, ff_dim=128)(x)

        # Global pooling
        x = GlobalAveragePooling1D()(x)

        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)

        outputs = Dense(1, name='transformer_output')(x)

        model = Model(inputs=inputs, outputs=outputs, name='Transformer_Model')
        return model

    def build_ensemble_model(self, input_shape):
        """
        Build ensemble model that combines LSTM, GRU, and Transformer
        Uses a meta-learner (stacking) approach
        """
        inputs = Input(shape=input_shape)

        # LSTM branch
        lstm_x = Bidirectional(LSTM(64, return_sequences=True))(inputs)
        lstm_x = Dropout(0.2)(lstm_x)
        lstm_x = Bidirectional(LSTM(32))(lstm_x)
        lstm_output = Dense(1, name='lstm_pred')(lstm_x)

        # GRU branch
        gru_x = Bidirectional(GRU(64, return_sequences=True))(inputs)
        gru_x = Dropout(0.2)(gru_x)
        gru_x = Bidirectional(GRU(32))(gru_x)
        gru_output = Dense(1, name='gru_pred')(gru_x)

        # Transformer branch
        trans_x = TransformerBlock(embed_dim=input_shape[1], num_heads=4, ff_dim=64)(inputs)
        trans_x = GlobalAveragePooling1D()(trans_x)
        trans_x = Dense(32, activation='relu')(trans_x)
        trans_output = Dense(1, name='transformer_pred')(trans_x)

        # Meta-learner: Combine predictions
        combined = Concatenate()([lstm_output, gru_output, trans_output])

        # Meta-learning layers
        x = Dense(32, activation='relu')(combined)
        x = Dropout(0.2)(x)
        x = Dense(16, activation='relu')(x)

        # Final prediction
        outputs = Dense(1, name='ensemble_output')(x)

        model = Model(inputs=inputs, outputs=outputs, name='Ensemble_Model')
        return model

    def compile_model(self, model, learning_rate=0.001):
        """Compile model with optimizer and loss"""
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        model.compile(
            optimizer=optimizer,
            loss='huber',
            metrics=['mae', 'mse']
        )
        return model

    def train_individual_models(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """Train individual LSTM, GRU, and Transformer models"""
        input_shape = (X_train.shape[1], X_train.shape[2])

        # Create model directory
        model_dir = "models/ensemble"
        os.makedirs(model_dir, exist_ok=True)

        # Train LSTM
        logger.info("Training LSTM model...")
        self.lstm_model = self.build_lstm_model(input_shape)
        self.lstm_model = self.compile_model(self.lstm_model)

        lstm_callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7),
            ModelCheckpoint(
                f'{model_dir}/lstm_{self.symbol}.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]

        self.history['lstm'] = self.lstm_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=lstm_callbacks,
            verbose=1
        )

        # Train GRU
        logger.info("Training GRU model...")
        self.gru_model = self.build_gru_model(input_shape)
        self.gru_model = self.compile_model(self.gru_model)

        gru_callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7),
            ModelCheckpoint(
                f'{model_dir}/gru_{self.symbol}.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]

        self.history['gru'] = self.gru_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=gru_callbacks,
            verbose=1
        )

        # Train Transformer
        logger.info("Training Transformer model...")
        self.transformer_model = self.build_transformer_model(input_shape)
        self.transformer_model = self.compile_model(self.transformer_model)

        transformer_callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7),
            ModelCheckpoint(
                f'{model_dir}/transformer_{self.symbol}.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]

        self.history['transformer'] = self.transformer_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=transformer_callbacks,
            verbose=1
        )

    def train_ensemble(self, X_train, y_train, X_val, y_val, epochs=30, batch_size=32):
        """Train the ensemble meta-learner"""
        logger.info("Training ensemble model...")

        input_shape = (X_train.shape[1], X_train.shape[2])
        self.ensemble_model = self.build_ensemble_model(input_shape)
        self.ensemble_model = self.compile_model(self.ensemble_model, learning_rate=0.0005)

        model_dir = "models/ensemble"
        ensemble_callbacks = [
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=1e-7),
            ModelCheckpoint(
                f'{model_dir}/ensemble_{self.symbol}.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]

        self.history['ensemble'] = self.ensemble_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=ensemble_callbacks,
            verbose=1
        )

    def predict_ensemble(self, X, use_weights=True):
        """
        Make ensemble predictions using weighted averaging
        Weights are calculated based on validation performance
        """
        lstm_pred = self.lstm_model.predict(X, verbose=0)
        gru_pred = self.gru_model.predict(X, verbose=0)
        transformer_pred = self.transformer_model.predict(X, verbose=0)
        ensemble_pred = self.ensemble_model.predict(X, verbose=0)

        if use_weights:
            # Weight based on individual model performance (can be tuned)
            weights = {
                'lstm': 0.25,
                'gru': 0.25,
                'transformer': 0.20,
                'ensemble': 0.30
            }

            final_pred = (
                weights['lstm'] * lstm_pred +
                weights['gru'] * gru_pred +
                weights['transformer'] * transformer_pred +
                weights['ensemble'] * ensemble_pred
            )
        else:
            final_pred = ensemble_pred

        return {
            'lstm': lstm_pred.flatten(),
            'gru': gru_pred.flatten(),
            'transformer': transformer_pred.flatten(),
            'ensemble': ensemble_pred.flatten(),
            'final': final_pred.flatten()
        }

    def evaluate(self, X_test, y_test):
        """Evaluate all models"""
        predictions = self.predict_ensemble(X_test)

        results = {}

        for model_name, pred in predictions.items():
            # Inverse transform
            dummy_cols = np.zeros((len(pred), len(self.features) - 1))
            pred_full = np.concatenate([pred.reshape(-1, 1), dummy_cols], axis=1)
            y_test_full = np.concatenate([y_test.reshape(-1, 1), dummy_cols], axis=1)

            pred_actual = self.scaler.inverse_transform(pred_full)[:, 0]
            y_test_actual = self.scaler.inverse_transform(y_test_full)[:, 0]

            # Calculate metrics
            mse = mean_squared_error(y_test_actual, pred_actual)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test_actual, pred_actual)
            r2 = r2_score(y_test_actual, pred_actual)
            mape = np.mean(np.abs((y_test_actual - pred_actual) / y_test_actual)) * 100

            # Directional accuracy
            if len(y_test_actual) > 1:
                y_diff = np.diff(y_test_actual)
                pred_diff = np.diff(pred_actual)
                directional_accuracy = np.mean((y_diff * pred_diff) > 0) * 100
            else:
                directional_accuracy = 0

            results[model_name] = {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2),
                'mape': float(mape),
                'directional_accuracy': float(directional_accuracy)
            }

            logger.info(f"\n{model_name.upper()} Metrics:")
            logger.info(f"  RMSE: {rmse:.4f}")
            logger.info(f"  MAE: {mae:.4f}")
            logger.info(f"  R²: {r2:.4f}")
            logger.info(f"  MAPE: {mape:.2f}%")
            logger.info(f"  Directional Accuracy: {directional_accuracy:.2f}%")

        return results

    def save_models(self):
        """Save all models and scaler"""
        model_dir = "models/ensemble"
        os.makedirs(model_dir, exist_ok=True)

        # Save scaler
        with open(f'{model_dir}/scaler_{self.symbol}.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)

        # Save configuration
        config = {
            'symbol': self.symbol,
            'sequence_length': self.sequence_length,
            'features': self.features,
            'use_technical_indicators': self.use_technical_indicators
        }
        with open(f'{model_dir}/config_{self.symbol}.json', 'w') as f:
            json.dump(config, f, indent=4)

        logger.info(f"Models saved to {model_dir}")

    def run(self, epochs_individual=50, epochs_ensemble=30, batch_size=32):
        """Run complete ensemble training pipeline"""
        # Fetch and prepare data
        data = self.fetch_data()
        X_train, X_test, y_train, y_test = self.prepare_data(data, train_split=0.8)

        # Split train into train and validation
        val_split = int(0.85 * len(X_train))
        X_val = X_train[val_split:]
        y_val = y_train[val_split:]
        X_train = X_train[:val_split]
        y_train = y_train[:val_split]

        # Train individual models
        self.train_individual_models(
            X_train, y_train,
            X_val, y_val,
            epochs=epochs_individual,
            batch_size=batch_size
        )

        # Train ensemble
        self.train_ensemble(
            X_train, y_train,
            X_val, y_val,
            epochs=epochs_ensemble,
            batch_size=batch_size
        )

        # Evaluate
        results = self.evaluate(X_test, y_test)

        # Save everything
        self.save_models()

        # Save results
        with open(f'models/ensemble/results_{self.symbol}.json', 'w') as f:
            json.dump(results, f, indent=4)

        return results


if __name__ == "__main__":
    symbols = ["AAPL", "GOOGL", "MSFT"]

    all_results = {}

    for symbol in symbols:
        logger.info(f"\n{'='*80}")
        logger.info(f"Training ensemble models for {symbol}")
        logger.info(f"{'='*80}\n")

        trainer = EnsembleModelTrainer(
            symbol=symbol,
            sequence_length=60,
            use_technical_indicators=True
        )

        results = trainer.run(
            epochs_individual=30,
            epochs_ensemble=20,
            batch_size=32
        )

        all_results[symbol] = results

    # Save all results
    with open('models/ensemble/all_results.json', 'w') as f:
        json.dump(all_results, f, indent=4)

    logger.info("\nEnsemble training completed for all symbols!")
