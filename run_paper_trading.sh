#!/bin/bash

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate schwabdev

echo "🚀 Starting Live Paper Trading System"
echo "======================================"
echo ""
echo "💰 Initial Capital: \$100,000"
echo "📊 Max Positions: 10"
echo "📈 Position Size: 5% per trade"
echo "⏰ Check Interval: 5 minutes"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run paper trading system
python paper_trading_system.py \
    --capital 100000 \
    --position-size 0.05 \
    --max-positions 10 \
    --min-ev 0.0003 \
    --min-confidence 0.48 \
    --interval 5

echo ""
echo "✅ Paper trading session ended"

