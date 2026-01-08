# Quick Start Guide

Get the trading platform running in 3 simple steps.

## Step 1: Install Dependencies

```bash
cd web-trading-app/next-trader
npm install
```

## Step 2: Start the WebSocket Server

In one terminal:

```bash
npm run mock:ws
```

You should see:
```
🚀 Mock WebSocket server running on ws://localhost:4001
```

## Step 3: Start the Next.js Dev Server

In another terminal:

```bash
npm run dev
```

Open your browser to [http://localhost:3000](http://localhost:3000)

## 🎉 You're Ready!

### First Actions

1. **Browse Symbols**: Click on any symbol in the left watchlist
2. **Place an Order**: 
   - Select symbol
   - Choose Buy/Sell
   - Set quantity
   - Click the green/red button
3. **Use Keyboard Shortcuts**:
   - Press `b` for quick buy
   - Press `s` for quick sell
   - Press `⌘K` (Mac) or `Ctrl+K` (Windows/Linux) for command palette
   - Press `/` to search symbols

### What You'll See

- **Top Bar**: Symbol selector, timeframe buttons, connection status
- **Left Panel**: Watchlist with real-time prices
- **Center**: 
  - Top: Candlestick chart
  - Bottom: Positions, Orders, Fills, Account tabs
- **Right Panel**:
  - Order book (bids and asks)
  - Recent trades tape
  - Order entry ticket

### Connection Status

Watch the badge in the top-right:
- 🟢 **Connected** - Real-time data flowing
- 🟡 **Connecting/Reconnecting** - Establishing connection
- 🔴 **Error/Disconnected** - Check if WebSocket server is running

## Troubleshooting

### "Cannot connect to WebSocket"

1. Ensure the mock server is running: `npm run mock:ws`
2. Check if port 4001 is available
3. Look for errors in the WebSocket server terminal

### "Chart not loading"

- Refresh the page
- Check the browser console for errors
- Ensure you're selecting a valid symbol from the watchlist

### Tests Not Running

```bash
# Install test dependencies if missing
npm install

# Run tests
npm test
```

## Next Steps

- Read the [full README](./README.md) for architecture details
- Explore the codebase structure
- Run tests with `npm test`
- Customize the UI in `app/globals.css`
- Integrate with real Schwab API (see parent repo docs)

## Environment Variables

Create `.env.local` to customize:

```bash
NEXT_PUBLIC_WS_URL=ws://localhost:4001
```

## Production Build

```bash
npm run build
npm start
```

The production server will run on [http://localhost:3000](http://localhost:3000)

---

**Happy Trading! 🚀📈**


