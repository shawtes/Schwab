"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Quote } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Search } from "lucide-react";

interface WatchlistProps {
  data: Quote[] | undefined;
  isLoading?: boolean;
  onSelectSymbol: (symbol: string) => void;
  currentSymbol: string;
}

export function Watchlist({
  data,
  isLoading,
  onSelectSymbol,
  currentSymbol
}: WatchlistProps) {
  const [search, setSearch] = useState("");

  if (isLoading) {
    return (
      <Card className="glass h-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Watchlist</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  const filteredData = data?.filter((quote) =>
    quote.symbol.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card className="glass h-full flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Watchlist</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col space-y-2 p-4">
        {/* Search input */}
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search symbols..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 h-9 text-sm"
          />
        </div>

        {/* Watchlist items */}
        <div className="flex-1 overflow-y-auto space-y-1">
          {!filteredData || filteredData.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              {search ? "No symbols found" : "No symbols in watchlist"}
            </div>
          ) : (
            filteredData.map((quote) => (
              <button
                key={quote.symbol}
                onClick={() => onSelectSymbol(quote.symbol)}
                className={cn(
                  "w-full p-2 rounded text-left hover:bg-accent/50 transition-colors border border-transparent",
                  currentSymbol === quote.symbol &&
                    "bg-accent border-primary/50"
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-mono font-semibold text-sm">
                      {quote.symbol}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Bid: {quote.bid.toFixed(2)} / Ask: {quote.ask.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-semibold text-sm">
                      {quote.last.toFixed(2)}
                    </div>
                    <div
                      className={cn(
                        "text-xs font-semibold",
                        quote.change >= 0 ? "text-green-400" : "text-red-400"
                      )}
                    >
                      {quote.change >= 0 ? "+" : ""}
                      {quote.change.toFixed(2)} ({quote.changePercent.toFixed(2)}%)
                    </div>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}


