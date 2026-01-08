# 📈 Live Paper Trading System Guide

## Overview

The **Paper Trading System** runs your **full ML trading strategy in real-time** without risking real money. It's the final validation step before going live!

## 🎯 What It Does

1. **Scans for momentum stocks** every N minutes
2. **Evaluates each stock** with the EV Classifier
3. **Opens positions** on BUY signals
4. **Monitors positions** for Take Profit (TP) and Stop Loss (SL)
5. **Tracks performance** with full metrics
6. **Logs all trades** to JSON files

## 🚀 Quick Start

### Test with a Single Cycle (Recommended First!)

```bash
chmod +x run_paper_single_cycle.sh
./run_paper_single_cycle.sh
```

This runs **one complete cycle** to verify everything works.

### Start Live Paper Trading

```bash
chmod +x run_paper_trading.sh
./run_paper_trading.sh
```

This runs **continuously** checking every 5 minutes during market hours.

## 📊 Output Files

The system creates these files:

1. **`paper_trades_log.json`** - All trade details
2. **`paper_trading_performance.json`** - Performance metrics

## 🎛️ Configuration

### Basic Parameters

```bash
python paper_trading_system.py \
    --capital 100000 \              # Starting capital
    --position-size 0.05 \          # 5% per trade
    --max-positions 10 \            # Max open positions
    --min-ev 0.0003 \              # Min EV threshold
    --min-confidence 0.48 \         # Min confidence
    --interval 5                    # Check every 5 minutes
```

### Scanner Parameters

```bash
python paper_trading_system.py \
    --min-price 10 \               # Min stock price
    --max-price 500 \              # Max stock price
    --min-volume 1000000 \         # Min daily volume
    --min-change 5 \               # Min % price change
    --max-stocks 20                # Max stocks to scan
```

## 📈 How It Works

### 1. Momentum Scanning

Every interval, the system:
- Scans for stocks with strong momentum
- Filters by volume, price range, % change
- Finds top candidates

### 2. EV Classification

For each momentum stock:
- Fetches multi-timeframe data
- Trains models on each timeframe
- Makes predictions
- Calculates Expected Value (EV)
- Generates BUY or NO_TRADE signal

### 3. Position Management

When opening a position:
- Calculates position size (% of capital)
- Sets Take Profit (TP) = 1.5x predicted return
- Sets Stop Loss (SL) = 0.5x predicted return
- Tracks entry time and price

### 4. Position Monitoring

For each open position:
- Fetches current price every interval
- Checks if TP or SL hit
- Closes position automatically
- Updates capital and logs

### 5. Performance Tracking

Tracks:
- Total P&L
- Win Rate
- Average Win/Loss
- Return %
- Number of trades

## 🔄 Example Session

```
🚀 Starting LIVE Paper Trading System
   Check interval: 5 minutes
   Initial capital: $100,000.00
   Max positions: 10
   Position size: 5%

🔄 Starting trading cycle at 2026-01-07 10:00:00

🔍 Scanning for opportunities...
   Found 12 momentum stocks
   Analyzing AAPL...
      ✅ BUY signal - EV: 0.0045, Confidence: 65%
   Analyzing MSFT...
      ❌ NO_TRADE - EV: 0.0002, Confidence: 45%
   ...

🟢 OPENED POSITION: AAPL
   Entry: $175.50 x 28 shares = $4,914.00
   Take Profit: $181.23
   Stop Loss: $172.87
   Remaining Capital: $95,086.00

📈 PAPER TRADING SYSTEM STATUS
============================================================
Initial Capital:     $100,000.00
Current Capital:     $95,086.00
Total Return:        +0.00%
Total P&L:           $0.00

Open Positions:      1/10
Closed Trades:       0
============================================================

⏰ Next check in 5 minutes...
```

## 📊 Viewing Results

### Check Trade Log

```bash
cat paper_trades_log.json | jq '.closed_trades'
```

### Check Performance

```bash
cat paper_trading_performance.json | jq
```

### View Open Positions

```bash
cat paper_trades_log.json | jq '.open_positions'
```

## 🎯 Strategy Details

### Position Sizing

```
Position Value = Capital × Position Size %
Shares = Position Value / Stock Price
```

Example with $100K capital and 5% position size:
- Position value = $5,000
- If stock is $50: Buy 100 shares

### Take Profit / Stop Loss

```
Predicted Return = Model's predicted price change %

Take Profit = Entry Price × (1 + |Predicted Return| × 1.5)
Stop Loss = Entry Price × (1 - |Predicted Return| × 0.5)
```

Example:
- Entry: $100
- Predicted Return: +2%
- TP: $100 × (1 + 0.02 × 1.5) = $103.00
- SL: $100 × (1 - 0.02 × 0.5) = $99.00

This means:
- **Risk 1%** to make **3%** (3:1 reward/risk)
- If prediction is correct, you make 1.5x more
- If wrong, you lose 0.5x less

## ⚙️ Optimization Tips

### 1. Too Many Trades?
```bash
# Increase thresholds
--min-ev 0.0005 \
--min-confidence 0.52
```

### 2. Not Enough Trades?
```bash
# Lower thresholds
--min-ev 0.0001 \
--min-confidence 0.45
```

### 3. More Aggressive?
```bash
# Increase position size and max positions
--position-size 0.10 \  # 10% per trade
--max-positions 15
```

### 4. More Conservative?
```bash
# Decrease position size
--position-size 0.02 \  # 2% per trade
--max-positions 5
```

### 5. More Opportunities?
```bash
# Broaden scanner criteria
--min-change 3 \        # Lower % change
--max-stocks 50         # Scan more stocks
```

## 🕐 Market Hours

The system automatically checks market hours:
- **Open**: 9:30 AM ET
- **Close**: 4:00 PM ET

Outside these hours, it waits until market opens.

## 🛑 Stopping the System

Press **Ctrl+C** to stop. The system will:
1. Save all open positions
2. Save all closed trades
3. Display final performance stats

You can restart anytime and it will **resume** from where it left off!

## 📝 Example Runs

### Conservative (Test Mode)

```bash
python paper_trading_system.py \
    --capital 10000 \
    --position-size 0.02 \
    --max-positions 3 \
    --min-ev 0.0005 \
    --min-confidence 0.52 \
    --single-cycle
```

### Moderate (Recommended)

```bash
python paper_trading_system.py \
    --capital 100000 \
    --position-size 0.05 \
    --max-positions 10 \
    --min-ev 0.0003 \
    --min-confidence 0.48 \
    --interval 5
```

### Aggressive

```bash
python paper_trading_system.py \
    --capital 100000 \
    --position-size 0.10 \
    --max-positions 15 \
    --min-ev 0.0001 \
    --min-confidence 0.42 \
    --interval 3
```

## 🔍 Monitoring

### Check if Running

```bash
ps aux | grep paper_trading_system.py
```

### View Live Output

Output is printed to terminal in real-time showing:
- Momentum scans
- EV classifications
- Trade entries/exits
- Performance updates

### Log to File

```bash
./run_paper_trading.sh > paper_trading.log 2>&1 &
tail -f paper_trading.log
```

## 🚦 Next Steps

1. **Run single cycle** to verify setup
2. **Let it run for 1 day** with small capital
3. **Analyze results** in JSON files
4. **Adjust parameters** based on performance
5. **Run for 1 week** to get meaningful stats
6. **Compare to backtest** results

## 📊 Success Metrics

After 1 week of paper trading, check:

- ✅ **Win Rate > 50%**
- ✅ **Avg Win > Avg Loss**
- ✅ **Total Return > 0%**
- ✅ **Sharpe Ratio > 1.0**
- ✅ **Max Drawdown < 10%**

If all green → Consider going live with **real small capital**!

## ⚠️ Important Notes

1. **This is paper trading** - No real money at risk
2. **Slippage not modeled** - Real execution may differ
3. **Uses real-time data** - Requires Schwab API access
4. **Market hours only** - No pre-market/after-hours
5. **TP/SL are automatic** - No manual intervention needed

## 🤝 Support

If you see issues:
1. Check `paper_trades_log.json` for errors
2. Verify Schwab API credentials
3. Ensure market is open during testing
4. Start with single cycle to debug

## 🎉 Ready to Go Live?

After successful paper trading:
1. Verify consistent profitability (2+ weeks)
2. Start with **real small capital** ($500-$1000)
3. Use same parameters as successful paper trading
4. Monitor closely for first week
5. Scale up gradually

---

**💡 Pro Tip**: Run paper trading in parallel with backtesting. If they match, your strategy is robust!

