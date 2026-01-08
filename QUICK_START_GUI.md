# Quick Start - Institutional Trading Platform GUI

## 🚀 Launch the Application

```bash
python3 launch_gui.py
```

Or directly:
```bash
python3 trading_gui.py
```

## ✅ Prerequisites Check

1. **API Credentials**: Ensure `.env` file exists with:
   ```
   app_key=YOUR_KEY
   app_secret=YOUR_SECRET
   callback_url=https://127.0.0.1
   ```

2. **Dependencies**: All installed via `requirements.txt`
   - PySide6 (GUI framework) ✅
   - matplotlib (Charts) ✅
   - pandas, numpy (Data) ✅
   - scikit-learn (ML) ✅

## 📋 First Steps

### 1. Stock Screener Tab
- Enter symbols: `AAPL, MSFT, GOOGL, AMZN, TSLA`
- Click **"Fetch & Analyze"**
- Wait for progress bar to complete
- View results in table

### 2. Filter & Sort
- Set RSI range (30-70)
- Check "Positive MACD Hist"
- Click **"Apply Filters"**
- Select sort metric and click **"Sort"**

### 3. View Charts
- Double-click any row in table
- OR go to Charts tab
- Enter symbol and click **"Plot Chart"**

## 🎯 Key Features

- **Real-time Data**: Fetched from Schwab API
- **184 Indicators**: Technical + Alpha factors
- **Trading Signals**: Automatic BUY/SELL/HOLD
- **Interactive Charts**: Zoom, pan, customize
- **Professional UI**: Dark theme, responsive

## 🐛 Troubleshooting

**GUI won't launch?**
- Check: `pip install PySide6`
- Verify Python 3.8+

**No data showing?**
- Check API credentials in `.env`
- Verify internet connection
- Run: `python3 setup_schwab.py`

**Charts not displaying?**
- Ensure data was fetched first
- Check symbol exists in screener

## 📚 Full Documentation

See `GUI_README.md` for complete guide.


