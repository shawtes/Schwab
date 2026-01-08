import { ConnectionState, OrderBookSnapshot, Quote, TradePrint } from "./types";

export type StreamCallbacks = {
  onQuote?: (quote: Quote) => void;
  onTrade?: (trade: TradePrint) => void;
  onOrderBook?: (book: OrderBookSnapshot) => void;
  onStatus?: (state: ConnectionState) => void;
};

// Connect to Schwab streaming server (port 8765)
const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8765";

export function connectMarketSocket(symbols: string[], callbacks: StreamCallbacks) {
  let socket: WebSocket | undefined;
  let retry = 0;
  let closedByUser = false;

  const connect = () => {
    callbacks.onStatus?.("connecting");
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      retry = 0;
      callbacks.onStatus?.("open");
      socket?.send(JSON.stringify({ type: "subscribe", symbols }));
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "quote") {
          // Schwab stream sends quote directly, not wrapped in payload
          const quote: Quote = {
            symbol: data.symbol,
            last: data.last || 0,
            change: data.change || 0,
            changePercent: data.changePercent || 0,
            bid: data.bid || 0,
            ask: data.ask || 0,
            timestamp: data.timestamp || Date.now()
          };
          callbacks.onQuote?.(quote);
        }
        if (data.type === "trade") callbacks.onTrade?.(data.payload as TradePrint);
        if (data.type === "orderbook") callbacks.onOrderBook?.(data.payload as OrderBookSnapshot);
        if (data.type === "candle") {
          // Real-time candle updates from Schwab
          console.log("Real-time candle update:", data);
        }
      } catch (error) {
        console.error("WS parse error", error);
      }
    };

    socket.onerror = () => {
      callbacks.onStatus?.("error");
    };

    socket.onclose = () => {
      callbacks.onStatus?.(closedByUser ? "closed" : "reconnecting");
      if (!closedByUser) {
        retry += 1;
        const backoff = Math.min(5000, 500 * retry);
        setTimeout(connect, backoff);
      }
    };
  };

  connect();

  return () => {
    closedByUser = true;
    socket?.close();
  };
}

