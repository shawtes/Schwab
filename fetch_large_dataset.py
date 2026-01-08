"""
Fetch Large Training Dataset from Schwab API
Schwab API Limits:
- Daily data: Up to 20 years
- Minute data: Up to 10 days (limited)
"""

import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()

from ensemble_trading_model import SchwabDataFetcher
import schwabdev


def fetch_maximum_data(symbol, frequency='daily'):
    """
    Fetch maximum available data from Schwab API
    
    Schwab API Limits:
    - Daily: periodType='year', period=20 (20 years!)
    - Weekly: periodType='year', period=20
    - Monthly: periodType='year', period=20
    - Minute (30-min): periodType='day', period=10 (10 days max)
    """
    print("=" * 80)
    print(f"FETCHING MAXIMUM DATA: {symbol} ({frequency})")
    print("=" * 80)
    
    # Initialize
    print("\n1. Initializing Schwab API...")
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    # Fetch based on frequency
    if frequency == 'daily':
        print("\n2. Fetching MAXIMUM daily data (up to 20 years)...")
        df = fetcher.get_price_history(
            symbol,
            periodType='year',
            period=20,  # ← MAXIMUM: 20 years!
            frequencyType='daily',
            frequency=1
        )
    
    elif frequency == 'weekly':
        print("\n2. Fetching MAXIMUM weekly data (up to 20 years)...")
        df = fetcher.get_price_history(
            symbol,
            periodType='year',
            period=20,  # ← MAXIMUM: 20 years!
            frequencyType='weekly',
            frequency=1
        )
    
    elif frequency == 'monthly':
        print("\n2. Fetching MAXIMUM monthly data (up to 20 years)...")
        df = fetcher.get_price_history(
            symbol,
            periodType='year',
            period=20,  # ← MAXIMUM: 20 years!
            frequencyType='monthly',
            frequency=1
        )
    
    elif frequency == '30min':
        print("\n2. Fetching MAXIMUM 30-min data (up to 10 days)...")
        df = fetcher.get_price_history(
            symbol,
            periodType='day',
            period=10,  # ← MAXIMUM: 10 days for intraday
            frequencyType='minute',
            frequency=30
        )
    
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")
    
    if df is None or len(df) == 0:
        print("   ✗ Failed to fetch data")
        return None
    
    print(f"   ✓ Fetched {len(df)} bars")
    print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
    print(f"   📊 Timespan: {(df.index.max() - df.index.min()).days} days")
    
    return df


def fetch_multiple_stocks_large_dataset(symbols, frequency='daily'):
    """
    Fetch large dataset for multiple stocks
    """
    print("\n" + "=" * 80)
    print(f"FETCHING LARGE DATASETS FOR {len(symbols)} STOCKS")
    print("=" * 80)
    
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    results = {}
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Fetching {symbol}...")
        
        try:
            if frequency == 'daily':
                df = fetcher.get_price_history(
                    symbol,
                    periodType='year',
                    period=20,  # 20 years
                    frequencyType='daily',
                    frequency=1
                )
            else:
                df = fetcher.get_price_history(
                    symbol,
                    periodType='year',
                    period=10,  # 10 years
                    frequencyType='daily',
                    frequency=1
                )
            
            if df is not None and len(df) > 0:
                results[symbol] = df
                timespan = (df.index.max() - df.index.min()).days
                print(f"   ✓ {len(df)} bars ({timespan} days)")
            else:
                print(f"   ✗ No data")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ Fetched data for {len(results)}/{len(symbols)} stocks")
    print("=" * 80)
    
    return results


def save_large_dataset(symbol, df, filename=None):
    """
    Save large dataset to CSV for reuse
    """
    if filename is None:
        filename = f"data/{symbol}_large_dataset.csv"
    
    import os
    os.makedirs('data', exist_ok=True)
    
    df.to_csv(filename)
    print(f"\n💾 Saved to: {filename}")
    print(f"   Size: {len(df)} rows")
    print(f"   File size: {os.path.getsize(filename) / 1024:.1f} KB")


def demo_large_dataset():
    """
    Demo: Fetch and compare dataset sizes
    """
    print("\n" + "=" * 80)
    print("DEMO: Small vs Large Dataset")
    print("=" * 80)
    
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    symbol = 'AAPL'
    
    # Small dataset (current)
    print("\n📊 CURRENT APPROACH: 1 year of data")
    print("-" * 80)
    df_small = fetcher.get_price_history(
        symbol,
        periodType='year',
        period=1,
        frequencyType='daily',
        frequency=1
    )
    
    if df_small is not None:
        print(f"   Bars: {len(df_small)}")
        print(f"   Date range: {df_small.index.min()} to {df_small.index.max()}")
        print(f"   Training samples (after features): ~{int(len(df_small) * 0.5)}")
    
    # Large dataset (recommended)
    print("\n📊 RECOMMENDED: 10 years of data")
    print("-" * 80)
    df_large = fetcher.get_price_history(
        symbol,
        periodType='year',
        period=10,  # 10 years
        frequencyType='daily',
        frequency=1
    )
    
    if df_large is not None:
        print(f"   Bars: {len(df_large)}")
        print(f"   Date range: {df_large.index.min()} to {df_large.index.max()}")
        print(f"   Training samples (after features): ~{int(len(df_large) * 0.5)}")
    
    # Comparison
    if df_small is not None and df_large is not None:
        print("\n" + "=" * 80)
        print("📈 COMPARISON")
        print("=" * 80)
        print(f"\nData Points:")
        print(f"   1 year:  {len(df_small)} bars")
        print(f"   10 years: {len(df_large)} bars")
        print(f"   Increase: {len(df_large) - len(df_small)} bars (+{(len(df_large)/len(df_small) - 1)*100:.0f}%)")
        
        print(f"\nTraining Samples (after feature engineering):")
        train_small = int(len(df_small) * 0.5)
        train_large = int(len(df_large) * 0.5)
        print(f"   1 year:  ~{train_small} samples")
        print(f"   10 years: ~{train_large} samples")
        print(f"   Increase: +{train_large - train_small} samples")
        
        print(f"\n💡 Recommendation:")
        print(f"   Use 5-10 years for daily ML training")
        print(f"   Expected R² improvement: -0.48 → 0.3-0.6")


def quick_fix_your_code():
    """
    Show how to quickly fix the existing test to use more data
    """
    print("\n" + "=" * 80)
    print("🔧 QUICK FIX: Update Your Test Script")
    print("=" * 80)
    
    print("""
Current code in test_full_ml_system.py (line ~47):
    df = fetcher.get_price_history(symbol, periodType='year', period=1)
    #                                                           ^^^^^^ 1 year

CHANGE TO:
    df = fetcher.get_price_history(symbol, periodType='year', period=10)
    #                                                           ^^^^^^^ 10 years

Or for maximum data:
    df = fetcher.get_price_history(symbol, periodType='year', period=20)
    #                                                           ^^^^^^^ 20 years!

This ONE change will give you 10x more training data!
    """)


if __name__ == '__main__':
    import sys
    
    # Quick fix instructions
    quick_fix_your_code()
    
    # Demo comparison
    print("\n" + "=" * 80)
    print("Running demo comparison...")
    print("=" * 80)
    
    demo_large_dataset()
    
    # Fetch example
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        print(f"\n\nFetching maximum data for {symbol}...")
        df = fetch_maximum_data(symbol, frequency='daily')
        
        if df is not None:
            save_large_dataset(symbol, df)

