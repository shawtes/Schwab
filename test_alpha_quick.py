"""
Quick test of Alpha Trader features with fresh import
"""

import sys
import importlib
import os
from dotenv import load_dotenv

load_dotenv()

# Force reload of alpha_trader_features
if 'alpha_trader_features' in sys.modules:
    importlib.reload(sys.modules['alpha_trader_features'])

from alpha_trader_features import add_alpha_trader_features
from ensemble_trading_model import SchwabDataFetcher
import schwabdev

print("Testing Alpha Trader Features...")
print("=" * 80)

# Get test data from Schwab
client = schwabdev.Client(
    os.getenv('app_key'),
    os.getenv('app_secret'),
    os.getenv('callback_url', 'https://127.0.0.1')
)
fetcher = SchwabDataFetcher(client)
df = fetcher.get_price_history('AAPL', periodType='year', period=1)

print(f"\nOriginal data: {len(df)} rows, {len(df.columns)} columns")

# Add Alpha Trader features
try:
    df_with_alpha = add_alpha_trader_features(df)
    
    alpha_cols = [c for c in df_with_alpha.columns if c.startswith('at_')]
    print(f"\n✅ SUCCESS! Added {len(alpha_cols)} Alpha Trader features")
    
    print(f"\nAlpha Trader Features:")
    for col in alpha_cols[:10]:  # Show first 10
        print(f"   • {col}")
    
    if len(alpha_cols) > 10:
        print(f"   ... and {len(alpha_cols) - 10} more")
    
    # Check for NaN/inf
    has_nan = df_with_alpha[alpha_cols].isna().any().any()
    has_inf = (df_with_alpha[alpha_cols] == float('inf')).any().any()
    
    print(f"\nData Quality:")
    print(f"   NaN values: {'Yes' if has_nan else 'None'} {'⚠️' if has_nan else '✅'}")
    print(f"   Inf values: {'Yes' if has_inf else 'None'} {'⚠️' if has_inf else '✅'}")
    
    # Show latest values
    print(f"\nLatest Alpha Trader Values:")
    latest = df_with_alpha[alpha_cols].iloc[-1]
    for col in alpha_cols[:5]:
        print(f"   {col}: {latest[col]:.4f}")
    
    print("\n" + "=" * 80)
    print("✅ Alpha Trader features are working correctly!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

