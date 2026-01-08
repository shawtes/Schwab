"""
Live Data Fetcher for Schwab API

This module provides functionality to fetch live/real-time quotes and data
for trading symbols using the Schwab API.
"""

import os
from dotenv import load_dotenv
import schwabdev

# Load environment variables
load_dotenv()


class LiveDataFetcher:
    """Fetches live/real-time data from Schwab API"""
    
    def __init__(self, client):
        """
        Initialize the live data fetcher
        
        Args:
            client: Schwab API client instance
        """
        self.client = client
    
    def get_quote(self, symbol):
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
        
        Returns:
            Dictionary with quote data including:
            - bidPrice, askPrice
            - lastPrice
            - totalVolume
            - tradeTime
            - quoteTime
            - highPrice, lowPrice
            - openPrice, closePrice
            - etc.
        """
        try:
            response = self.client.quotes(symbol)
            data = response.json()
            
            if not data:
                print(f"No quote data found for {symbol}")
                return None
            
            # Quotes API returns a dictionary keyed by symbol
            if symbol in data:
                return data[symbol]
            else:
                # If symbol not in response, try to get first entry
                if len(data) > 0:
                    return list(data.values())[0]
                return None
                
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_quotes(self, symbols):
        """
        Get real-time quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
                    or comma-separated string (e.g., 'AAPL,MSFT,GOOGL')
        
        Returns:
            Dictionary keyed by symbol with quote data
        """
        try:
            # Convert list to comma-separated string if needed
            if isinstance(symbols, list):
                symbol_str = ','.join(symbols)
            else:
                symbol_str = symbols
            
            response = self.client.quotes(symbol_str)
            data = response.json()
            
            return data if data else {}
            
        except Exception as e:
            print(f"Error fetching quotes: {e}")
            return {}
    
    def get_latest_price(self, symbol):
        """
        Get the latest (real-time) price for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
        
        Returns:
            Float: Latest price, or None if error
        """
        quote = self.get_quote(symbol)
        if quote:
            # Try different price fields (lastPrice, regularMarketLastPrice, etc.)
            price = quote.get('lastPrice') or \
                   quote.get('regularMarketLastPrice') or \
                   quote.get('askPrice') or \
                   quote.get('bidPrice')
            return float(price) if price is not None else None
        return None
    
    def get_latest_bid_ask(self, symbol):
        """
        Get the latest bid and ask prices for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
        
        Returns:
            Tuple: (bid_price, ask_price) or (None, None) if error
        """
        quote = self.get_quote(symbol)
        if quote:
            bid = quote.get('bidPrice')
            ask = quote.get('askPrice')
            bid_price = float(bid) if bid is not None else None
            ask_price = float(ask) if ask is not None else None
            return (bid_price, ask_price)
        return (None, None)
    
    def get_quote_summary(self, symbol):
        """
        Get a formatted summary of quote data
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
        
        Returns:
            String: Formatted summary of quote data
        """
        quote = self.get_quote(symbol)
        if not quote:
            return f"No quote data available for {symbol}"
        
        # Extract key fields
        last_price = quote.get('lastPrice') or quote.get('regularMarketLastPrice', 'N/A')
        bid_price = quote.get('bidPrice', 'N/A')
        ask_price = quote.get('askPrice', 'N/A')
        volume = quote.get('totalVolume') or quote.get('regularMarketVolume', 'N/A')
        high = quote.get('highPrice') or quote.get('regularMarketHighPrice', 'N/A')
        low = quote.get('lowPrice') or quote.get('regularMarketLowPrice', 'N/A')
        open_price = quote.get('openPrice') or quote.get('regularMarketOpenPrice', 'N/A')
        close_price = quote.get('closePrice') or quote.get('regularMarketClosePrice', 'N/A')
        
        summary = f"""
Quote Summary for {symbol}:
  Last Price: ${last_price}
  Bid: ${bid_price} | Ask: ${ask_price}
  Volume: {volume}
  High: ${high} | Low: ${low}
  Open: ${open_price} | Previous Close: ${close_price}
"""
        return summary


def main():
    """Example usage of LiveDataFetcher"""
    print("Live Data Fetcher Example")
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
    
    # Initialize live data fetcher
    print("\n2. Fetching live quotes...")
    fetcher = LiveDataFetcher(client)
    
    # Get quote for a single symbol
    symbol = 'AAPL'
    print(f"\nFetching live quote for {symbol}...")
    quote = fetcher.get_quote(symbol)
    
    if quote:
        print(f"   ✓ Quote received")
        print(f"\nQuote Summary:")
        print(fetcher.get_quote_summary(symbol))
    else:
        print(f"   ✗ Failed to get quote for {symbol}")
    
    # Get quotes for multiple symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"\nFetching live quotes for multiple symbols: {', '.join(symbols)}...")
    quotes = fetcher.get_quotes(symbols)
    
    if quotes:
        print(f"   ✓ Received quotes for {len(quotes)} symbol(s)")
        for sym, quote_data in quotes.items():
            price = fetcher.get_latest_price(sym)
            bid, ask = fetcher.get_latest_bid_ask(sym)
            print(f"   {sym}: ${price} (Bid: ${bid}, Ask: ${ask})")
    else:
        print(f"   ✗ Failed to get quotes")


if __name__ == "__main__":
    main()


