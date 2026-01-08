"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { OrderBookSnapshot } from "@/lib/types";
import { cn } from "@/lib/utils";

interface OrderBookProps {
  data: OrderBookSnapshot | undefined;
  isLoading?: boolean;
}

export function OrderBook({ data, isLoading }: OrderBookProps) {
  if (isLoading) {
    return (
      <Card className="glass h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Order Book</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="glass h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Order Book</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const maxSize = Math.max(
    ...data.asks.map((l) => l.size),
    ...data.bids.map((l) => l.size)
  );

  return (
    <Card className="glass h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Order Book</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        <div className="grid grid-cols-3 text-xs text-muted-foreground font-mono mb-2">
          <div className="text-right">Size</div>
          <div className="text-center">Price</div>
          <div className="text-left">Total</div>
        </div>

        {/* Asks (sells) - display in reverse */}
        <div className="space-y-0.5">
          {data.asks
            .slice(0, 8)
            .reverse()
            .map((level, idx) => {
              const widthPct = (level.size / maxSize) * 100;
              let cumulative = 0;
              for (let i = 0; i <= idx; i++) {
                cumulative += data.asks[data.asks.length - 1 - i].size;
              }
              return (
                <div
                  key={`ask-${idx}`}
                  className="relative grid grid-cols-3 text-xs font-mono h-5 items-center"
                >
                  <div
                    className="absolute inset-0 bg-red-500/10"
                    style={{ width: `${widthPct}%` }}
                  />
                  <div className="relative text-right pr-2">{level.size}</div>
                  <div className="relative text-center text-red-400">
                    {level.price.toFixed(2)}
                  </div>
                  <div className="relative text-left pl-2 text-muted-foreground">
                    {cumulative}
                  </div>
                </div>
              );
            })}
        </div>

        {/* Spread */}
        <div className="py-2 text-center">
          <div className="text-sm font-semibold text-primary">
            {data.mid.toFixed(2)}
          </div>
          <div className="text-xs text-muted-foreground">
            Spread: {data.spread.toFixed(2)}
          </div>
        </div>

        {/* Bids (buys) */}
        <div className="space-y-0.5">
          {data.bids.slice(0, 8).map((level, idx) => {
            const widthPct = (level.size / maxSize) * 100;
            let cumulative = 0;
            for (let i = 0; i <= idx; i++) {
              cumulative += data.bids[i].size;
            }
            return (
              <div
                key={`bid-${idx}`}
                className="relative grid grid-cols-3 text-xs font-mono h-5 items-center"
              >
                <div
                  className="absolute inset-0 bg-green-500/10"
                  style={{ width: `${widthPct}%` }}
                />
                <div className="relative text-right pr-2">{level.size}</div>
                <div className="relative text-center text-green-400">
                  {level.price.toFixed(2)}
                </div>
                <div className="relative text-left pl-2 text-muted-foreground">
                  {cumulative}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}


