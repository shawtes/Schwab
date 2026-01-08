# Project Structure Guide

Complete reference for the Schwab Pro Trading Platform architecture.

## 📂 Directory Overview

### Root Level

```
next-trader/
├── app/                    # Next.js App Router
├── src/                    # Source code
├── public/                 # Static assets
├── node_modules/           # Dependencies
├── package.json            # Project configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.ts      # Tailwind CSS configuration
├── next.config.mjs         # Next.js configuration
├── postcss.config.mjs      # PostCSS configuration
├── vitest.config.ts        # Test configuration
├── vitest.setup.ts         # Test setup
├── mock-ws-server.ts       # WebSocket mock server
├── README.md               # Main documentation
├── QUICK_START.md          # Quick start guide
└── PROJECT_STRUCTURE.md    # This file
```

## 🗂️ App Directory (`app/`)

Next.js 14 App Router structure.

### API Routes (`app/api/`)

RESTful API endpoints for server-side data:

```
app/api/
├── account/
│   └── route.ts           # GET /api/account
├── fills/
│   └── route.ts           # GET /api/fills
├── history/
│   └── route.ts           # GET /api/history?symbol=AAPL
├── orderbook/
│   └── route.ts           # GET /api/orderbook?symbol=AAPL
├── orders/
│   └── route.ts           # GET, POST /api/orders
├── positions/
│   └── route.ts           # GET /api/positions
├── trades/
│   └── route.ts           # GET /api/trades?symbol=AAPL
└── watchlist/
    └── route.ts           # GET /api/watchlist
```

**Key Files:**
- `route.ts` - API route handlers using Next.js Route Handlers
- Each returns JSON responses
- Uses mock data from `src/lib/mock-data.ts`

### Root Files

- `globals.css` - Global styles, CSS variables, dark theme
- `layout.tsx` - Root layout with providers
- `page.tsx` - Main trading interface page

## 📦 Source Directory (`src/`)

### Components (`src/components/`)

React components organized by feature:

#### UI Components (`src/components/ui/`)

Reusable shadcn/ui components:

```
ui/
├── badge.tsx              # Status badges (connected, working, etc.)
├── button.tsx             # Primary button component
├── card.tsx               # Card container with header/content
├── command.tsx            # Command palette primitives
├── dialog.tsx             # Modal dialog
├── input.tsx              # Text input field
└── tabs.tsx               # Tab navigation
```

#### Feature Components (`src/components/`)

Trading-specific components:

```
components/
├── Chart.tsx              # Candlestick chart (lightweight-charts)
├── CommandPalette.tsx     # Command palette (⌘K)
├── Fills.tsx              # Trade fills table
├── OrderBook.tsx          # Bid/ask depth display
├── Orders.tsx             # Orders table
├── OrderTicket.tsx        # Order entry form
├── Positions.tsx          # Positions table with P&L
├── TopBar.tsx             # Top navigation bar
├── TradesTape.tsx         # Recent trades list
└── Watchlist.tsx          # Symbol search and quotes
```

**Component Patterns:**

All feature components follow this pattern:

```typescript
interface ComponentProps {
  data: DataType | undefined;
  isLoading?: boolean;
}

export function Component({ data, isLoading }: ComponentProps) {
  // Loading state
  if (isLoading) return <LoadingState />;
  
  // Empty state
  if (!data || data.length === 0) return <EmptyState />;
  
  // Main render
  return <MainContent />;
}
```

### Library (`src/lib/`)

Core business logic and utilities:

```
lib/
├── __tests__/             # Unit tests
│   ├── pnl.test.ts       # P&L calculation tests
│   └── validation.test.ts # Order validation tests
├── api.ts                 # REST API client functions
├── hotkeys.ts             # Keyboard shortcuts hook
├── mock-data.ts           # Mock market data generator
├── pnl.ts                 # P&L calculation functions
├── state.ts               # Zustand stores
├── types.ts               # TypeScript type definitions
├── use-market-stream.ts   # WebSocket hook (optional)
├── utils.ts               # Utility functions (cn)
├── validation.ts          # Order validation logic
└── ws-client.ts           # WebSocket client
```

#### Key Files Deep Dive

**`types.ts`** - Type definitions
- `Candle` - OHLCV candlestick data
- `Quote` - Real-time quote
- `Order` - Order with status
- `Position` - Position with P&L
- `Fill` - Trade execution
- `OrderBookSnapshot` - Bid/ask levels
- `TradePrint` - Individual trade
- `AccountSummary` - Account balances

**`state.ts`** - Zustand stores
- `useUiStore` - UI state (symbol, timeframe, command palette)
- `useConnectionStore` - WebSocket connection state

**`api.ts`** - REST API client
- `fetchHistory()` - Get historical candles
- `fetchWatchlist()` - Get watchlist quotes
- `fetchOrderBook()` - Get order book snapshot
- `fetchTrades()` - Get recent trades
- `fetchOrders()` - Get orders
- `submitOrder()` - Submit new order
- `fetchPositions()` - Get positions
- `fetchAccount()` - Get account summary
- `fetchFills()` - Get trade fills

**`ws-client.ts`** - WebSocket client
- `connectMarketSocket()` - Establish WebSocket connection
- Handles reconnection with exponential backoff
- Emits events: `onQuote`, `onTrade`, `onOrderBook`, `onStatus`

**`validation.ts`** - Order validation
- `validateOrder()` - Validates order before submission
- Checks: symbol, quantity, side, type, limit price

**`pnl.ts`** - P&L calculations
- `calcOpenPnl()` - Calculate unrealized P&L
- `calcPnlPct()` - Calculate P&L percentage

**`hotkeys.ts`** - Keyboard shortcuts
- `useHotkeys()` - React hook for keyboard shortcuts
- Handles: `b`, `s`, `escape`, `cmd+k`

**`mock-data.ts`** - Mock data generator
- Generates realistic market data
- Simulates price movements
- Creates order book depth
- Generates trade history

### App Providers (`src/app/`)

```
app/
└── providers.tsx          # TanStack Query provider
```

Sets up QueryClient with default options.

## 🔧 Configuration Files

### `package.json`

Dependencies and scripts:

```json
{
  "scripts": {
    "dev": "next dev",                    // Start dev server
    "build": "next build",                // Build for production
    "start": "next start",                // Start production server
    "lint": "next lint",                  // Lint code
    "test": "vitest run",                 // Run tests once
    "test:watch": "vitest",               // Run tests in watch mode
    "mock:ws": "ts-node --transpile-only mock-ws-server.ts"  // Start mock WebSocket
  }
}
```

### `tsconfig.json`

TypeScript configuration with path aliases:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]   // Import alias
    }
  }
}
```

Usage: `import { Button } from "@/components/ui/button"`

### `tailwind.config.ts`

Tailwind CSS configuration with custom theme:

- Dark color palette
- Custom CSS variables
- Trading-specific colors (green/red)
- Glassmorphism utilities

### `vitest.config.ts`

Test configuration:

- jsdom environment for React component testing
- Path alias resolution
- Setup file: `vitest.setup.ts`

## 🌐 WebSocket Server (`mock-ws-server.ts`)

Standalone TypeScript server that simulates real-time market data:

**Features:**
- Runs on port 4001
- Subscribes to symbols
- Sends quotes every 1s
- Sends order book updates every 500ms
- Sends random trades every 2-5s
- Heartbeat every 10s

**Message Types:**
- `subscribe` - Client subscribes to symbols
- `unsubscribe` - Client unsubscribes
- `quote` - Real-time quote update
- `orderbook` - Order book snapshot
- `trade` - Trade print
- `heartbeat` - Connection keepalive

## 🎨 Styling System

### Global Styles (`app/globals.css`)

```css
:root {
  --background: 222.2 84% 4.9%;      /* Dark background */
  --foreground: 210 40% 98%;         /* Light text */
  --primary: 199 89% 48%;            /* Blue accent */
  --destructive: 0 84.2% 60.2%;      /* Red for sells */
  /* ... more variables */
}

.glass {
  /* Glassmorphism effect */
  @apply bg-gradient-to-br from-slate-900/70 
         via-slate-900/60 to-slate-800/60 
         border border-slate-700/70 backdrop-blur-md;
}
```

### Color System

- **Green** (`text-green-400`, `bg-green-600`) - Buy, positive P&L
- **Red** (`text-red-400`, `bg-red-600`) - Sell, negative P&L
- **Blue** (`text-primary`, `bg-primary`) - Primary accent
- **Gray** (`text-muted-foreground`) - Secondary text

## 🔄 Data Flow

```
User Action
    ↓
Component
    ↓
    ├─→ UI State (Zustand)
    │   ├─ Symbol selection
    │   ├─ Timeframe
    │   └─ Command palette
    │
    └─→ Server State (TanStack Query)
        ├─ REST API (historical, CRUD)
        └─ WebSocket (real-time)
            ├─ Quotes
            ├─ Order book
            └─ Trades
```

## 🧪 Testing Structure

```
__tests__/
├── validation.test.ts     # 15+ test cases
└── pnl.test.ts           # 10+ test cases
```

**Coverage:**
- Order validation rules
- P&L calculations
- Edge cases (zero, negative, NaN, Infinity)

## 📝 Type System Flow

```
types.ts
    ↓
validation.ts → OrderDraft
    ↓
api.ts → Order
    ↓
Components → Display
```

## 🚀 Build Output

After `npm run build`:

```
.next/
├── server/               # Server-side code
├── static/              # Static assets
└── cache/               # Build cache
```

## 📊 Component Props Pattern

Standard props interface:

```typescript
interface ComponentProps {
  data: DataType | undefined;    // Data to display
  isLoading?: boolean;           // Loading state
  onAction?: (param) => void;    // Event handlers
}
```

## 🎯 Import Patterns

```typescript
// UI components
import { Button } from "@/components/ui/button";

// Feature components
import { Chart } from "@/components/Chart";

// Lib utilities
import { cn } from "@/lib/utils";
import { useUiStore } from "@/lib/state";
import { fetchOrders } from "@/lib/api";

// Types
import type { Order, Position } from "@/lib/types";
```

## 🔗 Dependencies

### Production
- `next` - React framework
- `react` / `react-dom` - React library
- `@tanstack/react-query` - Server state management
- `zustand` - Client state management
- `lightweight-charts` - Charting library
- `tailwindcss` - CSS framework
- `lucide-react` - Icons
- `@radix-ui/*` - UI primitives
- `cmdk` - Command palette

### Development
- `typescript` - Type checking
- `vitest` - Testing framework
- `@testing-library/*` - React testing
- `ws` - WebSocket library for mock server

---

## 📚 Further Reading

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [Zustand Docs](https://zustand-demo.pmnd.rs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Docs](https://ui.shadcn.com/)


