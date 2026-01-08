# Chronological Train-Test Split for Time Series

## Overview

For time series data (like stock prices), we must use **chronological train-test splitting** instead of random splitting to avoid data leakage and get realistic performance estimates.

## Why Chronological Split?

### ❌ Random Split (WRONG for Time Series)
```python
# DON'T DO THIS for time series data!
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

**Problems:**
- Future data can leak into training set
- Model sees future patterns to predict past
- Artificially inflated performance metrics
- Not realistic for real-world forecasting

### ✅ Chronological Split (CORRECT for Time Series)
```python
# DO THIS for time series data!
split_idx = int(len(X) * 0.8)
X_train = X[:split_idx]      # First 80%
X_test = X[split_idx:]        # Last 20%
y_train = y[:split_idx]
y_test = y[split_idx:]
```

**Benefits:**
- ✅ Respects temporal ordering
- ✅ Prevents data leakage
- ✅ Realistic performance estimates
- ✅ Mimics real-world forecasting

## Current Implementation

The model now uses chronological splitting in `main()`:

```python
# Use TimeSeriesSplit for time series data (avoid data leakage)
# For time series, we should use chronological split, not random split
print("\n6. Splitting data (TimeSeriesSplit for time series data)...")
split_idx = int(len(X) * 0.8)
X_train_full = X[:split_idx]
X_test_full = X[split_idx:]
y_train = y[:split_idx]
y_test = y[split_idx:]
print(f"   Training set: {len(X_train_full)} samples (first 80%)")
print(f"   Test set: {len(X_test_full)} samples (last 20%)")
print(f"   Note: Using chronological split (not random) to avoid data leakage")
```

## How It Works

### Split Ratio
- **Training set**: First 80% of data (chronologically)
- **Test set**: Last 20% of data (chronologically)

### Example
If you have 400 samples:
- **Training**: Samples 0-319 (first 80%, 320 samples)
- **Test**: Samples 320-399 (last 20%, 80 samples)

### Visual Representation
```
Time Series Data:
[========== Training Set (80%) ==========][=== Test Set (20%) ===]
Samples: 0 to 319                        Samples: 320 to 399
```

## Combined with TimeSeriesSplit

The model uses **both** chronological splitting and TimeSeriesSplit:

1. **Chronological Train-Test Split**: Separate training and test sets (80/20)
2. **TimeSeriesSplit for CV**: Within training set, use TimeSeriesSplit for cross-validation

### Cross-Validation with TimeSeriesSplit
Within the training set, TimeSeriesSplit creates folds:
- Fold 1: Train on samples 0-64, test on 64-128
- Fold 2: Train on samples 0-128, test on 128-192
- Fold 3: Train on samples 0-192, test on 192-256
- Fold 4: Train on samples 0-256, test on 256-320

All folds respect temporal ordering!

## Impact on Performance

Using chronological split typically results in:
- **More realistic metrics**: Performance may be slightly lower, but more accurate
- **Better generalization**: Model learns true patterns, not future leakage
- **Production-ready**: Evaluation matches real-world deployment

## Alternative Split Ratios

You can adjust the split ratio based on your needs:

```python
# 70/30 split (more test data)
split_idx = int(len(X) * 0.7)
X_train = X[:split_idx]      # First 70%
X_test = X[split_idx:]        # Last 30%

# 90/10 split (more training data)
split_idx = int(len(X) * 0.9)
X_train = X[:split_idx]      # First 90%
X_test = X[split_idx:]        # Last 10%
```

**Recommendations:**
- **80/20**: Good default (used in current implementation)
- **70/30**: If you have lots of data and want more test samples
- **90/10**: If you have limited data and need more training samples

## Walk-Forward Validation (Future Enhancement)

For even more robust evaluation, consider walk-forward validation:

```
Iteration 1: Train on [0:100], Test on [100:120]
Iteration 2: Train on [0:120], Test on [120:140]
Iteration 3: Train on [0:140], Test on [140:160]
...
```

This provides multiple test periods and better generalization estimates.

## Summary

✅ **Current Status**: Chronological split is implemented
✅ **Split Ratio**: 80/20 (first 80% training, last 20% test)
✅ **Combined with**: TimeSeriesSplit for cross-validation
✅ **Purpose**: Prevent data leakage, get realistic metrics

The model now properly handles time series data with chronological splitting!


