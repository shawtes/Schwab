# Installation Instructions

## Requirements File Created

I've created `requirements.txt` with all necessary packages for the Ensemble Trading Model.

## Installation Steps

### Option 1: Using Conda Environment (Recommended)

Since you're using a conda environment, activate it first and then install:

```bash
# Activate your conda environment
conda activate newcondaenv  # or whatever your env name is

# Install all requirements
pip install -r requirements.txt

# OR install packages individually
pip install numpy pandas scikit-learn python-dotenv
```

### Option 2: Using the Installation Script

```bash
# Make sure you're in your conda environment first
conda activate newcondaenv

# Run the installation script
bash install_requirements.sh
```

## Required Packages

The `requirements.txt` file includes:

### Core Packages (Required)
- **numpy** >= 1.24.0 - Numerical computing
- **pandas** >= 2.0.0 - Data manipulation
- **scikit-learn** >= 1.3.0 - Machine learning
- **python-dotenv** >= 1.0.0 - Environment variables

### Schwab API
- Using source code (no installation needed - already in this directory)
- OR install from PyPI: `pip install schwabdev` (requires Python 3.11+)

### Optional Packages (Commented in requirements.txt)
- xgboost, lightgbm, catboost - Advanced boosting libraries
- matplotlib, seaborn, plotly - Visualization
- scipy, statsmodels - Statistical analysis
- jupyter, notebook - Development environment

## Verify Installation

After installing, verify all packages are available:

```bash
# In your conda environment
python -c "import numpy, pandas, sklearn; print('✓ All packages installed!')"
```

## Running the Ensemble Model

Once packages are installed in your conda environment:

```bash
# Make sure you're in the conda environment
conda activate newcondaenv

# Run the ensemble model
python ensemble_trading_model.py
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"
**Solution**: Make sure you're in your conda environment where packages are installed.

### Issue: "schwabdev not found"
**Solution**: You're using the source code, so this is fine. Make sure you run scripts from the project directory.

### Issue: Python version mismatch
**Solution**: Use your conda environment which has the correct Python version (3.11+ for schwabdev from PyPI, or any version for source code).

## Current Status

✅ `requirements.txt` created
✅ Installation script created (`install_requirements.sh`)
✅ All core packages listed

**Next Step**: Install packages in your conda environment using the commands above.


