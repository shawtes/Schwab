import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { createChart, IChartApi, ISeriesApi, ColorType, Time } from 'lightweight-charts';
import axios from 'axios';
import './LiveChart.css';

// Use relative URLs - Vite proxy will forward to backend
const API_BASE = '/api';
const WS_URL = `ws://${window.location.hostname}:3001`;

interface CandleData {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const LiveChart: React.FC = () => {
  const { symbol: urlSymbol } = useParams<{ symbol?: string }>();
  const navigate = useNavigate();
  const [symbol, setSymbol] = useState<string>(urlSymbol || 'AAPL');
  const [timeframe, setTimeframe] = useState<string>('1min');
  const [isLive, setIsLive] = useState<boolean>(false);
  const [price, setPrice] = useState<number>(0);
  const [change, setChange] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const timeframes = [
    { value: '1min', label: '1 Min' },
    { value: '5min', label: '5 Min' },
    { value: '15min', label: '15 Min' },
    { value: '30min', label: '30 Min' },
    { value: '1hour', label: '1 Hour' },
    { value: '1day', label: '1 Day' },
  ];

  // Load historical data
  const loadData = useCallback(async () => {
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current) {
      console.log('Chart series not ready yet');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log(`Loading data for ${symbol} with timeframe ${timeframe}`);
      
      const response = await axios.post(`${API_BASE}/price-history`, {
        symbol,
        periodType: timeframe === '1day' ? 'year' : 'day',
        period: timeframe === '1day' ? 1 : timeframe === '1hour' ? 10 : 1,
        frequencyType: timeframe === '1day' ? 'daily' : 'minute',
        frequency: timeframe === '1day' ? 1 : 
                   timeframe === '1hour' ? 60 :
                   timeframe === '30min' ? 30 :
                   timeframe === '15min' ? 15 :
                   timeframe === '5min' ? 5 : 1,
      });

      console.log('API Response:', response.data);

      const data = response.data;
      
      if (data.error) {
        console.error('API Error:', data.error);
        return;
      }

      if (data && data.candles && Array.isArray(data.candles) && data.candles.length > 0) {
        const candles: CandleData[] = data.candles.map((candle: any): CandleData | null => {
          // Handle different datetime formats
          let timestamp: number;
          if (typeof candle.datetime === 'string') {
            timestamp = Math.floor(new Date(candle.datetime).getTime() / 1000);
          } else if (typeof candle.datetime === 'number') {
            timestamp = Math.floor(candle.datetime / 1000);
          } else {
            console.error('Invalid datetime format:', candle.datetime);
            return null;
          }

          return {
            time: timestamp as Time,
            open: parseFloat(candle.open),
            high: parseFloat(candle.high),
            low: parseFloat(candle.low),
            close: parseFloat(candle.close),
            volume: parseInt(candle.volume),
          };
        }).filter((c: CandleData | null): c is CandleData => c !== null);

        if (candles.length === 0) {
          console.error('No valid candles after processing');
          return;
        }

        console.log(`Setting ${candles.length} candles on chart`);

        candlestickSeriesRef.current.setData(candles.map(c => ({
          time: c.time as Time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
        })));

        volumeSeriesRef.current.setData(candles.map(c => ({
          time: c.time as Time,
          value: c.volume,
          color: c.close >= c.open ? '#4caf50' : '#f44336',
        })));

        if (candles.length > 0) {
          const lastCandle = candles[candles.length - 1];
          setPrice(lastCandle.close);
        }
      } else {
        const errorMsg = 'No candles in response';
        console.error(errorMsg, data);
        setError(errorMsg);
      }
    } catch (error: any) {
      console.error('Error loading data:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Failed to load chart data';
      setError(errorMsg);
      if (error.response) {
        console.error('Response error:', error.response.data);
      }
    } finally {
      setIsLoading(false);
    }
  }, [symbol, timeframe]);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0a0e27' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#1f2937' },
        horzLines: { color: '#1f2937' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 600,
      timeScale: {
        timeVisible: true,
        secondsVisible: timeframe === '1min',
        borderColor: '#485563',
      },
      rightPriceScale: {
        borderColor: '#485563',
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#4caf50',
      downColor: '#f44336',
      borderVisible: false,
      wickUpColor: '#4caf50',
      wickDownColor: '#f44336',
    });

    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    // Load data after chart is initialized
    setTimeout(() => {
      loadData();
    }, 100);

    return () => {
      chart.remove();
    };
  }, [loadData]);

  // WebSocket connection for live data
  useEffect(() => {
    if (!isLive || !symbol) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'subscribe',
        symbols: [symbol],
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'price' && data.symbol === symbol) {
        setPrice(data.price);
        if (data.change !== undefined) {
          setChange(data.change);
        }

        // Update chart with new price
        if (candlestickSeriesRef.current) {
          const now = Math.floor(Date.now() / 1000) as Time;
          candlestickSeriesRef.current.update({
            time: now,
            open: data.price,
            high: data.price,
            low: data.price,
            close: data.price,
          });
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [isLive, symbol]);

  // Load data when symbol or timeframe changes (after chart is initialized)
  useEffect(() => {
    if (candlestickSeriesRef.current && volumeSeriesRef.current) {
      loadData();
    }
  }, [symbol, timeframe]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleLive = () => {
    setIsLive(!isLive);
  };

  return (
    <div className="live-chart">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Live Chart</h2>
        </div>

        <div className="chart-controls">
          <div className="form-group">
            <label className="form-label">Symbol</label>
            <input
              type="text"
              className="form-input"
              value={symbol}
              onChange={(e) => {
                setSymbol(e.target.value.toUpperCase());
                navigate(`/chart/${e.target.value.toUpperCase()}`);
              }}
              placeholder="Enter symbol"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Timeframe</label>
            <select
              className="form-select"
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
            >
              {timeframes.map(tf => (
                <option key={tf.value} value={tf.value}>{tf.label}</option>
              ))}
            </select>
          </div>

          <button
            className={`btn ${isLive ? 'btn-danger' : 'btn-success'}`}
            onClick={toggleLive}
          >
            {isLive ? 'Stop Live' : 'Start Live'}
          </button>
        </div>

        <div className="price-display">
          <div className="price-main">
            <span className="price-label">Price:</span>
            <span className={`price-value ${change >= 0 ? 'positive' : 'negative'}`}>
              ${price.toFixed(2)}
            </span>
            {change !== 0 && (
              <span className={`price-change ${change >= 0 ? 'positive' : 'negative'}`}>
                {change >= 0 ? '+' : ''}{change.toFixed(2)}
              </span>
            )}
          </div>
        </div>

        {error && (
          <div className="error-message" style={{ 
            padding: '1rem', 
            background: '#f44336', 
            color: 'white', 
            borderRadius: '8px', 
            marginBottom: '1rem' 
          }}>
            Error: {error}
          </div>
        )}

        {isLoading && (
          <div style={{ 
            padding: '1rem', 
            textAlign: 'center', 
            color: '#d1d5db' 
          }}>
            Loading chart data...
          </div>
        )}

        <div ref={chartContainerRef} className="chart-container" />
      </div>
    </div>
  );
};

export default LiveChart;

