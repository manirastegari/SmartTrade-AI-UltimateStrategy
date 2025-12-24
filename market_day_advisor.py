#!/usr/bin/env python3
"""
Market Day Advisor - Honest Trading Day Assessments
Provides clear "Skip Today" warnings and actionable guidance
"""

from typing import Dict, Optional, Tuple
from datetime import datetime


class MarketDayAdvisor:
    """
    Generates honest, actionable trading day assessments.
    Includes "Skip Today" warnings when conditions are unfavorable.
    """
    
    def __init__(self):
        # Thresholds for different warning levels
        self.vix_danger = 25.0      # VIX above this = high danger
        self.vix_caution = 18.0     # VIX above this = caution
        self.vix_optimal = 15.0     # VIX below this = favorable
        
        self.spy_crash = -0.02      # SPY down 2%+ = danger
        self.spy_weak = -0.01       # SPY down 1%+ = caution
        
    def analyze_trading_conditions(self, market_context: Dict) -> Dict:
        """
        Analyze market conditions and generate honest assessment.
        
        Args:
            market_context: Dict with vix, spy_return_1d, regime, trend, etc.
            
        Returns:
            {
                'action': 'TRADE' | 'CAUTION' | 'SKIP',
                'confidence': float (0-100),
                'skip_today': bool,
                'warning_level': 'GREEN' | 'YELLOW' | 'RED',
                'honest_assessment': str,
                'reasons': list[str],
                'next_check': str,
                'position_sizing': str,
                'strategy_focus': str
            }
        """
        vix = market_context.get('vix') or market_context.get('vix_level', 15.0)
        spy_return = market_context.get('spy_return_1d', 0.0)
        regime = market_context.get('regime', 'neutral').lower()
        trend = market_context.get('trend', 'sideways').lower()
        
        # Calculate component scores
        vix_score, vix_signal = self._analyze_vix(vix)
        trend_score, trend_signal = self._analyze_trend(spy_return, trend)
        regime_score, regime_signal = self._analyze_regime(regime)
        
        # Composite score (weighted)
        composite_score = (vix_score * 0.4) + (trend_score * 0.35) + (regime_score * 0.25)
        
        # Determine action and warning level
        action, warning_level, skip_today = self._determine_action(
            composite_score, vix, spy_return, regime
        )
        
        # Generate honest assessment
        honest_assessment = self._generate_honest_assessment(
            action, vix, spy_return, regime, trend, composite_score
        )
        
        # Collect reasons
        reasons = self._collect_reasons(vix_signal, trend_signal, regime_signal)
        
        # Position sizing recommendation
        position_sizing = self._recommend_position_sizing(action, composite_score)
        
        # Strategy focus
        strategy_focus = self._recommend_strategy_focus(action, regime, vix)
        
        # Next check recommendation
        next_check = self._recommend_next_check(action, vix)
        
        return {
            'action': action,
            'confidence': round(composite_score, 1),
            'skip_today': skip_today,
            'warning_level': warning_level,
            'honest_assessment': honest_assessment,
            'reasons': reasons,
            'next_check': next_check,
            'position_sizing': position_sizing,
            'strategy_focus': strategy_focus,
            'vix': vix,
            'spy_return': spy_return,
            'regime': regime,
            'trend': trend
        }
    
    def _analyze_vix(self, vix: float) -> Tuple[float, str]:
        """Analyze VIX and return score + signal"""
        if vix is None:
            return 50.0, "VIX data unavailable"
        
        if vix >= self.vix_danger:
            return 20.0, f"🔴 VIX at {vix:.1f} (DANGER: extreme fear)"
        elif vix >= self.vix_caution:
            return 45.0, f"🟡 VIX at {vix:.1f} (elevated anxiety)"
        elif vix >= self.vix_optimal:
            return 65.0, f"🟢 VIX at {vix:.1f} (moderate, watchful)"
        else:
            return 85.0, f"🟢 VIX at {vix:.1f} (calm, favorable)"
    
    def _analyze_trend(self, spy_return: float, trend: str) -> Tuple[float, str]:
        """Analyze market trend and return score + signal"""
        if spy_return is None:
            spy_return = 0.0
            
        if spy_return <= self.spy_crash:
            return 15.0, f"🔴 SPY down {abs(spy_return)*100:.1f}% (significant selloff)"
        elif spy_return <= self.spy_weak:
            return 40.0, f"🟡 SPY down {abs(spy_return)*100:.1f}% (weakness)"
        elif spy_return < 0.005:
            return 55.0, f"🟡 SPY flat ({spy_return*100:+.2f}%) (sideways chop)"
        elif spy_return < 0.01:
            return 70.0, f"🟢 SPY up {spy_return*100:.2f}% (mild strength)"
        else:
            return 85.0, f"🟢 SPY up {spy_return*100:.2f}% (strong momentum)"
    
    def _analyze_regime(self, regime: str) -> Tuple[float, str]:
        """Analyze market regime and return score + signal"""
        regime_scores = {
            'bull': (90.0, "🟢 Bull market regime (favorable)"),
            'risk-on': (85.0, "🟢 Risk-on environment (growth favored)"),
            'neutral': (60.0, "🟡 Neutral regime (selective)"),
            'caution': (40.0, "🟡 Caution regime (defensive only)"),
            'fear': (25.0, "🔴 Fear regime (avoid new positions)"),
            'bear': (20.0, "🔴 Bear market regime (cash preferred)"),
            'crisis': (10.0, "🔴 Crisis regime (preservation mode)")
        }
        return regime_scores.get(regime, (50.0, f"🟡 {regime.title()} regime"))
    
    def _determine_action(self, score: float, vix: float, spy_return: float, regime: str) -> Tuple[str, str, bool]:
        """Determine action, warning level, and skip flag"""
        
        # Hard skip conditions (override everything)
        if vix and vix >= 30:
            return 'SKIP', 'RED', True
        if spy_return and spy_return <= -0.03:
            return 'SKIP', 'RED', True
        if regime in ['crisis', 'bear']:
            return 'SKIP', 'RED', True
            
        # Score-based determination
        if score >= 70:
            return 'TRADE', 'GREEN', False
        elif score >= 50:
            return 'CAUTION', 'YELLOW', False
        elif score >= 35:
            return 'CAUTION', 'YELLOW', False
        else:
            return 'SKIP', 'RED', True
    
    def _generate_honest_assessment(self, action: str, vix: float, spy_return: float, 
                                    regime: str, trend: str, score: float) -> str:
        """Generate plain-language honest assessment"""
        
        if action == 'SKIP':
            return (
                f"Market conditions are unfavorable today. "
                f"VIX at {vix:.1f} with {regime} regime suggests elevated risk. "
                f"New positions likely to face headwinds. "
                f"Consider waiting for stabilization before deploying capital."
            )
        elif action == 'CAUTION':
            return (
                f"Mixed signals today - proceed with reduced position sizes. "
                f"VIX at {vix:.1f} is manageable but {regime} regime warrants selectivity. "
                f"Focus on defensive, high-quality names only. "
                f"Avoid aggressive entries; scale in gradually."
            )
        else:  # TRADE
            return (
                f"Conditions are favorable for trading today. "
                f"VIX at {vix:.1f} with {regime} regime supports risk-taking. "
                f"Full position sizing appropriate for high-conviction picks. "
                f"Both momentum and value strategies can work."
            )
    
    def _collect_reasons(self, *signals) -> list:
        """Collect all non-empty reason signals"""
        return [s for s in signals if s]
    
    def _recommend_position_sizing(self, action: str, score: float) -> str:
        """Recommend position sizing based on conditions"""
        if action == 'SKIP':
            return "NO NEW POSITIONS - Wait for better conditions"
        elif action == 'CAUTION':
            if score >= 45:
                return "HALF POSITIONS - Scale in gradually"
            else:
                return "QUARTER POSITIONS - Minimal exposure only"
        else:
            if score >= 80:
                return "FULL POSITIONS - High conviction appropriate"
            else:
                return "STANDARD POSITIONS - Normal allocation"
    
    def _recommend_strategy_focus(self, action: str, regime: str, vix: float) -> str:
        """Recommend which strategy type to focus on"""
        if action == 'SKIP':
            return "NONE - Preserve capital"
        elif action == 'CAUTION':
            return "DEFENSIVE ONLY - Consumer staples, utilities, healthcare, dividends"
        else:
            if regime in ['bull', 'risk-on']:
                return "GROWTH + MOMENTUM - Tech, financials, consumer discretionary"
            else:
                return "BALANCED - Mix of quality growth and defensive value"
    
    def _recommend_next_check(self, action: str, vix: float) -> str:
        """Recommend when to check again"""
        if action == 'SKIP':
            if vix and vix >= 25:
                return "Check again when VIX drops below 20"
            else:
                return "Check again tomorrow morning"
        elif action == 'CAUTION':
            return "Monitor intraday; reassess if conditions improve"
        else:
            return "Weekly check recommended (2-3x/week optimal)"
    
    def format_for_display(self, assessment: Dict) -> str:
        """Format assessment for terminal/console display"""
        action = assessment['action']
        warning = assessment['warning_level']
        
        # Color-coded header
        if warning == 'RED':
            header = "🔴 SKIP TODAY - Market conditions unfavorable"
            border = "━" * 70
        elif warning == 'YELLOW':
            header = "🟡 CAUTION - Proceed with reduced exposure"
            border = "─" * 70
        else:
            header = "🟢 FAVORABLE - Good conditions for trading"
            border = "═" * 70
        
        output = f"""
{border}
{header} (Confidence: {assessment['confidence']:.0f}%)
{border}

📊 MARKET STATE:
   VIX: {assessment.get('vix', 'N/A')}
   SPY: {assessment.get('spy_return', 0)*100:+.2f}%
   Regime: {assessment.get('regime', 'Unknown').title()}

💡 HONEST TAKE:
   {assessment['honest_assessment']}

📋 SIGNALS:
"""
        for reason in assessment['reasons']:
            output += f"   • {reason}\n"
        
        output += f"""
🎯 RECOMMENDATION:
   Position Sizing: {assessment['position_sizing']}
   Strategy Focus: {assessment['strategy_focus']}
   
📅 NEXT CHECK: {assessment['next_check']}
{border}
"""
        return output
    
    def format_for_excel(self, assessment: Dict) -> Dict:
        """Format assessment for Excel export"""
        return {
            'trading_action': assessment['action'],
            'warning_level': assessment['warning_level'],
            'skip_today': 'YES' if assessment['skip_today'] else 'NO',
            'confidence': assessment['confidence'],
            'honest_assessment': assessment['honest_assessment'],
            'position_sizing': assessment['position_sizing'],
            'strategy_focus': assessment['strategy_focus'],
            'next_check': assessment['next_check'],
            'vix_level': assessment.get('vix', 'N/A'),
            'spy_return_pct': f"{assessment.get('spy_return', 0)*100:+.2f}%",
            'market_regime': assessment.get('regime', 'Unknown').title()
        }
    
    def format_for_streamlit(self, assessment: Dict) -> Dict:
        """Format assessment for Streamlit UI display"""
        action = assessment['action']
        warning = assessment['warning_level']
        
        # Determine banner color and icon
        if warning == 'RED':
            banner_type = 'error'
            icon = '🔴'
            title = 'SKIP TODAY'
        elif warning == 'YELLOW':
            banner_type = 'warning'
            icon = '🟡'
            title = 'CAUTION'
        else:
            banner_type = 'success'
            icon = '🟢'
            title = 'FAVORABLE'
        
        return {
            'banner_type': banner_type,
            'icon': icon,
            'title': title,
            'confidence': assessment['confidence'],
            'skip_today': assessment['skip_today'],
            'honest_assessment': assessment['honest_assessment'],
            'position_sizing': assessment['position_sizing'],
            'strategy_focus': assessment['strategy_focus'],
            'next_check': assessment['next_check'],
            'reasons': assessment['reasons']
        }


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Market Day Advisor\n")
    
    advisor = MarketDayAdvisor()
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Good Day (Bull)',
            'context': {'vix': 13.5, 'spy_return_1d': 0.012, 'regime': 'bull', 'trend': 'uptrend'}
        },
        {
            'name': 'Caution Day',
            'context': {'vix': 17.0, 'spy_return_1d': -0.005, 'regime': 'caution', 'trend': 'sideways'}
        },
        {
            'name': 'Skip Day (High VIX)',
            'context': {'vix': 28.0, 'spy_return_1d': -0.025, 'regime': 'fear', 'trend': 'downtrend'}
        },
        {
            'name': 'Crisis Day',
            'context': {'vix': 35.0, 'spy_return_1d': -0.04, 'regime': 'crisis', 'trend': 'downtrend'}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*70}")
        print(f"📊 Scenario: {scenario['name']}")
        result = advisor.analyze_trading_conditions(scenario['context'])
        print(advisor.format_for_display(result))
