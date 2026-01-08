"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Order } from "@/lib/types";
import { cn } from "@/lib/utils";

interface OrdersProps {
  data: Order[] | undefined;
  isLoading?: boolean;
}

function formatTime(ts: number) {
  return new Date(ts).toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit"
  });
}

function getStatusColor(status: string) {
  switch (status) {
    case "working":
      return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    case "filled":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "rejected":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    case "canceled":
      return "bg-gray-500/20 text-gray-400 border-gray-500/30";
    case "partial":
      return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    default:
      return "bg-gray-500/20 text-gray-400 border-gray-500/30";
  }
}

export function Orders({ data, isLoading }: OrdersProps) {
  if (isLoading) {
    return (
      <Card className="glass">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Orders</CardTitle>
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
          <CardTitle className="text-sm">Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            No orders yet
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Orders</CardTitle>
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
                <th className="text-left px-4 py-2 font-medium">Type</th>
                <th className="text-right px-4 py-2 font-medium">Price</th>
                <th className="text-left px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 20).map((order) => (
                <tr
                  key={order.id}
                  className="border-b border-border/50 hover:bg-accent/30 transition-colors"
                >
                  <td className="px-4 py-2 font-mono text-muted-foreground">
                    {formatTime(order.submittedAt)}
                  </td>
                  <td className="px-4 py-2 font-mono font-semibold">
                    {order.symbol}
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={cn(
                        "uppercase font-semibold",
                        order.side === "buy" ? "text-green-400" : "text-red-400"
                      )}
                    >
                      {order.side}
                    </span>
                  </td>
                  <td className="text-right px-4 py-2 font-mono">{order.qty}</td>
                  <td className="px-4 py-2 uppercase text-muted-foreground">
                    {order.type}
                  </td>
                  <td className="text-right px-4 py-2 font-mono">
                    {order.limitPrice ? order.limitPrice.toFixed(2) : "-"}
                  </td>
                  <td className="px-4 py-2">
                    <Badge className={getStatusColor(order.status)}>
                      {order.status}
                    </Badge>
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


