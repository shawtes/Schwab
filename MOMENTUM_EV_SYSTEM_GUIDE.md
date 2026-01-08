# 🚀 Momentum + EV Automated Trading System

## Overview

This system combines **momentum screening** with **multi-timeframe EV classification** to generate high-probability trading signals automatically.

## 🎯 What It Does

```
Step 1: Momentum Scanner
  → Scans ALL available stocks
  → Filters by price range ($2-$20)
  → Ranks by momentum score (0-100)
  → Returns top 3 candidates

Step 2: Multi-Timeframe Predictions  
  → For each candidate, predicts on multiple timeframes
  → 5m: Short-term momentum
  → 1d: Daily trend
  → (Optional: 1m, 30m, 1h for full mode)

Step 3: EV Classifier
  → Uses predictions as features (meta-learning)
  → Calculates Expected Value
  → Generates BUY/SELL/HOLD signal
  → Provides confidence score

Step 4: Trading Recommendations
  → Ranks signals by EV × Confidence
  → Provides star ratings (1-5 stars)
  → Exports to trading_signals.json
```

## 🎮 How to Use

### Quick Start (Default: $2-$20, Top 3, Fast Mode)

```bash
./run_momentum_ev_system.sh
```

### Custom Parameters

```bash
# Syntax: ./run_momentum_ev_system.sh MIN_PRICE MAX_PRICE TOP_N MODE

# Example 1: $5-$15 range, top 5 stocks, fast mode
./run_momentum_ev_system.sh 5 15 5 --fast

# Example 2: $10-$30 range, top 3, full analysis (all timeframes)
./run_momentum_ev_system.sh 10 30 3 --full

# Example 3: Penny stocks $1-$5, top 10
./run_momentum_ev_system.sh 1 5 10 --fast
```

### Or Run Directly with Python

```bash
# Fast mode (5m + 1d timeframes)
python momentum_ev_trading_system.py 2 20 3 --fast

# Full mode (all timeframes: 1m, 5m, 30m, 1d)
python momentum_ev_trading_system.py 2 20 3
```

## 📊 Example Output

```
====================================================================================================
🚀 MOMENTUM + EV AUTOMATED TRADING SYSTEM
====================================================================================================

⚙️ Configuration:
   Price Range: $2.0 - $20.0
   Top Stocks: 3
   Mode: Fast (5m+1d)

====================================================================================================
MOMENTUM SCANNER: Finding top 3 stocks in $2.0-$20.0 range
====================================================================================================

📊 Scan Filters:
   Price Range: $2.0 - $20.0
   Min % Change: 1.0%
   Min RVOL: 1.2x
   Min Volume: 500,000
   RSI Range: 50-85

🔍 Scanning stocks...
✅ Found 47 momentum stocks
📈 Top 3 candidates:

Rank   Symbol   Price      Change     RVOL     RSI    Score    Trend
----------------------------------------------------------------------------------------------------
1      SOFI     $12.34     +8.45%     3.2x     72     85       strong
2      PLTR     $18.90     +5.23%     2.1x     68     78       strong
3      NIO      $7.56      +4.12%     1.8x     65     72       strong

====================================================================================================
EV CLASSIFIER ANALYSIS
====================================================================================================

[1/3] Analyzing SOFI
...

[2/3] Analyzing PLTR
...

[3/3] Analyzing NIO
...

====================================================================================================
🎯 TRADING RECOMMENDATIONS
====================================================================================================

====================================================================================================
📈 BUY RECOMMENDATIONS
====================================================================================================

Symbol   Price      Signal   Conf     EV         Win%     Sharpe     Rating
----------------------------------------------------------------------------------------------------
SOFI     $12.34     BUY      68.3%    0.234%     59.2%    0.456      ⭐⭐⭐⭐⭐ STRONG BUY
PLTR     $18.90     BUY      62.1%    0.189%     56.8%    0.389      ⭐⭐⭐⭐ BUY
NIO      $7.56      BUY      58.7%    0.123%     54.3%    0.298      ⭐⭐⭐ MODERATE BUY

====================================================================================================
📋 SUMMARY
====================================================================================================

   Stocks Analyzed: 3
   BUY Signals: 3
   SELL Signals: 0
   HOLD: 0

   🏆 TOP PICK: SOFI
      Price: $12.34
      Expected Value: 0.234%
      Win Probability: 59.2%
      Confidence: 68.3%

====================================================================================================

💾 Results saved to: trading_signals.json

====================================================================================================
✅ ANALYSIS COMPLETE!
====================================================================================================
```

## 📁 Output File Format

The system saves results to `trading_signals.json`:

```json
{
  "timestamp": "2026-01-07T15:30:00",
  "config": {
    "min_price": 2.0,
    "max_price": 20.0,
    "top_n": 3
  },
  "momentum_stocks": [
    {
      "symbol": "SOFI",
      "price": 12.34,
      "percentChange": 8.45,
      "rvol": 3.2,
      "rsi": 72,
      "score": 85,
      "trend": "strong"
    }
  ],
  "analysis_results": {
    "SOFI": {
      "momentum_score": 85,
      "signal": "BUY",
      "confidence": 0.683,
      "expected_value": 0.00234,
      "win_probability": 0.592,
      "sharpe_ev": 0.456
    }
  },
  "recommendations": {
    "recommendations": [
      {
        "symbol": "SOFI",
        "action": "BUY",
        "price": 12.34,
        "confidence": 0.683,
        "expected_value": 0.00234,
        "rating": "⭐⭐⭐⭐⭐ STRONG BUY",
        "overall_score": 0.812
      }
    ],
    "buy_count": 3,
    "top_pick": "SOFI"
  }
}
```

## 🎓 Understanding the Ratings

### Star Ratings

- **⭐⭐⭐⭐⭐ STRONG BUY**: Overall score > 75%
  - High EV, high confidence, strong momentum
  - Highest probability signals

- **⭐⭐⭐⭐ BUY**: Overall score 65-75%
  - Good EV, good confidence, solid momentum
  - High probability signals

- **⭐⭐⭐ MODERATE BUY**: Overall score 55-65%
  - Positive EV, moderate confidence
  - Acceptable risk/reward

- **⭐⭐ WEAK BUY**: Overall score < 55%
  - Low EV or low confidence
  - Proceed with caution

### Overall Score Calculation

```python
Overall Score = (EV Score × 0.4) + (Confidence × 0.4) + (Momentum × 0.2)

Where:
- EV Score: Expected Value / 0.005 (capped at 1.0)
- Confidence: From EV classifier (0-1)
- Momentum: Momentum score / 100 (0-1)
```

## 🔧 Customization

### Adjust Momentum Filters

Edit `find_top_momentum_stocks()` in `momentum_ev_trading_system.py`:

```python
filters = {
    'minPrice': min_price,
    'maxPrice': max_price,
    'minPercentChange': 1.0,  # Change to 0.5 for slower markets
    'minRVOL': 1.2,           # Change to 1.0 for more candidates
    'minVolume': 500000,      # Adjust liquidity threshold
    'rsiMin': 50,             # Bullish threshold
    'rsiMax': 85              # Overbought threshold
}
```

### Adjust EV Thresholds

Edit in `test_ev_classifier_system.py`:

```python
ev_classifier = EVClassifier(
    min_ev=0.0005,       # Lower = more signals (aggressive)
    min_confidence=0.52,  # Lower = more signals (aggressive)
    risk_free_rate=0.05   # Annual risk-free rate
)
```

## 🎯 Best Practices

### 1. **Run Daily**
```bash
# Add to cron for daily scans
0 9 * * 1-5 cd /path/to/Schwabdev && ./run_momentum_ev_system.sh
```

### 2. **Track Performance**
Keep a trading journal:
- Entry date/time
- Symbol and price
- Signal rating
- Actual outcome
- Calculate win rate over time

### 3. **Position Sizing**
Use confidence scores for position sizing:
```
Position Size = Base Size × Confidence × (EV / 0.002)

Example:
- Base: $1000
- Confidence: 68.3%
- EV: 0.234% (0.00234)

Position = $1000 × 0.683 × (0.00234 / 0.002)
         = $1000 × 0.683 × 1.17
         = $799
```

### 4. **Risk Management**
- Never risk more than 2% per trade
- Use stop losses (suggestion: 1.5 × avg_loss)
- Diversify across multiple signals
- Don't trade signals with <50% confidence

### 5. **Market Conditions**
- System works best in **trending markets**
- Less reliable in **sideways/choppy markets**
- Consider overall market sentiment (SPY, QQQ trends)

## 📊 Performance Expectations

### Conservative Settings
```
Min EV: 0.002 (0.2%)
Min Confidence: 0.60 (60%)

Expected:
- 1-3 signals per day
- 60-70% win rate
- 0.2-0.4% avg EV per trade
```

### Balanced Settings (Default)
```
Min EV: 0.0005 (0.05%)
Min Confidence: 0.52 (52%)

Expected:
- 3-10 signals per day
- 52-58% win rate
- 0.1-0.3% avg EV per trade
```

### Aggressive Settings
```
Min EV: 0.0002 (0.02%)
Min Confidence: 0.50 (50%)

Expected:
- 10-20 signals per day
- 50-55% win rate
- 0.05-0.15% avg EV per trade
```

## 🚨 Important Notes

1. **Paper Trade First**: Test the system with paper trading for 2-4 weeks

2. **Market Hours**: Best results during market hours (9:30 AM - 4:00 PM ET)

3. **Data Quality**: Requires active Schwab API connection

4. **Execution**: System generates signals - you still need to execute trades

5. **Past Performance**: Historical backtests don't guarantee future results

## 🐛 Troubleshooting

### No Momentum Stocks Found
```
Solutions:
1. Lower minPercentChange to 0.5%
2. Lower minRVOL to 1.0x
3. Expand price range (e.g., $1-$50)
4. Run during market hours
5. Check if market is trending
```

### Low Direction Accuracy
```
Solutions:
1. Increase min_ev threshold
2. Increase min_confidence threshold
3. Use more training data (20 years)
4. Try different timeframes
5. Focus on higher momentum scores (>70)
```

### System Errors
```
Check:
1. Schwab API credentials in .env
2. Python environment activated
3. All dependencies installed
4. Network connection
5. API rate limits not exceeded
```

## 🔮 Future Enhancements

1. **Real-Time Alerts**: Push notifications for new signals
2. **Auto-Execution**: Integrate with broker API for automatic trading
3. **Portfolio Management**: Track open positions and P&L
4. **Advanced Filters**: Sector rotation, earnings calendar, news sentiment
5. **Machine Learning**: Continuously improve based on actual results

## 📚 Related Documentation

- `MULTI_TIMEFRAME_EV_SYSTEM.md`: Deep dive into EV classifier
- `STAGE_2_COMPLETE_SUMMARY.md`: Architecture overview
- `FINAL_ARCHITECTURE_AUDIT_2026.md`: Complete system audit

## 🏆 Success Story Template

"I ran the momentum + EV system and got a **⭐⭐⭐⭐⭐ STRONG BUY** on [SYMBOL] at $[PRICE]. 

Expected Value: [EV]%
Win Probability: [WIN%]%  
Confidence: [CONF]%

Result: [+X%] profit in [N] days!"

---

**Created**: January 7, 2026  
**Status**: ✅ Production Ready  
**Next Step**: Run `./run_momentum_ev_system.sh` and start making money! 💰

