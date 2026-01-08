"""
Ensemble Trading Model
Based on methods from "Machine Learning for Algorithmic Trading" by Stefan Jansen
Integrates with Schwab API for real-time data and predictions

This module implements various ensemble methods:
- Random Forest (Bagging)
- Gradient Boosting
- Voting Ensemble
- Stacking Ensemble
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

import schwabdev

# Scikit-learn ensemble models
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    BaggingClassifier, BaggingRegressor,
    AdaBoostClassifier, AdaBoostRegressor,
    VotingClassifier, VotingRegressor,
    StackingClassifier, StackingRegressor
)
from sklearn.model_selection import (
    TimeSeriesSplit, cross_val_score, GridSearchCV,
    StratifiedKFold, cross_validate, train_test_split
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_squared_error, r2_score, roc_auc_score,
    precision_recall_curve, average_precision_score,
    roc_curve, mean_absolute_error, median_absolute_error
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR

# Optional: XGBoost for advanced ensemble (will check if available)
try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Note: xgboost not installed. Will use Ridge as meta-learner instead.")
    print("Install with: pip install xgboost")

# Optional: SMOTE for oversampling (will check if available)
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    print("Note: imbalanced-learn not installed. SMOTE oversampling disabled.")
    print("Install with: pip install imbalanced-learn")

# Load environment variables
load_dotenv()


class SchwabDataFetcher:
    """Fetches and processes data from Schwab API"""
    
    def __init__(self, client):
        self.client = client
    
    def get_price_history(self, symbol, periodType='year', period=1, frequencyType='daily', frequency=1, startDate=None, endDate=None):
        """
        Get price history for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            periodType: Period type ('day', 'month', 'year', 'ytd')
            period: Period (int) - for year: 1,2,3,5,10,15,20; for month: 1,2,3,6; etc.
            frequencyType: Frequency type ('minute', 'daily', 'weekly', 'monthly')
            frequency: Frequency (int) - for daily/weekly/monthly: 1; for minute: 1,5,10,15,30
            startDate: Start date (datetime) - optional, for specifying date range
            endDate: End date (datetime) - optional, for specifying date range
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            response = self.client.price_history(
                symbol, 
                periodType=periodType,
                period=period,
                frequencyType=frequencyType,
                frequency=frequency,
                startDate=startDate,
                endDate=endDate
            )
            
            # Check response status
            if response.status_code != 200:
                raise ValueError(f"API returned status {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                error_msg = data.get('error', 'Unknown error')
                raise ValueError(f"API error for {symbol}: {error_msg}")
            
            if 'candles' not in data:
                # Log the actual response for debugging
                print(f"Warning: Unexpected response structure for {symbol}. Keys: {list(data.keys())}")
                if 'empty' in str(data).lower() or len(data) == 0:
                    raise ValueError(f"No data available for {symbol} (symbol may be invalid or market closed)")
                raise ValueError(f"No candle data found for {symbol}. Response keys: {list(data.keys())}")
            
            candles = data['candles']
            if not candles or len(candles) == 0:
                raise ValueError(f"Empty candle data for {symbol}")
            
            df = pd.DataFrame(candles)
            
            # Check if datetime column exists
            if 'datetime' not in df.columns:
                # Try alternative column names
                if 'time' in df.columns:
                    df['datetime'] = df['time']
                elif 'timestamp' in df.columns:
                    df['datetime'] = df['timestamp']
                else:
                    raise ValueError(f"No datetime column found in response. Columns: {df.columns.tolist()}")
            
            # Convert datetime to pandas datetime
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms', errors='coerce')
            
            # Remove any rows with invalid datetime
            df = df.dropna(subset=['datetime'])
            
            if len(df) == 0:
                raise ValueError(f"No valid datetime data for {symbol}")
            
            df.set_index('datetime', inplace=True)
            
            # Rename columns to standard names (handle different column names)
            column_mapping = {
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            # Check actual column names and map them
            actual_cols = df.columns.tolist()
            for i, col in enumerate(['open', 'high', 'low', 'close', 'volume']):
                if i < len(actual_cols):
                    column_mapping[actual_cols[i]] = col
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Ensure we have the required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}. Available: {df.columns.tolist()}")
            
            return df[required_cols]
        except Exception as e:
            print(f"Error fetching price history for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_intraday_data(self, symbol, period=1, frequency=5):
        """
        Get intraday (minute-level) data for high-frequency trading
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Number of days (1, 2, 3, 4, 5, 10)
            frequency: Minute frequency (1, 5, 10, 15, 30)
        
        Returns:
            DataFrame with OHLCV data at minute level
        """
        return self.get_price_history(
            symbol, 
            periodType='day',
            period=period,
            frequencyType='minute',
            frequency=frequency
        )
    
    def get_extended_intraday_data(self, symbol, months=6, frequency=30):
        """
        Fetch multiple months of intraday data using startDate/endDate
        
        Note: According to API documentation, 30-minute intervals can get up to ~9 months
        of historical data using startDate/endDate parameters.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            months: Number of months to fetch (default: 6)
            frequency: Minute frequency (1, 5, 10, 15, 30)
        
        Returns:
            DataFrame with intraday data
        """
        from datetime import datetime, timedelta
        
        print(f"   Fetching {months} months of {frequency}-minute bar data...")
        print(f"   Using startDate/endDate to get {months} months of data...")
        
        # Calculate date range (6 months back from today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)  # Approximate 30 days per month
        
        print(f"   Date range: {start_date.date()} to {end_date.date()}")
        
        # Try using startDate/endDate (API supports this for minute data, up to ~9 months for 30-min bars)
        try:
            df = self.get_price_history(
                symbol,
                frequencyType='minute',
                frequency=frequency,
                startDate=start_date,
                endDate=end_date
            )
            
            if df is not None and len(df) > 0:
                print(f"   ✓ Fetched {len(df)} data points")
                print(f"   Actual date range: {df.index.min()} to {df.index.max()}")
                return df
        except Exception as e:
            print(f"   Error with startDate/endDate approach: {e}")
            print(f"   Trying fallback with periodType='day' (max 10 days)...")
        
        # Fallback: try day periodType (max 10 days)
        try:
            df = self.get_price_history(
                symbol,
                periodType='day',
                period=10,
                frequencyType='minute',
                frequency=frequency
            )
            if df is not None and len(df) > 0:
                print(f"   ✓ Fetched {len(df)} data points (max available: 10 days)")
                print(f"   Note: Using fallback - only returns most recent 10 days")
                return df
        except Exception as e2:
            print(f"   Error with fallback: {e2}")
        
        return None
    
    def get_maximum_data(self, symbol, frequencyType='minute', frequency=30):
        """
        Fetch maximum available data for a symbol by trying different periods
        and combining results if possible
        
        Args:
            symbol: Stock symbol
            frequencyType: 'minute' or 'daily'
            frequency: Frequency value (1, 5, 10, 15, 30 for minute; 1 for daily)
        
        Returns:
            DataFrame with maximum available data
        """
        all_data = []
        
        if frequencyType == 'minute':
            # For minute data, try maximum period (10 days)
            print(f"   Fetching maximum minute-level data for {symbol}...")
            periods_to_try = [
                ('day', 10),   # Maximum for minute data
                ('day', 5),
                ('day', 3),
                ('day', 1),
            ]
        else:  # daily
            # For daily data, try maximum periods
            print(f"   Fetching maximum daily data for {symbol}...")
            periods_to_try = [
                ('year', 20),  # Maximum: 20 years
                ('year', 10),
                ('year', 5),
                ('year', 2),
                ('year', 1),
                ('month', 6),
                ('month', 3),
                ('month', 1),
            ]
        
        for period_type, period in periods_to_try:
            try:
                df = self.get_price_history(symbol, periodType=period_type, period=period, 
                                          frequencyType=frequencyType, frequency=frequency)
                if df is not None and len(df) > 0:
                    all_data.append(df)
                    print(f"   ✓ Fetched {len(df)} points from {period} {period_type}(s)")
                    # If we got the maximum period, we're done
                    if (frequencyType == 'minute' and period == 10) or \
                       (frequencyType == 'daily' and period == 20):
                        break
            except Exception as e:
                print(f"   Warning: Could not fetch {period} {period_type}(s): {e}")
                continue
        
        if not all_data:
            return None
        
        # Combine all data, removing duplicates
        if len(all_data) > 1:
            combined_df = pd.concat(all_data, ignore_index=False)
            combined_df = combined_df[~combined_df.index.duplicated(keep='first')]
            combined_df = combined_df.sort_index()
            print(f"   ✓ Combined data: {len(combined_df)} total unique data points")
            return combined_df
        else:
            return all_data[0]
    
    def get_multiple_timeframes(self, symbol, timeframes=['1min', '5min', '15min', '1hour', '1day']):
        """
        Get data for multiple timeframes simultaneously
        
        Args:
            symbol: Stock symbol
            timeframes: List of timeframe strings like '1min', '5min', '15min', '1hour', '1day'
        
        Returns:
            Dictionary of DataFrames with keys as timeframe strings
        """
        data = {}
        
        timeframe_map = {
            '1min': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 1},
            '5min': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 5},
            '15min': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 15},
            '30min': {'periodType': 'day', 'period': 5, 'frequencyType': 'minute', 'frequency': 30},
            '1hour': {'periodType': 'day', 'period': 10, 'frequencyType': 'minute', 'frequency': 60},  # Not directly supported, using 60min
            '1day': {'periodType': 'year', 'period': 1, 'frequencyType': 'daily', 'frequency': 1}
        }
        
        for tf in timeframes:
            if tf in timeframe_map:
                params = timeframe_map[tf]
                df = self.get_price_history(symbol, **params)
                if df is not None:
                    data[tf] = df
                    print(f"  ✓ Fetched {len(df)} bars for {tf} timeframe")
        
        return data
    
    def get_quote(self, symbol):
        """Get current quote for a symbol"""
        try:
            response = self.client.quote(symbol)
            data = response.json()
            return data.get(symbol, {})
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return {}
    
    def create_features(self, df, lookback_periods=[5, 10, 20, 50]):
        """
        Create technical features from price data
        Enhanced feature engineering based on:
        - "Machine Learning for Algorithmic Trading" by Stefan Jansen
        - "Finding Alphas" by WorldQuant (alpha factor patterns)
        
        Args:
            df: DataFrame with OHLCV data
            lookback_periods: List of periods for moving averages
        
        Returns:
            DataFrame with features including:
            - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
            - Alpha factors from "Finding Alphas" book (rank, delay, correlation, etc.)
            - Momentum, volatility, and volume features
            - Time-based patterns
        """
        if df is None or len(df) == 0:
            return None
        
        features_df = df.copy()
        
        # ========== RETURNS & TRANSFORMATIONS ==========
        # Basic returns
        features_df['returns'] = features_df['close'].pct_change()
        features_df['log_returns'] = np.log(features_df['close'] / features_df['close'].shift(1))
        
        # Winsorize returns to handle outliers (clip at 0.01st and 99.99th percentile)
        q_low, q_high = features_df['returns'].quantile([0.0001, 0.9999])
        features_df['returns_winsorized'] = features_df['returns'].clip(lower=q_low, upper=q_high)
        
        # ========== LAGGED RETURNS (Multiple Timeframes) ==========
        # Based on book: lagged returns for 1 day, 1 week, 2 weeks, 1 month, 2 months, 3 months
        lag_periods = [1, 5, 10, 21, 42, 63]
        for lag in lag_periods:
            # Geometric mean of returns over period
            ret_lag = features_df['close'].pct_change(lag)
            features_df[f'return_{lag}d'] = (ret_lag + 1).pow(1 / lag) - 1
            
            # Additional lags (shifted by 1-5 periods)
            for shift in [1, 2, 3, 4, 5]:
                if lag in [1, 5, 10, 21]:  # Only for shorter periods
                    features_df[f'return_{lag}d_lag{shift}'] = features_df[f'return_{lag}d'].shift(shift * lag)
        
        # ========== MOVING AVERAGES ==========
        # Simple Moving Averages
        for period in lookback_periods:
            features_df[f'ma_{period}'] = features_df['close'].rolling(window=period).mean()
            features_df[f'ma_{period}_ratio'] = features_df['close'] / features_df[f'ma_{period}']
            features_df[f'ma_{period}_diff'] = features_df['close'] - features_df[f'ma_{period}']
            features_df[f'ma_{period}_pct'] = (features_df['close'] - features_df[f'ma_{period}']) / features_df[f'ma_{period}']
        
        # Exponential Moving Averages
        for period in [12, 26, 50]:
            features_df[f'ema_{period}'] = features_df['close'].ewm(span=period, adjust=False).mean()
            features_df[f'ema_{period}_ratio'] = features_df['close'] / features_df[f'ema_{period}']
        
        # ========== MOMENTUM INDICATORS ==========
        # Rate of Change (ROC)
        for period in [5, 10, 20]:
            features_df[f'roc_{period}'] = features_df['close'].pct_change(period) * 100
        
        # Momentum (price change over period)
        for period in [5, 10, 20]:
            features_df[f'momentum_{period}'] = features_df['close'] - features_df['close'].shift(period)
            features_df[f'momentum_{period}_pct'] = (features_df['close'] - features_df['close'].shift(period)) / features_df['close'].shift(period)
        
        # ========== VOLATILITY MEASURES ==========
        # Rolling standard deviation of returns
        for period in [5, 10, 20, 30]:
            features_df[f'volatility_{period}'] = features_df['returns'].rolling(window=period).std()
            features_df[f'volatility_{period}_annualized'] = features_df[f'volatility_{period}'] * np.sqrt(252)  # Annualized
        
        # ATR (Average True Range) - Based on book
        high_low = features_df['high'] - features_df['low']
        high_close = np.abs(features_df['high'] - features_df['close'].shift())
        low_close = np.abs(features_df['low'] - features_df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        features_df['atr'] = tr.rolling(window=14).mean()
        features_df['atr_ratio'] = features_df['atr'] / features_df['close']  # Normalized
        
        # Parkinson volatility estimator (uses high/low)
        features_df['parkinson_vol'] = np.sqrt((1 / (4 * np.log(2))) * 
                                               np.log(features_df['high'] / features_df['low'])**2)
        features_df['parkinson_vol_14'] = features_df['parkinson_vol'].rolling(window=14).mean()
        
        # ========== RSI (Relative Strength Index) ==========
        delta = features_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)  # Add small value to avoid division by zero
        features_df['rsi'] = 100 - (100 / (1 + rs))
        features_df['rsi_overbought'] = (features_df['rsi'] > 70).astype(int)
        features_df['rsi_oversold'] = (features_df['rsi'] < 30).astype(int)
        
        # ========== MACD (Moving Average Convergence Divergence) ==========
        ema_12 = features_df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = features_df['close'].ewm(span=26, adjust=False).mean()
        features_df['macd'] = ema_12 - ema_26
        features_df['macd_signal'] = features_df['macd'].ewm(span=9, adjust=False).mean()
        features_df['macd_hist'] = features_df['macd'] - features_df['macd_signal']
        features_df['macd_signal_cross'] = (features_df['macd'] > features_df['macd_signal']).astype(int)
        
        # ========== BOLLINGER BANDS (Enhanced) ==========
        # Based on book: use log transformations for better distribution
        for period in [20]:
            bb_ma = features_df['close'].rolling(window=period).mean()
            bb_std = features_df['close'].rolling(window=period).std()
            bb_upper = bb_ma + (bb_std * 2)
            bb_lower = bb_ma - (bb_std * 2)
            
            features_df[f'bb_upper_{period}'] = bb_upper
            features_df[f'bb_lower_{period}'] = bb_lower
            features_df[f'bb_width_{period}'] = bb_upper - bb_lower
            features_df[f'bb_position_{period}'] = (features_df['close'] - bb_lower) / (bb_upper - bb_lower + 1e-10)
            
            # Log transformations (as per book)
            features_df[f'bb_high_log'] = np.log1p((bb_upper - features_df['close']) / bb_upper)
            features_df[f'bb_low_log'] = np.log1p((features_df['close'] - bb_lower) / features_df['close'])
            
            # Band touches
            features_df[f'bb_touch_upper'] = (features_df['close'] >= bb_upper * 0.98).astype(int)
            features_df[f'bb_touch_lower'] = (features_df['close'] <= bb_lower * 1.02).astype(int)
        
        # ========== VOLUME FEATURES ==========
        # Volume moving averages
        for period in [10, 20, 50]:
            features_df[f'volume_ma_{period}'] = features_df['volume'].rolling(window=period).mean()
            features_df[f'volume_ratio_{period}'] = features_df['volume'] / (features_df[f'volume_ma_{period}'] + 1e-10)
        
        # OBV (On-Balance Volume)
        features_df['price_change'] = features_df['close'].diff()
        features_df['obv'] = (np.sign(features_df['price_change']) * features_df['volume']).fillna(0).cumsum()
        features_df['obv_ma'] = features_df['obv'].rolling(window=20).mean()
        features_df['obv_ratio'] = features_df['obv'] / (features_df['obv_ma'] + 1e-10)
        
        # Volume-Price Trend (VPT)
        features_df['vpt'] = (features_df['returns'] * features_df['volume']).fillna(0).cumsum()
        features_df['vpt_ma'] = features_df['vpt'].rolling(window=20).mean()
        features_df['vpt_signal'] = (features_df['vpt'] > features_df['vpt_ma']).astype(int)
        
        # Price-Volume relationship
        features_df['price_volume'] = features_df['close'] * features_df['volume']
        features_df['price_volume_ma'] = features_df['price_volume'].rolling(window=20).mean()
        features_df['price_volume_ratio'] = features_df['price_volume'] / (features_df['price_volume_ma'] + 1e-10)
        
        # ========== PRICE PATTERNS ==========
        # High-Low range
        features_df['hl_range'] = features_df['high'] - features_df['low']
        features_df['hl_range_pct'] = features_df['hl_range'] / features_df['close']
        
        # Price position within day's range
        features_df['price_position'] = (features_df['close'] - features_df['low']) / (features_df['high'] - features_df['low'] + 1e-10)
        
        # High-Low-Close patterns
        features_df['close_vs_high'] = (features_df['close'] - features_df['high']) / features_df['close']
        features_df['close_vs_low'] = (features_df['close'] - features_df['low']) / features_df['close']
        features_df['high_low_ratio'] = features_df['high'] / (features_df['low'] + 1e-10)
        
        # Body and shadows (candlestick patterns)
        features_df['body'] = np.abs(features_df['close'] - features_df['open'])
        features_df['upper_shadow'] = features_df['high'] - features_df[['open', 'close']].max(axis=1)
        features_df['lower_shadow'] = features_df[['open', 'close']].min(axis=1) - features_df['low']
        features_df['body_ratio'] = features_df['body'] / (features_df['hl_range'] + 1e-10)
        
        # ========== TIME-BASED FEATURES ==========
        # Extract datetime features if index is datetime
        if isinstance(features_df.index, pd.DatetimeIndex):
            features_df['day_of_week'] = features_df.index.dayofweek
            features_df['day_of_month'] = features_df.index.day
            features_df['month'] = features_df.index.month
            features_df['quarter'] = features_df.index.quarter
            features_df['is_month_end'] = features_df.index.is_month_end.astype(int)
            features_df['is_month_start'] = features_df.index.is_month_start.astype(int)
            features_df['is_quarter_end'] = features_df.index.is_quarter_end.astype(int)
        
        # ========== ADDITIONAL TECHNICAL PATTERNS ==========
        # Stochastic Oscillator (%K and %D)
        low_14 = features_df['low'].rolling(window=14).min()
        high_14 = features_df['high'].rolling(window=14).max()
        features_df['stoch_k'] = 100 * (features_df['close'] - low_14) / (high_14 - low_14 + 1e-10)
        features_df['stoch_d'] = features_df['stoch_k'].rolling(window=3).mean()
        features_df['stoch_signal'] = (features_df['stoch_k'] > features_df['stoch_d']).astype(int)
        
        # Williams %R
        features_df['williams_r'] = -100 * (high_14 - features_df['close']) / (high_14 - low_14 + 1e-10)
        
        # Commodity Channel Index (CCI)
        tp = (features_df['high'] + features_df['low'] + features_df['close']) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
        features_df['cci'] = (tp - sma_tp) / (0.015 * mad + 1e-10)
        
        # ========== ALPHA FACTORS (From "Finding Alphas" Book) ==========
        # Based on WorldQuant's "Finding Alphas" book patterns
        
        # 1. Inverse Price (1/price) - Invest more if price is low
        features_df['alpha_inv_price'] = 1.0 / (features_df['close'] + 1e-10)
        
        # 2. Price Delay patterns (momentum/reversion)
        for delay in [1, 3, 5]:
            features_df[f'alpha_price_delay_{delay}'] = features_df['close'] - features_df['close'].shift(delay)
            features_df[f'alpha_price_delay_{delay}_pct'] = (features_df['close'] - features_df['close'].shift(delay)) / (features_df['close'].shift(delay) + 1e-10)
            features_df[f'alpha_price_delay_ratio_{delay}'] = features_df['close'] / (features_df['close'].shift(delay) + 1e-10)
        
        # 3. Time-series Rank (Ts_Rank) - Rank within time window
        for period in [5, 10, 20]:
            # Rank over time window (0 to 1, where 1 is highest)
            features_df[f'alpha_ts_rank_close_{period}'] = features_df['close'].rolling(window=period).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
            )
            features_df[f'alpha_ts_rank_volume_{period}'] = features_df['volume'].rolling(window=period).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
            )
            features_df[f'alpha_ts_rank_returns_{period}'] = features_df['returns'].rolling(window=period).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
            )
        
        # 4. Cross-sectional Rank (Rank) - For single stock, use rolling quantile as proxy
        for period in [10, 20]:
            # Use rolling quantile as proxy for rank
            features_df[f'alpha_quantile_close_{period}'] = features_df['close'].rolling(window=period).apply(
                lambda x: pd.Series(x).quantile(0.5), raw=False
            ) / (features_df['close'] + 1e-10)
        
        # 5. Correlation patterns (trend detection)
        for period in [5, 10, 20]:
            # Correlation between price and delayed price (trend)
            close_delayed = features_df['close'].shift(1)
            features_df[f'alpha_corr_trend_{period}'] = features_df['close'].rolling(window=period).corr(close_delayed)
            
            # Correlation between returns and volume
            if 'returns' in features_df.columns:
                features_df[f'alpha_corr_ret_vol_{period}'] = features_df['returns'].rolling(window=period).corr(features_df['volume'])
        
        # 6. Mean Reversion Alpha (-returns)
        features_df['alpha_mean_reversion'] = -features_df['returns']
        features_df['alpha_mean_reversion_delay1'] = -features_df['returns'].shift(1)
        features_df['alpha_mean_reversion_delay3'] = -features_df['returns'].shift(3)
        
        # 7. Trend with Volume Rank: (price/delay(price,3)) * rank(volume)
        for delay in [3, 5]:
            price_trend = features_df['close'] / (features_df['close'].shift(delay) + 1e-10)
            # Use rolling quantile as proxy for volume rank
            volume_rank = features_df['volume'].rolling(window=20).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
            )
            features_df[f'alpha_trend_volume_rank_{delay}'] = price_trend * volume_rank
        
        # 8. Time-series Mean/Std (Sharpe-like ratios)
        for period in [5, 10, 20]:
            ts_mean = features_df['returns'].rolling(window=period).mean()
            ts_std = features_df['returns'].rolling(window=period).std()
            features_df[f'alpha_sharpe_{period}'] = ts_mean / (ts_std + 1e-10)
            
            # Mean/Std for price
            price_mean = features_df['close'].rolling(window=period).mean()
            price_std = features_df['close'].rolling(window=period).std()
            features_df[f'alpha_price_mean_std_{period}'] = price_mean / (price_std + 1e-10)
        
        # 9. Time-series Skewness and Kurtosis
        for period in [10, 20]:
            features_df[f'alpha_ts_skew_{period}'] = features_df['returns'].rolling(window=period).skew()
            # Kurtosis using .kurt() method (pandas Rolling has .kurt() but not .kurtosis())
            features_df[f'alpha_ts_kurt_{period}'] = features_df['returns'].rolling(window=period).kurt()
        
        # 10. Price position patterns (from book examples)
        features_df['alpha_close_minus_high'] = features_df['close'] - features_df['high']
        features_df['alpha_hl2_minus_close'] = ((features_df['high'] + features_df['low']) / 2) - features_df['close']
        
        # 11. Fisher Transform (for robustness - normalizes to [-1, 1])
        # Apply Fisher transform to returns (arctanh)
        returns_clipped = features_df['returns'].clip(-0.999, 0.999)  # Clip for stability
        features_df['alpha_fisher_transform'] = 0.5 * np.log((1 + returns_clipped) / (1 - returns_clipped + 1e-10))
        
        # 12. Z-score normalization (robust scaling)
        for period in [10, 20]:
            mean_val = features_df['close'].rolling(window=period).mean()
            std_val = features_df['close'].rolling(window=period).std()
            features_df[f'alpha_zscore_{period}'] = (features_df['close'] - mean_val) / (std_val + 1e-10)
        
        # 13. Advanced alpha patterns from book
        # Alpha: (close/delay(close,3)) - momentum with normalization
        for delay in [1, 3, 5]:
            norm_factor = features_df['close'].shift(delay)
            features_df[f'alpha_normalized_momentum_{delay}'] = (features_df['close'] - norm_factor) / (norm_factor + 1e-10)
        
        # 14. Price relative to recent range
        for period in [10, 20]:
            high_period = features_df['high'].rolling(window=period).max()
            low_period = features_df['low'].rolling(window=period).min()
            features_df[f'alpha_price_range_{period}'] = (features_df['close'] - low_period) / (high_period - low_period + 1e-10)
        
        # 15. Volume-weighted price patterns
        # Price-volume interaction (like VWAP deviations)
        vwap = (features_df['high'] + features_df['low'] + features_df['close']) / 3
        features_df['alpha_price_vwap_diff'] = features_df['close'] - vwap
        features_df['alpha_price_vwap_ratio'] = features_df['close'] / (vwap + 1e-10)
        
        # ========== DROP NaN VALUES ==========
        # Drop rows with NaN values (after all feature creation)
        features_df = features_df.dropna()
        
        return features_df


class EnsembleTradingModel:
    """
    Ensemble Trading Model combining multiple algorithms
    Based on methods from "Machine Learning for Algorithmic Trading"
    Supports multiple timeframes for high-frequency trading
    """
    
    def __init__(self, task='classification', random_state=42, use_class_weight=True, use_smote=False):
        """
        Initialize ensemble model
        
        Args:
            task: 'classification' or 'regression'
            random_state: Random seed for reproducibility
            use_class_weight: Use class_weight='balanced' for classification models
            use_smote: Use SMOTE oversampling (requires imbalanced-learn)
        """
        self.task = task
        self.random_state = random_state
        self.use_class_weight = use_class_weight and task == 'classification'
        self.use_smote = use_smote and SMOTE_AVAILABLE and task == 'classification'
        self.models = {}
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.feature_selector = None
        self.selected_feature_indices = None
        self.is_fitted = False
        self.smote = None
        if self.use_smote:
            self.smote = SMOTE(random_state=random_state)
        
    
    def create_base_models_mlb_style(self):
        """
        Create base models in MLB-style architecture (Ridge, Lasso, SVR, GradientBoosting)
        This is the architecture from the MLB training.py file
        """
        self.models = {}
        
        if self.task == 'classification':
            # Classification base models (if needed)
            self.models['ridge'] = Ridge()
            self.models['lasso'] = Lasso()
            self.models['svr'] = SVR()
            self.models['gradient_boosting'] = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=self.random_state
            )
        else:  # regression
            # Regression base models (MLB-style)
            self.models['ridge'] = Ridge(alpha=1.0, random_state=self.random_state)
            self.models['lasso'] = Lasso(alpha=1.0, random_state=self.random_state)
            self.models['svr'] = SVR(kernel='rbf', C=1.0, epsilon=0.1)
            self.models['gradient_boosting'] = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=7,
                min_samples_leaf=3,
                subsample=0.8,
                random_state=self.random_state
            )
    
    def create_base_models(self):
        """Create base models for ensemble (original implementation)"""
        if self.task == 'classification':
            # Random Forest
            rf_params = {
                'n_estimators': 100,
                'max_depth': 15,
                'min_samples_leaf': 5,
                'max_features': 'sqrt',
                'bootstrap': True,
                'oob_score': True,
                'n_jobs': -1,
                'random_state': self.random_state
            }
            if self.use_class_weight:
                rf_params['class_weight'] = 'balanced'
            self.models['random_forest'] = RandomForestClassifier(**rf_params)
            
            # Gradient Boosting (doesn't support class_weight, but we can use sample_weight in fit)
            self.models['gradient_boosting'] = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_leaf=5,
                random_state=self.random_state
            )
            
            # AdaBoost (uses sample_weight internally, so class_weight not needed)
            estimator = DecisionTreeClassifier(max_depth=1, min_samples_leaf=20)
            if self.use_class_weight:
                estimator.class_weight = 'balanced'
            self.models['adaboost'] = AdaBoostClassifier(
                estimator=estimator,
                n_estimators=100,
                learning_rate=1.0,
                random_state=self.random_state
            )
            
            # Bagging
            estimator = DecisionTreeClassifier(max_depth=10)
            if self.use_class_weight:
                estimator.class_weight = 'balanced'
            self.models['bagging'] = BaggingClassifier(
                estimator=estimator,
                n_estimators=100,
                bootstrap=True,
                n_jobs=-1,
                random_state=self.random_state
            )
            
        else:  # regression
            # Random Forest (increased trees and depth for better performance)
            self.models['random_forest'] = RandomForestRegressor(
                n_estimators=200,  # Increased from 100
                max_depth=20,  # Increased from 15
                min_samples_leaf=3,  # Reduced from 5 (allow deeper splits)
                max_features='sqrt',
                bootstrap=True,
                oob_score=True,
                n_jobs=-1,
                random_state=self.random_state
            )
            
            # Gradient Boosting (increased trees, lower learning rate)
            self.models['gradient_boosting'] = GradientBoostingRegressor(
                n_estimators=200,  # Increased from 100
                learning_rate=0.05,  # Reduced from 0.1 (better generalization)
                max_depth=7,  # Increased from 5
                min_samples_leaf=3,  # Reduced from 5
                subsample=0.8,  # Added subsample for regularization
                random_state=self.random_state
            )
            
            # AdaBoost (increased trees)
            estimator = DecisionTreeRegressor(max_depth=4)  # Increased from 3
            self.models['adaboost'] = AdaBoostRegressor(
                estimator=estimator,
                n_estimators=150,  # Increased from 100
                learning_rate=0.8,  # Reduced from 1.0 (better generalization)
                random_state=self.random_state
            )
            
            # Bagging (increased trees and depth)
            estimator = DecisionTreeRegressor(max_depth=12)  # Increased from 10
            self.models['bagging'] = BaggingRegressor(
                estimator=estimator,
                n_estimators=150,  # Increased from 100
                bootstrap=True,
                n_jobs=-1,
                random_state=self.random_state
            )
    
    def create_voting_ensemble(self):
        """Create voting ensemble from base models"""
        if not self.models:
            self.create_base_models()
        
        if self.task == 'classification':
            self.ensemble_model = VotingClassifier(
                estimators=list(self.models.items()),
                voting='soft',  # Use probabilities
                n_jobs=-1
            )
        else:
            self.ensemble_model = VotingRegressor(
                estimators=list(self.models.items()),
                n_jobs=-1
            )
    
    def create_stacking_ensemble(self, final_estimator=None, use_mlb_architecture=False):
        """
        Create stacking ensemble with meta-learner
        
        Args:
            final_estimator: Meta-learner (default: XGBoost for regression, LogisticRegression for classification)
            use_mlb_architecture: Use MLB-style multi-level stacking architecture
        """
        if use_mlb_architecture:
            self.create_mlb_stacking_ensemble(final_estimator)
            return
        
        # Original single-level stacking
        if not self.models:
            self.create_base_models()
        
        if final_estimator is None:
            if self.task == 'classification':
                from sklearn.linear_model import LogisticRegression
                # Try XGBoost first, fallback to LogisticRegression
                if XGBOOST_AVAILABLE:
                    final_estimator = XGBClassifier(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=3,
                        random_state=self.random_state,
                        n_jobs=-1
                    )
                else:
                    final_estimator = LogisticRegression(random_state=self.random_state)
            else:
                # Try XGBoost first, fallback to Ridge
                if XGBOOST_AVAILABLE:
                    final_estimator = XGBRegressor(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=6,
                        random_state=self.random_state,
                        n_jobs=-1,
                        tree_method='hist'
                    )
                else:
                    final_estimator = Ridge(alpha=1.0, random_state=self.random_state)
        
        if self.task == 'classification':
            self.ensemble_model = StackingClassifier(
                estimators=list(self.models.items()),
                final_estimator=final_estimator,
                cv=5,
                n_jobs=-1
            )
        else:
            self.ensemble_model = StackingRegressor(
                estimators=list(self.models.items()),
                final_estimator=final_estimator,
                cv=5,
                n_jobs=-1
            )
    
    def create_mlb_stacking_ensemble(self, final_estimator=None):
        """
        Create MLB-style multi-level stacking ensemble architecture:
        - Base models: Ridge, Lasso, SVR, GradientBoosting
        - Level 1: StackingRegressor with base models + XGBoost meta-learner
        - Level 2: VotingRegressor with base models
        - Level 3: StackingRegressor with Level 1 and Level 2 + XGBoost final meta-learner
        
        This is the architecture from the MLB training.py file
        """
        if self.task == 'classification':
            raise ValueError("MLB architecture currently only supports regression")
        
        # Always create base models (MLB-style) - reset if needed
        # Check if models exist and have the right keys for MLB architecture
        if not self.models or 'ridge' not in self.models:
            self.create_base_models_mlb_style()
        
        # XGBoost parameters (MLB-style)
        if XGBOOST_AVAILABLE:
            xgb_params = {
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6,
                'random_state': self.random_state,
                'n_jobs': -1,
                'tree_method': 'hist'
            }
            meta_model = XGBRegressor(**xgb_params)
            final_meta_model = XGBRegressor(**xgb_params)
        else:
            # Fallback to Ridge if XGBoost not available
            meta_model = Ridge(alpha=1.0, random_state=self.random_state)
            final_meta_model = Ridge(alpha=1.0, random_state=self.random_state)
            print("Warning: XGBoost not available. Using Ridge as meta-learner instead.")
        
        # Level 1: StackingRegressor with base models
        # Ensure we have all required models
        required_keys = ['ridge', 'lasso', 'svr', 'gradient_boosting']
        for key in required_keys:
            if key not in self.models:
                raise ValueError(f"Required model '{key}' not found. Call create_base_models_mlb_style() first.")
        
        base_models_list = [
            ('ridge', self.models['ridge']),
            ('lasso', self.models['lasso']),
            ('svr', self.models['svr']),
            ('gb', self.models['gradient_boosting'])
        ]
        
        stacking_model = StackingRegressor(
            estimators=base_models_list,
            final_estimator=meta_model,
            cv=5,
            n_jobs=-1
        )
        
        # Level 2: VotingRegressor with base models
        voting_model = VotingRegressor(
            estimators=base_models_list,
            n_jobs=-1
        )
        
        # Level 3: Final StackingRegressor combining Level 1 and Level 2
        ensemble_models = [
            ('stacking', stacking_model),
            ('voting', voting_model)
        ]
        
        self.ensemble_model = StackingRegressor(
            estimators=ensemble_models,
            final_estimator=final_meta_model,
            cv=5,
            n_jobs=-1
        )
    
    def prepare_target(self, df, forward_periods=1, threshold=0.02):
        """
        Create target variable for prediction
        
        Args:
            df: DataFrame with price data
            forward_periods: Number of periods to look ahead
            threshold: Minimum return threshold for classification (if task='classification')
        
        Returns:
            Target array
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain 'close' column")
        
        # Calculate forward returns
        forward_returns = df['close'].shift(-forward_periods) / df['close'] - 1
        
        if self.task == 'classification':
            # Binary classification: 1 if return > threshold, 0 otherwise
            target = (forward_returns > threshold).astype(int)
        else:
            # Regression: predict actual returns
            target = forward_returns
        
        # Remove NaN values
        valid_mask = ~target.isna()
        return target[valid_mask], valid_mask
    
    def prepare_features(self, df, select_top_n=None):
        """
        Prepare features for training
        
        Args:
            df: DataFrame with features
            select_top_n: If provided, select top N features by importance (None = use all features)
        
        Returns:
            Feature matrix X
        """
        # Select feature columns (exclude price/volume raw columns)
        feature_cols = [col for col in df.columns if col not in 
                       ['open', 'high', 'low', 'close', 'volume', 'returns', 'log_returns']]
        
        if not feature_cols:
            raise ValueError("No feature columns found")
        
        self.feature_names = feature_cols
        X = df[feature_cols].values
        
        return X
    
    def select_top_features(self, X, y, n_features=50, method='importance'):
        """
        Select top N features based on importance
        
        Args:
            X: Feature matrix
            y: Target vector
            n_features: Number of top features to select
            method: 'importance' (use Random Forest) or 'mutual_info' (mutual information)
        
        Returns:
            X_selected: Selected features
            selected_feature_names: Names of selected features
        """
        if n_features is None or n_features >= X.shape[1]:
            # Use all features
            self.selected_feature_indices = None
            return X, self.feature_names
        
        print(f"   Selecting top {n_features} features from {X.shape[1]} total features...")
        
        if method == 'importance':
            # Use Random Forest feature importance
            if self.task == 'classification':
                from sklearn.ensemble import RandomForestClassifier
                selector_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_leaf=5,
                    random_state=self.random_state,
                    n_jobs=-1
                )
            else:
                from sklearn.ensemble import RandomForestRegressor
                selector_model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_leaf=5,
                    random_state=self.random_state,
                    n_jobs=-1
                )
            
            # Fit to get feature importance (Random Forest doesn't need scaling)
            selector_model.fit(X, y)
            
            # Get feature importances
            importances = selector_model.feature_importances_
            
            # Select top N features
            top_indices = np.argsort(importances)[-n_features:][::-1]  # Sort descending, take top N
            
            # Store selected indices
            self.selected_feature_indices = top_indices
            
        elif method == 'mutual_info':
            # Use mutual information
            from sklearn.feature_selection import SelectKBest, mutual_info_regression, mutual_info_classif
            
            if self.task == 'classification':
                selector = SelectKBest(mutual_info_classif, k=n_features)
            else:
                selector = SelectKBest(mutual_info_regression, k=n_features)
            
            X_selected = selector.fit_transform(X, y)
            self.feature_selector = selector
            self.selected_feature_indices = selector.get_support(indices=True)
            
            # Get selected feature names
            selected_feature_names = [self.feature_names[i] for i in self.selected_feature_indices]
            return X_selected, selected_feature_names
        
        # For importance method
        X_selected = X[:, self.selected_feature_indices]
        selected_feature_names = [self.feature_names[i] for i in self.selected_feature_indices]
        
        # Update feature names to selected ones
        self.feature_names = selected_feature_names
        
        print(f"   Selected features (top {len(selected_feature_names)}):")
        for i, name in enumerate(selected_feature_names[:10]):  # Show top 10
            print(f"     {i+1}. {name}")
        if len(selected_feature_names) > 10:
            print(f"     ... and {len(selected_feature_names) - 10} more")
        
        return X_selected, selected_feature_names
    
    def fit(self, X, y, use_ensemble='voting', use_mlb_architecture=False):
        """
        Train the ensemble model
        
        Args:
            X: Feature matrix
            y: Target vector
            use_ensemble: 'voting', 'stacking', 'mlb', or 'individual'
            use_mlb_architecture: Use MLB-style multi-level stacking (only for regression)
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply SMOTE if enabled (only for classification)
        if self.use_smote and self.task == 'classification':
            print("   Applying SMOTE oversampling...")
            X_scaled, y = self.smote.fit_resample(X_scaled, y)
            print(f"   After SMOTE: {len(X_scaled)} samples, {y.sum()} positive ({y.mean():.2%})")
        
        if use_ensemble == 'mlb' or use_mlb_architecture:
            if self.task != 'regression':
                raise ValueError("MLB architecture only supports regression. Use 'stacking' or 'voting' for classification.")
            print("   Using MLB-style multi-level stacking architecture...")
            self.create_stacking_ensemble(use_mlb_architecture=True)
            self.ensemble_model.fit(X_scaled, y)
        elif use_ensemble == 'voting':
            self.create_voting_ensemble()
            self.ensemble_model.fit(X_scaled, y)
        elif use_ensemble == 'stacking':
            self.create_stacking_ensemble(use_mlb_architecture=False)
            self.ensemble_model.fit(X_scaled, y)
        else:  # individual models
            self.create_base_models()
            for name, model in self.models.items():
                print(f"Training {name}...")
                model.fit(X_scaled, y)
        
        self.is_fitted = True
    
    def predict(self, X):
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Select features if feature selection was used
        # Only apply selection if X has more features than selected (i.e., not already selected)
        if self.selected_feature_indices is not None and X.shape[1] > len(self.selected_feature_indices):
            X = X[:, self.selected_feature_indices]
        
        X_scaled = self.scaler.transform(X)
        
        if self.ensemble_model is not None:
            if self.task == 'classification':
                return self.ensemble_model.predict_proba(X_scaled)[:, 1]  # Probability of positive class
            else:
                return self.ensemble_model.predict(X_scaled)
        else:
            # Average predictions from individual models
            predictions = []
            for name, model in self.models.items():
                if self.task == 'classification':
                    pred = model.predict_proba(X_scaled)[:, 1]
                else:
                    pred = model.predict(X_scaled)
                predictions.append(pred)
            
            return np.mean(predictions, axis=0)
    
    def evaluate(self, X, y, threshold=0.5, show_pr_curve=False):
        """
        Evaluate model performance
        
        Args:
            X: Feature matrix
            y: Target vector
            threshold: Decision threshold for binary classification
            show_pr_curve: Whether to print precision-recall curve info
        """
        predictions = self.predict(X)
        
        if self.task == 'classification':
            # Convert probabilities to binary predictions
            binary_pred = (predictions > threshold).astype(int)
            accuracy = accuracy_score(y, binary_pred)
            
            # Calculate various metrics
            try:
                auc = roc_auc_score(y, predictions)
            except ValueError:
                auc = None  # Can't calculate if only one class present
            
            # Precision-Recall metrics
            ap_score = average_precision_score(y, predictions)
            
            print(f"Accuracy: {accuracy:.4f}")
            if auc is not None:
                print(f"AUC-ROC: {auc:.4f}")
            print(f"Average Precision (AP): {ap_score:.4f}")
            print(f"Decision Threshold: {threshold:.2f}")
            
            if show_pr_curve:
                precision, recall, thresholds_pr = precision_recall_curve(y, predictions)
                print(f"\nPrecision-Recall Curve:")
                print(f"  Optimal threshold (F1): {thresholds_pr[np.argmax(2 * precision * recall / (precision + recall + 1e-10))]:.4f}")
            
            print("\nClassification Report:")
            print(classification_report(y, binary_pred, zero_division=0))
            
            print("\nConfusion Matrix:")
            print(confusion_matrix(y, binary_pred))
            
            return {
                'accuracy': accuracy, 
                'auc': auc, 
                'ap_score': ap_score,
                'precision': precision if show_pr_curve else None,
                'recall': recall if show_pr_curve else None
            }
        else:
            # Regression metrics
            mse = mean_squared_error(y, predictions)
            r2 = r2_score(y, predictions)
            mae = mean_absolute_error(y, predictions)
            rmse = np.sqrt(mse)
            
            print(f"RMSE (Root Mean Squared Error): {rmse:.6f}")
            print(f"MAE (Mean Absolute Error): {mae:.6f}")
            print(f"R² Score: {r2:.4f}")
            print(f"MSE (Mean Squared Error): {mse:.8f}")
            
            # Additional statistics
            print(f"\nPrediction Statistics:")
            print(f"  Mean predicted return: {predictions.mean():.6f}")
            print(f"  Mean actual return: {y.mean():.6f}")
            print(f"  Std predicted return: {predictions.std():.6f}")
            print(f"  Std actual return: {y.std():.6f}")
            
            return {'rmse': rmse, 'mae': mae, 'r2': r2, 'mse': mse}
    
    def get_feature_importance(self, model_name='random_forest'):
        """
        Get feature importance from a model
        
        Args:
            model_name: Name of the model to get importance from
            
        Returns:
            DataFrame with feature importances or None
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting feature importance")
        
        # If using ensemble, try to access the underlying models
        if self.ensemble_model is not None:
            if hasattr(self.ensemble_model, 'estimators_'):
                # Voting or Stacking ensemble - access individual estimators
                estimators = self.ensemble_model.estimators_
                if model_name in [est[0] for est in self.ensemble_model.estimators]:
                    # Find the estimator
                    for name, est in self.ensemble_model.estimators:
                        if name == model_name:
                            model = est
                            break
                else:
                    # Default to first estimator that has feature_importances_
                    for name, est in self.ensemble_model.estimators:
                        if hasattr(est, 'feature_importances_'):
                            model = est
                            break
                    else:
                        return None
            elif hasattr(self.ensemble_model, 'named_estimators_'):
                # Try named_estimators_ attribute
                if model_name in self.ensemble_model.named_estimators_:
                    model = self.ensemble_model.named_estimators_[model_name]
                else:
                    return None
            else:
                # Fall back to individual models dictionary
                if model_name in self.models:
                    model = self.models[model_name]
                else:
                    return None
        else:
            # Using individual models
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            model = self.models[model_name]
        
        # Extract feature importance
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            if self.feature_names:
                importance_df = pd.DataFrame({
                    'feature': self.feature_names,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                return importance_df
            return importance
        return None
    
    def cross_validate(self, X, y, cv_folds=5, use_time_series=True, use_stratified=False):
        """
        Perform cross-validation
        
        Args:
            X: Feature matrix
            y: Target vector
            cv_folds: Number of CV folds
            use_time_series: Use TimeSeriesSplit for time series data (recommended for financial data)
            use_stratified: Use stratified k-fold for classification (only if use_time_series=False)
            
        Returns:
            Dictionary with CV results
        """
        X_scaled = self.scaler.fit_transform(X)
        
        # Use TimeSeriesSplit for time series data (recommended for financial/time series data)
        if use_time_series:
            cv = TimeSeriesSplit(n_splits=cv_folds)
            scoring = ['accuracy', 'roc_auc'] if self.task == 'classification' else ['r2', 'neg_mean_squared_error']
            print(f"   Using TimeSeriesSplit with {cv_folds} folds (recommended for time series data)")
        elif self.task == 'classification' and use_stratified:
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
            scoring = ['accuracy', 'roc_auc', 'precision', 'recall', 'f1']
        else:
            from sklearn.model_selection import KFold
            cv = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
            scoring = ['accuracy', 'roc_auc'] if self.task == 'classification' else ['r2', 'neg_mean_squared_error']
        
        # Create base models if not already created
        # For MLB architecture, we need to check if models exist
        if not self.models or ('random_forest' not in self.models and 'ridge' not in self.models):
            # Use appropriate base models based on architecture
            if hasattr(self, 'ensemble_model') and self.ensemble_model is not None:
                # If we're using MLB architecture, we need Ridge-based models
                # For CV, we'll use a simple Random Forest or Ridge
                if self.task == 'classification':
                    from sklearn.ensemble import RandomForestClassifier
                    estimator = RandomForestClassifier(
                        n_estimators=100,
                        max_depth=15,
                        random_state=self.random_state,
                        n_jobs=-1
                    )
                else:
                    from sklearn.linear_model import Ridge
                    estimator = Ridge(alpha=1.0, random_state=self.random_state)
            else:
                # Original architecture - use Random Forest
                if 'random_forest' not in self.models:
                    self.create_base_models()
                estimator = self.models.get('random_forest')
                if estimator is None:
                    # Fallback to Ridge if Random Forest not available
                    if self.task == 'classification':
                        from sklearn.linear_model import LogisticRegression
                        estimator = LogisticRegression(random_state=self.random_state)
                    else:
                        estimator = Ridge(alpha=1.0, random_state=self.random_state)
        else:
            # Use existing model
            if 'random_forest' in self.models:
                estimator = self.models['random_forest']
            elif 'ridge' in self.models:
                estimator = self.models['ridge']
            else:
                # Fallback
                if self.task == 'classification':
                    from sklearn.linear_model import LogisticRegression
                    estimator = LogisticRegression(random_state=self.random_state)
                else:
                    estimator = Ridge(alpha=1.0, random_state=self.random_state)
        
        results = cross_validate(
            estimator, X_scaled, y,
            cv=cv,
            scoring=scoring,
            return_train_score=True,
            n_jobs=-1
        )
        
        cv_type = "TimeSeriesSplit" if use_time_series else ("StratifiedKFold" if use_stratified else "KFold")
        print(f"\nCross-Validation Results ({cv_folds} folds, {cv_type}):")
        print("-" * 60)
        for metric in scoring:
            test_scores = results[f'test_{metric}']
            train_scores = results[f'train_{metric}']
            print(f"{metric}:")
            print(f"  Train: {train_scores.mean():.4f} (+/- {train_scores.std() * 2:.4f})")
            print(f"  Test:  {test_scores.mean():.4f} (+/- {test_scores.std() * 2:.4f})")
        
        return results


def main():
    """Example usage"""
    print("Ensemble Trading Model")
    print("=" * 60)
    
    # Check if credentials are loaded
    app_key = os.getenv('app_key')
    app_secret = os.getenv('app_secret')
    
    if not app_key or not app_secret:
        print("\nERROR: Missing credentials in .env file")
        print("Please make sure you have:")
        print("  - app_key=YOUR_KEY")
        print("  - app_secret=YOUR_SECRET")
        print("  - callback_url=https://127.0.0.1")
        print("\nRun: python3 setup_schwab.py")
        return
    
    # Initialize Schwab client
    print("\n1. Initializing Schwab API client...")
    try:
        client = schwabdev.Client(
            app_key,
            app_secret,
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        print("   ✓ Client initialized successfully")
    except Exception as e:
        print(f"   ✗ Error initializing client: {e}")
        return
    
    # Initialize data fetcher
    print("2. Fetching data...")
    fetcher = SchwabDataFetcher(client)
    
    # Fetch price data for a symbol (30-minute bars for 6 months)
    symbol = 'AAPL'
    print(f"   Fetching 6 months of 30-minute bar data for {symbol}...")
    print(f"   Prediction horizon: 30 minutes ahead")
    
    # Fetch 6 months of 30-minute bars using periodType='month'
    df = fetcher.get_extended_intraday_data(symbol, months=6, frequency=30)
    
    if df is None or len(df) == 0:
        print(f"   Error: Could not fetch data for {symbol}")
        return
    
    if len(df) < 100:
        print(f"   Warning: Only {len(df)} data points available (recommended: 100+)")
        print(f"   Note: This is the maximum available due to API limitations.")
        print(f"   Proceeding with available data...")
    else:
        print(f"   ✓ Successfully retrieved {len(df)} data points")
    
    # Create features
    print("3. Creating features...")
    features_df = fetcher.create_features(df)
    
    if features_df is None or len(features_df) < 50:
        print("Insufficient data after feature engineering")
        return
    
    print(f"   Created {len(features_df.columns)} features")
    
    # Initialize model for regression (price prediction)
    print("4. Initializing ensemble model...")
    print("   Task: Regression (predicting actual returns)")
    print("   Timeframe: 30-minute bars, predicting 30 minutes ahead")
    model = EnsembleTradingModel(
        task='regression',  # Changed to regression for price prediction
        random_state=42,
        use_class_weight=False,  # Not applicable for regression
        use_smote=False  # Not applicable for regression
    )
    
    # Prepare target for regression (actual forward returns)
    print("5. Preparing target variable...")
    print("   Predicting forward returns (regression)")
    print("   Prediction horizon: 30 minutes ahead (1 period of 30-min bars)")
    target, valid_mask = model.prepare_target(features_df, forward_periods=1)
    features_df_valid = features_df[valid_mask]
    
    # Prepare features
    X = model.prepare_features(features_df_valid)
    y = target.values
    
    # Use TimeSeriesSplit for time series data (avoid data leakage)
    # For time series, we should use chronological split, not random split
    print("\n6. Splitting data (TimeSeriesSplit for time series data)...")
    split_idx = int(len(X) * 0.8)
    X_train_full = X[:split_idx]
    X_test_full = X[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]
    print(f"   Training set: {len(X_train_full)} samples (first 80%)")
    print(f"   Test set: {len(X_test_full)} samples (last 20%)")
    print(f"   Note: Using chronological split (not random) to avoid data leakage")
    
    # Select top N features on training data only (recommended: 30-50 features for better performance)
    print("\n7. Feature selection...")
    print("-" * 60)
    n_features = 50  # Select top 50 features (adjust as needed)
    X_train, selected_feature_names = model.select_top_features(X_train_full, y_train, n_features=n_features, method='importance')
    
    # Apply same feature selection to test data
    if model.selected_feature_indices is not None:
        X_test = X_test_full[:, model.selected_feature_indices]
    else:
        X_test = X_test_full
    
    print(f"\n   Training set: {len(X_train)} samples, {X_train.shape[1]} features")
    print(f"   Test set: {len(X_test)} samples, {X_test.shape[1]} features")
    print(f"   Target statistics:")
    print(f"     Training - Mean: {y_train.mean():.4f}, Std: {y_train.std():.4f}, Min: {y_train.min():.4f}, Max: {y_train.max():.4f}")
    print(f"     Test - Mean: {y_test.mean():.4f}, Std: {y_test.std():.4f}, Min: {y_test.min():.4f}, Max: {y_test.max():.4f}")
    
    # Perform cross-validation using TimeSeriesSplit (recommended for time series)
    print("\n8. Performing cross-validation (TimeSeriesSplit)...")
    print("-" * 60)
    cv_results = model.cross_validate(X_train, y_train, cv_folds=5, use_time_series=True)
    
    # Train model with MLB-style multi-level stacking ensemble (best architecture)
    print("\n9. Training MLB-style multi-level stacking ensemble...")
    model.fit(X_train, y_train, use_ensemble='mlb', use_mlb_architecture=True)
    
    # Evaluate
    print("\n10. Evaluating on test set...")
    print("-" * 60)
    test_results = model.evaluate(X_test, y_test)
    
    # Feature importance - try to get from ensemble or train individual model
    print("\n11. Feature importance (Random Forest):")
    print("-" * 60)
    importance_df = model.get_feature_importance('random_forest')
    if importance_df is not None:
        print(importance_df.head(15).to_string(index=False))
    else:
        # If ensemble doesn't expose it, train a separate Random Forest
        print("   Feature importance not available from ensemble.")
        print("   Training separate Random Forest model for feature importance...")
        if model.task == 'classification':
            from sklearn.ensemble import RandomForestClassifier
            rf_standalone = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_leaf=5,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            )
        else:
            from sklearn.ensemble import RandomForestRegressor
            rf_standalone = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            )
        X_train_scaled = model.scaler.transform(X_train)
        rf_standalone.fit(X_train_scaled, y_train)
        
        if model.feature_names:
            importance_df = pd.DataFrame({
                'feature': model.feature_names,
                'importance': rf_standalone.feature_importances_
            }).sort_values('importance', ascending=False)
            print(importance_df.head(15).to_string(index=False))
        else:
            print("   Could not retrieve feature names")
    
    print("\n" + "=" * 60)
    print("Model training complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

