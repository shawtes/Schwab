# 🎯 Schwab Trading Platform - REAL API ONLY

This trading platform uses **ONLY real Schwab API data**. No mock data.

## 🚀 Quick Start (Easiest Way)

### One Command to Rule Them All:

```bash
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/next-trader
./START_REAL_API.sh
```

This will:
1. ✅ Kill any processes on ports 3000 and 3001
2. ✅ Start backend server (port 3001) with Schwab API
3. ✅ Start frontend (port 3000)
4. ✅ Open ready for trading with real data!

Press **Ctrl+C** to stop everything.

---

## 🔧 Manual Start (Two Terminals)

### Terminal 1: Backend Server (Port 3001)

```bash
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/server
npm run dev
```

**Wait for:** `✅ Server running on port 3001`

### Terminal 2: Frontend (Port 3000)

```bash
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/next-trader
npm run dev
```

**Open:** http://localhost:3000

---

## 📊 What Data is Real:

✅ **Chart Data** - Historical OHLCV from Schwab  
✅ **Watchlist Quotes** - Real-time prices, bid/ask  
✅ **Order Book** - Bid/ask spreads  

⚠️ **Not Yet Implemented** (will show empty):
- Order submission
- Positions
- Account balance  
- Trade fills

---

## 🔌 Architecture

```
Browser (Port 3000)
    ↓ HTTP/WebSocket
Node.js Backend (Port 3001)
    ↓ PythonShell
Python schwabdev Client
    ↓ HTTPS
Schwab API Servers
```

---

## ✅ Verify Real Data is Working

1. **Check Chart**: Should show real historical data for selected symbol
2. **Check Watchlist**: Prices should match current market prices
3. **Browser Console**: Should show API calls to `localhost:3001`
4. **Backend Terminal**: Should show requests being processed

---

## 🐛 Troubleshooting

### "Empty page" or "No data"

**Check backend is running:**
```bash
curl http://localhost:3001/api/health
```

Should return: `{"status":"ok"}`

**Check backend logs:**
```bash
tail -f /tmp/backend.log
```

### "Connection refused"

Make sure backend started successfully:
```bash
lsof -ti:3001
```

Should show a process ID. If not, backend isn't running.

### Backend won't start

Kill any process using port 3001:
```bash
lsof -ti:3001 | xargs kill -9
```

Then restart backend.

### Schwab API authentication errors

Check your Schwab credentials:
1. Verify tokens are not expired
2. Check `schwabdev/tokens.py`
3. Re-authenticate if needed

---

## 📝 Configuration

### Backend (.env in server/)

```bash
PORT=3001
```

### Frontend (.env.local in next-trader/)

```bash
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001
```

---

## 🎯 API Endpoints

### Backend Server (localhost:3001)

```bash
# Get real-time quotes
POST /api/quotes
Body: {"symbols": ["AAPL", "MSFT"]}

# Get price history
POST /api/price-history
Body: {
  "symbol": "AAPL",
  "periodType": "day",
  "period": 1,
  "frequencyType": "minute",
  "frequency": 5
}

# Health check
GET /api/health
```

---

## 🔥 Features Using Real Data

✅ **Live Chart**
- Real historical candles from Schwab
- Updates every 30 seconds
- 5-minute intervals

✅ **Watchlist**
- Real-time quotes
- Bid/Ask spreads
- Price changes

✅ **Order Book**
- Real bid/ask prices
- Spreads calculated from quotes

---

## 📚 Files Modified for Real API

- `src/lib/api.ts` - Now exports from api-real.ts
- `src/lib/api-real.ts` - Connects to backend server
- `src/lib/ws-client.ts` - Points to port 3001
- `.env.local` - Backend URL configuration

**Mock data files are still present but NOT USED.**

---

## ⚡ Performance Tips

1. **Backend caching**: Backend may cache some requests
2. **Rate limits**: Schwab API has rate limits, backend handles this
3. **Refresh intervals**: Chart updates every 30s to avoid limits

---

## 🎓 Next Steps

To implement remaining features:

1. **Order Submission** - Add order routes to backend
2. **Positions** - Connect to account positions API
3. **Account Info** - Fetch account balances
4. **WebSocket Streaming** - Real-time tick data

See `REALAPI_SETUP.md` for implementation guide.

---

**You are now running 100% REAL Schwab API data!** 🚀📈

No mock data. No simulation. Just real market data from Schwab.


