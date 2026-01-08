import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './StockScreener.css';

// Use relative URLs - Vite proxy will forward to backend
const API_BASE = '/api';

interface StockData {
  symbol: string;
  price: number;
  rsi: number;
  macd: number;
  macdHist: number;
  volumeRatio: number;
  momentum: number;
  alphaSharpe: number;
  returns21d: number;
  signal: string;
}

const StockScreener: React.FC = () => {
  const navigate = useNavigate();
  const [symbols, setSymbols] = useState<string>('AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA,JPM,V,JNJ');
  const [filters, setFilters] = useState({
    rsiMin: 30,
    rsiMax: 70,
    macdPositive: false,
    volumeMin: 1.0,
  });
  const [sortBy, setSortBy] = useState<string>('alphaSharpe');
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const { data: stocks, isLoading, refetch } = useQuery<StockData[]>({
    queryKey: ['screener-stocks', symbols, filters],
    queryFn: async () => {
      const symbolList = symbols.split(',').map(s => s.trim().toUpperCase());
      const response = await axios.post(`${API_BASE}/screen`, {
        symbols: symbolList,
        filters: filters
      });
      return response.data;
    },
    enabled: false,
  });

  const handleScreen = () => {
    refetch();
  };

  const sortedStocks = stocks ? [...stocks].sort((a, b) => {
    const aVal = (a as any)[sortBy] || 0;
    const bVal = (b as any)[sortBy] || 0;
    return sortAsc ? aVal - bVal : bVal - aVal;
  }) : [];

  return (
    <div className="screener">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Stock Screener</h2>
        </div>

        <div className="screener-controls">
          <div className="form-group">
            <label className="form-label">Symbols</label>
            <input
              type="text"
              className="form-input"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
              placeholder="AAPL, MSFT, GOOGL"
            />
          </div>

          <div className="filters">
            <h3>Filters</h3>
            <div className="filter-row">
              <div className="form-group">
                <label className="form-label">RSI Range</label>
                <div className="range-inputs">
                  <input
                    type="number"
                    className="form-input"
                    value={filters.rsiMin}
                    onChange={(e) => setFilters({...filters, rsiMin: parseFloat(e.target.value)})}
                    min="0"
                    max="100"
                  />
                  <span>to</span>
                  <input
                    type="number"
                    className="form-input"
                    value={filters.rsiMax}
                    onChange={(e) => setFilters({...filters, rsiMax: parseFloat(e.target.value)})}
                    min="0"
                    max="100"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Volume Ratio Min</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-input"
                  value={filters.volumeMin}
                  onChange={(e) => setFilters({...filters, volumeMin: parseFloat(e.target.value)})}
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.macdPositive}
                    onChange={(e) => setFilters({...filters, macdPositive: e.target.checked})}
                  />
                  Positive MACD Histogram
                </label>
              </div>
            </div>
          </div>

          <div className="sort-controls">
            <div className="form-group">
              <label className="form-label">Sort By</label>
              <select
                className="form-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="alphaSharpe">Alpha Sharpe</option>
                <option value="rsi">RSI</option>
                <option value="macdHist">MACD Hist</option>
                <option value="momentum">Momentum</option>
                <option value="volumeRatio">Volume Ratio</option>
                <option value="returns21d">Returns 21d</option>
              </select>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sortAsc}
                  onChange={(e) => setSortAsc(e.target.checked)}
                />
                Ascending
              </label>
            </div>
          </div>

          <button className="btn btn-primary" onClick={handleScreen} disabled={isLoading}>
            {isLoading ? 'Screening...' : 'Screen Stocks'}
          </button>
        </div>

        {isLoading && (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        )}

        {sortedStocks && sortedStocks.length > 0 && (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Price</th>
                  <th>RSI</th>
                  <th>MACD</th>
                  <th>MACD Hist</th>
                  <th>Volume Ratio</th>
                  <th>Momentum</th>
                  <th>Alpha Sharpe</th>
                  <th>Returns 21d</th>
                  <th>Signal</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedStocks.map((stock) => (
                  <tr key={stock.symbol}>
                    <td><strong>{stock.symbol}</strong></td>
                    <td>${stock.price.toFixed(2)}</td>
                    <td>{stock.rsi.toFixed(2)}</td>
                    <td>{stock.macd.toFixed(4)}</td>
                    <td>{stock.macdHist.toFixed(4)}</td>
                    <td>{stock.volumeRatio.toFixed(2)}</td>
                    <td>{(stock.momentum * 100).toFixed(2)}%</td>
                    <td>{stock.alphaSharpe.toFixed(4)}</td>
                    <td>{(stock.returns21d * 100).toFixed(2)}%</td>
                    <td>
                      <span className={`badge badge-${stock.signal.toLowerCase() === 'buy' ? 'success' : stock.signal.toLowerCase() === 'sell' ? 'danger' : 'warning'}`}>
                        {stock.signal}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        onClick={() => navigate(`/chart/${stock.symbol}`)}
                      >
                        Chart
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockScreener;

