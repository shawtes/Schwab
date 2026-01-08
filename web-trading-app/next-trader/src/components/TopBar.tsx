"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConnectionState, Timeframe } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Activity, Wifi, WifiOff } from "lucide-react";

export type MainView = "trading" | "scanner" | "ml-trader";

interface TopBarProps {
  symbol: string;
  connectionStatus: ConnectionState;
  currentView: MainView;
  onViewChange: (view: MainView) => void;
  onOpenCommandPalette: () => void;
}

function getConnectionBadge(status: ConnectionState) {
  switch (status) {
    case "open":
      return (
        <Badge variant="success" className="flex items-center gap-1">
          <Wifi className="h-3 w-3" />
          Connected
        </Badge>
      );
    case "connecting":
    case "reconnecting":
      return (
        <Badge variant="secondary" className="flex items-center gap-1">
          <Activity className="h-3 w-3 animate-pulse" />
          {status === "reconnecting" ? "Reconnecting" : "Connecting"}
        </Badge>
      );
    case "closed":
    case "error":
      return (
        <Badge variant="destructive" className="flex items-center gap-1">
          <WifiOff className="h-3 w-3" />
          {status === "error" ? "Error" : "Disconnected"}
        </Badge>
      );
  }
}

export function TopBar({
  symbol,
  connectionStatus,
  currentView,
  onViewChange,
  onOpenCommandPalette
}: TopBarProps) {
  return (
    <div className="glass border-b border-border">
      <div className="px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold font-mono">{symbol}</h1>
          <span className="text-sm text-muted-foreground">Schwab Pro Trading Platform</span>
        </div>

        <div className="flex items-center gap-3">
          {getConnectionBadge(connectionStatus)}
          <Button
            variant="outline"
            size="sm"
            onClick={onOpenCommandPalette}
            className="h-7 text-xs"
          >
            <span className="text-muted-foreground mr-1">⌘K</span>
            Commands
          </Button>
        </div>
      </div>
      
      {/* Main Navigation Tabs */}
      <div className="flex border-t border-border/50">
        <button
          onClick={() => onViewChange("trading")}
          className={cn(
            "px-6 py-2 text-sm font-medium transition-colors relative",
            currentView === "trading"
              ? "text-foreground bg-accent/50"
              : "text-muted-foreground hover:text-foreground hover:bg-accent/20"
          )}
        >
          📊 Trading
          {currentView === "trading" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>
        <button
          onClick={() => onViewChange("scanner")}
          className={cn(
            "px-6 py-2 text-sm font-medium transition-colors relative",
            currentView === "scanner"
              ? "text-foreground bg-accent/50"
              : "text-muted-foreground hover:text-foreground hover:bg-accent/20"
          )}
        >
          🔍 Momentum Scanner
          {currentView === "scanner" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>
        <button
          onClick={() => onViewChange("ml-trader")}
          className={cn(
            "px-6 py-2 text-sm font-medium transition-colors relative",
            currentView === "ml-trader"
              ? "text-foreground bg-accent/50"
              : "text-muted-foreground hover:text-foreground hover:bg-accent/20"
          )}
        >
          🤖 ML Auto Trader
          {currentView === "ml-trader" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>
      </div>
    </div>
  );
}

