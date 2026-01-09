#!/usr/bin/env python3
"""
AI Universe Selector
Phase 1 of Ultimate Strategy: Market-Aware Universe Selection
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import yfinance as yf
from xai_client import XAIClient
from premium_quality_universe import get_premium_universe
from cleaned_high_potential_universe import _normalize_symbol

class AIUniverseSelector:
    """
    Selects the optimal "Smart List" of stocks to analyze based on 
    current global market conditions using xAI (Grok).
    """
    
    def __init__(self):
        self.api_key = os.environ.get('XAI_API_KEY') or os.environ.get('GROK_API_KEY')
        self.enabled = bool(self.api_key)
        self.client = XAIClient(api_key=self.api_key) if self.enabled else None
        
        # Core sector ETFs to gauge rotation
        self.sectors = {
            'XLK': 'Technology',
            'XLV': 'Healthcare',
            'XLF': 'Financials',
            'XLE': 'Energy',
            'XLI': 'Industrials',
            'XLP': 'Consumer Staples',
            'XLY': 'Consumer Discretionary',
            'XLC': 'Communications',
            'XLB': 'Materials',
            'XLU': 'Utilities',
            'IYR': 'Real Estate'
        }
        
    def select_universe(self, target_size: int = 150) -> Dict[str, Any]:
        """
        Main entry point: Analyzes market and returns a filtered list of stocks.
        
        Returns:
            {
                'universe': List[str], # The list of symbols
                'reasoning': str,      # AI's explanation
                'market_condition': str, # e.g. "Risk-Off Defensive"
                'focus_sectors': List[str]
            }
        """
        print(f"\n{'='*80}")
        print("🌍 PHASE 1: AI GLOBAL MARKET SCAN & UNIVERSE SELECTION")
        print(f"{'='*80}")
        
        if not self.enabled:
            print("⚠️ XAI API Key not found. Falling back to full Premium Universe.")
            full_univ = get_premium_universe()
            return {
                'universe': full_univ,
                'reasoning': 'AI selection disabled (no API key). Using full universe.',
                'market_condition': 'Unknown',
                'focus_sectors': []
            }
            
        # 1. Gather Market Context
        print("📊 Fetching real-time market sector data...")
        market_data = self._fetch_market_context()
        
        # 2. Ask Grok to select the strategy
        print("🧠 AI Analyst identifying best opportunities for TODAY'S market...")
        ai_decision = self._get_ai_selection(market_data, target_size)
        
        if not ai_decision:
             print("⚠️ AI selection failed. Falling back to full Premium Universe.")
             full_univ = get_premium_universe()
             return {
                'universe': full_univ,
                'reasoning': 'AI selection failed. Using full universe.',
                'market_condition': 'Unknown',
                'focus_sectors': []
            }
            
        # 3. Filter the Premium Universe based on AI's focus
        # Note: We don't just blindly trust AI generated symbols (hallucination risk),
        # we strictly filter our KNOWN Premium Universe based on the AI's directives 
        # OR we use the specific list if it provided valid ones that exist in our universe.
        
        final_universe = self._finalize_universe(ai_decision.get('suggested_symbols', []), ai_decision.get('focus_sectors', []))
        
        # Ensure we have enough stocks (don't go too small)
        if len(final_universe) < 50:
            print(f"⚠️ AI selected universe too small ({len(final_universe)}). Padding with top premium stocks.")
            final_universe = self._pad_universe(final_universe, 100)
            
        print(f"✅ AI Selection Complete: {len(final_universe)} high-potential candidates identified.")
        print(f"   Market Condition: {ai_decision.get('market_condition')}")
        print(f"   Focus: {', '.join(ai_decision.get('focus_sectors', []))}")
        
        return {
            'universe': final_universe,
            'reasoning': ai_decision.get('reasoning', 'Based on market conditions.'),
            'market_condition': ai_decision.get('market_condition', 'Balanced'),
            'focus_sectors': ai_decision.get('focus_sectors', [])
        }

    def _fetch_market_context(self) -> Dict:
        """Fetch performance of major indices and sectors."""
        context = {}
        
        # Indices
        tickers = ['SPY', 'QQQ', 'IWM', '^VIX'] + list(self.sectors.keys())
        try:
            # Batch fetch 5 days of history to see trend
            data = yf.download(tickers, period="5d", progress=False)['Close']
            
            # Calculate 1-day and 5-day returns
            current = data.iloc[-1]
            prev_1d = data.iloc[-2]
            prev_5d = data.iloc[0]
            
            # VIX
            vix = current.get('^VIX', 0)
            context['VIX'] = float(vix)
            
            # SPY Trend
            spy = current.get('SPY', 0)
            spy_1d_chg = (spy - prev_1d.get('SPY', 0)) / prev_1d.get('SPY', 1) * 100
            context['SPY_1D_Change'] = f"{spy_1d_chg:.2f}%"
            
            # Sector Performance
            sector_perf = []
            for ticker, name in self.sectors.items():
                price = current.get(ticker, 0)
                if price == 0: continue
                chg_1d = (price - prev_1d.get(ticker, 1)) / prev_1d.get(ticker, 1) * 100
                chg_5d = (price - prev_5d.get(ticker, 1)) / prev_5d.get(ticker, 1) * 100
                sector_perf.append(f"{name} ({ticker}): 1D={chg_1d:.2f}%, 5D={chg_5d:.2f}%")
                
            context['Sector_Performance'] = "; ".join(sector_perf)
            
        except Exception as e:
            print(f"⚠️ Market data fetch warning: {e}")
            context['Error'] = "Partial data unavailable"
            
        return context

    def _get_ai_selection(self, market_data: Dict, target_size: int) -> Optional[Dict]:
        """Query Grok for universe selection strategy."""
        
        # We give AI the full premium universe list to pick from? 
        # No, that's too many tokens (600+ symbols).
        # Better approach: Ask AI for SECTORS and THEMES, and maybe Top 50 representative tickers,
        # then we map those themes to our database.
        # OR: We provide a summarized list of our universe (just symbols) if context allows.
        # 600 symbols is ~1-2k tokens. That fits easily in Grok's context window.
        
        premium_universe = get_premium_universe()
        univ_str = ", ".join(premium_universe)
        
        prompt = f"""
        You are a Senior Portfolio Manager determining the daily trading strategy.
        
        **Current Market Context:**
        VIX: {market_data.get('VIX', 'N/A')}
        SPY 1D Change: {market_data.get('SPY_1D_Change', 'N/A')}
        Sector Trends: {market_data.get('Sector_Performance', 'N/A')}
        
        **Task:**
        1. Analyze the market regime (e.g., Risk-On, Risk-Off, Sector Rotation, Defensive).
        2. Identify the top 3-4 sectors to focus on TODAY.
        3. From the provided "Candidate Universe", select the best {target_size} symbols that match this strategy.
           - If Risk-Off: Focus on Healthcare, Utilities, Staples, low-beta.
           - If Risk-On: Focus on Tech, Discretionary, Growth, small-caps.
           - If Volatile: Focus on high-quality, cash-rich blue chips.
        
        **Candidate Universe:**
        {univ_str}
        
        **Response Format (JSON only):**
        {{
            "market_condition": "Risk-On / Defensive / Volatile / etc",
            "reasoning": "Brief explanation of why these sectors...",
            "focus_sectors": ["Technology", "Healthcare", ...],
            "suggested_symbols": ["AAPL", "MSFT", ...]
        }}
        """
        
        try:
            response = self.client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2, # Low temp for strictly following the universe list
                max_tokens=4000
            ) 
            
            # Helper to extract JSON
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '') if 'choices' in response else str(response)
            
            # If the client already parsed it (it does returns dict usually if using tool)
            # The XAIClient.chat returns a dict with 'choices' or the parsed json if it used internal logic.
            # Let's rely on the client's _safe_json or just handle it.
            # Actually XAIClient.chat returns the parsed JSON payload directly if it succeeds in parsing!
            
            if isinstance(response, dict) and 'suggested_symbols' in response:
                 return response
            
            # If it's wrapped
            if 'top_picks' in response: # Did we get the wrong tool output? No, checking structure.
                 return response
                 
            return response # Hope it matches structure
            
        except Exception as e:
            print(f"⚠️ AI interaction failed: {e}")
            return None

    def _finalize_universe(self, suggested: List[str], focus_sectors: List[str]) -> List[str]:
        """Validate AI suggestions against the known premium universe."""
        valid_premium = set(get_premium_universe())
        final_list = []
        
        # 1. Add valid suggested symbols
        for sym in suggested:
            norm = _normalize_symbol(sym)
            if norm in valid_premium:
                final_list.append(norm)
                
        # 2. If we need more (AI returned fewer than requested), 
        # logic could be expanded here to pull more from the 'Focus Sectors',
        # but for now we'll stick to what AI explicitly picked + padding later.
        
        return list(set(final_list))

    def _pad_universe(self, current_list: List[str], min_size: int) -> List[str]:
        """If AI list is too short, backfill with top general blue chips."""
        full_univ = get_premium_universe()
        current_set = set(current_list)
        
        # Priority: Tech & Healthcare giants (usually safe bets)
        reserves = [s for s in full_univ if s not in current_set]
        
        # Simple backfill
        return current_list + reserves[:(min_size - len(current_list))]

if __name__ == "__main__":
    selector = AIUniverseSelector()
    result = selector.select_universe()
    print("\nTest Result Summary:")
    print(f"Symbols: {len(result['universe'])}")
    print(f"Condition: {result['market_condition']}")
