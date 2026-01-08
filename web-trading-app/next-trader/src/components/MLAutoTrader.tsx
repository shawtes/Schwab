"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { 
  Play, 
  Pause, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  DollarSign,
  Target,
  AlertCircle
} from "lucide-react";

interface MLAutoTraderProps {
  symbol: string;
}

interface TradeSignal {
  symbol: string;
  action: "BUY" | "SELL" | "HOLD";
  confidence: number;
  price: number;
  timestamp: string;
}

interface ModelStats {
  accuracy: number;
  totalTrades: number;
  winRate: number;
  profitLoss: number;
}

export function MLAutoTrader({ symbol }: MLAutoTraderProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [autoExecute, setAutoExecute] = useState(false);
  const [maxPosition, setMaxPosition] = useState("1000");
  const [riskLevel, setRiskLevel] = useState("medium");
  const [currentSignal, setCurrentSignal] = useState<TradeSignal | null>(null);
  const [recentSignals, setRecentSignals] = useState<TradeSignal[]>([]);
  const [modelStats, setModelStats] = useState<ModelStats>({
    accuracy: 0.73,
    totalTrades: 0,
    winRate: 0,
    profitLoss: 0
  });

  const toggleTrading = async () => {
    if (!isRunning) {
      // Start ML trading
      setIsRunning(true);
      // TODO: Call backend to start ML model
      console.log("Starting ML Auto Trading for", symbol);
    } else {
      // Stop ML trading
      setIsRunning(false);
      // TODO: Call backend to stop ML model
      console.log("Stopping ML Auto Trading");
    }
  };

  const getSignalColor = (action: string) => {
    switch (action) {
      case "BUY": return "text-green-400 bg-green-500/10";
      case "SELL": return "text-red-400 bg-red-500/10";
      default: return "text-gray-400 bg-gray-500/10";
    }
  };

  const getSignalIcon = (action: string) => {
    switch (action) {
      case "BUY": return <TrendingUp className="w-4 h-4" />;
      case "SELL": return <TrendingDown className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full flex flex-col gap-4 p-4">
      {/* Control Panel */}
      <Card className="glass">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="w-5 h-5" />
            ML Auto Trading Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Main Controls */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-sm font-medium">Trading Status</Label>
              <p className="text-xs text-muted-foreground">
                {isRunning ? "Model is actively analyzing markets" : "Model is stopped"}
              </p>
            </div>
            <Button 
              onClick={toggleTrading}
              size="lg"
              className={isRunning ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}
            >
              {isRunning ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  Stop Trading
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start Trading
                </>
              )}
            </Button>
          </div>

          {/* Settings Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
            <div className="space-y-2">
              <Label htmlFor="auto-execute" className="text-sm">Auto Execute Trades</Label>
              <div className="flex items-center gap-2">
                <Switch 
                  id="auto-execute"
                  checked={autoExecute}
                  onCheckedChange={setAutoExecute}
                  disabled={!isRunning}
                />
                <span className="text-xs text-muted-foreground">
                  {autoExecute ? "Enabled" : "Manual approval required"}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-position" className="text-sm">Max Position Size ($)</Label>
              <Input
                id="max-position"
                type="number"
                value={maxPosition}
                onChange={(e) => setMaxPosition(e.target.value)}
                className="font-mono"
                disabled={!isRunning}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="risk-level" className="text-sm">Risk Level</Label>
              <select
                id="risk-level"
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                className="w-full h-10 px-3 rounded-md border bg-background text-sm"
                disabled={!isRunning}
              >
                <option value="low">Low (Conservative)</option>
                <option value="medium">Medium (Balanced)</option>
                <option value="high">High (Aggressive)</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats and Signal Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Model Performance Stats */}
        <Card className="glass">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Model Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Accuracy</p>
                <p className="text-2xl font-bold font-mono text-blue-400">
                  {(modelStats.accuracy * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Win Rate</p>
                <p className="text-2xl font-bold font-mono text-green-400">
                  {(modelStats.winRate * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Total Trades</p>
                <p className="text-2xl font-bold font-mono">
                  {modelStats.totalTrades}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">P&L Today</p>
                <p className={`text-2xl font-bold font-mono ${modelStats.profitLoss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {modelStats.profitLoss >= 0 ? '+' : ''}{modelStats.profitLoss.toFixed(2)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Current Signal */}
        <Card className="glass">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Current Signal</CardTitle>
          </CardHeader>
          <CardContent>
            {currentSignal ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge className={`${getSignalColor(currentSignal.action)} text-base px-3 py-1`}>
                    {getSignalIcon(currentSignal.action)}
                    <span className="ml-2">{currentSignal.action}</span>
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {new Date(currentSignal.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Confidence</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-blue-500 to-green-500"
                          style={{ width: `${currentSignal.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-mono">
                        {(currentSignal.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Target Price</p>
                    <p className="text-lg font-mono font-bold">
                      ${currentSignal.price.toFixed(2)}
                    </p>
                  </div>
                </div>

                {!autoExecute && currentSignal.action !== "HOLD" && (
                  <div className="flex gap-2 pt-2">
                    <Button size="sm" className="flex-1 bg-green-600 hover:bg-green-700">
                      <Target className="w-3 h-3 mr-1" />
                      Execute Trade
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      Reject
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <AlertCircle className="w-8 h-8 mb-2" />
                <p className="text-sm">No active signal</p>
                <p className="text-xs">Start trading to receive ML predictions</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Signals */}
      <Card className="glass flex-1 overflow-hidden flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Recent Signals</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-auto">
          {recentSignals.length > 0 ? (
            <div className="space-y-2">
              {recentSignals.map((signal, idx) => (
                <div 
                  key={idx}
                  className="flex items-center justify-between p-3 rounded-lg border border-border/50 hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Badge className={`${getSignalColor(signal.action)} text-xs`}>
                      {signal.action}
                    </Badge>
                    <div>
                      <p className="text-sm font-medium">{signal.symbol}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(signal.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-mono">${signal.price.toFixed(2)}</p>
                    <p className="text-xs text-muted-foreground">
                      {(signal.confidence * 100).toFixed(0)}% confidence
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <Activity className="w-8 h-8 mb-2 opacity-50" />
              <p className="text-sm">No signals yet</p>
              <p className="text-xs">Signals will appear here when trading starts</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


