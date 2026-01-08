# Schwab Pro Trading Platform

A professional-grade trading web application built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui. Inspired by TradingView and Coinbase Advanced, this platform provides real-time market data, order management, and comprehensive trading tools.

## 🎯 Features

- **Real-time Market Data**: Live quotes, order book, and trade tape via WebSocket
- **Interactive Charting**: Candlestick charts with lightweight-charts library
- **Order Management**: Market and limit orders with real-time validation
- **Portfolio Tracking**: Live positions, P&L, and account summary
- **Command Palette**: Keyboard-first navigation (⌘K)
- **Responsive Layout**: Professional trading desk layout with watchlist, chart, order book, and order ticket
- **State Management**: Zustand for UI state, TanStack Query for server state
- **Error Handling**: Comprehensive loading, error, and reconnection states
- **Keyboard Shortcuts**: 
  - `/` - Focus symbol search
  - `b` - Quick buy
  - `s` - Quick sell
  - `Esc` - Close modals
  - `⌘K` / `Ctrl+K` - Command palette

## 📁 Project Structure

```
next-trader/
├── app/                          # Next.js app directory
│   ├── api/                      # API routes (REST endpoints)
│   │   ├── account/             # Account summary endpoint
│   │   ├── fills/               # Trade fills endpoint
│   │   ├── history/             # Historical candles endpoint
│   │   ├── orderbook/           # Order book snapshot endpoint
│   │   ├── orders/              # Orders CRUD endpoint
│   │   ├── positions/           # Positions endpoint
│   │   ├── trades/              # Recent trades endpoint
│   │   └── watchlist/           # Watchlist quotes endpoint
│   ├── globals.css              # Global styles and CSS variables
│   ├── layout.tsx               # Root layout with providers
│   └── page.tsx                 # Main trading page
│
├── src/
│   ├── app/
│   │   └── providers.tsx        # TanStack Query provider setup
│   │
│   ├── components/              # React components
│   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── badge.tsx
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── command.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   └── tabs.tsx
│   │   │
│   │   ├── Chart.tsx            # Candlestick chart component
│   │   ├── CommandPalette.tsx   # Command palette (⌘K)
│   │   ├── Fills.tsx            # Trade fills table
│   │   ├── OrderBook.tsx        # Bid/ask levels display
│   │   ├── Orders.tsx           # Orders table
│   │   ├── OrderTicket.tsx      # Order entry form
│   │   ├── Positions.tsx        # Positions table with P&L
│   │   ├── TopBar.tsx           # Top navigation bar
│   │   ├── TradesTape.tsx       # Recent trades list
│   │   └── Watchlist.tsx        # Symbol search and quotes
│   │
│   └── lib/                     # Core logic and utilities
│       ├── __tests__/           # Unit tests
│       │   ├── pnl.test.ts
│       │   └── validation.test.ts
│       │
│       ├── api.ts               # REST API client functions
│       ├── hotkeys.ts           # Keyboard shortcuts hook
│       ├── mock-data.ts         # Mock market data generator
│       ├── pnl.ts               # P&L calculation functions
│       ├── state.ts             # Zustand stores (UI & connection)
│       ├── types.ts             # TypeScript type definitions
│       ├── use-market-stream.ts # WebSocket hook (optional)
│       ├── utils.ts             # Utility functions (cn)
│       ├── validation.ts        # Order validation logic
│       └── ws-client.ts         # WebSocket client
│
├── mock-ws-server.ts            # Mock WebSocket server
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── vitest.config.ts             # Vitest configuration
└── vitest.setup.ts              # Test setup
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm

### Installation

1. **Navigate to the project directory:**

```bash
cd web-trading-app/next-trader
```

2. **Install dependencies:**

```bash
npm install
```
"try"----->>>>>npm install--legacy-peer-deps
or  new Vs ->>./START_STREAMING.sh
### Running the Application

You need to run two processes:

#### Terminal 1: Next.js Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

#### Terminal 2: Mock WebSocket Server

```bash
npm run mock:ws
```

The WebSocket server will run on `ws://localhost:4001`

### Running Tests

```bash
# Run all tests once
npm test

# Run tests in watch mode
npm run test:watch
```

### Building for Production

```bash
npm run build
npm start
```

## 🏗️ Architecture

### State Management

**Zustand** is used for UI state:
- Current symbol
- Timeframe selection
- Order ticket state (side, quantity, price)
- Command palette visibility
- Connection status

**TanStack Query** manages server state:
- Caching and automatic refetching
- Optimistic updates for mutations
- Query invalidation on order submission

### Data Flow

```
┌─────────────┐
│   REST API  │ ← Historical data, account info, CRUD operations
└─────────────┘
      ↓
┌─────────────┐
│ TanStack    │ ← Server state caching & mutations
│   Query     │
└─────────────┘
      ↓
┌─────────────┐
│  Components │ ← React components
└─────────────┘
      ↑
┌─────────────┐
│   Zustand   │ ← UI state
└─────────────┘
      ↑
┌─────────────┐
│  WebSocket  │ ← Real-time quotes, order book, trades
└─────────────┘
```

### Component Hierarchy

```
page.tsx (Main Trading Page)
├── TopBar
│   ├── Symbol & Timeframe selector
│   └── Connection status badge
├── Watchlist (left sidebar)
│   └── Symbol search & quote list
├── Chart (center top)
│   └── Candlestick chart with lightweight-charts
├── Bottom Tabs (center bottom)
│   ├── Positions table
│   ├── Orders table
│   ├── Fills table
│   └── Account summary
├── Right Sidebar
│   ├── OrderBook
│   ├── TradesTape
│   └── OrderTicket
└── CommandPalette (modal)
```

## 🧪 Testing Strategy

### Unit Tests

- **Validation Logic** (`validation.test.ts`): Tests order validation rules
- **P&L Calculations** (`pnl.test.ts`): Tests profit/loss calculation accuracy

### Test Coverage

- ✅ Order validation (symbol, quantity, price, type)
- ✅ P&L calculations for long/short positions
- ✅ Edge cases (zero, negative, NaN, Infinity)

### Running Specific Tests

```bash
# Run validation tests only
npm test validation

# Run PnL tests only
npm test pnl
```

## 🎨 Styling

The app uses **Tailwind CSS** with a custom dark theme:

- Dark background with glassmorphism effects
- Trading-specific color palette:
  - Green: Buy orders, positive P&L
  - Red: Sell orders, negative P&L
  - Blue: Primary accent
- Monospace font for prices and symbols
- Responsive grid layout

### Custom CSS Classes

- `.glass` - Glassmorphism effect with backdrop blur

## 🔌 API Endpoints

All endpoints are in `app/api/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/account` | GET | Account summary (equity, buying power, cash) |
| `/api/history?symbol=AAPL` | GET | Historical candles for chart |
| `/api/orderbook?symbol=AAPL` | GET | Order book snapshot (bids/asks) |
| `/api/trades?symbol=AAPL` | GET | Recent trade prints |
| `/api/orders` | GET | List all orders |
| `/api/orders` | POST | Submit new order |
| `/api/positions` | GET | Current positions |
| `/api/fills` | GET | Trade fills/executions |
| `/api/watchlist` | GET | Watchlist quotes |

## 🔄 WebSocket Protocol

### Client → Server

```json
{
  "type": "subscribe",
  "symbols": ["AAPL", "MSFT"]
}
```

### Server → Client

**Quote Update:**
```json
{
  "type": "quote",
  "payload": {
    "symbol": "AAPL",
    "last": 186.42,
    "bid": 186.40,
    "ask": 186.44,
    "change": 1.25,
    "changePercent": 0.68,
    "timestamp": 1234567890
  }
}
```

**Order Book Update:**
```json
{
  "type": "orderbook",
  "payload": {
    "bids": [{ "price": 186.40, "size": 500 }, ...],
    "asks": [{ "price": 186.44, "size": 300 }, ...],
    "mid": 186.42,
    "spread": 0.04,
    "ts": 1234567890
  }
}
```

**Trade Print:**
```json
{
  "type": "trade",
  "payload": {
    "price": 186.42,
    "size": 100,
    "side": "buy",
    "ts": 1234567890
  }
}
```

## 🔐 Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_WS_URL=ws://localhost:4001
```

## 📝 Type System

All types are defined in `src/lib/types.ts`:

- `Candle` - OHLCV candlestick data
- `Quote` - Real-time quote with bid/ask
- `Order` - Order with status tracking
- `Position` - Position with P&L
- `Fill` - Trade execution record
- `OrderBookSnapshot` - Bid/ask levels
- `TradePrint` - Individual trade
- `AccountSummary` - Account balances

## 🎯 Roadmap

Future enhancements:

- [ ] Real Schwab API integration
- [ ] Multi-leg options trading
- [ ] Advanced charting indicators
- [ ] Alert system
- [ ] Trade journal
- [ ] Risk management tools
- [ ] Dark/light theme toggle
- [ ] Mobile responsive layout
- [ ] Historical backtest mode

## 🐛 Troubleshooting

### WebSocket won't connect

Ensure the mock server is running:
```bash
npm run mock:ws
```

Check console for connection errors and verify `NEXT_PUBLIC_WS_URL`.

### Chart not rendering

Ensure historical data is available. Check browser console for errors.

### Tests failing

Run tests with verbose output:
```bash
npm test -- --reporter=verbose
```

## 📄 License

This project is part of the Schwabdev repository.

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Use conventional commits

## 📞 Support

For issues related to the Schwab API integration, refer to the parent repository documentation.


