# Quick Start Guide

## Issue: Python Version Requirement

Your conda environment is using Python 3.8, but schwabdev requires Python 3.11 or higher.

## Solution Options

### Option 1: Create a New Conda Environment with Python 3.11+ (Recommended)

```bash
# Create a new conda environment with Python 3.11
conda create -n schwabdev python=3.11
conda activate schwabdev

# Install schwabdev from PyPI
pip install schwabdev python-dotenv

# OR install from source (if you want to modify the code)
pip install -e . python-dotenv
```

### Option 2: Use the Source Code Directly (Current Environment)

Since you have the source code and dependencies installed, you can try using it directly. However, **this may not work properly** with Python 3.8 due to version requirements.

To use the source code directly:

1. Add the schwabdev directory to your Python path, or
2. Run scripts from the project directory and import schwabdev directly

Example:
```python
import sys
sys.path.insert(0, '/Users/sineshawmesfintesfaye/Schwabdev')
import schwabdev
```

## Next Steps After Fixing Python Version

1. **Set up your credentials**:
   ```bash
   python setup_schwab.py
   ```
   Or manually create a `.env` file with:
   ```
   app_key=YOUR_APP_KEY
   app_secret=YOUR_APP_SECRET
   callback_url=https://127.0.0.1
   ```

2. **Test your setup**:
   ```bash
   python docs/examples/api_demo.py
   ```

## Getting Your Credentials

1. Go to https://developer.schwab.com/dashboard/apps
2. Create an app (if you haven't) with callback URL: `https://127.0.0.1`
3. Add both API products:
   - Accounts and Trading Production
   - Market Data Production
4. Wait until status is "Ready for use"
5. Copy your App Key and App Secret


