#!/usr/bin/env python3
"""
Schwab WebSocket Streaming Server
Streams real-time market data from Schwab API to connected clients
"""

import asyncio
import json
import os
import websockets
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

import schwabdev

# Connected WebSocket clients
connected_clients = set()

# Current subscriptions
current_symbols = set()

# Latest data cache
latest_quotes = {}

def handle_stream_data(data):
    """Process incoming data from Schwab stream"""
    try:
        message = json.loads(data)
        
        # Handle different message types
        if 'data' in message:
            for item in message['data']:
                service = item.get('service')
                
                if service == 'LEVELONE_EQUITIES':
                    # Real-time quote data - correct field mappings from translate.py
                    content = item.get('content', [])
                    for quote_data in content:
                        symbol = quote_data.get('key')
                        
                        # Build quote object with CORRECT field numbers (0-indexed)
                        # 0=Symbol, 1=Bid, 2=Ask, 3=Last, 4=BidSize, 5=AskSize, 8=Volume
                        # 18=NetChange, 43=NetPercentChange, 34=QuoteTimeInLong
                        quote = {
                            'type': 'quote',
                            'symbol': symbol,
                            'bid': quote_data.get('1'),   # Bid Price
                            'ask': quote_data.get('2'),   # Ask Price
                            'last': quote_data.get('3'),  # Last Price
                            'bidSize': quote_data.get('4'),
                            'askSize': quote_data.get('5'),
                            'volume': quote_data.get('8'),  # Total Volume
                            'lastSize': quote_data.get('9'),
                            'change': quote_data.get('18'),  # Net Change
                            'changePercent': quote_data.get('43'),  # Net Percent Change
                            'timestamp': quote_data.get('34')  # Quote Time in Long (milliseconds)
                        }
                        
                        # Remove None values
                        quote = {k: v for k, v in quote.items() if v is not None}
                        
                        # Cache latest quote
                        latest_quotes[symbol] = quote
                        
                        # Broadcast to all connected clients
                        asyncio.create_task(broadcast(json.dumps(quote)))
                
                elif service == 'CHART_EQUITY':
                    # Real-time candle data - correct field mappings
                    # 0=key, 1=Sequence, 2=Open, 3=High, 4=Low, 5=Close, 6=Volume, 7=ChartTime, 8=ChartDay
                    content = item.get('content', [])
                    for candle_data in content:
                        symbol = candle_data.get('key')
                        
                        candle = {
                            'type': 'candle',
                            'symbol': symbol,
                            'sequence': candle_data.get('1'),  # Sequence number
                            'open': candle_data.get('2'),      # Open Price
                            'high': candle_data.get('3'),      # High Price
                            'low': candle_data.get('4'),       # Low Price
                            'close': candle_data.get('5'),     # Close Price
                            'volume': candle_data.get('6'),    # Volume
                            'timestamp': candle_data.get('7'), # Chart Time (milliseconds)
                            'chartDay': candle_data.get('8')   # Chart Day
                        }
                        
                        candle = {k: v for k, v in candle.items() if v is not None}
                        
                        # Broadcast candle update
                        asyncio.create_task(broadcast(json.dumps(candle)))
        
    except Exception as e:
        print(f"Error processing stream data: {e}")

async def broadcast(message):
    """Broadcast message to all connected clients"""
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )

async def handle_client(websocket):
    """Handle incoming WebSocket connections from clients"""
    connected_clients.add(websocket)
    print(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        # Send cached quotes to new client
        for quote in latest_quotes.values():
            await websocket.send(json.dumps(quote))
        
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'subscribe':
                    # Subscribe to symbols
                    symbols = data.get('symbols', [])
                    await subscribe_symbols(symbols)
                    
                elif msg_type == 'unsubscribe':
                    # Unsubscribe from symbols
                    symbols = data.get('symbols', [])
                    await unsubscribe_symbols(symbols)
                    
            except json.JSONDecodeError:
                print(f"Invalid JSON from client: {message}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")

async def subscribe_symbols(symbols):
    """Subscribe to symbols in Schwab stream"""
    global current_symbols
    
    new_symbols = set(symbols) - current_symbols
    if new_symbols and schwab_stream:
        print(f"Subscribing to: {new_symbols}")
        
        # Subscribe to level one quotes with CORRECT field numbers
        # 0=Symbol, 1=Bid, 2=Ask, 3=Last, 4=BidSize, 5=AskSize, 8=Volume, 
        # 9=LastSize, 18=NetChange, 43=NetPercentChange, 34=QuoteTime
        request = schwab_stream.level_one_equities(
            keys=list(new_symbols),
            fields="0,1,2,3,4,5,8,9,10,11,17,18,34,35,43",  # All key fields
            command="SUBS"
        )
        schwab_stream.send(request)
        
        # Subscribe to chart data with CORRECT field numbers
        # 0=key, 1=Sequence, 2=Open, 3=High, 4=Low, 5=Close, 6=Volume, 7=ChartTime
        chart_request = schwab_stream.chart_equity(
            keys=list(new_symbols),
            fields="0,1,2,3,4,5,6,7,8",  # All candle fields
            command="SUBS"
        )
        schwab_stream.send(chart_request)
        
        current_symbols.update(new_symbols)

async def unsubscribe_symbols(symbols):
    """Unsubscribe from symbols"""
    global current_symbols
    
    to_remove = set(symbols) & current_symbols
    if to_remove and schwab_stream:
        print(f"Unsubscribing from: {to_remove}")
        
        request = schwab_stream.level_one_equities(
            keys=list(to_remove),
            command="UNSUBS"
        )
        schwab_stream.send(request)
        
        chart_request = schwab_stream.chart_equity(
            keys=list(to_remove),
            command="UNSUBS"
        )
        schwab_stream.send(chart_request)
        
        current_symbols -= to_remove

# Global Schwab stream object
schwab_stream = None

async def start_servers():
    """Start both Schwab stream and WebSocket server"""
    global schwab_stream
    
    print("Initializing Schwab client...")
    client = schwabdev.Client(
        os.getenv('app_key'),
        os.getenv('app_secret'),
        os.getenv('callback_url', 'https://127.0.0.1')
    )
    
    print("Starting Schwab stream...")
    schwab_stream = schwabdev.Stream(client)
    schwab_stream.start(receiver=handle_stream_data)
    
    # Wait for stream to be active
    await asyncio.sleep(2)
    
    if not schwab_stream.active:
        print("ERROR: Failed to start Schwab stream!")
        return
    
    print("✅ Schwab stream active")
    
    # Subscribe to default watchlist symbols
    default_symbols = ["AAPL", "MSFT", "SPY", "TSLA", "NVDA", "AMD"]
    await subscribe_symbols(default_symbols)
    
    # Start WebSocket server for clients
    print("Starting WebSocket server on ws://localhost:8765")
    async with websockets.serve(handle_client, "localhost", 8765):
        print("🚀 Schwab Streaming Server ready!")
        print("   Connect from frontend to: ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(start_servers())
    except KeyboardInterrupt:
        print("\nShutting down...")
        if schwab_stream:
            schwab_stream.stop()

