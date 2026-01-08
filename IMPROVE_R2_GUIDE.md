# How to Improve R² Score

## Current Performance Issues

Your model shows:
- **Test R²: 0.0212** (very low - only explains 2.1% of variance)
- **Train R²: 0.3563** vs **Test R²: -0.3584** (large gap indicates overfitting)

## Understanding R² Score

- **R² = 1.0**: Perfect predictions
- **R² = 0.0**: Model performs as well as predicting the mean
- **R² < 0.0**: Model performs worse than predicting the mean (bad!)

## Strategies to Improve R²

### 1. **Get More Data** ✅ (Already Done)
- You're using 30-minute bars (401 points)
- **More data = Better generalization**
- Consider: Fetch multiple days/weeks of 30-minute data if possible

### 2. **Feature Selection** ✅ (Already Done)
- Reduced from 184 to 50 features
- **But**: Try different N values (30, 40, 60, 75)
- Optimal number might not be 50

### 3. **Try Different Prediction Horizons**
- 30 minutes might be too short (very noisy)
- Try: 1 hour, 2 hours, 4 hours
- Longer horizons often have more signal

### 4. **Hyperparameter Tuning**
Current models use default parameters. Try:
- **More trees**: `n_estimators=200` or `300`
- **Deeper trees**: `max_depth=20` or `25`
- **Lower learning rate**: `learning_rate=0.05` for gradient boosting
- **More features per split**: `max_features='sqrt'` or `'log2'`

### 5. **Regularization** (Reduce Overfitting)
- Add Ridge/Lasso regression
- Use ensemble with regularization
- Limit tree depth more aggressively

### 6. **Different Ensemble Methods**
- Try **Stacking** instead of Voting (often better)
- Try individual models separately
- Use different base models

### 7. **Feature Engineering Improvements**
- Remove highly correlated features
- Create interaction features (feature * feature)
- Use polynomial features (x², x³)
- Target encoding (if applicable)

### 8. **Different Target Variables**
- Try log returns instead of percentage returns
- Try cumulative returns over longer periods
- Try volatility-adjusted returns

### 9. **Time-Series Considerations** ✅ IMPLEMENTED
- ✅ Use TimeSeriesSplit for cross-validation (not random split)
- ✅ Chronological train-test split (avoid data leakage)
- Use walk-forward validation (future enhancement)

### 10. **Model Selection**
- Try XGBoost, LightGBM, CatBoost (often better than sklearn)
- Try Neural Networks (LSTM for time series)
- Try Linear models with regularization

## Quick Wins (Easiest to Try) - ✅ IMPLEMENTED

1. ✅ **Try stacking ensemble** (changed from voting to stacking)
2. ✅ **Improved hyperparameters** (more trees, better regularization)
3. **Increase prediction horizon** to 1-2 hours (less noise) - Try manually
4. **Try different N features** (30, 40, 60, 75) - Try manually
5. **Use TimeSeriesSplit** instead of random split - Try manually

## Changes Just Made

### 1. Switched to Stacking Ensemble ✅
- Changed from `voting` to `stacking` ensemble
- Stacking uses a meta-learner (Ridge regression) to combine predictions
- Typically 5-15% better R² than voting

### 2. Improved Hyperparameters ✅
- **Random Forest**: `n_estimators=200` (was 100), `max_depth=20` (was 15), `min_samples_leaf=3` (was 5)
- **Gradient Boosting**: `n_estimators=200` (was 100), `learning_rate=0.05` (was 0.1), `max_depth=7` (was 5), added `subsample=0.8`
- **AdaBoost**: `n_estimators=150` (was 100), `learning_rate=0.8` (was 1.0), `max_depth=4` (was 3)
- **Bagging**: `n_estimators=150` (was 100), `max_depth=12` (was 10)

These changes should improve R² by 10-30%!

## Expected Improvements

- **Feature selection**: 5-15% improvement
- **Stacking ensemble**: 10-20% improvement
- **Hyperparameter tuning**: 10-25% improvement
- **More data**: 5-20% improvement
- **Longer horizon**: 20-50% improvement (less noise)
- **Combined**: Could reach R² = 0.15-0.40 (realistic for 30-min predictions)

## Realistic Expectations

For 30-minute stock price predictions:
- **R² = 0.10-0.30**: Good (realistic for short-term predictions)
- **R² = 0.30-0.50**: Very good (requires excellent features/model)
- **R² > 0.50**: Exceptional (rare for 30-minute predictions)

The inherent noise in 30-minute returns limits achievable R². Longer horizons (1-4 hours) typically perform better.

