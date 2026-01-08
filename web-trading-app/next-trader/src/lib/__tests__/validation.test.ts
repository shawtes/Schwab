import { describe, it, expect } from "vitest";
import { validateOrder } from "../validation";

describe("validateOrder", () => {
  it("should accept valid market buy order", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(true);
  });

  it("should accept valid limit sell order", () => {
    const result = validateOrder({
      symbol: "TSLA",
      qty: 50,
      side: "sell",
      type: "limit",
      limitPrice: 250.5
    });
    expect(result.ok).toBe(true);
  });

  it("should reject empty symbol", () => {
    const result = validateOrder({
      symbol: "",
      qty: 100,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Symbol");
    }
  });

  it("should reject zero quantity", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 0,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Quantity");
    }
  });

  it("should reject negative quantity", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: -50,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Quantity");
    }
  });

  it("should reject invalid side", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "invalid" as any,
      type: "market"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Side");
    }
  });

  it("should reject invalid order type", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "buy",
      type: "stop" as any
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Type");
    }
  });

  it("should reject limit order without price", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "buy",
      type: "limit"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Limit price");
    }
  });

  it("should reject limit order with zero price", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "buy",
      type: "limit",
      limitPrice: 0
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Limit price");
    }
  });

  it("should reject limit order with negative price", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "buy",
      type: "limit",
      limitPrice: -50
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Limit price");
    }
  });

  it("should handle decimal quantities", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100.5,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(true);
  });

  it("should handle decimal limit prices", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: 100,
      side: "buy",
      type: "limit",
      limitPrice: 150.25
    });
    expect(result.ok).toBe(true);
  });

  it("should reject NaN quantity", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: NaN,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Quantity");
    }
  });

  it("should reject Infinity quantity", () => {
    const result = validateOrder({
      symbol: "AAPL",
      qty: Infinity,
      side: "buy",
      type: "market"
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Quantity");
    }
  });
});


