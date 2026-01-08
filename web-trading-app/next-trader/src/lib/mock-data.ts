import { AccountSummary, Candle, Fill, Order, OrderBookLevel, OrderBookSnapshot, Position, Quote, TradePrint } from "./types";
import { OrderDraft } from "./validation";

const SYMBOLS = ["AAPL", "MSFT", "SPY", "TSLA", "NVDA", "AMD"];

const BASE_PRICES: Record<string, number> = {
  AAPL: 186.42,
  MSFT: 415.23,
  SPY: 520.11,
  TSLA: 182.35,
  NVDA: 905.12,
  AMD: 176.4
};

const watchlistState: Record<string, Quote> = {};
const tradesStore: Record<string, TradePrint[]> = {};
const orderBookStore: Record<string, OrderBookSnapshot> = {};
const historyStore: Record<string, Candle[]> = {};

export const positions: Position[] = [
  { symbol: "AAPL", qty: 200, avgPrice: 184.5, plOpen: 380, plDay: 120 },
  { symbol: "NVDA", qty: 50, avgPrice: 855.2, plOpen: 2495, plDay: 640 },
  { symbol: "SPY", qty: -40, avgPrice: 523.4, plOpen: 132, plDay: 55 }
];

export const orders: Order[] = [
  {
    id: "ORD-1001",
    symbol: "MSFT",
    qty: 50,
    side: "buy",
    type: "limit",
    limitPrice: 410.5,
    status: "working",
    submittedAt: Date.now() - 1000 * 60 * 10
  },
  {
    id: "ORD-1000",
    symbol: "TSLA",
    qty: 25,
    side: "sell",
    type: "market",
    status: "filled",
    submittedAt: Date.now() - 1000 * 60 * 60
  }
];

export const fills: Fill[] = [
  {
    id: "FILL-2002",
    orderId: "ORD-1000",
    symbol: "TSLA",
    qty: 25,
    price: 182.05,
    side: "sell",
    timestamp: Date.now() - 1000 * 60 * 58
  }
];

export const account: AccountSummary = {
  buyingPower: 250000,
  cash: 150000,
  equity: 365000,
  maintenanceReq: 120000
};

function rand(min: number, max: number) {
  return Math.random() * (max - min) + min;
}

function jitterPrice(symbol: string) {
  const drift = rand(-1.5, 1.5);
  BASE_PRICES[symbol] = Math.max(1, BASE_PRICES[symbol] + drift);
  return Number(BASE_PRICES[symbol].toFixed(2));
}

function buildQuote(symbol: string): Quote {
  const last = jitterPrice(symbol);
  const change = rand(-2, 2);
  const changePercent = (change / Math.max(1, last - change)) * 100;
  const spread = rand(0.01, 0.25);
  const bid = last - spread / 2;
  const ask = last + spread / 2;
  return {
    symbol,
    last,
    change: Number(change.toFixed(2)),
    changePercent: Number(changePercent.toFixed(2)),
    bid: Number(bid.toFixed(2)),
    ask: Number(ask.toFixed(2)),
    timestamp: Date.now()
  };
}

function seedTrades(symbol: string) {
  const trades: TradePrint[] = [];
  const base = BASE_PRICES[symbol];
  for (let i = 0; i < 20; i++) {
    trades.push({
      price: Number((base + rand(-1.5, 1.5)).toFixed(2)),
      size: Math.floor(rand(10, 500)),
      side: Math.random() > 0.5 ? "buy" : "sell",
      ts: Date.now() - i * 1000 * 5
    });
  }
  tradesStore[symbol] = trades;
}

function seedHistory(symbol: string) {
  const candles: Candle[] = [];
  const base = BASE_PRICES[symbol];
  let cursor = base - rand(0, 3);
  for (let i = 60; i >= 0; i--) {
    const open = cursor + rand(-1, 1);
    const close = open + rand(-0.8, 0.8);
    const high = Math.max(open, close) + rand(0, 0.6);
    const low = Math.min(open, close) - rand(0, 0.6);
    const volume = Math.floor(rand(1e4, 8e4));
    candles.push({
      time: Date.now() - i * 60 * 1000,
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume
    });
    cursor = close;
  }
  historyStore[symbol] = candles;
}

function seedOrderBook(symbol: string) {
  orderBookStore[symbol] = buildOrderBook(symbol);
}

function buildLevels(mid: number, side: "bid" | "ask"): OrderBookLevel[] {
  const levels: OrderBookLevel[] = [];
  for (let i = 1; i <= 10; i++) {
    const price =
      side === "bid" ? mid - i * rand(0.05, 0.2) : mid + i * rand(0.05, 0.2);
    levels.push({
      price: Number(price.toFixed(2)),
      size: Math.floor(rand(50, 800))
    });
  }
  return levels;
}

function buildOrderBook(symbol: string): OrderBookSnapshot {
  const mid = jitterPrice(symbol);
  const bids = buildLevels(mid, "bid");
  const asks = buildLevels(mid, "ask");
  const bestBid = bids[0]?.price ?? mid;
  const bestAsk = asks[0]?.price ?? mid;
  return {
    bids,
    asks,
    mid,
    spread: Number((bestAsk - bestBid).toFixed(2)),
    ts: Date.now()
  };
}

SYMBOLS.forEach((sym) => {
  watchlistState[sym] = buildQuote(sym);
  seedTrades(sym);
  seedHistory(sym);
  seedOrderBook(sym);
});

export function getWatchlist(): Quote[] {
  return SYMBOLS.map((sym) => {
    const next = buildQuote(sym);
    watchlistState[sym] = next;
    return next;
  });
}

export function getOrderBook(symbol: string): OrderBookSnapshot {
  const snap = buildOrderBook(symbol);
  orderBookStore[symbol] = snap;
  return snap;
}

export function getTrades(symbol: string): TradePrint[] {
  const base = tradesStore[symbol] ?? [];
  const nextTrade: TradePrint = {
    price: Number((BASE_PRICES[symbol] + rand(-1, 1)).toFixed(2)),
    size: Math.floor(rand(25, 500)),
    side: Math.random() > 0.5 ? "buy" : "sell",
    ts: Date.now()
  };
  const updated = [nextTrade, ...base].slice(0, 50);
  tradesStore[symbol] = updated;
  return updated;
}

export function getHistory(symbol: string): Candle[] {
  if (!historyStore[symbol]) {
    seedHistory(symbol);
  }
  return historyStore[symbol];
}

export function createOrder(draft: OrderDraft): Order {
  const id = `ORD-${Date.now()}`;
  const status = draft.type === "market" ? "filled" : "working";
  const order: Order = {
    id,
    symbol: draft.symbol,
    qty: draft.qty,
    side: draft.side,
    type: draft.type,
    limitPrice: draft.limitPrice,
    status,
    submittedAt: Date.now()
  };
  orders.unshift(order);

  if (status === "filled") {
    fills.unshift({
      id: `FILL-${Date.now()}`,
      orderId: id,
      symbol: draft.symbol,
      qty: draft.qty,
      price: draft.limitPrice ?? BASE_PRICES[draft.symbol] ?? 0,
      side: draft.side,
      timestamp: Date.now()
    });
  }

  return order;
}

export function getQuote(symbol: string): Quote {
  return watchlistState[symbol] ?? buildQuote(symbol);
}

export function listSymbols() {
  return SYMBOLS;
}


