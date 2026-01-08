"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { 
  Search, 
  TrendingUp, 
  TrendingDown,
  Play,
  Pause,
  Filter,
  RefreshCw,
  Star,
  Flame,
  Zap,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Plus
} from "lucide-react";

interface ScanFilters {
  minPercentChange: number;
  minRVOL: number;
  minPrice: number;
  maxPrice: number;
  minVolume: number;
  rsiMin: number;
  rsiMax: number;
}

interface MomentumStock {
  symbol: string;
  price: number;
  change: number;
  percentChange: number;
  volume: number;
  rvol: number;
  rsi: number;
  macd: number;
  score: number;
  trend: "strong" | "moderate" | "weak";
}

export function MomentumScanner() {
  const [isScanning, setIsScanning] = useState(false);
  const [autoScan, setAutoScan] = useState(false);
  const [showFilters, setShowFilters] = useState(true);
  const [lastScanTime, setLastScanTime] = useState<Date | null>(null);
  
  const [filters, setFilters] = useState<ScanFilters>({
    minPercentChange: 3,
    minRVOL: 1.5,
    minPrice: 5,
    maxPrice: 1000,
    minVolume: 1000000,
    rsiMin: 50,
    rsiMax: 80
  });

  const [results, setResults] = useState<MomentumStock[]>([]);

  const [sortBy, setSortBy] = useState<keyof MomentumStock>("score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const runScan = useCallback(async () => {
    setIsScanning(true);
    console.log("Starting momentum scan with filters:", filters);
    
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
      const url = `${API_BASE}/api/momentum-scan`;
      console.log("Fetching from:", url);
      
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filters })
      });
      
      console.log("Response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Received data:", data);
        console.log("Number of results:", data.results?.length);
        
        if (data.results && Array.isArray(data.results)) {
          setResults(data.results);
          setLastScanTime(new Date());
          console.log("✅ Results updated:", data.results.length, "stocks");
        } else {
          console.error("Invalid data format:", data);
          setResults([]);
        }
      } else {
        const errorText = await response.text();
        console.error("Momentum scan failed:", errorText);
        alert(`Scan failed: ${errorText}`);
      }
    } catch (error) {
      console.error("Error running momentum scan:", error);
      alert(`Error: ${error}`);
    } finally {
      setIsScanning(false);
    }
  }, [filters]);

  // Auto-scan on component mount
  useEffect(() => {
    runScan(); // Initial scan when component loads
  }, [runScan]);

  // Auto-scan interval when enabled
  useEffect(() => {
    if (autoScan) {
      const interval = setInterval(() => {
        runScan();
      }, 60000); // Scan every minute
      return () => clearInterval(interval);
    }
  }, [autoScan, runScan]);

  const sortResults = (key: keyof MomentumStock) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortOrder("desc");
    }
  };

  const sortedResults = [...results].sort((a, b) => {
    const aVal = a[sortBy];
    const bVal = b[sortBy];
    if (typeof aVal === "number" && typeof bVal === "number") {
      return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
    }
    return 0;
  });

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "strong": return <Flame className="w-4 h-4 text-orange-500" />;
      case "moderate": return <Zap className="w-4 h-4 text-yellow-500" />;
      default: return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getMomentumColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-gray-400";
  };

  const formatVolume = (vol: number) => {
    if (vol >= 1000000) return `${(vol / 1000000).toFixed(1)}M`;
    if (vol >= 1000) return `${(vol / 1000).toFixed(1)}K`;
    return vol.toString();
  };

  return (
    <div className="h-full flex flex-col gap-2 p-2 overflow-hidden">
      {/* Header Controls */}
      <Card className="glass shrink-0">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Search className="w-5 h-5" />
              Momentum Scanner
            </CardTitle>
            <div className="flex items-center gap-2">
              {lastScanTime && (
                <span className="text-xs text-muted-foreground">
                  Last scan: {lastScanTime.toLocaleTimeString()}
                </span>
              )}
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="w-4 h-4 mr-1" />
                Filters
              </Button>
              <Button
                size="sm"
                onClick={runScan}
                disabled={isScanning}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isScanning ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                    Scanning...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4 mr-1" />
                    Scan Now
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>

        {/* Filters Panel */}
        {showFilters && (
          <CardContent className="border-t">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
              <div className="space-y-2">
                <Label className="text-xs">Min % Change</Label>
                <Input
                  type="number"
                  value={filters.minPercentChange}
                  onChange={(e) => setFilters({ ...filters, minPercentChange: parseFloat(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Min RVOL</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={filters.minRVOL}
                  onChange={(e) => setFilters({ ...filters, minRVOL: parseFloat(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Min Price ($)</Label>
                <Input
                  type="number"
                  value={filters.minPrice}
                  onChange={(e) => setFilters({ ...filters, minPrice: parseFloat(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Max Price ($)</Label>
                <Input
                  type="number"
                  value={filters.maxPrice}
                  onChange={(e) => setFilters({ ...filters, maxPrice: parseFloat(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Min Volume</Label>
                <Input
                  type="number"
                  value={filters.minVolume}
                  onChange={(e) => setFilters({ ...filters, minVolume: parseInt(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">RSI Min</Label>
                <Input
                  type="number"
                  value={filters.rsiMin}
                  onChange={(e) => setFilters({ ...filters, rsiMin: parseInt(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">RSI Max</Label>
                <Input
                  type="number"
                  value={filters.rsiMax}
                  onChange={(e) => setFilters({ ...filters, rsiMax: parseInt(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Auto Scan</Label>
                <div className="flex items-center gap-2 h-8">
                  <Switch
                    checked={autoScan}
                    onCheckedChange={setAutoScan}
                  />
                  <span className="text-xs text-muted-foreground">
                    {autoScan ? "Every 1min" : "Off"}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Results Table */}
      <Card className="glass flex-1 min-h-0 overflow-hidden flex flex-col">
        <CardHeader className="pb-2 pt-3 px-4 shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">
              Scan Results ({sortedResults.length})
            </CardTitle>
            <div className="flex gap-2">
              <Badge variant="outline" className="text-xs">
                <TrendingUp className="w-3 h-3 mr-1" />
                Strong: {sortedResults.filter(s => s.trend === "strong").length}
              </Badge>
              <Badge variant="outline" className="text-xs">
                <Activity className="w-3 h-3 mr-1" />
                Moderate: {sortedResults.filter(s => s.trend === "moderate").length}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex-1 min-h-0 overflow-auto p-0">
          {isScanning ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <p className="text-sm text-muted-foreground">Scanning all available stocks...</p>
              <p className="text-xs text-muted-foreground">Fetching data from Schwab API...</p>
            </div>
          ) : sortedResults.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 gap-3 text-muted-foreground">
              <Search className="w-12 h-12 opacity-50" />
              <p className="text-sm font-medium">No results found</p>
              <p className="text-xs">Try adjusting your filters or click "Scan Now"</p>
              <p className="text-xs mt-2 opacity-50">Debug: results={results.length}, sorted={sortedResults.length}</p>
            </div>
          ) : (
            <div className="w-full h-full overflow-auto">
              {/* Debug info */}
              <div className="px-4 py-2 text-xs text-muted-foreground border-b bg-accent/20">
                Displaying {sortedResults.length} stocks (Table rendered: {sortedResults.length > 0 ? "✓" : "✗"})
              </div>
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-card border-b z-10">
                  <tr className="text-xs text-muted-foreground">
                    <th className="p-3 text-left font-medium">Trend</th>
                    <th 
                      className="p-3 text-left font-medium cursor-pointer hover:text-foreground"
                      onClick={() => sortResults("symbol")}
                    >
                      Symbol {sortBy === "symbol" && (sortOrder === "asc" ? "↑" : "↓")}
                    </th>
                  <th 
                    className="p-3 text-right font-medium cursor-pointer hover:text-foreground"
                    onClick={() => sortResults("price")}
                  >
                    Price {sortBy === "price" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th 
                    className="p-3 text-right font-medium cursor-pointer hover:text-foreground"
                    onClick={() => sortResults("percentChange")}
                  >
                    Change {sortBy === "percentChange" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th 
                    className="p-3 text-right font-medium cursor-pointer hover:text-foreground"
                    onClick={() => sortResults("volume")}
                  >
                    Volume {sortBy === "volume" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th 
                    className="p-3 text-right font-medium cursor-pointer hover:text-foreground"
                    onClick={() => sortResults("rvol")}
                  >
                    RVOL {sortBy === "rvol" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th 
                    className="p-3 text-right font-medium cursor-pointer hover:text-foreground"
                    onClick={() => sortResults("rsi")}
                  >
                    RSI {sortBy === "rsi" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th 
                    className="p-3 text-right font-medium cursor-pointer hover:text-foreground"
                    onClick={() => sortResults("score")}
                  >
                    Score {sortBy === "score" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="p-3 text-center font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedResults.map((stock, idx) => (
                  <tr 
                    key={stock.symbol}
                    className="border-b border-border/50 hover:bg-accent/50 transition-colors"
                  >
                    <td className="p-3">
                      {getTrendIcon(stock.trend)}
                    </td>
                    <td className="p-3">
                      <div className="font-semibold">{stock.symbol}</div>
                    </td>
                    <td className="p-3 text-right font-mono">
                      ${stock.price.toFixed(2)}
                    </td>
                    <td className="p-3 text-right">
                      <div className={stock.change >= 0 ? "text-green-400" : "text-red-400"}>
                        <div className="flex items-center justify-end gap-1">
                          {stock.change >= 0 ? (
                            <ArrowUpRight className="w-3 h-3" />
                          ) : (
                            <ArrowDownRight className="w-3 h-3" />
                          )}
                          <span className="font-mono">
                            {stock.change >= 0 ? "+" : ""}{stock.change.toFixed(2)}
                          </span>
                        </div>
                        <div className="text-xs">
                          {stock.change >= 0 ? "+" : ""}{stock.percentChange.toFixed(2)}%
                        </div>
                      </div>
                    </td>
                    <td className="p-3 text-right font-mono text-sm">
                      {formatVolume(stock.volume)}
                    </td>
                    <td className="p-3 text-right">
                      <Badge 
                        variant="outline" 
                        className={`font-mono ${stock.rvol >= 2.5 ? "text-green-400" : stock.rvol >= 1.8 ? "text-yellow-400" : ""}`}
                      >
                        {stock.rvol.toFixed(1)}x
                      </Badge>
                    </td>
                    <td className="p-3 text-right font-mono text-sm">
                      {stock.rsi}
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden max-w-[60px]">
                          <div 
                            className={`h-full ${
                              stock.score >= 80 ? "bg-green-500" :
                              stock.score >= 60 ? "bg-yellow-500" : "bg-gray-500"
                            }`}
                            style={{ width: `${stock.score}%` }}
                          />
                        </div>
                        <span className={`font-mono text-sm font-bold ${getMomentumColor(stock.score)}`}>
                          {stock.score}
                        </span>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex items-center justify-center gap-1">
                        <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                          <Star className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                          <Plus className="w-3 h-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

