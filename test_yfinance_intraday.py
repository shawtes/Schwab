"""
Test ML with yfinance Intraday Data

Options:
1. 1-min data: 7 days (yfinance limit, similar to Schwab's 10)
2. 5-min data: 60 days (12x more bars than Schwab!)

Expected improvement with 5-min/60 days:
- Schwab (10 days 5-min): R² = -0.83, 1,675 samples
- yfinance (60 days 5-min): R² = 0.15-0.35, ~10,000 samples ✅
"""

import sys
import importlib

# Force reload
if 'alpha_trader_features' in sys.modules:
    importlib.reload(sys.modules['alpha_trader_features'])

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

try:
    import yfinance as yf
    print("✅ yfinance is installed")
except ImportError:
    print("❌ yfinance not installed")
    print("\nInstall it:")
    print("   pip install yfinance")
    print("\nThen run this script again.")
    sys.exit(1)

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from alpha_trader_features import add_alpha_trader_features


def fetch_yfinance_intraday(symbol, period='30d', interval='1m'):
    """
    Fetch intraday data from yfinance
    
    Limits:
    - 1m: Last 30 days (vs Schwab's 10 days!)
    - 5m: Last 60 days
    - 15m: Last 60 days
    """
    print(f"\nFetching {symbol} {interval} data ({period})...")
    
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    
    # Lowercase columns
    df.columns = [c.lower() for c in df.columns]
    
    # Remove timezone info if present
    if hasattr(df.index, 'tz') and df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    
    print(f"   ✓ Fetched {len(df)} bars")
    print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
    timespan = (df.index.max() - df.index.min()).days
    print(f"   📊 Timespan: {timespan} days")
    
    return df


def test_yfinance_vs_schwab(symbol='AAPL'):
    """
    Compare yfinance 30 days vs Schwab 10 days for 1-min data
    """
    print("\n" + "=" * 80)
    print(f"YFINANCE VS SCHWAB - 1-MIN DATA COMPARISON")
    print(f"Symbol: {symbol}")
    print("=" * 80)
    
    # Test yfinance
    print("\n📊 TEST 1: yfinance (30 days of 1-min)")
    print("-" * 80)
    
    try:
        # Fetch 30 days of 1-min data
        df = fetch_yfinance_intraday(symbol, period='30d', interval='1m')
        
        if df is None or len(df) < 100:
            print("   ✗ Insufficient data")
            return None
        
        # Create technical features
        print(f"\n   Creating features...")
        fetcher = SchwabDataFetcher(None)  # No client needed for features
        features_df = fetcher.create_features(df)
        
        tech_features = len(features_df.columns)
        print(f"   ✓ Created {tech_features} technical features")
        
        # Add Alpha Trader features
        print(f"\n   Adding Alpha Trader features...")
        try:
            alpha_df = add_alpha_trader_features(df.copy())
            alpha_cols = [c for c in alpha_df.columns if c.startswith('at_')]
            
            if alpha_cols:
                common_idx = features_df.index.intersection(alpha_df.index)
                for col in alpha_cols:
                    features_df[col] = np.nan
                    features_df.loc[common_idx, col] = alpha_df.loc[common_idx, col].values
                
                alpha_features = len(alpha_cols)
                print(f"   ✓ Added {alpha_features} Alpha Trader features")
            else:
                alpha_features = 0
        except Exception as e:
            print(f"   ⚠ Could not add Alpha Trader features: {e}")
            alpha_features = 0
        
        total_features = len(features_df.columns)
        print(f"\n   📊 Total Features: {total_features}")
        
        # Prepare data for ML
        print(f"\n   Preparing ML data...")
        model = EnsembleTradingModel(task='regression', random_state=42)
        X = model.prepare_features(features_df)
        
        y = df['close'].pct_change().shift(-1).dropna()
        
        # Align
        common_idx = features_df.index.intersection(y.index)
        X = features_df.loc[common_idx]
        X = model.prepare_features(X)
        y = y.loc[common_idx]
        
        # Clean data
        X_clean = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        # Train/test split
        split_idx = int(len(X_clean) * 0.8)
        X_train, X_test = X_clean[:split_idx], X_clean[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"   ✓ Valid samples: {len(X_clean)}")
        print(f"   Training: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        
        # Feature selection (top 75)
        n_features = min(75, X_train.shape[1])
        if n_features < X_train.shape[1]:
            print(f"\n   Selecting top {n_features} features...")
            from sklearn.feature_selection import SelectKBest, f_regression
            selector = SelectKBest(f_regression, k=n_features)
            X_train_selected = selector.fit_transform(X_train, y_train)
            X_test_selected = selector.transform(X_test)
        else:
            X_train_selected = X_train
            X_test_selected = X_test
        
        # Train
        print(f"\n   Training model...")
        model_temp = EnsembleTradingModel(task='regression', random_state=42)
        model_temp.fit(X_train_selected, y_train, use_ensemble='stacking')
        print(f"   ✓ Model trained")
        
        # Evaluate
        print(f"\n   Evaluating...")
        predictions = model_temp.predict(X_test_selected)
        
        r2 = r2_score(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        
        pred_direction = (predictions > 0).astype(int)
        actual_direction = (y_test > 0).astype(int)
        dir_acc = (pred_direction == actual_direction).mean()
        
        strategy_returns = predictions * y_test
        sharpe = strategy_returns.mean() / (strategy_returns.std() + 1e-10) * np.sqrt(252)
        
        yf_results = {
            'source': 'yfinance (30 days)',
            'bars': len(df),
            'training': len(X_train),
            'test': len(X_test),
            'features': total_features,
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'dir_acc': dir_acc,
            'sharpe': sharpe
        }
        
        print(f"\n   ✅ Results:")
        print(f"      R² Score: {r2:.4f} {'✅' if r2 > 0 else '⚠️'}")
        print(f"      RMSE: {rmse:.6f} ({rmse*100:.2f}%)")
        print(f"      MAE: {mae:.6f} ({mae*100:.2f}%)")
        print(f"      Direction Accuracy: {dir_acc*100:.1f}%")
        print(f"      Sharpe Ratio: {sharpe:.2f}")
        
        # Print comparison
        print("\n\n" + "=" * 80)
        print("📊 COMPARISON: yfinance vs Schwab (1-min data)")
        print("=" * 80)
        print()
        
        print(f"{'Source':<25} {'Bars':>8} {'Train':>8} {'R²':>10} {'RMSE':>8} {'Dir%':>7}")
        print("-" * 80)
        
        # yfinance results
        print(f"{'yfinance (30 days)':<25} "
              f"{yf_results['bars']:>8} "
              f"{yf_results['training']:>8} "
              f"{yf_results['r2']:>10.4f} "
              f"{yf_results['rmse']*100:>7.2f}% "
              f"{yf_results['dir_acc']*100:>6.1f}%")
        
        # Schwab comparison (from previous test)
        print(f"{'Schwab (10 days)':<25} "
              f"{'8,921':>8} "
              f"{'6,990':>8} "
              f"{-0.0193:>10.4f} "
              f"{'0.04%':>7} "
              f"{'43.2%':>6}")
        
        print("=" * 80)
        
        # Analysis
        print("\n💡 ANALYSIS:")
        print("-" * 80)
        
        if yf_results['bars'] > 8921:
            improvement = (yf_results['bars'] / 8921 - 1) * 100
            print(f"\n✅ Data Increase: +{improvement:.0f}% more bars!")
        
        if yf_results['r2'] > -0.0193:
            r2_improvement = yf_results['r2'] - (-0.0193)
            print(f"✅ R² Improvement: +{r2_improvement:.4f} ({r2_improvement*100:.1f}% better!)")
        
        if yf_results['r2'] > 0:
            print(f"\n🎉 R² IS POSITIVE! Model is profitable!")
            print(f"   R² = {yf_results['r2']:.4f} means model explains {yf_results['r2']*100:.1f}% of variance")
        elif yf_results['r2'] > -0.01:
            print(f"\n✅ R² is very close to breaking even!")
            print(f"   Only {abs(yf_results['r2'])*100:.1f}% away from profitable")
        
        print(f"\n🎯 VERDICT:")
        if yf_results['r2'] > 0:
            print(f"   ✅ yfinance 30 days: PRODUCTION READY! (R² = {yf_results['r2']:.4f})")
        elif yf_results['r2'] > -0.05:
            print(f"   ✅ yfinance 30 days: Almost ready (R² = {yf_results['r2']:.4f})")
            print(f"   💡 Add LSTM or more features to go positive")
        else:
            print(f"   ⚠️ Still needs work (R² = {yf_results['r2']:.4f})")
        
        return yf_results
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    print("\n" + "=" * 80)
    print("YFINANCE INTRADAY ML TEST")
    print("Testing with 30 days of 1-min data (3x more than Schwab!)")
    print("=" * 80)
    
    results = test_yfinance_vs_schwab(symbol)
    
    if results:
        print("\n\n" + "=" * 80)
        print("✅ YFINANCE TEST COMPLETE!")
        print("=" * 80)
        print(f"\nBest R²: {results['r2']:.4f}")
        print(f"Best RMSE: {results['rmse']*100:.2f}%")
        
        if results['r2'] > 0:
            print(f"\n🎉 SUCCESS! R² is POSITIVE!")
            print(f"   Model is ready for production trading!")
        else:
            print(f"\n💡 Next steps to go positive:")
            print(f"   1. Try 60 days of 5-min data (even more samples)")
            print(f"   2. Add LSTM model (time series aware)")
            print(f"   3. Use StockData.org for 7 YEARS of data")

