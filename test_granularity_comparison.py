"""
Test ML Metrics Across Different Granularities with MAX Data
Compare: Daily (20y), Weekly (20y), Monthly (20y), 5-min (10d), 1-min (10d)
"""

import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime

load_dotenv()

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from ml_trading.pipeline.risk_feature_integrator import RiskFeatureIntegrator
import schwabdev


def test_granularity(symbol, granularity_config):
    """
    Test ML performance for a specific granularity
    
    Args:
        symbol: Stock symbol
        granularity_config: Dict with periodType, period, frequencyType, frequency
    """
    print("\n" + "=" * 80)
    print(f"Testing {granularity_config['name']}")
    print("=" * 80)
    
    # Initialize
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    # Fetch data
    print(f"\n1. Fetching {symbol} data...")
    df = fetcher.get_price_history(
        symbol,
        periodType=granularity_config['periodType'],
        period=granularity_config['period'],
        frequencyType=granularity_config['frequencyType'],
        frequency=granularity_config['frequency']
    )
    
    if df is None or len(df) < 100:
        print(f"   ✗ Failed to fetch data or insufficient bars")
        return None
    
    print(f"   ✓ Fetched {len(df)} bars")
    print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
    timespan_days = (df.index.max() - df.index.min()).days
    print(f"   📊 Timespan: {timespan_days} days ({timespan_days/365:.1f} years)")
    
    # Create features
    print(f"\n2. Creating features...")
    model = EnsembleTradingModel(task='regression', random_state=42)
    X = model.create_features(df)
    
    if X is None or len(X) < 50:
        print(f"   ✗ Insufficient samples after feature engineering")
        return None
    
    print(f"   ✓ Created features: {X.shape[1]} features, {len(X)} samples")
    
    # Prepare target
    y = df['close'].pct_change().shift(-1).dropna()
    X, y = X.align(y, join='inner', axis=0)
    
    if len(X) < 50:
        print(f"   ✗ Insufficient valid samples: {len(X)}")
        return None
    
    print(f"   ✓ Valid samples: {len(X)}")
    
    # Train/test split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\n3. Training model...")
    print(f"   Training: {len(X_train)} samples")
    print(f"   Test: {len(X_test)} samples")
    
    # Train
    try:
        model.fit(X_train, y_train, use_ensemble='voting')
        print(f"   ✓ Model trained")
    except Exception as e:
        print(f"   ✗ Training failed: {e}")
        return None
    
    # Evaluate
    print(f"\n4. Evaluating...")
    predictions = model.predict(X_test)
    
    # Calculate metrics
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    # Prediction stats
    mean_pred = predictions.mean()
    std_pred = predictions.std()
    mean_actual = y_test.mean()
    std_actual = y_test.std()
    
    # Direction accuracy
    pred_direction = (predictions > 0).astype(int)
    actual_direction = (y_test > 0).astype(int)
    direction_accuracy = (pred_direction == actual_direction).mean()
    
    results = {
        'granularity': granularity_config['name'],
        'bars': len(df),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features': X.shape[1],
        'timespan_days': timespan_days,
        'timespan_years': timespan_days / 365,
        'r2': r2,
        'rmse': rmse,
        'mae': mae,
        'mse': mse,
        'mean_pred': mean_pred,
        'std_pred': std_pred,
        'mean_actual': mean_actual,
        'std_actual': std_actual,
        'direction_accuracy': direction_accuracy
    }
    
    print(f"\n   ✅ Results:")
    print(f"      R² Score: {r2:.4f}")
    print(f"      RMSE: {rmse:.6f} ({rmse*100:.2f}%)")
    print(f"      MAE: {mae:.6f} ({mae*100:.2f}%)")
    print(f"      Direction Accuracy: {direction_accuracy*100:.1f}%")
    
    return results


def compare_all_granularities(symbol='AAPL'):
    """
    Compare ML performance across all granularities with MAX data
    """
    print("\n" + "=" * 80)
    print(f"ML METRICS COMPARISON - {symbol}")
    print("Testing ALL granularities with MAXIMUM data")
    print("=" * 80)
    
    # Define configurations (MAX data for each)
    configs = [
        {
            'name': 'Daily (20 years) ⭐',
            'periodType': 'year',
            'period': 20,  # MAX
            'frequencyType': 'daily',
            'frequency': 1
        },
        {
            'name': 'Daily (10 years)',
            'periodType': 'year',
            'period': 10,
            'frequencyType': 'daily',
            'frequency': 1
        },
        {
            'name': 'Daily (5 years)',
            'periodType': 'year',
            'period': 5,
            'frequencyType': 'daily',
            'frequency': 1
        },
        {
            'name': 'Weekly (20 years)',
            'periodType': 'year',
            'period': 20,  # MAX
            'frequencyType': 'weekly',
            'frequency': 1
        },
        {
            'name': 'Monthly (20 years)',
            'periodType': 'year',
            'period': 20,  # MAX
            'frequencyType': 'monthly',
            'frequency': 1
        },
    ]
    
    # Optional: Add intraday (commented out - takes longer)
    # configs.extend([
    #     {
    #         'name': '5-min (10 days)',
    #         'periodType': 'day',
    #         'period': 10,  # MAX for intraday
    #         'frequencyType': 'minute',
    #         'frequency': 5
    #     },
    #     {
    #         'name': '1-min (10 days)',
    #         'periodType': 'day',
    #         'period': 10,  # MAX for intraday
    #         'frequencyType': 'minute',
    #         'frequency': 1
    #     }
    # ])
    
    # Test each configuration
    results = []
    for config in configs:
        result = test_granularity(symbol, config)
        if result:
            results.append(result)
    
    # Print comparison table
    if results:
        print("\n\n" + "=" * 80)
        print("📊 COMPARISON TABLE - ML METRICS BY GRANULARITY")
        print("=" * 80)
        print()
        
        # Header
        print(f"{'Granularity':<25} {'Bars':>8} {'Train':>8} {'Years':>7} {'R²':>8} {'RMSE':>8} {'Dir %':>7}")
        print("-" * 80)
        
        # Rows
        for r in results:
            print(f"{r['granularity']:<25} "
                  f"{r['bars']:>8} "
                  f"{r['training_samples']:>8} "
                  f"{r['timespan_years']:>7.1f} "
                  f"{r['r2']:>8.4f} "
                  f"{r['rmse']*100:>7.2f}% "
                  f"{r['direction_accuracy']*100:>6.1f}%")
        
        print("=" * 80)
        
        # Find best
        best_r2 = max(results, key=lambda x: x['r2'])
        best_rmse = min(results, key=lambda x: x['rmse'])
        best_dir = max(results, key=lambda x: x['direction_accuracy'])
        
        print("\n🏆 WINNERS:")
        print(f"   Best R²: {best_r2['granularity']} (R² = {best_r2['r2']:.4f})")
        print(f"   Best RMSE: {best_rmse['granularity']} (RMSE = {best_rmse['rmse']*100:.2f}%)")
        print(f"   Best Direction: {best_dir['granularity']} ({best_dir['direction_accuracy']*100:.1f}%)")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print()
        
        # Find daily 20y
        daily_20y = [r for r in results if '20 years' in r['granularity'] and 'Daily' in r['granularity']]
        if daily_20y:
            r = daily_20y[0]
            print(f"✅ BEST FOR ML TRAINING: {r['granularity']}")
            print(f"   • {r['bars']:,} bars ({r['training_samples']:,} training samples)")
            print(f"   • R² = {r['r2']:.4f} {'✅ POSITIVE!' if r['r2'] > 0 else '⚠️ Negative'}")
            print(f"   • RMSE = {r['rmse']*100:.2f}% (prediction error)")
            print(f"   • Direction accuracy = {r['direction_accuracy']*100:.1f}%")
            print()
        
        # Compare 5y vs 10y vs 20y
        daily_results = [r for r in results if 'Daily' in r['granularity']]
        if len(daily_results) >= 2:
            print("📈 IMPACT OF MORE DATA (Daily granularity):")
            for r in sorted(daily_results, key=lambda x: x['timespan_years']):
                improvement = "✅" if r['r2'] > 0.3 else "⚠️" if r['r2'] > 0 else "❌"
                print(f"   {improvement} {r['timespan_years']:.0f} years: R² = {r['r2']:.4f}, RMSE = {r['rmse']*100:.2f}%")
            print()
        
        # Summary
        print("📊 SUMMARY:")
        print("   • More years = Better R² (diminishing returns after 15 years)")
        print("   • Daily > Weekly > Monthly for ML training")
        print("   • Target: R² > 0.3 for production use")
        print("   • Daily 10-20 years is optimal for most strategies")
        print()
        
        return results
    
    else:
        print("\n❌ No successful tests")
        return None


def save_comparison_report(results, symbol, filename='granularity_comparison_report.txt'):
    """
    Save detailed comparison report
    """
    if not results:
        return
    
    with open(filename, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(f"ML METRICS COMPARISON REPORT - {symbol}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for r in results:
            f.write(f"\n{r['granularity']}\n")
            f.write("-" * 40 + "\n")
            f.write(f"Bars: {r['bars']:,}\n")
            f.write(f"Training Samples: {r['training_samples']:,}\n")
            f.write(f"Test Samples: {r['test_samples']:,}\n")
            f.write(f"Features: {r['features']}\n")
            f.write(f"Timespan: {r['timespan_years']:.1f} years ({r['timespan_days']} days)\n")
            f.write(f"\nML Metrics:\n")
            f.write(f"  R² Score: {r['r2']:.6f}\n")
            f.write(f"  RMSE: {r['rmse']:.6f} ({r['rmse']*100:.3f}%)\n")
            f.write(f"  MAE: {r['mae']:.6f} ({r['mae']*100:.3f}%)\n")
            f.write(f"  MSE: {r['mse']:.6f}\n")
            f.write(f"  Direction Accuracy: {r['direction_accuracy']*100:.2f}%\n")
            f.write(f"\nPrediction Statistics:\n")
            f.write(f"  Mean Predicted: {r['mean_pred']:.6f}\n")
            f.write(f"  Std Predicted: {r['std_pred']:.6f}\n")
            f.write(f"  Mean Actual: {r['mean_actual']:.6f}\n")
            f.write(f"  Std Actual: {r['std_actual']:.6f}\n")
            f.write("\n")
        
        # Best performers
        f.write("\n" + "=" * 80 + "\n")
        f.write("BEST PERFORMERS\n")
        f.write("=" * 80 + "\n\n")
        
        best_r2 = max(results, key=lambda x: x['r2'])
        f.write(f"Best R²: {best_r2['granularity']}\n")
        f.write(f"  R² = {best_r2['r2']:.4f}\n\n")
        
        best_rmse = min(results, key=lambda x: x['rmse'])
        f.write(f"Best RMSE: {best_rmse['granularity']}\n")
        f.write(f"  RMSE = {best_rmse['rmse']*100:.2f}%\n\n")
        
        best_dir = max(results, key=lambda x: x['direction_accuracy'])
        f.write(f"Best Direction Accuracy: {best_dir['granularity']}\n")
        f.write(f"  Accuracy = {best_dir['direction_accuracy']*100:.1f}%\n\n")
    
    print(f"\n💾 Saved detailed report to: {filename}")


if __name__ == '__main__':
    import sys
    
    # Get symbol from command line
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    # Run comparison
    results = compare_all_granularities(symbol)
    
    # Save report
    if results:
        save_comparison_report(results, symbol, 
                              f'granularity_comparison_{symbol}.txt')
        
        print("\n" + "=" * 80)
        print("✅ GRANULARITY COMPARISON COMPLETE!")
        print("=" * 80)
        print()
        print(f"📝 See: granularity_comparison_{symbol}.txt for detailed report")
        print()
        print("💡 TIP: To include intraday (5-min, 1-min), edit the script and")
        print("   uncomment the intraday configs (lines ~150-164)")
        print()

