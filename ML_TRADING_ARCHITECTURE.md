# ML Trading System Architecture

**Project:** Automated Multi-Timeframe ML Trading System  
**Date:** January 6, 2026  
**Status:** Architecture & Design Phase  
**Objective:** Integrate momentum scanning with multi-timeframe ML predictions and ensemble modeling

---

## 📋 Executive Summary

This document outlines the architecture for an advanced ML-based trading system that combines momentum scanning, multi-timeframe predictions, ensemble learning, and risk modeling to generate high-confidence buy/sell signals.

### Key Components:
1. **Momentum Scanner** - Identifies top stocks (1,453 stocks → filtered candidates)
2. **Multi-Timeframe ML Pipeline** - Predicts price movements across 6 timeframes
3. **Ensemble Classifier** - Aggregates predictions + features → BUY/SELL/HOLD
4. **Risk Modeling** - GARCH volatility + Copula correlation analysis
5. **Execution Engine** - Automated trade execution with risk management

---

## 🎯 System Objectives

### Primary Goals:
- ✅ **High Accuracy**: >65% win rate through ensemble methods
- ✅ **Risk-Aware**: GARCH volatility & Copula correlation modeling
- ✅ **Multi-Timeframe**: Capture opportunities across 1m to 1d timeframes
- ✅ **Scalable**: Process 50-100 stocks in real-time
- ✅ **Automated**: Minimal human intervention required

### Success Metrics:
- Win Rate: >65%
- Sharpe Ratio: >1.5
- Max Drawdown: <15%
- Avg Trade Duration: 1 hour - 1 day
- ROI: >20% annually

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA INGESTION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Schwab API → Real-time Quotes, Historical Data, Order Book     │
│  WebSocket Stream → Live price updates                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               STAGE 1: MOMENTUM SCREENING                        │
├─────────────────────────────────────────────────────────────────┤
│  Input:  1,453 stocks from comprehensive universe               │
│  Process: • Calculate RSI, RVOL, % Change, Volume              │
│           • Score based on momentum (0-100)                      │
│           • Filter: Score >= 70 (Strong/Moderate momentum)      │
│  Output: 30-50 candidate stocks (top momentum plays)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          STAGE 2: MULTI-TIMEFRAME ML PREDICTIONS                 │
├─────────────────────────────────────────────────────────────────┤
│  For each candidate stock, predict on 6 timeframes:             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Timeframe │ Lookback │ Features              │ Output   │  │
│  ├───────────┼──────────┼───────────────────────┼──────────┤  │
│  │ 1 min     │ 100 bars │ OHLCV + 50 indicators │ Price_1m │  │
│  │ 5 min     │ 100 bars │ OHLCV + 50 indicators │ Price_5m │  │
│  │ 30 min    │ 100 bars │ OHLCV + 50 indicators │ Price_30m│  │
│  │ 1 hour    │ 100 bars │ OHLCV + 50 indicators │ Price_1h │  │
│  │ 6 hour    │ 100 bars │ OHLCV + 50 indicators │ Price_6h │  │
│  │ 1 day     │ 252 bars │ OHLCV + 50 indicators │ Price_1d │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ML Models per Timeframe:                                       │
│  • LSTM (Long Short-Term Memory) - Sequential patterns          │
│  • GRU (Gated Recurrent Unit) - Faster LSTM alternative        │
│  • Transformer - Attention-based predictions                    │
│  • XGBoost - Gradient boosting for tabular features            │
│                                                                  │
│  Output: 6 predicted prices + confidence scores per stock       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            STAGE 3: FEATURE ENGINEERING                          │
├─────────────────────────────────────────────────────────────────┤
│  Aggregate Features for Ensemble Model:                         │
│                                                                  │
│  📊 PRICE PREDICTIONS (6 features):                             │
│     • predicted_price_1m, _5m, _30m, _1h, _6h, _1d             │
│                                                                  │
│  📈 TECHNICAL INDICATORS (50+ features):                        │
│     • Trend: SMA(5,10,20,50,200), EMA(12,26), MACD             │
│     • Momentum: RSI(14), Stochastic, ROC, MFI                   │
│     • Volatility: ATR, Bollinger Bands, Standard Dev           │
│     • Volume: OBV, Volume SMA, VWAP, Volume Ratio              │
│     • Pattern: Support/Resistance, Pivot Points                 │
│                                                                  │
│  💰 FUNDAMENTAL DATA (10 features):                             │
│     • Market Cap, P/E Ratio, Volume, Float, Sector             │
│                                                                  │
│  🎯 MOMENTUM SCORES (5 features):                               │
│     • Momentum Score (0-100), Trend Strength                    │
│     • RVOL (Relative Volume), %Change, RSI                     │
│                                                                  │
│  📉 RISK METRICS (from GARCH/Copula - 8 features):              │
│     • Predicted Volatility (next period)                        │
│     • VaR (Value at Risk) 95%, 99%                              │
│     • CVaR (Conditional VaR)                                    │
│     • Correlation with SPY, QQQ                                 │
│     • Beta, Sharpe Ratio                                        │
│                                                                  │
│  TOTAL FEATURES: ~80-100 per stock                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          STAGE 4: RISK MODELING (GARCH + COPULA)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  A. GARCH VOLATILITY MODELING                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Purpose: Predict future volatility for risk assessment   │  │
│  │                                                           │  │
│  │ Model: GARCH(1,1) or EGARCH for asymmetric volatility   │  │
│  │ Input: Historical returns (last 100-500 periods)         │  │
│  │ Output: • Forecasted volatility (next 1-10 periods)      │  │
│  │         • 95% confidence intervals                        │  │
│  │         • Volatility regime (low/normal/high)            │  │
│  │                                                           │  │
│  │ Use Case: Position sizing, stop-loss placement           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  B. COPULA CORRELATION MODELING                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Purpose: Model joint dependencies & tail risk            │  │
│  │                                                           │  │
│  │ Models: • Gaussian Copula (normal correlation)           │  │
│  │         • t-Copula (fat tails, extreme events)           │  │
│  │         • Clayton Copula (lower tail dependence)         │  │
│  │                                                           │  │
│  │ Input: Returns of [Stock, SPY, QQQ, Sector ETF]          │  │
│  │ Output: • Correlation matrix                             │  │
│  │         • Tail dependence coefficients                    │  │
│  │         • Conditional probabilities                       │  │
│  │                                                           │  │
│  │ Use Case: Portfolio diversification, hedge selection     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│       STAGE 5: ENSEMBLE CLASSIFIER (BUY/SELL DECISION)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: All 80-100 features (predictions + indicators + risk)   │
│                                                                  │
│  Ensemble Architecture:                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │  Base Models (5 models):                                 │  │
│  │  1. Random Forest (500 trees)         → Vote 1           │  │
│  │  2. XGBoost (gradient boosting)       → Vote 2           │  │
│  │  3. LightGBM (fast gradient boost)    → Vote 3           │  │
│  │  4. Neural Network (3 hidden layers)  → Vote 4           │  │
│  │  5. SVM (Support Vector Machine)      → Vote 5           │  │
│  │                                                           │  │
│  │  Meta-Learner:                                           │  │
│  │  Logistic Regression or XGBoost                          │  │
│  │  → Combines base model predictions                       │  │
│  │  → Outputs final decision + confidence                   │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Outputs:                                                       │
│  • Signal: BUY / SELL / HOLD                                    │
│  • Confidence: 0.0 - 1.0 (probability)                          │
│  • Expected Return: +X% / -Y%                                   │
│  • Risk Score: 1-10 (from GARCH/Copula)                         │
│  • Time Horizon: Recommended holding period                     │
│                                                                  │
│  Decision Rules:                                                │
│  • BUY:  Confidence >= 0.7 AND Risk Score <= 6                  │
│  • SELL: Confidence >= 0.7 AND Risk Score <= 6                  │
│  • HOLD: Confidence < 0.7 OR Risk Score > 6                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 6: POSITION MANAGEMENT                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  For each BUY signal:                                           │
│  • Calculate Position Size: Kelly Criterion or Fixed %          │
│  • Set Stop Loss: Based on GARCH volatility                     │
│  • Set Take Profit: Risk/Reward ratio (min 2:1)                │
│  • Monitor: Real-time price vs. predicted prices               │
│                                                                  │
│  For each SELL signal:                                          │
│  • Exit existing position                                       │
│  • Log performance metrics                                      │
│  • Update model feedback                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 7: EXECUTION & MONITORING                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  • Submit orders via Schwab API                                 │
│  • Real-time monitoring of open positions                       │
│  • Update predictions every 1-5 minutes                         │
│  • Log all trades for backtesting/improvement                   │
│  • Alert system for high-confidence signals                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Technology Stack

### Data & Processing:
- **Data Source**: Schwab API (real-time & historical)
- **Feature Engineering**: pandas, numpy, ta-lib
- **Time Series**: arch (GARCH), copulas library

### ML Models:
- **Deep Learning**: PyTorch or TensorFlow (LSTM, GRU, Transformer)
- **Gradient Boosting**: XGBoost, LightGBM, CatBoost
- **Ensemble**: scikit-learn (RandomForest, Voting, Stacking)
- **Risk Models**: statsmodels, arch, copulas

### Infrastructure:
- **Backend**: Python 3.10+, Node.js (API server)
- **Database**: PostgreSQL (trades), Redis (cache)
- **Queue**: Celery or RQ (async predictions)
- **Monitoring**: Prometheus + Grafana

---

## 📂 File Structure

```
Schwabdev/
├── ml_trading/
│   ├── __init__.py
│   ├── config.py                    # Configuration & hyperparameters
│   │
│   ├── data/
│   │   ├── fetcher.py              # Fetch data from Schwab API
│   │   ├── preprocessor.py         # Clean & normalize data
│   │   └── feature_engineer.py     # Generate 80-100 features
│   │
│   ├── models/
│   │   ├── timeframe_predictor.py  # Multi-timeframe LSTM/GRU models
│   │   ├── ensemble_classifier.py  # Final BUY/SELL ensemble
│   │   ├── garch_model.py          # GARCH volatility forecasting
│   │   └── copula_model.py         # Copula correlation analysis
│   │
│   ├── pipeline/
│   │   ├── momentum_filter.py      # Stage 1: Filter from scanner
│   │   ├── prediction_pipeline.py  # Stage 2: Multi-TF predictions
│   │   ├── risk_pipeline.py        # Stage 4: GARCH + Copula
│   │   └── decision_pipeline.py    # Stage 5: Ensemble decision
│   │
│   ├── execution/
│   │   ├── position_sizer.py       # Calculate position sizes
│   │   ├── order_manager.py        # Submit/manage orders
│   │   └── risk_manager.py         # Stop-loss, take-profit logic
│   │
│   ├── utils/
│   │   ├── indicators.py           # Technical indicators
│   │   ├── metrics.py              # Performance metrics
│   │   └── logger.py               # Structured logging
│   │
│   └── api/
│       ├── ml_endpoints.py         # REST API for predictions
│       └── websocket_handler.py    # Real-time updates
│
├── trained_models/
│   ├── lstm_1m.pth                 # Trained models per timeframe
│   ├── lstm_5m.pth
│   ├── ...
│   ├── ensemble_classifier.pkl     # Final ensemble model
│   ├── garch_params.pkl            # Pre-fit GARCH parameters
│   └── copula_params.pkl           # Pre-fit Copula parameters
│
├── data/
│   ├── historical/                 # Cached historical data
│   └── predictions/                # Logged predictions
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_ensemble_tuning.ipynb
│   └── 05_backtesting.ipynb
│
└── tests/
    ├── test_data.py
    ├── test_models.py
    └── test_pipeline.py
```

---

## 🎯 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure
- [ ] Data fetcher for all 6 timeframes
- [ ] Feature engineering pipeline (80-100 features)
- [ ] Basic LSTM/GRU models per timeframe

### Phase 2: Advanced Models (Week 3-4)
- [ ] Train multi-timeframe prediction models
- [ ] Implement GARCH volatility modeling
- [ ] Implement Copula correlation analysis
- [ ] Build ensemble classifier

### Phase 3: Integration (Week 5)
- [ ] Connect momentum scanner → ML pipeline
- [ ] Build decision pipeline (all stages)
- [ ] API endpoints for predictions
- [ ] Frontend integration

### Phase 4: Risk & Execution (Week 6)
- [ ] Position sizing logic
- [ ] Stop-loss/take-profit automation
- [ ] Order execution via Schwab API
- [ ] Real-time monitoring dashboard

### Phase 5: Testing & Optimization (Week 7-8)
- [ ] Backtesting on 2+ years data
- [ ] Walk-forward optimization
- [ ] Paper trading (1 month)
- [ ] Performance tuning

### Phase 6: Production (Week 9+)
- [ ] Live deployment with small capital
- [ ] Monitoring & alerts
- [ ] Continuous model retraining
- [ ] Performance reporting

---

## 🔢 Data Requirements

### Per Stock, Per Timeframe:
- **Historical Bars**: 100-500 (depending on timeframe)
- **Features**: 50+ technical indicators
- **Update Frequency**: 
  - 1m: Real-time (every minute)
  - 5m-1d: Every 5 minutes

### Storage Estimates:
- **Historical Data**: ~10 GB (1 year, all stocks)
- **Trained Models**: ~500 MB per timeframe × 6 = 3 GB
- **Predictions Log**: ~1 GB/month
- **Total**: ~15-20 GB

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Overfitting** | High | Cross-validation, walk-forward testing |
| **Data Quality** | High | Multiple data sources, validation checks |
| **Latency** | Medium | Async processing, caching, Redis |
| **API Rate Limits** | Medium | Batch requests, exponential backoff |
| **Model Drift** | High | Weekly retraining, performance monitoring |
| **Market Regime Change** | High | Ensemble diversity, regime detection |
| **Execution Slippage** | Medium | Limit orders, liquidity filters |

---

## 📊 Performance Monitoring

### Real-Time Metrics:
- Win Rate (rolling 30/60/90 days)
- Sharpe Ratio, Sortino Ratio
- Max Drawdown, Avg Drawdown
- Profit Factor (gross profit / gross loss)
- Avg Trade Duration
- Model Confidence Distribution

### Model Health:
- Prediction Accuracy per Timeframe
- Feature Importance Drift
- Ensemble Agreement Rate
- GARCH Volatility Forecast Accuracy
- Copula Correlation Stability

---

## 🔮 Future Enhancements

1. **Sentiment Analysis**: Incorporate news, social media, SEC filings
2. **Options Greeks**: IV, Delta, Gamma for options trading
3. **Multi-Asset**: Extend to crypto, forex, commodities
4. **Reinforcement Learning**: Deep Q-Network (DQN) for adaptive strategies
5. **Alternative Data**: Satellite imagery, credit card data, web traffic
6. **Portfolio Optimization**: Mean-variance, Black-Litterman
7. **Explainable AI**: SHAP values for trade justification

---

## 📞 Next Steps

1. **Review & Approve Architecture**
2. **Allocate Resources** (GPU, storage, API quotas)
3. **Begin Phase 1 Implementation**
4. **Set Up Development Environment**
5. **Schedule Weekly Progress Reviews**

---

**Document Version:** 1.0  
**Last Updated:** January 6, 2026  
**Author:** ML Trading System Architecture Team  
**Status:** Ready for Implementation


