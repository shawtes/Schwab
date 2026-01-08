import { describe, it, expect } from "vitest";
import { calcOpenPnl, calcPnlPct } from "../pnl";

describe("calcOpenPnl", () => {
  it("should calculate profit for long position", () => {
    const pnl = calcOpenPnl({
      qty: 100,
      avgPrice: 150,
      last: 160
    });
    expect(pnl).toBe(1000);
  });

  it("should calculate loss for long position", () => {
    const pnl = calcOpenPnl({
      qty: 100,
      avgPrice: 150,
      last: 140
    });
    expect(pnl).toBe(-1000);
  });

  it("should calculate profit for short position", () => {
    const pnl = calcOpenPnl({
      qty: -100,
      avgPrice: 150,
      last: 140
    });
    expect(pnl).toBe(1000);
  });

  it("should calculate loss for short position", () => {
    const pnl = calcOpenPnl({
      qty: -100,
      avgPrice: 150,
      last: 160
    });
    expect(pnl).toBe(-1000);
  });

  it("should return zero for no position", () => {
    const pnl = calcOpenPnl({
      qty: 0,
      avgPrice: 150,
      last: 160
    });
    expect(pnl).toBe(0);
  });

  it("should handle decimal quantities", () => {
    const pnl = calcOpenPnl({
      qty: 50.5,
      avgPrice: 100,
      last: 102
    });
    expect(pnl).toBe(101);
  });

  it("should handle decimal prices", () => {
    const pnl = calcOpenPnl({
      qty: 100,
      avgPrice: 150.25,
      last: 150.75
    });
    expect(pnl).toBe(50);
  });

  it("should calculate correctly when price unchanged", () => {
    const pnl = calcOpenPnl({
      qty: 100,
      avgPrice: 150,
      last: 150
    });
    expect(pnl).toBe(0);
  });
});

describe("calcPnlPct", () => {
  it("should calculate percentage gain", () => {
    const pct = calcPnlPct({
      pnl: 1000,
      avgPrice: 100,
      qty: 100
    });
    expect(pct).toBe(10);
  });

  it("should calculate percentage loss", () => {
    const pct = calcPnlPct({
      pnl: -1000,
      avgPrice: 100,
      qty: 100
    });
    expect(pct).toBe(-10);
  });

  it("should return zero for zero P&L", () => {
    const pct = calcPnlPct({
      pnl: 0,
      avgPrice: 100,
      qty: 100
    });
    expect(pct).toBe(0);
  });

  it("should return zero when basis is zero", () => {
    const pct = calcPnlPct({
      pnl: 100,
      avgPrice: 0,
      qty: 100
    });
    expect(pct).toBe(0);
  });

  it("should handle small positions", () => {
    const pct = calcPnlPct({
      pnl: 5,
      avgPrice: 100,
      qty: 1
    });
    expect(pct).toBe(5);
  });

  it("should handle large positions", () => {
    const pct = calcPnlPct({
      pnl: 50000,
      avgPrice: 100,
      qty: 10000
    });
    expect(pct).toBe(5);
  });

  it("should handle decimal values", () => {
    const pct = calcPnlPct({
      pnl: 123.45,
      avgPrice: 50.5,
      qty: 100
    });
    expect(pct).toBeCloseTo(24.44, 1);
  });

  it("should handle negative quantities (short positions)", () => {
    const pct = calcPnlPct({
      pnl: 500,
      avgPrice: 100,
      qty: -100
    });
    // For short positions, basis is still positive (absolute value)
    expect(pct).toBe(-5);
  });
});


