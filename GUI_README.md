# Institutional Trading Platform - Desktop GUI

Professional-grade desktop trading application with comprehensive stock screening, analysis, and visualization capabilities.

## Features

### 🎯 Stock Screener
- **Multi-Stock Analysis**: Analyze multiple stocks simultaneously
- **Real-time Data Fetching**: Fetch current market data from Schwab API
- **Advanced Filtering**: Filter stocks by RSI, MACD, Volume, and more
- **Smart Sorting**: Sort by any metric (Alpha Sharpe, RSI, Momentum, etc.)
- **Trading Signals**: Automatic BUY/SELL/HOLD signals based on indicators

### 📊 Chart Visualization
- **Interactive Charts**: Professional matplotlib charts integrated in GUI
- **Multiple Indicators**: RSI, MACD, Bollinger Bands, Volume
- **Customizable Views**: Toggle indicators on/off
- **Zoom & Pan**: Full navigation toolbar for chart analysis

### 🎨 Professional UI
- **Dark Theme**: Modern, eye-friendly dark interface
- **Tabbed Interface**: Organized workflow with multiple tabs
- **Real-time Updates**: Progress bars and status messages
- **Responsive Design**: Clean, institutional-grade layout

### 🔧 Technical Capabilities
- **184 Features**: Technical indicators and alpha factors
- **WorldQuant Alphas**: Implementation of "Finding Alphas" patterns
- **Machine Learning Ready**: Integration with ensemble trading models
- **Threaded Operations**: Non-blocking data fetching

## Installation

### Prerequisites
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Required Packages
- PyQt5 (GUI framework)
- matplotlib (Charting)
- pandas, numpy (Data processing)
- scikit-learn (Machine learning)
- python-dotenv (Configuration)

## Quick Start

### Launch the GUI
```bash
python3 launch_gui.py
```

Or directly:
```bash
python3 trading_gui.py
```

### First Time Setup
1. Ensure your `.env` file has Schwab API credentials:
   ```
   app_key=YOUR_KEY
   app_secret=YOUR_SECRET
   callback_url=https://127.0.0.1
   ```

2. If credentials are missing, run:
   ```bash
   python3 setup_schwab.py
   ```

## Usage Guide

### Stock Screener Tab

1. **Enter Symbols**
   - Type comma-separated symbols in the input field
   - Example: `AAPL, MSFT, GOOGL, AMZN, TSLA`

2. **Fetch & Analyze**
   - Click "Fetch & Analyze" button
   - Progress bar shows fetching status
   - Data is fetched, indicators calculated, and quotes retrieved

3. **View Results**
   - Table displays all stocks with key metrics:
     - Symbol, Price, RSI, MACD, MACD Histogram
     - Volume Ratio, Momentum, Alpha Sharpe, Returns
     - Trading Signal (BUY/SELL/HOLD)

4. **Filter Stocks**
   - Set RSI range (default: 30-70)
   - Check "Positive MACD Hist" for bullish signals
   - Set minimum Volume Ratio
   - Click "Apply Filters"

5. **Sort Stocks**
   - Select metric from dropdown
   - Choose ascending/descending
   - Click "Sort"

6. **View Chart**
   - Double-click any row to view detailed chart
   - Or switch to Charts tab manually

### Charts Tab

1. **Enter Symbol**
   - Type symbol in input field
   - Press Enter or click "Plot Chart"

2. **Select Indicators**
   - Check/uncheck indicators:
     - RSI (Relative Strength Index)
     - MACD (Moving Average Convergence Divergence)
     - Bollinger Bands
     - Volume

3. **Navigate Chart**
   - Use toolbar buttons:
     - Home: Reset view
     - Back/Forward: Navigate history
     - Pan: Move chart
     - Zoom: Zoom in/out
     - Configure: Subplot parameters
     - Save: Export chart

## Trading Signals

The application automatically calculates trading signals based on:

- **RSI**: Oversold (<40) = BUY signal, Overbought (>60) = SELL signal
- **MACD Histogram**: Positive = BUY signal, Negative = SELL signal
- **Momentum**: Positive 20-day momentum = BUY signal

**Signal Logic**:
- **BUY**: 2+ bullish indicators
- **SELL**: 2+ bearish indicators
- **HOLD**: Mixed signals

## Keyboard Shortcuts

- `Ctrl+Q`: Exit application
- `Enter` (in symbol field): Plot chart
- `Double-click` (table row): View chart for symbol

## Architecture

### Components

1. **TradingApplication** (Main Window)
   - Manages overall application state
   - Handles menu bar, status bar, tabs
   - Initializes API client

2. **StockScreenerTab**
   - Stock screening interface
   - Data fetching with progress
   - Filtering and sorting
   - Results table with signals

3. **ChartTab**
   - Chart visualization
   - Indicator selection
   - Interactive plotting

4. **ChartWidget**
   - Custom matplotlib widget
   - Multi-subplot charts
   - Navigation toolbar

5. **DataFetchThread**
   - Background data fetching
   - Non-blocking UI updates
   - Progress reporting

### Data Flow

```
User Input → DataFetchThread → StockScreener → 
Feature Calculation → Summary DataFrame → Table Display
```

## Advanced Features

### Custom Filters
You can extend filtering by modifying `apply_filters()` method:
```python
filters = {
    'RSI': (30, 70),
    'MACD_Hist': (0, None),
    'Volume_Ratio': (1.5, None),
    'Alpha_Sharpe_20': (1.0, None)
}
```

### Custom Signals
Modify `calculate_signal()` to implement your own trading logic:
```python
def calculate_signal(self, row):
    # Your custom logic here
    if condition:
        return "BUY"
    # ...
```

### Integration with ML Models
The GUI integrates with `ensemble_trading_model.py`:
```python
from ensemble_trading_model import EnsembleTradingModel

# Train model on screened stocks
model = EnsembleTradingModel(task='regression')
# Use screener data for training
```

## Troubleshooting

### GUI Not Launching
- Check PyQt5 installation: `pip install PyQt5`
- Verify Python version (3.8+)
- Check for display server (X11 on Linux)

### API Connection Errors
- Verify `.env` file exists and has correct credentials
- Check internet connection
- Run `python3 setup_schwab.py` to reconfigure

### Charts Not Displaying
- Ensure matplotlib backend is Qt5Agg (set automatically)
- Check if data was fetched successfully
- Verify symbol exists in screener data

### Performance Issues
- Reduce number of symbols analyzed
- Use shorter time periods
- Close other applications

## Future Enhancements

- [ ] Portfolio management tab
- [ ] Real-time streaming data
- [ ] Order placement integration
- [ ] Backtesting capabilities
- [ ] Strategy builder
- [ ] Risk management tools
- [ ] Export/import functionality
- [ ] Custom indicator builder
- [ ] Multi-timeframe analysis
- [ ] Alert system

## System Requirements

- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Display**: 1280x720 minimum resolution
- **Internet**: Required for API access

## Support

For issues or questions:
1. Check this README
2. Review `STOCK_SCREENER_README.md` for backend details
3. Check API credentials and connection
4. Review error messages in status bar

## License

Proprietary - Institutional Trading Platform
Built for professional trading operations


