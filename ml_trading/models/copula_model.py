"""
Copula Correlation Model
Based on "Machine Learning for Financial Risk Management with Python"
Models tail dependencies and correlation structures
"""

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class CopulaCorrelationModel:
    """
    Gaussian Copula Model for tail dependencies and correlations
    
    Purpose:
    - Model joint dependencies between assets
    - Capture tail dependencies (extreme event correlations)
    - Calculate Beta, correlation coefficients
    
    Based on: Chapter 7 - Gaussian Mixture Copula Model
    """
    
    def __init__(self):
        self.correlation_matrix = None
        self.fitted = False
    
    def fit_gaussian_copula(self, returns_stock, returns_spy, returns_qqq=None):
        """
        Fit Gaussian copula to model joint distribution
        
        Args:
            returns_stock: Stock returns (pandas Series)
            returns_spy: SPY returns (pandas Series)
            returns_qqq: QQQ returns (optional, pandas Series)
        
        Returns:
            correlation_matrix: Correlation matrix
        """
        # Align returns
        if returns_qqq is not None:
            df = pd.DataFrame({
                'stock': returns_stock,
                'spy': returns_spy,
                'qqq': returns_qqq
            }).dropna()
        else:
            df = pd.DataFrame({
                'stock': returns_stock,
                'spy': returns_spy
            }).dropna()
        
        if len(df) < 30:
            raise ValueError(f"Insufficient data: {len(df)} points (need at least 30)")
        
        # Calculate correlation matrix
        self.correlation_matrix = df.corr()
        self.fitted = True
        
        return self.correlation_matrix
    
    def calculate_beta(self, returns_stock, returns_market):
        """
        Calculate Beta (systematic risk measure)
        
        Beta = Cov(stock, market) / Var(market)
        
        Args:
            returns_stock: Stock returns
            returns_market: Market returns (SPY)
        
        Returns:
            beta: Beta coefficient
        """
        # Align returns
        df = pd.DataFrame({
            'stock': returns_stock,
            'market': returns_market
        }).dropna()
        
        if len(df) < 30:
            return 1.0  # Default to market beta
        
        # Calculate beta
        covariance = df['stock'].cov(df['market'])
        market_variance = df['market'].var()
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        
        return float(beta)
    
    def calculate_correlation(self, returns_stock, returns_market):
        """
        Calculate Pearson correlation coefficient
        
        Args:
            returns_stock: Stock returns
            returns_market: Market returns
        
        Returns:
            correlation: Correlation coefficient (-1 to 1)
        """
        df = pd.DataFrame({
            'stock': returns_stock,
            'market': returns_market
        }).dropna()
        
        if len(df) < 10:
            return 0.0
        
        correlation = df['stock'].corr(df['market'])
        
        return float(correlation) if not np.isnan(correlation) else 0.0
    
    def calculate_tail_dependence(self, returns_stock, returns_market, threshold=0.05):
        """
        Calculate tail dependence coefficients
        
        Measures probability of joint extreme events:
        - Lower tail: Probability both crash together
        - Upper tail: Probability both boom together
        
        Args:
            returns_stock: Stock returns
            returns_market: Market returns
            threshold: Percentile threshold (0.05 = 5th percentile)
        
        Returns:
            dict with lower_tail and upper_tail dependence
        """
        df = pd.DataFrame({
            'stock': returns_stock,
            'market': returns_market
        }).dropna()
        
        if len(df) < 50:
            return {
                'lower_tail_dependence': 0.0,
                'upper_tail_dependence': 0.0,
                'crash_correlation': 'unknown'
            }
        
        # Lower tail (crashes)
        stock_lower = df['stock'].quantile(threshold)
        market_lower = df['market'].quantile(threshold)
        
        both_crash = ((df['stock'] <= stock_lower) & (df['market'] <= market_lower)).sum()
        market_crash = (df['market'] <= market_lower).sum()
        
        lower_tail = both_crash / market_crash if market_crash > 0 else 0.0
        
        # Upper tail (booms)
        stock_upper = df['stock'].quantile(1 - threshold)
        market_upper = df['market'].quantile(1 - threshold)
        
        both_boom = ((df['stock'] >= stock_upper) & (df['market'] >= market_upper)).sum()
        market_boom = (df['market'] >= market_upper).sum()
        
        upper_tail = both_boom / market_boom if market_boom > 0 else 0.0
        
        # Classification
        crash_correlation = 'high' if lower_tail > 0.5 else 'moderate' if lower_tail > 0.3 else 'low'
        
        return {
            'lower_tail_dependence': float(lower_tail),
            'upper_tail_dependence': float(upper_tail),
            'crash_correlation': crash_correlation,
            'boom_correlation': 'high' if upper_tail > 0.5 else 'moderate' if upper_tail > 0.3 else 'low'
        }
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """
        Calculate Sharpe Ratio
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev
        
        Args:
            returns: pandas Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            sharpe_ratio: Risk-adjusted return metric
        """
        if len(returns) < 10:
            return 0.0
        
        # Annualized return and volatility
        mean_return = returns.mean() * 252  # Annualize
        volatility = returns.std() * np.sqrt(252)  # Annualize
        
        if volatility == 0:
            return 0.0
        
        sharpe = (mean_return - risk_free_rate) / volatility
        
        return float(sharpe)
    
    def generate_correlation_features(self, returns_stock, returns_spy, returns_qqq=None):
        """
        Generate all correlation-based features
        
        Args:
            returns_stock: Stock returns
            returns_spy: SPY returns
            returns_qqq: QQQ returns (optional)
        
        Returns:
            dict with all correlation features
        """
        features = {}
        
        # Beta
        features['beta_spy'] = self.calculate_beta(returns_stock, returns_spy)
        if returns_qqq is not None:
            features['beta_qqq'] = self.calculate_beta(returns_stock, returns_qqq)
        else:
            features['beta_qqq'] = None
        
        # Correlation
        features['correlation_spy'] = self.calculate_correlation(returns_stock, returns_spy)
        if returns_qqq is not None:
            features['correlation_qqq'] = self.calculate_correlation(returns_stock, returns_qqq)
        else:
            features['correlation_qqq'] = None
        
        # Tail dependencies
        tail_deps = self.calculate_tail_dependence(returns_stock, returns_spy)
        features['lower_tail_dependence'] = tail_deps['lower_tail_dependence']
        features['upper_tail_dependence'] = tail_deps['upper_tail_dependence']
        features['crash_correlation'] = tail_deps['crash_correlation']
        
        # Sharpe ratio
        features['sharpe_ratio'] = self.calculate_sharpe_ratio(returns_stock)
        
        return features


def test_copula_model():
    """Test Copula model with sample data"""
    print("Testing Copula Correlation Model...")
    print("=" * 60)
    
    # Generate sample returns
    np.random.seed(42)
    n = 252  # 1 year of daily data
    
    # Correlated returns (stock somewhat follows market)
    market_returns = pd.Series(np.random.randn(n) * 0.015, name='SPY')
    stock_returns = pd.Series(
        0.7 * market_returns + 0.3 * np.random.randn(n) * 0.02,
        name='STOCK'
    )
    qqq_returns = pd.Series(
        0.8 * market_returns + 0.2 * np.random.randn(n) * 0.018,
        name='QQQ'
    )
    
    # Initialize model
    copula = CopulaCorrelationModel()
    
    # Fit Gaussian copula
    print("\n1. Fitting Gaussian Copula:")
    corr_matrix = copula.fit_gaussian_copula(stock_returns, market_returns, qqq_returns)
    print("\n   Correlation Matrix:")
    print(corr_matrix)
    
    # Calculate Beta
    print("\n2. Beta Coefficients:")
    beta_spy = copula.calculate_beta(stock_returns, market_returns)
    beta_qqq = copula.calculate_beta(stock_returns, qqq_returns)
    print(f"   Beta (SPY): {beta_spy:.3f}")
    print(f"   Beta (QQQ): {beta_qqq:.3f}")
    
    # Correlation
    print("\n3. Correlations:")
    corr_spy = copula.calculate_correlation(stock_returns, market_returns)
    corr_qqq = copula.calculate_correlation(stock_returns, qqq_returns)
    print(f"   Correlation (SPY): {corr_spy:.3f}")
    print(f"   Correlation (QQQ): {corr_qqq:.3f}")
    
    # Tail dependencies
    print("\n4. Tail Dependencies:")
    tail_deps = copula.calculate_tail_dependence(stock_returns, market_returns)
    print(f"   Lower Tail (Crash): {tail_deps['lower_tail_dependence']:.3f} ({tail_deps['crash_correlation']})")
    print(f"   Upper Tail (Boom): {tail_deps['upper_tail_dependence']:.3f} ({tail_deps['boom_correlation']})")
    
    # Sharpe ratio
    print("\n5. Sharpe Ratio:")
    sharpe = copula.calculate_sharpe_ratio(stock_returns)
    print(f"   Sharpe Ratio: {sharpe:.3f}")
    
    # Generate all features
    print("\n6. All Correlation Features:")
    features = copula.generate_correlation_features(stock_returns, market_returns, qqq_returns)
    for key, value in features.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Copula model test complete!")
    
    return copula, features


if __name__ == '__main__':
    test_copula_model()

