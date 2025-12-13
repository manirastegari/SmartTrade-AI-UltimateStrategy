#!/usr/bin/env python3
"""
Enhanced AI Market & Pick Validator
Uses Grok AI to:
1. Analyze if market conditions are favorable for trading
2. Validate quant picks using news, sentiment, X posts
3. Provide risk assessment and profit validation
"""

import os
from typing import Dict, List
from datetime import datetime

class AIMarketValidator:
    """
    AI-powered market condition and pick validation
    Uses Grok to analyze real-time data beyond quant metrics
    """
    
    def __init__(self):
        self.api_key = os.environ.get('XAI_API_KEY') or os.environ.get('GROK_API_KEY')
        self.enabled = bool(self.api_key)
    
    def analyze_market_tradability(self, market_context: Dict) -> Dict:
        """
        Ask Grok: Is now a good time to trade?
        
        Returns:
            {
                'trade_recommendation': 'FAVORABLE' | 'NEUTRAL' | 'CAUTION' | 'AVOID',
                'confidence': 0-100,
                'reasoning': str,
                'key_risks': [str],
                'opportunities': [str],
                'brief_summary': str  # For interface display
            }
        """
        if not self.enabled:
            return self._default_market_analysis()
        
        try:
            from xai_client import XAIClient
            
            client = XAIClient(api_key=self.api_key)
            
            prompt = f"""You are an expert market analyst. You do NOT have guaranteed access to real-time market data.

**Current Market Data:**
- VIX: {market_context.get('vix', 'N/A')}
- Regime: {market_context.get('regime', 'Unknown')}
- Trend: {market_context.get('trend', 'Unknown')}
- Date: {datetime.now().strftime('%Y-%m-%d')}

**Your Task:**
Analyze if NOW is a good time to trade stocks. Use ONLY:
1. The market context provided (VIX/regime/trend)
2. General market principles and risk management heuristics

Do NOT fabricate news, prices, events, or "current" facts. If you lack information, say so.

**Provide:**
1. Trade Recommendation: FAVORABLE, NEUTRAL, CAUTION, or AVOID
2. Confidence Level: 0-100
3. Brief Summary (1-2 sentences for user interface)
4. Detailed Reasoning (3-4 sentences)
5. Top 3 Key Risks to watch
6. Top 3 Opportunities if trading

Respond as JSON with keys: trade_recommendation, confidence, brief_summary, reasoning, key_risks (array), opportunities (array)
"""
            
            response = client.chat(
                messages=[
                    {"role": "system", "content": "You provide tradability assessments from provided context only. Do not invent facts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Low temperature for consistent analysis
                max_tokens=800
            )
            
            if isinstance(response, dict):
                response.pop("model_used", None)
                response.pop("raw", None)
                return response
            
            return self._default_market_analysis()
            
        except Exception as e:
            print(f"⚠️ AI market validation failed: {e}")
            return self._default_market_analysis()
    
    def validate_picks(self, picks: List[Dict], market_context: Dict) -> Dict:
        """
        Ask Grok: Are these quant picks valid? Low risk? High profit potential?
        
        Uses AI to analyze:
        - Recent news about each stock
        - Sentiment from X/Twitter
        - Hidden risks quant metrics miss
        - Profit potential validation
        
        Returns:
            {
                'overall_validation': 'STRONG' | 'MODERATE' | 'WEAK',
                'validated_picks': [
                    {
                        'symbol': str,
                        'ai_validation': 'CONFIRMED' | 'NEUTRAL' | 'REJECTED',
                        'risk_level': 'LOW' | 'MEDIUM' | 'HIGH',
                        'profit_potential': 'HIGH' | 'MEDIUM' | 'LOW',
                        'news_sentiment': 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE',
                        'hidden_risks': [str],
                        'ai_notes': str,
                        'brief_verdict': str  # For Excel display
                    }
                ],
                'summary': str
            }
        """
        if not self.enabled or not picks:
            return self._default_validation(picks)
        
        try:
            from xai_client import XAIClient
            
            client = XAIClient(api_key=self.api_key)
            
            # Build prompt with pick details
            picks_text = "\n".join([
                f"{i+1}. {p['symbol']}: Quality {p.get('quality_score', 0)}/100, "
                f"Consensus {p.get('consensus_score', 0)}/100, "
                f"ML Prob {p.get('ml_probability', 0)*100:.0f}%, "
                f"Sector: {p.get('sector', 'Unknown')}"
                for i, p in enumerate(picks[:10])  # Top 10 picks
            ])
            
            prompt = f"""You are an expert stock analyst. You do NOT have guaranteed access to real-time news or social media.

**Market Context:**
- VIX: {market_context.get('vix', 'N/A')}
- Regime: {market_context.get('regime', 'Unknown')}
- Date: {datetime.now().strftime('%Y-%m-%d')}

**Quant-Selected Stock Picks to Validate:**
{picks_text}

**Your Expert Validation Task:**
For EACH stock, use ONLY the provided quant context (scores/sector) and general risk heuristics.
Do NOT fabricate recent news, earnings, legal issues, upgrades/downgrades, or "current" events.
If insufficient information, mark fields as UNKNOWN/NEUTRAL.

**For EACH stock, provide:**
- AI Validation: CONFIRMED (good pick), NEUTRAL (ok), or REJECTED (avoid)
- Risk Level: LOW, MEDIUM, HIGH (beyond quant metrics)
- Profit Potential: HIGH (>20%), MEDIUM (10-20%), LOW (<10%)
- News Sentiment: POSITIVE, NEUTRAL, NEGATIVE
- Hidden Risks: List any non-obvious risks
- Brief Verdict: 1 sentence summary for user

**Also provide:**
- Overall Validation: STRONG, MODERATE, WEAK (for the entire list)
- Summary: 2-3 sentences on overall pick quality

Respond as JSON with structure:
{{
  "overall_validation": "STRONG|MODERATE|WEAK",
  "validated_picks": [
    {{"symbol": "XYZ", "ai_validation": "...", "risk_level": "...", "profit_potential": "...", 
      "news_sentiment": "...", "hidden_risks": [...], "brief_verdict": "..."}}
  ],
  "summary": "..."
}}
"""
            
            response = client.chat(
                messages=[
                    {"role": "system", "content": "Validate picks from provided quant context only. Do not invent facts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000  # Need more tokens for detailed validation
            )
            
            if isinstance(response, dict):
                response.pop("model_used", None)
                response.pop("raw", None)
                
                # Ensure we have validated_picks
                if 'validated_picks' not in response:
                    response['validated_picks'] = []
                
                return response
            
            return self._default_validation(picks)
            
        except Exception as e:
            print(f"⚠️ AI pick validation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._default_validation(picks)
    
    def _default_market_analysis(self) -> Dict:
        """Default response when AI unavailable"""
        return {
            'trade_recommendation': 'NEUTRAL',
            'confidence': 50,
            'brief_summary': 'AI market analysis unavailable - proceed with caution',
            'reasoning': 'Grok API not configured or unavailable',
            'key_risks': ['AI validation disabled', 'Limited market context'],
            'opportunities': ['Rely on quant metrics only']
        }
    
    def _default_validation(self, picks: List[Dict]) -> Dict:
        """Default response when AI unavailable"""
        return {
            'overall_validation': 'MODERATE',
            'validated_picks': [
                {
                    'symbol': p['symbol'],
                    'ai_validation': 'NEUTRAL',
                    'risk_level': 'MEDIUM',
                    'profit_potential': 'MEDIUM',
                    'news_sentiment': 'NEUTRAL',
                    'hidden_risks': ['AI validation unavailable'],
                    'ai_notes': 'Grok API not configured',
                    'brief_verdict': 'Quant metrics only - AI validation disabled'
                }
                for p in picks[:10]
            ],
            'summary': 'AI validation unavailable - picks based on quant metrics only'
        }
