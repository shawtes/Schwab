"""
Enhanced ML Pipeline with Risk Features
Integrates GARCH/Copula risk models with existing ensemble ML system
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ml_trading.pipeline.risk_feature_integrator import RiskFeatureIntegrator

try:
    from ensemble_trading_model import SchwabDataFetcher, EnsembleTradingModel
except ImportError:
    # For demo mode without full dependencies
    SchwabDataFetcher = None
    EnsembleTradingModel = None


class EnhancedMLPipeline:
    """
    Complete ML pipeline with risk-aware features
    
    Pipeline:
    1. Fetch stock data (existing: SchwabDataFetcher)
    2. Create technical features (existing: create_features)
    3. Add risk features (NEW: GARCH + Copula)
    4. Train/predict with ensemble (existing: EnsembleTradingModel)
    5. Generate risk-aware signals
    """
    
    def __init__(self, client, spy_data=None, qqq_data=None):
        """
        Initialize enhanced pipeline
        
        Args:
            client: Schwab API client
            spy_data: SPY historical data (for correlation)
            qqq_data: QQQ historical data (optional)
        """
        self.client = client
        self.fetcher = SchwabDataFetcher(client)
        
        # Get market returns for correlation
        spy_returns = None
        qqq_returns = None
        
        if spy_data is not None:
            spy_returns = spy_data['close'].pct_change().dropna()
        
        if qqq_data is not None:
            qqq_returns = qqq_data['close'].pct_change().dropna()
        
        self.risk_integrator = RiskFeatureIntegrator(
            spy_returns=spy_returns,
            qqq_returns=qqq_returns
        )
    
    def fetch_and_prepare_features(self, symbol, momentum_score=None):
        """
        Fetch data and prepare features with risk metrics
        
        Args:
            symbol: Stock symbol
            momentum_score: Momentum score from Stage 1 (0-100)
        
        Returns:
            features_df: DataFrame with 80+ technical + 8 risk features
        """
        print(f"\nProcessing {symbol}...")
        print("-" * 60)
        
        # Step 1: Fetch price data
        print("  1. Fetching price history...")
        df = self.fetcher.get_price_history(
            symbol, 
            periodType='year', 
            period=1, 
            frequencyType='daily', 
            frequency=1
        )
        
        if df is None or len(df) < 100:
            print(f"  ✗ Insufficient data for {symbol}")
            return None
        
        print(f"     ✓ Fetched {len(df)} bars")
        
        # Step 2: Create technical features
        print("  2. Creating technical features...")
        features_df = self.fetcher.create_features(df)
        
        if features_df is None or len(features_df) < 50:
            print(f"  ✗ Failed to create features for {symbol}")
            return None
        
        print(f"     ✓ Created {len(features_df.columns)} technical features")
        
        # Step 3: Add risk features (NEW!)
        print("  3. Adding risk features (GARCH + Copula)...")
        try:
            risk_features = self.risk_integrator.calculate_risk_features(
                features_df, momentum_score=momentum_score
            )
            
            # Add risk features as columns
            for key, value in risk_features.items():
                if isinstance(value, (int, float)):
                    features_df[f'risk_{key}'] = value
            
            # Calculate risk score
            risk_score = self.risk_integrator.get_risk_score(risk_features)
            features_df['risk_score'] = risk_score
            
            print(f"     ✓ Added 8 risk features")
            print(f"     ✓ Risk Score: {risk_score}/10")
            print(f"     ✓ Volatility: {risk_features['annualized_volatility']:.2%}")
            print(f"     ✓ Beta (SPY): {risk_features['beta_spy']:.2f}")
            print(f"     ✓ Sharpe Ratio: {risk_features['sharpe_ratio']:.2f}")
            
        except Exception as e:
            print(f"     ⚠ Warning: Risk features partially failed: {e}")
            # Continue without full risk features
        
        print(f"\n  Total Features: {len(features_df.columns)}")
        return features_df
    
    def train_ensemble_with_risk(self, symbol, momentum_score=None, 
                                  forward_periods=1, threshold=0.02):
        """
        Train ensemble model with risk-aware features
        
        Args:
            symbol: Stock symbol
            momentum_score: Momentum score (0-100)
            forward_periods: Periods ahead to predict
            threshold: Return threshold for classification
        
        Returns:
            model: Trained ensemble model
            test_results: Performance metrics
        """
        # Get features
        features_df = self.fetch_and_prepare_features(symbol, momentum_score)
        
        if features_df is None:
            return None, None
        
        # Initialize model
        print("\n4. Training ensemble model...")
        model = EnsembleTradingModel(
            task='classification',
            random_state=42,
            use_class_weight=True
        )
        
        # Prepare target
        target, valid_mask = model.prepare_target(
            features_df, 
            forward_periods=forward_periods, 
            threshold=threshold
        )
        features_df_valid = features_df[valid_mask]
        
        # Prepare features
        X = model.prepare_features(features_df_valid)
        y = target.values
        
        # Split data (80/20)
        split_idx = int(len(X) * 0.8)
        X_train = X[:split_idx]
        X_test = X[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        print(f"   Training set: {len(X_train)} samples")
        print(f"   Test set: {len(X_test)} samples")
        print(f"   Features: {X.shape[1]}")
        
        # Train
        model.fit(X_train, y_train, use_ensemble='stacking')
        
        # Evaluate
        print("\n5. Evaluating on test set...")
        test_results = model.evaluate(X_test, y_test, threshold=0.5)
        
        return model, test_results
    
    def generate_signal(self, features_df, model):
        """
        Generate trading signal with risk awareness
        
        Args:
            features_df: DataFrame with features
            model: Trained ensemble model
        
        Returns:
            dict with signal, confidence, risk_score
        """
        # Get latest features
        X = model.prepare_features(features_df.tail(1))
        
        # Predict
        probability = model.predict(X)[0]
        
        # Get risk score
        risk_score = features_df['risk_score'].iloc[-1] if 'risk_score' in features_df.columns else 5
        
        # Risk-aware decision rules
        # From architecture: BUY if confidence >= 0.7 AND risk_score <= 6
        if probability >= 0.7 and risk_score <= 6:
            signal = 'BUY'
        elif probability <= 0.3 and risk_score <= 6:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return {
            'signal': signal,
            'confidence': float(probability),
            'risk_score': int(risk_score),
            'recommended': signal if (probability >= 0.7 or probability <= 0.3) and risk_score <= 6 else 'HOLD'
        }


def demo_enhanced_pipeline():
    """Demo the enhanced ML pipeline"""
    print("=" * 70)
    print("Enhanced ML Pipeline Demo (with Risk Features)")
    print("=" * 70)
    
    # Note: This is a demo with simulated data
    # In production, use real Schwab client
    print("\n⚠️  Demo Mode: Using simulated data")
    print("   In production, initialize with real Schwab client\n")
    
    # Simulate data fetcher (without API)
    class MockFetcher:
        def get_price_history(self, *args, **kwargs):
            n = 252
            dates = pd.date_range('2023-01-01', periods=n, freq='D')
            prices = 100 * np.exp(np.cumsum(np.random.randn(n) * 0.02))
            return pd.DataFrame({
                'open': prices * 0.99,
                'high': prices * 1.01,
                'low': prices * 0.98,
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, n)
            }, index=dates)
        
        def create_features(self, df):
            features = df.copy()
            features['returns'] = features['close'].pct_change()
            features['rsi'] = 50 + np.random.randn(len(df)) * 10
            features['macd'] = np.random.randn(len(df)) * 0.5
            return features.dropna()
    
    # Create mock pipeline
    class MockPipeline:
        def __init__(self):
            self.fetcher = MockFetcher()
            spy_data = self.fetcher.get_price_history('SPY')
            spy_returns = spy_data['close'].pct_change().dropna()
            self.risk_integrator = RiskFeatureIntegrator(spy_returns=spy_returns)
    
    pipeline = MockPipeline()
    
    # Test feature generation
    print("\n" + "=" * 70)
    print("TEST: Generating Features with Risk Metrics")
    print("=" * 70)
    
    symbol = 'AAPL'
    momentum_score = 75
    
    # Fetch data
    df = pipeline.fetcher.get_price_history(symbol)
    print(f"\n✓ Fetched {len(df)} bars for {symbol}")
    
    # Create technical features
    features_df = pipeline.fetcher.create_features(df)
    print(f"✓ Created {len(features_df.columns)} technical features")
    
    # Add risk features
    risk_features = pipeline.risk_integrator.calculate_risk_features(
        features_df, momentum_score=momentum_score
    )
    
    for key, value in risk_features.items():
        if isinstance(value, (int, float)):
            features_df[f'risk_{key}'] = value
    
    risk_score = pipeline.risk_integrator.get_risk_score(risk_features)
    features_df['risk_score'] = risk_score
    
    print(f"✓ Added 8 risk features")
    print(f"\n📊 Risk Metrics:")
    print(f"   Volatility (Ann.): {risk_features['annualized_volatility']:.2%}")
    print(f"   VaR 95%: ${risk_features['var_95']:.2f}")
    print(f"   Beta (SPY): {risk_features['beta_spy']:.2f}")
    print(f"   Sharpe Ratio: {risk_features['sharpe_ratio']:.2f}")
    print(f"   Risk Score: {risk_score}/10")
    
    print(f"\n✅ Total Features: {len(features_df.columns)}")
    print(f"   - Technical: ~{len(features_df.columns) - 9}")
    print(f"   - Risk: 9")
    
    print("\n" + "=" * 70)
    print("✅ Enhanced ML Pipeline Ready!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. ✓ Risk models implemented (GARCH + Copula)")
    print("2. ✓ Risk features integrated with existing ML")
    print("3. → Train ensemble with enhanced features")
    print("4. → Test on real stocks with Schwab API")
    print("5. → Deploy for live trading")


if __name__ == '__main__':
    demo_enhanced_pipeline()

