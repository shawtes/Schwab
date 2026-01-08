#!/usr/bin/env python3
"""
ML Trading Quick Start - Integrated Book Methodologies
Based on "Machine Learning for Financial Risk Management with Python"

This script demonstrates the enhanced pipeline with:
- Advanced volatility models (GARCH variants)
- Market risk metrics (VaR, ES, LA-ES)
- Liquidity modeling (GMM)
- Copula correlation
- Fraud detection
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# STEP 1: Data Preparation
# ============================================================================

def fetch_sample_data(symbol='AAPL', days=500):
    """
    Fetch historical data for demonstration
    In production: Use Schwab API
    """
    print(f"📊 Fetching {days} days of data for {symbol}...")
    
    # For demo: Generate synthetic returns
    # In production: Replace with Schwab API call
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, days)
    
    # Create realistic price series
    prices = 100 * np.exp(np.cumsum(returns))
    
    # Create volume data
    volumes = np.random.lognormal(15, 0.5, days)
    
    df = pd.DataFrame({
        'date': pd.date_range(end=datetime.now(), periods=days),
        'close': prices,
        'returns': returns,
        'volume': volumes
    })
    
    print(f"✅ Loaded {len(df)} days of data")
    return df


# ============================================================================
# STEP 2: Advanced Volatility Modeling (GARCH)
# ============================================================================

def model_volatility_advanced(returns):
    """
    Implement GARCH family models with BIC selection
    Based on: Chapter 4 of Karasan
    """
    print("\n📈 STEP 2: Advanced Volatility Modeling")
    print("=" * 60)
    
    from arch import arch_model
    
    models = {}
    bic_scores = {}
    
    # Test multiple GARCH variants
    garch_configs = [
        ('ARCH', {'vol': 'ARCH', 'p': 2}),
        ('GARCH', {'vol': 'Garch', 'p': 1, 'q': 1}),
        ('GJR-GARCH', {'vol': 'GARCH', 'p': 1, 'o': 1, 'q': 1}),
        ('EGARCH', {'vol': 'EGARCH', 'p': 1, 'q': 1})
    ]
    
    print("\n🔍 Testing GARCH models:")
    for name, config in garch_configs:
        try:
            model = arch_model(returns, mean='Zero', **config)
            result = model.fit(disp='off')
            bic_scores[name] = result.bic
            models[name] = result
            print(f"  {name:15} BIC: {result.bic:.2f}")
        except Exception as e:
            print(f"  {name:15} Failed: {str(e)[:40]}")
    
    # Select best model
    best_model_name = min(bic_scores, key=bic_scores.get)
    best_model = models[best_model_name]
    
    print(f"\n✅ Best Model: {best_model_name} (BIC: {bic_scores[best_model_name]:.2f})")
    
    # Forecast volatility
    forecast = best_model.forecast(horizon=5)
    forecast_vol = np.sqrt(forecast.variance.values[-1, :].mean())
    
    print(f"📊 Forecasted Volatility: {forecast_vol:.4f}")
    print(f"📊 Annualized Vol: {forecast_vol * np.sqrt(252):.2%}")
    
    return {
        'best_model': best_model_name,
        'forecast_volatility': forecast_vol,
        'annualized_volatility': forecast_vol * np.sqrt(252),
        'bic_scores': bic_scores
    }


# ============================================================================
# STEP 3: Market Risk Metrics (VaR, ES, LA-ES)
# ============================================================================

def calculate_market_risk(returns, volume_data, confidence=0.95):
    """
    Calculate comprehensive market risk metrics
    Based on: Chapter 5 of Karasan
    """
    print("\n💰 STEP 3: Market Risk Metrics")
    print("=" * 60)
    
    from scipy import stats
    
    # 1. Value at Risk (VaR) - Three methods
    print("\n🎯 Value at Risk (VaR):")
    
    # Method 1: Variance-Covariance (Parametric)
    mu = np.mean(returns)
    sigma = np.std(returns)
    z_score = stats.norm.ppf(1 - confidence)
    var_parametric = -(mu + z_score * sigma)
    print(f"  Parametric VaR:  {var_parametric:.2%}")
    
    # Method 2: Historical Simulation
    var_historical = -np.percentile(returns, (1 - confidence) * 100)
    print(f"  Historical VaR:  {var_historical:.2%}")
    
    # Method 3: Monte Carlo
    n_sims = 10000
    sim_returns = np.random.normal(mu, sigma, n_sims)
    var_monte_carlo = -np.percentile(sim_returns, (1 - confidence) * 100)
    print(f"  Monte Carlo VaR: {var_monte_carlo:.2%}")
    
    # 2. Expected Shortfall (ES) / Conditional VaR
    print("\n📉 Expected Shortfall (ES):")
    var_threshold = np.percentile(returns, (1 - confidence) * 100)
    tail_losses = returns[returns <= var_threshold]
    es = -np.mean(tail_losses) if len(tail_losses) > 0 else 0
    print(f"  ES (CVaR):       {es:.2%}")
    print(f"  Tail events:     {len(tail_losses)} observations")
    
    # 3. Liquidity-Adjusted ES (LA-ES)
    print("\n💧 Liquidity-Adjusted Expected Shortfall:")
    
    # Liquidity metrics
    avg_volume = np.mean(volume_data)
    current_volume = volume_data.iloc[-1]
    volume_ratio = current_volume / avg_volume
    
    # Assume bid-ask spread (in production: fetch from API)
    bid_ask_spread = 0.001  # 0.1%
    
    # Liquidity adjustment factor
    liquidity_factor = (bid_ask_spread) * (1 / volume_ratio)
    la_es = es * (1 + liquidity_factor)
    
    print(f"  Base ES:         {es:.2%}")
    print(f"  Liquidity Adj:   {liquidity_factor:.4f}")
    print(f"  LA-ES:           {la_es:.2%}")
    print(f"  Volume Ratio:    {volume_ratio:.2f}x")
    
    return {
        'var_parametric': var_parametric,
        'var_historical': var_historical,
        'var_monte_carlo': var_monte_carlo,
        'expected_shortfall': es,
        'la_es': la_es,
        'liquidity_factor': liquidity_factor
    }


# ============================================================================
# STEP 4: Liquidity Modeling (GMM)
# ============================================================================

def model_liquidity(volume_data, returns):
    """
    Gaussian Mixture Model for liquidity classification
    Based on: Chapter 7 of Karasan
    """
    print("\n💧 STEP 4: Liquidity Modeling with GMM")
    print("=" * 60)
    
    from sklearn.mixture import GaussianMixture
    
    # Create liquidity features
    # Feature 1: Bid-ask spread proxy (volatility)
    bid_ask_proxy = returns.rolling(20).std().fillna(0)
    
    # Feature 2: Volume normalized
    volume_norm = (volume_data - volume_data.mean()) / volume_data.std()
    
    # Feature 3: Turnover (simplified)
    turnover = returns.abs() * volume_data
    turnover_norm = (turnover - turnover.mean()) / turnover.std()
    
    # Combine features
    X = np.column_stack([
        bid_ask_proxy[-100:],
        volume_norm[-100:],
        turnover_norm[-100:]
    ])
    
    # Fit GMM with 3 components (high, medium, low liquidity)
    gmm = GaussianMixture(n_components=3, covariance_type='full', random_state=42)
    gmm.fit(X)
    
    # Classify current state
    current_features = X[-1:, :]
    current_cluster = gmm.predict(current_features)[0]
    probabilities = gmm.predict_proba(current_features)[0]
    
    # Identify regimes (cluster with lowest spread = high liquidity)
    means = gmm.means_
    spread_means = means[:, 0]  # Bid-ask proxy
    sorted_idx = np.argsort(spread_means)
    
    regimes = {
        'high_liquidity': sorted_idx[0],
        'medium_liquidity': sorted_idx[1],
        'low_liquidity': sorted_idx[2]
    }
    
    # Determine current regime
    regime_names = ['high', 'medium', 'low']
    for regime_name, regime_idx in regimes.items():
        if current_cluster == regime_idx:
            current_regime = regime_name.replace('_liquidity', '')
            break
    
    print(f"\n🎯 Liquidity Classification:")
    print(f"  Current Regime:  {current_regime.upper()}")
    print(f"  Confidence:      {probabilities[current_cluster]:.1%}")
    print(f"\n📊 Regime Probabilities:")
    for i, prob in enumerate(probabilities):
        print(f"  Cluster {i}:      {prob:.1%}")
    
    return {
        'regime': current_regime,
        'confidence': probabilities[current_cluster],
        'cluster': int(current_cluster),
        'probabilities': probabilities.tolist()
    }


# ============================================================================
# STEP 5: Copula Correlation (Tail Dependence)
# ============================================================================

def calculate_tail_dependence(returns):
    """
    Calculate tail dependence using copulas
    Based on: Chapter 7 of Karasan
    """
    print("\n🔗 STEP 5: Copula Correlation Analysis")
    print("=" * 60)
    
    # Simulate SPY returns for demonstration
    # In production: Fetch real SPY data
    np.random.seed(42)
    spy_returns = returns + np.random.normal(0, 0.005, len(returns))
    
    # Calculate correlations
    pearson_corr = np.corrcoef(returns, spy_returns)[0, 1]
    
    # Tail dependence (simplified)
    # Lower tail: Both in bottom 5%
    stock_lower = returns <= np.percentile(returns, 5)
    spy_lower = spy_returns <= np.percentile(spy_returns, 5)
    lower_tail_dep = np.mean(stock_lower & spy_lower) / 0.05
    
    # Upper tail: Both in top 5%
    stock_upper = returns >= np.percentile(returns, 95)
    spy_upper = spy_returns >= np.percentile(spy_returns, 95)
    upper_tail_dep = np.mean(stock_upper & spy_upper) / 0.05
    
    print(f"\n📊 Correlation with SPY:")
    print(f"  Pearson Corr:    {pearson_corr:.3f}")
    print(f"  Lower Tail Dep:  {lower_tail_dep:.3f} (crash correlation)")
    print(f"  Upper Tail Dep:  {upper_tail_dep:.3f} (boom correlation)")
    
    crash_risk = "HIGH" if lower_tail_dep > 0.7 else "MEDIUM" if lower_tail_dep > 0.4 else "LOW"
    print(f"\n⚠️  Crash Correlation Risk: {crash_risk}")
    
    return {
        'pearson_correlation': pearson_corr,
        'lower_tail_dependence': lower_tail_dep,
        'upper_tail_dependence': upper_tail_dep,
        'crash_risk': crash_risk
    }


# ============================================================================
# STEP 6: Fraud Detection
# ============================================================================

def detect_trade_anomalies(returns, volume_data):
    """
    Anomaly detection for trade validation
    Based on: Chapter 8 of Karasan
    """
    print("\n🚨 STEP 6: Fraud Detection & Anomaly Analysis")
    print("=" * 60)
    
    from sklearn.ensemble import IsolationForest
    
    # Create trade features
    X = np.column_stack([
        returns[-100:],
        volume_data[-100:] / volume_data[-100:].mean(),
        returns[-100:].abs()
    ])
    
    # Fit Isolation Forest
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    iso_forest.fit(X)
    
    # Analyze recent trades
    recent_features = X[-10:, :]
    predictions = iso_forest.predict(recent_features)
    scores = iso_forest.score_samples(recent_features)
    
    anomalies = np.sum(predictions == -1)
    avg_score = np.mean(scores)
    
    print(f"\n🔍 Anomaly Detection Results:")
    print(f"  Recent Trades:   10")
    print(f"  Anomalies:       {anomalies}")
    print(f"  Avg Score:       {avg_score:.3f}")
    print(f"  Status:          {'⚠️  SUSPICIOUS' if anomalies > 2 else '✅ NORMAL'}")
    
    return {
        'anomalies_detected': int(anomalies),
        'average_score': float(avg_score),
        'is_suspicious': anomalies > 2
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Run complete enhanced ML pipeline
    """
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║     ENHANCED ML TRADING SYSTEM - BOOK INTEGRATION DEMO        ║")
    print("║   Machine Learning for Financial Risk Management with Python  ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    
    # Fetch data
    df = fetch_sample_data('AAPL', days=500)
    returns = df['returns'].values
    volume_data = df['volume']
    
    # Run all analysis steps
    results = {}
    
    try:
        results['volatility'] = model_volatility_advanced(returns)
    except Exception as e:
        print(f"\n⚠️  Volatility modeling error: {e}")
        results['volatility'] = {'error': str(e)}
    
    results['market_risk'] = calculate_market_risk(returns, volume_data)
    results['liquidity'] = model_liquidity(volume_data, pd.Series(returns))
    results['copula'] = calculate_tail_dependence(returns)
    results['fraud'] = detect_trade_anomalies(returns, volume_data.values)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL RISK ASSESSMENT SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ VOLATILITY:")
    if 'error' not in results['volatility']:
        print(f"  Model: {results['volatility']['best_model']}")
        print(f"  Annualized Vol: {results['volatility']['annualized_volatility']:.1%}")
    
    print(f"\n💰 MARKET RISK:")
    print(f"  VaR (95%): {results['market_risk']['var_parametric']:.2%}")
    print(f"  Expected Shortfall: {results['market_risk']['expected_shortfall']:.2%}")
    print(f"  LA-ES: {results['market_risk']['la_es']:.2%}")
    
    print(f"\n💧 LIQUIDITY:")
    print(f"  Regime: {results['liquidity']['regime'].upper()}")
    print(f"  Confidence: {results['liquidity']['confidence']:.1%}")
    
    print(f"\n🔗 CORRELATION:")
    print(f"  SPY Correlation: {results['copula']['pearson_correlation']:.3f}")
    print(f"  Crash Risk: {results['copula']['crash_risk']}")
    
    print(f"\n🚨 FRAUD CHECK:")
    print(f"  Status: {'⚠️  SUSPICIOUS' if results['fraud']['is_suspicious'] else '✅ CLEAN'}")
    
    # Trading recommendation
    print("\n" + "=" * 60)
    print("🎯 TRADING RECOMMENDATION")
    print("=" * 60)
    
    # Simple scoring
    risk_score = 0
    if results['market_risk']['la_es'] > 0.03:
        risk_score += 3
    if results['liquidity']['regime'] == 'low':
        risk_score += 2
    if results['copula']['crash_risk'] == 'HIGH':
        risk_score += 2
    if results['fraud']['is_suspicious']:
        risk_score += 3
    
    if risk_score <= 3:
        recommendation = "✅ LOW RISK - PROCEED WITH TRADE"
    elif risk_score <= 6:
        recommendation = "⚠️  MEDIUM RISK - REDUCE POSITION SIZE"
    else:
        recommendation = "🛑 HIGH RISK - HOLD OR EXIT"
    
    print(f"\n{recommendation}")
    print(f"Risk Score: {risk_score}/10")
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()


