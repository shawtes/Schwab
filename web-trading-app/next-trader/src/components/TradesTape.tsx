"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TradePrint } from "@/lib/types";
import { cn } from "@/lib/utils";

interface TradesTapeProps {
  data: TradePrint[] | undefined;
  isLoading?: boolean;
}

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

export function TradesTape({ data, isLoading }: TradesTapeProps) {
  if (isLoading) {
    return (
      <Card className="glass h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="glass h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            No trades yet
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Trades</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="grid grid-cols-4 text-xs text-muted-foreground font-mono px-4 py-2 border-b border-border">
          <div>Time</div>
          <div className="text-right">Price</div>
          <div className="text-right">Size</div>
          <div className="text-right">Side</div>
        </div>
        <div className="max-h-96 overflow-y-auto">
          {data.slice(0, 30).map((trade, idx) => (
            <div
              key={`${trade.ts}-${idx}`}
              className="grid grid-cols-4 text-xs font-mono px-4 py-1.5 hover:bg-accent/50 transition-colors"
            >
              <div className="text-muted-foreground">{formatTime(trade.ts)}</div>
              <div
                className={cn(
                  "text-right font-semibold",
                  trade.side === "buy" ? "text-green-400" : "text-red-400"
                )}
              >
                {trade.price.toFixed(2)}
              </div>
              <div className="text-right">{trade.size}</div>
              <div
                className={cn(
                  "text-right uppercase text-xs",
                  trade.side === "buy" ? "text-green-400" : "text-red-400"
                )}
              >
                {trade.side}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}


