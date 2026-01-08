import { OrderType, Side } from "./types";

export interface OrderDraft {
  symbol: string;
  qty: number;
  side: Side;
  type: OrderType;
  limitPrice?: number;
}

export type ValidationResult =
  | { ok: true }
  | { ok: false; reason: string };

export function validateOrder(order: OrderDraft): ValidationResult {
  if (!order.symbol || order.symbol.trim().length < 1) {
    return { ok: false, reason: "Symbol is required" };
  }
  if (!Number.isFinite(order.qty) || order.qty <= 0) {
    return { ok: false, reason: "Quantity must be greater than zero" };
  }
  if (!["buy", "sell"].includes(order.side)) {
    return { ok: false, reason: "Side must be buy or sell" };
  }
  if (!["market", "limit"].includes(order.type)) {
    return { ok: false, reason: "Type must be market or limit" };
  }
  if (order.type === "limit") {
    if (!Number.isFinite(order.limitPrice)) {
      return { ok: false, reason: "Limit price required for limit orders" };
    }
    if (order.limitPrice !== undefined && order.limitPrice <= 0) {
      return { ok: false, reason: "Limit price must be positive" };
    }
  }
  return { ok: true };
}

