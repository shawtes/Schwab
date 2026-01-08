"use client";

import { useState } from "react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList
} from "@/components/ui/command";
import { Timeframe } from "@/lib/types";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectSymbol: (symbol: string) => void;
  onSetTimeframe: (tf: Timeframe) => void;
  onSetSide: (side: "buy" | "sell") => void;
}

const SYMBOLS = ["AAPL", "MSFT", "SPY", "TSLA", "NVDA", "AMD", "GOOGL", "AMZN", "META"];
const TIMEFRAMES: Timeframe[] = ["1m", "5m", "15m", "1h", "1d"];

export function CommandPalette({
  open,
  onOpenChange,
  onSelectSymbol,
  onSetTimeframe,
  onSetSide
}: CommandPaletteProps) {
  const [search, setSearch] = useState("");

  const handleSelect = (callback: () => void) => {
    callback();
    onOpenChange(false);
    setSearch("");
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="Type a command or search..."
        value={search}
        onValueChange={setSearch}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Symbols">
          {SYMBOLS.filter((sym) =>
            sym.toLowerCase().includes(search.toLowerCase())
          ).map((sym) => (
            <CommandItem
              key={sym}
              onSelect={() => handleSelect(() => onSelectSymbol(sym))}
            >
              <span className="font-mono">{sym}</span>
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandGroup heading="Timeframe">
          {TIMEFRAMES.map((tf) => (
            <CommandItem
              key={tf}
              onSelect={() => handleSelect(() => onSetTimeframe(tf))}
            >
              Set timeframe to <span className="font-mono ml-1">{tf}</span>
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandGroup heading="Actions">
          <CommandItem onSelect={() => handleSelect(() => onSetSide("buy"))}>
            Set side to <span className="text-green-400 ml-1 font-semibold">BUY</span>
          </CommandItem>
          <CommandItem onSelect={() => handleSelect(() => onSetSide("sell"))}>
            Set side to <span className="text-red-400 ml-1 font-semibold">SELL</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}


