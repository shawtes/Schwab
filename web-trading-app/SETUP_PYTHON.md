# Python Environment Setup for Web Trading App

## Issue
The web app requires a Python virtual environment with specific dependencies. The system Python is externally managed and cannot install packages directly.

## Solution

### Option 1: Install Dependencies in Virtual Environment (Recommended)

The virtual environment has been created at `web-trading-app/venv/`. Install dependencies:

```bash
cd web-trading-app
source venv/bin/activate
pip install -r requirements.txt
```

If you get "No space left on device" error, free up disk space first.

### Option 2: Use Existing Python Environment

If you have a conda environment or another Python environment with the dependencies:

1. Update `server/src/server.ts` to use your Python path:
   ```typescript
   const PYTHON_PATH = '/path/to/your/python'; // e.g., conda env python
   ```

2. Or set it via environment variable in the server startup.

### Option 3: Install Minimal Dependencies Only

If disk space is limited, install only what's needed:

```bash
cd web-trading-app
source venv/bin/activate
pip install python-dotenv requests aiohttp cryptography websockets pandas numpy scikit-learn
```

## Required Dependencies

- `python-dotenv` - For loading .env file
- `requests` - HTTP requests (for schwabdev)
- `aiohttp` - Async HTTP (for schwabdev)
- `cryptography` - Encryption (for schwabdev)
- `websockets` - WebSocket support (for schwabdev)
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - Machine learning (for ensemble_trading_model)

## Verify Installation

```bash
cd web-trading-app
source venv/bin/activate
python fetch_stock_data.py AAPL day 1 minute 1
```

If successful, you should see JSON output with stock data.

## Server Configuration

The server automatically detects and uses the virtual environment Python at:
`web-trading-app/venv/bin/python`

If the venv doesn't exist, it falls back to `python3`.


