import { useEffect, useMemo, useState } from "react";
import { connectMarketSocket, StreamCallbacks } from "./ws-client";
import { OrderBookSnapshot, Quote, TradePrint } from "./types";
import { useConnectionStore } from "./state";

type StreamState = {
  quote?: Quote;
  trade?: TradePrint;
  orderBook?: OrderBookSnapshot;
};

export function useMarketStream(symbol: string) {
  const [state, setState] = useState<StreamState>({});
  const { setStatus, setHeartbeat, setError } = useConnectionStore();

  const callbacks = useMemo<StreamCallbacks>(
    () => ({
      onQuote: (quote) => setState((prev) => ({ ...prev, quote })),
      onTrade: (trade) => setState((prev) => ({ ...prev, trade })),
      onOrderBook: (orderBook) => setState((prev) => ({ ...prev, orderBook })),
      onStatus: (status) => {
        setStatus(status);
        if (status === "open") setHeartbeat(Date.now());
        if (status === "error") setError("WebSocket error");
      }
    }),
    [setError, setHeartbeat, setStatus]
  );

  useEffect(() => {
    const disconnect = connectMarketSocket([symbol], callbacks);
    return () => disconnect?.();
  }, [callbacks, symbol]);

  return state;
}


