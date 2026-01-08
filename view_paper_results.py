"""
View Paper Trading Results
Analyzes and displays paper trading performance
"""

import json
import pandas as pd
from datetime import datetime
import sys

def load_trades():
    """Load trade log"""
    try:
        with open('paper_trades_log.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No trade log found. Run paper trading first!")
        sys.exit(1)

def print_summary(data):
    """Print performance summary"""
    print("\n" + "="*70)
    print("📈 PAPER TRADING PERFORMANCE SUMMARY")
    print("="*70)
    
    initial = data['initial_capital']
    current = data['current_capital']
    total_return = ((current - initial) / initial) * 100
    
    print(f"\n💰 CAPITAL:")
    print(f"   Initial:    ${initial:,.2f}")
    print(f"   Current:    ${current:,.2f}")
    print(f"   Return:     {total_return:+.2f}%")
    print(f"   P&L:        ${current - initial:+,.2f}")
    
    open_pos = data.get('open_positions', [])
    closed = data.get('closed_trades', [])
    
    print(f"\n📊 POSITIONS:")
    print(f"   Open:       {len(open_pos)}")
    print(f"   Closed:     {len(closed)}")
    
    if closed:
        print_closed_trades_stats(closed)
    
    if open_pos:
        print_open_positions(open_pos)
    
    print("\n" + "="*70)

def print_closed_trades_stats(trades):
    """Print statistics for closed trades"""
    df = pd.DataFrame(trades)
    
    winning = df[df['pnl'] > 0]
    losing = df[df['pnl'] <= 0]
    
    print(f"\n📊 CLOSED TRADES STATS:")
    print(f"   Total Trades:    {len(df)}")
    print(f"   Winners:         {len(winning)} ({len(winning)/len(df)*100:.1f}%)")
    print(f"   Losers:          {len(losing)} ({len(losing)/len(df)*100:.1f}%)")
    
    print(f"\n💵 P&L:")
    print(f"   Total:           ${df['pnl'].sum():+,.2f}")
    print(f"   Average:         ${df['pnl'].mean():+,.2f}")
    print(f"   Best Trade:      ${df['pnl'].max():+,.2f}")
    print(f"   Worst Trade:     ${df['pnl'].min():+,.2f}")
    
    if len(winning) > 0 and len(losing) > 0:
        avg_win = winning['pnl'].mean()
        avg_loss = abs(losing['pnl'].mean())
        print(f"\n📈 WIN/LOSS:")
        print(f"   Avg Win:         ${avg_win:,.2f}")
        print(f"   Avg Loss:        ${avg_loss:,.2f}")
        print(f"   Win/Loss Ratio:  {avg_win/avg_loss:.2f}x")
    
    print(f"\n⏱️  EXIT REASONS:")
    for reason in df['exit_reason'].value_counts().items():
        print(f"   {reason[0]:<15} {reason[1]} trades")

def print_open_positions(positions):
    """Print current open positions"""
    print(f"\n🔓 OPEN POSITIONS:")
    
    for pos in positions:
        print(f"\n   {pos['symbol']}:")
        print(f"      Entry:        ${pos['entry_price']:.2f}")
        print(f"      Shares:       {pos['shares']}")
        print(f"      Take Profit:  ${pos['take_profit']:.2f}")
        print(f"      Stop Loss:    ${pos['stop_loss']:.2f}")
        print(f"      Entry Time:   {pos['entry_time'][:19]}")

def print_trade_history(trades):
    """Print detailed trade history"""
    if not trades:
        print("\n📋 No closed trades yet")
        return
    
    print("\n" + "="*70)
    print("📋 TRADE HISTORY (Most Recent First)")
    print("="*70)
    
    # Sort by exit time (most recent first)
    sorted_trades = sorted(trades, key=lambda x: x['exit_time'], reverse=True)
    
    for i, trade in enumerate(sorted_trades[:20], 1):  # Show last 20
        entry_time = datetime.fromisoformat(trade['entry_time']).strftime('%m/%d %H:%M')
        exit_time = datetime.fromisoformat(trade['exit_time']).strftime('%m/%d %H:%M')
        
        pnl_color = "🟢" if trade['pnl'] > 0 else "🔴"
        
        print(f"\n{i}. {trade['symbol']} {pnl_color}")
        print(f"   Entry: ${trade['entry_price']:.2f} @ {entry_time}")
        print(f"   Exit:  ${trade['exit_price']:.2f} @ {exit_time} ({trade['exit_reason']})")
        print(f"   P&L:   ${trade['pnl']:+.2f} ({trade['return_pct']:+.2f}%)")

def main():
    """Main function"""
    data = load_trades()
    
    # Print summary
    print_summary(data)
    
    # Ask if user wants detailed history
    closed = data.get('closed_trades', [])
    if closed:
        print("\n📜 Show detailed trade history? (y/n): ", end='')
        try:
            response = input().strip().lower()
            if response == 'y':
                print_trade_history(closed)
        except (EOFError, KeyboardInterrupt):
            pass
    
    print("\n✅ Analysis complete!")
    print(f"📁 Full data: paper_trades_log.json")
    print(f"📊 Metrics: paper_trading_performance.json")

if __name__ == '__main__':
    main()

