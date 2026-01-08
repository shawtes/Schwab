"""
Test Feature Selection to Improve R²
With 20 years of data and 189 features, we might have too many features
Try reducing to 50-100 best features
"""

import os
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

load_dotenv()

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from ml_trading.pipeline.risk_feature_integrator import RiskFeatureIntegrator
import schwabdev


def test_with_feature_selection(symbol='AAPL', n_features_list=[50, 75, 100, 150, 189]):
    """
    Test different numbers of features to find optimal
    """
    print("\n" + "=" * 80)
    print(f"FEATURE SELECTION TEST - {symbol}")
    print("Testing different feature counts to optimize R²")
    print("=" * 80)
    
    # Initialize
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    fetcher = SchwabDataFetcher(client)
    
    # Fetch data (20 years)
    print(f"\n1. Fetching market data...")
    spy_data = fetcher.get_price_history('SPY', periodType='year', period=20)
    spy_returns = spy_data['close'].pct_change().dropna() if spy_data is not None else None
    
    print(f"\n2. Fetching {symbol} data (20 years)...")
    df = fetcher.get_price_history(symbol, periodType='year', period=20)
    
    if df is None or len(df) < 100:
        print("   ✗ Failed to fetch data")
        return
    
    print(f"   ✓ Fetched {len(df)} bars")
    
    # Create features
    print(f"\n3. Creating features...")
    features_df = fetcher.create_features(df)
    
    if features_df is None or len(features_df) < 50:
        print(f"   ✗ Feature creation failed")
        return None
    
    tech_features = len(features_df.columns)
    print(f"   ✓ Created {tech_features} technical features")
    
    # Add risk features
    print(f"\n4. Adding risk features...")
    risk_integrator = RiskFeatureIntegrator(spy_returns=spy_returns)
    
    try:
        risk_features = risk_integrator.calculate_risk_features(features_df, momentum_score=70)
        
        # Add to DataFrame
        for key, value in risk_features.items():
            if isinstance(value, (int, float)):
                features_df[f'risk_{key}'] = value
        
        risk_score = risk_integrator.get_risk_score(risk_features)
        features_df['risk_score'] = risk_score
        
        print(f"   ✓ Added risk features")
    except Exception as e:
        print(f"   ⚠ Warning: Could not add risk features: {e}")
    
    print(f"   ✓ Total features: {len(features_df.columns)}")
    
    # Prepare features and target
    model = EnsembleTradingModel(task='regression', random_state=42)
    X = model.prepare_features(features_df)
    
    y = df['close'].pct_change().shift(-1).dropna()
    
    # Align X and y
    common_idx = features_df.index.intersection(y.index)
    X = features_df.loc[common_idx]
    X = model.prepare_features(X)
    y = y.loc[common_idx]
    
    # Split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"   ✓ Training: {len(X_train)} samples, Test: {len(X_test)} samples")
    
    # Test different feature counts
    results = []
    n_total_features = len(model.feature_names)
    
    for n_features in n_features_list:
        if n_features > n_total_features:
            continue
        
        print(f"\n" + "=" * 80)
        print(f"Testing with {n_features} features")
        print("=" * 80)
        
        # Select top features
        if n_features < n_total_features:
            print(f"   Selecting top {n_features} features...")
            # Use model's select_top_features method
            from sklearn.feature_selection import SelectKBest, f_regression
            selector = SelectKBest(f_regression, k=n_features)
            X_train_selected = selector.fit_transform(X_train, y_train)
            X_test_selected = selector.transform(X_test)
        else:
            print(f"   Using all {n_features} features...")
            X_train_selected = X_train
            X_test_selected = X_test
        
        # Train model
        print(f"   Training model...")
        model_temp = EnsembleTradingModel(task='regression', random_state=42)
        model_temp.fit(X_train_selected, y_train, use_ensemble='stacking')
        
        # Predict
        predictions = model_temp.predict(X_test_selected)
        
        # Evaluate
        r2 = r2_score(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        
        # Direction accuracy
        pred_direction = (predictions > 0).astype(int)
        actual_direction = (y_test > 0).astype(int)
        dir_acc = (pred_direction == actual_direction).mean()
        
        results.append({
            'n_features': n_features,
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'dir_acc': dir_acc
        })
        
        print(f"\n   📊 Results:")
        print(f"      R²: {r2:.4f} {'✅' if r2 > 0 else '⚠️'}")
        print(f"      RMSE: {rmse:.6f} ({rmse*100:.2f}%)")
        print(f"      MAE: {mae:.6f} ({mae*100:.2f}%)")
        print(f"      Direction Accuracy: {dir_acc*100:.1f}%")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("📊 FEATURE SELECTION SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Features':>12} {'R²':>10} {'RMSE':>10} {'MAE':>10} {'Dir Acc':>10}")
    print("-" * 80)
    
    for r in results:
        status = "✅" if r['r2'] > 0 else "⚠️"
        print(f"{r['n_features']:>12} {r['r2']:>10.4f} {status:>2} "
              f"{r['rmse']*100:>8.2f}% {r['mae']*100:>8.2f}% {r['dir_acc']*100:>9.1f}%")
    
    # Find best
    best_r2 = max(results, key=lambda x: x['r2'])
    best_rmse = min(results, key=lambda x: x['rmse'])
    
    print("\n" + "=" * 80)
    print("🏆 BEST RESULTS:")
    print("=" * 80)
    print(f"\nBest R²: {best_r2['n_features']} features")
    print(f"   R² = {best_r2['r2']:.4f} {'✅ POSITIVE!' if best_r2['r2'] > 0 else '⚠️ Negative'}")
    print(f"   RMSE = {best_r2['rmse']*100:.2f}%")
    
    print(f"\nBest RMSE: {best_rmse['n_features']} features")
    print(f"   RMSE = {best_rmse['rmse']*100:.2f}%")
    print(f"   R² = {best_rmse['r2']:.4f}")
    
    print("\n💡 RECOMMENDATION:")
    if best_r2['r2'] > 0:
        print(f"   ✅ Use {best_r2['n_features']} features for best R² ({best_r2['r2']:.4f})")
    else:
        print(f"   ⚠️ Try ensemble_method='mlb' or add more base models")
        print(f"   ⚠️ Current best: {best_r2['n_features']} features (R² = {best_r2['r2']:.4f})")
    
    return results


if __name__ == '__main__':
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    print("\n" + "=" * 80)
    print("FEATURE SELECTION OPTIMIZATION")
    print("Testing: 50, 75, 100, 150, 189 features")
    print("Goal: Find optimal feature count for positive R²")
    print("=" * 80)
    
    results = test_with_feature_selection(symbol)
    
    print("\n" + "=" * 80)
    print("✅ FEATURE SELECTION TEST COMPLETE!")
    print("=" * 80)
    print("\n💡 With 20 years of data, fewer features often work better!")
    print("   Try using the optimal count shown above in your main system.")

