#!/bin/bash

# Run Full System Backtest (Momentum Scanner + EV Classifier)

echo "=========================================="
echo "🔬 Full System Backtest"
echo "=========================================="
echo ""

# Activate conda environment
echo "Activating schwabdev environment..."
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null
conda activate schwabdev

# Default parameters
CAPITAL=${CAPITAL:-10000}
RISK=${RISK:-0.02}
POSITIONS=${POSITIONS:-3}
MIN_PRICE=${MIN_PRICE:-2}
MAX_PRICE=${MAX_PRICE:-20}
TOP_N=${TOP_N:-3}
DAYS=${DAYS:-90}
MIN_EV=${MIN_EV:-0.0003}
MIN_CONFIDENCE=${MIN_CONFIDENCE:-0.48}

echo "Configuration:"
echo "  Capital: \$$CAPITAL"
echo "  Risk per Trade: $(echo "$RISK * 100" | bc)%"
echo "  Max Positions: $POSITIONS"
echo "  Price Range: \$$MIN_PRICE-\$$MAX_PRICE"
echo "  Top Stocks: $TOP_N"
echo "  Backtest Period: $DAYS days"
echo "  Min EV: $MIN_EV ($(echo "$MIN_EV * 100" | bc)%)"
echo "  Min Win Prob: $MIN_CONFIDENCE ($(echo "$MIN_CONFIDENCE * 100" | bc)%)"
echo ""

# Run backtest
python backtest_full_system.py \
  --capital $CAPITAL \
  --risk $RISK \
  --positions $POSITIONS \
  --min-price $MIN_PRICE \
  --max-price $MAX_PRICE \
  --top-n $TOP_N \
  --days $DAYS \
  --min-ev $MIN_EV \
  --min-confidence $MIN_CONFIDENCE

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

