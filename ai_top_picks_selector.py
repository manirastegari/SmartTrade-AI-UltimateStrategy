#!/usr/bin/env python3
"""
AI Top Picks Selector
Combines ALL analytical layers to select best trading opportunities:
- Layer 1: Quality Metrics (fundamentals, momentum, risk, sentiment)
- Layer 2: Multi-Strategy Consensus (4 perspectives)
- Layer 3: ML Predictions (30-feature model)
- Layer 4: AI Validation (news, sentiment, hidden risks)

Provides BRIEF, ACTIONABLE recommendations
"""

import os
import json
import re
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime


class AITopPicksSelector:
    """
    AI-powered top picks selection using complete Ultimate Strategy intelligence
    Brief, instructive, actionable recommendations
    """
    
    def __init__(self):
        self.api_key = os.environ.get('XAI_API_KEY') or os.environ.get('GROK_API_KEY')
        self.enabled = bool(self.api_key)
    
    def select_top_picks(
        self, 
        consensus_picks: List[Dict],
        market_context: Dict,
        max_picks: int = 10
    ) -> Dict:
        """
        Analyze ALL consensus picks and select THE BEST using complete intelligence
        
        Returns BRIEF, ACTIONABLE recommendations:
        {
            'ai_top_picks': [
                {
                    'symbol': 'AAPL',
                    'rank': 1,
                    'ai_score': 95,  # Combined intelligence score
                    'why_selected': 'Brief 1-sentence reason',
                    'action': 'BUY' | 'STRONG BUY' | 'HOLD',
                    'position_size': 'Large' | 'Medium' | 'Small',
                    'entry_timing': 'Immediate' | 'Wait for dip' | 'Scale in'
                },
                ...
            ],
            'brief_summary': '2-3 sentence market overview',
            'key_insight': '1 sentence most important insight',
            'total_analyzed': int,
            'total_recommended': int
        }
        """
        if not self.enabled or not consensus_picks:
            return self._default_selection(consensus_picks, max_picks)
        
        try:
            from xai_client import XAIClient
            
            client = XAIClient(api_key=self.api_key)
            
            # Prepare concise data for AI analysis
            picks_summary = self._prepare_picks_summary(consensus_picks[:30])  # Top 30 to analyze
            
            prompt = f"""You are an expert stock picker analyzing {len(picks_summary)} stocks using complete intelligence:
- Quality metrics (fundamentals, momentum, risk, sentiment)
- Multi-strategy consensus (4 investment perspectives)
- ML predictions (30-feature model)
- Real-time validation (news, sentiment, hidden risks)

**Market Context:**
VIX: {market_context.get('vix', 'N/A')} | Regime: {market_context.get('regime', 'Unknown')} | Trend: {market_context.get('trend', 'Unknown')}

**Stocks to Analyze:**
{picks_summary}

**Your Task:**
Select the TOP {max_picks} BEST trading opportunities RIGHT NOW.

**Requirements:**
1. Be BRIEF and ACTIONABLE (no long explanations)
2. Consider ALL data layers (quality, consensus, ML, validation)
3. Rank by overall opportunity (not just one metric)
4. Provide clear entry timing and position sizing
5. One-sentence reason for each pick

**Output Format (JSON):**
{{
    "top_picks": [
        {{
            "symbol": "AAPL",
            "rank": 1,
            "ai_score": 95,
            "why_selected": "Strong fundamentals + ML confirms + positive news momentum",
            "action": "STRONG BUY",
            "position_size": "Large",
            "entry_timing": "Immediate"
        }},
        ...
    ],
    "brief_summary": "Market conditions favorable. Focus on tech leaders with ML confirmation.",
    "key_insight": "Quality + ML alignment = highest conviction trades"
}}

IMPORTANT: Keep it BRIEF. One sentence per pick. Clear actions."""

            response = client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Balanced - not too creative
                max_tokens=2000
            )

            parsed = self._normalize_top_pick_response(response)
            if not parsed:
                print("⚠️ Could not parse AI response, using default selection")
                return self._default_selection(consensus_picks, max_picks)

            top_picks_raw = parsed.get('top_picks') or parsed.get('ai_top_picks') or []

            return {
                'ai_top_picks': top_picks_raw[:max_picks],
                'brief_summary': parsed.get('brief_summary', ''),
                'key_insight': parsed.get('key_insight', ''),
                'total_analyzed': len(consensus_picks),
                'total_recommended': min(max_picks, len(top_picks_raw))
            }
                
        except Exception as e:
            print(f"⚠️ AI top picks selection failed: {e}")
            return self._default_selection(consensus_picks, max_picks)

    def _normalize_top_pick_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """Normalize XAIClient response into expected dict format."""
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

        if not any(key in payload for key in ('top_picks', 'ai_top_picks')):
            return None

        return payload

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Best-effort extraction of JSON object from a text response."""
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
    
    def _prepare_picks_summary(self, picks: List[Dict]) -> str:
        """Prepare concise summary of picks for AI analysis"""
        summary_lines = []
        
        for pick in picks:
            # Extract key data
            symbol = pick.get('symbol', 'N/A')
            quality = pick.get('quality_score', 0)
            consensus = pick.get('consensus_score', 0)
            agreement = pick.get('strategies_agreeing', 0)
            ml_prob = pick.get('ml_probability', 0)
            ml_return = pick.get('ml_expected_return', 0)
            ultimate = pick.get('ultimate_score', 0)
            ai_val = pick.get('ai_validation', 'N/A')
            ai_risk = pick.get('ai_risk_level', 'N/A')
            ai_profit = pick.get('ai_profit_potential', 'N/A')
            sentiment = pick.get('ai_news_sentiment', 'N/A')
            
            # Concise one-line summary
            line = (
                f"{symbol}: Quality={quality:.0f} | Consensus={consensus:.0f} | "
                f"Agreement={agreement}/4 | ML={ml_prob*100:.0f}% (+{ml_return:.1f}%) | "
                f"Ultimate={ultimate:.0f} | AI={ai_val}/{ai_risk}/{ai_profit} | News={sentiment}"
            )
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
    
    def _default_selection(self, consensus_picks: List[Dict], max_picks: int) -> Dict:
        """
        Fallback selection when AI unavailable
        Uses Ultimate Score + validation to rank
        """
        if not consensus_picks:
            return {
                'ai_top_picks': [],
                'brief_summary': 'No consensus picks available for selection.',
                'key_insight': 'Increase stock universe or relax filters.',
                'total_analyzed': 0,
                'total_recommended': 0
            }
        
        # Determine global trading mode if passed through market_context on picks
        # (FixedUltimateStrategyAnalyzer will attach this later when needed)
        global_mode = None
        if consensus_picks and isinstance(consensus_picks[0], dict):
            global_mode = consensus_picks[0].get('global_trading_mode') or None

        # Score each pick using all available data
        scored_picks = []
        
        for pick in consensus_picks:
            # Base score from Ultimate Score (combines quality + consensus + ML)
            ultimate_score = pick.get('ultimate_score', 0)
            
            # Bonus for AI confirmation
            ai_val = pick.get('ai_validation', '')
            ai_bonus = 0
            if ai_val == 'CONFIRMED':
                ai_bonus = 10
            elif ai_val == 'REJECTED':
                ai_bonus = -20
            
            # Bonus for 4/4 agreement
            agreement_bonus = (pick.get('strategies_agreeing', 0) - 2) * 5
            
            # Penalty for high AI risk
            risk_penalty = 0
            ai_risk = pick.get('ai_risk_level', '')
            if ai_risk == 'HIGH':
                risk_penalty = -10
            elif ai_risk == 'LOW':
                risk_penalty = 5
            
            # Base AI score
            ai_score = ultimate_score + ai_bonus + agreement_bonus + risk_penalty

            # Regime-aware adjustment from entry_score if available
            entry_score = pick.get('entry_score')
            if entry_score is not None:
                # Blend ultimate_score-based ai_score with entry_score (both 0-100)
                ai_score = 0.5 * ai_score + 0.5 * float(entry_score)

            # Global trading mode adjustments
            mode = global_mode or 'NORMAL'
            if mode == 'DEFENSIVE':
                ai_score -= 10
            elif mode == 'NO_NEW_TRADES':
                ai_score -= 30
            elif mode == 'AGGRESSIVE':
                ai_score += 5
            ai_score = max(0, min(100, ai_score))  # Clamp 0-100
            
            # Determine action and base position size from regime-aware score
            if ai_score >= 85 and pick.get('strategies_agreeing', 0) >= 3:
                action = 'STRONG BUY'
                position_size = 'Large'
            elif ai_score >= 75:
                action = 'BUY'
                position_size = 'Medium'
            else:
                action = 'HOLD'
                position_size = 'Small'

            # In NO_NEW_TRADES mode, force no new entries
            today_status = 'OK_TO_ENTER'
            if mode == 'NO_NEW_TRADES':
                action = 'HOLD'
                position_size = 'Small'
                today_status = 'NO_NEW_POSITION'
            elif mode == 'DEFENSIVE':
                # Defensive: Only allow entries for top-tier, high score names
                if ai_score < 90 or pick.get('strategies_agreeing', 0) < 3:
                    action = 'HOLD'
                    position_size = 'Small'
                    today_status = 'ONLY_SCALE_IN'
            
            # Entry timing based on ML and regime
            ml_prob = pick.get('ml_probability', 0)
            if ml_prob and ml_prob > 0.7:
                entry_timing = 'Immediate' if mode in ('NORMAL', 'AGGRESSIVE') else 'Scale in'
            elif ml_prob and ml_prob > 0.6:
                entry_timing = 'Scale in' if mode != 'NO_NEW_TRADES' else 'Wait for confirmation'
            else:
                entry_timing = 'Wait for confirmation'
            
            # Why selected (brief)
            reasons = []
            if pick.get('strategies_agreeing', 0) == 4:
                reasons.append('4/4 consensus')
            if pick.get('quality_score', 0) >= 85:
                reasons.append('top quality')
            if ai_val == 'CONFIRMED':
                reasons.append('AI confirmed')
            if ml_prob and ml_prob > 0.7:
                reasons.append('ML confirms')
            
            why_selected = ' + '.join(reasons) if reasons else 'Strong metrics'
            
            scored_picks.append({
                'symbol': pick.get('symbol', 'N/A'),
                'rank': 0,  # Will assign after sorting
                'ai_score': round(ai_score, 1),
                'why_selected': why_selected,
                'action': action,
                'position_size': position_size,
                'entry_timing': entry_timing,
                'today_status': today_status,
                'ultimate_score': ultimate_score,
                'quality_score': pick.get('quality_score', 0),
                'agreement': pick.get('strategies_agreeing', 0)
            })
        
        # Sort by AI score
        scored_picks.sort(key=lambda x: x['ai_score'], reverse=True)
        
        # Assign ranks
        for i, pick in enumerate(scored_picks[:max_picks], 1):
            pick['rank'] = i
        
        # Generate brief summary
        top_picks = scored_picks[:max_picks]
        strong_buys = sum(1 for p in top_picks if p['action'] == 'STRONG BUY')
        avg_score = sum(p['ai_score'] for p in top_picks) / len(top_picks) if top_picks else 0
        
        brief_summary = (
            f"Selected {len(top_picks)} top opportunities from {len(consensus_picks)} candidates. "
            f"{strong_buys} STRONG BUY rated. Average AI score: {avg_score:.0f}/100."
        )
        
        key_insight = "Focus on 4/4 consensus picks with AI confirmation for highest confidence."
        
        return {
            'ai_top_picks': top_picks,
            'brief_summary': brief_summary,
            'key_insight': key_insight,
            'total_analyzed': len(consensus_picks),
            'total_recommended': len(top_picks)
        }


def format_ai_picks_display(ai_picks_result: Dict) -> str:
    """Format AI top picks for console/interface display - BRIEF format"""
    
    lines = []
    lines.append("\n" + "="*80)
    lines.append("🎯 AI TOP PICKS - ULTIMATE STRATEGY RECOMMENDATION")
    lines.append("="*80)
    
    # Summary
    lines.append(f"\n📊 {ai_picks_result.get('brief_summary', 'No summary available')}")
    lines.append(f"💡 KEY INSIGHT: {ai_picks_result.get('key_insight', 'N/A')}")
    
    # Top picks table
    lines.append(f"\n🏆 TOP {len(ai_picks_result.get('ai_top_picks', []))} PICKS:")
    lines.append("-" * 80)
    
    for pick in ai_picks_result.get('ai_top_picks', []):
        rank = pick.get('rank', 0)
        symbol = pick.get('symbol', 'N/A')
        ai_score = pick.get('ai_score', 0)
        action = pick.get('action', 'HOLD')
        position = pick.get('position_size', 'Small')
        timing = pick.get('entry_timing', 'Wait')
        why = pick.get('why_selected', 'N/A')
        
        # Action emoji
        action_emoji = '🚀' if action == 'STRONG BUY' else '✅' if action == 'BUY' else '⚠️'
        
        lines.append(
            f"{rank}. {action_emoji} {symbol:6} | AI Score: {ai_score:5.1f} | {action:12} | "
            f"{position:7} position | {timing:20}"
        )
        lines.append(f"   Why: {why}")
    
    lines.append("="*80)
    lines.append(f"📈 Analyzed: {ai_picks_result.get('total_analyzed', 0)} | "
                 f"Recommended: {ai_picks_result.get('total_recommended', 0)}")
    lines.append("="*80 + "\n")
    
    return "\n".join(lines)
