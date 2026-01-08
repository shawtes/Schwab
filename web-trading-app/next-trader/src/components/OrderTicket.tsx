"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { submitOrder } from "@/lib/api";
import { validateOrder } from "@/lib/validation";
import { OrderType, Side } from "@/lib/types";
import { cn } from "@/lib/utils";

interface OrderTicketProps {
  symbol: string;
  currentPrice?: number;
}

export function OrderTicket({ symbol, currentPrice }: OrderTicketProps) {
  const [side, setSide] = useState<Side>("buy");
  const [type, setType] = useState<OrderType>("market");
  const [qty, setQty] = useState<string>("100");
  const [limitPrice, setLimitPrice] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: submitOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      queryClient.invalidateQueries({ queryKey: ["positions"] });
      queryClient.invalidateQueries({ queryKey: ["fills"] });
      setQty("100");
      setLimitPrice("");
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    }
  });

  const handleSubmit = () => {
    const qtyNum = parseFloat(qty);
    const limitPriceNum = limitPrice ? parseFloat(limitPrice) : undefined;

    const order = {
      symbol,
      qty: qtyNum,
      side,
      type,
      limitPrice: type === "limit" ? limitPriceNum : undefined
    };

    const result = validateOrder(order);
    if (!result.ok) {
      setError(result.reason);
      return;
    }

    setError(null);
    mutation.mutate(order);
  };

  return (
    <Card className="glass h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <span>Order Ticket</span>
          {currentPrice && (
            <Badge variant="outline" className="font-mono">
              {currentPrice.toFixed(2)}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Symbol */}
        <div>
          <label className="text-xs text-muted-foreground mb-1 block">
            Symbol
          </label>
          <Input value={symbol} disabled className="font-mono" />
        </div>

        {/* Side selector */}
        <div>
          <label className="text-xs text-muted-foreground mb-2 block">Side</label>
          <div className="grid grid-cols-2 gap-2">
            <Button
              onClick={() => setSide("buy")}
              variant={side === "buy" ? "default" : "outline"}
              className={cn(
                "h-10",
                side === "buy" && "bg-green-600 hover:bg-green-700"
              )}
            >
              Buy
            </Button>
            <Button
              onClick={() => setSide("sell")}
              variant={side === "sell" ? "default" : "outline"}
              className={cn(
                "h-10",
                side === "sell" && "bg-red-600 hover:bg-red-700"
              )}
            >
              Sell
            </Button>
          </div>
        </div>

        {/* Order type */}
        <div>
          <label className="text-xs text-muted-foreground mb-2 block">
            Order Type
          </label>
          <div className="grid grid-cols-2 gap-2">
            <Button
              onClick={() => setType("market")}
              variant={type === "market" ? "default" : "outline"}
              size="sm"
            >
              Market
            </Button>
            <Button
              onClick={() => setType("limit")}
              variant={type === "limit" ? "default" : "outline"}
              size="sm"
            >
              Limit
            </Button>
          </div>
        </div>

        {/* Quantity */}
        <div>
          <label className="text-xs text-muted-foreground mb-1 block">
            Quantity
          </label>
          <Input
            type="number"
            value={qty}
            onChange={(e) => setQty(e.target.value)}
            placeholder="100"
            className="font-mono"
          />
        </div>

        {/* Limit Price (conditional) */}
        {type === "limit" && (
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">
              Limit Price
            </label>
            <Input
              type="number"
              step="0.01"
              value={limitPrice}
              onChange={(e) => setLimitPrice(e.target.value)}
              placeholder={currentPrice?.toFixed(2) ?? "0.00"}
              className="font-mono"
            />
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded p-2">
            {error}
          </div>
        )}

        {/* Submit button */}
        <Button
          onClick={handleSubmit}
          disabled={mutation.isPending}
          className={cn(
            "w-full h-11 font-semibold",
            side === "buy"
              ? "bg-green-600 hover:bg-green-700"
              : "bg-red-600 hover:bg-red-700"
          )}
        >
          {mutation.isPending
            ? "Submitting..."
            : `${side === "buy" ? "Buy" : "Sell"} ${symbol}`}
        </Button>
      </CardContent>
    </Card>
  );
}


