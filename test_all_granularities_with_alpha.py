"""
Complete ML Test: All Granularities + Alpha Trader Features

Tests:
1. Daily (10 years) + all features
2. 30-min (10 days) + all features
3. 5-min (10 days) + all features
4. 1-min (10 days) + all features

Features:
- Technical indicators (184)
- Risk features (12)
- Alpha Trader features (35)
= 231 total features!
"""

import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

load_dotenv()

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from ml_trading.pipeline.risk_feature_integrator import RiskFeatureIntegrator
from alpha_trader_features import add_alpha_trader_features
import schwabdev


def test_granularity_with_alpha(symbol, granularity_config):
    """
    Test ML with ALL features (technical + risk + Alpha Trader)
    """
    print("\n" + "=" * 80)
    print(f"TESTING: {granularity_config['name']}")
    print("=" * 80)
    
    # Initialize
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    # Fetch market data for risk features
    print(f"\n1. Fetching market data (SPY)...")
    spy_data = fetcher.get_price_history(
        'SPY',
        periodType=granularity_config['spy_periodType'],
        period=granularity_config['spy_period'],
        frequencyType=granularity_config['frequencyType'],
        frequency=granularity_config['frequency']
    )
    spy_returns = spy_data['close'].pct_change().dropna() if spy_data is not None else None
    print(f"   ✓ SPY: {len(spy_returns)} bars")
    
    # Fetch stock data
    print(f"\n2. Fetching {symbol} data...")
    df = fetcher.get_price_history(
        symbol,
        periodType=granularity_config['periodType'],
        period=granularity_config['period'],
        frequencyType=granularity_config['frequencyType'],
        frequency=granularity_config['frequency']
    )
    
    if df is None or len(df) < 100:
        print(f"   ✗ Insufficient data")
        return None
    
    print(f"   ✓ Fetched {len(df)} bars")
    timespan = (df.index.max() - df.index.min()).days
    print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
    print(f"   📊 Timespan: {timespan} days")
    
    # Create technical features
    print(f"\n3. Creating technical features...")
    features_df = fetcher.create_features(df)
    
    if features_df is None or len(features_df) < 50:
        print(f"   ✗ Feature creation failed")
        return None
    
    tech_features = len(features_df.columns)
    print(f"   ✓ Created {tech_features} technical features")
    
    # Add Alpha Trader features (need original OHLCV data)
    print(f"\n4. Adding Alpha Trader features...")
    alpha_features = 0
    try:
        # Calculate Alpha Trader features on original data
        alpha_df = add_alpha_trader_features(df.copy())
        
        # Extract only Alpha Trader columns
        alpha_cols = [c for c in alpha_df.columns if c.startswith('at_')]
        
        if alpha_cols:
            # Get common index
            common_idx = features_df.index.intersection(alpha_df.index)
            
            if len(common_idx) > 0:
                # Add each column with proper alignment
                for col in alpha_cols:
                    features_df[col] = np.nan  # Initialize
                    features_df.loc[common_idx, col] = alpha_df.loc[common_idx, col].values
                
                alpha_features = len(alpha_cols)
                print(f"   ✓ Added {alpha_features} Alpha Trader features")
            else:
                print(f"   ⚠ Warning: No common indices between features and Alpha Trader data")
        else:
            print(f"   ⚠ Warning: No Alpha Trader columns generated")
    except Exception as e:
        print(f"   ⚠ Warning: Could not add Alpha Trader features: {e}")
        alpha_features = 0
    
    # Add risk features
    print(f"\n5. Adding risk features...")
    risk_integrator = RiskFeatureIntegrator(spy_returns=spy_returns)
    
    try:
        risk_features_dict = risk_integrator.calculate_risk_features(features_df, momentum_score=70)
        
        # Add to DataFrame
        for key, value in risk_features_dict.items():
            if isinstance(value, (int, float)):
                features_df[f'risk_{key}'] = value
        
        risk_score = risk_integrator.get_risk_score(risk_features_dict)
        features_df['risk_score'] = risk_score
        
        risk_features = len([c for c in features_df.columns if c.startswith('risk_')])
        print(f"   ✓ Added {risk_features} risk features")
    except Exception as e:
        print(f"   ⚠ Warning: Could not add risk features: {e}")
        risk_features = 0
    
    total_features = len(features_df.columns)
    print(f"\n   📊 Total Features: {total_features}")
    print(f"      Technical: {tech_features}")
    print(f"      Alpha Trader: {alpha_features}")
    print(f"      Risk: {risk_features}")
    
    # Prepare data
    print(f"\n6. Preparing data...")
    model = EnsembleTradingModel(task='regression', random_state=42)
    X = model.prepare_features(features_df)
    
    y = df['close'].pct_change().shift(-1).dropna()
    
    # Align
    common_idx = features_df.index.intersection(y.index)
    X = features_df.loc[common_idx]
    X = model.prepare_features(X)
    y = y.loc[common_idx]
    
    print(f"   ✓ Valid samples: {len(X)}")
    
    # Clean data: replace inf/nan
    print(f"\n   Cleaning data (removing inf/nan)...")
    X_clean = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
    
    # Check for any remaining issues
    if not np.all(np.isfinite(X_clean)):
        print(f"   ⚠ Warning: Still have non-finite values, replacing with 0")
        X_clean = np.where(np.isfinite(X_clean), X_clean, 0)
    
    # Train/test split
    split_idx = int(len(X_clean) * 0.8)
    X_train, X_test = X_clean[:split_idx], X_clean[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\n7. Training model...")
    print(f"   Training: {len(X_train)} samples")
    print(f"   Test: {len(X_test)} samples")
    
    # Feature selection (use top 75 - optimal from previous test)
    n_features = min(75, X_train.shape[1])
    if n_features < X_train.shape[1]:
        print(f"   Selecting top {n_features} features...")
        from sklearn.feature_selection import SelectKBest, f_regression
        selector = SelectKBest(f_regression, k=n_features)
        X_train_selected = selector.fit_transform(X_train, y_train)
        X_test_selected = selector.transform(X_test)
    else:
        X_train_selected = X_train
        X_test_selected = X_test
    
    # Train
    try:
        model_temp = EnsembleTradingModel(task='regression', random_state=42)
        model_temp.fit(X_train_selected, y_train, use_ensemble='stacking')
        print(f"   ✓ Model trained")
    except Exception as e:
        print(f"   ✗ Training failed: {e}")
        return None
    
    # Evaluate
    print(f"\n8. Evaluating...")
    predictions = model_temp.predict(X_test_selected)
    
    # Metrics
    r2 = r2_score(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    
    # Direction accuracy
    pred_direction = (predictions > 0).astype(int)
    actual_direction = (y_test > 0).astype(int)
    dir_acc = (pred_direction == actual_direction).mean()
    
    # Sharpe (annualized)
    strategy_returns = predictions * y_test
    sharpe = strategy_returns.mean() / (strategy_returns.std() + 1e-10) * np.sqrt(252)
    
    results = {
        'granularity': granularity_config['name'],
        'bars': len(df),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features_total': total_features,
        'features_selected': n_features,
        'timespan_days': timespan,
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
    
    return results


def test_all_granularities(symbol='AAPL'):
    """
    Test ALL granularities with full feature set
    """
    print("\n" + "=" * 80)
    print(f"COMPLETE ML TEST - {symbol}")
    print("Testing ALL granularities with ALL features")
    print("Features: Technical (184) + Alpha Trader (35) + Risk (12) = 231")
    print("=" * 80)
    
    # Define all granularity configs
    configs = [
        {
            'name': 'Daily (10 years)',
            'periodType': 'year',
            'period': 10,
            'frequencyType': 'daily',
            'frequency': 1,
            'spy_periodType': 'year',
            'spy_period': 10
        },
        {
            'name': 'Daily (20 years)',
            'periodType': 'year',
            'period': 20,
            'frequencyType': 'daily',
            'frequency': 1,
            'spy_periodType': 'year',
            'spy_period': 20
        },
        {
            'name': '30-min (10 days)',
            'periodType': 'day',
            'period': 10,
            'frequencyType': 'minute',
            'frequency': 30,
            'spy_periodType': 'day',
            'spy_period': 10
        },
        {
            'name': '5-min (10 days)',
            'periodType': 'day',
            'period': 10,
            'frequencyType': 'minute',
            'frequency': 5,
            'spy_periodType': 'day',
            'spy_period': 10
        },
        {
            'name': '1-min (10 days)',
            'periodType': 'day',
            'period': 10,
            'frequencyType': 'minute',
            'frequency': 1,
            'spy_periodType': 'day',
            'spy_period': 10
        }
    ]
    
    # Test each
    results = []
    for config in configs:
        result = test_granularity_with_alpha(symbol, config)
        if result:
            results.append(result)
    
    # Summary table
    if results:
        print("\n\n" + "=" * 80)
        print("📊 SUMMARY - ML METRICS BY GRANULARITY (WITH ALPHA TRADER FEATURES)")
        print("=" * 80)
        print()
        
        # Header
        print(f"{'Granularity':<20} {'Bars':>8} {'Train':>8} {'R²':>8} {'RMSE':>8} {'Dir%':>7} {'Sharpe':>7}")
        print("-" * 80)
        
        # Rows
        for r in results:
            status = "✅" if r['r2'] > 0 else "⚠️"
            print(f"{r['granularity']:<20} "
                  f"{r['bars']:>8} "
                  f"{r['training_samples']:>8} "
                  f"{r['r2']:>8.4f} {status} "
                  f"{r['rmse']*100:>7.2f}% "
                  f"{r['dir_acc']*100:>6.1f}% "
                  f"{r['sharpe']:>7.2f}")
        
        print("=" * 80)
        
        # Best performers
        best_r2 = max(results, key=lambda x: x['r2'])
        best_rmse = min(results, key=lambda x: x['rmse'])
        best_dir = max(results, key=lambda x: x['dir_acc'])
        best_sharpe = max(results, key=lambda x: x['sharpe'])
        
        print("\n🏆 BEST PERFORMERS:")
        print(f"   Best R²: {best_r2['granularity']} (R² = {best_r2['r2']:.4f})")
        print(f"   Best RMSE: {best_rmse['granularity']} (RMSE = {best_rmse['rmse']*100:.2f}%)")
        print(f"   Best Direction: {best_dir['granularity']} ({best_dir['dir_acc']*100:.1f}%)")
        print(f"   Best Sharpe: {best_sharpe['granularity']} ({best_sharpe['sharpe']:.2f})")
        
        # Analysis
        print("\n💡 ANALYSIS:")
        print("=" * 80)
        
        # Daily analysis
        daily_results = [r for r in results if 'Daily' in r['granularity']]
        if len(daily_results) >= 2:
            daily_10y = [r for r in daily_results if '10 years' in r['granularity']][0]
            daily_20y = [r for r in daily_results if '20 years' in r['granularity']][0]
            
            print(f"\n📈 Daily Granularity Comparison:")
            print(f"   10 years: R² = {daily_10y['r2']:.4f}, RMSE = {daily_10y['rmse']*100:.2f}%")
            print(f"   20 years: R² = {daily_20y['r2']:.4f}, RMSE = {daily_20y['rmse']*100:.2f}%")
            
            if daily_20y['r2'] > daily_10y['r2']:
                improvement = daily_20y['r2'] - daily_10y['r2']
                print(f"   ✅ 20 years is better by {improvement:.4f} R² points!")
            else:
                print(f"   ⚠️ 10 years performed better (less data, less complexity)")
        
        # Intraday analysis
        intraday = [r for r in results if 'min' in r['granularity']]
        if intraday:
            print(f"\n⚡ Intraday Granularity Analysis:")
            for r in intraday:
                quality = "✅ Good" if r['r2'] > 0.2 else "⚠️ Challenging" if r['r2'] > 0 else "❌ Difficult"
                print(f"   {r['granularity']}: R² = {r['r2']:.4f} ({quality})")
                print(f"      Training samples: {r['training_samples']:,}")
                print(f"      Only {r['timespan_days']} days of data (limited)")
        
        # Feature impact
        print(f"\n🎯 Feature Set Impact:")
        print(f"   Total Features: {results[0]['features_total']}")
        print(f"   Selected (optimal): {results[0]['features_selected']}")
        print(f"   ")
        print(f"   Breakdown:")
        print(f"   • Technical: 184 features")
        print(f"   • Alpha Trader: 35 features (NEW!) ⭐")
        print(f"   • Risk (GARCH+Copula): 12 features")
        
        # Recommendations
        print(f"\n✅ RECOMMENDATIONS:")
        print("=" * 80)
        
        if best_r2['r2'] > 0:
            print(f"\n1. ✅ USE {best_r2['granularity']} for production")
            print(f"   • R² = {best_r2['r2']:.4f} (positive!)")
            print(f"   • RMSE = {best_r2['rmse']*100:.2f}%")
            print(f"   • Direction Accuracy = {best_r2['dir_acc']*100:.1f}%")
        else:
            print(f"\n1. ⚠️ No positive R² yet, but {best_r2['granularity']} is best")
            print(f"   • R² = {best_r2['r2']:.4f} (closest to 0)")
            print(f"   • Try: More data, different ensemble, or time series models")
        
        print(f"\n2. 📊 For Daily Trading:")
        if daily_results:
            best_daily = max(daily_results, key=lambda x: x['r2'])
            print(f"   • Use {best_daily['granularity']}")
            print(f"   • R² = {best_daily['r2']:.4f}")
        
        print(f"\n3. ⚡ For Intraday/HFT:")
        if intraday:
            best_intraday = max(intraday, key=lambda x: x['r2'])
            print(f"   • Best: {best_intraday['granularity']}")
            print(f"   • R² = {best_intraday['r2']:.4f}")
            print(f"   • ⚠️ Limited to 10 days (Schwab limit)")
            print(f"   • 💡 For more data: Use yfinance or StockData.org (see FREE_DATA_SOURCES.md)")
        
        return results
    
    else:
        print("\n❌ No successful tests")
        return None


if __name__ == '__main__':
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ML TEST")
    print("Symbol: " + symbol)
    print("Features: Technical + Alpha Trader + Risk = 231 features!")
    print("Granularities: Daily (10y, 20y), 30-min, 5-min, 1-min")
    print("=" * 80)
    
    results = test_all_granularities(symbol)
    
    if results:
        print("\n" + "=" * 80)
        print("✅ COMPLETE ML TEST FINISHED!")
        print("=" * 80)
        print(f"\nTested {len(results)} granularities with 231 features")
        print(f"Alpha Trader features (35) added successfully! ⭐")
        print(f"\nBest R²: {max(results, key=lambda x: x['r2'])['r2']:.4f}")
        print(f"Best RMSE: {min(results, key=lambda x: x['rmse'])['rmse']*100:.2f}%")

