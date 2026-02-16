
#!/usr/bin/env python3
"""
AI Top Picks Selector (Enhanced with Chain-of-Thought)
Combines ALL analytical layers using "Debate-Style" reasoning:
- Layer 1: Quality Metrics (fundamentals, momentum, risk, sentiment)
- Layer 2: Multi-Strategy Consensus (4 perspectives)
- Layer 3: ML Predictions (30-feature model)
- Layer 4: AI Validation (news, macro fit)
- Layer 5: Chain-of-Thought Reasoning (Deep Logic)
"""

import os
import json
import re
import logging
from typing import Dict, List, Any, Optional

class AITopPicksSelector:
    """
    AI-powered top picks selection using Chain-of-Thought reasoning.
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
        Analyze ALL consensus picks and select THE BEST using Debate/CoT reasoning.
        """
        if not self.enabled or not consensus_picks:
            return self._default_selection(consensus_picks, max_picks)
        
        try:
            from xai_client import XAIClient
            client = XAIClient(api_key=self.api_key)
            
            # Prepare concise data for AI analysis
            # We select top 40 candidates to give AI good variety to filter down
            candidates = consensus_picks[:40]
            picks_summary = self._prepare_picks_summary(candidates)
            
            # Chain-of-Thought Prompt
            prompt = f"""You are a Senior Portfolio Manager conducting a final investment committee review.

**Objective:**
Select the TOP {max_picks} highest-conviction trading opportunities from the candidate list below.
Use "Chain of Thought" reasoning: Debate the pros/cons of each candidate against the current Macro Regime.

**Current Macro Context:**
- Regime: {market_context.get('regime', 'Unknown')}
- VIX: {market_context.get('vix', 'N/A')} (Risk Level)
- Macro Score: {market_context.get('macro_score', 'N/A')}/100
- 10Y Bond Yield: {market_context.get('yield_10y', 'N/A')}
- Dollar Index: {market_context.get('dollar_index', 'N/A')}
- Market Trend: {market_context.get('trend', 'Unknown')}

**Candidate Stocks (Pre-screened by Quant Models):**
{picks_summary}

**Instructions:**
1. **Analyze Regime Fit**: Which *types* of stocks prosper in this specific macro environment? (e.g. if Yields UP -> Avoid Debt/Growth, Favor Cash/Value).
2. **Debate Candidates**: For the best candidates, debate their strengths (Consensus/ML) vs weaknesses (Risk/Macro Fit).
3. **Select Winners**: Choose the top {max_picks} that have the best *Risk-Adjusted* potential.

**Output Format (Strict JSON):**
{{
    "reasoning_trace": "Your step-by-step logic. e.g. 'Given rising yields, I am rejecting high-PE growth names... AAPL is retained due to cash pile...'",
    "top_picks": [
        {{
            "symbol": "AAPL",
            "rank": 1,
            "ai_score": 96,
            "confidence": 92,
            "macro_fit": "High",
            "why_selected": "Strong fundamentals + ML confirms. Cash pile offsets yield risk.",
            "action": "STRONG BUY",
            "position_size": "Large",
            "entry_timing": "Immediate"
        }}
    ],
    "brief_summary": "2-3 sentences summarizing the strategy for today.",
    "key_insight": "The 'Alpha' insight (e.g. 'Market is ignoring X...')"
}}

IMPORTANT RULES:
- "ai_score" must be an integer 0-100 representing your conviction.
- "confidence" must be an integer 0-100 representing overall confidence of this pick.
- "macro_fit" must be exactly one of: "High", "Neutral", "Low".
- You MUST return valid JSON only, no extra text.
"""

            response = client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,  # Slightly higher for reasoning capability
                max_tokens=2500
            )

            parsed = self._normalize_top_pick_response(response)
            if not parsed:
                print("⚠️ Could not parse AI response, using fallback.")
                return self._default_selection(consensus_picks, max_picks)

            top_picks_raw = parsed.get('top_picks') or parsed.get('ai_top_picks') or []
            
            # Inject reasoning trace if available
            reasoning_trace = parsed.get('reasoning_trace', 'No trace provided.')

            # CRITICAL FIX: Backfill current_price, confidence, quality_score from consensus data
            # The AI prompt does NOT have access to prices — only quant scores.
            consensus_lookup = {p.get('symbol'): p for p in consensus_picks}
            for ai_pick in top_picks_raw:
                sym = ai_pick.get('symbol')
                match = consensus_lookup.get(sym, {})
                # Backfill price and quality data AI cannot know
                if not ai_pick.get('current_price'):
                    ai_pick['current_price'] = match.get('current_price', 0)
                if not ai_pick.get('quality_score'):
                    ai_pick['quality_score'] = match.get('quality_score', 0)
                # Ensure confidence is int 0-100 (AI may return it, or we use consensus)
                raw_conf = ai_pick.get('confidence')
                if raw_conf is not None:
                    ai_pick['confidence'] = int(float(raw_conf)) if float(raw_conf) <= 100 else int(float(raw_conf))
                else:
                    # Derive from consensus confidence (0-1 scale → 0-100)
                    ai_pick['confidence'] = int(match.get('confidence', 0) * 100)
                # Ensure ai_score is numeric
                raw_score = ai_pick.get('ai_score', 0)
                try:
                    ai_pick['ai_score'] = float(raw_score)
                except (ValueError, TypeError):
                    ai_pick['ai_score'] = 0.0
                # Backfill buy_zone / take_profit from consensus trade levels
                if not ai_pick.get('buy_zone') and match.get('buy_zone'):
                    ai_pick['buy_zone'] = match['buy_zone']
                if not ai_pick.get('take_profit') and match.get('take_profit'):
                    ai_pick['take_profit'] = match['take_profit']

            return {
                'ai_top_picks': top_picks_raw[:max_picks],
                'brief_summary': parsed.get('brief_summary', ''),
                'key_insight': parsed.get('key_insight', ''),
                'reasoning_trace': reasoning_trace,
                'total_analyzed': len(candidates),
                'total_recommended': min(max_picks, len(top_picks_raw))
            }
                
        except Exception as e:
            print(f"⚠️ AI top picks selection failed: {e}")
            import traceback
            traceback.print_exc()
            return self._default_selection(consensus_picks, max_picks)

    def _normalize_top_pick_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """Normalize XAIClient response into expected dict format."""
        payload: Optional[Dict[str, Any]] = None

        if isinstance(response, dict):
            # If the response is already a dict, check if it has the keys or 'message'
            if 'choices' in response: # OpenAI format wrapper
                 try:
                     content = response['choices'][0]['message']['content']
                     return self._extract_json_from_text(content)
                 except:
                     pass
            payload = dict(response)
        elif isinstance(response, str):
            payload = self._extract_json_from_text(response)

        if payload is None:
            # Check validation of XAI client internal structure
            if isinstance(response, dict) and 'top_picks' in response:
                return response
            return None

        # Clean/Validate
        if not any(key in payload for key in ('top_picks', 'ai_top_picks')):
            # Sometimes AI puts top_picks inside a 'result' or 'output' key
            for k in ['result', 'output', 'selection']:
                if isinstance(payload.get(k), dict) and 'top_picks' in payload[k]:
                    return payload[k]
            return None

        return payload

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        if not isinstance(text, str): return None
        candidate = text.strip()
        
        # Try finding the largest {...} block
        # Because we asked for strict JSON, but sometimes they add markdown ```json ... ```
        json_pattern = re.compile(r'\{.*\}', re.DOTALL)
        match = json_pattern.search(candidate)
        if match:
            candidate = match.group()
        
        try:
            return json.loads(candidate)
        except Exception:
            # Simple repair: sometimes trailing commas cause issues
            try:
                # Basic cleanup
                candidate = re.sub(r',\s*\}', '}', candidate)
                candidate = re.sub(r',\s*\]', ']', candidate)
                return json.loads(candidate)
            except:
                return None
    
    def _prepare_picks_summary(self, picks: List[Dict]) -> str:
        """Prepare concise summary of picks for AI analysis"""
        summary_lines = []
        
        for pick in picks:
            symbol = pick.get('symbol', 'N/A')
            quality = pick.get('quality_score', 0)
            agreement = pick.get('strategies_agreeing', 0)
            ml_prob = pick.get('ml_probability', 0)
            ultimate = pick.get('ultimate_score', 0)
            ai_val = pick.get('ai_validation', 'N/A')
            
            line = (
                f"- {symbol}: UltScore={ultimate:.0f} | Quality={quality:.0f} | "
                f"Consensus={agreement}/5 | ML_Prob={ml_prob*100:.0f}% | "
                f"Validation={ai_val}"
            )
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
    
    def _default_selection(self, consensus_picks: List[Dict], max_picks: int) -> Dict:
        """Fallback logic if AI fails."""
        # Simple sorting by Ultimate Score (which already includes quality/consensus/ML)
        sorted_picks = sorted(
            consensus_picks, 
            key=lambda x: float(x.get('ultimate_score', 0) or 0), 
            reverse=True
        )
        
        top_picks = []
        for i, pick in enumerate(sorted_picks[:max_picks], 1):
            top_picks.append({
                'symbol': pick.get('symbol'),
                'rank': i,
                'ai_score': pick.get('ultimate_score', 0),
                'macro_fit': 'Neutral (Fallback)',
                'why_selected': 'High quantitative score (AI unavailable)',
                'action': 'BUY',
                'position_size': 'Medium',
                'entry_timing': 'Scale in',
                # CRITICAL FIX: Pass accurate price data for Excel
                'current_price': pick.get('current_price', 0),
                'buy_zone': pick.get('buy_zone') or f"${pick.get('current_price', 0):.2f} - ${pick.get('current_price', 0)*1.02:.2f}",
                'take_profit': pick.get('take_profit') or f"${pick.get('current_price', 0)*1.15:.2f} (+15%)",
                'confidence': int(pick.get('confidence', 0)*100),
                'quality_score': pick.get('quality_score', 0)
            })
            
        return {
            'ai_top_picks': top_picks,
            'brief_summary': 'AI unavailable. Selections based on quantitative Ultimate Score.',
            'key_insight': 'Ensure XAI API Key is valid for advanced reasoning.',
            'reasoning_trace': 'Fallback mode active.',
            'total_analyzed': len(consensus_picks),
            'total_recommended': len(top_picks)
        }

def format_ai_picks_display(ai_picks_result: Dict) -> str:
    """Format AI top picks for console/interface display."""
    lines = []
    lines.append("\n" + "="*80)
    lines.append("🎯 AI TOP PICKS - CHAIN-OF-THOUGHT REASONING")
    lines.append("="*80)
    
    lines.append(f"\n🧠 LOGIC TRACE: {ai_picks_result.get('reasoning_trace', 'N/A')[:300]}...") # Truncate for display
    lines.append(f"📊 SUMMARY: {ai_picks_result.get('brief_summary', 'N/A')}")
    lines.append(f"💡 INSIGHT: {ai_picks_result.get('key_insight', 'N/A')}")
    
    lines.append(f"\n🏆 TOP {len(ai_picks_result.get('ai_top_picks', []))} PICKS:")
    lines.append("-" * 80)
    
    for pick in ai_picks_result.get('ai_top_picks', []):
        rank = pick.get('rank', 0)
        symbol = pick.get('symbol', 'N/A')
        ai_score = pick.get('ai_score', 0)
        macro = pick.get('macro_fit', 'N/A')
        action = pick.get('action', 'HOLD')
        why = pick.get('why_selected', 'N/A')
        
        action_emoji = '🚀' if action == 'STRONG BUY' else '✅' if action == 'BUY' else '⚠️'
        
        lines.append(
            f"{rank}. {action_emoji} {symbol:6} | Score: {ai_score:5.1f} | MacroFit: {macro:10} | {action}"
        )
        lines.append(f"   Why: {why}")

    lines.append("="*80 + "\n")
    return "\n".join(lines)
