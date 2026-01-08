"""
Risk Feature Integrator
Combines GARCH volatility and Copula correlation features with existing technical features
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ml_trading.models.garch_model import AdvancedVolatilityModeler
from ml_trading.models.copula_model import CopulaCorrelationModel


class RiskFeatureIntegrator:
    """
    Integrates risk features (GARCH + Copula) with existing technical features
    
    Adds 8 risk features:
    1. Predicted Volatility (GARCH forecast)
    2. VaR 95% (Value at Risk)
    3. VaR 99%
    4. CVaR 95% (Conditional VaR)
    5. Beta (with SPY)
    6. Correlation (with SPY)
    7. Sharpe Ratio
    8. Tail Dependence (crash correlation)
    """
    
    def __init__(self, spy_returns=None, qqq_returns=None):
        """
        Initialize risk feature integrator
        
        Args:
            spy_returns: SPY returns data (pandas Series)
            qqq_returns: QQQ returns data (optional, pandas Series)
        """
        self.garch_model = AdvancedVolatilityModeler()
        self.copula_model = CopulaCorrelationModel()
        self.spy_returns = spy_returns
        self.qqq_returns = qqq_returns
    
    def calculate_risk_features(self, stock_df, momentum_score=None):
        """
        Calculate all 8 risk features for a stock
        
        Args:
            stock_df: DataFrame with OHLCV data (must have 'close' column)
            momentum_score: Optional momentum score from Stage 1 (0-100)
        
        Returns:
            dict with 8+ risk features
        """
        # Calculate returns
        if 'returns' in stock_df.columns:
            returns = stock_df['returns'].dropna()
        else:
            returns = stock_df['close'].pct_change().dropna()
        
        if len(returns) < 50:
            # Not enough data, return default/null features
            return self._get_default_features()
        
        risk_features = {}
        
        # ========== GARCH FEATURES ==========
        try:
            # Forecast volatility
            vol_forecast = self.garch_model.forecast_volatility(returns, horizon=5)
            
            risk_features['predicted_volatility'] = vol_forecast['forecast_volatility']
            risk_features['annualized_volatility'] = vol_forecast['annualized_volatility']
            risk_features['volatility_regime'] = vol_forecast['volatility_regime']
            
            # VaR (Value at Risk)
            position_value = 10000  # Assume $10,000 position for calculation
            risk_features['var_95'] = self.garch_model.calculate_var(
                returns, vol_forecast['forecast_volatility'], 
                confidence=0.95, position_value=position_value
            )
            risk_features['var_99'] = self.garch_model.calculate_var(
                returns, vol_forecast['forecast_volatility'], 
                confidence=0.99, position_value=position_value
            )
            
            # CVaR (Conditional VaR / Expected Shortfall)
            risk_features['cvar_95'] = self.garch_model.calculate_cvar(returns, confidence=0.95)
            
        except Exception as e:
            print(f"  Warning: GARCH calculation failed: {e}")
            risk_features['predicted_volatility'] = returns.std()
            risk_features['annualized_volatility'] = returns.std() * np.sqrt(252)
            risk_features['volatility_regime'] = 'unknown'
            risk_features['var_95'] = 0.0
            risk_features['var_99'] = 0.0
            risk_features['cvar_95'] = 0.0
        
        # ========== COPULA FEATURES ==========
        try:
            if self.spy_returns is not None:
                # Align returns with market
                aligned_spy = self.spy_returns.reindex(returns.index).dropna()
                aligned_returns = returns.reindex(aligned_spy.index).dropna()
                
                if len(aligned_returns) >= 30:
                    # Beta
                    risk_features['beta_spy'] = self.copula_model.calculate_beta(
                        aligned_returns, aligned_spy
                    )
                    
                    # Correlation
                    risk_features['correlation_spy'] = self.copula_model.calculate_correlation(
                        aligned_returns, aligned_spy
                    )
                    
                    # Tail dependence
                    tail_deps = self.copula_model.calculate_tail_dependence(
                        aligned_returns, aligned_spy
                    )
                    risk_features['tail_dependence'] = tail_deps['lower_tail_dependence']
                    risk_features['crash_correlation'] = tail_deps['crash_correlation']
                else:
                    # Not enough aligned data
                    risk_features['beta_spy'] = 1.0
                    risk_features['correlation_spy'] = 0.0
                    risk_features['tail_dependence'] = 0.0
                    risk_features['crash_correlation'] = 'unknown'
            else:
                # No market data provided
                risk_features['beta_spy'] = 1.0
                risk_features['correlation_spy'] = 0.0
                risk_features['tail_dependence'] = 0.0
                risk_features['crash_correlation'] = 'unknown'
            
            # Sharpe Ratio
            risk_features['sharpe_ratio'] = self.copula_model.calculate_sharpe_ratio(returns)
            
        except Exception as e:
            print(f"  Warning: Copula calculation failed: {e}")
            risk_features['beta_spy'] = 1.0
            risk_features['correlation_spy'] = 0.0
            risk_features['tail_dependence'] = 0.0
            risk_features['crash_correlation'] = 'unknown'
            risk_features['sharpe_ratio'] = 0.0
        
        # ========== MOMENTUM INTEGRATION ==========
        if momentum_score is not None:
            risk_features['momentum_score'] = momentum_score
            risk_features['risk_adjusted_momentum'] = momentum_score * (1 / (1 + risk_features['predicted_volatility']))
        
        return risk_features
    
    def _get_default_features(self):
        """Return default features when data is insufficient"""
        return {
            'predicted_volatility': 0.02,
            'annualized_volatility': 0.32,
            'volatility_regime': 'unknown',
            'var_95': 0.0,
            'var_99': 0.0,
            'cvar_95': 0.0,
            'beta_spy': 1.0,
            'correlation_spy': 0.0,
            'tail_dependence': 0.0,
            'crash_correlation': 'unknown',
            'sharpe_ratio': 0.0
        }
    
    def add_risk_features_to_dataframe(self, features_df, momentum_score=None):
        """
        Add risk features as new columns to existing features DataFrame
        
        Args:
            features_df: DataFrame with existing technical features
            momentum_score: Optional momentum score
        
        Returns:
            DataFrame with risk features added
        """
        # Calculate risk features from the DataFrame
        risk_features = self.calculate_risk_features(features_df, momentum_score)
        
        # Add as new columns (use latest value for entire DataFrame)
        for feature_name, feature_value in risk_features.items():
            if not isinstance(feature_value, str):  # Skip categorical features
                features_df[f'risk_{feature_name}'] = feature_value
        
        return features_df
    
    def get_risk_score(self, risk_features):
        """
        Calculate overall risk score (1-10, higher = riskier)
        
        Based on:
        - Predicted volatility
        - VaR
        - Tail dependence
        
        Args:
            risk_features: Dict of risk features
        
        Returns:
            risk_score: 1-10 (1=low risk, 10=high risk)
        """
        score = 0.0
        
        # Volatility component (0-4 points)
        vol = risk_features.get('predicted_volatility', 0.02)
        if vol > 0.05:
            score += 4
        elif vol > 0.04:
            score += 3
        elif vol > 0.03:
            score += 2
        elif vol > 0.02:
            score += 1
        
        # VaR component (0-3 points)
        var_95 = risk_features.get('var_95', 0)
        if var_95 > 500:
            score += 3
        elif var_95 > 300:
            score += 2
        elif var_95 > 150:
            score += 1
        
        # Tail dependence component (0-3 points)
        tail_dep = risk_features.get('tail_dependence', 0)
        if tail_dep > 0.7:
            score += 3
        elif tail_dep > 0.5:
            score += 2
        elif tail_dep > 0.3:
            score += 1
        
        # Ensure score is between 1 and 10
        risk_score = max(1, min(10, int(np.ceil(score))))
        
        return risk_score


def test_integration():
    """Test risk feature integration"""
    print("Testing Risk Feature Integration...")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    n = 252
    dates = pd.date_range('2023-01-01', periods=n, freq='D')
    
    # Stock data
    stock_prices = 100 * np.exp(np.cumsum(np.random.randn(n) * 0.02))
    stock_df = pd.DataFrame({
        'close': stock_prices,
        'returns': pd.Series(stock_prices).pct_change()
    }, index=dates)
    
    # Market data (SPY)
    spy_prices = 400 * np.exp(np.cumsum(np.random.randn(n) * 0.015))
    spy_returns = pd.Series(spy_prices, index=dates).pct_change()
    
    # Initialize integrator
    print("\n1. Initializing Risk Feature Integrator...")
    integrator = RiskFeatureIntegrator(spy_returns=spy_returns)
    
    # Calculate risk features
    print("\n2. Calculating Risk Features...")
    risk_features = integrator.calculate_risk_features(stock_df, momentum_score=75)
    
    print("\n   Risk Features Generated:")
    for key, value in risk_features.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")
    
    # Calculate risk score
    print("\n3. Overall Risk Score:")
    risk_score = integrator.get_risk_score(risk_features)
    print(f"   Risk Score: {risk_score}/10")
    
    # Test DataFrame integration
    print("\n4. Testing DataFrame Integration...")
    features_df = stock_df.copy()
    enhanced_df = integrator.add_risk_features_to_dataframe(features_df, momentum_score=75)
    
    print(f"   Original columns: {len(stock_df.columns)}")
    print(f"   Enhanced columns: {len(enhanced_df.columns)}")
    print(f"   New risk columns: {len(enhanced_df.columns) - len(stock_df.columns)}")
    
    print("\n   New columns added:")
    risk_cols = [col for col in enhanced_df.columns if col.startswith('risk_')]
    for col in risk_cols:
        print(f"   - {col}")
    
    print("\n" + "=" * 60)
    print("✅ Risk feature integration test complete!")
    print("\n📊 Summary:")
    print(f"   - 8 core risk features generated")
    print(f"   - Risk score: {risk_score}/10")
    print(f"   - Ready for ensemble model integration")
    
    return integrator, risk_features, enhanced_df


if __name__ == '__main__':
    test_integration()

