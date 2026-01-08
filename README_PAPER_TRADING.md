# 🚀 Paper Trading System - README

## ⚡ Quick Start (30 seconds)

```bash
# Interactive menu
./start_here.sh

# Or directly:
./run_paper_single_cycle.sh    # Test first
./run_paper_trading.sh          # Then run live
python view_paper_results.py   # View results
```

## 💡 What Is This?

A **live paper trading system** that:
- Runs your ML strategy in real-time
- Uses real market data
- **NO real money at risk**
- Final validation before going live

## 🎯 Why Paper Trade?

1. **Verify backtest results** with live data
2. **Test system reliability** in real conditions  
3. **Build confidence** before risking money
4. **Find bugs** without consequences

## 📋 The System Does

✅ Scans momentum stocks every 5 minutes  
✅ Evaluates with your ML EV Classifier  
✅ Opens BUY positions automatically  
✅ Monitors Take Profit & Stop Loss  
✅ Closes positions automatically  
✅ Tracks all performance & trades  

## 🎮 Commands

### Run
```bash
./run_paper_single_cycle.sh     # Test with one cycle
./run_paper_trading.sh           # Run continuously
```

### Monitor
```bash
python view_paper_results.py           # View performance
python compare_backtest_paper.py       # Compare to backtest
cat paper_trades_log.json | jq         # View raw logs
```

### Stop
Press **Ctrl+C** (all data auto-saved!)

## 📊 What You'll See

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
Total Return:        +1.24%
Open Positions:      3/10
Closed Trades:       5
Win Rate:            60.0%
============================================================
```

## 🎛️ Configuration

Default (Recommended):
```bash
Capital:       $100,000
Position Size: 5% per trade
Max Positions: 10
Min EV:        0.0003 (0.03%)
Min Confidence: 0.48 (48%)
```

Custom:
```bash
python paper_trading_system.py \
    --capital 10000 \
    --position-size 0.02 \
    --max-positions 5 \
    --min-confidence 0.52
```

## 📁 Output Files

- `paper_trades_log.json` - All trades & positions
- `paper_trading_performance.json` - Performance stats

## ⏱️ Timeline

- **Day 1**: Test with single cycle
- **Week 1-2**: Run continuously during market hours
- **After 20+ trades**: Compare to backtest
- **If successful**: Ready for small live capital!

## 🎯 Success Criteria

After 1-2 weeks, check:
- ✅ Win rate ≥ 45-50%
- ✅ Total return > 0%
- ✅ Avg win > Avg loss
- ✅ No system crashes
- ✅ Matches backtest (within ±5-10%)

**If all ✅ → Ready for live trading!**

## 🔧 Troubleshooting

**No trades?**
```bash
# Lower thresholds
python paper_trading_system.py --min-confidence 0.42
```

**Too many trades?**
```bash
# Raise thresholds
python paper_trading_system.py --min-confidence 0.55
```

**API errors?**
- Check `.env` file credentials
- Activate conda: `conda activate schwabdev`
- Verify market hours (9:30 AM - 4:00 PM ET)

## 📚 Full Documentation

- **Quick**: `PAPER_TRADING_QUICK_START.md`
- **Complete**: `PAPER_TRADING_GUIDE.md`
- **Master**: `TRADING_SYSTEM_COMPLETE.md`

## 🎉 What Makes This Special?

This isn't just a simple paper trader. It's:

✅ **Multi-timeframe ML** (7 timeframes)  
✅ **231 features** (technical + alpha + risk)  
✅ **Expected Value based** (not just predictions)  
✅ **Risk-aware** (GARCH + Copula)  
✅ **Fully automated** (scan → evaluate → trade)  
✅ **Production-ready** (logging, monitoring, error handling)  

## 🚦 Next Steps

1. **Today**: Test with single cycle ✅
2. **This week**: Start continuous paper trading ✅
3. **Daily**: Check results ✅
4. **After 1-2 weeks**: Compare to backtest ✅
5. **If good**: Go live with small capital! 🚀

## 💬 Remember

- This is **validation**, not optimization
- Run for **1-2 weeks minimum**
- Need **20-30 trades** for good stats
- **Compare to backtest** closely
- Only go live when **confident**

## 🏁 Ready?

```bash
./start_here.sh
```

Choose option 1 to test, then option 2 to run live!

**Good luck! 🍀**

---

**Questions?** Check `TRADING_SYSTEM_COMPLETE.md` for everything.

