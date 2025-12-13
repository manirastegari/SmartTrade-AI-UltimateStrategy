#!/usr/bin/env python3
"""
Enhanced AI Stock Catalyst & News Analyzer
Deep analysis for each stock: news, catalysts, risks, opportunities
Focuses on TOP TIER picks for maximum accuracy
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class AIStockCatalystAnalyzer:
    """
    Deep AI analysis for individual stocks
    Searches for: news, catalysts, risks, opportunities, earnings, sentiment
    """
    
    def __init__(self):
        self.api_key = os.environ.get('XAI_API_KEY') or os.environ.get('GROK_API_KEY')
        self.enabled = bool(self.api_key)
    
    def analyze_stock_catalysts(self, stock: Dict, market_context: Dict) -> Dict:
        """
        Deep dive analysis for ONE stock
        Searches for all catalysts, news, risks, opportunities
        
        Args:
            stock: Stock data with symbol, quality_score, consensus_score, etc.
            market_context: Market conditions
        
        Returns:
            {
                'symbol': str,
                'catalyst_score': 0-100,  # Overall catalyst strength
                'recent_news': [
                    {
                        'headline': str,
                        'impact': 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE',
                        'importance': 'HIGH' | 'MEDIUM' | 'LOW'
                    }
                ],
                'growth_catalysts': [str],  # Specific growth drivers
                'risks': [str],  # Specific risks
                'earnings_outlook': 'BEAT' | 'MEET' | 'MISS' | 'UNKNOWN',
                'sentiment_summary': str,  # Brief sentiment overview
                'ai_recommendation': 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL',
                'confidence': 0-100,
                'brief_catalyst_summary': str  # 1-2 sentences for UI
            }
        """
        if not self.enabled:
            return self._default_catalyst_analysis(stock)
        
        try:
            from xai_client import XAIClient
            
            client = XAIClient(api_key=self.api_key)
            
            symbol = stock.get('symbol', 'N/A')
            quality = stock.get('quality_score', 0)
            consensus = stock.get('consensus_score', 0)
            ml_prob = stock.get('ml_probability', 0)
            sector = stock.get('sector', 'Unknown')
            
            prompt = f"""You are an expert stock analyst. You do NOT have guaranteed access to real-time news. Analyze {symbol} in detail.

**Stock Overview:**
- Symbol: {symbol}
- Sector: {sector}
- Quality Score: {quality}/100
- Consensus Score: {consensus}/100
- ML Probability: {ml_prob*100:.0f}%

**Market Context:**
- VIX: {market_context.get('vix', 'N/A')}
- Regime: {market_context.get('regime', 'Unknown')}
- Date: {datetime.now().strftime('%Y-%m-%d')}

**Deep Analysis Required:**

1. **Recent News & Events** (only if you are confident):
   - Earnings reports (beat/meet/miss?)
   - Product launches or announcements
   - Management changes
   - Analyst upgrades/downgrades
   - Regulatory news
   - M&A activity

2. **Growth Catalysts** (what will drive stock UP):
   - New products or services
   - Market expansion opportunities
   - Technology advantages
   - Partnership announcements
   - Industry tailwinds
   - Margin expansion potential

3. **Risks** (what could hurt the stock):
   - Competition threats
   - Regulatory risks
   - Supply chain issues
   - Earnings headwinds
   - Valuation concerns
   - Industry challenges

4. **Earnings Outlook**:
   - Next earnings date approaching?
   - Expected to beat/meet/miss estimates?
   - Guidance trends

5. **Sentiment Analysis**:
   - Social media sentiment (X/Twitter, Reddit)
   - Analyst sentiment
   - Retail vs institutional sentiment
   - Recent price action sentiment

**Output Format (JSON):**
{{
    "catalyst_score": 85,
    "recent_news": [
        {{"headline": "Q3 earnings beat by 15%", "impact": "POSITIVE", "importance": "HIGH"}},
        {{"headline": "New AI chip announced", "impact": "POSITIVE", "importance": "MEDIUM"}}
    ],
    "growth_catalysts": [
        "AI chip demand accelerating",
        "Cloud revenue up 40% YoY",
        "Expanding into new markets"
    ],
    "risks": [
        "High valuation at 30x P/E",
        "Competition from AMD intensifying"
    ],
    "earnings_outlook": "BEAT",
    "sentiment_summary": "Strong bullish sentiment on social media, analysts upgrading targets",
    "ai_recommendation": "STRONG BUY",
    "confidence": 90,
    "brief_catalyst_summary": "Strong earnings beat + AI chip momentum + expanding margins"
}}

IMPORTANT: 
- Do NOT fabricate dates, numbers, headlines, or events.
- If you are not confident, set fields to UNKNOWN / NEUTRAL and provide generic risk factors.
- Focus on ACTIONABLE catalysts
- Keep it BRIEF and FACTUAL
"""

            # Use XAIClient's chat() method directly
            response = client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Low for factual accuracy
                max_tokens=1500   # Detailed analysis
            )

            parsed = self._normalize_catalyst_response(response)
            if not parsed:
                print(f"⚠️ Could not parse AI catalyst analysis for {symbol}")
                return self._default_catalyst_analysis(stock)

            parsed.setdefault('symbol', symbol)
            return parsed
                
        except Exception as e:
            print(f"⚠️ AI catalyst analysis failed for {symbol}: {e}")
            return self._default_catalyst_analysis(stock)
    
    def batch_analyze_catalysts(self, stocks: List[Dict], market_context: Dict, max_stocks: int = 10) -> List[Dict]:
        """
        Analyze catalysts for multiple stocks (focus on top tier)
        
        Args:
            stocks: List of stock dicts
            market_context: Market conditions
            max_stocks: Maximum stocks to analyze (default 10 for API efficiency)
        
        Returns:
            List of catalyst analysis results
        """
        if not stocks:
            return []
        
        results = []
        
        # Prioritize top stocks (highest agreement, highest quality)
        sorted_stocks = sorted(
            stocks,
            key=lambda x: (
                x.get('strategies_agreeing', 0),
                x.get('quality_score', 0),
                x.get('ultimate_score', 0)
            ),
            reverse=True
        )
        
        top_stocks = sorted_stocks[:max_stocks]
        
        print(f"\n🔍 Analyzing catalysts for TOP {len(top_stocks)} stocks...")
        print("   (Prioritized by: Agreement > Quality > Ultimate Score)")

        order_map = {stock.get('symbol'): idx for idx, stock in enumerate(top_stocks)}
        ordered_results: List[Optional[Dict]] = [None] * len(top_stocks)

        max_workers = max(1, min(4, len(top_stocks)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self.analyze_stock_catalysts, stock, market_context): stock
                for stock in top_stocks
            }

            for future in as_completed(future_map):
                stock = future_map[future]
                symbol = stock.get('symbol', 'N/A')
                idx = order_map.get(symbol, 0)
                try:
                    data = future.result()
                except Exception as e:
                    print(f"   ⚠️ {symbol}: Catalyst analysis failed ({e})")
                    data = self._default_catalyst_analysis(stock)
                ordered_results[idx] = data
                print(f"   ✓ {symbol}: Catalyst Score {data.get('catalyst_score', 0)}/100")

        results = [r for r in ordered_results if r]
        print(f"✅ Catalyst analysis complete for {len(results)} stocks\n")
        
        return results

    def _normalize_catalyst_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """Normalize raw xAI response into expected catalyst payload."""
        payload: Optional[Dict[str, Any]] = None

        if isinstance(response, dict):
            payload = dict(response)
        elif isinstance(response, str):
            payload = self._extract_json_from_text(response)

        if payload is None and isinstance(response, dict):
            raw = response.get('raw')
            if isinstance(raw, str):
                payload = self._extract_json_from_text(raw)

        if payload is None:
            return None

        payload.pop('model_used', None)
        payload.pop('raw', None)

        # Ensure we have at least core catalyst keys
        if 'catalyst_score' not in payload and 'growth_catalysts' not in payload:
            return None

        return payload

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        if not isinstance(text, str):
            return None

        candidate = text.strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

        match = re.search(r'\{[\s\S]*\}', candidate)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return None
        return None
    
    def _default_catalyst_analysis(self, stock: Dict) -> Dict:
        """Fallback when AI unavailable"""
        return {
            'symbol': stock.get('symbol', 'N/A'),
            'catalyst_score': 50,
            'recent_news': [],
            'growth_catalysts': ['Quality metrics indicate strong fundamentals'],
            'risks': ['AI catalyst analysis unavailable - consider manual research'],
            'earnings_outlook': 'UNKNOWN',
            'sentiment_summary': 'AI analysis unavailable',
            'ai_recommendation': 'HOLD',
            'confidence': 50,
            'brief_catalyst_summary': 'AI catalyst analysis unavailable - based on quant metrics only'
        }


def format_catalyst_display(catalyst_results: List[Dict]) -> str:
    """Format catalyst analysis for console display - BRIEF but informative"""
    
    lines = []
    lines.append("\n" + "="*80)
    lines.append("🔍 AI CATALYST & NEWS ANALYSIS")
    lines.append("="*80)
    
    for result in catalyst_results:
        symbol = result.get('symbol', 'N/A')
        catalyst_score = result.get('catalyst_score', 0)
        recommendation = result.get('ai_recommendation', 'HOLD')
        confidence = result.get('confidence', 0)
        summary = result.get('brief_catalyst_summary', 'N/A')
        
        # Recommendation emoji
        rec_emoji = '🚀' if recommendation == 'STRONG BUY' else '✅' if recommendation == 'BUY' else '⚠️'
        
        lines.append(f"\n{rec_emoji} {symbol} | Catalyst Score: {catalyst_score}/100 | {recommendation} ({confidence}%)")
        lines.append(f"   {summary}")
        
        # Growth catalysts (top 3)
        catalysts = result.get('growth_catalysts', [])
        if catalysts:
            lines.append("   Catalysts:")
            for cat in catalysts[:3]:
                lines.append(f"     • {cat}")
        
        # Risks (top 2)
        risks = result.get('risks', [])
        if risks:
            lines.append("   Risks:")
            for risk in risks[:2]:
                lines.append(f"     ⚠️ {risk}")
        
        # Recent news (top 2)
        news = result.get('recent_news', [])
        if news:
            lines.append("   Recent News:")
            for item in news[:2]:
                impact_emoji = '📈' if item['impact'] == 'POSITIVE' else '📉' if item['impact'] == 'NEGATIVE' else '➡️'
                lines.append(f"     {impact_emoji} {item['headline']}")
    
    lines.append("\n" + "="*80 + "\n")
    
    return "\n".join(lines)


def enhance_picks_with_catalysts(picks: List[Dict], catalyst_results: List[Dict]) -> List[Dict]:
    """
    Merge catalyst data into picks for complete intelligence
    
    Args:
        picks: Original consensus picks
        catalyst_results: Catalyst analysis results
    
    Returns:
        Enhanced picks with catalyst data
    """
    # Create lookup dict
    catalyst_by_symbol = {r['symbol']: r for r in catalyst_results}
    
    # Enhance picks
    enhanced = []
    for pick in picks:
        enhanced_pick = dict(pick)
        
        symbol = pick.get('symbol')
        if symbol in catalyst_by_symbol:
            catalyst = catalyst_by_symbol[symbol]
            
            # Add catalyst fields
            enhanced_pick['catalyst_score'] = catalyst.get('catalyst_score', 0)
            enhanced_pick['growth_catalysts'] = catalyst.get('growth_catalysts', [])
            enhanced_pick['catalyst_risks'] = catalyst.get('risks', [])
            enhanced_pick['recent_news'] = catalyst.get('recent_news', [])
            enhanced_pick['earnings_outlook'] = catalyst.get('earnings_outlook', 'UNKNOWN')
            enhanced_pick['sentiment_summary'] = catalyst.get('sentiment_summary', '')
            enhanced_pick['catalyst_summary'] = catalyst.get('brief_catalyst_summary', '')
            
            # Boost AI score based on catalysts
            if 'ai_score' in enhanced_pick:
                catalyst_bonus = (catalyst.get('catalyst_score', 50) - 50) / 5  # -10 to +10
                enhanced_pick['ai_score'] = min(100, enhanced_pick['ai_score'] + catalyst_bonus)
        
        enhanced.append(enhanced_pick)
    
    return enhanced
