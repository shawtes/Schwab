/**
 * Trading Platform Backend Server
 * Node.js + Express + TypeScript
 * Provides API endpoints and WebSocket server for real-time data
 */

import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import dotenv from 'dotenv';
import path from 'path';
import { spawn } from 'child_process';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const httpServer = createServer(app);

// WebSocket Server
const wss = new WebSocketServer({ server: httpServer });

// Middleware
app.use(cors());
app.use(express.json());

// Store active WebSocket connections
const clients = new Set<WebSocket>();

// Python script paths (relative to project root)
// Find web-trading-app root directory (where Python scripts are located)
// __dirname is server/src when running, or server/dist when compiled
const PROJECT_ROOT = path.resolve(__dirname, '../..');

// Get Python path - prefer conda environment or virtual environment
const fs = require('fs');
const condaPython = '/opt/anaconda3/envs/schwabdev/bin/python';
const venvPython = path.join(PROJECT_ROOT, 'venv', 'bin', 'python');
const PYTHON_PATH = fs.existsSync(condaPython) ? condaPython : 
                    fs.existsSync(venvPython) ? venvPython : 'python3';

console.log('🐍 Using Python:', PYTHON_PATH);

interface StockData {
  symbol: string;
  price: number;
  volume: number;
  timestamp: string;
  bid?: number;
  ask?: number;
}

interface PriceHistoryRequest {
  symbol: string;
  periodType?: string;
  period?: number;
  frequencyType?: string;
  frequency?: number;
}

// API Routes

/**
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * Get price history for a symbol
 */
app.post('/api/price-history', async (req, res) => {
  try {
    const { symbol, periodType = 'year', period = 1, frequencyType = 'daily', frequency = 1 }: PriceHistoryRequest = req.body;

    if (!symbol) {
      return res.status(400).json({ error: 'Symbol is required' });
    }

    // Call Python script to fetch data using spawn
    const scriptPath = path.join(PROJECT_ROOT, 'fetch_stock_data.py');
    console.log(`[DEBUG] Calling Python: ${PYTHON_PATH} fetch_stock_data.py ${symbol}`);
    
    const pythonProcess = spawn(PYTHON_PATH, [scriptPath, symbol, periodType, period.toString(), frequencyType, frequency.toString()], {
      cwd: PROJECT_ROOT
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`[ERROR] Python script exited with code ${code}`);
        console.error(`[ERROR] stderr: ${errorOutput}`);
        return res.status(500).json({ error: 'Failed to fetch price history', details: errorOutput });
      }

      try {
        const data = JSON.parse(output.trim());
        res.json(data);
      } catch (parseErr) {
        console.error('[ERROR] Failed to parse Python output:', output);
        return res.status(500).json({ error: 'Invalid response from Python script' });
      }
    });

    setTimeout(() => {
      if (!res.headersSent) {
        pythonProcess.kill();
        console.error('[ERROR] Python script timeout after 30 seconds');
        res.status(504).json({ error: 'Request timeout' });
      }
    }, 30000); // 30 seconds for historical data
  } catch (error) {
    console.error('Error fetching price history:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Get quotes for multiple symbols
 */
app.post('/api/quotes', async (req, res) => {
  try {
    const { symbols }: { symbols: string[] } = req.body;

    if (!symbols || !Array.isArray(symbols)) {
      return res.status(400).json({ error: 'Symbols array is required' });
    }

    // Call Python script to fetch quotes using spawn
    const scriptPath = path.join(PROJECT_ROOT, 'fetch_quotes.py');
    console.log(`[DEBUG] Calling Python: ${PYTHON_PATH} ${scriptPath} ${symbols.join(',')}`);
    
    const pythonProcess = spawn(PYTHON_PATH, [scriptPath, symbols.join(',')], {
      cwd: PROJECT_ROOT
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`[ERROR] Python script exited with code ${code}`);
        console.error(`[ERROR] stderr: ${errorOutput}`);
        return res.status(500).json({ error: 'Failed to fetch quotes', details: errorOutput });
      }

      console.log(`[DEBUG] Python output: ${output.substring(0, 200)}...`);
      
      try {
        const data = JSON.parse(output.trim());
        console.log(`[DEBUG] Successfully parsed quotes for ${Object.keys(data).length} symbols`);
        res.json(data);
      } catch (parseErr) {
        console.error('[ERROR] Failed to parse Python output:', output);
        return res.status(500).json({ error: 'Invalid response from Python script' });
      }
    });

    // Handle timeout
    setTimeout(() => {
      if (!res.headersSent) {
        pythonProcess.kill();
        console.error('[ERROR] Python script timeout');
        res.status(504).json({ error: 'Request timeout' });
      }
    }, 10000);
  } catch (error) {
    console.error('Error fetching quotes:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Get indicators and features for a symbol
 */
app.post('/api/indicators', async (req, res) => {
  try {
    const { symbol }: { symbol: string } = req.body;

    if (!symbol) {
      return res.status(400).json({ error: 'Symbol is required' });
    }

    // Call Python script to calculate indicators
    const scriptPath = path.join(PROJECT_ROOT, 'calculate_indicators.py');
    const options = {
      mode: 'json' as const,
      pythonPath: PYTHON_PATH,
      args: [symbol]
    };

    PythonShell.run(scriptPath, options, (err, results) => {
      if (err) {
        console.error('Python script error:', err);
        return res.status(500).json({ error: 'Failed to calculate indicators' });
      }

      if (results && results.length > 0) {
        res.json(results[0]);
      } else {
        res.status(404).json({ error: 'No indicators found' });
      }
    });
  } catch (error) {
    console.error('Error calculating indicators:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Root route - provide helpful message
 */
app.get('/', (req, res) => {
  res.json({
    message: 'Trading Platform API Server',
    status: 'running',
    frontend: 'http://localhost:3000',
    api: 'http://localhost:3001/api',
    endpoints: [
      'GET /api/health',
      'POST /api/price-history',
      'POST /api/quotes',
      'POST /api/indicators',
      'POST /api/screen'
    ]
  });
});

/**
 * Screen stocks with filters
 */
app.post('/api/screen', async (req, res) => {
  try {
    const { symbols, filters }: { symbols: string[], filters?: any } = req.body;

    if (!symbols || !Array.isArray(symbols)) {
      return res.status(400).json({ error: 'Symbols array is required' });
    }

    // Call Python script to screen stocks
    const scriptPath = path.join(PROJECT_ROOT, 'screen_stocks.py');
    const options = {
      mode: 'json' as const,
      pythonPath: PYTHON_PATH,
      args: [symbols.join(','), JSON.stringify(filters || {})]
    };

    PythonShell.run(scriptPath, options, (err, results) => {
      if (err) {
        console.error('Python script error:', err);
        return res.status(500).json({ error: 'Failed to screen stocks' });
      }

      if (results && results.length > 0) {
        res.json(results[0]);
      } else {
        res.status(404).json({ error: 'No stocks found' });
      }
    });
  } catch (error) {
    console.error('Error screening stocks:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Momentum Scanner - Scan all stocks for momentum opportunities
 */
app.post('/api/momentum-scan', async (req, res) => {
  try {
    const { filters } = req.body;
    
    if (!filters) {
      return res.status(400).json({ error: 'Filters are required' });
    }

    console.log('[DEBUG] Running momentum scan with filters:', filters);
    
    // Call Python momentum scanner script
    const scriptPath = path.join(PROJECT_ROOT, 'momentum_scanner.py');
    const pythonProcess = spawn(PYTHON_PATH, [scriptPath, JSON.stringify(filters)], {
      cwd: PROJECT_ROOT
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('[ERROR] Momentum scanner exited with code', code);
        console.error('[ERROR] stderr:', errorOutput);
        return res.status(500).json({ error: 'Failed to run momentum scan', details: errorOutput });
      }

      try {
        const data = JSON.parse(output.trim());
        console.log(`[DEBUG] Momentum scan found ${data.results?.length || 0} stocks`);
        res.json(data);
      } catch (parseErr) {
        console.error('[ERROR] Failed to parse momentum scanner output:', output);
        return res.status(500).json({ error: 'Invalid response from momentum scanner' });
      }
    });

    // Timeout after 60 seconds (scanning can take a while)
    setTimeout(() => {
      if (!res.headersSent) {
        pythonProcess.kill();
        console.error('[ERROR] Momentum scanner timeout');
        res.status(504).json({ error: 'Scan timeout - try reducing the universe size' });
      }
    }, 60000);
  } catch (error) {
    console.error('Error running momentum scan:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// WebSocket connection handling
wss.on('connection', (ws: WebSocket) => {
  console.log('New WebSocket connection');
  clients.add(ws);

  ws.on('message', (message: string) => {
    try {
      const data = JSON.parse(message.toString());
      
      if (data.type === 'subscribe') {
        // Handle subscription to symbols
        const { symbols } = data;
        console.log(`Client subscribed to: ${symbols.join(', ')}`);
        
        // Start streaming data for subscribed symbols
        // This would integrate with Schwab streaming API
        ws.send(JSON.stringify({
          type: 'subscribed',
          symbols: symbols
        }));
      } else if (data.type === 'unsubscribe') {
        // Handle unsubscription
        console.log('Client unsubscribed');
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
    }
  });

  ws.on('close', () => {
    console.log('WebSocket connection closed');
    clients.delete(ws);
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    clients.delete(ws);
  });

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Connected to trading server'
  }));
});

// Broadcast function to send data to all connected clients
function broadcast(data: any) {
  const message = JSON.stringify(data);
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// Start server
httpServer.listen(PORT, () => {
  console.log(`🚀 Trading Server running on http://localhost:${PORT}`);
  console.log(`📡 WebSocket server ready for connections`);
});

export { broadcast };

