"""
Full System Backtest - Momentum Scanner + EV Classifier

Simulates the complete trading workflow:
1. Run momentum scanner daily
2. Get top N momentum stocks
3. Run EV classifier on each
4. Take BUY signals
5. Manage positions with TP/SL
6. Track performance

This is how the system would actually be used in production.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
web_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web-trading-app')
if os.path.exists(web_app_path):
    sys.path.append(web_app_path)

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from ml_trading.pipeline.multi_timeframe_system import EVClassifier

load_dotenv()
import schwabdev

# Import momentum scanner
try:
    from momentum_scanner import scan_momentum_stocks
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "momentum_scanner",
        os.path.join(web_app_path, "momentum_scanner.py")
    )
    momentum_scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(momentum_scanner)
    scan_momentum_stocks = momentum_scanner.scan_momentum_stocks


class FullSystemBacktester:
    """
    Backtest the complete momentum + EV system
    """
    
    def __init__(self, initial_capital=10000, risk_per_trade=0.02,
                 max_positions=3, tp_multiplier=1.5, sl_multiplier=2.0,
                 min_ev=0.0003, min_confidence=0.48):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            risk_per_trade: Risk per trade as fraction
            max_positions: Maximum concurrent positions
            tp_multiplier: Take profit multiplier
            sl_multiplier: Stop loss multiplier (ATR)
            min_ev: Minimum EV for BUY signal
            min_confidence: Minimum win probability for BUY signal
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.tp_multiplier = tp_multiplier
        self.sl_multiplier = sl_multiplier
        self.min_ev = min_ev
        self.min_confidence = min_confidence
        
        self.trades = []
        self.equity_curve = []
        self.open_positions = {}  # {symbol: position_dict}
        self.daily_scans = []
        
        # Initialize Schwab client
        try:
            self.client = schwabdev.Client(
                os.getenv('app_key'),
                os.getenv('app_secret'),
                os.getenv('callback_url', 'https://127.0.0.1')
            )
            self.fetcher = SchwabDataFetcher(self.client)
        except Exception as e:
            print(f"❌ Failed to initialize Schwab client: {e}")
            self.client = None
            self.fetcher = None
    
    def run_momentum_scan(self, min_price=2.0, max_price=20.0, top_n=3):
        """
        Run momentum scanner
        
        Returns:
            list: Top momentum stocks
        """
        filters = {
            'minPrice': min_price,
            'maxPrice': max_price,
            'minPercentChange': 1.0,
            'minRVOL': 1.2,
            'minVolume': 500000,
            'rsiMin': 50,
            'rsiMax': 85
        }
        
        try:
            results = scan_momentum_stocks(filters)
            if 'results' in results:
                return results['results'][:top_n]
        except Exception as e:
            print(f"   ⚠️ Momentum scan error: {e}")
        
        return []
    
    def calculate_position_size(self, price, stop_loss, confidence):
        """Calculate position size based on risk"""
        # Available capital for this trade
        available_capital = self.capital
        
        # Risk amount
        risk_amount = available_capital * self.risk_per_trade
        
        # Adjust by confidence
        adjusted_risk = risk_amount * confidence
        
        # Risk per share
        risk_per_share = abs(price - stop_loss)
        
        if risk_per_share > 0:
            shares = int(adjusted_risk / risk_per_share)
        else:
            shares = 0
        
        # Ensure we can afford it
        max_shares = int(available_capital / price) if price > 0 else 0
        shares = min(shares, max_shares)
        
        return shares
    
    def evaluate_stock_for_entry(self, symbol, current_date):
        """
        Evaluate a stock for BUY signal
        
        Returns:
            dict or None: Signal information if BUY, None otherwise
        """
        try:
            # Fetch data up to current date
            df = self.fetcher.get_price_history(
                symbol,
                periodType='year',
                period=2,  # 2 years for training
                frequencyType='daily',
                frequency=1
            )
            
            if df is None or len(df) < 100:
                return None
            
            # Only use data up to current_date (no look-ahead)
            df = df[df.index <= current_date]
            
            if len(df) < 100:
                return None
            
            # Create features
            features_df = self.fetcher.create_features(df)
            
            if features_df is None or len(features_df) < 50:
                return None
            
            # Prepare for ML
            model = EnsembleTradingModel(task='regression', random_state=42)
            X = model.prepare_features(features_df)
            y = df['close'].pct_change().shift(-1).dropna()
            
            # Align
            common_idx = features_df.index.intersection(y.index)
            X_aligned = features_df.loc[common_idx]
            X_values = model.prepare_features(X_aligned)
            y_aligned = y.loc[common_idx]
            
            # Clean
            X_values = np.nan_to_num(X_values, nan=0.0, posinf=1e10, neginf=-1e10)
            
            # Train EV classifier on recent data
            train_size = int(len(X_values) * 0.8)
            X_train = X_values[:train_size]
            y_train = y_aligned[:train_size]
            
            if len(X_train) < 50:
                return None
            
            # Train classifier with configurable thresholds
            ev_classifier = EVClassifier(
                min_ev=self.min_ev,
                min_confidence=self.min_confidence,
                use_timeframe_features=False
            )
            
            ev_classifier.fit(X_train, y_train)
            
            # Get signal for latest bar
            signal, confidence, ev_metrics = ev_classifier.predict_signal(X_values[-1])
            
            if signal == 'BUY' and ev_metrics['expected_value'] > 0:
                current_price = df.loc[current_date, 'close']
                
                # Calculate ATR for stop loss
                atr = df['high'].sub(df['low']).rolling(14).mean()
                current_atr = atr.loc[current_date] if current_date in atr.index else current_price * 0.02
                
                return {
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': confidence,
                    'ev': ev_metrics['expected_value'],
                    'expected_return': ev_metrics['expected_return'],
                    'win_prob': ev_metrics['win_probability'],
                    'price': current_price,
                    'atr': current_atr
                }
            
        except Exception as e:
            #print(f"   ⚠️ Error evaluating {symbol}: {e}")
            pass
        
        return None
    
    def check_exits(self, current_date, price_data):
        """
        Check if any open positions hit TP/SL
        
        Args:
            current_date: Current trading date
            price_data: Dict of {symbol: df} with price data
        """
        for symbol in list(self.open_positions.keys()):
            position = self.open_positions[symbol]
            
            if symbol not in price_data:
                continue
            
            df = price_data[symbol]
            
            if current_date not in df.index:
                continue
            
            high = df.loc[current_date, 'high']
            low = df.loc[current_date, 'low']
            close = df.loc[current_date, 'close']
            
            # Check stop loss
            if low <= position['stop_loss']:
                self.close_position(symbol, position, current_date, position['stop_loss'], 'SL')
            # Check take profit
            elif high >= position['take_profit']:
                self.close_position(symbol, position, current_date, position['take_profit'], 'TP')
    
    def open_position(self, symbol, signal_info, current_date):
        """Open a new position"""
        if len(self.open_positions) >= self.max_positions:
            return False
        
        price = signal_info['price']
        atr = signal_info['atr']
        expected_return = signal_info['expected_return']
        confidence = signal_info['confidence']
        
        # Calculate TP/SL
        tp_return = abs(expected_return) * self.tp_multiplier
        take_profit = price * (1 + tp_return)
        stop_loss = price - (atr * self.sl_multiplier)
        
        # Calculate position size
        shares = self.calculate_position_size(price, stop_loss, confidence)
        
        if shares == 0:
            return False
        
        # Check if we have enough capital
        cost = shares * price
        if cost > self.capital:
            return False
        
        # Open position
        self.capital -= cost
        
        self.open_positions[symbol] = {
            'symbol': symbol,
            'entry_date': current_date,
            'entry_price': price,
            'shares': shares,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'expected_return': expected_return,
            'confidence': confidence,
            'ev': signal_info['ev'],
            'cost': cost
        }
        
        return True
    
    def close_position(self, symbol, position, exit_date, exit_price, reason):
        """Close a position"""
        pnl = (exit_price - position['entry_price']) * position['shares']
        pnl_pct = (exit_price / position['entry_price'] - 1)
        
        # Return capital
        proceeds = position['shares'] * exit_price
        self.capital += proceeds
        
        # Record trade
        trade = {
            'symbol': symbol,
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'shares': position['shares'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': reason,
            'days_held': (exit_date - position['entry_date']).days,
            'expected_return': position['expected_return'],
            'confidence': position['confidence'],
            'ev': position['ev']
        }
        
        self.trades.append(trade)
        del self.open_positions[symbol]
    
    def run_backtest(self, start_date=None, end_date=None, 
                     min_price=2.0, max_price=20.0, top_n=3,
                     scan_frequency_days=1):
        """
        Run full system backtest
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            min_price: Min stock price for momentum scan
            max_price: Max stock price for momentum scan
            top_n: Top N momentum stocks to evaluate
            scan_frequency_days: How often to run momentum scan (1 = daily)
        """
        print(f"\n{'='*100}")
        print(f"FULL SYSTEM BACKTEST")
        print(f"{'='*100}")
        
        if self.fetcher is None:
            print("❌ No Schwab client available")
            return None
        
        # Set date range
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)  # 1 year backtest
        
        print(f"\n⚙️ Configuration:")
        print(f"   Period: {start_date.date()} to {end_date.date()}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Max Positions: {self.max_positions}")
        print(f"   Risk per Trade: {self.risk_per_trade*100:.1f}%")
        print(f"   Price Range: ${min_price}-${max_price}")
        print(f"   Top Stocks: {top_n}")
        print(f"   Scan Frequency: Every {scan_frequency_days} day(s)")
        print(f"   Min EV: {self.min_ev*100:.2f}% (trades must beat this)")
        print(f"   Min Win Prob: {self.min_confidence*100:.0f}% (minimum confidence)")
        
        # Generate trading days
        trading_days = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days
        
        print(f"\n🔄 Running backtest on {len(trading_days)} trading days...")
        
        last_scan_date = None
        momentum_stocks = []
        
        for i, current_date in enumerate(trading_days):
            # Progress indicator
            if i % 20 == 0:
                print(f"   Processing: {current_date.date()} ({i}/{len(trading_days)}) - "
                      f"Capital: ${self.capital:,.0f}, Positions: {len(self.open_positions)}, "
                      f"Trades: {len(self.trades)}")
            
            # Run momentum scan periodically
            if last_scan_date is None or (current_date - last_scan_date).days >= scan_frequency_days:
                momentum_stocks = self.run_momentum_scan(min_price, max_price, top_n)
                last_scan_date = current_date
                
                self.daily_scans.append({
                    'date': current_date,
                    'stocks_found': len(momentum_stocks),
                    'symbols': [s['symbol'] for s in momentum_stocks] if momentum_stocks else []
                })
            
            # Fetch price data for all relevant symbols
            price_data = {}
            
            # Get data for open positions
            for symbol in self.open_positions.keys():
                try:
                    df = self.fetcher.get_price_history(
                        symbol,
                        periodType='month',
                        period=1,
                        frequencyType='daily',
                        frequency=1
                    )
                    if df is not None:
                        price_data[symbol] = df
                except:
                    pass
            
            # Check exits for open positions
            self.check_exits(current_date, price_data)
            
            # Look for new entry signals if we have capacity
            if len(self.open_positions) < self.max_positions and momentum_stocks:
                for stock in momentum_stocks:
                    if len(self.open_positions) >= self.max_positions:
                        break
                    
                    symbol = stock['symbol']
                    
                    # Skip if already in position
                    if symbol in self.open_positions:
                        continue
                    
                    # Evaluate for BUY signal
                    signal_info = self.evaluate_stock_for_entry(symbol, current_date)
                    
                    if signal_info is not None:
                        success = self.open_position(symbol, signal_info, current_date)
                        if success:
                            print(f"   💰 {current_date.date()}: BUY {symbol} @ ${signal_info['price']:.2f} "
                                  f"(EV: {signal_info['ev']*100:.2f}%, Conf: {signal_info['confidence']*100:.0f}%)")
            
            # Track equity curve
            equity = self.capital
            for position in self.open_positions.values():
                # Estimate current value (use latest close)
                if position['symbol'] in price_data and current_date in price_data[position['symbol']].index:
                    current_price = price_data[position['symbol']].loc[current_date, 'close']
                    equity += position['shares'] * current_price
                else:
                    equity += position['cost']  # Use entry value if no data
            
            self.equity_curve.append({
                'date': current_date,
                'equity': equity,
                'capital': self.capital,
                'positions': len(self.open_positions)
            })
        
        # Close remaining positions at end
        print(f"\n📊 Closing {len(self.open_positions)} remaining positions...")
        for symbol in list(self.open_positions.keys()):
            position = self.open_positions[symbol]
            if symbol in price_data and trading_days[-1] in price_data[symbol].index:
                exit_price = price_data[symbol].loc[trading_days[-1], 'close']
            else:
                exit_price = position['entry_price']  # Break even if no data
            
            self.close_position(symbol, position, trading_days[-1], exit_price, 'END')
        
        # Calculate results
        results = self.calculate_results()
        
        return results
    
    def calculate_results(self):
        """Calculate backtest metrics"""
        if len(self.trades) == 0:
            print("\n⚠️ No trades executed")
            return None
        
        trades_df = pd.DataFrame(self.trades)
        
        # Win/Loss stats
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]
        
        win_rate = len(wins) / len(trades_df)
        avg_win = wins['pnl_pct'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl_pct'].mean() if len(losses) > 0 else 0
        
        # Returns
        total_return = (self.capital / self.initial_capital - 1)
        
        # Equity curve analysis
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe ratio
        sharpe = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252) if equity_df['returns'].std() > 0 else 0
        
        # Max drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Profit factor
        gross_profit = wins['pnl'].sum() if len(wins) > 0 else 0
        gross_loss = abs(losses['pnl'].sum()) if len(losses) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Exit reasons
        exit_reasons = trades_df['exit_reason'].value_counts()
        
        results = {
            'total_trades': len(trades_df),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'final_capital': self.capital,
            'exit_reasons': exit_reasons,
            'trades_df': trades_df,
            'equity_df': equity_df,
            'unique_symbols': trades_df['symbol'].nunique(),
            'avg_days_held': trades_df['days_held'].mean()
        }
        
        return results
    
    def print_results(self, results):
        """Print backtest results"""
        if results is None:
            return
        
        print(f"\n{'='*100}")
        print(f"FULL SYSTEM BACKTEST RESULTS")
        print(f"{'='*100}")
        
        print(f"\n📊 Trading Statistics:")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Unique Symbols: {results['unique_symbols']}")
        print(f"   Wins: {results['wins']} ({results['win_rate']*100:.1f}%)")
        print(f"   Losses: {results['losses']}")
        print(f"   Avg Win: {results['avg_win']*100:+.2f}%")
        print(f"   Avg Loss: {results['avg_loss']*100:+.2f}%")
        print(f"   Profit Factor: {results['profit_factor']:.2f}")
        print(f"   Avg Days Held: {results['avg_days_held']:.1f}")
        
        print(f"\n💰 Performance:")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Final Capital: ${results['final_capital']:,.2f}")
        print(f"   Total Return: {results['total_return']*100:+.2f}%")
        
        print(f"\n📈 Risk Metrics:")
        print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {results['max_drawdown']*100:.2f}%")
        
        print(f"\n🎯 Exit Breakdown:")
        for reason, count in results['exit_reasons'].items():
            pct = (count / results['total_trades']) * 100
            print(f"   {reason}: {count} ({pct:.1f}%)")
        
        # Show best and worst trades
        trades_df = results['trades_df']
        
        print(f"\n🏆 Best Trades (Top 5):")
        best = trades_df.nlargest(5, 'pnl_pct')
        for _, trade in best.iterrows():
            print(f"   {trade['symbol']}: {trade['entry_date'].strftime('%Y-%m-%d')} → "
                  f"{trade['exit_date'].strftime('%Y-%m-%d')}, "
                  f"{trade['pnl_pct']*100:+.2f}% ({trade['exit_reason']})")
        
        print(f"\n❌ Worst Trades (Top 5):")
        worst = trades_df.nsmallest(5, 'pnl_pct')
        for _, trade in worst.iterrows():
            print(f"   {trade['symbol']}: {trade['entry_date'].strftime('%Y-%m-%d')} → "
                  f"{trade['exit_date'].strftime('%Y-%m-%d')}, "
                  f"{trade['pnl_pct']*100:+.2f}% ({trade['exit_reason']})")
        
        print(f"\n{'='*100}")


def main():
    """Run full system backtest"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Full System Backtest')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    parser.add_argument('--risk', type=float, default=0.02, help='Risk per trade')
    parser.add_argument('--positions', type=int, default=3, help='Max concurrent positions')
    parser.add_argument('--min-price', type=float, default=2.0, help='Min stock price')
    parser.add_argument('--max-price', type=float, default=20.0, help='Max stock price')
    parser.add_argument('--top-n', type=int, default=3, help='Top N momentum stocks')
    parser.add_argument('--days', type=int, default=90, help='Backtest period (days)')
    parser.add_argument('--min-ev', type=float, default=0.0003, help='Min EV threshold (e.g., 0.0003 = 0.03%)')
    parser.add_argument('--min-confidence', type=float, default=0.48, help='Min win probability (e.g., 0.48 = 48%)')
    
    args = parser.parse_args()
    
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    backtester = FullSystemBacktester(
        initial_capital=args.capital,
        risk_per_trade=args.risk,
        max_positions=args.positions,
        min_ev=args.min_ev,
        min_confidence=args.min_confidence
    )
    
    results = backtester.run_backtest(
        start_date=start_date,
        end_date=end_date,
        min_price=args.min_price,
        max_price=args.max_price,
        top_n=args.top_n
    )
    
    if results:
        backtester.print_results(results)


if __name__ == '__main__':
    main()

