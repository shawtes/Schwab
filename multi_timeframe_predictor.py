"""
Multi-Timeframe Trading Predictor
For high-frequency trading with predictions across multiple timeframes
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ensemble_trading_model import EnsembleTradingModel, SchwabDataFetcher
import schwabdev

# Load environment variables
load_dotenv()


class MultiTimeframePredictor:
    """
    Predictor for multiple timeframes (high-frequency trading)
    """
    
    def __init__(self, client, base_model_params=None):
        """
        Initialize multi-timeframe predictor
        
        Args:
            client: Schwab API client
            base_model_params: Dictionary of parameters for base model
        """
        self.client = client
        self.fetcher = SchwabDataFetcher(client)
        
        # Default model parameters
        if base_model_params is None:
            base_model_params = {
                'task': 'classification',
                'random_state': 42,
                'use_class_weight': True,
                'use_smote': False  # Disable SMOTE for smaller intraday datasets
            }
        self.base_model_params = base_model_params
        
        # Store models for each timeframe
        self.timeframe_models = {}
        self.timeframe_configs = {
            '1min': {
                'periodType': 'day',
                'period': 1,
                'frequencyType': 'minute',
                'frequency': 1,
                'forward_periods': 1,  # Predict 1 minute ahead
                'threshold': 0.001  # 0.1% threshold for 1-minute
            },
            '5min': {
                'periodType': 'day',
                'period': 1,
                'frequencyType': 'minute',
                'frequency': 5,
                'forward_periods': 1,  # Predict 5 minutes ahead
                'threshold': 0.002  # 0.2% threshold for 5-minute
            },
            '15min': {
                'periodType': 'day',
                'period': 1,
                'frequencyType': 'minute',
                'frequency': 15,
                'forward_periods': 1,  # Predict 15 minutes ahead
                'threshold': 0.003  # 0.3% threshold for 15-minute
            },
            '30min': {
                'periodType': 'day',
                'period': 5,
                'frequencyType': 'minute',
                'frequency': 30,
                'forward_periods': 1,  # Predict 30 minutes ahead
                'threshold': 0.005  # 0.5% threshold for 30-minute
            },
            '1hour': {
                'periodType': 'day',
                'period': 10,
                'frequencyType': 'minute',
                'frequency': 30,  # Use 30min as proxy (60min not directly supported)
                'forward_periods': 2,  # Predict 2 periods ahead (1 hour)
                'threshold': 0.01  # 1% threshold for 1-hour
            },
            '1day': {
                'periodType': 'year',
                'period': 1,
                'frequencyType': 'daily',
                'frequency': 1,
                'forward_periods': 1,  # Predict 1 day ahead
                'threshold': 0.015  # 1.5% threshold for daily
            }
        }
    
    def train_timeframe(self, symbol, timeframe, min_samples=100):
        """
        Train a model for a specific timeframe
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe string ('1min', '5min', '15min', etc.)
            min_samples: Minimum number of samples required
        
        Returns:
            Trained model or None if insufficient data
        """
        if timeframe not in self.timeframe_configs:
            print(f"Unknown timeframe: {timeframe}")
            return None
        
        config = self.timeframe_configs[timeframe]
        print(f"\n{'='*60}")
        print(f"Training model for {timeframe} timeframe")
        print(f"{'='*60}")
        
        # Fetch data
        print(f"Fetching {timeframe} data for {symbol}...")
        df = self.fetcher.get_price_history(
            symbol,
            periodType=config['periodType'],
            period=config['period'],
            frequencyType=config['frequencyType'],
            frequency=config['frequency']
        )
        
        if df is None or len(df) < min_samples:
            print(f"Insufficient data: {len(df) if df is not None else 0} samples (need {min_samples})")
            return None
        
        print(f"  Fetched {len(df)} bars")
        
        # Create features
        print("Creating features...")
        features_df = self.fetcher.create_features(df)
        
        if features_df is None or len(features_df) < min_samples // 2:
            print(f"Insufficient data after feature engineering: {len(features_df) if features_df is not None else 0} samples")
            return None
        
        print(f"  Created {len(features_df.columns)} features")
        
        # Create and train model
        model = EnsembleTradingModel(**self.base_model_params)
        
        # Prepare target
        print(f"Preparing target (threshold: {config['threshold']:.1%}, forward: {config['forward_periods']} periods)...")
        target, valid_mask = model.prepare_target(
            features_df,
            forward_periods=config['forward_periods'],
            threshold=config['threshold']
        )
        
        features_df_valid = features_df[valid_mask]
        X = model.prepare_features(features_df_valid)
        y = target.values
        
        if len(X) < min_samples // 2:
            print(f"Insufficient samples after target preparation: {len(X)}")
            return None
        
        # Split data (80/20)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        print(f"  Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        print(f"  Positive class ratio: {y_train.mean():.2%}")
        
        # Train model
        print("Training model...")
        model.fit(X_train, y_train, use_ensemble='voting')
        
        # Quick evaluation
        print("Evaluating...")
        results = model.evaluate(X_test, y_test, threshold=0.5, show_pr_curve=False)
        
        # Store model and config
        self.timeframe_models[timeframe] = {
            'model': model,
            'config': config,
            'symbol': symbol,
            'results': results
        }
        
        print(f"✓ Model trained for {timeframe}")
        return model
    
    def train_all_timeframes(self, symbol, timeframes=None):
        """
        Train models for multiple timeframes
        
        Args:
            symbol: Stock symbol
            timeframes: List of timeframes to train (None = all)
        
        Returns:
            Dictionary of trained models
        """
        if timeframes is None:
            timeframes = list(self.timeframe_configs.keys())
        
        trained = {}
        for tf in timeframes:
            model = self.train_timeframe(symbol, tf)
            if model is not None:
                trained[tf] = model
        
        return trained
    
    def predict_timeframe(self, symbol, timeframe, current_data=None):
        """
        Make prediction for a specific timeframe
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe string
            current_data: Optional DataFrame with current data (if None, fetches latest)
        
        Returns:
            Dictionary with prediction results
        """
        if timeframe not in self.timeframe_models:
            return {'error': f'Model not trained for {timeframe}'}
        
        model_info = self.timeframe_models[timeframe]
        model = model_info['model']
        config = model_info['config']
        
        # Get current data if not provided
        if current_data is None:
            df = self.fetcher.get_price_history(
                symbol,
                periodType=config['periodType'],
                period=config['period'],
                frequencyType=config['frequencyType'],
                frequency=config['frequency']
            )
            if df is None or len(df) < 10:
                return {'error': 'Insufficient current data'}
        else:
            df = current_data.copy()
        
        # Create features for latest data point
        features_df = self.fetcher.create_features(df)
        if features_df is None or len(features_df) == 0:
            return {'error': 'Could not create features'}
        
        # Get the latest row (most recent data point)
        X = model.prepare_features(features_df.tail(1))
        
        # Make prediction
        probability = model.predict(X)[0]
        prediction = 1 if probability > 0.5 else 0
        
        return {
            'timeframe': timeframe,
            'symbol': symbol,
            'probability': float(probability),
            'prediction': int(prediction),
            'threshold': config['threshold'],
            'forward_periods': config['forward_periods'],
            'current_price': float(df['close'].iloc[-1]),
            'timestamp': df.index[-1] if isinstance(df.index, pd.DatetimeIndex) else None
        }
    
    def predict_all_timeframes(self, symbol):
        """
        Make predictions for all trained timeframes
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary of predictions by timeframe
        """
        predictions = {}
        for timeframe in self.timeframe_models.keys():
            pred = self.predict_timeframe(symbol, timeframe)
            if 'error' not in pred:
                predictions[timeframe] = pred
            else:
                predictions[timeframe] = pred
        
        return predictions
    
    def get_prediction_summary(self, symbol):
        """
        Get a summary of predictions across all timeframes
        
        Args:
            symbol: Stock symbol
        
        Returns:
            DataFrame with prediction summary
        """
        predictions = self.predict_all_timeframes(symbol)
        
        results = []
        for tf, pred in predictions.items():
            if 'error' not in pred:
                results.append({
                    'timeframe': tf,
                    'probability': pred['probability'],
                    'prediction': 'UP' if pred['prediction'] == 1 else 'DOWN',
                    'threshold': pred['threshold'],
                    'forward_periods': pred['forward_periods'],
                    'current_price': pred['current_price']
                })
        
        if results:
            return pd.DataFrame(results)
        return None


def main():
    """Example usage for multi-timeframe predictions"""
    print("Multi-Timeframe Trading Predictor")
    print("=" * 60)
    
    # Load credentials
    app_key = os.getenv('app_key')
    app_secret = os.getenv('app_secret')
    
    if not app_key or not app_secret:
        print("ERROR: Missing credentials in .env file")
        return
    
    # Initialize client
    print("\n1. Initializing Schwab API client...")
    client = schwabdev.Client(
        app_key,
        app_secret,
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    
    # Initialize predictor
    print("2. Initializing multi-timeframe predictor...")
    predictor = MultiTimeframePredictor(client)
    
    # Symbol to analyze
    symbol = 'AAPL'
    
    # Train models for different timeframes
    # Start with longer timeframes (more data available)
    print(f"\n3. Training models for {symbol}...")
    print("Note: Starting with daily timeframe (most data available)")
    print("      For intraday timeframes, you need market to be open or recent data")
    
    timeframes_to_train = ['1day']  # Start with daily
    # Add intraday timeframes if you have recent data
    # timeframes_to_train = ['1day', '1hour', '30min', '15min', '5min']
    
    trained = predictor.train_all_timeframes(symbol, timeframes_to_train)
    
    if not trained:
        print("No models were trained successfully")
        return
    
    # Make predictions
    print(f"\n4. Making predictions for {symbol}...")
    print("-" * 60)
    
    summary = predictor.get_prediction_summary(symbol)
    if summary is not None:
        print(summary.to_string(index=False))
    else:
        print("Could not generate predictions")
    
    print("\n" + "=" * 60)
    print("Multi-timeframe prediction complete!")
    print("=" * 60)
    print("\nTo use intraday timeframes, make sure:")
    print("  1. Market is open (for real-time data)")
    print("  2. Or use recent historical data")
    print("  3. Adjust timeframe_configs thresholds for your strategy")


if __name__ == '__main__':
    main()

