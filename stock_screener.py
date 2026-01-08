"""
Stock Screener with Indicators and Alphas
Fetches, displays, and sorts stocks based on technical indicators and alpha factors
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import seaborn as sns
warnings.filterwarnings('ignore')

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import schwabdev
from ensemble_trading_model import SchwabDataFetcher

# Load environment variables
load_dotenv()

# Set style for better-looking charts
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except OSError:
    try:
        plt.style.use('seaborn-darkgrid')
    except OSError:
        plt.style.use('ggplot')
sns.set_palette("husl")


class StockScreener:
    """
    Stock Screener that fetches, analyzes, and displays stocks with indicators and alphas
    """
    
    def __init__(self, client):
        """
        Initialize the stock screener
        
        Args:
            client: Schwab API client instance
        """
        self.client = client
        self.fetcher = SchwabDataFetcher(client)
        self.stock_data = {}  # Store raw data for each symbol
        self.stock_features = {}  # Store features/indicators for each symbol
        self.stock_quotes = {}  # Store current quotes for each symbol
        
    def fetch_stocks(self, symbols, periodType='year', period=1, frequencyType='daily', frequency=1):
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
            periodType: Period type ('day', 'month', 'year', 'ytd')
            period: Period (int)
            frequencyType: Frequency type ('minute', 'daily', 'weekly', 'monthly')
            frequency: Frequency (int)
        
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        print(f"\n{'='*60}")
        print(f"Fetching data for {len(symbols)} stocks...")
        print(f"{'='*60}")
        
        results = {}
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] Fetching {symbol}...")
            try:
                df = self.fetcher.get_price_history(
                    symbol,
                    periodType=periodType,
                    period=period,
                    frequencyType=frequencyType,
                    frequency=frequency
                )
                
                if df is not None and len(df) > 0:
                    results[symbol] = df
                    self.stock_data[symbol] = df
                    print(f"  ✓ Successfully fetched {len(df)} data points")
                    print(f"  Date range: {df.index.min()} to {df.index.max()}")
                else:
                    print(f"  ✗ No data available for {symbol}")
            except Exception as e:
                print(f"  ✗ Error fetching {symbol}: {e}")
        
        print(f"\n{'='*60}")
        print(f"Successfully fetched {len(results)}/{len(symbols)} stocks")
        print(f"{'='*60}\n")
        
        return results
    
    def calculate_indicators(self, symbols=None):
        """
        Calculate indicators and alphas for stocks
        
        Args:
            symbols: List of symbols to process (None = process all fetched stocks)
        
        Returns:
            Dictionary with symbol as key and features DataFrame as value
        """
        if symbols is None:
            symbols = list(self.stock_data.keys())
        
        if not symbols:
            print("No stock data available. Fetch stocks first.")
            return {}
        
        print(f"\n{'='*60}")
        print(f"Calculating indicators and alphas for {len(symbols)} stocks...")
        print(f"{'='*60}")
        
        results = {}
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
            if symbol not in self.stock_data:
                print(f"  ✗ No data available for {symbol}")
                continue
            
            try:
                features_df = self.fetcher.create_features(self.stock_data[symbol])
                if features_df is not None and len(features_df) > 0:
                    results[symbol] = features_df
                    self.stock_features[symbol] = features_df
                    print(f"  ✓ Calculated {len(features_df.columns)} features")
                    print(f"  Data points: {len(features_df)}")
                else:
                    print(f"  ✗ Failed to calculate features for {symbol}")
            except Exception as e:
                print(f"  ✗ Error processing {symbol}: {e}")
        
        print(f"\n{'='*60}")
        print(f"Successfully processed {len(results)}/{len(symbols)} stocks")
        print(f"{'='*60}\n")
        
        return results
    
    def get_current_quotes(self, symbols):
        """
        Get current quotes for symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary with symbol as key and quote data as value
        """
        print(f"\nFetching current quotes for {len(symbols)} stocks...")
        quotes = {}
        
        for symbol in symbols:
            try:
                quote = self.fetcher.get_quote(symbol)
                if quote:
                    quotes[symbol] = quote
                    self.stock_quotes[symbol] = quote
            except Exception as e:
                print(f"  ✗ Error fetching quote for {symbol}: {e}")
        
        return quotes
    
    def create_summary_dataframe(self, symbols=None, include_quotes=True):
        """
        Create a summary DataFrame with key metrics for all stocks
        
        Args:
            symbols: List of symbols to include (None = all fetched)
            include_quotes: Whether to include current quote data
        
        Returns:
            DataFrame with summary metrics
        """
        if symbols is None:
            symbols = list(self.stock_features.keys())
        
        if not symbols:
            print("No stock features available. Calculate indicators first.")
            return pd.DataFrame()
        
        summary_data = []
        
        for symbol in symbols:
            if symbol not in self.stock_features:
                continue
            
            features_df = self.stock_features[symbol]
            if len(features_df) == 0:
                continue
            
            # Get latest values
            latest = features_df.iloc[-1]
            
            # Extract key metrics
            metrics = {
                'Symbol': symbol,
                'Current_Price': latest.get('close', np.nan),
                'RSI': latest.get('rsi', np.nan),
                'MACD': latest.get('macd', np.nan),
                'MACD_Signal': latest.get('macd_signal', np.nan),
                'MACD_Hist': latest.get('macd_hist', np.nan),
                'BB_Position': latest.get('bb_position_20', np.nan),
                'Volume_Ratio': latest.get('volume_ratio_20', np.nan),
                'Momentum_20': latest.get('momentum_20_pct', np.nan),
                'Volatility_20': latest.get('volatility_20', np.nan),
                'ATR_Ratio': latest.get('atr_ratio', np.nan),
                'Alpha_TS_Rank_Close_20': latest.get('alpha_ts_rank_close_20', np.nan),
                'Alpha_ZScore_20': latest.get('alpha_zscore_20', np.nan),
                'Alpha_Sharpe_20': latest.get('alpha_sharpe_20', np.nan),
                'Returns_1d': latest.get('return_1d', np.nan),
                'Returns_5d': latest.get('return_5d', np.nan),
                'Returns_21d': latest.get('return_21d', np.nan),
            }
            
            # Add quote data if available
            if include_quotes and symbol in self.stock_quotes:
                quote = self.stock_quotes[symbol]
                if isinstance(quote, dict):
                    # Extract relevant quote fields
                    metrics['Quote_LastPrice'] = quote.get('lastPrice', np.nan)
                    metrics['Quote_NetChange'] = quote.get('netChange', np.nan)
                    metrics['Quote_PercentChange'] = quote.get('netPercentChangeInDouble', np.nan)
            
            summary_data.append(metrics)
        
        df = pd.DataFrame(summary_data)
        return df
    
    def sort_stocks(self, df, sort_by='Alpha_Sharpe_20', ascending=False, top_n=None):
        """
        Sort stocks by a specific metric
        
        Args:
            df: Summary DataFrame
            sort_by: Column name to sort by
            ascending: Sort order
            top_n: Return only top N stocks (None = all)
        
        Returns:
            Sorted DataFrame
        """
        if sort_by not in df.columns:
            print(f"Warning: Column '{sort_by}' not found. Available columns: {list(df.columns)}")
            return df
        
        sorted_df = df.sort_values(by=sort_by, ascending=ascending, na_position='last')
        
        if top_n:
            sorted_df = sorted_df.head(top_n)
        
        return sorted_df
    
    def filter_stocks(self, df, filters=None):
        """
        Filter stocks based on criteria
        
        Args:
            df: Summary DataFrame
            filters: Dictionary of {column: (min_value, max_value)} or {column: condition}
                    Examples:
                    - {'RSI': (30, 70)}  # RSI between 30 and 70
                    - {'MACD_Hist': (0, None)}  # MACD_Hist > 0
                    - {'Volume_Ratio': (1.0, None)}  # Volume_Ratio > 1.0
        
        Returns:
            Filtered DataFrame
        """
        if filters is None:
            return df
        
        filtered_df = df.copy()
        
        for column, condition in filters.items():
            if column not in filtered_df.columns:
                print(f"Warning: Column '{column}' not found. Skipping filter.")
                continue
            
            if isinstance(condition, tuple):
                min_val, max_val = condition
                if min_val is not None:
                    filtered_df = filtered_df[filtered_df[column] >= min_val]
                if max_val is not None:
                    filtered_df = filtered_df[filtered_df[column] <= max_val]
            elif callable(condition):
                filtered_df = filtered_df[condition(filtered_df[column])]
            else:
                # Single value comparison
                filtered_df = filtered_df[filtered_df[column] == condition]
        
        return filtered_df
    
    def plot_stock_chart(self, symbol, figsize=(16, 12), show_indicators=True, 
                        indicators=['RSI', 'MACD', 'BB', 'Volume'], save_path=None):
        """
        Plot comprehensive stock chart with indicators and alphas
        
        Args:
            symbol: Stock symbol
            figsize: Figure size tuple
            show_indicators: Whether to show indicator subplots
            indicators: List of indicators to show ['RSI', 'MACD', 'BB', 'Volume', 'Alphas']
            save_path: Path to save figure (None = don't save)
        """
        if symbol not in self.stock_features:
            print(f"No data available for {symbol}")
            return
        
        features_df = self.stock_features[symbol]
        if len(features_df) == 0:
            print(f"No features available for {symbol}")
            return
        
        # Determine number of subplots
        n_plots = 1  # Price chart
        if 'RSI' in indicators:
            n_plots += 1
        if 'MACD' in indicators:
            n_plots += 1
        if 'BB' in indicators:
            n_plots += 1
        if 'Volume' in indicators:
            n_plots += 1
        if 'Alphas' in indicators:
            n_plots += 1
        
        # Create figure with subplots
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(n_plots, 1, figure=fig, hspace=0.3)
        
        plot_idx = 0
        
        # 1. Price Chart with Moving Averages
        ax1 = fig.add_subplot(gs[plot_idx, 0])
        plot_idx += 1
        
        # Plot price
        ax1.plot(features_df.index, features_df['close'], label='Close', linewidth=2, color='#1f77b4')
        ax1.fill_between(features_df.index, features_df['low'], features_df['high'], 
                         alpha=0.2, color='gray', label='High-Low Range')
        
        # Plot moving averages
        if 'ma_20' in features_df.columns:
            ax1.plot(features_df.index, features_df['ma_20'], label='MA 20', linewidth=1.5, alpha=0.7)
        if 'ma_50' in features_df.columns:
            ax1.plot(features_df.index, features_df['ma_50'], label='MA 50', linewidth=1.5, alpha=0.7)
        if 'ema_12' in features_df.columns:
            ax1.plot(features_df.index, features_df['ema_12'], label='EMA 12', linewidth=1.5, alpha=0.7, linestyle='--')
        if 'ema_26' in features_df.columns:
            ax1.plot(features_df.index, features_df['ema_26'], label='EMA 26', linewidth=1.5, alpha=0.7, linestyle='--')
        
        # Plot Bollinger Bands if requested
        if 'BB' in indicators and 'bb_upper_20' in features_df.columns:
            ax1.plot(features_df.index, features_df['bb_upper_20'], label='BB Upper', 
                    linewidth=1, alpha=0.5, color='red', linestyle=':')
            ax1.plot(features_df.index, features_df['bb_lower_20'], label='BB Lower', 
                    linewidth=1, alpha=0.5, color='red', linestyle=':')
            ax1.fill_between(features_df.index, features_df['bb_upper_20'], features_df['bb_lower_20'], 
                           alpha=0.1, color='red')
        
        ax1.set_title(f'{symbol} - Price Chart with Indicators', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 2. RSI
        if 'RSI' in indicators and 'rsi' in features_df.columns:
            ax2 = fig.add_subplot(gs[plot_idx, 0])
            plot_idx += 1
            ax2.plot(features_df.index, features_df['rsi'], label='RSI', linewidth=2, color='purple')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought (70)')
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold (30)')
            ax2.fill_between(features_df.index, 30, 70, alpha=0.1, color='gray')
            ax2.set_ylabel('RSI', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.legend(loc='best', fontsize=9)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 3. MACD
        if 'MACD' in indicators and 'macd' in features_df.columns:
            ax3 = fig.add_subplot(gs[plot_idx, 0])
            plot_idx += 1
            ax3.plot(features_df.index, features_df['macd'], label='MACD', linewidth=2, color='blue')
            if 'macd_signal' in features_df.columns:
                ax3.plot(features_df.index, features_df['macd_signal'], label='Signal', 
                        linewidth=1.5, color='orange')
            if 'macd_hist' in features_df.columns:
                colors = ['green' if x >= 0 else 'red' for x in features_df['macd_hist']]
                ax3.bar(features_df.index, features_df['macd_hist'], label='Histogram', 
                       alpha=0.6, color=colors, width=0.8)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax3.set_ylabel('MACD', fontsize=12)
            ax3.legend(loc='best', fontsize=9)
            ax3.grid(True, alpha=0.3)
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 4. Volume
        if 'Volume' in indicators and 'volume' in features_df.columns:
            ax4 = fig.add_subplot(gs[plot_idx, 0])
            plot_idx += 1
            colors = ['green' if features_df['close'].iloc[i] >= features_df['close'].iloc[i-1] 
                     else 'red' for i in range(len(features_df))]
            ax4.bar(features_df.index, features_df['volume'], alpha=0.6, color=colors)
            if 'volume_ma_20' in features_df.columns:
                ax4.plot(features_df.index, features_df['volume_ma_20'], 
                       label='Volume MA 20', linewidth=1.5, color='blue')
            ax4.set_ylabel('Volume', fontsize=12)
            ax4.legend(loc='best', fontsize=9)
            ax4.grid(True, alpha=0.3)
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 5. Alpha Factors
        if 'Alphas' in indicators:
            ax5 = fig.add_subplot(gs[plot_idx, 0])
            plot_idx += 1
            
            alpha_cols = [col for col in features_df.columns if col.startswith('alpha_')]
            if alpha_cols:
                # Plot a few key alpha factors
                key_alphas = ['alpha_ts_rank_close_20', 'alpha_zscore_20', 'alpha_sharpe_20']
                for alpha_col in key_alphas:
                    if alpha_col in features_df.columns:
                        ax5.plot(features_df.index, features_df[alpha_col], 
                               label=alpha_col.replace('alpha_', '').replace('_', ' ').title(), 
                               linewidth=1.5, alpha=0.7)
                
                ax5.set_ylabel('Alpha Factors', fontsize=12)
                ax5.legend(loc='best', fontsize=9)
                ax5.grid(True, alpha=0.3)
                ax5.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        
        plt.show()
    
    def display_summary_table(self, df, sort_by=None, ascending=False, top_n=20):
        """
        Display summary table of stocks
        
        Args:
            df: Summary DataFrame
            sort_by: Column to sort by (None = no sorting)
            ascending: Sort order
            top_n: Show only top N stocks
        """
        if df.empty:
            print("No data to display")
            return
        
        display_df = df.copy()
        
        if sort_by:
            display_df = self.sort_stocks(display_df, sort_by=sort_by, ascending=ascending, top_n=top_n)
        elif top_n:
            display_df = display_df.head(top_n)
        
        # Format numeric columns for better display
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if 'Price' in col or 'Quote' in col:
                display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            elif 'Ratio' in col or 'Position' in col or 'Rank' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "N/A")
            elif 'Percent' in col or 'Change' in col or 'Returns' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        
        print(f"\n{'='*120}")
        print(f"Stock Summary Table ({len(display_df)} stocks)")
        if sort_by:
            print(f"Sorted by: {sort_by} ({'Ascending' if ascending else 'Descending'})")
        print(f"{'='*120}")
        print(display_df.to_string(index=False))
        print(f"{'='*120}\n")
        
        return display_df


def main():
    """Example usage of Stock Screener"""
    print("Stock Screener with Indicators and Alphas")
    print("=" * 60)
    
    # Check if credentials are loaded
    app_key = os.getenv('app_key')
    app_secret = os.getenv('app_secret')
    
    if not app_key or not app_secret:
        print("\nERROR: Missing credentials in .env file")
        print("Please make sure you have:")
        print("  - app_key=YOUR_KEY")
        print("  - app_secret=YOUR_SECRET")
        print("  - callback_url=https://127.0.0.1")
        print("\nRun: python3 setup_schwab.py")
        return
    
    # Initialize Schwab client
    print("\n1. Initializing Schwab API client...")
    try:
        client = schwabdev.Client(
            app_key,
            app_secret,
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        print("   ✓ Client initialized successfully")
    except Exception as e:
        print(f"   ✗ Error initializing client: {e}")
        return
    
    # Initialize screener
    print("\n2. Initializing Stock Screener...")
    screener = StockScreener(client)
    
    # Define stocks to analyze
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ']
    
    # Fetch stock data
    print("\n3. Fetching stock data...")
    screener.fetch_stocks(symbols, periodType='year', period=1, frequencyType='daily', frequency=1)
    
    # Calculate indicators and alphas
    print("\n4. Calculating indicators and alphas...")
    screener.calculate_indicators()
    
    # Get current quotes
    print("\n5. Fetching current quotes...")
    screener.get_current_quotes(symbols)
    
    # Create summary DataFrame
    print("\n6. Creating summary...")
    summary_df = screener.create_summary_dataframe(include_quotes=True)
    
    # Display summary table sorted by Alpha Sharpe
    print("\n7. Displaying summary table (sorted by Alpha Sharpe)...")
    screener.display_summary_table(summary_df, sort_by='Alpha_Sharpe_20', ascending=False, top_n=10)
    
    # Filter stocks (example: RSI between 30-70, positive MACD histogram)
    print("\n8. Filtering stocks (RSI 30-70, Positive MACD Histogram)...")
    filtered_df = screener.filter_stocks(summary_df, filters={
        'RSI': (30, 70),
        'MACD_Hist': (0, None)  # Positive MACD histogram
    })
    print(f"   Found {len(filtered_df)} stocks matching criteria")
    if len(filtered_df) > 0:
        screener.display_summary_table(filtered_df, sort_by='Alpha_Sharpe_20', ascending=False)
    
    # Plot charts for top 3 stocks
    print("\n9. Plotting charts for top 3 stocks...")
    top_stocks = screener.sort_stocks(summary_df, sort_by='Alpha_Sharpe_20', ascending=False, top_n=3)
    
    for symbol in top_stocks['Symbol'].head(3):
        print(f"\n   Plotting chart for {symbol}...")
        screener.plot_stock_chart(
            symbol,
            show_indicators=True,
            indicators=['RSI', 'MACD', 'BB', 'Volume', 'Alphas'],
            save_path=f"{symbol}_chart.png"
        )
    
    print("\n" + "=" * 60)
    print("Stock screening complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()

