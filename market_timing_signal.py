#!/usr/bin/env python3
"""
Market Timing Signal Generator
Provides clear, actionable BUY / WAIT / TAKE PROFITS signals based on market conditions
"""

from typing import Dict, Tuple

class MarketTimingSignal:
    """
    Generates clear market timing signals for trading decisions
    Based on: VIX level, SPY trend, regime analysis, yield curve
    """
    
    def __init__(self):
        self.signal_descriptions = {
            'STRONG_BUY': '🟢 STRONG BUY - Excellent entry conditions',
            'BUY': '🟢 BUY - Good entry opportunity',
            'CAUTIOUS_BUY': '🟡 CAUTIOUS BUY - Enter with smaller positions',
            'WAIT': '🟡 WAIT - Better entry opportunity coming',
            'HOLD': '🟠 HOLD - Not ideal for new entries',
            'TAKE_PROFITS': '🔴 TAKE PROFITS - Consider reducing exposure',
            'CRISIS': '🔴 CRISIS MODE - Preserve capital, wait'
        }
    
    def analyze_market_conditions(self, market_context: Dict) -> Dict:
        """
        Analyze market conditions and generate clear action signal
        
        Args:
            market_context: Dict with vix, spy_return_1d, regime, trend, etc.
        
        Returns:
            {
                'signal': 'STRONG_BUY' | 'BUY' | 'CAUTIOUS_BUY' | 'WAIT' | 'HOLD' | 'TAKE_PROFITS' | 'CRISIS',
                'action': 'BUY NOW' | 'WAIT FOR BETTER ENTRY' | 'TAKE PROFITS' | 'STOP - PRESERVE CAPITAL',
                'confidence': 0-100,
                'brief_reason': str,  # 1-2 sentences
                'position_sizing': 'FULL' | 'HALF' | 'SMALL' | 'NONE',
                'vix_level': float,
                'market_regime': str,
                'details': {
                    'vix_signal': str,
                    'trend_signal': str,
                    'regime_signal': str,
                    'volatility_signal': str
                }
            }
        """
        
        # Extract market data
        # Extract market data
        vix = market_context.get('vix_proxy') or market_context.get('vix')
        spy_return = market_context.get('spy_return_1d', 0.0)
        spy_vol = market_context.get('spy_vol_20', 0.015)
        regime = market_context.get('regime', 'neutral')
        trend = market_context.get('trend', 'sideways')
        yield_curve = market_context.get('yield_curve_slope', 0.0)
        
        # Handle None/Zero values
        if vix == 0:
            vix = None
        if spy_return is None:
            spy_return = 0.0
        if spy_vol is None:
            spy_vol = 0.015
            
        # Analyze each component
        vix_score, vix_signal = self._analyze_vix(vix)
        trend_score, trend_signal = self._analyze_trend(spy_return, trend)
        regime_score, regime_signal = self._analyze_regime(regime)
        vol_score, vol_signal = self._analyze_volatility(spy_vol)
        curve_score = self._analyze_yield_curve(yield_curve)
        
        # Calculate composite score (0-100)
        composite_score = (
            vix_score * 0.35 +      # VIX most important for timing
            trend_score * 0.30 +     # Trend strength
            regime_score * 0.20 +    # Regime quality
            vol_score * 0.10 +       # Volatility level
            curve_score * 0.05       # Yield curve (minor)
        )
        
        # Generate signal based on composite score
        signal, action, position_sizing = self._generate_signal(
            composite_score, vix, regime, trend
        )
        
        # Generate brief reason
        brief_reason = self._generate_reason(
            signal, vix, regime, trend, spy_return
        )
        
        return {
            'signal': signal,
            'action': action,
            'confidence': int(composite_score),
            'brief_reason': brief_reason,
            'position_sizing': position_sizing,
            'vix_level': round(vix, 2) if vix else None,
            'market_regime': regime,
            'spy_return_1d': round(spy_return * 100, 2),
            'details': {
                'vix_signal': vix_signal,
                'trend_signal': trend_signal,
                'regime_signal': regime_signal,
                'volatility_signal': vol_signal,
                'composite_score': round(composite_score, 1)
            }
        }
    
    def _analyze_vix(self, vix: float) -> Tuple[float, str]:
        """Analyze VIX level and return score (0-100) and signal"""
        if vix is None:
            return 50, "VIX Unavailable - Neutral"
            
        if vix < 12:
            return 100, "Extremely calm (VIX < 12) - Complacent"
        elif vix < 15:
            return 95, "Very calm (VIX 12-15) - Excellent entry"
        elif vix < 20:
            return 85, "Calm (VIX 15-20) - Good conditions"
        elif vix < 25:
            return 60, "Elevated (VIX 20-25) - Cautious"
        elif vix < 30:
            return 40, "High (VIX 25-30) - Wait for clarity"
        elif vix < 40:
            return 20, "Very high (VIX 30-40) - Crisis building"
        else:
            return 5, "Extreme (VIX > 40) - Crisis mode"
    
    def _analyze_trend(self, spy_return: float, trend: str) -> Tuple[float, str]:
        """Analyze market trend and return score"""
        if trend == 'up' or spy_return > 0.01:
            return 90, "Strong uptrend"
        elif trend == 'up' or spy_return > 0.003:
            return 75, "Moderate uptrend"
        elif trend == 'sideways' or abs(spy_return) < 0.003:
            return 50, "Sideways consolidation"
        elif trend == 'down' or spy_return < -0.01:
            return 20, "Strong downtrend"
        else:
            return 40, "Weak downtrend"
    
    def _analyze_regime(self, regime: str) -> Tuple[float, str]:
        """Analyze market regime"""
        regime_lower = str(regime).lower()
        if 'bull' in regime_lower:
            return 90, "Bullish regime"
        elif 'neutral' in regime_lower or 'mixed' in regime_lower:
            return 50, "Neutral regime"
        elif 'bear' in regime_lower:
            return 20, "Bearish regime"
        else:
            return 50, "Unknown regime"
    
    def _analyze_volatility(self, spy_vol: float) -> Tuple[float, str]:
        """Analyze volatility level"""
        if spy_vol < 0.01:
            return 90, "Low volatility"
        elif spy_vol < 0.015:
            return 75, "Normal volatility"
        elif spy_vol < 0.025:
            return 50, "Elevated volatility"
        else:
            return 30, "High volatility"
    
    def _analyze_yield_curve(self, slope: float) -> float:
        """Analyze yield curve (minor factor)"""
        if slope > 1.0:
            return 80  # Steep positive curve = healthy
        elif slope > 0:
            return 60  # Positive but flat
        elif slope > -0.5:
            return 40  # Slightly inverted
        else:
            return 20  # Deep inversion = recession risk
    
    def _generate_signal(
        self, 
        score: float, 
        vix: float, 
        regime: str, 
        trend: str
    ) -> Tuple[str, str, str]:
        """Generate signal, action, and position sizing based on score"""
        
        # Crisis override (VIX > 35 regardless of score)
        if vix and vix > 35:
            return 'CRISIS', 'STOP - PRESERVE CAPITAL', 'NONE'
        
        # Score-based signals
        if score >= 85:
            return 'STRONG_BUY', 'BUY NOW', 'FULL'
        elif score >= 70:
            return 'BUY', 'BUY NOW', 'FULL'
        elif score >= 55:
            return 'CAUTIOUS_BUY', 'BUY WITH CAUTION', 'HALF'
        elif score >= 45:
            return 'WAIT', 'WAIT FOR BETTER ENTRY', 'SMALL'
        elif score >= 30:
            return 'HOLD', 'WAIT FOR BETTER ENTRY', 'NONE'
        else:
            return 'TAKE_PROFITS', 'TAKE PROFITS / REDUCE EXPOSURE', 'NONE'
    
    def _generate_reason(
        self,
        signal: str,
        vix: float,
        regime: str,
        trend: str,
        spy_return: float
    ) -> str:
        """Generate brief reason for the signal"""
        
        vix_str = f"{vix:.1f}" if vix else "N/A"
        
        if signal == 'STRONG_BUY':
            return f"Low VIX ({vix_str}), {regime} regime, {trend} trend. Ideal entry conditions."
        
        elif signal == 'BUY':
            return f"VIX {vix_str}, {regime} regime. Good risk/reward for new positions."
        
        elif signal == 'CAUTIOUS_BUY':
            return f"VIX {vix_str}. Enter with smaller positions, scale as conditions improve."
        
        elif signal == 'WAIT':
            return f"VIX {vix_str}, mixed signals. Wait for better entry opportunity."
        
        elif signal == 'HOLD':
            return f"Elevated VIX ({vix_str}), uncertain trend. Not ideal for new entries."
        
        elif signal == 'TAKE_PROFITS':
            return f"High VIX ({vix_str}), negative trend. Consider taking profits."
        
        elif signal == 'CRISIS':
            return f"Crisis level VIX ({vix_str}). Preserve capital, wait for stabilization."
        
        else:
            return f"VIX {vix_str}, {regime} regime, {trend} trend."
    
    def format_for_display(self, timing_signal: Dict) -> str:
        """Format timing signal for terminal display"""
        signal = timing_signal['signal']
        action = timing_signal['action']
        confidence = timing_signal['confidence']
        reason = timing_signal['brief_reason']
        position_sizing = timing_signal['position_sizing']
        
        emoji = self.signal_descriptions.get(signal, signal).split()[0]
        
        output = f"\n{'=' * 70}\n"
        output += f"{emoji} MARKET TIMING SIGNAL: {action}\n"
        output += f"{'=' * 70}\n"
        output += f"Signal: {signal} (Confidence: {confidence}%)\n"
        output += f"Position Sizing: {position_sizing}\n"
        output += f"Reason: {reason}\n"
        output += f"\nMarket Conditions:\n"
        output += f"  VIX: {timing_signal['vix_level']}\n"
        output += f"  SPY 1D Return: {timing_signal['spy_return_1d']}%\n"
        output += f"  Regime: {timing_signal['market_regime']}\n"
        output += f"{'=' * 70}\n"
        
        return output
    
    def format_for_excel(self, timing_signal: Dict) -> Dict:
        """Format timing signal for Excel export"""
        return {
            'Market_Signal': timing_signal['signal'],
            'Action': timing_signal['action'],
            'Position_Sizing': timing_signal['position_sizing'],
            'Confidence': f"{timing_signal['confidence']}%",
            'VIX_Level': timing_signal['vix_level'],
            'SPY_Return_1D': f"{timing_signal['spy_return_1d']}%",
            'Market_Regime': timing_signal['market_regime'],
            'Reason': timing_signal['brief_reason']
        }


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Market Timing Signal Generator\n")
    
    signal_gen = MarketTimingSignal()
    
    # Test different market conditions
    test_scenarios = [
        {
            'name': 'Bull Market - Low VIX',
            'context': {'vix_proxy': 14.5, 'spy_return_1d': 0.008, 'regime': 'bullish', 'trend': 'up'}
        },
        {
            'name': 'Normal Market',
            'context': {'vix_proxy': 18.0, 'spy_return_1d': 0.002, 'regime': 'neutral', 'trend': 'sideways'}
        },
        {
            'name': 'Elevated Volatility',
            'context': {'vix_proxy': 28.0, 'spy_return_1d': -0.005, 'regime': 'bearish', 'trend': 'down'}
        },
        {
            'name': 'Crisis',
            'context': {'vix_proxy': 45.0, 'spy_return_1d': -0.025, 'regime': 'bearish', 'trend': 'down'}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        result = signal_gen.analyze_market_conditions(scenario['context'])
        print(signal_gen.format_for_display(result))
