import { AccountSummary, Candle, Fill, Order, OrderBookSnapshot, Position, Quote, TradePrint } from "./types";
import { OrderDraft } from "./validation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

const headers = { "Content-Type": "application/json" };

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, { headers, ...init });
  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || "Request failed");
  }
  return res.json();
}

// Convert Schwab API response to our format
function convertToCandles(schwabData: any): Candle[] {
  if (!schwabData || !schwabData.candles) return [];
  
  return schwabData.candles.map((candle: any) => {
    // Schwab API returns datetime as milliseconds since epoch
    const timestampMs = candle.datetime;
    
    // Convert to Unix timestamp in SECONDS (lightweight-charts uses seconds)
    return {
      time: Math.floor(timestampMs / 1000),
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
      volume: candle.volume
    };
  });
}

function convertToQuote(schwabQuote: any, symbol: string): Quote {
  const quote = schwabQuote.quote || schwabQuote;
  const lastPrice = quote.lastPrice || quote.mark || 0;
  const bidPrice = quote.bidPrice || 0;
  const askPrice = quote.askPrice || 0;
  const change = quote.netChange || 0;
  const changePercent = quote.netPercentChange || 0;

  return {
    symbol,
    last: lastPrice,
    change,
    changePercent,
    bid: bidPrice,
    ask: askPrice,
    timestamp: Date.now()
  };
}

export const fetchHistory = async (symbol: string, timeframe: string = "5m"): Promise<Candle[]> => {
  try {
    // Convert timeframe to Schwab API parameters
    let periodType = "day";
    let period = 1;
    let frequencyType = "minute";
    let frequency = 5;

    switch (timeframe) {
      case "1m":
        periodType = "day";
        period = 1;
        frequencyType = "minute";
        frequency = 1;
        break;
      case "5m":
        periodType = "day";
        period = 1;
        frequencyType = "minute";
        frequency = 5;
        break;
      case "15m":
        periodType = "day";
        period = 1;
        frequencyType = "minute";
        frequency = 15;
        break;
      case "1h":
        periodType = "day";
        period = 10;
        frequencyType = "minute";
        frequency = 60;
        break;
      case "1d":
        periodType = "year";
        period = 1;
        frequencyType = "daily";
        frequency = 1;
        break;
    }

    const data = await api<any>("/api/price-history", {
      method: "POST",
      body: JSON.stringify({
        symbol,
        periodType,
        period,
        frequencyType,
        frequency
      })
    });
    return convertToCandles(data);
  } catch (error) {
    console.error("Error fetching history:", error);
    return [];
  }
};

export const fetchWatchlist = async (): Promise<Quote[]> => {
  try {
    const symbols = ["AAPL", "MSFT", "SPY", "TSLA", "NVDA", "AMD"];
    const data = await api<any>("/api/quotes", {
      method: "POST",
      body: JSON.stringify({ symbols })
    });
    
    // Convert Schwab quotes to our format
    return symbols.map(symbol => {
      const schwabQuote = data[symbol];
      return convertToQuote(schwabQuote, symbol);
    });
  } catch (error) {
    console.error("Error fetching watchlist:", error);
    return [];
  }
};

// Note: Schwab API doesn't provide order book depth in the same way
// We'll use bid/ask from quotes
export const fetchOrderBook = async (symbol: string): Promise<OrderBookSnapshot> => {
  try {
    const data = await api<any>("/api/quotes", {
      method: "POST",
      body: JSON.stringify({ symbols: [symbol] })
    });
    
    const quote = data[symbol]?.quote || data[symbol];
    const bid = quote.bidPrice || 0;
    const ask = quote.askPrice || 0;
    const mid = (bid + ask) / 2;
    const spread = ask - bid;

    // Generate order book levels around bid/ask
    const bids = Array.from({ length: 10 }, (_, i) => ({
      price: Number((bid - i * 0.01).toFixed(2)),
      size: Math.floor(Math.random() * 500 + 100)
    }));

    const asks = Array.from({ length: 10 }, (_, i) => ({
      price: Number((ask + i * 0.01).toFixed(2)),
      size: Math.floor(Math.random() * 500 + 100)
    }));

    return {
      bids,
      asks,
      mid,
      spread,
      ts: Date.now()
    };
  } catch (error) {
    console.error("Error fetching order book:", error);
    throw error;
  }
};

// Trade tape - use recent trades if available
export const fetchTrades = async (symbol: string): Promise<TradePrint[]> => {
  try {
    // Schwab doesn't provide recent trades in the same format
    // Return empty for now, or generate from quote updates
    return [];
  } catch (error) {
    console.error("Error fetching trades:", error);
    return [];
  }
};

// These would need to be implemented with Schwab account API
export const fetchOrders = async (): Promise<Order[]> => {
  // TODO: Implement with Schwab orders API
  console.warn("Orders API not yet implemented with real Schwab API");
  return [];
};

export const submitOrder = async (order: OrderDraft): Promise<Order> => {
  // TODO: Implement order submission with Schwab API
  console.warn("Order submission not yet implemented with real Schwab API");
  throw new Error("Order submission not yet implemented");
};

export const fetchPositions = async (): Promise<Position[]> => {
  // TODO: Implement with Schwab account API
  console.warn("Positions API not yet implemented with real Schwab API");
  return [];
};

export const fetchAccount = async (): Promise<AccountSummary> => {
  // TODO: Implement with Schwab account API
  console.warn("Account API not yet implemented with real Schwab API");
  return {
    buyingPower: 0,
    cash: 0,
    equity: 0,
    maintenanceReq: 0
  };
};

export const fetchFills = async (): Promise<Fill[]> => {
  // TODO: Implement with Schwab account API
  console.warn("Fills API not yet implemented with real Schwab API");
  return [];
};

