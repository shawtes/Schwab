#!/usr/bin/env python3
"""
Python script to screen stocks for Node.js backend
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

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
from stock_screener import StockScreener

def calculate_signal(row):
    """Calculate trading signal"""
    rsi = row.get('RSI', 50)
    macd_hist = row.get('MACD_Hist', 0)
    momentum = row.get('Momentum_20', 0)
    
    buy_signals = 0
    sell_signals = 0
    
    if rsi < 40:
        buy_signals += 1
    elif rsi > 60:
        sell_signals += 1
    
    if macd_hist > 0:
        buy_signals += 1
    else:
        sell_signals += 1
    
    if momentum > 0:
        buy_signals += 1
    else:
        sell_signals += 1
    
    if buy_signals >= 2:
        return "BUY"
    elif sell_signals >= 2:
        return "SELL"
    else:
        return "HOLD"

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    symbols_str = sys.argv[1]
    filters_json = sys.argv[2]
    
    symbols = [s.strip().upper() for s in symbols_str.split(',')]
    filters = json.loads(filters_json) if filters_json else {}
    
    try:
        client = schwabdev.Client(
            os.getenv('app_key'),
            os.getenv('app_secret'),
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        
        screener = StockScreener(client)
        
        # Fetch and process
        screener.fetch_stocks(symbols, periodType='year', period=1, frequencyType='daily', frequency=1)
        screener.calculate_indicators()
        
        # Create summary
        summary_df = screener.create_summary_dataframe(include_quotes=True)
        
        # Apply filters
        if filters:
            summary_df = screener.filter_stocks(summary_df, filters={
                'RSI': (filters.get('rsiMin'), filters.get('rsiMax')),
                'MACD_Hist': (0, None) if filters.get('macdPositive') else None,
                'Volume_Ratio': (filters.get('volumeMin'), None) if filters.get('volumeMin') else None,
            })
        
        # Convert to JSON
        result = []
        for _, row in summary_df.iterrows():
            result.append({
                "symbol": str(row.get('Symbol', '')),
                "price": float(row.get('Current_Price', 0)),
                "rsi": float(row.get('RSI', 0)),
                "macd": float(row.get('MACD', 0)),
                "macdHist": float(row.get('MACD_Hist', 0)),
                "volumeRatio": float(row.get('Volume_Ratio', 0)),
                "momentum": float(row.get('Momentum_20', 0)),
                "alphaSharpe": float(row.get('Alpha_Sharpe_20', 0)),
                "returns21d": float(row.get('Returns_21d', 0)),
                "signal": calculate_signal(row)
            })
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

