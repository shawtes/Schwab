#!/bin/bash

# Run Multi-Timeframe EV System Test
# Usage: ./run_ev_system.sh [SYMBOL] [--all]

echo "=========================================="
echo "Multi-Timeframe EV Trading System"
echo "=========================================="
echo ""

# Activate conda environment
echo "Activating schwabdev environment..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
conda activate schwabdev

# Default symbol
SYMBOL=${1:-AAPL}

# Run test
echo "Testing $SYMBOL..."
echo ""

python test_ev_classifier_system.py "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Test completed successfully!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ Test failed with exit code $EXIT_CODE"
    echo "=========================================="
fi

exit $EXIT_CODE

