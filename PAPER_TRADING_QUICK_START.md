# 🚀 Paper Trading - Quick Start

## TL;DR

```bash
# Test with one cycle first
./run_paper_single_cycle.sh

# If it works, start live paper trading
./run_paper_trading.sh

# View results anytime
python view_paper_results.py
```

## What It Does

✅ Scans for momentum stocks every 5 minutes  
✅ Evaluates with your ML EV Classifier  
✅ Opens BUY positions automatically  
✅ Monitors for Take Profit / Stop Loss  
✅ Tracks all trades and performance  
✅ **NO REAL MONEY AT RISK!**

## Files Created

- `paper_trades_log.json` - All trade details
- `paper_trading_performance.json` - Performance metrics

## Expected Output

```
🔍 Scanning for opportunities...
   Found 12 momentum stocks
   Analyzing AAPL...
      ✅ BUY signal - EV: 0.0045, Confidence: 65%

🟢 OPENED POSITION: AAPL
   Entry: $175.50 x 28 shares = $4,914.00
   Take Profit: $181.23
   Stop Loss: $172.87

📈 PAPER TRADING SYSTEM STATUS
============================================================
Current Capital:     $95,086.00
Total Return:        +0.00%
Open Positions:      1/10
Closed Trades:       0
Win Rate:            N/A
============================================================
```

## Customization

### More Conservative
```bash
python paper_trading_system.py \
    --capital 10000 \
    --position-size 0.02 \
    --max-positions 5 \
    --min-confidence 0.52
```

### More Aggressive
```bash
python paper_trading_system.py \
    --capital 100000 \
    --position-size 0.10 \
    --max-positions 15 \
    --min-confidence 0.45
```

## Stopping

Press **Ctrl+C** - all data is saved automatically!

## Next Steps

1. ✅ Run single cycle to verify setup
2. ✅ Let it run for 1-2 weeks
3. ✅ Analyze results with `view_paper_results.py`
4. ✅ Compare to backtest results
5. ✅ If profitable → Go live with small capital!

## Full Documentation

See `PAPER_TRADING_GUIDE.md` for complete details.

