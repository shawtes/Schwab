# Live Multi-Timeframe Charting System

Professional-grade real-time charting system with multiple timeframes, similar to Bloomberg Terminal and TradingView.

## Features

### 🎯 Real-Time Streaming
- **Live Price Updates**: Real-time price data via Schwab streaming API
- **WebSocket Integration**: Low-latency data delivery
- **Auto-Refresh**: Charts update automatically every second
- **Price Display**: Live price with color-coded direction (↑↓→)

### 📊 Multiple Timeframes
- **1min**: 1-minute bars (intraday)
- **5min**: 5-minute bars (intraday)
- **15min**: 15-minute bars (intraday)
- **30min**: 30-minute bars (intraday)
- **1hour**: 1-hour bars (intraday)
- **1day**: Daily bars (historical)

### 📈 Professional Charting
- **Candlestick Charts**: Professional OHLC candlestick visualization
- **Color Coding**: Green for up, red for down
- **Moving Averages**: MA20 and MA50 overlays
- **Bollinger Bands**: Volatility bands with fill
- **Volume Bars**: Color-coded volume indicators
- **Dark Theme**: Professional dark interface

### 🎨 Interactive Features
- **Timeframe Selector**: Switch between timeframes instantly
- **Indicator Toggles**: Show/hide MA20, MA50, Bollinger Bands, Volume
- **Zoom & Pan**: Full matplotlib navigation toolbar
- **Symbol Input**: Enter any stock symbol
- **Start/Stop Streaming**: Toggle live data on/off

## Usage

### Launch the GUI

```bash
python launch_gui.py
```

### Using Live Charts

1. **Navigate to Live Charts Tab**
   - Click on "Live Charts" tab in the main window

2. **Enter Symbol**
   - Type symbol in the input field (e.g., "AAPL")
   - Press Enter or click "Load Chart"

3. **Select Timeframe**
   - Choose from dropdown: 1min, 5min, 15min, 30min, 1hour, 1day
   - Chart automatically reloads with new timeframe

4. **Start Live Streaming**
   - Click "Start Live" button
   - Real-time price updates begin
   - Price label updates with live data

5. **Toggle Indicators**
   - Check/uncheck: MA20, MA50, BB (Bollinger Bands), Volume
   - Chart updates in real-time

6. **Navigate Chart**
   - Use toolbar buttons to zoom, pan, reset view
   - Export chart as image

## Architecture

### Components

1. **LiveChartWidget**
   - Main chart widget
   - Handles data loading and display
   - Manages streaming thread

2. **StreamDataThread**
   - Background thread for streaming
   - Processes WebSocket messages
   - Emits data signals to main thread

3. **LiveChartTab**
   - Tab wrapper for integration
   - Provides clean interface

### Data Flow

```
User Input → Load Historical Data → Display Chart
                ↓
         Start Streaming → StreamDataThread → Process Messages
                ↓
         Emit Signals → Update Chart → Real-time Display
```

## Technical Details

### Streaming API

Uses Schwab's Level One Equities streaming:
- **Field 0**: Bid Price
- **Field 1**: Ask Price
- **Field 3**: Last Price
- **Field 8**: Total Volume

### Chart Rendering

- **Candlesticks**: Custom matplotlib rectangles
- **Wicks**: High-low lines
- **Colors**: Green (#4caf50) for up, Red (#f44336) for down
- **Updates**: 1-second refresh interval

### Timeframe Mapping

```python
'1min': 1-minute bars, 1 day history
'5min': 5-minute bars, 1 day history
'15min': 15-minute bars, 1 day history
'30min': 30-minute bars, 5 days history
'1hour': 60-minute bars, 10 days history
'1day': Daily bars, 1 year history
```

## Performance

- **Update Rate**: 1 second (configurable)
- **Data Buffer**: 1000 points max (deque)
- **Thread Safety**: QMutex for data access
- **Memory**: Efficient deque for streaming data

## Troubleshooting

### Chart Not Loading
- Check symbol is valid
- Verify API credentials
- Check internet connection
- Ensure market is open (for live data)

### Streaming Not Working
- Verify WebSocket connection
- Check API subscription limits
- Ensure symbol is subscribed
- Check network firewall

### Performance Issues
- Reduce update frequency
- Limit number of indicators
- Close other applications
- Use shorter timeframes for less data

## Future Enhancements

- [ ] Multiple symbols on one chart
- [ ] Drawing tools (lines, shapes)
- [ ] More indicators (RSI, MACD overlay)
- [ ] Alerts and notifications
- [ ] Historical data export
- [ ] Custom timeframe selection
- [ ] Chart templates
- [ ] Order placement integration

## Integration

The live chart is integrated into the main trading GUI:

```python
from live_chart import LiveChartTab

# In TradingApplication
self.live_chart_tab = LiveChartTab(self.client)
self.tabs.addTab(self.live_chart_tab, "Live Charts")
```

## Professional Features

This implementation provides institutional-level features:
- ✅ Real-time data streaming
- ✅ Multiple timeframes
- ✅ Professional candlestick charts
- ✅ Technical indicators
- ✅ Low-latency updates
- ✅ Thread-safe architecture
- ✅ Professional UI/UX

Perfect for professional trading operations!


