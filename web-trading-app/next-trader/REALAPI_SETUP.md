# 🔌 Real Schwab API Integration Guide

This guide shows how to connect the Next.js trading UI to your real Schwab API backend.

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js UI     │  Port 3000 (Frontend)
│  (next-trader)  │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Node.js Server │  Port 3001 (Backend)
│  (TypeScript)    │
└────────┬────────┘
         │
         │ PythonShell
         ▼
┌─────────────────┐
│  Python Scripts │  Schwab API Client
│  (schwabdev)    │
└─────────────────┘
```

## 🚀 Quick Start

### 1. Start Backend Server (Port 3001)

In **Terminal 1**:
```bash
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/server
npm install
npm run dev
```

You should see:
```
🚀 Server running on port 3001
✅ WebSocket server ready
```

### 2. Start Next.js Frontend (Port 3000)

In **Terminal 2**:
```bash
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/next-trader

# Make sure .env.local is configured for real API
# (already created with NEXT_PUBLIC_USE_REAL_API=true)

npm run dev
```

### 3. Open Browser

Navigate to: **http://localhost:3000**

The UI will now fetch **real market data** from Schwab API! 🎉

---

## ⚙️ Configuration

### Environment Variables (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:3001

# WebSocket URL
NEXT_PUBLIC_WS_URL=ws://localhost:3001

# Use real API (true) or mock data (false)
NEXT_PUBLIC_USE_REAL_API=true
```

### Switch Between Mock and Real Data

**Use Real API:**
```bash
# In .env.local
NEXT_PUBLIC_USE_REAL_API=true
```

**Use Mock Data (for testing):**
```bash
# In .env.local
NEXT_PUBLIC_USE_REAL_API=false
```

Then restart: `npm run dev`

---

## 📡 Available API Endpoints

### Backend Server (Port 3001)

✅ **Market Data:**
- `POST /api/price-history` - Get historical candles
- `POST /api/quotes` - Get real-time quotes
- `GET /api/health` - Health check

✅ **WebSocket:**
- `ws://localhost:3001` - Real-time streaming data

### What's Working:

✅ **Chart Data** - Historical price data from Schwab  
✅ **Watchlist** - Real-time quotes for multiple symbols  
✅ **Order Book** - Bid/ask prices (derived from quotes)  

### What Needs Implementation:

⚠️ **Orders** - Submit/cancel orders  
⚠️ **Positions** - Account positions  
⚠️ **Account** - Account balances  
⚠️ **Fills** - Trade history  
⚠️ **Trades Tape** - Recent executions  

---

## 🔧 Implementing Missing Features

### 1. Orders API

Update your backend server (`server/src/server.ts`):

```typescript
// Submit order to Schwab
app.post('/api/orders', async (req, res) => {
  const order = req.body;
  
  // Call Python script to submit order
  const scriptPath = path.join(PROJECT_ROOT, 'submit_order.py');
  const options = {
    mode: 'json' as const,
    pythonPath: PYTHON_PATH,
    args: [JSON.stringify(order)]
  };
  
  PythonShell.run(scriptPath, options, (err, results) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to submit order' });
    }
    res.json(results[0]);
  });
});
```

### 2. Positions API

```typescript
app.get('/api/positions', async (req, res) => {
  // Call Python script to get positions
  const scriptPath = path.join(PROJECT_ROOT, 'get_positions.py');
  // ... similar to above
});
```

### 3. Account API

```typescript
app.get('/api/account', async (req, res) => {
  // Call Python script to get account info
  const scriptPath = path.join(PROJECT_ROOT, 'get_account.py');
  // ... similar to above
});
```

---

## 🐍 Python Scripts Needed

Create these in `/web-trading-app/`:

### `submit_order.py`
```python
import sys
import json
from schwabdev import Client

# Initialize Schwab client
client = Client()

# Get order from args
order = json.loads(sys.argv[1])

# Submit order to Schwab
result = client.order_place(
    account_hash=client.account_hash,
    order=order
)

print(json.dumps(result))
```

### `get_positions.py`
```python
import sys
import json
from schwabdev import Client

client = Client()
positions = client.account_positions(account_hash=client.account_hash)
print(json.dumps(positions))
```

### `get_account.py`
```python
import sys
import json
from schwabdev import Client

client = Client()
account = client.account_details(account_hash=client.account_hash)
print(json.dumps(account))
```

---

## 🔐 Authentication

Make sure your Schwab API credentials are configured:

1. **Tokens location:** Check `schwabdev/tokens.py`
2. **Environment variables:** Set in `.env` if needed
3. **OAuth flow:** Ensure refresh tokens are valid

---

## 🧪 Testing

### Test Backend Alone:

```bash
# Test quotes endpoint
curl -X POST http://localhost:3001/api/quotes \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"]}'

# Test price history
curl -X POST http://localhost:3001/api/price-history \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "periodType": "day", "period": 1}'
```

### Test Frontend:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh page
4. Check requests to `localhost:3001`

---

## 📊 Data Flow

```
User clicks symbol in watchlist
         ↓
Next.js calls fetchWatchlist()
         ↓
api-real.ts makes request to localhost:3001/api/quotes
         ↓
Node.js server calls fetch_quotes.py
         ↓
Python script uses schwabdev client
         ↓
Schwab API returns quote data
         ↓
Data flows back up the chain
         ↓
React component displays data
```

---

## 🐛 Troubleshooting

### Backend not starting:
```bash
# Check if port 3001 is in use
lsof -ti:3001 | xargs kill -9

# Reinstall dependencies
cd server
rm -rf node_modules
npm install
```

### Python errors:
```bash
# Check Python path
which python3

# Activate venv if you have one
source ../venv/bin/activate

# Install schwabdev
pip install schwabdev
```

### Connection refused:
- Make sure backend is running on port 3001
- Check NEXT_PUBLIC_API_URL in .env.local
- Check CORS settings in server

### No data showing:
- Check browser console for errors
- Verify Schwab API credentials
- Test backend endpoints with curl

---

## 🎯 Current Status

✅ **Infrastructure ready** - Backend and frontend connected  
✅ **Market data working** - Charts and quotes from real API  
⚠️ **Trading features** - Need to implement order/account APIs  
⚠️ **WebSocket streaming** - Need to connect to Schwab streaming  

---

## 📝 Next Steps

1. ✅ Configure .env.local (DONE)
2. ✅ Create api-real.ts integration layer (DONE)
3. Start backend server on port 3001
4. Test market data endpoints
5. Implement order submission
6. Implement account/positions APIs
7. Add WebSocket streaming
8. Add error handling and retry logic

---

**You're now ready to use real Schwab market data in your trading UI!** 🚀

For questions or issues, check:
- Backend logs in Terminal 1
- Frontend logs in browser console
- Network tab in DevTools


