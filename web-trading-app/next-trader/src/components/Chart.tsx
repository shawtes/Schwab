"use client";

import { useEffect, useRef, useState } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from "lightweight-charts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { Candle, Timeframe } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ChartProps {
  data: Candle[];
  symbol: string;
  currentPrice?: number;
  timeframe?: Timeframe;
  onTimeframeChange?: (tf: Timeframe) => void;
  onSymbolChange?: (symbol: string) => void;
  isRefetching?: boolean;
}

const timeframes: Timeframe[] = ["1m", "5m", "15m", "1h", "1d"];

function getRefreshText(timeframe: Timeframe): string {
  switch (timeframe) {
    case "1m": return "1s";
    case "5m": return "2s";
    case "15m": return "5s";
    case "1h": return "10s";
    case "1d": return "1m";
    default: return "2s";
  }
}

export function Chart({ data, symbol, currentPrice, timeframe = "1m", onTimeframeChange, onSymbolChange, isRefetching }: ChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const priceLineRef = useRef<any>(null);
  const previousDataLengthRef = useRef(0);
  
  // Track live candle state
  const [liveCandle, setLiveCandle] = useState<{
    time: number;
    open: number;
    high: number;
    low: number;
  } | null>(null);
  
  // Search state
  const [searchInput, setSearchInput] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Determine if we should show seconds based on timeframe
    const shouldShowSeconds = timeframe === "1m" || timeframe === "5m";
    const shouldShowTime = timeframe !== "1d";

    // Get the actual container dimensions
    const containerWidth = chartContainerRef.current.clientWidth;
    const containerHeight = chartContainerRef.current.clientHeight || chartContainerRef.current.parentElement?.clientHeight || 500;

    const chart = createChart(chartContainerRef.current, {
      width: containerWidth,
      height: containerHeight,
      layout: {
        background: { color: "#0a0e1a" },
        textColor: "#e5e7eb",
        fontSize: 12,
        fontFamily: "monospace"
      },
      grid: {
        vertLines: { 
          color: "#1f2937",
          visible: true
        },
        horzLines: { 
          color: "#1f2937",
          visible: true
        }
      },
      crosshair: {
        mode: 1,
        vertLine: {
          labelVisible: true
        },
        horzLine: {
          labelVisible: true
        }
      },
      rightPriceScale: {
        borderColor: "#374151",
        visible: true
      },
      timeScale: {
        borderColor: "#6b7280",
        timeVisible: true,
        secondsVisible: false,
        visible: true,
        borderVisible: true
      },
      handleScroll: {
        vertTouchDrag: false
      }
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: "#10b981",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#10b981",
      wickDownColor: "#ef4444"
    });

    chartRef.current = chart;
    seriesRef.current = candlestickSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        const containerWidth = chartContainerRef.current.clientWidth;
        const containerHeight = chartContainerRef.current.clientHeight || chartContainerRef.current.parentElement?.clientHeight || 500;
        
        chartRef.current.applyOptions({
          width: containerWidth,
          height: containerHeight
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [timeframe]);

  useEffect(() => {
    if (!seriesRef.current || data.length === 0) return;

    // Map historical candles
    const historicalData: CandlestickData<Time>[] = data.map((candle) => ({
      time: candle.time as Time,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close
    }));

    // Add live candle if we have current price
    if (currentPrice && data.length > 0) {
      const lastCandle = data[data.length - 1];
      
      // Calculate live candle time based on current real-world time
      const getLiveCandleTime = () => {
        const intervals: Record<string, number> = {
          "1m": 60,
          "5m": 300,
          "15m": 900,
          "1h": 3600,
          "1d": 86400
        };
        const interval = intervals[timeframe || "5m"] || 300;
        
        // Get current time in seconds (Unix timestamp)
        const now = Math.floor(Date.now() / 1000);
        
        // Round down to the start of the current candle period
        const currentCandleTime = Math.floor(now / interval) * interval;
        
        // Make sure we don't overlap with historical data
        // If current period is before or equal to last historical candle, use next period
        if (currentCandleTime <= lastCandle.time) {
          return lastCandle.time + interval;
        }
        
        return currentCandleTime;
      };
      
      const currentCandleTime = getLiveCandleTime();
      
      // Initialize or update live candle state
      if (!liveCandle || liveCandle.time !== currentCandleTime) {
        // New candle period started
        setLiveCandle({
          time: currentCandleTime,
          open: currentPrice,
          high: currentPrice,
          low: currentPrice
        });
      } else {
        // Update existing live candle
        setLiveCandle(prev => prev ? {
          ...prev,
          high: Math.max(prev.high, currentPrice),
          low: Math.min(prev.low, currentPrice)
        } : null);
      }
      
      // Add live candle to chart
      if (liveCandle) {
        const liveCandleData: CandlestickData<Time> = {
          time: liveCandle.time as Time,
          open: liveCandle.open,
          high: Math.max(liveCandle.high, currentPrice),
          low: Math.min(liveCandle.low, currentPrice),
          close: currentPrice
        };
        historicalData.push(liveCandleData);
      }
    }

    seriesRef.current.setData(historicalData);
    
    // Only fit content when data length changes (new candles) or symbol/timeframe changes
    // This allows user to zoom/pan without being reset
    if (data.length !== previousDataLengthRef.current) {
      chartRef.current?.timeScale().fitContent();
      previousDataLengthRef.current = data.length;
    }
  }, [data, currentPrice, timeframe, liveCandle]);

  const lastCandle = data[data.length - 1];
  const priceDiff = currentPrice && lastCandle ? currentPrice - lastCandle.close : 0;
  const priceDiffPercent = lastCandle && priceDiff ? ((priceDiff / lastCandle.close) * 100) : 0;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim() && onSymbolChange) {
      onSymbolChange(searchInput.trim().toUpperCase());
      setSearchInput("");
      setIsSearching(false);
    }
  };

  return (
    <Card className="glass flex flex-col h-full">
      <CardHeader className="pb-2 pt-3 px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {isSearching ? (
              <form onSubmit={handleSearch} className="flex items-center gap-2">
                <Input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Enter symbol (e.g., AAPL)"
                  className="h-8 w-48 font-mono text-sm"
                  autoFocus
                  onBlur={() => {
                    if (!searchInput) setIsSearching(false);
                  }}
                />
                <Button type="submit" size="sm" className="h-8 px-2">
                  Go
                </Button>
                <Button 
                  type="button" 
                  size="sm" 
                  variant="ghost" 
                  className="h-8 px-2"
                  onClick={() => {
                    setSearchInput("");
                    setIsSearching(false);
                  }}
                >
                  Cancel
                </Button>
              </form>
            ) : (
              <>
                <CardTitle className="text-lg font-mono">{symbol}</CardTitle>
                {onSymbolChange && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-7 px-2"
                    onClick={() => setIsSearching(true)}
                  >
                    <Search className="w-4 h-4" />
                  </Button>
                )}
              </>
            )}
            {!isSearching && currentPrice && lastCandle && (
              <div className="flex items-center gap-2 text-sm">
                <span className="font-mono font-bold">${currentPrice.toFixed(2)}</span>
                <span className={priceDiff >= 0 ? "text-green-400" : "text-red-400"}>
                  {priceDiff >= 0 ? "+" : ""}{priceDiff.toFixed(2)} ({priceDiffPercent.toFixed(2)}%)
                </span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              {timeframes.map((tf) => (
                <Button
                  key={tf}
                  variant={timeframe === tf ? "default" : "ghost"}
                  size="sm"
                  onClick={() => onTimeframeChange?.(tf)}
                  disabled={!onTimeframeChange}
                  className={cn(
                    "h-7 px-2 text-xs font-mono",
                    timeframe === tf && "bg-primary/20"
                  )}
                >
                  {tf}
                </Button>
              ))}
            </div>
            <Badge variant="outline" className="flex items-center gap-1">
              <span className={cn("h-2 w-2 rounded-full bg-green-500", isRefetching && "animate-pulse")} />
              <span className="text-xs">LIVE · {getRefreshText(timeframe)}</span>
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <div 
          ref={chartContainerRef} 
          style={{ width: '100%', height: '100%' }}
        />
      </CardContent>
    </Card>
  );
}

