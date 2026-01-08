"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Chart } from "@/components/Chart";
import { OrderBook } from "@/components/OrderBook";
import { TradesTape } from "@/components/TradesTape";
import { OrderTicket } from "@/components/OrderTicket";
import { Positions } from "@/components/Positions";
import { Orders } from "@/components/Orders";
import { Fills } from "@/components/Fills";
import { Watchlist } from "@/components/Watchlist";
import { TopBar } from "@/components/TopBar";
import { CommandPalette } from "@/components/CommandPalette";
import { useUiStore, useConnectionStore } from "@/lib/state";
import { useHotkeys } from "@/lib/hotkeys";
import { connectMarketSocket } from "@/lib/ws-client";
import {
  fetchHistory,
  fetchWatchlist,
  fetchOrderBook,
  fetchTrades,
  fetchOrders,
  fetchPositions,
  fetchAccount,
  fetchFills
} from "@/lib/api";
import { OrderBookSnapshot, Quote, TradePrint } from "@/lib/types";

export default function TradingPage() {
  const {
    symbol,
    timeframe,
    commandPaletteOpen,
    setSymbol,
    setTimeframe,
    setSide,
    toggleCommandPalette
  } = useUiStore();

  const { status, setStatus } = useConnectionStore();

  const [realtimeQuote, setRealtimeQuote] = useState<Quote | undefined>();
  const [realtimeOrderBook, setRealtimeOrderBook] = useState<
    OrderBookSnapshot | undefined
  >();
  const [realtimeTrades, setRealtimeTrades] = useState<TradePrint[]>([]);

  // Queries
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ["history", symbol],
    queryFn: () => fetchHistory(symbol),
    refetchInterval: 30000
  });

  const { data: watchlistData, isLoading: watchlistLoading } = useQuery({
    queryKey: ["watchlist"],
    queryFn: fetchWatchlist,
    refetchInterval: 5000
  });

  const { data: orderBookData, isLoading: orderBookLoading } = useQuery({
    queryKey: ["orderbook", symbol],
    queryFn: () => fetchOrderBook(symbol),
    refetchInterval: false
  });

  const { data: tradesData, isLoading: tradesLoading } = useQuery({
    queryKey: ["trades", symbol],
    queryFn: () => fetchTrades(symbol),
    refetchInterval: false
  });

  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: fetchOrders,
    refetchInterval: 2000
  });

  const { data: positionsData, isLoading: positionsLoading } = useQuery({
    queryKey: ["positions"],
    queryFn: fetchPositions,
    refetchInterval: 2000
  });

  const { data: accountData } = useQuery({
    queryKey: ["account"],
    queryFn: fetchAccount,
    refetchInterval: 5000
  });

  const { data: fillsData, isLoading: fillsLoading } = useQuery({
    queryKey: ["fills"],
    queryFn: fetchFills,
    refetchInterval: 2000
  });

  // WebSocket connection
  useEffect(() => {
    const disconnect = connectMarketSocket([symbol], {
      onQuote: (quote) => {
        if (quote.symbol === symbol) {
          setRealtimeQuote(quote);
        }
      },
      onOrderBook: (book) => {
        setRealtimeOrderBook(book);
      },
      onTrade: (trade) => {
        setRealtimeTrades((prev) => [trade, ...prev].slice(0, 50));
      },
      onStatus: (state) => {
        setStatus(state);
      }
    });

    return disconnect;
  }, [symbol, setStatus]);

  // Keyboard shortcuts
  useHotkeys({
    b: () => setSide("buy"),
    s: () => setSide("sell"),
    escape: () => toggleCommandPalette(false),
    "cmd+k": () => toggleCommandPalette()
  });

  const currentPrice = realtimeQuote?.last ?? realtimeOrderBook?.mid;
  const displayOrderBook = realtimeOrderBook ?? orderBookData;
  const displayTrades =
    realtimeTrades.length > 0 ? realtimeTrades : tradesData ?? [];

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Top Bar */}
      <TopBar
        symbol={symbol}
        timeframe={timeframe}
        connectionStatus={status}
        onTimeframeChange={setTimeframe}
        onOpenCommandPalette={() => toggleCommandPalette(true)}
      />

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Watchlist */}
        <div className="w-64 border-r border-border overflow-y-auto p-2">
          <Watchlist
            data={watchlistData}
            isLoading={watchlistLoading}
            onSelectSymbol={setSymbol}
            currentSymbol={symbol}
          />
        </div>

        {/* Center - Chart + Bottom Tabs */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chart Area */}
          <div className="h-[60%] p-2">
            {historyLoading ? (
              <div className="glass h-full flex items-center justify-center">
                <p className="text-muted-foreground">Loading chart...</p>
              </div>
            ) : historyData && historyData.length > 0 ? (
              <Chart data={historyData} symbol={symbol} />
            ) : (
              <div className="glass h-full flex items-center justify-center">
                <p className="text-muted-foreground">No chart data available</p>
              </div>
            )}
          </div>

          {/* Bottom Tabs */}
          <div className="flex-1 border-t border-border overflow-hidden">
            <Tabs defaultValue="positions" className="h-full flex flex-col">
              <TabsList className="w-full justify-start px-4">
                <TabsTrigger value="positions">Positions</TabsTrigger>
                <TabsTrigger value="orders">Orders</TabsTrigger>
                <TabsTrigger value="fills">Fills</TabsTrigger>
                <TabsTrigger value="account">Account</TabsTrigger>
              </TabsList>
              <div className="flex-1 overflow-auto p-2">
                <TabsContent value="positions" className="mt-0 h-full">
                  <Positions data={positionsData} isLoading={positionsLoading} />
                </TabsContent>
                <TabsContent value="orders" className="mt-0 h-full">
                  <Orders data={ordersData} isLoading={ordersLoading} />
                </TabsContent>
                <TabsContent value="fills" className="mt-0 h-full">
                  <Fills data={fillsData} isLoading={fillsLoading} />
                </TabsContent>
                <TabsContent value="account" className="mt-0 h-full">
                  {accountData && (
                    <div className="glass p-6 space-y-4">
                      <h3 className="text-lg font-semibold">Account Summary</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Equity
                          </p>
                          <p className="text-2xl font-bold font-mono">
                            ${accountData.equity.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Buying Power
                          </p>
                          <p className="text-2xl font-bold font-mono">
                            ${accountData.buyingPower.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Cash
                          </p>
                          <p className="text-lg font-mono">
                            ${accountData.cash.toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Maintenance Req
                          </p>
                          <p className="text-lg font-mono">
                            ${accountData.maintenanceReq.toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </div>

        {/* Right Sidebar - Order Book, Trades, Order Ticket */}
        <div className="w-80 border-l border-border flex flex-col overflow-hidden">
          <div className="h-[35%] border-b border-border overflow-y-auto p-2">
            <OrderBook data={displayOrderBook} isLoading={orderBookLoading} />
          </div>
          <div className="h-[35%] border-b border-border overflow-y-auto p-2">
            <TradesTape data={displayTrades} isLoading={tradesLoading} />
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <OrderTicket symbol={symbol} currentPrice={currentPrice} />
          </div>
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette
        open={commandPaletteOpen}
        onOpenChange={toggleCommandPalette}
        onSelectSymbol={setSymbol}
        onSetTimeframe={setTimeframe}
        onSetSide={setSide}
      />
    </div>
  );
}


