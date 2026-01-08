#!/usr/bin/env python3
"""
Python script to fetch stock price history for Node.js backend
Called from Express server via child_process.spawn
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Load .env from project root (Schwabdev directory)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to current directory
    load_dotenv()

import schwabdev

def main():
    if len(sys.argv) < 6:
        print(json.dumps({"error": "Invalid arguments. Expected: symbol periodType period frequencyType frequency"}))
        sys.exit(1)
    
    symbol = sys.argv[1]
    periodType = sys.argv[2]
    period = int(sys.argv[3])
    frequencyType = sys.argv[4]
    frequency = int(sys.argv[5])
    
    try:
        # Initialize Schwab client
        client = schwabdev.Client(
            os.getenv('app_key'),
            os.getenv('app_secret'),
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        
        # Fetch price history directly from Schwab API
        response = client.price_history(
            symbol,
            periodType=periodType,
            period=period,
            frequencyType=frequencyType,
            frequency=frequency
        )
        
        # Parse response
        data = response.json()
        
        if 'candles' not in data or not data['candles']:
            print(json.dumps({"error": "No data found", "symbol": symbol}))
            sys.exit(1)
        
        # Format candles for frontend
        candles = []
        for candle in data['candles']:
            candles.append({
                "datetime": candle.get('datetime'),  # Milliseconds since epoch
                "open": float(candle.get('open', 0)),
                "high": float(candle.get('high', 0)),
                "low": float(candle.get('low', 0)),
                "close": float(candle.get('close', 0)),
                "volume": int(candle.get('volume', 0))
            })
        
        result = {
            "symbol": symbol,
            "candles": candles,
            "count": len(candles)
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e), "symbol": symbol}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
