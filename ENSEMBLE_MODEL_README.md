# Ensemble Trading Model

A comprehensive ensemble trading model framework based on methods from **"Machine Learning for Algorithmic Trading"** by Stefan Jansen, integrated with the Schwab API for real-time data.

## Features

### Ensemble Methods Implemented

1. **Random Forest** (Bagging)
   - Bootstrap aggregation with random feature sampling
   - Out-of-bag (OOB) scoring
   - Feature importance analysis

2. **Gradient Boosting**
   - Sequential learning with weak learners
   - Adaptive boosting approach

3. **AdaBoost**
   - Adaptive boosting with decision tree stumps
   - Weighted ensemble predictions

4. **Bagging**
   - Bootstrap aggregation with customizable base estimators

5. **Voting Ensemble**
   - Soft voting (probability-based) for classification
   - Average voting for regression

6. **Stacking Ensemble**
   - Meta-learner approach
   - Cross-validated predictions as features

### Technical Features

- **Comprehensive Feature Engineering**:
  - Moving averages (5, 10, 20, 50 periods)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Volatility measures
  - Volume indicators
  - Price position metrics

- **Data Integration**:
  - Direct integration with Schwab API
  - Real-time price history fetching
  - Automated feature creation
  - Data preprocessing and scaling

- **Model Capabilities**:
  - Classification: Predict direction of price movements
  - Regression: Predict actual returns
  - Feature importance analysis
  - Model evaluation metrics

## Installation

### Required Packages

```bash
pip install scikit-learn pandas numpy python-dotenv schwabdev
```

Or if using the source code:
```bash
pip install scikit-learn pandas numpy python-dotenv
```

## Usage

### Basic Usage

```python
from ensemble_trading_model import EnsembleTradingModel, SchwabDataFetcher
import schwabdev
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv()
client = schwabdev.Client(
    os.getenv('app_key'),
    os.getenv('app_secret'),
    os.getenv('callback_url')
)

# Initialize data fetcher
fetcher = SchwabDataFetcher(client)

# Fetch data
df = fetcher.get_price_history('AAPL', period='year', frequency_type='daily')

# Create features
features_df = fetcher.create_features(df)

# Initialize model (classification: predict if return > 2%)
model = EnsembleTradingModel(task='classification', random_state=42)

# Prepare data
target, valid_mask = model.prepare_target(features_df, forward_periods=1, threshold=0.02)
features_df_valid = features_df[valid_mask]
X = model.prepare_features(features_df_valid)
y = target.values

# Split data
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

# Train with voting ensemble
model.fit(X_train, y_train, use_ensemble='voting')

# Evaluate
results = model.evaluate(X_test, y_test)

# Make predictions
predictions = model.predict(X_test)
```

### Running the Example

```bash
python ensemble_trading_model.py
```

This will:
1. Connect to Schwab API
2. Fetch AAPL price history
3. Create technical features
4. Train a voting ensemble model
5. Evaluate on test data
6. Display feature importance

## Model Types

### Classification Task

Predicts whether the forward return will exceed a threshold (e.g., 2%).

```python
model = EnsembleTradingModel(task='classification', random_state=42)
target, valid_mask = model.prepare_target(
    features_df, 
    forward_periods=1, 
    threshold=0.02  # 2% threshold
)
```

### Regression Task

Predicts the actual forward returns.

```python
model = EnsembleTradingModel(task='regression', random_state=42)
target, valid_mask = model.prepare_target(features_df, forward_periods=1)
```

## Ensemble Types

### 1. Voting Ensemble

Averages predictions from all base models:

```python
model.fit(X_train, y_train, use_ensemble='voting')
```

### 2. Stacking Ensemble

Uses a meta-learner to combine base model predictions:

```python
model.fit(X_train, y_train, use_ensemble='stacking')
```

### 3. Individual Models

Train models separately and average predictions:

```python
model.fit(X_train, y_train, use_ensemble='individual')
predictions = model.predict(X_test)  # Automatically averages
```

## Customization

### Adjust Model Parameters

```python
# Modify base models before training
model.create_base_models()

# Customize Random Forest
model.models['random_forest'].set_params(
    n_estimators=200,
    max_depth=20,
    min_samples_leaf=10
)

# Then fit
model.fit(X_train, y_train, use_ensemble='voting')
```

### Custom Features

Add your own feature engineering in `SchwabDataFetcher.create_features()`:

```python
def create_features(self, df):
    features_df = df.copy()
    # Add your custom features here
    features_df['custom_feature'] = ...
    return features_df
```

### Custom Meta-Learner for Stacking

```python
from sklearn.linear_model import LogisticRegression

# For classification
meta_learner = LogisticRegression(C=1.0, random_state=42)
model.create_stacking_ensemble(final_estimator=meta_learner)
model.fit(X_train, y_train, use_ensemble='stacking')
```

## Feature Importance

Get feature importance from trained models:

```python
# Random Forest feature importance
importance_df = model.get_feature_importance('random_forest')
print(importance_df.head(10))

# Gradient Boosting feature importance
importance_df = model.get_feature_importance('gradient_boosting')
print(importance_df.head(10))
```

## Evaluation Metrics

### Classification
- Accuracy
- AUC-ROC
- Classification Report (precision, recall, F1-score)
- Confusion Matrix

### Regression
- RMSE (Root Mean Squared Error)
- R² Score
- MSE (Mean Squared Error)

## Based on Book Methods

This implementation follows concepts from **"Machine Learning for Algorithmic Trading"** by Stefan Jansen:

- **Chapter 11**: Random Forests and Bagging
- **Chapter 12**: Gradient Boosting and AdaBoost
- Ensemble methods and their applications to trading
- Feature engineering for financial data
- Time-series cross-validation considerations

## Notes

1. **Time-Series Considerations**: The current implementation uses simple train-test split. For production use, consider time-series cross-validation (e.g., `TimeSeriesSplit` from sklearn).

2. **Data Requirements**: Requires sufficient historical data (minimum 100+ data points recommended).

3. **Overfitting**: Ensemble methods can overfit. Monitor performance on validation sets and consider regularization.

4. **Lookahead Bias**: Ensure forward returns are calculated correctly to avoid lookahead bias in backtesting.

5. **Market Conditions**: Model performance may vary with market conditions. Consider retraining periodically.

## Example Output

```
Ensemble Trading Model
============================================================

1. Initializing Schwab API client...
2. Fetching data...
   Fetched 252 data points for AAPL
3. Creating features...
   Created 35 features
4. Initializing ensemble model...
5. Preparing target variable...
   Training set: 162 samples
   Test set: 40 samples
   Positive class ratio: 45.68%

6. Training voting ensemble...
Training random_forest...
Training gradient_boosting...
Training adaboost...
Training bagging...

7. Evaluating on test set...
------------------------------------------------------------
Accuracy: 0.6750
AUC: 0.7125

Classification Report:
              precision    recall  f1-score   support
           0       0.65      0.72      0.68        18
           1       0.71      0.64      0.67        22
    accuracy                           0.68        40
   macro avg       0.68      0.68      0.68        40
weighted avg       0.68      0.68      0.68        40

8. Feature importance (Random Forest):
------------------------------------------------------------
        feature  importance
0    ma_20_ratio    0.145234
1   volatility_20    0.132156
2            rsi    0.098765
3    ma_50_ratio    0.087654
4          macd    0.076543
...

============================================================
Model training complete!
============================================================
```

## Next Steps

1. **Backtesting**: Implement proper time-series backtesting framework
2. **Hyperparameter Tuning**: Use GridSearchCV or RandomizedSearchCV
3. **Multiple Symbols**: Extend to portfolio of stocks
4. **Live Trading**: Integrate with order execution (use with caution!)
5. **Advanced Features**: Add more technical indicators, sentiment data, etc.

## Disclaimer

This is for educational and research purposes only. Past performance does not guarantee future results. Always use proper risk management and never invest more than you can afford to lose.


