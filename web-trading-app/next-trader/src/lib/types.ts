export type Timeframe = "1m" | "5m" | "15m" | "1h" | "1d";

export type Side = "buy" | "sell";

export type OrderType = "market" | "limit";

export type OrderStatus = "working" | "filled" | "rejected" | "canceled" | "partial";

export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Quote {
  symbol: string;
  last: number;
  change: number;
  changePercent: number;
  bid: number;
  ask: number;
  timestamp: number;
}

export interface Order {
  id: string;
  symbol: string;
  qty: number;
  type: OrderType;
  side: Side;
  limitPrice?: number;
  status: OrderStatus;
  submittedAt: number;
}

export interface Position {
  symbol: string;
  qty: number;
  avgPrice: number;
  plOpen: number;
  plDay: number;
}

export interface Fill {
  id: string;
  orderId: string;
  symbol: string;
  qty: number;
  price: number;
  side: Side;
  timestamp: number;
}

export interface OrderBookLevel {
  price: number;
  size: number;
}

export interface OrderBookSnapshot {
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  mid: number;
  spread: number;
  ts: number;
}

export interface TradePrint {
  price: number;
  size: number;
  side: Side;
  ts: number;
}

export type ConnectionState = "connecting" | "open" | "closed" | "error" | "reconnecting";

export interface AccountSummary {
  buyingPower: number;
  cash: number;
  equity: number;
  maintenanceReq: number;
}

