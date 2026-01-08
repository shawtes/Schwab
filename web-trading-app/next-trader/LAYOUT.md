# 📐 Layout & Visual Reference

Visual guide to the trading platform layout and component placement.

## 🖥️ Full Screen Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  TopBar                                                              │
│  [AAPL] [1m][5m][15m][1h][1d]           🟢 Connected  [⌘K Commands] │
├──────────┬────────────────────────────────────────────┬──────────────┤
│          │                                            │              │
│          │           Chart (Center)                   │  OrderBook   │
│ Watch    │                                            │              │
│ list     │   ┌─────────────────────────────────┐     │  Bids/Asks   │
│          │   │                                 │     │  Spread      │
│ [Search] │   │     Candlestick Chart           │     │              │
│          │   │                                 │     ├──────────────┤
│ AAPL     │   │     (Lightweight Charts)        │     │              │
│ MSFT     │   │                                 │     │ TradesTape   │
│ SPY      │   │                                 │     │              │
│ TSLA     │   └─────────────────────────────────┘     │ Recent       │
│ NVDA     │                                            │ Executions   │
│ AMD      │                                            │              │
│          │                                            ├──────────────┤
│          ├────────────────────────────────────────────┤              │
│          │                                            │ OrderTicket  │
│          │  Bottom Tabs                               │              │
│          │  [Positions][Orders][Fills][Account]      │ [Buy][Sell]  │
│          │                                            │              │
│          │  ┌──────────────────────────────────────┐ │ Market/Limit │
│          │  │                                      │ │              │
│          │  │  Positions Table                     │ │ Quantity     │
│          │  │  Symbol | Qty | Avg | P&L | Day P&L │ │              │
│          │  │                                      │ │ [Submit]     │
│          │  └──────────────────────────────────────┘ │              │
│          │                                            │              │
└──────────┴────────────────────────────────────────────┴──────────────┘
```

## 📊 Component Breakdown

### Top Bar (100% width, fixed height)
```
┌────────────────────────────────────────────────────────────┐
│ [Symbol] [Timeframe Buttons]    [Status] [Commands]        │
└────────────────────────────────────────────────────────────┘
```

### Left Sidebar (Fixed width: 256px)
```
┌─────────────┐
│ Watchlist   │
├─────────────┤
│ [Search]    │
│             │
│ ● AAPL      │
│   186.42 ↑  │
│             │
│   MSFT      │
│   415.23 ↓  │
│             │
│   SPY       │
│   520.11 ↑  │
│             │
│   ...       │
└─────────────┘
```

### Center Area (Flexible width)

#### Chart Section (60% height)
```
┌─────────────────────────────────────┐
│ AAPL                                │
├─────────────────────────────────────┤
│                                     │
│    ┌─┐  ┌─┐                        │
│    │ │  │ │  ┌─┐                   │
│  ┌─┘ └──┘ └──┘ └─┐                 │
│  │                │                 │
│  └────────────────┘                 │
│                                     │
│  Price                              │
│                                     │
│      Time                           │
└─────────────────────────────────────┘
```

#### Bottom Tabs (40% height)
```
┌─────────────────────────────────────┐
│ [Positions][Orders][Fills][Account] │
├─────────────────────────────────────┤
│                                     │
│  Symbol │ Qty │ Avg │ P&L │ Day    │
│  ────────────────────────────────   │
│  AAPL   │ 200 │ 184 │ +380│ +120   │
│  NVDA   │  50 │ 855 │+2495│ +640   │
│  SPY    │ -40 │ 523 │ +132│  +55   │
│                                     │
└─────────────────────────────────────┘
```

### Right Sidebar (Fixed width: 320px)

```
┌──────────────────┐
│ Order Book       │
├──────────────────┤
│ Size│Price│Total│
│  500│186.44│ 500│ ← Ask
│  300│186.43│ 800│ ← Ask
│ ─────────────── │
│    186.42       │ ← Mid
│ ─────────────── │
│  200│186.41│ 200│ ← Bid
│  400│186.40│ 600│ ← Bid
├──────────────────┤
│ Trades           │
├──────────────────┤
│ Time │Price│Size│
│ 10:30│186.42│100│
│ 10:29│186.40│ 50│
├──────────────────┤
│ Order Ticket     │
├──────────────────┤
│ Symbol: AAPL     │
│                  │
│ [Buy]   [Sell]   │
│                  │
│ [Market][Limit]  │
│                  │
│ Qty: [   100   ] │
│                  │
│ [Submit Order]   │
└──────────────────┘
```

## 🎨 Color Guide

### Status Colors
- 🟢 **Green** (#10b981) - Buy, Positive P&L, Connected
- 🔴 **Red** (#ef4444) - Sell, Negative P&L, Error
- 🔵 **Blue** (#0ea5e9) - Primary accent, Working orders
- ⚪ **Gray** (#6b7280) - Neutral, Muted text

### Component Colors
- **Background**: Very dark gray (#0f1419)
- **Card Background**: Dark gray with glass effect
- **Border**: Subtle gray (#374151)
- **Text Primary**: Light gray (#f9fafb)
- **Text Secondary**: Medium gray (#9ca3af)

## 📏 Dimensions

### Responsive Breakpoints
- Desktop: Full layout as shown
- Tablet: Sidebar becomes drawer
- Mobile: Stack vertically

### Fixed Sizes
- TopBar Height: `48px`
- Left Sidebar Width: `256px` (16rem)
- Right Sidebar Width: `320px` (20rem)

### Flexible Sizes
- Center Area: Remaining width
- Chart Height: 60% of center area
- Bottom Tabs: 40% of center area

## 🖱️ Interactive Elements

### Hover States
```
Default:   bg-transparent
Hover:     bg-accent/50
Active:    bg-accent
Selected:  bg-accent border-primary
```

### Button States
```
Default:   Normal colors
Hover:     Brightness +10%
Active:    Brightness -10%
Disabled:  Opacity 50%
```

### Input States
```
Default:   border-input
Focus:     ring-1 ring-ring
Error:     border-destructive
```

## 📱 Mobile Layout (< 768px)

```
┌──────────────────┐
│     TopBar       │
├──────────────────┤
│                  │
│     Chart        │
│                  │
├──────────────────┤
│  Order Ticket    │
├──────────────────┤
│  Bottom Tabs     │
│  (Positions)     │
└──────────────────┘

[Hamburger Menu]
  → Watchlist
  → Order Book
  → Trades
```

## 🎯 Component Hierarchy

```
TradingPage
│
├─ TopBar
│  ├─ Symbol Display
│  ├─ Timeframe Buttons
│  ├─ Connection Badge
│  └─ Command Palette Button
│
├─ Layout (3-column grid)
│  │
│  ├─ Left Sidebar
│  │  └─ Watchlist
│  │     ├─ Search Input
│  │     └─ Symbol List
│  │
│  ├─ Center Area (2-row grid)
│  │  │
│  │  ├─ Chart Section
│  │  │  └─ Chart Component
│  │  │
│  │  └─ Bottom Tabs
│  │     ├─ Positions Tab → Positions Component
│  │     ├─ Orders Tab → Orders Component
│  │     ├─ Fills Tab → Fills Component
│  │     └─ Account Tab → Account Summary
│  │
│  └─ Right Sidebar (3-section stack)
│     ├─ OrderBook Component
│     ├─ TradesTape Component
│     └─ OrderTicket Component
│
└─ CommandPalette (modal overlay)
```

## 🎬 Animation & Transitions

### Transitions
- Hover effects: `150ms ease`
- Tab switching: `200ms ease-in-out`
- Modal open/close: `300ms ease-out`

### Loading States
- Skeleton loader: Pulsing animation
- Spinner: Rotate 360° in 1s

## 🔲 Grid System

### Main Layout Grid
```css
display: grid;
grid-template-columns: 256px 1fr 320px;
grid-template-rows: 48px 1fr;
```

### Center Area Grid
```css
display: grid;
grid-template-rows: 60% 40%;
```

## 📐 Spacing System

```
xs:  0.25rem (4px)
sm:  0.5rem  (8px)
md:  1rem    (16px)
lg:  1.5rem  (24px)
xl:  2rem    (32px)
```

## 🎨 Typography

### Font Families
- **Sans-serif**: Inter (body text)
- **Monospace**: Default system mono (prices, symbols)

### Font Sizes
- xs: 0.75rem (12px)
- sm: 0.875rem (14px)
- base: 1rem (16px)
- lg: 1.125rem (18px)
- xl: 1.25rem (20px)
- 2xl: 1.5rem (24px)

### Font Weights
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

---

## 🖼️ Visual Examples

### Chart Styles
- Green candles: Close > Open
- Red candles: Close < Open
- Wick colors match candle color
- Grid lines: Subtle gray
- Crosshair: White with transparency

### Order Book Styles
- Bids: Green background gradient (left to right)
- Asks: Red background gradient (left to right)
- Size bar width: Proportional to max size
- Mid price: Blue highlight

### Table Styles
- Header: Sticky, gray background
- Row hover: Light gray background
- Border: Subtle gray between rows
- Alternate rows: None (all same background)

---

**This layout provides a professional trading experience optimized for speed, clarity, and keyboard-first navigation.**


