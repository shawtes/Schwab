# Quick Start Guide

Get your web trading platform running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Python 3.8+ with all dependencies from main project
- Schwab API credentials configured in `.env`

## Step 1: Install Dependencies

```bash
cd web-trading-app
npm run install:all
```

This installs:
- Root dependencies (concurrently)
- Server dependencies (Express, TypeScript, WebSocket)
- Client dependencies (React, Vite, TradingView Charts)

## Step 2: Verify Environment

Ensure `.env` file exists in project root with:
```
app_key=YOUR_KEY
app_secret=YOUR_SECRET
callback_url=https://127.0.0.1
```

## Step 3: Start Development Servers

```bash
npm run dev
```

This starts:
- **Backend**: http://localhost:3001
- **Frontend**: http://localhost:3000

## Step 4: Open Browser

Navigate to: **http://localhost:3000**

## Features Available

### 🏠 Dashboard
- View market overview
- Add symbols to watchlist
- Quick price quotes

### 🔍 Stock Screener
- Screen multiple stocks
- Filter by RSI, MACD, Volume
- Sort by any metric
- View trading signals

### 📈 Live Charts
- Professional candlestick charts
- Multiple timeframes
- Real-time updates
- Volume indicators

## Troubleshooting

### Port Already in Use (EADDRINUSE)

If you see `Error: listen EADDRINUSE: address already in use :::3001`:

**Option 1: Use the helper script**
```bash
npm run kill-ports
# Then start again
npm run dev
```

**Option 2: Use clean-start (kills ports and starts)**
```bash
npm run clean-start
```

**Option 3: Manual kill**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 3001
lsof -ti:3001 | xargs kill -9
```

### Python Scripts Not Working
```bash
# Make scripts executable
chmod +x *.py

# Test Python script directly
python3 fetch_stock_data.py AAPL year 1 daily 1
```

### Module Not Found Errors
```bash
# Reinstall dependencies
cd server && rm -rf node_modules && npm install
cd ../client && rm -rf node_modules && npm install
```

## Production Build

```bash
npm run build
npm start
```

## Next Steps

- Customize styling in `client/src/App.css`
- Add more indicators in Python scripts
- Extend API endpoints in `server/src/server.ts`
- Add authentication for production

