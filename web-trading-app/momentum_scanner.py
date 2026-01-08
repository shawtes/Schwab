#!/usr/bin/env python3
"""
Momentum Scanner - Scans all stocks for momentum trading opportunities
Uses real-time data from Schwab API
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import warnings
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Suppress warnings
warnings.filterwarnings('ignore')

# Load .env from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

import schwabdev

# Import comprehensive stock universe
try:
    from stock_universe import get_comprehensive_universe
    COMPREHENSIVE_UNIVERSE_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_UNIVERSE_AVAILABLE = False

def get_stock_universe(client, use_cache=True, fetch_all=True):
    """
    Fetch all available stocks from Schwab API
    Falls back to popular stocks if API fails
    
    Args:
        client: Schwab API client
        use_cache: Whether to use cached results (future implementation)
        fetch_all: If True, fetches ALL stocks from Schwab. If False, uses curated list.
    """
    
    # Fallback list of popular liquid stocks (in case API fails)
    FALLBACK_UNIVERSE = [
        # Tech Giants
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "NFLX", "AVGO", "QCOM", "TXN", "ADI",
        # Finance
        "JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA", "AXP", "BLK", "SCHW", "BK", "USB", "TFC", "PNC",
        # Healthcare
        "JNJ", "UNH", "PFE", "ABBV", "TMO", "MRK", "ABT", "DHR", "LLY", "BMY", "AMGN", "GILD", "REGN", "VRTX", "BIIB",
        # Consumer
        "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "COST", "LOW", "DIS", "CMCSA", "KO", "PEP", "PM", "MO", "PG",
        # Energy
        "XOM", "CVX", "COP", "SLB", "EOG", "PXD", "MPC", "PSX", "VLO", "OXY", "HAL", "BKR", "WMB", "KMI", "OKE",
        # Industrials
        "BA", "CAT", "GE", "HON", "UPS", "RTX", "LMT", "DE", "MMM", "UNP", "FDX", "NSC", "CSX", "EMR", "ETN",
        # Communication
        "T", "VZ", "TMUS", "CHTR", "NFLX", "DIS", "PARA",
        # Materials
        "LIN", "APD", "ECL", "DD", "DOW", "NEM", "FCX", "NUE", "VMC", "MLM",
        # Real Estate REITs
        "PLD", "AMT", "CCI", "EQIX", "SPG", "PSA", "O", "WELL", "DLR", "AVB",
        # Utilities
        "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "ED", "ES",
        # Growth/Momentum
        "RIVN", "LCID", "PLTR", "SOFI", "COIN", "RBLX", "SNAP", "UBER", "LYFT", "DASH", "ABNB",
        "SQ", "PYPL", "SHOP", "ROKU", "ZM", "DOCU", "CRWD", "NET", "DDOG", "SNOW", "MDB",
        # Top 100 S&P 500
        "TSLA", "BRK.B", "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "LLY", "TSM",
        "V", "WMT", "JPM", "XOM", "UNH", "MA", "AVGO", "JNJ", "PG", "HD",
        "ORCL", "MRK", "CVX", "ABBV", "COST", "KO", "PEP", "ADBE", "CRM", "NFLX",
        "BAC", "TMO", "MCD", "CSCO", "ACN", "WFC", "LIN", "ABT", "INTC", "AMD",
        "DHR", "CMCSA", "PM", "TXN", "DIS", "INTU", "VZ", "IBM", "COP", "QCOM",
        # ETFs
        "SPY", "QQQ", "IWM", "DIA", "EEM", "EFA", "VTI", "VOO", "VEA", "AGG"
    ]
    
    if not fetch_all:
        print(f"Using curated universe of {len(set(FALLBACK_UNIVERSE))} liquid stocks", file=sys.stderr)
        return list(set(FALLBACK_UNIVERSE))
    
    # First, try to use comprehensive pre-compiled universe (1100+ stocks)
    if COMPREHENSIVE_UNIVERSE_AVAILABLE:
        try:
            comprehensive_list = get_comprehensive_universe()
            if len(comprehensive_list) > 500:
                print(f"✅ Using comprehensive universe of {len(comprehensive_list)} stocks!", file=sys.stderr)
                print(f"   Covers: S&P 500, NASDAQ 100, Russell 2000, Meme stocks, Crypto, Growth Tech", file=sys.stderr)
                return comprehensive_list
        except Exception as e:
            print(f"Error loading comprehensive universe: {e}", file=sys.stderr)
    
    # If comprehensive list not available, try API fetch
    try:
        print("Fetching ALL available stocks from Schwab API...", file=sys.stderr)
        
        # Strategy: Use regex patterns to search for all symbols
        all_symbols = set()
        
        # Approach 1: Try broad regex search for all uppercase symbols (common stock pattern)
        try:
            print("  Trying broad symbol search...", file=sys.stderr)
            # Try searching for all symbols with 1-5 capital letters
            response = client.instruments("[A-Z]{1,5}", "symbol-regex")
            data = response.json()
            
            if 'instruments' in data and len(data['instruments']) > 0:
                print(f"  Found {len(data['instruments'])} instruments from regex search", file=sys.stderr)
                for instrument in data['instruments']:
                    symbol = instrument.get('symbol', '')
                    asset_type = instrument.get('assetType', '')
                    
                    # Filter for equities only
                    if asset_type in ['EQUITY', 'COMMON_STOCK'] and symbol and len(symbol) <= 5:
                        all_symbols.add(symbol)
        except Exception as e:
            print(f"  Regex search failed: {e}", file=sys.stderr)
        
        # Approach 2: If regex didn't work, try letter-by-letter with desc-search
        if len(all_symbols) == 0:
            print("  Trying letter-by-letter search...", file=sys.stderr)
            import string
            for letter in string.ascii_uppercase:
                try:
                    # Use desc-search which is more permissive
                    response = client.instruments(letter, "desc-search")
                    data = response.json()
                    
                    if 'instruments' in data:
                        for instrument in data['instruments']:
                            symbol = instrument.get('symbol', '')
                            asset_type = instrument.get('assetType', '')
                            description = instrument.get('description', '')
                            
                            # Filter for equities only and symbols starting with letter
                            if (asset_type in ['EQUITY', 'COMMON_STOCK'] and 
                                symbol and symbol[0] == letter and len(symbol) <= 5):
                                all_symbols.add(symbol)
                    
                    if len(data.get('instruments', [])) > 0:
                        print(f"  {letter}: +{len(data.get('instruments', []))} instruments", file=sys.stderr)
                    
                except Exception as e:
                    print(f"  Error on {letter}: {e}", file=sys.stderr)
                    continue
        
        if len(all_symbols) > 100:  # Reasonable threshold
            symbols_list = sorted(list(all_symbols))
            print(f"✅ Successfully fetched {len(symbols_list)} stocks from Schwab API!", file=sys.stderr)
            # Filter out obvious non-stocks (options, etc.)
            filtered = [s for s in symbols_list if s.isalpha() and len(s) <= 5]
            print(f"✅ Filtered to {len(filtered)} valid stock symbols", file=sys.stderr)
            return filtered if len(filtered) > 100 else symbols_list
        else:
            raise Exception(f"Insufficient symbols found: {len(all_symbols)}")
            
    except Exception as e:
        print(f"⚠️  API fetch failed: {e}", file=sys.stderr)
        print(f"⚠️  Falling back to comprehensive curated list", file=sys.stderr)
        return list(set(FALLBACK_UNIVERSE))

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down if down != 0 else 0
    rsi = 100. - 100./(1. + rs)
    return rsi

def calculate_momentum_score(stock_data):
    """Calculate momentum score (0-100) based on multiple factors"""
    score = 0
    
    # Price momentum (0-30 points)
    pct_change = stock_data.get('percentChange', 0)
    if pct_change > 10:
        score += 30
    elif pct_change > 7:
        score += 25
    elif pct_change > 5:
        score += 20
    elif pct_change > 3:
        score += 15
    elif pct_change > 1:
        score += 10
    
    # Volume momentum (0-25 points)
    rvol = stock_data.get('rvol', 1.0)
    if rvol > 4:
        score += 25
    elif rvol > 3:
        score += 20
    elif rvol > 2:
        score += 15
    elif rvol > 1.5:
        score += 10
    elif rvol > 1.2:
        score += 5
    
    # RSI strength (0-25 points)
    rsi = stock_data.get('rsi', 50)
    if 60 <= rsi <= 75:
        score += 25
    elif 55 <= rsi < 60:
        score += 20
    elif 75 < rsi <= 80:
        score += 15
    elif 50 <= rsi < 55:
        score += 10
    
    # Volume threshold (0-20 points)
    volume = stock_data.get('volume', 0)
    if volume > 50000000:
        score += 20
    elif volume > 20000000:
        score += 15
    elif volume > 10000000:
        score += 10
    elif volume > 5000000:
        score += 5
    
    return min(score, 100)

def get_trend_strength(score):
    """Determine trend strength based on score"""
    if score >= 75:
        return "strong"
    elif score >= 60:
        return "moderate"
    else:
        return "weak"

def scan_momentum_stocks(filters, custom_symbols=None):
    """Scan stocks for momentum opportunities"""
    try:
        # Initialize Schwab client
        client = schwabdev.Client(
            os.getenv('app_key'),
            os.getenv('app_secret'),
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        
        # Get stock universe (use custom symbols if provided, otherwise fetch all)
        if custom_symbols:
            stock_universe = custom_symbols
        else:
            stock_universe = get_stock_universe(client, fetch_all=True)
        
        print(f"Scanning {len(stock_universe)} stocks for momentum...", file=sys.stderr)
        
        # Fetch quotes for all symbols (Schwab API can handle batch requests)
        # Split into chunks of 500 to avoid URL length limits
        chunk_size = 500
        all_quotes_data = {}
        
        for i in range(0, len(stock_universe), chunk_size):
            chunk = stock_universe[i:i+chunk_size]
            symbols_str = ','.join(chunk)
            try:
                response = client.quotes(symbols_str)
                quotes_data = response.json()
                all_quotes_data.update(quotes_data)
            except Exception as e:
                print(f"Error fetching quotes for chunk {i//chunk_size + 1}: {e}", file=sys.stderr)
                continue
        
        results = []
        
        for symbol in stock_universe:
            try:
                if symbol not in all_quotes_data:
                    continue
                
                quote = all_quotes_data[symbol].get('quote', {})
                
                # Extract data
                price = quote.get('lastPrice', 0)
                change = quote.get('netChange', 0)
                percent_change = quote.get('netPercentChange', 0)
                volume = quote.get('totalVolume', 0)
                
                # Calculate average volume (estimate based on typical volume patterns)
                # In production, you'd fetch historical data for accurate avg volume
                # For now, use 52-week high volume as proxy, or estimate based on price/volume ratio
                week_52_high_vol = quote.get('52WkHigh', price) * 10000000  # Rough estimate
                avg_volume = week_52_high_vol / 252  # Daily average estimate
                if avg_volume == 0:
                    avg_volume = 10000000  # Default fallback
                rvol = volume / avg_volume if avg_volume > 0 else 1.0
                rvol = min(rvol, 10.0)  # Cap at 10x for realistic values
                
                # For RSI, we'd need historical data. For now, estimate from price action
                # In production, fetch historical candles and calculate proper RSI
                # Map percent change to RSI range (more realistic distribution)
                if percent_change > 5:
                    rsi = 70 + min(percent_change - 5, 10)
                elif percent_change > 2:
                    rsi = 60 + (percent_change - 2) * 3.3
                elif percent_change > 0:
                    rsi = 50 + percent_change * 5
                elif percent_change > -2:
                    rsi = 50 + percent_change * 5
                elif percent_change > -5:
                    rsi = 40 + (percent_change + 2) * 3.3
                else:
                    rsi = 30 + max(percent_change + 5, -10)
                rsi = max(0, min(100, rsi))
                
                # Apply filters
                if price < filters.get('minPrice', 0):
                    continue
                if price > filters.get('maxPrice', 999999):
                    continue
                if percent_change < filters.get('minPercentChange', 0):
                    continue
                if rvol < filters.get('minRVOL', 0):
                    continue
                if volume < filters.get('minVolume', 0):
                    continue
                if rsi < filters.get('rsiMin', 0) or rsi > filters.get('rsiMax', 100):
                    continue
                
                # Calculate momentum data
                stock_data = {
                    'percentChange': percent_change,
                    'rvol': rvol,
                    'rsi': rsi,
                    'volume': volume
                }
                
                score = calculate_momentum_score(stock_data)
                
                # Only include stocks with some momentum score
                # Lower threshold to show results even in slow markets
                if score < 30:
                    continue
                
                result = {
                    'symbol': symbol,
                    'price': round(price, 2),
                    'change': round(change, 2),
                    'percentChange': round(percent_change, 2),
                    'volume': int(volume),
                    'rvol': round(rvol, 2),
                    'rsi': int(rsi),
                    'macd': 0,  # Would calculate from historical data
                    'score': score,
                    'trend': get_trend_strength(score)
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}", file=sys.stderr)
                continue
        
        # Sort by momentum score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit to top 50 for performance
        results = results[:50]
        
        print(f"Found {len(results)} momentum stocks", file=sys.stderr)
        
        return {
            'results': results,
            'scanTime': datetime.now().isoformat(),
            'totalScanned': len(stock_universe),
            'totalFound': len(results)
        }
        
    except Exception as e:
        print(f"Error in momentum scan: {e}", file=sys.stderr)
        return {
            'results': [],
            'error': str(e)
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Filters required"}))
        sys.exit(1)
    
    try:
        filters = json.loads(sys.argv[1])
        result = scan_momentum_stocks(filters)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

