# Institutional Trading Platform - Web Application

Professional-grade web-based trading platform built with React, Node.js, and TypeScript.

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** - Fast build tool
- **TradingView Lightweight Charts** - Professional charting library
- **React Query** - Data fetching and caching
- **React Router** - Navigation
- **Zustand** - State management

### Backend
- **Node.js** with Express
- **TypeScript** - Type safety
- **WebSocket (ws)** - Real-time data streaming
- **Python Integration** - Calls existing Python trading modules

## Project Structure

```
web-trading-app/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.tsx        # Main app component
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── server/                 # Node.js backend
│   ├── src/
│   │   └── server.ts      # Express server
│   ├── package.json
│   └── tsconfig.json
│
├── fetch_stock_data.py     # Python script for data fetching
├── fetch_quotes.py          # Python script for quotes
├── screen_stocks.py         # Python script for screening
└── package.json            # Root package.json
```

## Installation

### 1. Install All Dependencies

```bash
cd web-trading-app
npm run install:all
```

This installs dependencies for:
- Root project
- Server (Node.js)
- Client (React)

### 2. Configure Environment

Create `.env` file in project root (same as desktop app):
```
app_key=YOUR_KEY
app_secret=YOUR_SECRET
callback_url=https://127.0.0.1
```

## Running the Application

### Development Mode (Both Frontend & Backend)

```bash
npm run dev
```

This starts:
- Backend server on `http://localhost:3001`
- Frontend dev server on `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
```

## Features

### 🎯 Dashboard
- Market overview
- Watchlist management
- Quick stock quotes
- Navigation to charts

### 📊 Stock Screener
- Multi-stock analysis
- Advanced filtering (RSI, MACD, Volume)
- Sorting by any metric
- Trading signals (BUY/SELL/HOLD)

### 📈 Live Charts
- Professional candlestick charts
- Multiple timeframes (1min to 1day)
- Real-time price updates via WebSocket
- Volume indicators
- Zoom and pan support

## API Endpoints

### REST API

- `POST /api/price-history` - Get historical price data
- `POST /api/quotes` - Get current quotes
- `POST /api/indicators` - Calculate indicators
- `POST /api/screen` - Screen stocks with filters
- `GET /api/health` - Health check

### WebSocket

- Connect to `ws://localhost:3001`
- Subscribe: `{ type: 'subscribe', symbols: ['AAPL', 'MSFT'] }`
- Receive: `{ type: 'price', symbol: 'AAPL', price: 150.25 }`

## Architecture

### Data Flow

```
React Frontend → Express API → Python Scripts → Schwab API
                      ↓
                 WebSocket Server → Real-time Updates → Frontend
```

### Python Integration

The Node.js backend calls Python scripts using `python-shell`:
- Maintains existing Python trading logic
- Reuses all indicators and alpha factors
- No need to rewrite in JavaScript

## Development

### Server Development

```bash
cd server
npm run dev
```

### Client Development

```bash
cd client
npm run dev
```

### Type Checking

```bash
cd server && npm run type-check
cd client && npm run type-check
```

## Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables

Set in production:
- `PORT` - Server port (default: 3001)
- `NODE_ENV=production`

### Serve Static Files

The built React app can be served by Express or a CDN.

## Features Comparison

| Feature | Desktop GUI | Web App |
|---------|------------|---------|
| Stock Screening | ✅ | ✅ |
| Live Charts | ✅ | ✅ |
| Real-time Data | ✅ | ✅ |
| Multiple Timeframes | ✅ | ✅ |
| Indicators | ✅ | ✅ |
| Trading Signals | ✅ | ✅ |
| Cross-platform | ❌ | ✅ |
| Mobile-friendly | ❌ | ✅ |
| Cloud deployment | ❌ | ✅ |

## Troubleshooting

### Python Scripts Not Found
- Ensure Python scripts are executable: `chmod +x *.py`
- Check Python path in server code

### WebSocket Connection Failed
- Verify server is running on port 3001
- Check firewall settings
- Ensure WebSocket server is initialized

### CORS Errors
- Backend CORS is configured for localhost:3000
- Adjust in `server/src/server.ts` if needed

## Next Steps

- [ ] Add authentication
- [ ] Portfolio management
- [ ] Order placement
- [ ] Alerts and notifications
- [ ] Historical backtesting
- [ ] Multi-user support
- [ ] Advanced charting tools

## License

Proprietary - Institutional Trading Platform


