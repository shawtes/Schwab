"""
Backtesting System for EV-Based Trading Strategy

Tests the multi-timeframe EV classifier on historical data:
- Simulates BUY signals over time
- Applies TP/SL exit logic
- Tracks performance metrics
- Compares with buy-and-hold
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
from test_ev_classifier_system import test_multi_timeframe_ev_system

load_dotenv()
import schwabdev


class EVBacktester:
    """
    Backtest the EV classifier trading system
    """
    
    def __init__(self, initial_capital=10000, risk_per_trade=0.02, 
                 tp_multiplier=1.5, sl_multiplier=2.0):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            risk_per_trade: Risk per trade as fraction of capital (e.g., 0.02 = 2%)
            tp_multiplier: Take profit = expected_return × tp_multiplier
            sl_multiplier: Stop loss = ATR × sl_multiplier
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.tp_multiplier = tp_multiplier
        self.sl_multiplier = sl_multiplier
        
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
    def calculate_position_size(self, price, stop_loss, confidence):
        """
        Calculate position size based on risk and confidence
        
        Args:
            price: Entry price
            stop_loss: Stop loss price
            confidence: Signal confidence (0-1)
        
        Returns:
            shares: Number of shares to buy
        """
        # Risk amount
        risk_amount = self.capital * self.risk_per_trade
        
        # Adjust by confidence (higher confidence = larger position)
        confidence_factor = confidence  # 0.5 = half size, 1.0 = full size
        adjusted_risk = risk_amount * confidence_factor
        
        # Risk per share
        risk_per_share = abs(price - stop_loss)
        
        # Calculate shares
        if risk_per_share > 0:
            shares = int(adjusted_risk / risk_per_share)
        else:
            shares = 0
        
        # Ensure we can afford it
        max_shares = int(self.capital / price) if price > 0 else 0
        shares = min(shares, max_shares)
        
        return shares
    
    def backtest_symbol(self, symbol, start_date=None, end_date=None):
        """
        Backtest on a single symbol
        
        Args:
            symbol: Stock symbol
            start_date: Start date for backtest
            end_date: End date for backtest
        
        Returns:
            dict: Backtest results
        """
        print(f"\n{'='*100}")
        print(f"BACKTESTING {symbol}")
        print(f"{'='*100}")
        
        # Initialize Schwab client
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
        
        # Fetch historical data
        print(f"\n📊 Fetching historical data...")
        df = fetcher.get_price_history(
            symbol,
            periodType='year',
            period=20,  # Max available data
            frequencyType='daily',
            frequency=1
        )
        
        if df is None or len(df) < 252:  # Need at least 1 year
            print(f"❌ Insufficient data for {symbol}")
            return None
        
        print(f"✓ Loaded {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")
        
        # Filter by date range if specified
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        if len(df) < 100:
            print(f"❌ Insufficient data in date range")
            return None
        
        # Create features
        print(f"\n🔧 Creating features...")
        features_df = fetcher.create_features(df)
        
        if features_df is None or len(features_df) < 50:
            print(f"❌ Feature creation failed")
            return None
        
        print(f"✓ Created {features_df.shape[1]} features for {len(features_df)} samples")
        
        # Prepare for ML
        model = EnsembleTradingModel(task='regression', random_state=42)
        X = model.prepare_features(features_df)
        y = df['close'].pct_change().shift(-1).dropna()
        
        # Align
        common_idx = features_df.index.intersection(y.index)
        X = features_df.loc[common_idx]
        X = model.prepare_features(X)
        y = y.loc[common_idx]
        
        # Clean data
        X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        
        # Use first 60% for training, remaining 40% for backtest
        train_size = int(len(X) * 0.6)
        X_train = X[:train_size]
        y_train = y[:train_size]
        X_backtest = X[train_size:]
        y_backtest = y[train_size:]
        backtest_dates = y.index[train_size:]
        
        print(f"\n📈 Training Period: {len(X_train)} samples")
        print(f"📉 Backtest Period: {len(X_backtest)} samples ({backtest_dates[0].date()} to {backtest_dates[-1].date()})")
        
        # Train EV classifier
        print(f"\n🤖 Training EV Classifier...")
        from ml_trading.pipeline.multi_timeframe_system import EVClassifier
        
        ev_classifier = EVClassifier(
            min_ev=0.0005,
            min_confidence=0.52,
            use_timeframe_features=False  # Use base features only for speed
        )
        
        ev_classifier.fit(X_train, y_train)
        
        # Simulate trading on backtest period
        print(f"\n💰 Running Backtest...")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Risk per Trade: {self.risk_per_trade*100:.1f}%")
        
        # Get ATR for stop loss calculation
        atr = df['high'].sub(df['low']).rolling(14).mean()
        
        # Track open positions
        open_position = None
        
        for i, date in enumerate(backtest_dates):
            # Skip if we don't have enough future data
            if i >= len(backtest_dates) - 1:
                break
            
            current_price = df.loc[date, 'close']
            current_atr = atr.loc[date] if date in atr.index else current_price * 0.02
            
            # Check open position first
            if open_position is not None:
                # Check TP/SL
                high = df.loc[date, 'high']
                low = df.loc[date, 'low']
                
                # Check stop loss hit
                if low <= open_position['stop_loss']:
                    exit_price = open_position['stop_loss']
                    pnl = (exit_price - open_position['entry_price']) * open_position['shares']
                    pnl_pct = (exit_price / open_position['entry_price'] - 1)
                    
                    self.capital += pnl
                    
                    trade = {
                        'symbol': symbol,
                        'entry_date': open_position['entry_date'],
                        'exit_date': date,
                        'entry_price': open_position['entry_price'],
                        'exit_price': exit_price,
                        'shares': open_position['shares'],
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'exit_reason': 'SL',
                        'days_held': (date - open_position['entry_date']).days
                    }
                    self.trades.append(trade)
                    open_position = None
                    
                # Check take profit hit
                elif high >= open_position['take_profit']:
                    exit_price = open_position['take_profit']
                    pnl = (exit_price - open_position['entry_price']) * open_position['shares']
                    pnl_pct = (exit_price / open_position['entry_price'] - 1)
                    
                    self.capital += pnl
                    
                    trade = {
                        'symbol': symbol,
                        'entry_date': open_position['entry_date'],
                        'exit_date': date,
                        'entry_price': open_position['entry_price'],
                        'exit_price': exit_price,
                        'shares': open_position['shares'],
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'exit_reason': 'TP',
                        'days_held': (date - open_position['entry_date']).days
                    }
                    self.trades.append(trade)
                    open_position = None
            
            # Check for new entry signal
            if open_position is None:
                try:
                    signal, confidence, ev_metrics = ev_classifier.predict_signal(X_backtest[i])
                    
                    if signal == 'BUY' and ev_metrics['expected_value'] > 0:
                        # Calculate TP/SL
                        expected_return = ev_metrics['expected_return']
                        
                        # Take Profit: expected return × multiplier
                        tp_return = abs(expected_return) * self.tp_multiplier
                        take_profit = current_price * (1 + tp_return)
                        
                        # Stop Loss: ATR-based
                        stop_loss = current_price - (current_atr * self.sl_multiplier)
                        
                        # Calculate position size
                        shares = self.calculate_position_size(current_price, stop_loss, confidence)
                        
                        if shares > 0:
                            # Open position
                            cost = shares * current_price
                            self.capital -= cost
                            
                            open_position = {
                                'entry_date': date,
                                'entry_price': current_price,
                                'shares': shares,
                                'take_profit': take_profit,
                                'stop_loss': stop_loss,
                                'expected_return': expected_return,
                                'confidence': confidence,
                                'ev': ev_metrics['expected_value']
                            }
                
                except Exception as e:
                    # Skip this bar if error
                    continue
            
            # Track equity curve
            equity = self.capital
            if open_position is not None:
                equity += open_position['shares'] * current_price
            
            self.equity_curve.append({
                'date': date,
                'equity': equity,
                'capital': self.capital,
                'position_value': equity - self.capital
            })
        
        # Close any remaining position at end
        if open_position is not None:
            exit_price = df.loc[backtest_dates[-1], 'close']
            pnl = (exit_price - open_position['entry_price']) * open_position['shares']
            pnl_pct = (exit_price / open_position['entry_price'] - 1)
            
            self.capital += pnl + (open_position['shares'] * exit_price)
            
            trade = {
                'symbol': symbol,
                'entry_date': open_position['entry_date'],
                'exit_date': backtest_dates[-1],
                'entry_price': open_position['entry_price'],
                'exit_price': exit_price,
                'shares': open_position['shares'],
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': 'END',
                'days_held': (backtest_dates[-1] - open_position['entry_date']).days
            }
            self.trades.append(trade)
        
        # Calculate metrics
        results = self.calculate_metrics(symbol, df, backtest_dates)
        
        return results
    
    def calculate_metrics(self, symbol, price_df, backtest_dates):
        """
        Calculate backtest performance metrics
        """
        if len(self.trades) == 0:
            print(f"\n⚠️ No trades executed during backtest period")
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
        
        # Buy and hold comparison
        first_price = price_df.loc[backtest_dates[0], 'close']
        last_price = price_df.loc[backtest_dates[-1], 'close']
        bh_return = (last_price / first_price - 1)
        
        # Equity curve analysis
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe ratio (annualized)
        sharpe = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252) if equity_df['returns'].std() > 0 else 0
        
        # Max drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Profit factor
        gross_profit = wins['pnl'].sum() if len(wins) > 0 else 0
        gross_loss = abs(losses['pnl'].sum()) if len(losses) > 0 else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        results = {
            'symbol': symbol,
            'total_trades': len(trades_df),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_return': total_return,
            'bh_return': bh_return,
            'outperformance': total_return - bh_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'final_capital': self.capital,
            'trades_df': trades_df,
            'equity_df': equity_df
        }
        
        return results
    
    def print_results(self, results):
        """
        Print backtest results
        """
        if results is None:
            return
        
        print(f"\n{'='*100}")
        print(f"BACKTEST RESULTS - {results['symbol']}")
        print(f"{'='*100}")
        
        print(f"\n📊 Trading Statistics:")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Wins: {results['wins']} ({results['win_rate']*100:.1f}%)")
        print(f"   Losses: {results['losses']}")
        print(f"   Avg Win: {results['avg_win']*100:+.2f}%")
        print(f"   Avg Loss: {results['avg_loss']*100:+.2f}%")
        print(f"   Profit Factor: {results['profit_factor']:.2f}")
        
        print(f"\n💰 Performance:")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Final Capital: ${results['final_capital']:,.2f}")
        print(f"   Total Return: {results['total_return']*100:+.2f}%")
        print(f"   Buy & Hold Return: {results['bh_return']*100:+.2f}%")
        print(f"   Outperformance: {results['outperformance']*100:+.2f}%")
        
        print(f"\n📈 Risk Metrics:")
        print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {results['max_drawdown']*100:.2f}%")
        
        # Show recent trades
        print(f"\n📋 Recent Trades (Last 10):")
        trades_df = results['trades_df']
        print(f"\n{'Date':<12} {'Entry':<10} {'Exit':<10} {'P&L%':<10} {'Exit':<6} {'Days'}")
        print("-" * 70)
        
        for _, trade in trades_df.tail(10).iterrows():
            print(f"{trade['entry_date'].strftime('%Y-%m-%d'):<12} "
                  f"${trade['entry_price']:<9.2f} ${trade['exit_price']:<9.2f} "
                  f"{trade['pnl_pct']*100:>+8.2f}% {trade['exit_reason']:<6} {trade['days_held']}")
        
        print(f"\n{'='*100}")


def main():
    """
    Run backtest on specified symbols
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtest EV Trading System')
    parser.add_argument('symbols', nargs='+', help='Stock symbols to backtest')
    parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    parser.add_argument('--risk', type=float, default=0.02, help='Risk per trade (0.02 = 2%%)')
    parser.add_argument('--tp', type=float, default=1.5, help='Take profit multiplier')
    parser.add_argument('--sl', type=float, default=2.0, help='Stop loss multiplier (ATR)')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 100)
    print("EV TRADING SYSTEM - BACKTEST")
    print("=" * 100)
    
    print(f"\n⚙️ Configuration:")
    print(f"   Initial Capital: ${args.capital:,.2f}")
    print(f"   Risk per Trade: {args.risk*100:.1f}%")
    print(f"   Take Profit: {args.tp}x expected return")
    print(f"   Stop Loss: {args.sl}x ATR")
    
    all_results = []
    
    for symbol in args.symbols:
        backtester = EVBacktester(
            initial_capital=args.capital,
            risk_per_trade=args.risk,
            tp_multiplier=args.tp,
            sl_multiplier=args.sl
        )
        
        results = backtester.backtest_symbol(symbol)
        
        if results:
            backtester.print_results(results)
            all_results.append(results)
    
    # Summary across all symbols
    if len(all_results) > 1:
        print(f"\n{'='*100}")
        print("SUMMARY ACROSS ALL SYMBOLS")
        print(f"{'='*100}")
        
        print(f"\n{'Symbol':<8} {'Trades':<8} {'Win%':<8} {'Return':<10} {'B&H':<10} {'Sharpe':<8} {'MaxDD'}")
        print("-" * 100)
        
        for res in all_results:
            print(f"{res['symbol']:<8} {res['total_trades']:<8} "
                  f"{res['win_rate']*100:<7.1f}% {res['total_return']*100:>+8.2f}% "
                  f"{res['bh_return']*100:>+8.2f}% {res['sharpe_ratio']:>7.2f} "
                  f"{res['max_drawdown']*100:>7.2f}%")
    
    print(f"\n{'='*100}")
    print("✅ BACKTEST COMPLETE")
    print(f"{'='*100}")


if __name__ == '__main__':
    main()

