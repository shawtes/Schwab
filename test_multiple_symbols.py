"""
Test EV Classifier System on Multiple Symbols
Quick comparison to find best-performing symbols
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_ev_classifier_system import test_multi_timeframe_ev_system


def test_multiple_symbols(symbols=None):
    """
    Test multiple symbols and compare results
    """
    if symbols is None:
        symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'META']
    
    print("\n" + "=" * 100)
    print("MULTI-SYMBOL EV SYSTEM COMPARISON")
    print("=" * 100)
    
    results = {}
    
    for symbol in symbols:
        print(f"\n\n{'=' * 100}")
        print(f"Testing {symbol}...")
        print(f"{'=' * 100}\n")
        
        try:
            result = test_multi_timeframe_ev_system(symbol, use_all_timeframes=False)
            
            if result and 'test_metrics' in result:
                metrics = result['test_metrics']
                results[symbol] = {
                    'signal': result['signal'],
                    'confidence': result['confidence'],
                    'ev': result['ev_metrics']['expected_value'],
                    'avg_ev': metrics['avg_ev'],
                    'direction_accuracy': metrics['direction_accuracy'],
                    'buy_signals': metrics['buy_signals'],
                    'sell_signals': metrics['sell_signals'],
                    'buy_return': metrics['buy_return'],
                    'sell_return': metrics['sell_return']
                }
        except Exception as e:
            print(f"\n❌ {symbol} failed: {e}")
            results[symbol] = None
    
    # Print comparison
    print("\n\n" + "=" * 100)
    print("RESULTS COMPARISON")
    print("=" * 100)
    
    print("\n{:<8} {:<8} {:<10} {:<8} {:<10} {:<10} {:<12}".format(
        "Symbol", "Signal", "Confidence", "Avg EV", "Dir Acc", "BUY Ret", "SELL Ret"
    ))
    print("-" * 100)
    
    for symbol, result in results.items():
        if result:
            print("{:<8} {:<8} {:<10.1f}% {:<8.3f}% {:<10.1f}% {:<10.2f}% {:<12.2f}%".format(
                symbol,
                result['signal'],
                result['confidence'] * 100,
                result['avg_ev'] * 100,
                result['direction_accuracy'] * 100,
                result['buy_return'] * 100,
                result['sell_return'] * 100
            ))
        else:
            print(f"{symbol:<8} FAILED")
    
    print("\n" + "=" * 100)
    
    # Find best performers
    valid_results = {k: v for k, v in results.items() if v is not None}
    
    if valid_results:
        best_ev = max(valid_results.items(), key=lambda x: x[1]['avg_ev'])
        best_accuracy = max(valid_results.items(), key=lambda x: x[1]['direction_accuracy'])
        
        print("\n🏆 Best Average EV: {} ({:.3f}%)".format(
            best_ev[0], best_ev[1]['avg_ev'] * 100
        ))
        print("🏆 Best Direction Accuracy: {} ({:.1f}%)".format(
            best_accuracy[0], best_accuracy[1]['direction_accuracy'] * 100
        ))
        
        # Recommend best for trading
        buy_symbols = [k for k, v in valid_results.items() 
                      if v['signal'] == 'BUY' and v['ev'] > 0.001]
        
        if buy_symbols:
            print(f"\n✅ Recommended BUY: {', '.join(buy_symbols)}")
        else:
            print(f"\n⏸️ No strong BUY signals at this time")
    
    print("\n" + "=" * 100)
    
    return results


if __name__ == '__main__':
    # Default symbols
    symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'META']
    
    # Or use command line args
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    
    results = test_multiple_symbols(symbols)

