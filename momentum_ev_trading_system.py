"""
Momentum + EV Trading System

Combines momentum scanner with multi-timeframe EV classifier:
1. Scans for top momentum stocks in $2-$20 price range
2. Runs EV classifier on top 3 candidates
3. Provides actionable trading signals

This is the complete automated trading signal generator!
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
web_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web-trading-app')
if os.path.exists(web_app_path):
    sys.path.append(web_app_path)

# Load environment
load_dotenv()

import schwabdev

# Import momentum scanner
try:
    from momentum_scanner import scan_momentum_stocks
except ImportError:
    # Try alternative path
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "momentum_scanner",
        os.path.join(web_app_path, "momentum_scanner.py")
    )
    momentum_scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(momentum_scanner)
    scan_momentum_stocks = momentum_scanner.scan_momentum_stocks

from test_ev_classifier_system import test_multi_timeframe_ev_system
from ensemble_trading_model import SchwabDataFetcher


def find_top_momentum_stocks(min_price=2.0, max_price=20.0, top_n=3):
    """
    Find top N momentum stocks in price range
    
    Args:
        min_price: Minimum stock price
        max_price: Maximum stock price
        top_n: Number of top stocks to return
    
    Returns:
        list: Top momentum stocks with scores
    """
    print("\n" + "=" * 100)
    print(f"MOMENTUM SCANNER: Finding top {top_n} stocks in ${min_price}-${max_price} range")
    print("=" * 100)
    
    # Configure filters for momentum scan
    filters = {
        'minPrice': min_price,
        'maxPrice': max_price,
        'minPercentChange': 1.0,  # At least 1% move
        'minRVOL': 1.2,           # Above average volume
        'minVolume': 500000,      # Minimum liquidity
        'rsiMin': 50,             # Bullish momentum
        'rsiMax': 85              # Not overbought
    }
    
    print(f"\n📊 Scan Filters:")
    print(f"   Price Range: ${min_price} - ${max_price}")
    print(f"   Min % Change: {filters['minPercentChange']}%")
    print(f"   Min RVOL: {filters['minRVOL']}x")
    print(f"   Min Volume: {filters['minVolume']:,}")
    print(f"   RSI Range: {filters['rsiMin']}-{filters['rsiMax']}")
    
    # Run momentum scan
    print(f"\n🔍 Scanning stocks...")
    scan_results = scan_momentum_stocks(filters)
    
    if 'error' in scan_results:
        print(f"❌ Scan error: {scan_results['error']}")
        return []
    
    results = scan_results.get('results', [])
    
    if not results:
        print("❌ No stocks found matching criteria")
        print("\n💡 Try adjusting filters:")
        print("   - Lower minPercentChange to 0.5%")
        print("   - Lower minRVOL to 1.0x")
        print("   - Expand price range")
        return []
    
    # Get top N
    top_stocks = results[:top_n]
    
    print(f"\n✅ Found {len(results)} momentum stocks")
    print(f"📈 Top {len(top_stocks)} candidates:\n")
    
    print(f"{'Rank':<6} {'Symbol':<8} {'Price':<10} {'Change':<10} {'RVOL':<8} {'RSI':<6} {'Score':<8} {'Trend'}")
    print("-" * 100)
    
    for i, stock in enumerate(top_stocks, 1):
        print(f"{i:<6} {stock['symbol']:<8} ${stock['price']:<9.2f} "
              f"{stock['percentChange']:>+7.2f}% {stock['rvol']:<7.2f}x "
              f"{stock['rsi']:<6} {stock['score']:<8} {stock['trend']}")
    
    return top_stocks


def analyze_with_ev_classifier(stocks, fast_mode=True):
    """
    Run EV classifier on momentum stocks
    
    Args:
        stocks: List of stock dicts from momentum scanner
        fast_mode: If True, uses 5m+1d. If False, uses all timeframes
    
    Returns:
        dict: Analysis results with trading signals
    """
    print("\n" + "=" * 100)
    print("EV CLASSIFIER ANALYSIS")
    print("=" * 100)
    
    results = {}
    
    for i, stock in enumerate(stocks, 1):
        symbol = stock['symbol']
        
        print(f"\n{'=' * 100}")
        print(f"[{i}/{len(stocks)}] Analyzing {symbol}")
        print(f"{'=' * 100}")
        
        try:
            # Run EV classifier
            result = test_multi_timeframe_ev_system(
                symbol,
                use_all_timeframes=(not fast_mode)
            )
            
            if result:
                # Extract key metrics
                ev_metrics = result.get('ev_metrics', {})
                test_metrics = result.get('test_metrics', {})
                
                results[symbol] = {
                    'momentum_score': stock['score'],
                    'momentum_change': stock['percentChange'],
                    'signal': result['signal'],
                    'confidence': result['confidence'],
                    'expected_return': ev_metrics.get('expected_return', 0),
                    'win_probability': ev_metrics.get('win_probability', 0),
                    'expected_value': ev_metrics.get('expected_value', 0),
                    'sharpe_ev': ev_metrics.get('sharpe_ev', 0),
                    'risk_reward': ev_metrics.get('risk_reward_ratio', 0),
                    'direction_accuracy': test_metrics.get('direction_accuracy', 0),
                    'avg_ev': test_metrics.get('avg_ev', 0),
                    'buy_signals': test_metrics.get('buy_signals', 0),
                    'buy_return': test_metrics.get('buy_return', 0),
                    'price': stock['price']
                }
            else:
                print(f"   ⚠️ Analysis failed for {symbol}")
                results[symbol] = None
                
        except Exception as e:
            print(f"   ❌ Error analyzing {symbol}: {e}")
            results[symbol] = None
    
    return results


def generate_trading_recommendations(results):
    """
    Generate final trading recommendations
    
    Args:
        results: Dict of analysis results by symbol
    
    Returns:
        dict: Trading recommendations
    """
    print("\n" + "=" * 100)
    print("🎯 TRADING RECOMMENDATIONS")
    print("=" * 100)
    
    # Filter valid results
    valid_results = {k: v for k, v in results.items() if v is not None}
    
    if not valid_results:
        print("\n❌ No valid analysis results")
        return {'recommendations': []}
    
    # Separate by signal
    buy_candidates = []
    no_trade_candidates = []
    
    for symbol, data in valid_results.items():
        if data['signal'] == 'BUY' and data['expected_value'] > 0:
            buy_candidates.append((symbol, data))
        else:
            no_trade_candidates.append((symbol, data))
    
    # Sort buy candidates by EV * confidence
    buy_candidates.sort(key=lambda x: x[1]['expected_value'] * x[1]['confidence'], reverse=True)
    
    # Generate recommendations
    recommendations = []
    
    print("\n" + "=" * 100)
    print("📈 BUY RECOMMENDATIONS (Use TP/SL for exits)")
    print("=" * 100)
    
    if buy_candidates:
        print(f"\n{'Symbol':<8} {'Price':<10} {'Conf':<8} {'EV':<10} "
              f"{'Win%':<8} {'Sharpe':<10} {'Rating'}")
        print("-" * 100)
        
        for symbol, data in buy_candidates:
            # Calculate overall rating
            ev_score = min(data['expected_value'] / 0.005, 1.0)  # Cap at 0.5%
            conf_score = data['confidence']
            momentum_score = data['momentum_score'] / 100
            
            overall_rating = (ev_score * 0.4 + conf_score * 0.4 + momentum_score * 0.2)
            
            if overall_rating > 0.75:
                rating = "⭐⭐⭐⭐⭐ STRONG BUY"
            elif overall_rating > 0.65:
                rating = "⭐⭐⭐⭐ BUY"
            elif overall_rating > 0.55:
                rating = "⭐⭐⭐ MODERATE BUY"
            else:
                rating = "⭐⭐ CAUTIOUS BUY"
            
            print(f"{symbol:<8} ${data['price']:<9.2f} "
                  f"{data['confidence']*100:<7.1f}% {data['expected_value']*100:<9.3f}% "
                  f"{data['win_probability']*100:<7.1f}% {data['sharpe_ev']:<9.3f} {rating}")
            
            recommendations.append({
                'symbol': symbol,
                'action': 'BUY',
                'price': data['price'],
                'confidence': data['confidence'],
                'expected_value': data['expected_value'],
                'win_probability': data['win_probability'],
                'rating': rating,
                'overall_score': overall_rating
            })
    else:
        print("\n⚠️ No BUY signals with positive EV at this time")
        print("💡 Tip: Try different price ranges or wait for market conditions to improve")
    
    # Show NO_TRADE stocks (for reference)
    if no_trade_candidates and len(no_trade_candidates) <= 5:
        print("\n" + "=" * 100)
        print(f"⏸️ NO TRADE - Insufficient Edge ({len(no_trade_candidates)} stocks)")
        print("=" * 100)
        for symbol, data in no_trade_candidates[:5]:  # Show max 5
            print(f"   {symbol}: EV={data['expected_value']*100:.3f}%, Conf={data['confidence']*100:.1f}%")
    
    # Summary
    print("\n" + "=" * 100)
    print("📋 SUMMARY")
    print("=" * 100)
    
    print(f"\n   Stocks Analyzed: {len(valid_results)}")
    print(f"   BUY Signals: {len(buy_candidates)}")
    print(f"   NO_TRADE: {len(no_trade_candidates)}")
    
    if buy_candidates:
        best_buy = buy_candidates[0]
        print(f"\n   🏆 TOP PICK: {best_buy[0]}")
        print(f"      Price: ${best_buy[1]['price']:.2f}")
        print(f"      Expected Value: {best_buy[1]['expected_value']*100:.3f}%")
        print(f"      Win Probability: {best_buy[1]['win_probability']*100:.1f}%")
        print(f"      Confidence: {best_buy[1]['confidence']*100:.1f}%")
        print(f"\n   💡 Suggested Position Sizing:")
        if best_buy[1]['expected_value'] > 0.005:
            print(f"      Full size (high EV)")
        elif best_buy[1]['expected_value'] > 0.002:
            print(f"      Normal size")
        else:
            print(f"      Reduced size (lower EV)")
        print(f"\n   📊 Exit Strategy:")
        print(f"      Use Take Profit (TP) and Stop Loss (SL)")
        print(f"      Suggested TP: 1.5-2x Expected Return")
        print(f"      Suggested SL: Based on volatility/ATR")
    else:
        print(f"\n   ⚠️ No BUY opportunities found")
        print(f"   💡 Consider:")
        print(f"      - Expanding price range")
        print(f"      - Waiting for better market conditions")
        print(f"      - Trying different momentum filters")
    
    print("\n" + "=" * 100)
    
    return {
        'recommendations': recommendations,
        'buy_count': len(buy_candidates),
        'no_trade_count': len(no_trade_candidates),
        'top_pick': buy_candidates[0][0] if buy_candidates else None
    }


def main():
    """
    Main execution: Momentum scan → EV analysis → Trading signals
    """
    print("\n" + "=" * 100)
    print("🚀 MOMENTUM + EV AUTOMATED TRADING SYSTEM")
    print("=" * 100)
    
    # Parse arguments
    min_price = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    max_price = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    fast_mode = '--fast' in sys.argv or '-f' in sys.argv
    
    print(f"\n⚙️ Configuration:")
    print(f"   Price Range: ${min_price} - ${max_price}")
    print(f"   Top Stocks: {top_n}")
    print(f"   Mode: {'Fast (5m+1d)' if fast_mode else 'Full (all timeframes)'}")
    
    # Step 1: Find top momentum stocks
    top_stocks = find_top_momentum_stocks(min_price, max_price, top_n)
    
    if not top_stocks:
        print("\n❌ No momentum stocks found. Exiting.")
        return
    
    # Step 2: Analyze with EV classifier
    results = analyze_with_ev_classifier(top_stocks, fast_mode)
    
    # Step 3: Generate recommendations
    recommendations = generate_trading_recommendations(results)
    
    # Step 4: Export results
    output_file = 'trading_signals.json'
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': pd.Timestamp.now().isoformat(),
            'config': {
                'min_price': min_price,
                'max_price': max_price,
                'top_n': top_n
            },
            'momentum_stocks': top_stocks,
            'analysis_results': {k: v for k, v in results.items() if v is not None},
            'recommendations': recommendations
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "=" * 100)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 100)


if __name__ == '__main__':
    import pandas as pd
    main()

