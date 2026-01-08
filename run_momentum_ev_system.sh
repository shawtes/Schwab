#!/bin/bash

# Run Momentum + EV Trading System
# Finds top momentum stocks and generates trading signals

echo "=========================================="
echo "🚀 Momentum + EV Trading System"
echo "=========================================="
echo ""

# Activate conda environment
echo "Activating schwabdev environment..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
conda activate schwabdev

# Default parameters
MIN_PRICE=${1:-2}
MAX_PRICE=${2:-20}
TOP_N=${3:-3}
MODE=${4:---fast}

echo "Configuration:"
echo "  Price Range: \$$MIN_PRICE - \$$MAX_PRICE"
echo "  Top Stocks: $TOP_N"
echo "  Mode: $MODE"
echo ""

# Run system
python momentum_ev_trading_system.py $MIN_PRICE $MAX_PRICE $TOP_N $MODE

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Analysis complete!"
    echo "📊 Check trading_signals.json for results"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ Analysis failed with exit code $EXIT_CODE"
    echo "=========================================="
fi

exit $EXIT_CODE

