# Stock Screener with Indicators and Alphas

A comprehensive stock screening tool that fetches, analyzes, and displays stocks with integrated technical indicators and alpha factors.

## Features

- **Multi-Stock Analysis**: Fetch and analyze multiple stocks simultaneously
- **Technical Indicators**: 
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Moving Averages (MA, EMA)
  - Volume indicators (OBV, VPT)
  - Volatility measures (ATR, Parkinson)
  - Stochastic Oscillator
  - Williams %R
  - CCI (Commodity Channel Index)

- **Alpha Factors** (from "Finding Alphas" book):
  - Time-series Rank (Ts_Rank)
  - Z-score normalization
  - Sharpe-like ratios
  - Price delay patterns
  - Correlation patterns
  - Mean reversion alphas
  - Trend with volume rank
  - And many more...

- **Visualization**: 
  - Comprehensive charts with multiple subplots
  - Price charts with moving averages
  - Indicator overlays
  - Volume analysis
  - Alpha factor visualization

- **Sorting & Filtering**:
  - Sort stocks by any metric
  - Filter by multiple criteria
  - Top N stock selection

## Installation

Make sure you have the required dependencies:

```bash
pip install pandas numpy matplotlib seaborn python-dotenv
```

The screener uses the existing `ensemble_trading_model.py` module for data fetching and feature calculation.

## Usage

### Quick Start (Interactive Mode)

Run the interactive launcher:

```bash
python3 run_screener.py
```

This will:
1. Prompt you for stock symbols (or use defaults)
2. Fetch data for all stocks
3. Calculate indicators and alphas
4. Provide an interactive menu for:
   - Viewing summary tables
   - Sorting by metrics
   - Filtering stocks
   - Plotting charts

### Programmatic Usage

```python
from stock_screener import StockScreener
import schwabdev
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize client
client = schwabdev.Client(
    os.getenv('app_key'),
    os.getenv('app_secret'),
    os.getenv('callback_url', 'https://127.0.0.1')
)

# Initialize screener
screener = StockScreener(client)

# Define stocks to analyze
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Fetch data
screener.fetch_stocks(symbols, periodType='year', period=1, frequencyType='daily', frequency=1)

# Calculate indicators
screener.calculate_indicators()

# Get current quotes
screener.get_current_quotes(symbols)

# Create summary DataFrame
summary_df = screener.create_summary_dataframe(include_quotes=True)

# Sort by Alpha Sharpe
sorted_df = screener.sort_stocks(summary_df, sort_by='Alpha_Sharpe_20', ascending=False, top_n=10)

# Filter stocks
filtered_df = screener.filter_stocks(summary_df, filters={
    'RSI': (30, 70),  # RSI between 30 and 70
    'MACD_Hist': (0, None)  # Positive MACD histogram
})

# Display summary
screener.display_summary_table(sorted_df)

# Plot chart for a stock
screener.plot_stock_chart('AAPL', indicators=['RSI', 'MACD', 'BB', 'Volume', 'Alphas'])
```

## Available Metrics

The summary DataFrame includes:

### Price & Returns
- `Current_Price`: Latest close price
- `Returns_1d`, `Returns_5d`, `Returns_21d`: Returns over different periods

### Technical Indicators
- `RSI`: Relative Strength Index (0-100)
- `MACD`, `MACD_Signal`, `MACD_Hist`: MACD components
- `BB_Position`: Bollinger Band position (0-1)
- `Volume_Ratio`: Current volume vs average
- `Momentum_20`: 20-period momentum
- `Volatility_20`: 20-period volatility
- `ATR_Ratio`: Average True Range ratio

### Alpha Factors
- `Alpha_TS_Rank_Close_20`: Time-series rank of close price
- `Alpha_ZScore_20`: Z-score normalization
- `Alpha_Sharpe_20`: Sharpe-like ratio

### Quote Data (if available)
- `Quote_LastPrice`: Last traded price
- `Quote_NetChange`: Net change in price
- `Quote_PercentChange`: Percentage change

## Sorting Examples

```python
# Sort by RSI (ascending - oversold first)
sorted_df = screener.sort_stocks(summary_df, sort_by='RSI', ascending=True)

# Sort by Alpha Sharpe (descending - best first)
sorted_df = screener.sort_stocks(summary_df, sort_by='Alpha_Sharpe_20', ascending=False, top_n=5)

# Sort by momentum
sorted_df = screener.sort_stocks(summary_df, sort_by='Momentum_20', ascending=False)
```

## Filtering Examples

```python
# RSI between 30 and 70 (not overbought/oversold)
filtered = screener.filter_stocks(summary_df, filters={'RSI': (30, 70)})

# Positive MACD histogram (bullish signal)
filtered = screener.filter_stocks(summary_df, filters={'MACD_Hist': (0, None)})

# High volume (volume ratio > 1.5)
filtered = screener.filter_stocks(summary_df, filters={'Volume_Ratio': (1.5, None)})

# Multiple filters
filtered = screener.filter_stocks(summary_df, filters={
    'RSI': (30, 70),
    'MACD_Hist': (0, None),
    'Volume_Ratio': (1.0, None),
    'Alpha_Sharpe_20': (0, None)  # Positive Sharpe
})
```

## Chart Customization

```python
# Basic chart
screener.plot_stock_chart('AAPL')

# Chart with specific indicators
screener.plot_stock_chart(
    'AAPL',
    indicators=['RSI', 'MACD', 'BB', 'Volume']
)

# Chart with all indicators including alphas
screener.plot_stock_chart(
    'AAPL',
    indicators=['RSI', 'MACD', 'BB', 'Volume', 'Alphas'],
    figsize=(16, 12),
    save_path='AAPL_chart.png'
)
```

## Example Workflow

1. **Screen for Oversold Stocks with Positive Momentum**:
```python
# Fetch and calculate
screener.fetch_stocks(['AAPL', 'MSFT', 'GOOGL'])
screener.calculate_indicators()
summary_df = screener.create_summary_dataframe()

# Filter: RSI < 40 (oversold) and positive momentum
oversold = screener.filter_stocks(summary_df, filters={
    'RSI': (None, 40),
    'Momentum_20': (0, None)
})

# Sort by momentum strength
top_oversold = screener.sort_stocks(oversold, sort_by='Momentum_20', ascending=False, top_n=5)
screener.display_summary_table(top_oversold)
```

2. **Find Stocks with Strong Alpha Signals**:
```python
# Filter for positive alpha Sharpe and high volume
strong_alphas = screener.filter_stocks(summary_df, filters={
    'Alpha_Sharpe_20': (1.0, None),  # Strong positive Sharpe
    'Volume_Ratio': (1.2, None)  # Above average volume
})

# Sort by alpha strength
top_alphas = screener.sort_stocks(strong_alphas, sort_by='Alpha_Sharpe_20', ascending=False)
screener.display_summary_table(top_alphas)

# Plot charts for top 3
for symbol in top_alphas['Symbol'].head(3):
    screener.plot_stock_chart(symbol, indicators=['RSI', 'MACD', 'BB', 'Volume', 'Alphas'])
```

## Notes

- The screener uses the same feature engineering as `ensemble_trading_model.py`
- All indicators and alphas are calculated using the methods from "Finding Alphas" and "Machine Learning for Algorithmic Trading"
- Charts are saved as PNG files if `save_path` is provided
- The interactive mode (`run_screener.py`) is recommended for first-time users

## Troubleshooting

**No data available for symbol**: 
- Check if the symbol is valid
- Verify API credentials are set correctly
- Some symbols may not be available through the API

**Charts not displaying**:
- Make sure matplotlib backend is configured correctly
- On some systems, you may need to set `matplotlib.use('TkAgg')` or similar

**Missing indicators**:
- Some indicators require minimum data points (e.g., 20 periods for MA)
- Ensure sufficient historical data is fetched

## Integration with Trading Model

The screener can be used to:
1. Identify promising stocks for further analysis
2. Pre-filter stocks before training models
3. Validate model predictions against technical indicators
4. Generate watchlists based on multiple criteria

Combine with `ensemble_trading_model.py` for complete analysis:
```python
# Screen stocks
screener = StockScreener(client)
screener.fetch_stocks(symbols)
screener.calculate_indicators()

# Get top stocks
summary_df = screener.create_summary_dataframe()
top_stocks = screener.sort_stocks(summary_df, sort_by='Alpha_Sharpe_20', top_n=5)

# Train model on top stocks
from ensemble_trading_model import EnsembleTradingModel
model = EnsembleTradingModel(task='regression')
# ... train on top stocks ...
```


