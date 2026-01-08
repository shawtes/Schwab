#!/bin/bash

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate schwabdev

echo "🔄 Running Single Paper Trading Cycle"
echo "====================================="
echo ""

# Run single cycle (good for testing)
python paper_trading_system.py \
    --capital 100000 \
    --position-size 0.05 \
    --max-positions 10 \
    --min-ev 0.0003 \
    --min-confidence 0.48 \
    --single-cycle

echo ""
echo "✅ Cycle complete"

