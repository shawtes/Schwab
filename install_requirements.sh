#!/bin/bash
# Install requirements script
# Run this from your conda environment

echo "Installing requirements for Ensemble Trading Model..."
echo "=================================================="

# Check if we're in a conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "WARNING: Not in a conda environment!"
    echo "Please activate your conda environment first:"
    echo "  conda activate newcondaenv"
    exit 1
fi

echo "Conda environment: $CONDA_DEFAULT_ENV"
echo "Python version: $(python --version)"
echo ""

# Install requirements
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo ""
echo "To verify installation, run:"
echo "  python -c 'import numpy, pandas, sklearn, dotenv; print(\"All packages installed!\")'"


