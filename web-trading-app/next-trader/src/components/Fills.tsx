"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Fill } from "@/lib/types";
import { cn } from "@/lib/utils";

interface FillsProps {
  data: Fill[] | undefined;
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

export function Fills({ data, isLoading }: FillsProps) {
  if (isLoading) {
    return (
      <Card className="glass">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Fills</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="glass">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Fills</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            No fills yet
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Fills</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead className="border-b border-border">
              <tr className="text-muted-foreground">
                <th className="text-left px-4 py-2 font-medium">Time</th>
                <th className="text-left px-4 py-2 font-medium">Symbol</th>
                <th className="text-left px-4 py-2 font-medium">Side</th>
                <th className="text-right px-4 py-2 font-medium">Qty</th>
                <th className="text-right px-4 py-2 font-medium">Price</th>
                <th className="text-right px-4 py-2 font-medium">Total</th>
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 20).map((fill) => {
                const total = fill.qty * fill.price;
                return (
                  <tr
                    key={fill.id}
                    className="border-b border-border/50 hover:bg-accent/30 transition-colors"
                  >
                    <td className="px-4 py-2 font-mono text-muted-foreground">
                      {formatTime(fill.timestamp)}
                    </td>
                    <td className="px-4 py-2 font-mono font-semibold">
                      {fill.symbol}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={cn(
                          "uppercase font-semibold",
                          fill.side === "buy"
                            ? "text-green-400"
                            : "text-red-400"
                        )}
                      >
                        {fill.side}
                      </span>
                    </td>
                    <td className="text-right px-4 py-2 font-mono">
                      {fill.qty}
                    </td>
                    <td className="text-right px-4 py-2 font-mono">
                      {fill.price.toFixed(2)}
                    </td>
                    <td className="text-right px-4 py-2 font-mono font-semibold">
                      {total.toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}


