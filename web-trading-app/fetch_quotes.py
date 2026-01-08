#!/usr/bin/env python3
"""
Python script to fetch quotes for Node.js backend
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')

# Redirect stderr to suppress debug output
import io
sys.stderr = io.StringIO()

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env from project root (Schwabdev directory)
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to current directory
    load_dotenv()

import schwabdev

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    symbols_str = sys.argv[1]
    symbols = [s.strip().upper() for s in symbols_str.split(',')]
    
    try:
        # Initialize client (suppress any print output)
        client = schwabdev.Client(
            os.getenv('app_key'),
            os.getenv('app_secret'),
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        
        # Fetch quotes from Schwab API directly
        quotes_response = client.quotes(symbols).json()
        
        result = {}
        for symbol in symbols:
            if symbol in quotes_response:
                quote_data = quotes_response[symbol]
                # Extract quote details
                if 'quote' in quote_data:
                    quote = quote_data['quote']
                else:
                    quote = quote_data
                    
                result[symbol] = {
                    "quote": {
                        "lastPrice": quote.get('lastPrice', 0),
                        "netChange": quote.get('netChange', 0),
                        "netPercentChange": quote.get('netPercentChangeInDouble', 0),
                        "bidPrice": quote.get('bidPrice', 0),
                        "askPrice": quote.get('askPrice', 0),
                        "totalVolume": quote.get('totalVolume', 0)
                    }
                }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()

