"""
GARCH Volatility Model
Based on "Machine Learning for Financial Risk Management with Python" by Abdullah Karasan
Implements multiple GARCH variants for volatility forecasting
"""

import numpy as np
import pandas as pd
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')


class AdvancedVolatilityModeler:
    """
    Implements multiple GARCH variants for volatility modeling
    
    Models:
    - ARCH(p): Basic volatility clustering
    - GARCH(p,q): Lagged conditional variance
    - GJR-GARCH: Asymmetric volatility (leverage effect)
    - EGARCH: Exponential GARCH (log volatility)
    
    Based on: Chapter 4 - Machine Learning-Based Volatility Prediction
    """
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.fitted_model = None
    
    def select_best_model(self, returns, models=['GARCH', 'EGARCH', 'GJR-GARCH']):
        """
        Select best volatility model using BIC criterion
        
        Args:
            returns: pandas Series of historical returns
            models: List of model types to test
        
        Returns:
            best_model: Name of best model
            fitted_model: Fitted arch model object
        """
        if len(returns) < 50:
            raise ValueError(f"Insufficient data: {len(returns)} points (need at least 50)")
        
        # Remove NaN and infinite values
        returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(returns) < 50:
            raise ValueError("Insufficient valid data after cleaning")
        
        bic_scores = {}
        
        for model_type in models:
            try:
                if model_type == 'ARCH':
                    # Test different p values (1-5)
                    best_p = self._optimize_arch(returns)
                    model = arch_model(returns, vol='ARCH', p=best_p)
                    
                elif model_type == 'GARCH':
                    # Test GARCH(1,1) to GARCH(3,3)
                    best_p, best_q = self._optimize_garch(returns)
                    model = arch_model(returns, vol='Garch', p=best_p, q=best_q)
                    
                elif model_type == 'GJR-GARCH':
                    # Asymmetric GARCH for leverage effect
                    model = arch_model(returns, vol='GARCH', p=1, o=1, q=1)
                    
                elif model_type == 'EGARCH':
                    # Exponential GARCH (log volatility)
                    model = arch_model(returns, vol='EGARCH', p=1, q=1)
                else:
                    continue
                
                # Fit model
                result = model.fit(disp='off', show_warning=False)
                bic_scores[model_type] = result.bic
                self.models[model_type] = result
                
            except Exception as e:
                print(f"  Warning: {model_type} failed to fit: {e}")
                continue
        
        if not bic_scores:
            # Fallback to simple GARCH(1,1)
            print("  All models failed, using simple GARCH(1,1)")
            model = arch_model(returns, vol='Garch', p=1, q=1)
            result = model.fit(disp='off', show_warning=False)
            self.best_model = 'GARCH'
            self.fitted_model = result
            return 'GARCH', result
        
        # Select model with minimum BIC
        self.best_model = min(bic_scores, key=bic_scores.get)
        self.fitted_model = self.models[self.best_model]
        
        return self.best_model, self.fitted_model
    
    def _optimize_arch(self, returns):
        """Optimize ARCH lag order using BIC"""
        bic_scores = []
        for p in range(1, min(6, len(returns) // 20)):  # Ensure we have enough data
            try:
                model = arch_model(returns, vol='ARCH', p=p)
                result = model.fit(disp='off', show_warning=False)
                bic_scores.append((result.bic, p))
            except:
                continue
        
        if not bic_scores:
            return 1  # Default
        
        return min(bic_scores)[1]
    
    def _optimize_garch(self, returns):
        """Optimize GARCH orders using BIC"""
        best_bic = np.inf
        best_params = (1, 1)
        
        max_order = min(3, len(returns) // 30)  # Adjust based on data length
        
        for p in range(1, max_order + 1):
            for q in range(1, max_order + 1):
                try:
                    model = arch_model(returns, vol='Garch', p=p, q=q)
                    result = model.fit(disp='off', show_warning=False)
                    if result.bic < best_bic:
                        best_bic = result.bic
                        best_params = (p, q)
                except:
                    continue
        
        return best_params
    
    def forecast_volatility(self, returns, horizon=5):
        """
        Forecast volatility using best model
        
        Args:
            returns: pandas Series of historical returns
            horizon: Number of periods ahead to forecast
        
        Returns:
            dict with:
            - model: Best model name
            - forecast_volatility: Expected volatility
            - annualized_volatility: Annualized (252 trading days)
            - current_volatility: Current realized volatility
            - confidence_interval: (lower, upper) bounds
            - volatility_regime: 'low', 'normal', or 'high'
        """
        # Fit model if not already fitted
        if self.fitted_model is None:
            self.select_best_model(returns)
        
        # Forecast (use horizon=1 for EGARCH, simulation for others if needed)
        # EGARCH only supports analytic forecasts for horizon=1
        if self.best_model == 'EGARCH':
            forecast = self.fitted_model.forecast(horizon=1, reindex=False)
        else:
            # Other models can use longer horizons
            forecast = self.fitted_model.forecast(horizon=horizon, reindex=False)
        
        # Extract volatility forecast
        forecast_var = forecast.variance.iloc[-1]
        if isinstance(forecast_var, pd.Series):
            forecast_vol = np.sqrt(forecast_var.mean())
        else:
            forecast_vol = np.sqrt(forecast_var)
        
        # Current volatility
        current_vol = returns.std()
        
        # Annualized volatility (assuming 252 trading days)
        annualized_vol = forecast_vol * np.sqrt(252)
        
        # Confidence interval (approximate)
        ci_lower = forecast_vol * 0.8
        ci_upper = forecast_vol * 1.2
        
        # Volatility regime
        if forecast_vol > current_vol * 1.3:
            regime = 'high'
        elif forecast_vol < current_vol * 0.7:
            regime = 'low'
        else:
            regime = 'normal'
        
        return {
            'model': self.best_model,
            'forecast_volatility': float(forecast_vol),
            'annualized_volatility': float(annualized_vol),
            'current_volatility': float(current_vol),
            'confidence_interval': (float(ci_lower), float(ci_upper)),
            'volatility_regime': regime,
            'bic': float(self.fitted_model.bic) if hasattr(self.fitted_model, 'bic') else None
        }
    
    def calculate_var(self, returns, forecast_vol, confidence=0.95, position_value=1.0):
        """
        Calculate Value at Risk using GARCH forecast
        
        Args:
            returns: Historical returns
            forecast_vol: Forecasted volatility from GARCH
            confidence: Confidence level (0.95 or 0.99)
            position_value: Position size in dollars
        
        Returns:
            VaR at specified confidence level
        """
        from scipy import stats
        
        mean_return = returns.mean()
        z_score = stats.norm.ppf(1 - confidence)
        
        # VaR = -(mean + z * sigma) * position_value
        var = -(mean_return + z_score * forecast_vol) * position_value
        
        return float(var)
    
    def calculate_cvar(self, returns, confidence=0.95):
        """
        Calculate Conditional Value at Risk (Expected Shortfall)
        
        Args:
            returns: Historical returns
            confidence: Confidence level
        
        Returns:
            CVaR (average loss beyond VaR)
        """
        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        losses_beyond_var = returns[returns <= var_threshold]
        
        if len(losses_beyond_var) == 0:
            return 0.0
        
        cvar = -np.mean(losses_beyond_var)
        return float(cvar)


def test_garch_model():
    """Test GARCH model with sample data"""
    print("Testing GARCH Volatility Model...")
    print("=" * 60)
    
    # Generate sample returns
    np.random.seed(42)
    n = 252  # 1 year of daily data
    returns = pd.Series(np.random.randn(n) * 0.02)  # 2% daily volatility
    
    # Initialize model
    modeler = AdvancedVolatilityModeler()
    
    # Select best model
    print("\n1. Model Selection:")
    best_model, fitted = modeler.select_best_model(returns)
    print(f"   Best Model: {best_model}")
    print(f"   BIC: {fitted.bic:.2f}")
    
    # Forecast volatility
    print("\n2. Volatility Forecast:")
    forecast = modeler.forecast_volatility(returns, horizon=5)
    print(f"   Model: {forecast['model']}")
    print(f"   Forecast Volatility: {forecast['forecast_volatility']:.4f}")
    print(f"   Annualized Volatility: {forecast['annualized_volatility']:.2%}")
    print(f"   Current Volatility: {forecast['current_volatility']:.4f}")
    print(f"   Regime: {forecast['volatility_regime']}")
    print(f"   95% CI: ({forecast['confidence_interval'][0]:.4f}, {forecast['confidence_interval'][1]:.4f})")
    
    # Calculate risk metrics
    print("\n3. Risk Metrics:")
    var_95 = modeler.calculate_var(returns, forecast['forecast_volatility'], 
                                   confidence=0.95, position_value=10000)
    var_99 = modeler.calculate_var(returns, forecast['forecast_volatility'], 
                                   confidence=0.99, position_value=10000)
    cvar_95 = modeler.calculate_cvar(returns, confidence=0.95)
    
    print(f"   VaR 95%: ${var_95:.2f}")
    print(f"   VaR 99%: ${var_99:.2f}")
    print(f"   CVaR 95%: {cvar_95:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ GARCH model test complete!")
    
    return modeler, forecast


if __name__ == '__main__':
    test_garch_model()

