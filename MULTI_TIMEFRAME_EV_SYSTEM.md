# Multi-Timeframe Expected Value (EV) Trading System

## 🎯 Overview

This system implements a **meta-learning approach** that combines predictions from multiple timeframes to generate high-confidence trading signals based on Expected Value (EV) calculations.

## 📊 Architecture

### Stage 1: Multi-Timeframe Predictions

Generates predictions on multiple timeframes:
- **1-minute**: Ultra-short-term momentum
- **5-minute**: Short-term trends
- **30-minute**: Intraday patterns
- **1-day**: Daily trends and patterns

Each timeframe prediction uses:
- Technical features (RSI, MACD, Bollinger Bands, etc.)
- Alpha Trader features (35 advanced signals)
- Risk features (GARCH volatility, Copula correlations)
- Ensemble models (Stacking: RF, XGB, LGBM, Neural Net, SVM)

### Stage 2: Meta-Learning Features

**Key Innovation**: Uses predictions from each timeframe as features for the final classifier.

```python
# Example Feature Set for EV Classifier:
Base Features (196):
  - Technical indicators (85)
  - Alpha Trader features (35)
  - Risk features (76: GARCH + Copula)

Multi-Timeframe Features (4):
  + pred_1m: 1-minute prediction
  + pred_5m: 5-minute prediction
  + pred_30m: 30-minute prediction
  + pred_1d: Daily prediction

Total Features: 200
```

### Stage 3: Expected Value (EV) Classification

The EV Classifier trains two models:

#### 1. **Regression Model** (GradientBoosting)
Predicts the expected return for next period:
```
Expected Return = f(features, timeframe_predictions)
```

#### 2. **Classification Model** (Calibrated Random Forest)
Predicts the probability of a profitable trade:
```
Win Probability = P(return > 0 | features, timeframe_predictions)
```

#### 3. **EV Calculation**
```
EV = (Win_Prob × Expected_Win) - (Loss_Prob × Expected_Loss)

Where:
- Win_Prob = from classification model
- Loss_Prob = 1 - Win_Prob
- Expected_Win = max(predicted_return, historical_avg_win)
- Expected_Loss = max(abs(predicted_return), historical_avg_loss)
```

#### 4. **Risk-Adjusted EV**
```
Sharpe_EV = (EV - risk_free_rate) / volatility

Risk_Reward_Ratio = Expected_Return / Historical_Volatility
```

## 🎯 Signal Generation

### BUY Signal
Generated when:
```
EV > min_ev (default: 0.001 = 0.1%)
AND Win_Prob > min_confidence (default: 0.55 = 55%)
AND Expected_Return > 0
```

**Confidence Score**: Based on EV magnitude and win probability

### SELL Signal
Generated when:
```
EV < -min_ev (default: -0.001 = -0.1%)
AND Loss_Prob > min_confidence (default: 0.55 = 55%)
AND Expected_Return < 0
```

**Confidence Score**: Based on negative EV magnitude and loss probability

### HOLD Signal
Generated when:
```
Neither BUY nor SELL conditions are met
```

**Reason**: Insufficient edge or conflicting signals

## 💰 Expected Value Metrics

For each signal, the system provides:

```python
{
  'expected_return': 0.0023,      # 0.23% expected return
  'win_probability': 0.58,        # 58% chance of profit
  'expected_value': 0.0015,       # 0.15% EV
  'sharpe_ev': 0.45,              # Risk-adjusted EV
  'risk_reward_ratio': 1.8        # 1.8:1 risk/reward
}
```

## 🚀 Usage

### Basic Usage

```python
from ml_trading.pipeline.multi_timeframe_system import (
    MultiTimeframePredictor, EVClassifier
)

# 1. Generate multi-timeframe predictions
mtp = MultiTimeframePredictor(
    timeframes=['1m', '5m', '30m', '1d'],
    use_lstm=False
)
predictions = mtp.predict_all_timeframes(fetcher, 'AAPL')

# 2. Train EV classifier with timeframe features
ev_classifier = EVClassifier(
    min_ev=0.001,              # 0.1% minimum EV
    min_confidence=0.55,        # 55% minimum confidence
    use_timeframe_features=True # Use predictions as features
)

# Prepare features and timeframe predictions
X_train, y_train = prepare_data()
tf_predictions_train = get_timeframe_predictions()

ev_classifier.fit(X_train, y_train, 
                  timeframe_predictions=tf_predictions_train)

# 3. Generate signal
signal, confidence, ev_metrics = ev_classifier.predict_signal(
    X_latest,
    timeframe_predictions={'1m': 0.002, '5m': 0.003, '1d': 0.001}
)

print(f"Signal: {signal}")
print(f"Confidence: {confidence*100:.1f}%")
print(f"Expected Value: {ev_metrics['expected_value']*100:.3f}%")
```

### Running the Complete Test

```bash
# Fast test (5m + 1d only)
python test_ev_classifier_system.py AAPL

# Full test (all timeframes)
python test_ev_classifier_system.py AAPL --all

# Test another symbol
python test_ev_classifier_system.py TSLA
```

## 📈 Performance Metrics

The system evaluates performance using:

1. **Expected Value Metrics**
   - Average EV across all signals
   - Average Positive EV (for trades taken)
   
2. **Direction Accuracy**
   - % of BUY signals that were profitable
   - % of SELL signals that were profitable
   
3. **Signal Distribution**
   - Number of BUY/SELL/HOLD signals
   - Win rate for each signal type
   - Average return for each signal type

4. **Risk Metrics**
   - Sharpe EV (risk-adjusted)
   - Risk/Reward ratio
   - Average confidence score

## 🎓 Why This Works

### 1. **Multi-Timeframe Consensus**
Different timeframes capture different market patterns:
- **1m/5m**: Captures momentum and microstructure
- **30m**: Captures intraday trends
- **1d**: Captures daily patterns and sentiment

When all timeframes agree, confidence is higher.

### 2. **Meta-Learning**
Using predictions as features allows the model to learn:
- Which timeframe is most reliable for different market conditions
- How to weight conflicting signals
- Optimal combinations of timeframes

### 3. **Expected Value Focus**
Traditional classifiers maximize accuracy. EV classifiers maximize profitability:
- Only takes trades with positive expected value
- Factors in win rate AND average win/loss
- Risk-adjusted for volatility

### 4. **Calibrated Probabilities**
Uses `CalibratedClassifierCV` to ensure:
- Confidence scores are well-calibrated
- 60% confidence = 60% actual win rate
- Better position sizing decisions

## 🔧 Configuration

### Tunable Parameters

```python
EVClassifier(
    min_ev=0.001,              # Minimum EV to trade
                               # Higher = fewer, higher-quality trades
                               
    min_confidence=0.55,       # Minimum win probability
                               # Higher = more conservative
                               
    risk_free_rate=0.05,       # Annual risk-free rate
                               # Used for Sharpe EV calculation
                               
    use_timeframe_features=True # Use multi-timeframe predictions
                                # False = use base features only
)
```

### Recommended Settings

**Conservative**:
```python
min_ev=0.002,         # 0.2% minimum EV
min_confidence=0.60   # 60% minimum confidence
```

**Balanced** (Default):
```python
min_ev=0.001,         # 0.1% minimum EV
min_confidence=0.55   # 55% minimum confidence
```

**Aggressive**:
```python
min_ev=0.0005,        # 0.05% minimum EV
min_confidence=0.52   # 52% minimum confidence
```

## 📊 Example Output

```
====================================================================================================
STAGE 5: FINAL TRADING SIGNAL (Latest Bar with Live Predictions)
====================================================================================================

   Using predictions from 3 timeframes:
      5m: +0.234%
      1d: +0.123%
      combined: +0.189%

   🎯 SIGNAL: BUY
   📊 Confidence: 67.3%

   💰 Expected Value Analysis:
      Expected Return: +0.189%
      Win Probability: 58.5%
      Expected Value (EV): +0.142%
      Sharpe EV: +0.523
      Risk/Reward Ratio: 1.94

   📋 TRADING RECOMMENDATION:
      ✅ BUY
      Reason: Positive EV detected
```

## 🏆 Advantages Over Traditional Systems

| Feature | Traditional | EV-Based System |
|---------|-------------|-----------------|
| **Prediction** | Single timeframe | Multiple timeframes |
| **Feature Engineering** | Manual | Meta-learning (predictions as features) |
| **Decision Metric** | Accuracy / Threshold | Expected Value |
| **Risk Awareness** | Limited | Sharpe EV, Risk/Reward |
| **Confidence Scores** | Uncalibrated | Calibrated probabilities |
| **Win Rate Focus** | ❌ | ✅ (Win% × Win - Loss% × Loss) |

## 🔮 Future Enhancements

1. **LSTM Integration**: Add LSTM predictions for time series patterns
2. **Adaptive Thresholds**: Adjust `min_ev` based on market volatility
3. **Position Sizing**: Use EV and confidence for Kelly Criterion
4. **Multi-Asset**: Extend to portfolio-level EV optimization
5. **Real-Time Updates**: Continuous prediction updates
6. **Execution Integration**: Connect to actual trading

## 📝 Files

- `ml_trading/pipeline/multi_timeframe_system.py`: Core implementation
- `ml_trading/models/lstm_model.py`: LSTM predictor (optional)
- `test_ev_classifier_system.py`: Complete system test
- `MULTI_TIMEFRAME_EV_SYSTEM.md`: This documentation

## 🎯 Next Steps

1. **Test the system**:
   ```bash
   python test_ev_classifier_system.py AAPL
   ```

2. **Evaluate performance** on multiple symbols

3. **Tune parameters** based on backtesting results

4. **Implement paper trading** to validate in live market

5. **Monitor EV accuracy** vs actual returns

---

**Created**: January 2026  
**Status**: ✅ Complete - Ready for Testing  
**Stage**: STAGE 2 (Multi-Timeframe) + STAGE 5 (Classification) - 100% Complete

