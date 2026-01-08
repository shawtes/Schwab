# ⚡ Quick Reference Card

## 🚀 Most Used Commands

```bash
# Interactive menu (EASIEST!)
./start_here.sh

# Paper trading
./run_paper_single_cycle.sh    # Test first
./run_paper_trading.sh          # Run live

# Backtesting
./run_full_backtest.sh          # Full system

# Analysis
python view_paper_results.py           # Paper results
python compare_backtest_paper.py       # Comparison
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `paper_trades_log.json` | All trades & positions |
| `paper_trading_performance.json` | Performance metrics |
| `backtest_log_*.json` | Backtest results |

## 🎛️ Key Parameters

```bash
--capital 100000           # Starting capital
--position-size 0.05       # 5% per trade
--max-positions 10         # Max open positions
--min-ev 0.0003           # Min EV (0.03%)
--min-confidence 0.48      # Min confidence (48%)
--interval 5               # Check every 5 min
```

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Win Rate | ≥ 50% (backtest), ≥ 45% (paper) |
| Total Return | > 0% (positive) |
| Sharpe Ratio | > 1.0 |
| Avg Win vs Loss | Win > Loss |
| Max Drawdown | < 10% |

## 🔧 Quick Fixes

### No Trades
```bash
python paper_trading_system.py --min-confidence 0.42 --min-ev 0.0001
```

### Too Many Trades
```bash
python paper_trading_system.py --min-confidence 0.55 --min-ev 0.0008
```

### API Errors
```bash
conda activate schwabdev
# Check .env file
```

## 📚 Documentation Quick Links

| Want to... | Read... |
|------------|---------|
| Get started NOW | `README_PAPER_TRADING.md` |
| Understand paper trading | `PAPER_TRADING_GUIDE.md` |
| See the big picture | `TRADING_SYSTEM_COMPLETE.md` |
| Visual flowcharts | `SYSTEM_FLOWCHART.md` |
| Compare backtest vs paper | `PAPER_TRADING_COMPARISON.md` |

## ⏱️ Timeline

| Week | Activity | Goal |
|------|----------|------|
| 1-2 | Backtest | Win rate > 50% |
| 3-4 | Paper trade | Confirm profitability |
| 5 | Compare | Verify consistency |
| 6+ | Go live | Start small! |

## 🎯 System Flow (Super Simple)

```
Scan → Evaluate → BUY → Monitor → Exit → Profit
```

## 🆘 Emergency Commands

```bash
# Stop paper trading
Ctrl+C

# View current status
python view_paper_results.py

# Check if running
ps aux | grep paper_trading

# View logs
cat paper_trades_log.json | jq

# Start fresh (careful!)
rm paper_trades_log.json paper_trading_performance.json
```

## 💡 Pro Tips

1. **Always test first**: `./run_paper_single_cycle.sh`
2. **Be patient**: Need 20+ trades for statistics
3. **Check daily**: `python view_paper_results.py`
4. **Compare often**: `python compare_backtest_paper.py`
5. **Start small**: $500-$1000 when going live

## 🚦 Go/No-Go Checklist

After 1-2 weeks paper trading:

- [ ] Win rate ≥ 45%?
- [ ] Total return > 0%?
- [ ] Avg win > Avg loss?
- [ ] No crashes?
- [ ] Matches backtest?
- [ ] Confident?

**All checked? → Ready for live! 🚀**

---

**Keep this card handy!** 📌

