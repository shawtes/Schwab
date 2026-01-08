# Full System Backtest Guide

Complete guide for backtesting the **Momentum Scanner + EV Classifier** system.

---

## 🎯 What This Backtest Does

Simulates the **complete production workflow**:

```
Daily Loop:
├─ 1. Scan 1,453 stocks for momentum
├─ 2. Select top 3 momentum stocks
├─ 3. Train EV classifier on each
├─ 4. Take BUY signals (if EV is positive)
├─ 5. Manage positions with TP/SL
└─ 6. Track performance
```

This is **exactly** how the system works in production!

---

## 🚀 Quick Start

### Basic Run (90 days, default settings)
```bash
./run_full_backtest.sh
```

### Custom Period
```bash
python backtest_full_system.py --days 180  # 6 months
python backtest_full_system.py --days 365  # 1 year
python backtest_full_system.py --days 30   # 1 month
```

---

## ⚙️ Configuration Parameters

### Capital & Risk
```bash
--capital 10000      # Starting capital ($10,000 default)
--risk 0.02          # Risk per trade (2% default)
--positions 3        # Max concurrent positions (3 default)
```

### Momentum Scanner
```bash
--min-price 2        # Min stock price ($2 default)
--max-price 20       # Max stock price ($20 default)
--top-n 3            # Top N momentum stocks (3 default)
```

### EV Classifier (CRITICAL!)
```bash
--min-ev 0.0003          # Min EV to trade (0.03% default)
--min-confidence 0.48    # Min win probability (48% default)
```

### Backtest Period
```bash
--days 90            # Backtest period (90 days default)
```

---

## 🔧 EV Classifier Thresholds

### Why These Matter

The EV classifier filters trades based on:
1. **Expected Value (EV)**: Must be positive
2. **Win Probability**: Must exceed threshold
3. **Expected Return**: Must be positive

**If thresholds are too high → No trades!**  
**If thresholds are too low → Too many bad trades!**

### Recommended Settings

| Market | Min EV | Min Confidence | Rationale |
|--------|--------|----------------|-----------|
| **Momentum Stocks ($2-$20)** | 0.0003 | 0.48 | High volatility, ~48-51% win rate |
| **Large Cap ($50+)** | 0.0002 | 0.52 | More predictable, higher win rate |
| **Penny Stocks ($1-$5)** | 0.0005 | 0.45 | Very volatile, lower win rate |
| **Conservative** | 0.0005 | 0.55 | Fewer trades, higher quality |
| **Aggressive** | 0.0001 | 0.45 | More trades, more risk |

### Historical Win Rates

Based on training data, typical win rates are:
- **Momentum stocks**: 48-51%
- **High volatility**: 45-50%
- **Low volatility**: 52-58%

**Set `--min-confidence` slightly BELOW the historical win rate** to ensure trades are taken!

---

## 📊 Example Runs

### Conservative (High Quality Trades)
```bash
python backtest_full_system.py \
  --days 180 \
  --min-ev 0.0005 \
  --min-confidence 0.55 \
  --positions 2 \
  --risk 0.01
```

**Expected**: Fewer trades, higher win rate, lower drawdown

### Aggressive (More Trades)
```bash
python backtest_full_system.py \
  --days 180 \
  --min-ev 0.0001 \
  --min-confidence 0.45 \
  --positions 5 \
  --risk 0.03
```

**Expected**: More trades, lower win rate, higher returns (if working)

### Balanced (Default)
```bash
./run_full_backtest.sh
```

**Expected**: ~20-40 trades in 90 days, 48-55% win rate

### Higher Price Range
```bash
python backtest_full_system.py \
  --min-price 10 \
  --max-price 50 \
  --min-ev 0.0002 \
  --min-confidence 0.52
```

**Expected**: Different momentum stocks, potentially higher win rate

---

## 📈 Success Metrics

### Good Results
- ✅ **Win Rate**: 50-60%
- ✅ **Profit Factor**: > 1.5
- ✅ **Sharpe Ratio**: > 1.0
- ✅ **Max Drawdown**: < 15%
- ✅ **Total Return**: > 10% (for 90 days)
- ✅ **Trades**: 20-40 (not too few, not too many)

### Warning Signs
- ⚠️ **No trades**: Thresholds too high
- ⚠️ **100+ trades**: Thresholds too low
- ⚠️ **Win rate < 45%**: System not working
- ⚠️ **Profit factor < 1.0**: Losing money
- ⚠️ **Max drawdown > 25%**: Too risky

---

## 🔍 Troubleshooting

### Problem: No Trades Taken

**Symptom**: 
```
Processing: 2025-11-06 (20/65) - Capital: $10,000, Positions: 0, Trades: 0
```

**Cause**: Thresholds are too strict!

**Fix**:
```bash
# Lower the thresholds
python backtest_full_system.py \
  --min-ev 0.0001 \
  --min-confidence 0.45
```

**Check**: Look at training output:
```
Historical Stats:
   Win Rate: 48.1%    ← If this is below min_confidence, NO TRADES!
```

### Problem: Too Many Trades

**Symptom**: 100+ trades in 90 days

**Cause**: Thresholds too low

**Fix**:
```bash
# Raise the thresholds
python backtest_full_system.py \
  --min-ev 0.0005 \
  --min-confidence 0.55
```

### Problem: Low Win Rate

**Symptom**: Win rate < 45%

**Cause**: Market conditions or bad features

**Fix**:
1. Check date range (avoid bear markets)
2. Adjust price range
3. Change scan frequency
4. Use different granularity data

---

## 🎓 Understanding the Output

### Configuration Section
```
⚙️ Configuration:
   Period: 2024-10-09 to 2025-01-07
   Initial Capital: $10,000.00
   Max Positions: 3
   Risk per Trade: 2.0%
   Price Range: $2-$20
   Top Stocks: 3
   Scan Frequency: Every 1 day(s)
   Min EV: 0.03% (trades must beat this)    ← CRITICAL
   Min Win Prob: 48% (minimum confidence)   ← CRITICAL
```

### Training Output
```
Training EV Classifier on 265 samples...
Historical Stats:
   Win Rate: 47.9%        ← Historical performance
   Avg Win: 3.57%         ← Average winning return
   Avg Loss: 3.02%        ← Average losing return
✓ EV Classifier trained
```

**If Win Rate < Min Win Prob → NO BUY SIGNAL**

### Trade Output
```
💰 2025-11-15: BUY SOFI @ $8.45 (EV: 0.12%, Conf: 54%)
```

This means:
- Date: 2025-11-15
- Symbol: SOFI
- Entry: $8.45
- Expected Value: 0.12%
- Confidence: 54%

### Results Section
```
📊 Trading Statistics:
   Total Trades: 27              ← Aim for 20-40 in 90 days
   Wins: 17 (63.0%)              ← Win rate (aim for >55%)
   Profit Factor: 2.35           ← Aim for >1.5
   
💰 Performance:
   Total Return: +12.50%         ← Aim for >10% in 90 days
   
📈 Risk Metrics:
   Sharpe Ratio: 1.65            ← Aim for >1.0
   Max Drawdown: -6.20%          ← Aim for <15%
```

---

## 🎯 Optimization Strategy

### Step 1: Baseline
```bash
# Run with defaults
./run_full_backtest.sh
```

### Step 2: Adjust if Needed

**No trades?**
```bash
python backtest_full_system.py --min-confidence 0.45 --min-ev 0.0001
```

**Too many trades?**
```bash
python backtest_full_system.py --min-confidence 0.55 --min-ev 0.0005
```

### Step 3: Optimize Parameters

Test different combinations:
```bash
# Test 1: Conservative
python backtest_full_system.py --min-ev 0.0005 --min-confidence 0.52

# Test 2: Balanced
python backtest_full_system.py --min-ev 0.0003 --min-confidence 0.48

# Test 3: Aggressive
python backtest_full_system.py --min-ev 0.0001 --min-confidence 0.45
```

Compare:
- Total Return
- Win Rate
- Profit Factor
- Max Drawdown
- Sharpe Ratio

### Step 4: Choose Best Settings

Pick the configuration with:
- Highest Sharpe Ratio
- Acceptable drawdown (<15%)
- Good win rate (>50%)
- Reasonable number of trades (20-40)

---

## 💡 Pro Tips

### 1. Match Thresholds to Historical Data
```
If training shows 49% win rate → Set --min-confidence 0.48
If training shows 52% win rate → Set --min-confidence 0.50
```

### 2. Start Conservative, Then Loosen
```bash
# Start here
python backtest_full_system.py --min-confidence 0.55

# If no trades, gradually lower
python backtest_full_system.py --min-confidence 0.52
python backtest_full_system.py --min-confidence 0.50
python backtest_full_system.py --min-confidence 0.48
```

### 3. Use Environment Variables
```bash
# Quick tuning without typing full command
MIN_CONFIDENCE=0.48 MIN_EV=0.0003 ./run_full_backtest.sh
```

### 4. Test Multiple Periods
```bash
# Bull market
python backtest_full_system.py --days 90

# Different season
python backtest_full_system.py --days 180

# Full year
python backtest_full_system.py --days 365
```

### 5. Document Your Best Settings
```
Date: 2025-01-07
Period: 90 days
Settings: --min-ev 0.0003 --min-confidence 0.48
Results: 27 trades, 63% win rate, +12.5% return, 1.65 Sharpe
```

---

## 🚨 Common Mistakes

### ❌ Setting Thresholds Too High
```bash
# BAD: This will generate NO trades if win rate is ~50%
python backtest_full_system.py --min-confidence 0.60
```

### ❌ Ignoring Historical Win Rate
```
If training shows 48% win rate but you set --min-confidence 0.52,
you'll get ZERO trades! Always check the training output.
```

### ❌ Not Testing Multiple Periods
```bash
# BAD: Only testing one period
python backtest_full_system.py --days 30

# GOOD: Test multiple periods
for days in 30 60 90 180; do
  python backtest_full_system.py --days $days
done
```

### ❌ Comparing Apples to Oranges
```
Don't compare:
- 30-day backtest vs 180-day backtest
- $2-$20 stocks vs $50+ stocks
- Different min-confidence settings

Always compare similar configurations!
```

---

## 📁 Related Files

- `backtest_full_system.py` - Main backtest script
- `run_full_backtest.sh` - Easy run script
- `momentum_ev_trading_system.py` - Production system
- `ml_trading/pipeline/multi_timeframe_system.py` - EV classifier
- `BACKTEST_GUIDE.md` - Single stock backtest guide

---

## 🎓 Next Steps

1. ✅ **Run baseline**: `./run_full_backtest.sh`
2. ✅ **Check results**: Look for trades, win rate, returns
3. ✅ **Adjust thresholds**: Based on historical win rates
4. ✅ **Optimize**: Test different configurations
5. ✅ **Validate**: Run on multiple periods
6. ✅ **Deploy**: Use best settings in production

---

## 🏆 Example: Finding Optimal Settings

```bash
# Test conservative
echo "Testing Conservative..."
python backtest_full_system.py --min-ev 0.0005 --min-confidence 0.52 --days 90 > results_conservative.txt

# Test balanced
echo "Testing Balanced..."
python backtest_full_system.py --min-ev 0.0003 --min-confidence 0.48 --days 90 > results_balanced.txt

# Test aggressive
echo "Testing Aggressive..."
python backtest_full_system.py --min-ev 0.0001 --min-confidence 0.45 --days 90 > results_aggressive.txt

# Compare
echo "\nConservative:"
grep "Total Return" results_conservative.txt
grep "Win Rate" results_conservative.txt
grep "Sharpe Ratio" results_conservative.txt

echo "\nBalanced:"
grep "Total Return" results_balanced.txt
grep "Win Rate" results_balanced.txt
grep "Sharpe Ratio" results_balanced.txt

echo "\nAggressive:"
grep "Total Return" results_aggressive.txt
grep "Win Rate" results_aggressive.txt
grep "Sharpe Ratio" results_aggressive.txt
```

---

**🚀 Ready to backtest? Run `./run_full_backtest.sh` now!**

