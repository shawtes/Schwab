import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

// Use relative URLs - Vite proxy will forward to backend
const API_BASE = '/api';

interface StockSummary {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  rsi?: number;
  macd?: number;
  signal?: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [symbols, setSymbols] = useState<string>('AAPL,MSFT,GOOGL,AMZN,TSLA');
  const [isLoading, setIsLoading] = useState(false);

  const { data: stocks, refetch } = useQuery<StockSummary[]>({
    queryKey: ['dashboard-stocks'],
    queryFn: async () => {
      const symbolList = symbols.split(',').map(s => s.trim().toUpperCase());
      const response = await axios.post(`${API_BASE}/quotes`, {
        symbols: symbolList
      });
      return response.data;
    },
    enabled: false,
  });

  const handleLoad = async () => {
    setIsLoading(true);
    await refetch();
    setIsLoading(false);
  };

  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Market Overview</h2>
          <button className="btn btn-primary" onClick={handleLoad} disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        <div className="form-group">
          <label className="form-label">Watchlist Symbols (comma-separated)</label>
          <input
            type="text"
            className="form-input"
            value={symbols}
            onChange={(e) => setSymbols(e.target.value)}
            placeholder="AAPL, MSFT, GOOGL"
          />
        </div>

        {stocks && stocks.length > 0 && (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Price</th>
                  <th>Change</th>
                  <th>Change %</th>
                  <th>Volume</th>
                  <th>Signal</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {stocks.map((stock) => (
                  <tr key={stock.symbol}>
                    <td>
                      <strong>{stock.symbol}</strong>
                    </td>
                    <td>${stock.price.toFixed(2)}</td>
                    <td className={stock.change >= 0 ? 'positive' : 'negative'}>
                      {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                    </td>
                    <td className={stock.changePercent >= 0 ? 'positive' : 'negative'}>
                      {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                    </td>
                    <td>{stock.volume.toLocaleString()}</td>
                    <td>
                      <span className={`badge badge-${stock.signal?.toLowerCase() === 'buy' ? 'success' : stock.signal?.toLowerCase() === 'sell' ? 'danger' : 'warning'}`}>
                        {stock.signal || 'HOLD'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        onClick={() => navigate(`/chart/${stock.symbol}`)}
                      >
                        View Chart
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

export default Dashboard;

