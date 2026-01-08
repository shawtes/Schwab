"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Position } from "@/lib/types";
import { cn } from "@/lib/utils";

interface PositionsProps {
  data: Position[] | undefined;
  isLoading?: boolean;
}

export function Positions({ data, isLoading }: PositionsProps) {
  if (isLoading) {
    return (
      <Card className="glass">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Positions</CardTitle>
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
          <CardTitle className="text-sm">Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            No open positions
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalPnL = data.reduce((sum, pos) => sum + pos.plOpen, 0);

  return (
    <Card className="glass">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Positions</CardTitle>
        <Badge
          variant={totalPnL >= 0 ? "success" : "destructive"}
          className="font-mono"
        >
          {totalPnL >= 0 ? "+" : ""}
          {totalPnL.toFixed(2)}
        </Badge>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead className="border-b border-border">
              <tr className="text-muted-foreground">
                <th className="text-left px-4 py-2 font-medium">Symbol</th>
                <th className="text-right px-4 py-2 font-medium">Qty</th>
                <th className="text-right px-4 py-2 font-medium">Avg Price</th>
                <th className="text-right px-4 py-2 font-medium">P&L Open</th>
                <th className="text-right px-4 py-2 font-medium">P&L Day</th>
              </tr>
            </thead>
            <tbody>
              {data.map((pos) => (
                <tr
                  key={pos.symbol}
                  className="border-b border-border/50 hover:bg-accent/30 transition-colors"
                >
                  <td className="px-4 py-2 font-mono font-semibold">
                    {pos.symbol}
                  </td>
                  <td
                    className={cn(
                      "text-right px-4 py-2 font-mono",
                      pos.qty > 0 ? "text-green-400" : "text-red-400"
                    )}
                  >
                    {pos.qty > 0 ? "+" : ""}
                    {pos.qty}
                  </td>
                  <td className="text-right px-4 py-2 font-mono text-muted-foreground">
                    {pos.avgPrice.toFixed(2)}
                  </td>
                  <td
                    className={cn(
                      "text-right px-4 py-2 font-mono font-semibold",
                      pos.plOpen >= 0 ? "text-green-400" : "text-red-400"
                    )}
                  >
                    {pos.plOpen >= 0 ? "+" : ""}
                    {pos.plOpen.toFixed(2)}
                  </td>
                  <td
                    className={cn(
                      "text-right px-4 py-2 font-mono",
                      pos.plDay >= 0 ? "text-green-400" : "text-red-400"
                    )}
                  >
                    {pos.plDay >= 0 ? "+" : ""}
                    {pos.plDay.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}


