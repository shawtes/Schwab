#!/bin/bash

# Run Backtest on EV Trading System

echo "=========================================="
echo "🔬 EV Trading System - Backtest"
echo "=========================================="
echo ""

# Activate conda environment
echo "Activating schwabdev environment..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
conda activate schwabdev

# Default parameters
SYMBOLS=${@:-AAPL MSFT NVDA}
CAPITAL=${CAPITAL:-10000}
RISK=${RISK:-0.02}
TP=${TP:-1.5}
SL=${SL:-2.0}

echo "Configuration:"
echo "  Symbols: $SYMBOLS"
echo "  Capital: \$$CAPITAL"
echo "  Risk: $(echo "$RISK * 100" | bc)%"
echo "  TP Multiplier: ${TP}x"
echo "  SL Multiplier: ${SL}x ATR"
echo ""

# Run backtest
python backtest_ev_system.py $SYMBOLS --capital $CAPITAL --risk $RISK --tp $TP --sl $SL

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Backtest complete!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ Backtest failed with exit code $EXIT_CODE"
    echo "=========================================="
fi

exit $EXIT_CODE

