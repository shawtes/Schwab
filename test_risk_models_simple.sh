#!/bin/bash
# Test Risk Models with schwabdev conda environment
# Usage: conda activate schwabdev && bash test_risk_models_simple.sh

echo "======================================================================"
echo "Testing Risk Models (GARCH + Copula)"
echo "======================================================================"
echo ""

echo "Python version:"
python --version
echo ""

echo "======================================================================"
echo "Test 1: GARCH Volatility Model"
echo "======================================================================"
python ml_trading/models/garch_model.py
echo ""

echo "======================================================================"
echo "Test 2: Copula Correlation Model"
echo "======================================================================"
python ml_trading/models/copula_model.py
echo ""

echo "======================================================================"
echo "Test 3: Risk Feature Integration"
echo "======================================================================"
python ml_trading/pipeline/risk_feature_integrator.py
echo ""

echo "======================================================================"
echo "Test 4: Enhanced ML Pipeline"
echo "======================================================================"
python ml_trading/pipeline/enhanced_ml_pipeline.py
echo ""

echo "======================================================================"
echo "✅ ALL TESTS COMPLETE!"
echo "======================================================================"
echo ""
echo "To test with real Schwab API data:"
echo "  python test_risk_integration.py"
echo ""

