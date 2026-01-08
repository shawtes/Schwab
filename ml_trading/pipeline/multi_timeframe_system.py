"""
Multi-Timeframe Prediction System with Classifier
STAGE 2 + STAGE 5 Integration

Combines predictions from multiple timeframes and generates
BUY/SELL/HOLD signals with confidence scores.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel

try:
    from ml_trading.models.lstm_model import LSTMPredictor, KERAS_AVAILABLE
except:
    KERAS_AVAILABLE = False
    print("⚠️ LSTM not available")


class MultiTimeframePredictor:
    """
    Predict on multiple timeframes and combine results
    """
    
    def __init__(self, timeframes=None, use_lstm=False):
        """
        Initialize multi-timeframe predictor
        
        Args:
            timeframes: List of timeframes to predict on
            use_lstm: Whether to use LSTM (requires TensorFlow)
        """
        if timeframes is None:
            timeframes = ['1m', '5m', '30m', '1d']  # Default timeframes
        
        self.timeframes = timeframes
        self.use_lstm = use_lstm and KERAS_AVAILABLE
        self.models = {}  # {timeframe: model}
        self.predictions = {}  # {timeframe: predictions}
        
    def fetch_timeframe_data(self, fetcher, symbol, timeframe):
        """
        Fetch data for specific timeframe
        
        Args:
            fetcher: SchwabDataFetcher instance
            symbol: Stock symbol
            timeframe: Timeframe string ('1m', '5m', '30m', '1d')
        
        Returns:
            df: OHLCV dataframe
        """
        # Map timeframe to Schwab API parameters
        timeframe_config = {
            '1m': {'periodType': 'day', 'period': 10, 'frequencyType': 'minute', 'frequency': 1},
            '5m': {'periodType': 'day', 'period': 10, 'frequencyType': 'minute', 'frequency': 5},
            '30m': {'periodType': 'day', 'period': 10, 'frequencyType': 'minute', 'frequency': 30},
            '1h': {'periodType': 'month', 'period': 1, 'frequencyType': 'minute', 'frequency': 60},
            '1d': {'periodType': 'year', 'period': 10, 'frequencyType': 'daily', 'frequency': 1}
        }
        
        if timeframe not in timeframe_config:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        
        config = timeframe_config[timeframe]
        
        df = fetcher.get_price_history(
            symbol,
            periodType=config['periodType'],
            period=config['period'],
            frequencyType=config['frequencyType'],
            frequency=config['frequency']
        )
        
        return df
    
    def predict_timeframe(self, fetcher, symbol, timeframe):
        """
        Generate prediction for specific timeframe
        
        Args:
            fetcher: SchwabDataFetcher instance
            symbol: Stock symbol
            timeframe: Timeframe string
        
        Returns:
            prediction: Dict with prediction results
        """
        print(f"\n   Predicting {timeframe}...")
        
        # Fetch data
        df = self.fetch_timeframe_data(fetcher, symbol, timeframe)
        
        if df is None or len(df) < 100:
            print(f"      ✗ Insufficient data")
            return None
        
        # Create features
        features_df = fetcher.create_features(df)
        
        if features_df is None or len(features_df) < 50:
            print(f"      ✗ Feature creation failed")
            return None
        
        # Prepare for ML
        model = EnsembleTradingModel(task='regression', random_state=42)
        X = model.prepare_features(features_df)
        
        # Target: next period return
        y = df['close'].pct_change().shift(-1).dropna()
        
        # Align
        common_idx = features_df.index.intersection(y.index)
        X = features_df.loc[common_idx]
        X = model.prepare_features(X)
        y = y.loc[common_idx]
        
        # Clean data
        X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        # Train/test split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        if self.use_lstm and timeframe in ['1m', '5m', '1d']:  # Use LSTM for these
            try:
                lstm = LSTMPredictor(lookback=30, units=50)
                lstm.fit(X_train, y_train, epochs=20, verbose=0)
                latest_pred = lstm.predict(X_test)[-1] if len(X_test) > 30 else 0
                model_type = 'LSTM'
            except:
                # Fallback to ensemble
                model.fit(X_train, y_train, use_ensemble='stacking')
                latest_pred = model.predict(X_test[-1:].reshape(1, -1))[0]
                model_type = 'Ensemble'
        else:
            # Use ensemble model
            model.fit(X_train, y_train, use_ensemble='stacking')
            latest_pred = model.predict(X_test[-1:].reshape(1, -1))[0]
            model_type = 'Ensemble'
        
        # Evaluate
        if self.use_lstm and model_type == 'LSTM':
            predictions = lstm.predict(X_test)
            valid_mask = ~np.isnan(predictions)
            if valid_mask.sum() > 0:
                r2 = 1 - ((y_test[valid_mask] - predictions[valid_mask])**2).sum() / ((y_test[valid_mask] - y_test[valid_mask].mean())**2).sum()
                rmse = np.sqrt(((y_test[valid_mask] - predictions[valid_mask])**2).mean())
            else:
                r2, rmse = np.nan, np.nan
        else:
            predictions = model.predict(X_test)
            r2 = 1 - ((y_test - predictions)**2).sum() / ((y_test - y_test.mean())**2).sum()
            rmse = np.sqrt(((y_test - predictions)**2).mean())
        
        print(f"      ✓ {model_type}: Pred={latest_pred:.4f}, R²={r2:.4f}, RMSE={rmse:.4f}")
        
        result = {
            'timeframe': timeframe,
            'prediction': latest_pred,
            'r2': r2,
            'rmse': rmse,
            'model_type': model_type,
            'bars': len(df),
            'samples': len(X_train)
        }
        
        # Store
        self.predictions[timeframe] = result
        
        return result
    
    def predict_all_timeframes(self, fetcher, symbol):
        """
        Predict on all configured timeframes
        
        Args:
            fetcher: SchwabDataFetcher instance
            symbol: Stock symbol
        
        Returns:
            predictions: Dict of predictions by timeframe
        """
        print(f"\nGenerating Multi-Timeframe Predictions for {symbol}:")
        print("=" * 80)
        
        results = {}
        
        for timeframe in self.timeframes:
            try:
                result = self.predict_timeframe(fetcher, symbol, timeframe)
                if result:
                    results[timeframe] = result
            except Exception as e:
                print(f"      ✗ Error: {e}")
        
        self.predictions = results
        
        return results
    
    def get_combined_signal(self):
        """
        Combine predictions from all timeframes
        
        Returns:
            combined_prediction: Weighted average of predictions
            confidence: Confidence score (0-1)
        """
        if not self.predictions:
            return 0.0, 0.0
        
        # Weight by inverse RMSE (better predictions get more weight)
        weights = []
        predictions = []
        
        for tf, pred in self.predictions.items():
            if pred['rmse'] > 0:
                weight = 1.0 / pred['rmse']
                weights.append(weight)
                predictions.append(pred['prediction'])
        
        if not weights:
            return 0.0, 0.0
        
        # Normalize weights
        weights = np.array(weights) / sum(weights)
        
        # Weighted average
        combined = np.average(predictions, weights=weights)
        
        # Confidence: agreement between timeframes
        pred_std = np.std(predictions)
        confidence = 1.0 / (1.0 + pred_std * 100)  # Higher std = lower confidence
        
        return combined, confidence
    
    def generate_training_predictions(self, fetcher, symbol, timeframe, train_size=0.8):
        """
        Generate predictions for all samples in a timeframe (for training)
        
        Args:
            fetcher: SchwabDataFetcher instance
            symbol: Stock symbol
            timeframe: Timeframe string
            train_size: Fraction to use for training
        
        Returns:
            predictions: Array of predictions for all samples
            trained_model: The trained model
        """
        print(f"      Generating {timeframe} predictions for training...")
        
        # Fetch data
        df = self.fetch_timeframe_data(fetcher, symbol, timeframe)
        
        if df is None or len(df) < 100:
            return None, None
        
        # Create features
        features_df = fetcher.create_features(df)
        
        if features_df is None or len(features_df) < 50:
            return None, None
        
        # Prepare for ML
        model = EnsembleTradingModel(task='regression', random_state=42)
        X = model.prepare_features(features_df)
        
        # Target: next period return
        y = df['close'].pct_change().shift(-1).dropna()
        
        # Align
        common_idx = features_df.index.intersection(y.index)
        X = features_df.loc[common_idx]
        X = model.prepare_features(X)
        y = y.loc[common_idx]
        
        # Clean data
        X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        # Train/test split
        split_idx = int(len(X) * train_size)
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        
        # Train model
        model.fit(X_train, y_train, use_ensemble='stacking')
        
        # Predict on ALL samples (including train)
        predictions = model.predict(X)
        
        print(f"         ✓ {len(predictions)} predictions generated")
        
        return predictions, model


class EVClassifier:
    """
    Expected Value (EV) Based Classifier with Multi-Timeframe Features
    
    Classifies trades based on Expected Value:
    EV = (Win% × Avg Win) - (Loss% × Avg Loss)
    
    Uses predictions from multiple timeframes as features (meta-learning/stacking).
    Only takes trades with positive EV and sufficient confidence.
    """
    
    def __init__(self, min_ev=0.001, min_confidence=0.6, risk_free_rate=0.05, 
                 use_timeframe_features=True):
        """
        Initialize EV-based classifier
        
        Args:
            min_ev: Minimum expected value to trade (e.g., 0.001 = 0.1%)
            min_confidence: Minimum confidence to take trade (0-1)
            risk_free_rate: Risk-free rate for Sharpe calculation
            use_timeframe_features: Whether to use multi-timeframe predictions as features
        """
        self.min_ev = min_ev
        self.min_confidence = min_confidence
        self.risk_free_rate = risk_free_rate
        self.use_timeframe_features = use_timeframe_features
        self.regression_model = None  # Predicts expected return
        self.classifier_model = None  # Predicts win probability
        self.is_fitted = False
        self.performance_stats = None
        self.timeframe_cols = []  # Track which columns are timeframe predictions
    
    def calculate_performance_stats(self, y_returns):
        """
        Calculate historical win/loss statistics
        
        Args:
            y_returns: Historical returns
        
        Returns:
            stats: Dict with win rate, avg win, avg loss
        """
        wins = y_returns[y_returns > 0]
        losses = y_returns[y_returns < 0]
        
        win_rate = len(wins) / len(y_returns) if len(y_returns) > 0 else 0.5
        avg_win = wins.mean() if len(wins) > 0 else 0.01
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0.01
        
        return {
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_trades': len(y_returns),
            'wins': len(wins),
            'losses': len(losses)
        }
    
    def fit(self, X, y_returns, timeframe_predictions=None):
        """
        Train EV-based classifier with optional multi-timeframe predictions
        
        Trains two models:
        1. Regression model to predict expected return
        2. Classification model to predict win probability
        
        Args:
            X: Base feature data (can be DataFrame or array)
            y_returns: Target returns
            timeframe_predictions: Optional dict {timeframe: predictions_array}
                                  e.g., {'1m': array([...]), '5m': array([...]), '1d': array([...])}
        """
        from sklearn.ensemble import GradientBoostingRegressor
        
        print(f"\n   Training EV Classifier on {len(X)} samples...")
        
        # Convert to DataFrame if needed
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        # Add timeframe predictions as features
        if self.use_timeframe_features and timeframe_predictions:
            print(f"   Adding {len(timeframe_predictions)} timeframe predictions as features...")
            
            for tf, preds in timeframe_predictions.items():
                col_name = f'pred_{tf}'
                # Ensure same length (pad with NaN if needed)
                if len(preds) < len(X):
                    preds = np.pad(preds, (0, len(X) - len(preds)), constant_values=np.nan)
                elif len(preds) > len(X):
                    preds = preds[:len(X)]
                
                X[col_name] = preds
                self.timeframe_cols.append(col_name)
            
            print(f"      Features with timeframes: {X.shape[1]} columns")
            print(f"      Timeframe features: {', '.join(self.timeframe_cols)}")
        
        # Convert to numpy for sklearn
        X_array = X.values if isinstance(X, pd.DataFrame) else X
        
        # Calculate performance stats
        self.performance_stats = self.calculate_performance_stats(y_returns)
        print(f"   Historical Stats:")
        print(f"      Win Rate: {self.performance_stats['win_rate']*100:.1f}%")
        print(f"      Avg Win: {self.performance_stats['avg_win']*100:.2f}%")
        print(f"      Avg Loss: {self.performance_stats['avg_loss']*100:.2f}%")
        
        # 1. Train regression model for expected return
        self.regression_model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            random_state=42
        )
        self.regression_model.fit(X_array, y_returns)
        
        # 2. Train classifier for win/loss probability
        y_binary = (y_returns > 0).astype(int)  # 1=win, 0=loss
        
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=20,
            random_state=42,
            class_weight='balanced'
        )
        
        # Calibrate for accurate probabilities
        self.classifier_model = CalibratedClassifierCV(rf, method='sigmoid', cv=3)
        self.classifier_model.fit(X_array, y_binary)
        
        self.is_fitted = True
        
        print(f"   ✓ EV Classifier trained")
        
        return self
    
    def calculate_ev(self, expected_return, win_prob):
        """
        Calculate Expected Value
        
        EV = (Win Prob × Expected Return) - (Loss Prob × Expected Loss)
        
        Args:
            expected_return: Predicted return
            win_prob: Probability of winning
        
        Returns:
            ev: Expected value
        """
        # Use historical avg win/loss as baseline
        avg_win = self.performance_stats['avg_win']
        avg_loss = self.performance_stats['avg_loss']
        
        # Adjust by predicted return
        if expected_return > 0:
            adjusted_win = max(expected_return, avg_win)
            adjusted_loss = avg_loss
        else:
            adjusted_win = avg_win
            adjusted_loss = max(abs(expected_return), avg_loss)
        
        # Calculate EV
        loss_prob = 1 - win_prob
        ev = (win_prob * adjusted_win) - (loss_prob * adjusted_loss)
        
        return ev
    
    def predict_signal(self, X, timeframe_predictions=None):
        """
        Predict trading signal based on Expected Value
        
        Args:
            X: Base feature data (single sample or array)
            timeframe_predictions: Optional dict {timeframe: prediction_value}
                                  e.g., {'1m': 0.002, '5m': 0.003, '1d': 0.001}
        
        Returns:
            signal: 'BUY', 'SELL', or 'HOLD'
            confidence: Confidence score (0-1)
            ev_metrics: Dict with EV analysis
        """
        if not self.is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")
        
        # Convert to DataFrame if needed
        if not isinstance(X, pd.DataFrame):
            if X.ndim == 1:
                X = X.reshape(1, -1)
            X = pd.DataFrame(X)
        
        # Add timeframe predictions as features
        if self.use_timeframe_features and timeframe_predictions:
            for tf, pred in timeframe_predictions.items():
                col_name = f'pred_{tf}'
                if col_name in self.timeframe_cols:
                    X[col_name] = pred
        
        # Convert to numpy for sklearn
        X_array = X.values if isinstance(X, pd.DataFrame) else X
        
        # Ensure 2D
        if X_array.ndim == 1:
            X_array = X_array.reshape(1, -1)
        
        # 1. Predict expected return
        expected_return = self.regression_model.predict(X_array)[0]
        
        # 2. Predict win probability
        win_prob = self.classifier_model.predict_proba(X_array)[0][1]  # Prob of return > 0
        
        # 3. Calculate Expected Value
        ev = self.calculate_ev(expected_return, win_prob)
        
        # 4. Calculate risk-adjusted EV (Sharpe-like)
        # Assuming volatility ~ avg_loss
        volatility = self.performance_stats['avg_loss']
        sharpe_ev = (ev - self.risk_free_rate / 252) / volatility if volatility > 0 else 0
        
        # 5. Generate BUY signal based on positive EV
        # Only BUY if: positive EV + good win probability + positive expected return
        if ev > self.min_ev and win_prob > self.min_confidence and expected_return > 0:
            signal = 'BUY'
            # Confidence based on EV magnitude and win probability
            ev_strength = min(ev / (self.min_ev * 2), 1.0)  # How much above min EV
            confidence = (win_prob * 0.6 + ev_strength * 0.4)  # Weighted average
            confidence = min(confidence, 1.0)
        else:
            signal = 'NO_TRADE'
            # Confidence in NOT trading (inverse of how close we are to BUY threshold)
            if ev > 0 and expected_return > 0:
                # Close to BUY threshold but not quite
                confidence = 0.5 + (1 - min(ev / self.min_ev, 1.0)) * 0.3
            else:
                # Clearly not a good trade
                confidence = 0.7 + min(abs(ev) / self.min_ev, 0.3)
        
        # EV metrics
        ev_metrics = {
            'expected_return': expected_return,
            'win_probability': win_prob,
            'expected_value': ev,
            'sharpe_ev': sharpe_ev,
            'risk_reward_ratio': abs(expected_return / volatility) if volatility > 0 else 0
        }
        
        return signal, confidence, ev_metrics
    
    def evaluate(self, X, y_returns, timeframe_predictions=None):
        """
        Evaluate EV classifier performance
        
        Args:
            X: Feature data
            y_returns: True returns
            timeframe_predictions: Optional dict {timeframe: predictions_array}
        
        Returns:
            metrics: Dict with performance metrics
        """
        # Predict for all samples
        signals = []
        evs = []
        confidences = []
        
        for i in range(len(X)):
            # Get timeframe predictions for this sample
            tf_preds_i = None
            if timeframe_predictions:
                tf_preds_i = {tf: preds[i] for tf, preds in timeframe_predictions.items()
                             if i < len(preds)}
            
            signal, confidence, ev_metrics = self.predict_signal(X[i], tf_preds_i)
            signals.append(signal)
            evs.append(ev_metrics['expected_value'])
            confidences.append(confidence)
        
        signals = np.array(signals)
        evs = np.array(evs)
        
        # Calculate trading performance (BUY signals only)
        buy_mask = signals == 'BUY'
        no_trade_mask = signals == 'NO_TRADE'
        
        # Returns for BUY signals
        buy_returns = y_returns[buy_mask].mean() if buy_mask.sum() > 0 else 0
        
        # Win rate for BUY signals
        buy_wins = (y_returns[buy_mask] > 0).sum() if buy_mask.sum() > 0 else 0
        buy_total = buy_mask.sum()
        buy_win_rate = buy_wins / buy_total if buy_total > 0 else 0
        
        # Average EV (only for BUY signals)
        buy_evs = evs[buy_mask] if buy_mask.sum() > 0 else np.array([])
        avg_ev = buy_evs.mean() if len(buy_evs) > 0 else 0
        avg_positive_ev = buy_evs[buy_evs > 0].mean() if (buy_evs > 0).sum() > 0 else 0
        
        # Direction accuracy (for BUY signals only)
        direction_accuracy = buy_win_rate  # Same as win rate for BUY-only system
        
        # Confidence stats
        buy_confidences = np.array([confidences[i] for i in range(len(signals)) if signals[i] == 'BUY'])
        avg_buy_confidence = buy_confidences.mean() if len(buy_confidences) > 0 else 0
        
        # Profitability estimate
        total_profit = buy_returns * buy_total if buy_total > 0 else 0
        
        return {
            'avg_ev': avg_ev,
            'avg_positive_ev': avg_positive_ev,
            'buy_signals': buy_mask.sum(),
            'no_trade_signals': no_trade_mask.sum(),
            'buy_return': buy_returns,
            'buy_win_rate': buy_win_rate,
            'direction_accuracy': direction_accuracy,
            'avg_confidence': np.mean(confidences),
            'avg_buy_confidence': avg_buy_confidence,
            'total_profit_estimate': total_profit
        }


def test_complete_system(symbol='AAPL'):
    """
    Test complete multi-timeframe system with classifier
    """
    print("\n" + "=" * 80)
    print(f"COMPLETE MULTI-TIMEFRAME SYSTEM TEST - {symbol}")
    print("=" * 80)
    
    # Initialize
    import schwabdev
    from dotenv import load_dotenv
    load_dotenv()
    
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    # Multi-timeframe predictions
    print("\n1. MULTI-TIMEFRAME PREDICTIONS:")
    print("-" * 80)
    
    mtp = MultiTimeframePredictor(timeframes=['5m', '1d'], use_lstm=False)
    predictions = mtp.predict_all_timeframes(fetcher, symbol)
    
    if not predictions:
        print("   ✗ No predictions generated")
        return
    
    # Combined signal
    print("\n2. COMBINED SIGNAL:")
    print("-" * 80)
    
    combined_pred, confidence = mtp.get_combined_signal()
    print(f"   Combined Prediction: {combined_pred:.4f} ({combined_pred*100:.2f}%)")
    print(f"   Confidence: {confidence:.2f}")
    
    # Train EV Classifier
    print("\n3. TRAINING EV CLASSIFIER:")
    print("-" * 80)
    
    # Use daily data for classifier training
    df_daily = fetcher.get_price_history(symbol, periodType='year', period=10)
    features_df = fetcher.create_features(df_daily)
    
    model = EnsembleTradingModel(task='regression', random_state=42)
    X = model.prepare_features(features_df)
    y = df_daily['close'].pct_change().shift(-1).dropna()
    
    # Align
    common_idx = features_df.index.intersection(y.index)
    X = features_df.loc[common_idx]
    X = model.prepare_features(X)
    y = y.loc[common_idx]
    
    # Clean
    X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
    
    # Split
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Train EV classifier
    ev_classifier = EVClassifier(min_ev=0.001, min_confidence=0.55)
    ev_classifier.fit(X_train, y_train)
    
    # Evaluate
    print("\n4. EV CLASSIFIER EVALUATION:")
    print("-" * 80)
    
    metrics = ev_classifier.evaluate(X_test, y_test)
    print(f"   Average EV: {metrics['avg_ev']*100:.3f}%")
    print(f"   Avg Positive EV: {metrics['avg_positive_ev']*100:.3f}%")
    print(f"   Direction Accuracy: {metrics['direction_accuracy']*100:.1f}%")
    print(f"\n   Signal Distribution:")
    print(f"      BUY:  {metrics['buy_signals']} signals ({metrics['buy_win_rate']*100:.1f}% win rate, {metrics['buy_return']*100:.2f}% avg return)")
    print(f"      SELL: {metrics['sell_signals']} signals ({metrics['sell_win_rate']*100:.1f}% win rate, {metrics['sell_return']*100:.2f}% avg return)")
    print(f"      HOLD: {metrics['hold_signals']} signals")
    
    # Generate signal for latest bar
    print("\n5. FINAL SIGNAL (Latest Bar):")
    print("-" * 80)
    
    signal, sig_conf, ev_metrics = ev_classifier.predict_signal(X_test[-1])
    
    print(f"\n   🎯 SIGNAL: {signal}")
    print(f"   📊 Confidence: {sig_conf*100:.1f}%")
    print(f"\n   💰 Expected Value Analysis:")
    print(f"      Expected Return: {ev_metrics['expected_return']*100:.3f}%")
    print(f"      Win Probability: {ev_metrics['win_probability']*100:.1f}%")
    print(f"      Expected Value (EV): {ev_metrics['expected_value']*100:.3f}%")
    print(f"      Sharpe EV: {ev_metrics['sharpe_ev']:.3f}")
    print(f"      Risk/Reward Ratio: {ev_metrics['risk_reward_ratio']:.2f}")
    
    # Trading recommendation
    print(f"\n   📋 Recommendation:")
    if signal == 'BUY' and ev_metrics['expected_value'] > 0.002:
        print(f"      ✅ STRONG BUY - High positive EV")
    elif signal == 'BUY':
        print(f"      ⚠️ WEAK BUY - Low positive EV")
    elif signal == 'SELL' and ev_metrics['expected_value'] < -0.002:
        print(f"      ✅ STRONG SELL - High negative EV")
    elif signal == 'SELL':
        print(f"      ⚠️ WEAK SELL - Low negative EV")
    else:
        print(f"      ⏸️ HOLD - No clear edge")
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE EV-BASED SYSTEM TEST FINISHED!")
    print("=" * 80)
    
    return {
        'predictions': predictions,
        'combined_prediction': combined_pred,
        'confidence': confidence,
        'signal': signal,
        'signal_confidence': sig_conf,
        'ev_metrics': ev_metrics,
        'classifier_metrics': metrics
    }


if __name__ == '__main__':
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    test_complete_system(symbol)

