"""
Alpha Trader Features - Based on "Alpha Trader" by Brent Donnelly

Key Concepts from the Book:
1. Market Regime Detection (Trending vs Range-bound vs Chaotic)
2. Volatility-based Risk Assessment (Order vs Chaos)
3. Risk Aversion Levels (Crisis vs Normal)
4. Position Sizing Signals based on Volatility
5. Sentiment Shifts and Narrative Changes
6. Technical Reference Points (Support/Resistance strength)
"""

import pandas as pd
import numpy as np
from scipy import stats


class AlphaTraderFeatures:
    """
    Generate alpha factors based on Alpha Trader methodology
    """
    
    def __init__(self):
        self.feature_names = []
    
    def _safe_int_convert(self, series):
        """
        Safely convert a boolean/float series to int, handling NaN/inf
        """
        return series.replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
    
    def calculate_all_features(self, df):
        """
        Calculate all Alpha Trader features
        
        Args:
            df: DataFrame with OHLCV data (must have 'close', 'high', 'low', 'open' columns)
            
        Returns:
            DataFrame with new alpha features added
        """
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Ensure we have required OHLCV columns
        required_cols = ['close', 'high', 'low', 'open']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # 1. Market Regime Detection
        df = self._add_market_regime_features(df)
        
        # 2. Volatility & Chaos Metrics
        df = self._add_volatility_chaos_features(df)
        
        # 3. Risk Aversion Indicators
        df = self._add_risk_aversion_features(df)
        
        # 4. Position Sizing Signals
        df = self._add_position_sizing_signals(df)
        
        # 5. Sentiment & Narrative
        df = self._add_sentiment_features(df)
        
        # 6. Technical Reference Strength
        df = self._add_technical_strength_features(df)
        
        # 7. Clean all Alpha Trader features (remove inf/nan)
        at_cols = [c for c in df.columns if c.startswith('at_')]
        for col in at_cols:
            # Replace inf with large numbers, nan with 0
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            
            # For binary columns (0 or 1), fill with 0
            if df[col].dropna().isin([0, 1]).all():
                df[col] = df[col].fillna(0).astype(int)
            else:
                # For continuous columns, fill with 0 and clip if needed
                df[col] = df[col].fillna(0)
                # Clip to reasonable range if it looks like it should be bounded
                if col.endswith('_score') or col.endswith('_percentile'):
                    df[col] = np.clip(df[col], 0, 1)
        
        return df
    
    def _add_market_regime_features(self, df):
        """
        Detect market regime: Trending vs Range-bound vs Chaotic
        Based on: Chapter 14 - "Order vs Chaos"
        """
        returns = df['close'].pct_change()
        
        # Trending Score (ADX-like)
        # High when strong trend, low when ranging
        high_low = df['high'] - df['low']
        close_prev = df['close'].shift(1)
        
        # Directional Movement
        up_move = df['high'] - df['high'].shift(1)
        down_move = df['low'].shift(1) - df['low']
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        atr_14 = high_low.rolling(14).mean()
        plus_di = 100 * pd.Series(plus_dm).rolling(14).mean() / atr_14
        minus_di = 100 * pd.Series(minus_dm).rolling(14).mean() / atr_14
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        adx = dx.rolling(14).mean()
        
        # Handle NaN/inf before converting
        adx_clean = adx.replace([np.inf, -np.inf], np.nan).fillna(0)
        df['at_trending_score'] = np.clip(adx_clean / 100, 0, 1)  # 0-1 scale
        df['at_is_trending'] = (adx_clean > 25).astype(int)  # Binary: trending or not
        
        # Use pandas methods to avoid length mismatch
        trend_strength = pd.Series(0, index=df.index)
        trend_strength[adx > 25] = 1  # Weak trend
        trend_strength[adx > 40] = 2  # Strong trend
        df['at_trend_strength'] = trend_strength
        
        # Range-bound Score
        # High when price oscillating in range
        bb_mid = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        bb_width = (bb_std / bb_mid) * 100
        
        df['at_rangebound_score'] = 1 / (1 + bb_width)  # Higher = more range-bound
        df['at_is_rangebound'] = self._safe_int_convert(adx < 20)
        
        # Chaos Score (Market turbulence)
        # High during flash crashes, crisis periods
        returns_std_20 = returns.rolling(20).std()
        returns_std_100 = returns.rolling(100).std()
        
        # Ratio of recent to long-term vol (>2 = chaos)
        vol_ratio = returns_std_20 / (returns_std_100 + 1e-10)
        df['at_chaos_score'] = np.clip(vol_ratio, 0, 5) / 5  # Normalize to 0-1
        df['at_is_chaotic'] = self._safe_int_convert(vol_ratio > 2)
        
        return df
    
    def _add_volatility_chaos_features(self, df):
        """
        Volatility-based features for risk management
        Based on: "Volatility and Risk Management" section
        """
        returns = df['close'].pct_change()
        
        # Current volatility vs historical
        vol_5 = returns.rolling(5).std() * np.sqrt(252)  # Annualized
        vol_20 = returns.rolling(20).std() * np.sqrt(252)
        vol_60 = returns.rolling(60).std() * np.sqrt(252)
        
        # Use pandas methods to avoid length mismatch
        vol_regime = pd.Series(0, index=df.index)
        vol_regime[vol_5 > vol_60] = 1  # Normal vol
        vol_regime[vol_5 > vol_60 * 1.5] = 2  # High vol
        df['at_vol_regime'] = vol_regime
        
        # Volatility percentile (where are we in historical range?)
        vol_100_pct = returns.rolling(100).apply(
            lambda x: stats.percentileofscore(x, x.iloc[-1]) / 100 if len(x) > 1 else 0.5
        )
        df['at_vol_percentile'] = vol_100_pct
        
        # Volatility expansion/contraction
        df['at_vol_expanding'] = self._safe_int_convert((vol_5 > vol_20) & (vol_20 > vol_60))
        df['at_vol_contracting'] = self._safe_int_convert((vol_5 < vol_20) & (vol_20 < vol_60))
        
        # Fast market indicator (high vol + wide spreads)
        high_low_pct = (df['high'] - df['low']) / df['close']
        df['at_fast_market'] = self._safe_int_convert(
            (vol_5 > vol_60 * 2) & (high_low_pct > high_low_pct.rolling(20).mean() * 1.5)
        )
        
        return df
    
    def _add_risk_aversion_features(self, df):
        """
        Detect crisis-level risk aversion vs normal conditions
        Based on: "No Overbought/Oversold in Crisis"
        """
        returns = df['close'].pct_change()
        
        # Extreme move detection
        returns_std = returns.rolling(100).std()
        z_score = (returns - returns.rolling(100).mean()) / (returns_std + 1e-10)
        
        df['at_extreme_down'] = self._safe_int_convert(z_score < -2)  # 2 std down
        df['at_extreme_up'] = self._safe_int_convert(z_score > 2)     # 2 std up
        df['at_z_score'] = np.clip(z_score, -5, 5) / 5      # Normalized
        
        # Drawdown from recent high (risk aversion proxy)
        rolling_max = df['close'].rolling(60, min_periods=1).max()
        drawdown = (df['close'] - rolling_max) / rolling_max
        
        df['at_drawdown'] = drawdown
        df['at_crisis_mode'] = self._safe_int_convert(drawdown < -0.15)  # 15%+ drawdown = crisis
        df['at_recovery_mode'] = self._safe_int_convert(
            (drawdown > -0.05) & (drawdown.shift(5) < -0.10)
        )  # Recovering
        
        # Gap risk (overnight gaps indicate panic)
        gap = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        gap_abs = np.abs(gap)
        
        df['at_gap_risk'] = gap_abs.rolling(20).mean()
        df['at_panic_gaps'] = self._safe_int_convert(gap_abs > gap_abs.rolling(100).quantile(0.95))
        
        return df
    
    def _add_position_sizing_signals(self, df):
        """
        Position sizing recommendations based on volatility
        Based on: "Adapting position size based on volatility"
        """
        returns = df['close'].pct_change()
        vol_20 = returns.rolling(20).std() * np.sqrt(252)
        vol_100 = returns.rolling(100).std() * np.sqrt(252)
        
        # Position size multiplier (1 = normal, <1 = reduce, >1 = increase)
        # Inverse relationship with volatility
        base_vol = vol_100.rolling(100).mean()
        size_multiplier = base_vol / (vol_20 + 1e-10)
        df['at_position_size'] = np.clip(size_multiplier, 0.25, 2.0)
        
        # Confidence score (based on regime clarity)
        adx = df.get('at_trending_score', 0.5)
        chaos = df.get('at_chaos_score', 0.5)
        
        # High confidence when: trending + low chaos
        # Low confidence when: ranging + high chaos
        df['at_confidence'] = (adx * (1 - chaos)).fillna(0.5)
        
        # Risk level recommendation (1-5, where 5 = lowest risk/smallest position)
        vol_pct = df.get('at_vol_percentile', 0.5)
        crisis = df.get('at_crisis_mode', 0)
        
        df['at_risk_level'] = self._safe_int_convert(
            np.clip((vol_pct * 3) + (crisis * 2), 1, 5)
        )
        
        return df
    
    def _add_sentiment_features(self, df):
        """
        Sentiment and momentum-based features
        Based on: "Understand Narrative" and "Sentiment Indicators"
        """
        returns = df['close'].pct_change()
        
        # Momentum persistence (how long has trend lasted?)
        returns_sign = np.sign(returns)
        streak = (returns_sign.groupby((returns_sign != returns_sign.shift()).cumsum()).cumcount() + 1)
        
        df['at_trend_days'] = streak
        df['at_extended_trend'] = self._safe_int_convert(streak > 10)
        
        # Momentum exhaustion (long trend + overbought)
        rsi_14 = self._calculate_rsi(df['close'], 14)
        df['at_momentum_exhaustion'] = self._safe_int_convert((streak > 7) & (rsi_14 > 70))
        df['at_oversold_bounce'] = self._safe_int_convert((streak > 5) & (rsi_14 < 30))
        
        # Narrative shift detection (momentum reversal)
        sma_20 = df['close'].rolling(20).mean()
        sma_50 = df['close'].rolling(50).mean()
        
        was_below = (sma_20.shift(1) < sma_50.shift(1))
        now_above = (sma_20 > sma_50)
        
        df['at_narrative_shift'] = self._safe_int_convert(was_below & now_above) - \
                                   self._safe_int_convert((~was_below) & (~now_above))
        
        # Sentiment score (-1 = bearish, 0 = neutral, 1 = bullish)
        price_vs_sma20 = (df['close'] - sma_20) / sma_20
        df['at_sentiment'] = np.clip(price_vs_sma20 * 10, -1, 1)
        
        return df
    
    def _add_technical_strength_features(self, df):
        """
        Technical reference point strength
        Based on: "Understand Technicals"
        """
        # Support/Resistance strength
        # How many times has price bounced off this level?
        
        close = df['close']
        
        # Find recent lows (support)
        rolling_low = close.rolling(20, min_periods=1).min()
        at_support = np.abs(close - rolling_low) / close < 0.02  # Within 2%
        support_tests = at_support.rolling(60).sum()
        
        df['at_support_strength'] = np.clip(support_tests / 5, 0, 1)
        df['at_at_support'] = self._safe_int_convert(at_support)
        
        # Find recent highs (resistance)
        rolling_high = close.rolling(20, min_periods=1).max()
        at_resistance = np.abs(close - rolling_high) / close < 0.02
        resistance_tests = at_resistance.rolling(60).sum()
        
        df['at_resistance_strength'] = np.clip(resistance_tests / 5, 0, 1)
        df['at_at_resistance'] = self._safe_int_convert(at_resistance)
        
        # Breakout potential
        # Strong when: near resistance + momentum + low chaos
        momentum_20 = (close - close.shift(20)) / close.shift(20)
        chaos = df.get('at_chaos_score', 0.5)
        
        df['at_breakout_potential'] = (
            at_resistance.astype(float) * 
            np.clip(momentum_20 * 10, 0, 1) * 
            (1 - chaos)
        )
        
        # Breakdown risk (inverse of breakout)
        df['at_breakdown_risk'] = (
            at_support.astype(float) * 
            np.clip(-momentum_20 * 10, 0, 1) * 
            (1 - chaos)
        )
        
        return df
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_feature_count(self, df):
        """Count Alpha Trader features"""
        at_features = [col for col in df.columns if col.startswith('at_')]
        return len(at_features)


def add_alpha_trader_features(df):
    """
    Convenience function to add all Alpha Trader features
    
    Usage:
        df = add_alpha_trader_features(df)
    """
    at = AlphaTraderFeatures()
    df = at.calculate_all_features(df)
    
    # Print summary
    feature_count = at.get_feature_count(df)
    print(f"✅ Added {feature_count} Alpha Trader features")
    
    return df


if __name__ == '__main__':
    # Test with sample data
    import yfinance as yf
    
    print("Testing Alpha Trader Features...")
    print("=" * 80)
    
    # Fetch test data
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="1y", interval="1d")
    df.columns = [c.lower() for c in df.columns]
    
    print(f"\nOriginal columns: {len(df.columns)}")
    print(f"Rows: {len(df)}")
    
    # Add features
    df = add_alpha_trader_features(df)
    
    print(f"\nAfter adding Alpha Trader features: {len(df.columns)} columns")
    
    # Show feature categories
    at_features = [col for col in df.columns if col.startswith('at_')]
    
    print(f"\n📊 Alpha Trader Features ({len(at_features)}):")
    print("-" * 80)
    
    categories = {
        'Market Regime': [f for f in at_features if 'trending' in f or 'rangebound' in f or 'chaos' in f or 'regime' in f],
        'Volatility': [f for f in at_features if 'vol_' in f or 'fast_market' in f],
        'Risk Aversion': [f for f in at_features if 'extreme' in f or 'crisis' in f or 'drawdown' in f or 'gap' in f or 'panic' in f],
        'Position Sizing': [f for f in at_features if 'position' in f or 'confidence' in f or 'risk_level' in f],
        'Sentiment': [f for f in at_features if 'sentiment' in f or 'narrative' in f or 'trend_days' in f or 'momentum' in f or 'oversold' in f],
        'Technical': [f for f in at_features if 'support' in f or 'resistance' in f or 'breakout' in f or 'breakdown' in f or 'z_score' in f]
    }
    
    for category, features in categories.items():
        print(f"\n{category} ({len(features)} features):")
        for f in features:
            print(f"   • {f}")
    
    # Show current values for latest bar
    print(f"\n📈 Latest Values (AAPL):")
    print("-" * 80)
    latest = df.iloc[-1]
    
    print(f"\nMarket Regime:")
    print(f"   Trending Score: {latest.get('at_trending_score', 0):.2f}")
    print(f"   Chaos Score: {latest.get('at_chaos_score', 0):.2f}")
    print(f"   Is Chaotic: {latest.get('at_is_chaotic', 0)}")
    
    print(f"\nRisk Assessment:")
    print(f"   Risk Level: {latest.get('at_risk_level', 3)}/5")
    print(f"   Confidence: {latest.get('at_confidence', 0):.2f}")
    print(f"   Crisis Mode: {latest.get('at_crisis_mode', 0)}")
    
    print(f"\nPosition Sizing:")
    print(f"   Recommended Size: {latest.get('at_position_size', 1):.2f}x")
    
    print("\n✅ Alpha Trader Features Test Complete!")

