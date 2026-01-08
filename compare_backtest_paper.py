"""
Compare Backtest vs Paper Trading Results
Shows side-by-side comparison to validate strategy
"""

import json
import pandas as pd
from pathlib import Path

def load_backtest_results():
    """Load backtest results"""
    # Try to find most recent backtest log
    backtest_files = list(Path('.').glob('backtest_log_*.json'))
    
    if not backtest_files:
        print("❌ No backtest results found")
        return None
    
    # Get most recent
    latest = max(backtest_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest, 'r') as f:
        data = json.load(f)
    
    print(f"📁 Loaded backtest: {latest}")
    return data

def load_paper_results():
    """Load paper trading results"""
    try:
        with open('paper_trades_log.json', 'r') as f:
            data = json.load(f)
        print(f"📁 Loaded paper trading results")
        return data
    except FileNotFoundError:
        print("❌ No paper trading results found")
        return None

def calculate_backtest_stats(data):
    """Calculate stats from backtest data"""
    trades = data.get('trades', [])
    
    if not trades:
        return None
    
    df = pd.DataFrame(trades)
    
    winning = df[df['pnl'] > 0]
    losing = df[df['pnl'] <= 0]
    
    initial = data.get('initial_capital', 100000)
    final = data.get('final_capital', initial)
    
    return {
        'total_trades': len(df),
        'winning_trades': len(winning),
        'losing_trades': len(losing),
        'win_rate': len(winning) / len(df) * 100 if len(df) > 0 else 0,
        'total_pnl': df['pnl'].sum(),
        'avg_pnl': df['pnl'].mean(),
        'avg_win': winning['pnl'].mean() if len(winning) > 0 else 0,
        'avg_loss': losing['pnl'].mean() if len(losing) > 0 else 0,
        'total_return': ((final - initial) / initial) * 100,
        'initial_capital': initial,
        'final_capital': final
    }

def calculate_paper_stats(data):
    """Calculate stats from paper trading data"""
    trades = data.get('closed_trades', [])
    
    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'total_return': 0,
            'initial_capital': data.get('initial_capital', 100000),
            'final_capital': data.get('current_capital', data.get('initial_capital', 100000))
        }
    
    df = pd.DataFrame(trades)
    
    winning = df[df['pnl'] > 0]
    losing = df[df['pnl'] <= 0]
    
    initial = data.get('initial_capital', 100000)
    final = data.get('current_capital', initial)
    
    return {
        'total_trades': len(df),
        'winning_trades': len(winning),
        'losing_trades': len(losing),
        'win_rate': len(winning) / len(df) * 100,
        'total_pnl': df['pnl'].sum(),
        'avg_pnl': df['pnl'].mean(),
        'avg_win': winning['pnl'].mean() if len(winning) > 0 else 0,
        'avg_loss': losing['pnl'].mean() if len(losing) > 0 else 0,
        'total_return': ((final - initial) / initial) * 100,
        'initial_capital': initial,
        'final_capital': final
    }

def compare_stats(backtest_stats, paper_stats):
    """Compare backtest vs paper trading"""
    print("\n" + "="*90)
    print("📊 BACKTEST vs PAPER TRADING COMPARISON")
    print("="*90)
    
    # Header
    print(f"\n{'Metric':<30} {'Backtest':<25} {'Paper Trading':<25} {'Diff':<10}")
    print("-"*90)
    
    # Total Trades
    print(f"{'Total Trades':<30} {backtest_stats['total_trades']:<25} {paper_stats['total_trades']:<25}", end='')
    if paper_stats['total_trades'] < 10:
        print("⚠️  Low")
    else:
        print("✅")
    
    # Win Rate
    bt_wr = backtest_stats['win_rate']
    pt_wr = paper_stats['win_rate']
    diff_wr = pt_wr - bt_wr
    
    print(f"{'Win Rate':<30} {bt_wr:.1f}%{' '*20} {pt_wr:.1f}%{' '*20}", end='')
    if abs(diff_wr) < 5:
        print(f"{diff_wr:+.1f}% ✅")
    elif diff_wr > 0:
        print(f"{diff_wr:+.1f}% 🎉")
    else:
        print(f"{diff_wr:+.1f}% ⚠️")
    
    # Total Return
    bt_ret = backtest_stats['total_return']
    pt_ret = paper_stats['total_return']
    
    print(f"{'Total Return':<30} {bt_ret:+.2f}%{' '*19} {pt_ret:+.2f}%{' '*19}", end='')
    if pt_ret > 0:
        print("✅")
    else:
        print("❌")
    
    # Average P&L
    bt_avg = backtest_stats['avg_pnl']
    pt_avg = paper_stats['avg_pnl']
    
    print(f"{'Avg P&L per Trade':<30} ${bt_avg:+,.2f}{' '*17} ${pt_avg:+,.2f}{' '*17}", end='')
    if pt_avg > 0:
        print("✅")
    else:
        print("❌")
    
    # Win/Loss Ratio
    if backtest_stats['avg_loss'] != 0:
        bt_ratio = abs(backtest_stats['avg_win'] / backtest_stats['avg_loss'])
    else:
        bt_ratio = 0
    
    if paper_stats['avg_loss'] != 0:
        pt_ratio = abs(paper_stats['avg_win'] / paper_stats['avg_loss'])
    else:
        pt_ratio = 0
    
    print(f"{'Win/Loss Ratio':<30} {bt_ratio:.2f}x{' '*20} {pt_ratio:.2f}x{' '*20}", end='')
    if pt_ratio >= 1.0:
        print("✅")
    else:
        print("⚠️")
    
    print("-"*90)
    
    # Capital
    print(f"\n{'Initial Capital':<30} ${backtest_stats['initial_capital']:,.2f}")
    print(f"{'Backtest Final Capital':<30} ${backtest_stats['final_capital']:,.2f}")
    print(f"{'Paper Trading Capital':<30} ${paper_stats['final_capital']:,.2f}")
    
    print("\n" + "="*90)

def provide_recommendations(backtest_stats, paper_stats):
    """Provide go/no-go recommendations"""
    print("\n🎯 RECOMMENDATIONS")
    print("="*90)
    
    checks = []
    
    # Check 1: Enough trades
    if paper_stats['total_trades'] >= 10:
        checks.append(("✅", "Enough trades for statistical significance"))
    else:
        checks.append(("⚠️", f"Only {paper_stats['total_trades']} trades - run longer for better stats"))
    
    # Check 2: Win rate
    if paper_stats['win_rate'] >= 50:
        checks.append(("✅", f"Win rate {paper_stats['win_rate']:.1f}% is good"))
    elif paper_stats['win_rate'] >= 45:
        checks.append(("⚠️", f"Win rate {paper_stats['win_rate']:.1f}% is acceptable but watch closely"))
    else:
        checks.append(("❌", f"Win rate {paper_stats['win_rate']:.1f}% is too low"))
    
    # Check 3: Positive return
    if paper_stats['total_return'] > 0:
        checks.append(("✅", f"Positive return of {paper_stats['total_return']:+.2f}%"))
    else:
        checks.append(("❌", f"Negative return of {paper_stats['total_return']:+.2f}%"))
    
    # Check 4: Win/Loss ratio
    if paper_stats['avg_loss'] != 0:
        ratio = abs(paper_stats['avg_win'] / paper_stats['avg_loss'])
        if ratio >= 1.0:
            checks.append(("✅", f"Win/Loss ratio {ratio:.2f}x is favorable"))
        else:
            checks.append(("⚠️", f"Win/Loss ratio {ratio:.2f}x - wins smaller than losses"))
    
    # Check 5: Consistency with backtest
    wr_diff = abs(paper_stats['win_rate'] - backtest_stats['win_rate'])
    if wr_diff < 5:
        checks.append(("✅", "Win rate matches backtest closely"))
    elif wr_diff < 10:
        checks.append(("⚠️", f"Win rate differs by {wr_diff:.1f}% from backtest"))
    else:
        checks.append(("❌", f"Win rate differs significantly ({wr_diff:.1f}%) from backtest"))
    
    # Print checks
    print()
    for emoji, message in checks:
        print(f"{emoji} {message}")
    
    # Final decision
    print("\n" + "="*90)
    
    go_count = sum(1 for emoji, _ in checks if emoji == "✅")
    warn_count = sum(1 for emoji, _ in checks if emoji == "⚠️")
    no_go_count = sum(1 for emoji, _ in checks if emoji == "❌")
    
    print(f"\n📊 SCORE: {go_count} ✅  |  {warn_count} ⚠️  |  {no_go_count} ❌")
    
    if no_go_count > 0:
        print("\n❌ NOT READY FOR LIVE TRADING")
        print("   - Fix issues and continue paper trading")
        print("   - Adjust parameters (min-ev, min-confidence)")
        print("   - Verify backtest on recent data")
    elif warn_count > 2:
        print("\n⚠️  PROCEED WITH CAUTION")
        print("   - Run paper trading longer for more data")
        print("   - Start with very small capital if going live")
        print("   - Monitor closely")
    else:
        print("\n🎉 READY FOR LIVE TRADING!")
        print("   - Start with small capital ($500-$1000)")
        print("   - Use same parameters as paper trading")
        print("   - Scale up gradually as you gain confidence")
    
    print("\n" + "="*90)

def main():
    """Main function"""
    # Load data
    backtest = load_backtest_results()
    paper = load_paper_results()
    
    if not backtest or not paper:
        print("\n⚠️  Need both backtest and paper trading results to compare")
        return
    
    # Calculate stats
    backtest_stats = calculate_backtest_stats(backtest)
    paper_stats = calculate_paper_stats(paper)
    
    if not backtest_stats:
        print("\n❌ No trades in backtest")
        return
    
    # Compare
    compare_stats(backtest_stats, paper_stats)
    
    # Recommendations
    provide_recommendations(backtest_stats, paper_stats)
    
    print("\n💡 TIP: Run paper trading for at least 1-2 weeks before going live!")

if __name__ == '__main__':
    main()

