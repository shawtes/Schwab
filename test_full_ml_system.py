"""
Full ML System Test - End-to-End
Tests: Data Fetch → Features (Technical + Risk) → Ensemble Training → Predictions
"""

import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()

# Import existing ML system
from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
import schwabdev

# Import new risk models
from ml_trading.pipeline.risk_feature_integrator import RiskFeatureIntegrator


def test_full_ml_pipeline(symbol='AAPL', use_risk_features=True):
    """
    Test complete ML pipeline with risk features
    
    Args:
        symbol: Stock to test
        use_risk_features: If True, adds risk features; if False, uses only technical
    """
    print("=" * 80)
    print(f"FULL ML SYSTEM TEST - {symbol}")
    print("=" * 80)
    
    # Initialize Schwab client
    print("\n1. Initializing Schwab API...")
    try:
        client = schwabdev.Client(
            os.getenv('app_key'),
            os.getenv('app_secret'),
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        print("   ✓ Client initialized")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None
    
    # Initialize components
    fetcher = SchwabDataFetcher(client)
    
    # Fetch market data for risk features
    print("\n2. Fetching market data (SPY for correlations)...")
    spy_data = fetcher.get_price_history('SPY', periodType='year', period=20)  # 20 years MAX!
    spy_returns = spy_data['close'].pct_change().dropna() if spy_data is not None else None
    print(f"   ✓ SPY: {len(spy_returns)} bars")
    
    # Initialize risk integrator
    risk_integrator = RiskFeatureIntegrator(spy_returns=spy_returns) if use_risk_features else None
    
    # Fetch stock data
    print(f"\n3. Fetching {symbol} data...")
    df = fetcher.get_price_history(symbol, periodType='year', period=20)  # 20 years MAX!
    
    if df is None or len(df) < 100:
        print(f"   ✗ Insufficient data")
        return None
    
    print(f"   ✓ Fetched {len(df)} bars")
    print(f"   Date range: {df.index.min()} to {df.index.max()}")
    
    # Create technical features
    print(f"\n4. Creating features...")
    features_df = fetcher.create_features(df)
    
    if features_df is None or len(features_df) < 50:
        print(f"   ✗ Feature creation failed")
        return None
    
    tech_features = len(features_df.columns)
    print(f"   ✓ Created {tech_features} technical features")
    
    # Add risk features
    if use_risk_features:
        print(f"\n5. Adding risk features (GARCH + Copula)...")
        try:
            risk_features = risk_integrator.calculate_risk_features(features_df, momentum_score=70)
            
            # Add to DataFrame
            for key, value in risk_features.items():
                if isinstance(value, (int, float)):
                    features_df[f'risk_{key}'] = value
            
            risk_score = risk_integrator.get_risk_score(risk_features)
            features_df['risk_score'] = risk_score
            
            risk_feature_count = len(features_df.columns) - tech_features
            print(f"   ✓ Added {risk_feature_count} risk features")
            print(f"   📊 Risk Metrics:")
            print(f"      Volatility: {risk_features['annualized_volatility']:.2%}")
            print(f"      VaR 95%: ${risk_features['var_95']:.2f}")
            print(f"      Beta (SPY): {risk_features['beta_spy']:.2f}")
            print(f"      Sharpe Ratio: {risk_features['sharpe_ratio']:.2f}")
            print(f"      Risk Score: {risk_score}/10")
        except Exception as e:
            print(f"   ⚠ Warning: {e}")
            use_risk_features = False
    
    total_features = len(features_df.columns)
    print(f"\n   Total Features: {total_features}")
    
    # Train ensemble model
    print(f"\n6. Training Ensemble Model...")
    model = EnsembleTradingModel(
        task='regression',  # Predict returns
        random_state=42
    )
    
    # Prepare target
    print(f"   Preparing target (next-period returns)...")
    target, valid_mask = model.prepare_target(features_df, forward_periods=1)
    features_df_valid = features_df[valid_mask]
    
    # Prepare features
    X = model.prepare_features(features_df_valid)
    y = target.values
    
    print(f"   Valid samples: {len(X)}")
    print(f"   Features: {X.shape[1]}")
    print(f"   Target stats: Mean={y.mean():.4f}, Std={y.std():.4f}")
    
    # Split data (80/20 chronological)
    split_idx = int(len(X) * 0.8)
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]
    
    print(f"\n7. Training on {len(X_train)} samples...")
    print(f"   Test set: {len(X_test)} samples")
    
    # Train
    model.fit(X_train, y_train, use_ensemble='stacking')
    print(f"   ✓ Model trained")
    
    # Evaluate
    print(f"\n8. Evaluating on test set...")
    print("-" * 80)
    test_results = model.evaluate(X_test, y_test)
    
    # Make prediction on latest data
    print(f"\n9. Making prediction on latest data...")
    latest_X = X[-1:] if len(X) > 0 else None
    
    if latest_X is not None:
        prediction = model.predict(latest_X)[0]
        
        print(f"\n   📈 Prediction for {symbol}:")
        print(f"      Predicted Return: {prediction:.4f} ({prediction*100:.2f}%)")
        
        # Generate signal
        confidence = abs(prediction)
        
        if use_risk_features:
            risk_score = features_df['risk_score'].iloc[-1]
            
            # Risk-aware decision (from architecture)
            if prediction > 0.01 and confidence >= 0.02 and risk_score <= 6:
                signal = 'BUY'
                reason = f"Positive return predicted ({prediction:.2%}), acceptable risk ({risk_score}/10)"
            elif prediction < -0.01 and confidence >= 0.02 and risk_score <= 6:
                signal = 'SELL'
                reason = f"Negative return predicted ({prediction:.2%}), acceptable risk ({risk_score}/10)"
            elif risk_score > 6:
                signal = 'HOLD'
                reason = f"Risk too high ({risk_score}/10)"
            else:
                signal = 'HOLD'
                reason = f"Low confidence ({confidence:.2%})"
            
            print(f"      Signal: {signal}")
            print(f"      Reason: {reason}")
            print(f"      Risk Score: {risk_score}/10")
        else:
            # Simple signal without risk
            if prediction > 0.01:
                signal = 'BUY'
            elif prediction < -0.01:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            print(f"      Signal: {signal}")
            print(f"      Confidence: {confidence:.4f}")
    
    print("\n" + "=" * 80)
    print("✅ FULL ML SYSTEM TEST COMPLETE!")
    print("=" * 80)
    
    return {
        'model': model,
        'features_df': features_df,
        'test_results': test_results,
        'prediction': prediction if latest_X is not None else None,
        'signal': signal if latest_X is not None else None,
        'risk_score': risk_score if use_risk_features else None
    }


def compare_with_without_risk(symbol='AAPL'):
    """
    Compare ML performance with and without risk features
    """
    print("\n" + "=" * 80)
    print("COMPARISON: WITH vs WITHOUT Risk Features")
    print("=" * 80)
    
    print("\n📊 Test 1: WITHOUT Risk Features")
    print("-" * 80)
    results_without = test_full_ml_pipeline(symbol, use_risk_features=False)
    
    print("\n\n📊 Test 2: WITH Risk Features")
    print("-" * 80)
    results_with = test_full_ml_pipeline(symbol, use_risk_features=True)
    
    if results_without and results_with:
        print("\n" + "=" * 80)
        print("📊 COMPARISON RESULTS")
        print("=" * 80)
        
        print(f"\nModel Performance (R² Score):")
        print(f"   WITHOUT Risk Features: {results_without['test_results']['r2']:.4f}")
        print(f"   WITH Risk Features:    {results_with['test_results']['r2']:.4f}")
        
        r2_improvement = (results_with['test_results']['r2'] - results_without['test_results']['r2'])
        print(f"   Improvement: {r2_improvement:+.4f}")
        
        print(f"\nFeature Count:")
        print(f"   WITHOUT Risk: {results_without['features_df'].shape[1]} features")
        print(f"   WITH Risk:    {results_with['features_df'].shape[1]} features")
        
        print(f"\nPrediction:")
        print(f"   WITHOUT Risk: {results_without['prediction']:.4f} ({results_without['prediction']*100:.2f}%)")
        print(f"   WITH Risk:    {results_with['prediction']:.4f} ({results_with['prediction']*100:.2f}%)")
        
        print(f"\nTrading Signal:")
        print(f"   WITHOUT Risk: {results_without['signal']}")
        print(f"   WITH Risk:    {results_with['signal']} (Risk Score: {results_with['risk_score']}/10)")
        
        print("\n" + "=" * 80)
        print("✅ COMPARISON COMPLETE!")
        print("=" * 80)


if __name__ == '__main__':
    import sys
    
    # Test single stock with risk features
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        print(f"\nTesting {symbol} with risk features...")
        test_full_ml_pipeline(symbol, use_risk_features=True)
    else:
        # Run comparison test
        compare_with_without_risk('AAPL')

