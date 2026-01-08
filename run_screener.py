#!/usr/bin/env python3
"""
Quick launcher script for Stock Screener
Allows easy customization of screening parameters
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from stock_screener import StockScreener
import schwabdev

# Load environment variables
load_dotenv()


def main():
    """Interactive stock screener"""
    print("=" * 60)
    print("Stock Screener - Quick Launcher")
    print("=" * 60)
    
    # Check credentials
    app_key = os.getenv('app_key')
    app_secret = os.getenv('app_secret')
    
    if not app_key or not app_secret:
        print("\nERROR: Missing credentials in .env file")
        print("Please run: python3 setup_schwab.py")
        return
    
    # Initialize client
    print("\nInitializing Schwab API client...")
    try:
        client = schwabdev.Client(
            app_key,
            app_secret,
            os.getenv('callback_url', 'https://127.0.0.1')
        )
        print("✓ Client initialized")
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Initialize screener
    screener = StockScreener(client)
    
    # Get symbols from user or use default
    print("\n" + "=" * 60)
    print("Enter stock symbols (comma-separated) or press Enter for default:")
    print("Default: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM, V, JNJ")
    user_input = input("Symbols: ").strip()
    
    if user_input:
        symbols = [s.strip().upper() for s in user_input.split(',')]
    else:
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ']
    
    print(f"\nAnalyzing {len(symbols)} stocks: {', '.join(symbols)}")
    
    # Fetch data
    print("\n" + "=" * 60)
    print("Step 1: Fetching stock data...")
    screener.fetch_stocks(symbols, periodType='year', period=1, frequencyType='daily', frequency=1)
    
    # Calculate indicators
    print("\n" + "=" * 60)
    print("Step 2: Calculating indicators and alphas...")
    screener.calculate_indicators()
    
    # Get quotes
    print("\n" + "=" * 60)
    print("Step 3: Fetching current quotes...")
    screener.get_current_quotes(symbols)
    
    # Create summary
    print("\n" + "=" * 60)
    print("Step 4: Creating summary...")
    summary_df = screener.create_summary_dataframe(include_quotes=True)
    
    # Display options
    while True:
        print("\n" + "=" * 60)
        print("Options:")
        print("1. Display summary table (all stocks)")
        print("2. Sort and display by metric")
        print("3. Filter stocks by criteria")
        print("4. Plot chart for a specific stock")
        print("5. Plot charts for top N stocks")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            print("\n" + "=" * 60)
            screener.display_summary_table(summary_df)
        
        elif choice == '2':
            print("\nAvailable metrics to sort by:")
            numeric_cols = [col for col in summary_df.columns if col != 'Symbol']
            for i, col in enumerate(numeric_cols, 1):
                print(f"  {i}. {col}")
            
            metric_input = input("\nEnter metric name or number: ").strip()
            
            # Try to find by number or name
            if metric_input.isdigit():
                idx = int(metric_input) - 1
                if 0 <= idx < len(numeric_cols):
                    sort_by = numeric_cols[idx]
                else:
                    print("Invalid number")
                    continue
            else:
                sort_by = metric_input
            
            if sort_by not in summary_df.columns:
                print(f"Metric '{sort_by}' not found")
                continue
            
            ascending_input = input("Sort ascending? (y/n, default=n): ").strip().lower()
            ascending = ascending_input == 'y'
            
            top_n_input = input("Show top N stocks (Enter for all): ").strip()
            top_n = int(top_n_input) if top_n_input.isdigit() else None
            
            print("\n" + "=" * 60)
            screener.display_summary_table(summary_df, sort_by=sort_by, ascending=ascending, top_n=top_n)
        
        elif choice == '3':
            print("\nFilter options:")
            print("Format: column_name min_value max_value")
            print("Example: RSI 30 70")
            print("Example: MACD_Hist 0 (for > 0)")
            print("Press Enter to skip filter")
            
            filter_input = input("Enter filter: ").strip()
            if not filter_input:
                continue
            
            try:
                parts = filter_input.split()
                col = parts[0]
                min_val = float(parts[1]) if len(parts) > 1 and parts[1] != 'None' else None
                max_val = float(parts[2]) if len(parts) > 2 and parts[2] != 'None' else None
                
                filters = {col: (min_val, max_val)}
                filtered_df = screener.filter_stocks(summary_df, filters=filters)
                
                print(f"\nFound {len(filtered_df)} stocks matching criteria")
                if len(filtered_df) > 0:
                    screener.display_summary_table(filtered_df)
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '4':
            symbol = input("Enter stock symbol: ").strip().upper()
            if symbol in screener.stock_features:
                print(f"\nPlotting chart for {symbol}...")
                screener.plot_stock_chart(
                    symbol,
                    show_indicators=True,
                    indicators=['RSI', 'MACD', 'BB', 'Volume', 'Alphas']
                )
            else:
                print(f"No data available for {symbol}")
        
        elif choice == '5':
            top_n_input = input("Enter number of top stocks to plot (default=3): ").strip()
            top_n = int(top_n_input) if top_n_input.isdigit() else 3
            
            sort_by_input = input("Sort by metric (default=Alpha_Sharpe_20): ").strip()
            sort_by = sort_by_input if sort_by_input else 'Alpha_Sharpe_20'
            
            if sort_by not in summary_df.columns:
                print(f"Metric '{sort_by}' not found")
                continue
            
            top_stocks = screener.sort_stocks(summary_df, sort_by=sort_by, ascending=False, top_n=top_n)
            
            for symbol in top_stocks['Symbol'].head(top_n):
                print(f"\nPlotting chart for {symbol}...")
                screener.plot_stock_chart(
                    symbol,
                    show_indicators=True,
                    indicators=['RSI', 'MACD', 'BB', 'Volume', 'Alphas']
                )
        
        elif choice == '6':
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice")


if __name__ == '__main__':
    main()


