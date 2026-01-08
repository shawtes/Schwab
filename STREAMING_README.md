# 🚀 Schwab Real-Time Streaming Trading Platform

## What's New: WebSocket Streaming

Your trading platform now uses **Schwab's official WebSocket Streaming API** for true real-time data!

### ⚡ Benefits Over Polling:
- **Sub-second updates** - Data pushed instantly when available
- **Lower latency** - No 1-2 second delays
- **Real tick-by-tick data** - Just like Schwab's own platform
- **Efficient** - Single WebSocket vs constant HTTP polling
- **Auto-reconnection** - Handles disconnects gracefully

## 🏗️ Architecture

```
┌─────────────────────┐
│   Schwab API        │
│  (WebSocket Stream) │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ schwab_stream_      │
│    server.py        │ ← Receives real-time data
│  (Port 8765)        │   from Schwab, forwards
└──────────┬──────────┘   to connected clients
           │
           ↓
┌─────────────────────┐
│   Next.js Frontend  │
│   (Port 3000)       │ ← Displays live data
└─────────────────────┘
```

## 🚀 Quick Start

### 1. Start Everything:
```bash
./START_STREAMING.sh
```

This starts:
- Schwab WebSocket Streaming Server (port 8765)
- Next.js Frontend (port 3000)

### 2. Open Browser:
Navigate to: **http://localhost:3000**

## 📊 What You Get

### Real-Time Quote Updates:
- **Last Price** - Updates on every trade
- **Bid/Ask** - Live order book top-of-book
- **Volume** - Running total volume
- **Change %** - Real-time price changes

### Live Candle Data:
- **Chart updates** as candles form
- **High/Low tracking** in real-time
- **Volume accumulation** during candle period

## 🔧 Manual Start (Alternative)

### Terminal 1 - Start Streaming Server:
```bash
conda activate schwabdev
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app
python schwab_stream_server.py
```

### Terminal 2 - Start Frontend:
```bash
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/next-trader
npm run dev
```

## 📡 WebSocket API

### Connect:
```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### Subscribe to Symbols:
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  symbols: ['AAPL', 'MSFT', 'NVDA']
}));
```

### Receive Real-Time Data:
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'quote') {
    // Real-time quote update
    console.log(data.symbol, data.last, data.bid, data.ask);
  }
  
  if (data.type === 'candle') {
    // Real-time candle update
    console.log(data.symbol, data.open, data.high, data.low, data.close);
  }
};
```

## 🎯 Features

### ✅ Implemented:
- Real-time stock quotes (LEVELONE_EQUITIES)
- Live candle updates (CHART_EQUITY)
- Auto-reconnection on disconnect
- Subscription management
- Client broadcast system

### 🔄 Coming Soon:
- Order book depth (NASDAQ_BOOK, NYSE_BOOK)
- Time & Sales / Trade tape
- Account activity updates
- Order status updates

## 🐛 Troubleshooting

### Streaming Server Won't Start:
```bash
# Check if port 8765 is in use
lsof -ti:8765 | xargs kill -9

# Reinstall dependencies
pip install websockets python-dotenv schwabdev
```

### Frontend Won't Connect:
1. Check streaming server is running: `http://localhost:8765`
2. Check browser console for WebSocket errors
3. Verify `.env` has correct Schwab credentials

### No Data Showing:
1. Check you're authenticated with Schwab (tokens.db exists)
2. Check streaming server logs for errors
3. Verify market is open or use paper trading mode

## 📚 Schwab Stream API

Fields available in `LEVELONE_EQUITIES`:
- `1` - Last Price
- `2` - Bid Price
- `3` - Ask Price  
- `4` - Bid Size
- `5` - Ask Size
- `8` - Total Volume
- `9` - Last Size
- `29` - Net Change
- `30` - Percent Change
- `50` - Quote Time

See `schwabdev/translate.py` for full field mappings.

## 🎉 Enjoy Real-Time Trading!

Your platform now has professional-grade real-time data streaming just like Schwab's own interface!


