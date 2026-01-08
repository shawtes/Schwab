"""
Live Paper Trading System
Runs the full momentum scanner + EV classifier in real-time
Simulates trades without risking real money
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import time
import argparse
from typing import Dict, List, Optional, Tuple

# Import trading components
from momentum_scanner import MomentumScanner
from ml_trading.pipeline.multi_timeframe_system import MultiTimeframePredictor, EVClassifier
from ml_trading.data.schwab_fetcher import SchwabDataFetcher

class PaperTrade:
    """Represents a single paper trade"""
    def __init__(self, symbol: str, entry_price: float, shares: int, 
                 entry_time: datetime, signal_data: dict):
        self.symbol = symbol
        self.entry_price = entry_price
        self.shares = shares
        self.entry_time = entry_time
        self.signal_data = signal_data
        
        # Calculate TP/SL based on predicted return
        predicted_return = signal_data.get('predicted_return', 0.01)
        self.take_profit = entry_price * (1 + abs(predicted_return) * 1.5)  # 1.5x predicted
        self.stop_loss = entry_price * (1 - abs(predicted_return) * 0.5)    # 0.5x predicted
        
        self.exit_price = None
        self.exit_time = None
        self.exit_reason = None
        self.pnl = None
        self.return_pct = None
        
    def update_price(self, current_price: float, current_time: datetime) -> bool:
        """Check if TP or SL hit. Returns True if trade should close"""
        if current_price >= self.take_profit:
            self.close_trade(current_price, current_time, "TAKE_PROFIT")
            return True
        elif current_price <= self.stop_loss:
            self.close_trade(current_price, current_time, "STOP_LOSS")
            return True
        return False
    
    def close_trade(self, exit_price: float, exit_time: datetime, reason: str):
        """Close the trade and calculate PnL"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = reason
        self.pnl = (exit_price - self.entry_price) * self.shares
        self.return_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        
    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            'symbol': self.symbol,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'shares': self.shares,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'exit_reason': self.exit_reason,
            'pnl': self.pnl,
            'return_pct': self.return_pct,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'signal_data': self.signal_data
        }

class PaperTradingSystem:
    """Live paper trading system"""
    def __init__(self, 
                 initial_capital: float = 100000,
                 position_size_pct: float = 0.05,
                 max_positions: int = 10,
                 min_ev: float = 0.0003,
                 min_confidence: float = 0.48,
                 scanner_params: dict = None):
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.max_positions = max_positions
        
        # Initialize components
        self.fetcher = SchwabDataFetcher()
        self.scanner = MomentumScanner(
            min_price=scanner_params.get('min_price', 10) if scanner_params else 10,
            max_price=scanner_params.get('max_price', 500) if scanner_params else 500,
            min_volume=scanner_params.get('min_volume', 1000000) if scanner_params else 1000000,
            min_percent_change=scanner_params.get('min_percent_change', 5) if scanner_params else 5,
            max_stocks=scanner_params.get('max_stocks', 20) if scanner_params else 20
        )
        self.ev_classifier = EVClassifier(min_ev=min_ev, min_confidence=min_confidence)
        
        # Trading state
        self.open_positions: Dict[str, PaperTrade] = {}
        self.closed_trades: List[PaperTrade] = []
        self.trade_log_file = "paper_trades_log.json"
        self.performance_file = "paper_trading_performance.json"
        
        # Load existing trades if any
        self._load_trades()
        
    def _load_trades(self):
        """Load existing trades from file"""
        if os.path.exists(self.trade_log_file):
            try:
                with open(self.trade_log_file, 'r') as f:
                    data = json.load(f)
                    print(f"📂 Loaded {len(data.get('closed_trades', []))} historical trades")
            except Exception as e:
                print(f"⚠️  Could not load trade history: {e}")
    
    def _save_trades(self):
        """Save all trades to file"""
        data = {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'open_positions': [trade.to_dict() for trade in self.open_positions.values()],
            'closed_trades': [trade.to_dict() for trade in self.closed_trades],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.trade_log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _calculate_position_size(self, price: float) -> int:
        """Calculate number of shares to buy"""
        position_value = self.current_capital * self.position_size_pct
        shares = int(position_value / price)
        return max(1, shares)  # At least 1 share
    
    def scan_for_opportunities(self) -> List[dict]:
        """Run momentum scanner and EV classifier"""
        print("\n🔍 Scanning for opportunities...")
        
        # Get momentum stocks
        momentum_stocks = self.scanner.scan()
        
        if not momentum_stocks:
            print("   No momentum stocks found")
            return []
        
        print(f"   Found {len(momentum_stocks)} momentum stocks")
        
        # Evaluate with EV classifier
        opportunities = []
        
        for stock in momentum_stocks:
            symbol = stock['symbol']
            
            # Skip if already holding
            if symbol in self.open_positions:
                continue
            
            print(f"   Analyzing {symbol}...")
            
            try:
                # Get signal from EV classifier
                signal = self.ev_classifier.predict_signal(symbol)
                
                if signal['signal'] == 'BUY':
                    opportunities.append({
                        'symbol': symbol,
                        'current_price': stock['close'],
                        'momentum_data': stock,
                        'signal_data': signal
                    })
                    print(f"      ✅ BUY signal - EV: {signal['ev']:.4f}, Confidence: {signal['confidence']:.2%}")
                else:
                    print(f"      ❌ NO_TRADE - EV: {signal['ev']:.4f}, Confidence: {signal['confidence']:.2%}")
                    
            except Exception as e:
                print(f"      ⚠️  Error analyzing {symbol}: {e}")
        
        return opportunities
    
    def open_position(self, opportunity: dict) -> Optional[PaperTrade]:
        """Open a new paper position"""
        if len(self.open_positions) >= self.max_positions:
            print(f"   ⚠️  Max positions ({self.max_positions}) reached")
            return None
        
        symbol = opportunity['symbol']
        price = opportunity['current_price']
        shares = self._calculate_position_size(price)
        cost = shares * price
        
        if cost > self.current_capital:
            print(f"   ⚠️  Insufficient capital for {symbol}")
            return None
        
        # Create trade
        trade = PaperTrade(
            symbol=symbol,
            entry_price=price,
            shares=shares,
            entry_time=datetime.now(),
            signal_data=opportunity['signal_data']
        )
        
        # Update capital and positions
        self.current_capital -= cost
        self.open_positions[symbol] = trade
        
        print(f"\n🟢 OPENED POSITION: {symbol}")
        print(f"   Entry: ${price:.2f} x {shares} shares = ${cost:.2f}")
        print(f"   Take Profit: ${trade.take_profit:.2f}")
        print(f"   Stop Loss: ${trade.stop_loss:.2f}")
        print(f"   Remaining Capital: ${self.current_capital:.2f}")
        
        self._save_trades()
        return trade
    
    def update_positions(self):
        """Update all open positions and check TP/SL"""
        if not self.open_positions:
            return
        
        print("\n📊 Updating open positions...")
        
        to_close = []
        for symbol, trade in self.open_positions.items():
            try:
                # Get current price
                df = self.fetcher.fetch_data(
                    symbol=symbol,
                    period_type='day',
                    period=1,
                    frequency_type='minute',
                    frequency=1
                )
                
                if df.empty:
                    print(f"   ⚠️  No data for {symbol}")
                    continue
                
                current_price = df['close'].iloc[-1]
                current_time = datetime.now()
                
                # Calculate unrealized PnL
                unrealized_pnl = (current_price - trade.entry_price) * trade.shares
                unrealized_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                
                print(f"\n   {symbol}:")
                print(f"      Current: ${current_price:.2f} (Entry: ${trade.entry_price:.2f})")
                print(f"      Unrealized P&L: ${unrealized_pnl:.2f} ({unrealized_pct:+.2f}%)")
                print(f"      TP: ${trade.take_profit:.2f} | SL: ${trade.stop_loss:.2f}")
                
                # Check if TP/SL hit
                if trade.update_price(current_price, current_time):
                    to_close.append(symbol)
                    
            except Exception as e:
                print(f"   ⚠️  Error updating {symbol}: {e}")
        
        # Close positions that hit TP/SL
        for symbol in to_close:
            self._close_position(symbol)
    
    def _close_position(self, symbol: str):
        """Close a position and update capital"""
        trade = self.open_positions.pop(symbol)
        
        # Return capital
        proceeds = trade.exit_price * trade.shares
        self.current_capital += proceeds
        
        # Add to closed trades
        self.closed_trades.append(trade)
        
        print(f"\n🔴 CLOSED POSITION: {symbol}")
        print(f"   Exit: ${trade.exit_price:.2f} x {trade.shares} shares = ${proceeds:.2f}")
        print(f"   Reason: {trade.exit_reason}")
        print(f"   P&L: ${trade.pnl:.2f} ({trade.return_pct:+.2f}%)")
        print(f"   Current Capital: ${self.current_capital:.2f}")
        
        self._save_trades()
    
    def get_performance_stats(self) -> dict:
        """Calculate performance statistics"""
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'total_return': 0
            }
        
        winning_trades = [t for t in self.closed_trades if t.pnl > 0]
        losing_trades = [t for t in self.closed_trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in self.closed_trades)
        total_return = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        stats = {
            'total_trades': len(self.closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.closed_trades) * 100,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(self.closed_trades),
            'avg_win': sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            'avg_loss': sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0,
            'total_return': total_return,
            'current_capital': self.current_capital,
            'open_positions': len(self.open_positions)
        }
        
        # Save performance stats
        with open(self.performance_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def print_status(self):
        """Print current system status"""
        stats = self.get_performance_stats()
        
        print("\n" + "="*60)
        print("📈 PAPER TRADING SYSTEM STATUS")
        print("="*60)
        print(f"Initial Capital:     ${self.initial_capital:,.2f}")
        print(f"Current Capital:     ${stats['current_capital']:,.2f}")
        print(f"Total Return:        {stats['total_return']:+.2f}%")
        print(f"Total P&L:           ${stats['total_pnl']:+,.2f}")
        print(f"\nOpen Positions:      {stats['open_positions']}/{self.max_positions}")
        print(f"Closed Trades:       {stats['total_trades']}")
        
        if stats['total_trades'] > 0:
            print(f"Win Rate:            {stats['win_rate']:.1f}% ({stats['winning_trades']}W / {stats['losing_trades']}L)")
            print(f"Avg P&L per Trade:   ${stats['avg_pnl']:+,.2f}")
            print(f"Avg Win:             ${stats['avg_win']:+,.2f}")
            print(f"Avg Loss:            ${stats['avg_loss']:+,.2f}")
        
        print("="*60)
    
    def run_cycle(self):
        """Run one complete trading cycle"""
        print(f"\n🔄 Starting trading cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Update existing positions
        self.update_positions()
        
        # 2. Scan for new opportunities if we have room
        if len(self.open_positions) < self.max_positions:
            opportunities = self.scan_for_opportunities()
            
            # 3. Open new positions
            for opp in opportunities:
                if len(self.open_positions) >= self.max_positions:
                    break
                self.open_position(opp)
        else:
            print(f"\n📦 Portfolio full ({len(self.open_positions)}/{self.max_positions} positions)")
        
        # 4. Print status
        self.print_status()
    
    def run_live(self, check_interval_minutes: int = 5):
        """Run live paper trading continuously"""
        print("\n🚀 Starting LIVE Paper Trading System")
        print(f"   Check interval: {check_interval_minutes} minutes")
        print(f"   Initial capital: ${self.initial_capital:,.2f}")
        print(f"   Max positions: {self.max_positions}")
        print(f"   Position size: {self.position_size_pct*100}%")
        print("\n   Press Ctrl+C to stop")
        
        try:
            while True:
                # Check if market is open (9:30 AM - 4:00 PM ET)
                now = datetime.now()
                market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
                market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
                
                if market_open <= now <= market_close:
                    # Run trading cycle
                    self.run_cycle()
                else:
                    print(f"\n💤 Market closed. Next check at market open.")
                
                # Wait for next cycle
                print(f"\n⏰ Next check in {check_interval_minutes} minutes...")
                time.sleep(check_interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping paper trading system...")
            self.print_status()
            print("\n✅ All trades saved to:", self.trade_log_file)

def main():
    parser = argparse.ArgumentParser(description='Live Paper Trading System')
    
    # Capital settings
    parser.add_argument('--capital', type=float, default=100000,
                       help='Initial capital (default: $100,000)')
    parser.add_argument('--position-size', type=float, default=0.05,
                       help='Position size as % of capital (default: 0.05 = 5%%)')
    parser.add_argument('--max-positions', type=int, default=10,
                       help='Maximum number of open positions (default: 10)')
    
    # EV Classifier settings
    parser.add_argument('--min-ev', type=float, default=0.0003,
                       help='Minimum EV threshold (default: 0.0003 = 0.03%%)')
    parser.add_argument('--min-confidence', type=float, default=0.48,
                       help='Minimum confidence threshold (default: 0.48 = 48%%)')
    
    # Scanner settings
    parser.add_argument('--min-price', type=float, default=10,
                       help='Minimum stock price (default: $10)')
    parser.add_argument('--max-price', type=float, default=500,
                       help='Maximum stock price (default: $500)')
    parser.add_argument('--min-volume', type=int, default=1000000,
                       help='Minimum daily volume (default: 1,000,000)')
    parser.add_argument('--min-change', type=float, default=5,
                       help='Minimum %% price change (default: 5%%)')
    parser.add_argument('--max-stocks', type=int, default=20,
                       help='Maximum stocks to scan (default: 20)')
    
    # Runtime settings
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in minutes (default: 5)')
    parser.add_argument('--single-cycle', action='store_true',
                       help='Run single cycle instead of continuous')
    
    args = parser.parse_args()
    
    # Create scanner params
    scanner_params = {
        'min_price': args.min_price,
        'max_price': args.max_price,
        'min_volume': args.min_volume,
        'min_percent_change': args.min_change,
        'max_stocks': args.max_stocks
    }
    
    # Initialize system
    system = PaperTradingSystem(
        initial_capital=args.capital,
        position_size_pct=args.position_size,
        max_positions=args.max_positions,
        min_ev=args.min_ev,
        min_confidence=args.min_confidence,
        scanner_params=scanner_params
    )
    
    # Run
    if args.single_cycle:
        system.run_cycle()
    else:
        system.run_live(check_interval_minutes=args.interval)

if __name__ == '__main__':
    main()

