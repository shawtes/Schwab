"""
Test Complete Multi-Timeframe System with EV-Based Classifier

This script tests:
1. Multi-timeframe predictions (1m, 5m, 30m, 1d)
2. Combined signal generation
3. EV-based classification (Expected Value)
4. BUY/SELL/HOLD with confidence scores
"""

import os
import sys
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import schwabdev

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from ml_trading.pipeline.multi_timeframe_system import MultiTimeframePredictor, EVClassifier


def test_multi_timeframe_ev_system(symbol='AAPL', use_all_timeframes=False):
    """
    Test complete multi-timeframe EV system
    
    Args:
        symbol: Stock symbol to test
        use_all_timeframes: If True, test all timeframes (slower)
    """
    print("\n" + "=" * 100)
    print(f"MULTI-TIMEFRAME EV-BASED TRADING SYSTEM TEST - {symbol}")
    print("=" * 100)
    
    # Initialize Schwab client
    load_dotenv()
    
    try:
        client = schwabdev.Client(
            os.getenv('app_key'),
            os.getenv('app_secret'),
            os.getenv('callback_url', 'https://127.0.0.1')
        )
    except Exception as e:
        print(f"❌ Failed to initialize Schwab client: {e}")
        return None
    
    fetcher = SchwabDataFetcher(client)
    
    # ===== STAGE 1: MULTI-TIMEFRAME PREDICTIONS =====
    print("\n" + "=" * 100)
    print("STAGE 1: MULTI-TIMEFRAME PREDICTIONS")
    print("=" * 100)
    
    if use_all_timeframes:
        timeframes = ['1m', '5m', '30m', '1d']
    else:
        timeframes = ['5m', '1d']  # Fast test
    
    mtp = MultiTimeframePredictor(timeframes=timeframes, use_lstm=False)
    
    try:
        predictions = mtp.predict_all_timeframes(fetcher, symbol)
    except Exception as e:
        print(f"\n❌ Multi-timeframe prediction failed: {e}")
        return None
    
    if not predictions:
        print("\n❌ No predictions generated")
        return None
    
    # Display predictions
    print("\n📊 Predictions by Timeframe:")
    print("-" * 100)
    for tf, pred in predictions.items():
        print(f"\n   {tf.upper()}:")
        print(f"      Prediction: {pred['prediction']*100:+.3f}%")
        print(f"      R²: {pred['r2']:.4f}")
        print(f"      RMSE: {pred['rmse']:.6f}")
        print(f"      Model: {pred['model_type']}")
        print(f"      Data: {pred['samples']} samples from {pred['bars']} bars")
    
    # ===== STAGE 2: COMBINED SIGNAL =====
    print("\n" + "=" * 100)
    print("STAGE 2: COMBINED MULTI-TIMEFRAME SIGNAL")
    print("=" * 100)
    
    combined_pred, tf_confidence = mtp.get_combined_signal()
    
    print(f"\n   🎯 Combined Prediction: {combined_pred*100:+.3f}%")
    print(f"   📊 Timeframe Agreement: {tf_confidence*100:.1f}%")
    
    # ===== STAGE 3: EV CLASSIFIER TRAINING WITH TIMEFRAME FEATURES =====
    print("\n" + "=" * 100)
    print("STAGE 3: EV-BASED CLASSIFIER TRAINING (with Multi-Timeframe Features)")
    print("=" * 100)
    
    # Get daily data for training
    print("\n   Fetching training data (20 years daily)...")
    df_daily = fetcher.get_price_history(
        symbol,
        periodType='year',
        period=20,
        frequencyType='daily',
        frequency=1
    )
    
    if df_daily is None or len(df_daily) < 100:
        print("   ❌ Insufficient training data")
        return None
    
    print(f"   ✓ Loaded {len(df_daily)} bars")
    
    # Create features
    print("\n   Creating base features...")
    features_df = fetcher.create_features(df_daily)
    
    if features_df is None:
        print("   ❌ Feature creation failed")
        return None
    
    print(f"   ✓ Created {features_df.shape[1]} base features")
    
    # Prepare for ML
    model = EnsembleTradingModel(task='regression', random_state=42)
    X = model.prepare_features(features_df)
    y = df_daily['close'].pct_change().shift(-1).dropna()
    
    # Align
    common_idx = features_df.index.intersection(y.index)
    X = features_df.loc[common_idx]
    X = model.prepare_features(X)
    y = y.loc[common_idx]
    
    # Clean
    X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
    
    # Split
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    print(f"   Train: {len(X_train)} samples")
    print(f"   Test: {len(X_test)} samples")
    
    # Generate multi-timeframe predictions as features
    print("\n   Generating multi-timeframe predictions as features...")
    
    timeframe_preds_train = {}
    timeframe_preds_test = {}
    
    # For this demo, we'll use different granularities of the same symbol
    # In production, you'd use actual different timeframes
    for tf in ['1d']:  # Use daily for now (same as training data)
        try:
            preds, _ = mtp.generate_training_predictions(fetcher, symbol, tf, train_size=0.8)
            if preds is not None:
                # Align with X length
                if len(preds) >= len(X):
                    timeframe_preds_train[tf] = preds[:split]
                    timeframe_preds_test[tf] = preds[split:split+len(X_test)]
                    print(f"      ✓ Added {tf} predictions")
        except Exception as e:
            print(f"      ⚠️ Could not add {tf}: {e}")
    
    # Train EV classifier with timeframe predictions
    print("\n   Training EV Classifier with timeframe features...")
    ev_classifier = EVClassifier(
        min_ev=0.0005,       # 0.05% minimum EV (more aggressive)
        min_confidence=0.52,  # 52% minimum confidence (more aggressive)
        risk_free_rate=0.05,  # 5% annual risk-free rate
        use_timeframe_features=True
    )
    
    try:
        ev_classifier.fit(X_train, y_train, timeframe_predictions=timeframe_preds_train)
    except Exception as e:
        print(f"   ❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ===== STAGE 4: EVALUATION =====
    print("\n" + "=" * 100)
    print("STAGE 4: EV CLASSIFIER EVALUATION (Test Set with Timeframe Features)")
    print("=" * 100)
    
    try:
        metrics = ev_classifier.evaluate(X_test, y_test, timeframe_predictions=timeframe_preds_test)
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print(f"\n   📈 Performance Metrics:")
    print(f"      Average EV (BUY signals): {metrics['avg_ev']*100:.3f}%")
    print(f"      Avg Positive EV: {metrics['avg_positive_ev']*100:.3f}%")
    print(f"      BUY Win Rate: {metrics['buy_win_rate']*100:.1f}%")
    print(f"      Avg BUY Confidence: {metrics.get('avg_buy_confidence', 0)*100:.1f}%")
    
    print(f"\n   📊 Signal Distribution:")
    total_signals = metrics['buy_signals'] + metrics['no_trade_signals']
    print(f"      BUY:      {metrics['buy_signals']:3d} ({metrics['buy_signals']/total_signals*100:.1f}%) - "
          f"Win: {metrics['buy_win_rate']*100:.1f}%, Avg Return: {metrics['buy_return']*100:+.3f}%")
    print(f"      NO_TRADE: {metrics['no_trade_signals']:3d} ({metrics['no_trade_signals']/total_signals*100:.1f}%)")
    
    # Calculate profitability
    if metrics['buy_signals'] > 0:
        total_profit = metrics.get('total_profit_estimate', metrics['buy_return'] * metrics['buy_signals'])
        print(f"\n   💰 Estimated Profit: {total_profit*100:+.2f}% (on {metrics['buy_signals']} BUY trades)")
        print(f"   📊 Profit per Trade: {metrics['buy_return']*100:+.3f}%")
    
    # ===== STAGE 5: FINAL SIGNAL =====
    print("\n" + "=" * 100)
    print("STAGE 5: FINAL TRADING SIGNAL (Latest Bar with Live Predictions)")
    print("=" * 100)
    
    # Get latest timeframe predictions
    latest_tf_preds = {}
    if timeframe_preds_test:
        for tf, preds in timeframe_preds_test.items():
            if len(preds) > 0:
                latest_tf_preds[tf] = preds[-1]
    
    # Also add the live predictions from Stage 1
    for tf, pred_info in predictions.items():
        latest_tf_preds[tf] = pred_info['prediction']
    
    print(f"\n   Using predictions from {len(latest_tf_preds)} timeframes:")
    for tf, pred in latest_tf_preds.items():
        print(f"      {tf}: {pred*100:+.3f}%")
    
    try:
        signal, confidence, ev_metrics = ev_classifier.predict_signal(X_test[-1], 
                                                                       timeframe_predictions=latest_tf_preds)
    except Exception as e:
        print(f"\n❌ Signal generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    print(f"\n   🎯 SIGNAL: {signal}")
    print(f"   📊 Confidence: {confidence*100:.1f}%")
    
    print(f"\n   💰 Expected Value Analysis:")
    print(f"      Expected Return: {ev_metrics['expected_return']*100:+.3f}%")
    print(f"      Win Probability: {ev_metrics['win_probability']*100:.1f}%")
    print(f"      Expected Value (EV): {ev_metrics['expected_value']*100:+.3f}%")
    print(f"      Sharpe EV: {ev_metrics['sharpe_ev']:+.3f}")
    print(f"      Risk/Reward Ratio: {ev_metrics['risk_reward_ratio']:.2f}")
    
    # Trading recommendation
    print(f"\n   📋 TRADING RECOMMENDATION:")
    if signal == 'BUY':
        if ev_metrics['expected_value'] > 0.005:
            strength = "💪 STRONG BUY"
            reason = "High positive EV with strong win probability"
            action = "Enter position with full size"
        elif ev_metrics['expected_value'] > 0.002:
            strength = "✅ BUY"
            reason = "Positive EV detected"
            action = "Enter position with normal size"
        else:
            strength = "⚠️ CAUTIOUS BUY"
            reason = "Low positive EV"
            action = "Enter position with reduced size or wait"
        
        print(f"      {strength}")
        print(f"      Reason: {reason}")
        print(f"      Action: {action}")
        print(f"      💡 Use TP/SL for exit management")
    else:
        strength = "⏸️ NO TRADE"
        reason = "Insufficient edge or negative EV"
        print(f"      {strength}")
        print(f"      Reason: {reason}")
        print(f"      Action: Wait for better setup")
    
    # ===== SUMMARY =====
    print("\n" + "=" * 100)
    print("SYSTEM SUMMARY")
    print("=" * 100)
    
    print(f"\n   ✅ Multi-Timeframe Predictions: {len(predictions)} timeframes")
    print(f"   ✅ Combined Signal: {combined_pred*100:+.3f}%")
    print(f"   ✅ EV Classifier: Trained on {len(X_train)} samples")
    print(f"   ✅ Test Performance: {metrics['direction_accuracy']*100:.1f}% direction accuracy")
    print(f"   ✅ Final Signal: {signal} with {confidence*100:.1f}% confidence")
    
    print("\n" + "=" * 100)
    print("✅ MULTI-TIMEFRAME EV SYSTEM TEST COMPLETE!")
    print("=" * 100)
    
    return {
        'symbol': symbol,
        'predictions': predictions,
        'combined_prediction': combined_pred,
        'signal': signal,
        'confidence': confidence,
        'ev_metrics': ev_metrics,
        'test_metrics': metrics
    }


if __name__ == '__main__':
    # Parse arguments
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    use_all_tf = '--all' in sys.argv
    
    # Run test
    result = test_multi_timeframe_ev_system(symbol, use_all_timeframes=use_all_tf)
    
    if result:
        print("\n✅ Test completed successfully!")
        print(f"\nFinal recommendation: {result['signal']} {result['symbol']} "
              f"with {result['confidence']*100:.1f}% confidence")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

