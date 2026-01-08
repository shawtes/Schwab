"""
LSTM Model for Time Series Prediction
Part of Multi-Timeframe ML System
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("⚠️ TensorFlow/Keras not available. Install: pip install tensorflow")


class LSTMPredictor:
    """
    LSTM model for time series price prediction
    """
    
    def __init__(self, lookback=60, units=50, dropout=0.2, random_state=42):
        """
        Initialize LSTM model
        
        Args:
            lookback: Number of time steps to look back
            units: Number of LSTM units
            dropout: Dropout rate for regularization
            random_state: Random seed
        """
        self.lookback = lookback
        self.units = units
        self.dropout = dropout
        self.random_state = random_state
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_fitted = False
        
        if not KERAS_AVAILABLE:
            raise ImportError("TensorFlow/Keras required for LSTM. Install: pip install tensorflow")
        
        # Set random seeds
        np.random.seed(random_state)
        keras.utils.set_random_seed(random_state)
    
    def create_sequences(self, data, target=None):
        """
        Create sequences for LSTM
        
        Args:
            data: Feature data (n_samples, n_features)
            target: Target data (n_samples,)
        
        Returns:
            X_seq, y_seq: Sequences for training
        """
        X_seq, y_seq = [], []
        
        for i in range(self.lookback, len(data)):
            X_seq.append(data[i-self.lookback:i])
            if target is not None:
                y_seq.append(target[i])
        
        return np.array(X_seq), np.array(y_seq) if target is not None else None
    
    def build_model(self, n_features):
        """
        Build LSTM architecture
        
        Args:
            n_features: Number of input features
        """
        model = Sequential([
            # First LSTM layer
            LSTM(units=self.units, return_sequences=True, 
                 input_shape=(self.lookback, n_features)),
            Dropout(self.dropout),
            BatchNormalization(),
            
            # Second LSTM layer
            LSTM(units=self.units // 2, return_sequences=False),
            Dropout(self.dropout),
            BatchNormalization(),
            
            # Dense layers
            Dense(units=25, activation='relu'),
            Dropout(self.dropout),
            
            # Output layer
            Dense(units=1)
        ])
        
        # Compile
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def fit(self, X, y, validation_split=0.2, epochs=50, batch_size=32, verbose=0):
        """
        Train LSTM model
        
        Args:
            X: Feature data
            y: Target data (next period returns)
            validation_split: Validation set size
            epochs: Training epochs
            batch_size: Batch size
            verbose: Verbosity
        """
        # Scale data
        X_scaled = self.scaler.fit_transform(X)
        
        # Create sequences
        X_seq, y_seq = self.create_sequences(X_scaled, y)
        
        if len(X_seq) == 0:
            raise ValueError(f"Not enough data for lookback={self.lookback}")
        
        # Build model
        self.model = self.build_model(X.shape[1])
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=verbose
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=verbose
            )
        ]
        
        # Train
        history = self.model.fit(
            X_seq, y_seq,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        self.is_fitted = True
        
        return history
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X: Feature data
        
        Returns:
            predictions: Predicted returns
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Scale data
        X_scaled = self.scaler.transform(X)
        
        # Create sequences
        X_seq, _ = self.create_sequences(X_scaled)
        
        if len(X_seq) == 0:
            raise ValueError(f"Not enough data for lookback={self.lookback}")
        
        # Predict
        predictions = self.model.predict(X_seq, verbose=0).flatten()
        
        # Pad beginning with NaN to match original length
        padded_predictions = np.full(len(X), np.nan)
        padded_predictions[self.lookback:] = predictions
        
        return padded_predictions
    
    def evaluate(self, X, y):
        """
        Evaluate model performance
        
        Args:
            X: Feature data
            y: True target values
        
        Returns:
            metrics: Dict with R², RMSE, MAE
        """
        predictions = self.predict(X)
        
        # Remove NaN values
        valid_mask = ~np.isnan(predictions)
        predictions_valid = predictions[valid_mask]
        y_valid = y[valid_mask]
        
        if len(predictions_valid) == 0:
            return {'r2': np.nan, 'rmse': np.nan, 'mae': np.nan}
        
        r2 = r2_score(y_valid, predictions_valid)
        rmse = np.sqrt(mean_squared_error(y_valid, predictions_valid))
        mae = np.mean(np.abs(y_valid - predictions_valid))
        
        return {
            'r2': r2,
            'rmse': rmse,
            'mae': mae
        }


def test_lstm_quick():
    """
    Quick test of LSTM model
    """
    print("Testing LSTM Model...")
    print("=" * 80)
    
    if not KERAS_AVAILABLE:
        print("❌ TensorFlow/Keras not installed")
        print("\nInstall it:")
        print("   pip install tensorflow")
        return
    
    # Create synthetic data
    np.random.seed(42)
    n_samples = 500
    n_features = 10
    
    X = np.random.randn(n_samples, n_features)
    y = np.random.randn(n_samples) * 0.02  # Returns
    
    # Train/test split
    split = int(n_samples * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Initialize and train
    print("\n1. Training LSTM model...")
    lstm = LSTMPredictor(lookback=30, units=50, dropout=0.2)
    
    try:
        history = lstm.fit(X_train, y_train, epochs=20, verbose=1)
        print("   ✓ Model trained")
    except Exception as e:
        print(f"   ✗ Training failed: {e}")
        return
    
    # Evaluate
    print("\n2. Evaluating...")
    metrics = lstm.evaluate(X_test, y_test)
    
    print(f"\n   Results:")
    print(f"      R²: {metrics['r2']:.4f}")
    print(f"      RMSE: {metrics['rmse']:.6f}")
    print(f"      MAE: {metrics['mae']:.6f}")
    
    # Predict
    print("\n3. Making predictions...")
    predictions = lstm.predict(X_test)
    valid_predictions = predictions[~np.isnan(predictions)]
    print(f"   ✓ Generated {len(valid_predictions)} predictions")
    
    print("\n" + "=" * 80)
    print("✅ LSTM Model Test Complete!")
    print("=" * 80)


if __name__ == '__main__':
    test_lstm_quick()

