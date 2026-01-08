# High-Frequency Trading (HFT) Multi-Timeframe Predictor

This module extends the ensemble trading model to support multiple timeframes for high-frequency trading strategies.

## Features

- **Multiple Timeframes**: Predictions for 1min, 5min, 15min, 30min, 1hour, and 1day
- **Timeframe-Specific Models**: Each timeframe has its own trained model with appropriate thresholds
- **Real-time Predictions**: Make predictions using the latest market data
- **Flexible Configuration**: Adjustable thresholds and forward periods for each timeframe

## Supported Timeframes

| Timeframe | Data Frequency | Forward Period | Default Threshold | Use Case |
|-----------|---------------|----------------|-------------------|----------|
| 1min      | 1 minute      | 1 minute       | 0.1%              | Ultra HFT |
| 5min      | 5 minutes     | 5 minutes      | 0.2%              | Very HFT |
| 15min     | 15 minutes    | 15 minutes     | 0.3%              | HFT |
| 30min     | 30 minutes    | 30 minutes     | 0.5%              | Short-term |
| 1hour     | 60 minutes    | 1 hour         | 1.0%              | Medium-term |
| 1day      | Daily         | 1 day          | 1.5%              | Swing trading |

## Usage

### Basic Usage

```python
from multi_timeframe_predictor import MultiTimeframePredictor
import schwabdev
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = schwabdev.Client(
    os.getenv('app_key'),
    os.getenv('app_secret'),
    os.getenv('callback_url')
)

# Create predictor
predictor = MultiTimeframePredictor(client)

# Train models for specific timeframes
symbol = 'AAPL'
predictor.train_timeframe(symbol, '1day')  # Start with daily
predictor.train_timeframe(symbol, '15min')  # Add 15-minute
predictor.train_timeframe(symbol, '5min')   # Add 5-minute

# Make predictions
prediction = predictor.predict_timeframe(symbol, '15min')
print(f"Probability: {prediction['probability']:.2%}")
print(f"Prediction: {'UP' if prediction['prediction'] == 1 else 'DOWN'}")
```

### Train All Timeframes

```python
# Train models for all timeframes
trained = predictor.train_all_timeframes('AAPL', ['1day', '1hour', '30min', '15min', '5min'])

# Get predictions for all timeframes
predictions = predictor.predict_all_timeframes('AAPL')

# Get summary
summary = predictor.get_prediction_summary('AAPL')
print(summary)
```

### Custom Configuration

```python
# Customize thresholds and forward periods
predictor.timeframe_configs['5min']['threshold'] = 0.003  # 0.3% instead of 0.2%
predictor.timeframe_configs['5min']['forward_periods'] = 2  # Predict 10 minutes ahead

# Train with custom config
predictor.train_timeframe('AAPL', '5min')
```

### Real-Time Predictions

```python
# Make prediction using latest data
prediction = predictor.predict_timeframe('AAPL', '5min')

# Or provide your own current data
current_data = fetcher.get_intraday_data('AAPL', period=1, frequency=5)
prediction = predictor.predict_timeframe('AAPL', '5min', current_data=current_data)
```

## Running the Example

```bash
python multi_timeframe_predictor.py
```

This will:
1. Train models for available timeframes
2. Make predictions for the symbol
3. Display a summary of predictions

## Notes for High-Frequency Trading

### Data Requirements

- **Intraday data** requires the market to be open or recent historical data
- **Minute-level data** has limitations:
  - 1-minute: Only available for current day
  - 5-minute: Available for 1 day
  - 15-minute: Available for 1 day
  - 30-minute: Available for 5 days
  - 60-minute: Available for 10 days

### Threshold Selection

- **Lower timeframes** (1min, 5min) use smaller thresholds (0.1-0.2%) because:
  - Smaller price movements expected
  - Higher noise levels
  - More frequent but smaller opportunities

- **Higher timeframes** (1hour, 1day) use larger thresholds (1-1.5%) because:
  - Larger price movements expected
  - Less noise
  - Fewer but more significant opportunities

### Best Practices

1. **Start with Daily**: Train daily model first (most data available)
2. **Add Intraday Gradually**: Add shorter timeframes as data becomes available
3. **Adjust Thresholds**: Fine-tune thresholds based on your strategy and risk tolerance
4. **Market Hours**: Intraday predictions work best during market hours
5. **Model Refresh**: Retrain models periodically as market conditions change
6. **Risk Management**: Always use proper risk management (stop losses, position sizing)

## Integration with Trading Strategy

```python
# Example: Multi-timeframe consensus strategy
predictions = predictor.predict_all_timeframes('AAPL')

# Count bullish signals
bullish_count = sum(1 for p in predictions.values() 
                   if isinstance(p, dict) and p.get('prediction') == 1)

# Trade if majority of timeframes are bullish
if bullish_count >= len(predictions) * 0.6:  # 60% consensus
    print("Strong bullish signal across multiple timeframes")
    # Execute trade logic here
```

## Limitations

1. **API Rate Limits**: Schwab API has rate limits - be mindful when fetching multiple timeframes
2. **Data Availability**: Intraday data requires market to be open or recent data
3. **Overfitting Risk**: Smaller datasets for intraday timeframes increase overfitting risk
4. **Latency**: Real-time predictions depend on data freshness

## Next Steps

- Add real-time streaming data integration
- Implement ensemble predictions (weighted average across timeframes)
- Add backtesting framework for multi-timeframe strategies
- Integrate with order execution system (use with caution!)


