# AI Agent Implementation Prompt

## 🎯 Mission Statement

You are an AI agent tasked with implementing an advanced ML-based trading system that combines momentum scanning, multi-timeframe predictions, ensemble learning, and risk modeling to generate automated buy/sell signals.

---

## 📋 Context & Existing Infrastructure

### What Already Exists:
1. **Momentum Scanner** (`momentum_scanner.py`)
   - Scans 1,453 stocks from Schwab API
   - Calculates RSI, RVOL, % Change, Volume
   - Scores each stock (0-100) based on momentum
   - Outputs JSON with top 30-50 candidates

2. **Schwab API Integration** (`schwabdev` library)
   - Real-time quotes via `client.quotes()`
   - Historical data via `client.price_history()`
   - WebSocket streaming for live updates
   - Order execution capabilities

3. **Frontend Dashboard** (Next.js/React)
   - Trading view with live charts
   - Momentum Scanner tab (full-page view)
   - Order ticket & position management
   - Real-time WebSocket updates

4. **Backend Server** (Node.js/Express)
   - API endpoints for data fetching
   - Calls Python scripts via `child_process.spawn`
   - Serves frontend and handles requests

---

## 🎯 Your Task: Build the ML Trading Pipeline

### High-Level Objective:
Create a **7-stage pipeline** that takes momentum scanner output and produces BUY/SELL signals with confidence scores.

---

## 📐 Stage-by-Stage Implementation Guide

### **STAGE 1: Momentum Filtering** ✅ (Already Exists)
**Status:** Complete  
**What it does:** Scans 1,453 stocks → Outputs 30-50 top candidates  
**Your action:** Use existing `momentum_scanner.py` output as input

---

### **STAGE 2: Multi-Timeframe Data Collection**

**Objective:** For each candidate stock, fetch historical data for 6 timeframes

**Implementation:**
```python
# File: ml_trading/data/fetcher.py

class MultiTimeframeDataFetcher:
    def __init__(self, schwab_client):
        self.client = schwab_client
        self.timeframes = {
            '1m': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 1},
            '5m': {'periodType': 'day', 'period': 2, 'frequencyType': 'minute', 'frequency': 5},
            '30m': {'periodType': 'day', 'period': 5, 'frequencyType': 'minute', 'frequency': 30},
            '1h': {'periodType': 'day', 'period': 10, 'frequencyType': 'minute', 'frequency': 60},
            '6h': {'periodType': 'month', 'period': 1, 'frequencyType': 'daily', 'frequency': 1},  # Resample
            '1d': {'periodType': 'year', 'period': 1, 'frequencyType': 'daily', 'frequency': 1}
        }
    
    def fetch_all_timeframes(self, symbol):
        """Fetch data for all 6 timeframes for a given symbol"""
        data = {}
        for tf_name, params in self.timeframes.items():
            df = self._fetch_timeframe(symbol, params)
            data[tf_name] = df
        return data
    
    def _fetch_timeframe(self, symbol, params):
        """Fetch single timeframe data from Schwab API"""
        response = self.client.price_history(symbol, **params)
        # Parse response, convert to pandas DataFrame
        # Columns: timestamp, open, high, low, close, volume
        return df
```

**Deliverables:**
- [ ] `fetcher.py` - Fetch OHLCV data for 6 timeframes
- [ ] Handle API rate limits (batch requests, delays)
- [ ] Cache data locally to avoid redundant API calls
- [ ] Return consistent pandas DataFrames

---

### **STAGE 3: Feature Engineering**

**Objective:** Calculate 80-100 features for each stock

**Implementation:**
```python
# File: ml_trading/data/feature_engineer.py

class FeatureEngineer:
    def __init__(self):
        self.features = []
    
    def engineer_features(self, ohlcv_data, momentum_data):
        """
        Generate all features for a stock
        
        Args:
            ohlcv_data: dict of DataFrames (6 timeframes)
            momentum_data: dict from momentum scanner
        
        Returns:
            feature_vector: numpy array of ~80-100 features
        """
        features = {}
        
        # 1. Technical Indicators (50+ features)
        features.update(self._calculate_technical_indicators(ohlcv_data))
        
        # 2. Price Statistics (10 features)
        features.update(self._calculate_price_statistics(ohlcv_data))
        
        # 3. Volume Analysis (10 features)
        features.update(self._calculate_volume_features(ohlcv_data))
        
        # 4. Momentum Scores (5 features)
        features.update({
            'momentum_score': momentum_data['score'],
            'rsi': momentum_data['rsi'],
            'rvol': momentum_data['rvol'],
            'percent_change': momentum_data['percentChange'],
            'trend': 1 if momentum_data['trend'] == 'strong' else 0
        })
        
        return pd.Series(features)
    
    def _calculate_technical_indicators(self, ohlcv_data):
        """Calculate RSI, MACD, Bollinger Bands, ATR, etc."""
        indicators = {}
        
        # Use most recent timeframe (1d) for technical indicators
        df = ohlcv_data['1d']
        
        # Trend Indicators
        indicators['sma_5'] = df['close'].rolling(5).mean().iloc[-1]
        indicators['sma_20'] = df['close'].rolling(20).mean().iloc[-1]
        indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1]
        indicators['macd'] = self._calculate_macd(df)
        
        # Momentum Indicators
        indicators['rsi_14'] = self._calculate_rsi(df, 14)
        indicators['stoch_k'] = self._calculate_stochastic(df)
        indicators['roc'] = self._calculate_roc(df)
        
        # Volatility Indicators
        indicators['atr_14'] = self._calculate_atr(df, 14)
        indicators['bb_upper'], indicators['bb_lower'] = self._calculate_bollinger(df)
        
        # Volume Indicators
        indicators['obv'] = self._calculate_obv(df)
        indicators['volume_sma'] = df['volume'].rolling(20).mean().iloc[-1]
        
        return indicators
```

**Deliverables:**
- [ ] `feature_engineer.py` - Generate 80-100 features per stock
- [ ] Use `ta-lib` or `pandas_ta` for technical indicators
- [ ] Normalize/scale features for ML models
- [ ] Handle missing values gracefully

---

### **STAGE 4: Multi-Timeframe ML Predictions**

**Objective:** Train/use 6 separate ML models (one per timeframe) to predict future prices

**Implementation:**
```python
# File: ml_trading/models/timeframe_predictor.py

import torch
import torch.nn as nn

class LSTMPredictor(nn.Module):
    def __init__(self, input_size=50, hidden_size=128, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)  # Predict next price
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        prediction = self.fc(lstm_out[:, -1, :])
        return prediction

class MultiTimeframePredictor:
    def __init__(self):
        self.models = {
            '1m': self._load_model('trained_models/lstm_1m.pth'),
            '5m': self._load_model('trained_models/lstm_5m.pth'),
            '30m': self._load_model('trained_models/lstm_30m.pth'),
            '1h': self._load_model('trained_models/lstm_1h.pth'),
            '6h': self._load_model('trained_models/lstm_6h.pth'),
            '1d': self._load_model('trained_models/lstm_1d.pth'),
        }
    
    def predict_all_timeframes(self, ohlcv_data):
        """
        Predict future price for all 6 timeframes
        
        Returns:
            predictions: dict with keys '1m', '5m', etc.
                         values are predicted prices + confidence
        """
        predictions = {}
        for tf_name, model in self.models.items():
            data = ohlcv_data[tf_name]
            pred_price, confidence = self._predict_single_timeframe(model, data)
            predictions[tf_name] = {
                'predicted_price': pred_price,
                'confidence': confidence,
                'current_price': data['close'].iloc[-1],
                'expected_return': (pred_price / data['close'].iloc[-1] - 1) * 100
            }
        return predictions
```

**Deliverables:**
- [ ] `timeframe_predictor.py` - LSTM/GRU models for each timeframe
- [ ] Training script (`train_models.py`) - Train on historical data
- [ ] Saved model files (`.pth` or `.pkl`) for each timeframe
- [ ] Prediction function that outputs price + confidence

**Model Training Requirements:**
- Use 2+ years of historical data
- Train separately for each timeframe
- Features: OHLCV + 50 technical indicators (100 bars lookback)
- Target: Next period's close price
- Loss: MSE or Huber Loss
- Validation: Walk-forward split (80/20)

---

### **STAGE 5: Risk Modeling (GARCH + Copula)**

**Objective:** Model volatility and correlation for risk assessment

**Implementation:**
```python
# File: ml_trading/models/garch_model.py

from arch import arch_model

class GARCHVolatilityModel:
    def __init__(self):
        self.models = {}  # Cache fitted models per symbol
    
    def forecast_volatility(self, returns, horizon=5):
        """
        Forecast future volatility using GARCH(1,1)
        
        Args:
            returns: pandas Series of historical returns
            horizon: number of periods ahead to forecast
        
        Returns:
            forecast_vol: forecasted volatility
            confidence_interval: (lower, upper) bounds
        """
        model = arch_model(returns, vol='Garch', p=1, q=1)
        fitted = model.fit(disp='off')
        forecast = fitted.forecast(horizon=horizon)
        
        forecast_vol = forecast.variance.iloc[-1].mean() ** 0.5
        return {
            'forecast_volatility': forecast_vol,
            'annualized_vol': forecast_vol * (252 ** 0.5),  # Annualize
            'current_vol': returns.std(),
            'vol_regime': 'high' if forecast_vol > returns.std() * 1.5 else 'normal'
        }


# File: ml_trading/models/copula_model.py

from copulas.multivariate import GaussianMultivariate

class CopulaCorrelationModel:
    def __init__(self):
        self.copula = None
    
    def fit_and_analyze(self, stock_returns, spy_returns, qqq_returns):
        """
        Fit copula to model joint distribution
        
        Returns:
            correlation_metrics: dict with correlation & tail dependence
        """
        data = pd.DataFrame({
            'stock': stock_returns,
            'spy': spy_returns,
            'qqq': qqq_returns
        })
        
        copula = GaussianMultivariate()
        copula.fit(data)
        
        # Generate scenarios and calculate metrics
        correlation_matrix = data.corr()
        tail_dependence = self._calculate_tail_dependence(data)
        
        return {
            'correlation_spy': correlation_matrix.loc['stock', 'spy'],
            'correlation_qqq': correlation_matrix.loc['stock', 'qqq'],
            'tail_dependence_lower': tail_dependence['lower'],
            'tail_dependence_upper': tail_dependence['upper'],
            'diversification_benefit': 1 - abs(correlation_matrix.loc['stock', 'spy'])
        }
```

**Deliverables:**
- [ ] `garch_model.py` - GARCH volatility forecasting
- [ ] `copula_model.py` - Copula correlation analysis
- [ ] Output 8 risk features per stock
- [ ] Use `arch` and `copulas` Python libraries

---

### **STAGE 6: Ensemble Classifier (Final Decision)**

**Objective:** Combine all features + predictions → BUY/SELL/HOLD decision

**Implementation:**
```python
# File: ml_trading/models/ensemble_classifier.py

from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import joblib

class EnsembleTradeClassifier:
    def __init__(self):
        # Load pre-trained base models
        self.rf = joblib.load('trained_models/random_forest.pkl')
        self.xgb = joblib.load('trained_models/xgboost.pkl')
        self.lgbm = joblib.load('trained_models/lightgbm.pkl')
        self.nn = joblib.load('trained_models/neural_net.pkl')
        self.svm = joblib.load('trained_models/svm.pkl')
        
        # Meta-learner (stacking)
        self.meta_model = joblib.load('trained_models/meta_learner.pkl')
    
    def predict(self, features):
        """
        Predict BUY/SELL/HOLD with confidence
        
        Args:
            features: dict with ~100 features:
                - 6 predicted prices (from Stage 4)
                - 50 technical indicators
                - 8 risk metrics (from Stage 5)
                - 5 momentum scores
                - etc.
        
        Returns:
            decision: 'BUY', 'SELL', or 'HOLD'
            confidence: 0.0 - 1.0
            expected_return: estimated % return
            risk_score: 1-10
        """
        # Convert features to array
        X = self._prepare_features(features)
        
        # Get predictions from all base models
        rf_pred = self.rf.predict_proba(X)[0]
        xgb_pred = self.xgb.predict_proba(X)[0]
        lgbm_pred = self.lgbm.predict_proba(X)[0]
        nn_pred = self.nn.predict_proba(X)[0]
        svm_pred = self.svm.predict_proba(X)[0]
        
        # Stack predictions and feed to meta-learner
        stacked = np.column_stack([rf_pred, xgb_pred, lgbm_pred, nn_pred, svm_pred])
        final_pred = self.meta_model.predict_proba(stacked)[0]
        
        # Map to BUY/SELL/HOLD
        decision_idx = np.argmax(final_pred)
        decisions = ['SELL', 'HOLD', 'BUY']
        decision = decisions[decision_idx]
        confidence = final_pred[decision_idx]
        
        # Calculate expected return (weighted avg of timeframe predictions)
        expected_return = self._calculate_expected_return(features)
        
        # Calculate risk score (from GARCH/Copula features)
        risk_score = self._calculate_risk_score(features)
        
        # Apply decision rules
        if confidence < 0.7 or risk_score > 6:
            decision = 'HOLD'
        
        return {
            'decision': decision,
            'confidence': float(confidence),
            'expected_return': expected_return,
            'risk_score': risk_score,
            'time_horizon': self._recommend_time_horizon(features)
        }
```

**Deliverables:**
- [ ] `ensemble_classifier.py` - Final BUY/SELL decision model
- [ ] Training script for ensemble (historical trades labeled BUY/SELL)
- [ ] Saved ensemble model files
- [ ] Decision rules (confidence threshold, risk limits)

**Training Requirements:**
- Labels: Historical trades labeled as profitable (BUY) vs unprofitable (SELL)
- Use 80/20 train/test split
- Optimize for F1-score (balance precision/recall)
- Target: >65% accuracy on test set

---

### **STAGE 7: Pipeline Integration & API**

**Objective:** Connect all stages into a single pipeline and expose via API

**Implementation:**
```python
# File: ml_trading/pipeline/full_pipeline.py

class MLTradingPipeline:
    def __init__(self):
        self.data_fetcher = MultiTimeframeDataFetcher(schwab_client)
        self.feature_engineer = FeatureEngineer()
        self.timeframe_predictor = MultiTimeframePredictor()
        self.garch_model = GARCHVolatilityModel()
        self.copula_model = CopulaCorrelationModel()
        self.ensemble_classifier = EnsembleTradeClassifier()
    
    def analyze_stock(self, symbol, momentum_data):
        """
        Run full pipeline for a single stock
        
        Returns:
            signal: dict with decision, confidence, etc.
        """
        # Stage 2: Fetch multi-timeframe data
        ohlcv_data = self.data_fetcher.fetch_all_timeframes(symbol)
        
        # Stage 3: Engineer features
        technical_features = self.feature_engineer.engineer_features(ohlcv_data, momentum_data)
        
        # Stage 4: Multi-timeframe predictions
        predictions = self.timeframe_predictor.predict_all_timeframes(ohlcv_data)
        
        # Stage 5: Risk modeling
        returns = ohlcv_data['1d']['close'].pct_change().dropna()
        vol_forecast = self.garch_model.forecast_volatility(returns)
        correlation = self.copula_model.fit_and_analyze(returns, spy_returns, qqq_returns)
        
        # Combine all features
        all_features = {
            **technical_features,
            **predictions,
            **vol_forecast,
            **correlation
        }
        
        # Stage 6: Ensemble decision
        signal = self.ensemble_classifier.predict(all_features)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            **signal,
            'predictions': predictions,
            'risk_metrics': {**vol_forecast, **correlation}
        }
    
    def process_momentum_candidates(self, momentum_results):
        """
        Process all candidates from momentum scanner
        
        Returns:
            buy_signals: list of BUY signals
            sell_signals: list of SELL signals
        """
        signals = []
        for stock in momentum_results:
            try:
                signal = self.analyze_stock(stock['symbol'], stock)
                signals.append(signal)
            except Exception as e:
                print(f"Error processing {stock['symbol']}: {e}")
        
        # Filter and sort
        buy_signals = [s for s in signals if s['decision'] == 'BUY']
        buy_signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return buy_signals


# File: ml_trading/api/ml_endpoints.py

from flask import Flask, jsonify, request

app = Flask(__name__)
pipeline = MLTradingPipeline()

@app.route('/api/ml/scan', methods=['POST'])
def ml_scan():
    """
    Endpoint: Run full ML pipeline on momentum candidates
    
    Input: JSON from momentum scanner
    Output: Top BUY signals with confidence
    """
    momentum_results = request.json['results']
    
    buy_signals = pipeline.process_momentum_candidates(momentum_results)
    
    return jsonify({
        'signals': buy_signals[:10],  # Top 10
        'total_analyzed': len(momentum_results),
        'buy_count': len(buy_signals),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ml/predict', methods=['POST'])
def predict_single():
    """
    Endpoint: Get prediction for a single stock
    """
    symbol = request.json['symbol']
    momentum_data = request.json.get('momentum_data', {})
    
    signal = pipeline.analyze_stock(symbol, momentum_data)
    
    return jsonify(signal)
```

**Deliverables:**
- [ ] `full_pipeline.py` - Orchestrates all 7 stages
- [ ] `ml_endpoints.py` - Flask/FastAPI REST endpoints
- [ ] Error handling & logging
- [ ] Performance monitoring (timing each stage)

---

## 🎓 Training Data Requirements

### For Multi-Timeframe Predictors (Stage 4):
- **Data:** 2 years of historical OHLCV for all 6 timeframes
- **Symbols:** Train on S&P 500 stocks (500 stocks)
- **Labels:** Next period's close price
- **Validation:** Walk-forward (train on months 1-20, test on 21-24)

### For Ensemble Classifier (Stage 6):
- **Data:** Historical trades from backtesting
- **Features:** All 80-100 features (predictions + indicators + risk)
- **Labels:** Profitable trade = BUY (1), Unprofitable = SELL/HOLD (0)
- **Balance:** Use SMOTE if imbalanced
- **Validation:** Stratified 5-fold cross-validation

---

## 🔧 Tools & Libraries

```python
# requirements.txt

# Data & ML
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.3.0
xgboost==2.0.0
lightgbm==4.0.0
catboost==1.2.0

# Deep Learning
torch==2.0.0
tensorflow==2.13.0

# Time Series & Risk
arch==6.0.0            # GARCH models
copulas==0.9.0         # Copula models
statsmodels==0.14.0

# Technical Indicators
ta-lib==0.4.28
pandas-ta==0.3.14b

# API & Backend
flask==2.3.0
fastapi==0.100.0
celery==5.3.0
redis==4.6.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0
joblib==1.3.0
```

---

## 📊 Success Criteria

Your implementation will be considered successful when:

1. ✅ **Pipeline Runs End-to-End**
   - Momentum scanner → ML predictions → BUY/SELL signals

2. ✅ **Performance Meets Targets**
   - Backtest win rate: >60%
   - Sharpe ratio: >1.2
   - Max drawdown: <20%

3. ✅ **API is Functional**
   - `/api/ml/scan` returns top 10 BUY signals
   - Response time: <30 seconds for 50 stocks

4. ✅ **Models are Trained**
   - 6 timeframe predictors (LSTM/GRU)
   - 1 ensemble classifier
   - GARCH & Copula models fitted

5. ✅ **Code Quality**
   - Modular, well-documented code
   - Unit tests for critical functions
   - Error handling & logging

---

## 🚀 Quick Start Guide

### Step 1: Set Up Environment
```bash
cd /Users/sineshawmesfintesfaye/Schwabdev
mkdir -p ml_trading/{data,models,pipeline,execution,utils,api}
cd ml_trading
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Fetch Training Data
```bash
python scripts/fetch_historical_data.py --symbols SP500 --years 2 --timeframes all
```

### Step 3: Train Models
```bash
python ml_trading/models/train_timeframe_predictors.py
python ml_trading/models/train_ensemble_classifier.py
```

### Step 4: Test Pipeline
```bash
python ml_trading/pipeline/test_pipeline.py --symbol AAPL
```

### Step 5: Start API Server
```bash
python ml_trading/api/ml_endpoints.py
```

### Step 6: Integrate with Frontend
- Call `/api/ml/scan` from Node.js backend
- Display signals in ML Auto Trader tab

---

## 💡 Key Implementation Tips

1. **Start Simple**: 
   - Begin with 1 timeframe (1d), then scale to 6
   - Use XGBoost before LSTM (faster to train)

2. **Cache Everything**:
   - Cache historical data locally
   - Cache model predictions (TTL: 5 minutes)

3. **Handle API Limits**:
   - Batch Schwab API requests (max 50 symbols/request)
   - Add exponential backoff for rate limits

4. **Monitor Performance**:
   - Log all predictions vs actual outcomes
   - Weekly model retraining with new data

5. **Risk Management First**:
   - Implement stop-loss before live trading
   - Start with paper trading (no real money)

---

## 📞 Questions & Clarifications

If you need clarification on any step, refer to:
- **Architecture Doc**: `ML_TRADING_ARCHITECTURE.md`
- **Existing Code**: `momentum_scanner.py`, `fetch_stock_data.py`
- **Schwab API Docs**: `docs/pages/api.html`

---

## 🎯 Final Deliverable

At the end of implementation, you should be able to:

1. Run momentum scanner → Get 50 candidates
2. Call `/api/ml/scan` with those 50 candidates
3. Receive top 10 BUY signals with:
   - Confidence score (>0.7)
   - Expected return (e.g., +3.2%)
   - Risk score (1-10)
   - Recommended time horizon (e.g., "1 hour")
4. Display signals in frontend ML Auto Trader tab
5. (Optional) Auto-execute trades based on signals

---

**Good luck! Build something amazing! 🚀**


