# Conda Environment Guide

## List Conda Environments

To see all available conda environments, run:

```bash
conda env list
```

Or:

```bash
conda info --envs
```

## Activate a Conda Environment

To activate a conda environment, use:

```bash
conda activate ENVIRONMENT_NAME
```

## For This Project

Based on our previous setup, you need to use Python 3.11+ because `schwabdev` requires Python 3.10+ (uses `match` statement).

### Recommended: Use `schwabdev` Environment

```bash
# Activate the schwabdev environment (Python 3.11+)
conda activate schwabdev
```

### If `schwabdev` Environment Doesn't Exist

Create it first:

```bash
# Create new environment with Python 3.11
conda create -n schwabdev python=3.11 -y

# Activate it
conda activate schwabdev

# Install dependencies
cd /Users/sineshawmesfintesfaye/Schwabdev
pip install numpy pandas scikit-learn python-dotenv imbalanced-learn
```

### Current Environment Issues

Your `newcondaenv` environment has Python 3.8, which **will NOT work** with `schwabdev` because it uses Python 3.10+ syntax (`match` statement).

## Verify Python Version

After activating an environment, verify:

```bash
python --version
# Should show: Python 3.11.x or higher (NOT 3.8)
```

## Deactivate Environment

To deactivate the current conda environment:

```bash
conda deactivate
```

## If Conda Command Not Found

If you get `command not found: conda`, you may need to initialize conda:

```bash
# For Anaconda (typical location)
source ~/anaconda3/etc/profile.d/conda.sh

# Or for Miniconda
source ~/miniconda3/etc/profile.d/conda.sh

# Or if installed in /opt
source /opt/anaconda3/etc/profile.d/conda.sh

# Then try again
conda env list
```

## Quick Reference

```bash
# List environments
conda env list

# Activate environment (Python 3.11+ required)
conda activate schwabdev

# Verify Python version
python --version

# Run your script
cd /Users/sineshawmesfintesfaye/Schwabdev
python ensemble_trading_model.py
```


