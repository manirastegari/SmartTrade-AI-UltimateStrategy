#!/usr/bin/env python3
"""
Premium Ultimate Strategy Analyzer
Simplified, focused approach using 15 quality metrics instead of 200+ indicators

Uses 4 investment perspectives applied to quality scores:
1. Institutional Consensus (stability + quality)
2. Hedge Fund Alpha (momentum + growth)
3. Quant Value Hunter (value + fundamentals)
4. Risk-Managed Core (safety + risk metrics)

Designed for 614 premium institutional-grade stocks
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time
from typing import List, Dict, Optional
import streamlit as st
from collections import defaultdict
from premium_stock_analyzer import PremiumStockAnalyzer


class FixedUltimateStrategyAnalyzer:
    """
    Premium Ultimate Strategy - Uses quality scores instead of technical noise
    Analyzes stocks through 4 investment perspectives for consensus picks
    """
    
    def __init__(self, analyzer):
        """
        Initialize with the main AdvancedTradingAnalyzer instance OR AdvancedDataFetcher
        
        Args:
            analyzer: AdvancedTradingAnalyzer instance OR AdvancedDataFetcher instance
        """
        # Support both direct data fetcher and full analyzer
        if hasattr(analyzer, 'data_fetcher'):
            # Full analyzer passed
            self.analyzer = analyzer
            self.premium_analyzer = PremiumStockAnalyzer(data_fetcher=analyzer.data_fetcher)
        else:
            # Direct data fetcher passed - create wrapper
            self.analyzer = type('obj', (object,), {'data_fetcher': analyzer})()
            self.premium_analyzer = PremiumStockAnalyzer(data_fetcher=analyzer)
        
        self.base_results = {}  # Store quality analysis
        self.strategy_results = {}
        self.consensus_recommendations = []
        
        # Guardrails DISABLED - Premium universe pre-screened
        self.guard_enabled = False
        
        # Symbol hygiene
        self._symbol_denylist = self._load_symbol_denylist()
        self._denylist_excluded = []
        
        print("✅ Premium Ultimate Strategy initialized")
        print("   Using 15 quality metrics instead of 200+ indicators")
    
    def run_ultimate_strategy(self, progress_callback=None, *, auto_export: bool = True):
        """
        Run Premium Ultimate Strategy
        
        1. Analyze all stocks with 15 quality metrics
        2. Apply 4 investment perspectives
        3. Find consensus (2/4, 3/4, 4/4 agreement)
        4. Optional AI review and market analysis
        
        Returns:
            dict: Consensus recommendations with quality breakdowns
        """
        from datetime import datetime
        self.analysis_start_time = datetime.now()
        
        if progress_callback:
            progress_callback("Starting Premium Ultimate Strategy...", 0)
        
        # STEP 1: Get universe
        if progress_callback:
            progress_callback("Loading premium stock universe...", 5)
        
        full_universe = self.analyzer._get_expanded_stock_universe()
        full_universe, self._denylist_excluded = self._apply_symbol_denylist(full_universe)
        
        total_stocks = len(full_universe)
        if progress_callback:
            progress_callback(f"Loaded {total_stocks} premium stocks", 8)
        
        print(f"\n{'='*80}")
        print(f"🎯 PREMIUM ULTIMATE STRATEGY")
        print(f"   Universe: {total_stocks} institutional-grade stocks")
        print(f"   Method: 15 quality metrics (not 200+ indicators)")
        print(f"   Perspectives: 4 investment styles for consensus")
        print(f"{'='*80}\n")
        
        # STEP 2: Analyze market conditions
        if progress_callback:
            progress_callback("Analyzing market conditions...", 10)
        
        market_analysis = self._analyze_market_conditions()
        
        # STEP 3: Run quality analysis on all stocks
        if progress_callback:
            progress_callback(f"Running quality analysis on {total_stocks} stocks...", 15)
        
        self.base_results = self._run_quality_analysis(
            full_universe, progress_callback
        )
        
        if not self.base_results:
            print("❌ No quality results!")
            return self._empty_results()
        
        # STEP 4: Apply 4 investment perspectives
        if progress_callback:
            progress_callback("Applying 4 investment perspectives...", 70)
        
        print(f"\n{'='*80}")
        print("📊 Applying 4 Investment Perspectives to Quality Scores")
        print(f"{'='*80}")
        
        self.strategy_results = {
            'institutional': self._apply_institutional_perspective(self.base_results),
            'hedge_fund': self._apply_hedge_fund_perspective(self.base_results),
            'quant_value': self._apply_quant_value_perspective(self.base_results),
            'risk_managed': self._apply_risk_managed_perspective(self.base_results)
        }
        
        # STEP 5: Find consensus
        if progress_callback:
            progress_callback("Finding consensus recommendations...", 80)
        
        consensus_picks = self._find_consensus(self.strategy_results)
        
        # STEP 6: Apply regime filters (relaxed for premium stocks)
        if progress_callback:
            progress_callback("Applying market regime filters...", 85)
        
        consensus_picks, regime_removed = self._apply_regime_filters(
            consensus_picks, market_analysis
        )
        
        # STEP 7: Optional: Get AI review for top picks
        if progress_callback:
            progress_callback("Generating AI insights...", 90)
        
        ai_insights = self._get_ai_market_review(
            consensus_picks, market_analysis, self.base_results
        )
        
        # STEP 8: Prepare final results
        if progress_callback:
            progress_callback("Preparing final results...", 95)
        
        final_results = self._prepare_final_results(
            consensus_picks, market_analysis, ai_insights
        )
        
        # STEP 9: Auto-export if requested
        if auto_export and consensus_picks:
            try:
                from excel_export import export_analysis_to_excel
                self._export_results(consensus_picks, final_results)
            except Exception as e:
                print(f"⚠️ Excel export failed: {e}")
        
        if progress_callback:
            progress_callback("Analysis complete!", 100)
        
        return final_results
    
    def _run_quality_analysis(self, symbols: List[str], progress_callback=None) -> Dict:
        """
        Run quality analysis on all stocks using PremiumStockAnalyzer
        
        Returns dict: {symbol: quality_analysis_result}
        """
        results = {}
        total = len(symbols)
        
        print(f"\n📊 Analyzing {total} stocks with 15 quality metrics...")
        
        for idx, symbol in enumerate(symbols, 1):
            try:
                # Update progress
                if progress_callback and idx % 10 == 0:
                    pct = int(15 + (idx / total * 55))  # 15% to 70%
                    progress_callback(f"Analyzing {symbol} ({idx}/{total})...", pct)
                
                # Get comprehensive data from analyzer's data fetcher
                stock_data = self.analyzer.data_fetcher.get_comprehensive_stock_data(symbol)
                
                if not stock_data or 'hist' not in stock_data:
                    continue
                
                hist_data = stock_data.get('hist')
                info = stock_data.get('info', {})
                
                # Run quality analysis
                quality_result = self.premium_analyzer.analyze_stock(
                    symbol, hist_data=hist_data, info=info
                )
                
                if quality_result.get('success'):
                    results[symbol] = quality_result
                    
                    if idx % 50 == 0:
                        print(f"   ✅ Analyzed {idx}/{total} stocks")
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {symbol}: {e}")
                continue
        
        print(f"\n✅ Quality analysis complete: {len(results)}/{total} stocks successful")
        return results
    
    def _apply_institutional_perspective(self, quality_results: Dict) -> List[Dict]:
        """
        Institutional Consensus Perspective
        Focus: Stability + Quality + Low Risk
        
        Weight: Fundamentals 60%, Risk 30%, Momentum 10%
        """
        picks = []
        
        for symbol, result in quality_results.items():
            # Institutional scoring: prioritize quality and safety
            inst_score = (
                result['fundamentals']['score'] * 0.60 +
                result['risk']['score'] * 0.30 +
                result['momentum']['score'] * 0.10
            )
            
            # Institutional threshold: prefer quality
            if inst_score >= 65:
                picks.append({
                    'symbol': symbol,
                    'score': round(inst_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if inst_score >= 75 else 'WEAK BUY',
                    'perspective': 'Institutional',
                    'fundamentals_grade': result['fundamentals']['grade'],
                    'risk_level': result['risk']['risk_level'],
                    'current_price': result['current_price']
                })
        
        picks.sort(key=lambda x: x['score'], reverse=True)
        print(f"   Institutional Consensus: {len(picks)} picks (focus: stability + quality)")
        return picks
    
    def _apply_hedge_fund_perspective(self, quality_results: Dict) -> List[Dict]:
        """
        Hedge Fund Alpha Perspective
        Focus: Momentum + Growth + Performance
        
        Weight: Momentum 50%, Fundamentals 30%, Risk 20%
        """
        picks = []
        
        for symbol, result in quality_results.items():
            # Hedge fund scoring: prioritize momentum and growth
            hf_score = (
                result['momentum']['score'] * 0.50 +
                result['fundamentals']['score'] * 0.30 +
                result['risk']['score'] * 0.20
            )
            
            # Hedge fund threshold: prefer momentum
            if hf_score >= 60:
                picks.append({
                    'symbol': symbol,
                    'score': round(hf_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if hf_score >= 70 else 'WEAK BUY',
                    'perspective': 'Hedge Fund',
                    'momentum_grade': result['momentum']['grade'],
                    'trend': result['momentum'].get('price_trend', 'Unknown'),
                    'current_price': result['current_price']
                })
        
        picks.sort(key=lambda x: x['score'], reverse=True)
        print(f"   Hedge Fund Alpha: {len(picks)} picks (focus: momentum + growth)")
        return picks
    
    def _apply_quant_value_perspective(self, quality_results: Dict) -> List[Dict]:
        """
        Quant Value Hunter Perspective
        Focus: Value + Fundamentals + Quality
        
        Weight: Fundamentals 70%, Momentum 20%, Risk 10%
        """
        picks = []
        
        for symbol, result in quality_results.items():
            # Value scoring: prioritize fundamentals and valuation
            value_score = (
                result['fundamentals']['score'] * 0.70 +
                result['momentum']['score'] * 0.20 +
                result['risk']['score'] * 0.10
            )
            
            # Value threshold: prefer quality fundamentals
            if value_score >= 65:
                picks.append({
                    'symbol': symbol,
                    'score': round(value_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if value_score >= 75 else 'WEAK BUY',
                    'perspective': 'Quant Value',
                    'fundamentals_grade': result['fundamentals']['grade'],
                    'pe_ratio': result['fundamentals'].get('pe_ratio'),
                    'current_price': result['current_price']
                })
        
        picks.sort(key=lambda x: x['score'], reverse=True)
        print(f"   Quant Value Hunter: {len(picks)} picks (focus: value + fundamentals)")
        return picks
    
    def _apply_risk_managed_perspective(self, quality_results: Dict) -> List[Dict]:
        """
        Risk-Managed Core Perspective
        Focus: Safety + Low Risk + Defensive
        
        Weight: Risk 50%, Fundamentals 40%, Momentum 10%
        """
        picks = []
        
        for symbol, result in quality_results.items():
            # Risk-managed scoring: prioritize safety
            risk_score = (
                result['risk']['score'] * 0.50 +
                result['fundamentals']['score'] * 0.40 +
                result['momentum']['score'] * 0.10
            )
            
            # Risk-managed threshold: prefer safety
            if risk_score >= 70:  # Higher threshold for safety-first
                picks.append({
                    'symbol': symbol,
                    'score': round(risk_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if risk_score >= 80 else 'WEAK BUY',
                    'perspective': 'Risk-Managed',
                    'risk_level': result['risk']['risk_level'],
                    'beta': result['risk'].get('beta'),
                    'current_price': result['current_price']
                })
        
        picks.sort(key=lambda x: x['score'], reverse=True)
        print(f"   Risk-Managed Core: {len(picks)} picks (focus: safety + low risk)")
        return picks
    
    def _find_consensus(self, strategy_results: Dict) -> List[Dict]:
        """
        Find stocks where multiple strategies agree
        
        Returns consensus picks with agreement counts (2/4, 3/4, 4/4)
        """
        print(f"\n{'='*80}")
        print("🎯 Finding Consensus Picks (Multi-Strategy Agreement)")
        print(f"{'='*80}")
        
        # Collect all picks by symbol
        symbol_picks = defaultdict(list)
        
        for strategy_name, picks in strategy_results.items():
            for pick in picks:
                symbol_picks[pick['symbol']].append({
                    'strategy': strategy_name,
                    'score': pick['score'],
                    'perspective': pick['perspective']
                })
        
        # Build consensus list
        consensus = []
        for symbol, picks in symbol_picks.items():
            agreement_count = len(picks)
            
            if agreement_count >= 2:  # At least 2/4 strategies agree
                avg_score = np.mean([p['score'] for p in picks])
                strategies_agreeing = [p['perspective'] for p in picks]
                
                # Get base quality data
                quality_data = self.base_results.get(symbol, {})
                
                consensus.append({
                    'symbol': symbol,
                    'strategies_agreeing': agreement_count,
                    'agreeing_perspectives': strategies_agreeing,
                    'consensus_score': round(avg_score, 2),
                    'quality_score': quality_data.get('quality_score', 0),
                    'recommendation': self._consensus_recommendation(agreement_count, avg_score),
                    'confidence': self._consensus_confidence(agreement_count, avg_score),
                    'fundamentals': quality_data.get('fundamentals', {}),
                    'momentum': quality_data.get('momentum', {}),
                    'risk': quality_data.get('risk', {}),
                    'sentiment': quality_data.get('sentiment', {}),
                    'current_price': quality_data.get('current_price', 0),
                    'tier': f"{agreement_count}/4"
                })
        
        # Sort by agreement count, then score
        consensus.sort(key=lambda x: (x['strategies_agreeing'], x['consensus_score']), reverse=True)
        
        # Print summary
        tier_counts = {4: 0, 3: 0, 2: 0}
        for pick in consensus:
            tier_counts[pick['strategies_agreeing']] = tier_counts.get(pick['strategies_agreeing'], 0) + 1
        
        print(f"\n📊 Consensus Summary:")
        print(f"   4/4 Agreement (STRONG BUY): {tier_counts[4]} stocks")
        print(f"   3/4 Agreement (BUY): {tier_counts[3]} stocks")
        print(f"   2/4 Agreement (WEAK BUY): {tier_counts[2]} stocks")
        print(f"   Total Consensus: {len(consensus)} stocks")
        
        return consensus
    
    def _consensus_recommendation(self, agreement: int, avg_score: float) -> str:
        """Determine recommendation based on agreement and score"""
        if agreement == 4:
            return 'STRONG BUY'
        elif agreement == 3:
            return 'BUY' if avg_score >= 75 else 'WEAK BUY'
        elif agreement == 2:
            return 'WEAK BUY' if avg_score >= 70 else 'HOLD'
        else:
            return 'HOLD'
    
    def _consensus_confidence(self, agreement: int, avg_score: float) -> float:
        """Calculate confidence based on agreement and score"""
        base_conf = {4: 0.95, 3: 0.85, 2: 0.75}.get(agreement, 0.60)
        
        # Adjust for score quality
        if avg_score >= 80:
            return min(0.98, base_conf + 0.05)
        elif avg_score < 65:
            return max(0.60, base_conf - 0.10)
        else:
            return base_conf
    
    def _apply_regime_filters(self, consensus_list: List[Dict], market_ctx: Dict) -> tuple:
        """
        Apply RELAXED regime filters for premium universe
        Only activates in 'caution' market regime
        
        Relaxed thresholds:
        - ≥2/4 agreement (vs 3/4 before)
        - Momentum ≥50 (vs 65 before)
        - Volatility ≤75 (vs 65 before)
        - No risk exclusion (premium stocks can handle risk)
        """
        try:
            import os
            regime = str((market_ctx or {}).get('regime') or '').lower()
            
            # Check for manual disable
            if os.environ.get('SMARTTRADE_DISABLE_REGIME_FILTER', '').lower() in ('1', 'true', 'yes'):
                return list(consensus_list or []), []
            
            # Only activate in caution regime
            if regime != 'caution':
                return list(consensus_list or []), []
            
            print(f"\n⚠️ CAUTION REGIME: Applying relaxed filters")
            
        except Exception:
            return list(consensus_list or []), []
        
        kept = []
        removed = []
        
        for stock in (consensus_list or []):
            symbol = stock.get('symbol')
            momentum = stock.get('momentum', {})
            agreement = stock.get('strategies_agreeing', 0)
            
            mom_score = momentum.get('score', 0)
            vol_score = 100 - stock.get('risk', {}).get('score', 50)  # Higher risk score = lower volatility
            
            reasons = []
            
            # Relaxed filters
            if agreement < 2:
                reasons.append('Caution: require ≥2/4 agreement')
            if mom_score < 50:
                reasons.append(f'Caution: momentum {mom_score:.0f} < 50')
            if vol_score > 75:
                reasons.append(f'Caution: volatility {vol_score:.0f} > 75')
            
            if reasons:
                removed.append({'symbol': symbol, 'reasons': ', '.join(reasons)})
            else:
                kept.append(stock)
        
        if removed:
            print(f"   Filtered {len(removed)} stocks in caution mode")
        
        return kept, removed
    
    def _get_ai_market_review(self, consensus_picks: List[Dict], 
                              market_ctx: Dict, quality_results: Dict) -> Dict:
        """
        Get AI review of top consensus picks and market conditions
        
        Focused prompts using quality scores (not 200+ indicators)
        """
        try:
            # Check if XAI is configured
            import os
            xai_key = os.environ.get('XAI_API_KEY') or os.environ.get('GROK_API_KEY')
            
            if not xai_key or not consensus_picks:
                return {'available': False}
            
            # Get top picks by tier
            tier_4_picks = [p for p in consensus_picks if p['strategies_agreeing'] == 4][:5]
            tier_3_picks = [p for p in consensus_picks if p['strategies_agreeing'] == 3][:5]
            
            if not tier_4_picks and not tier_3_picks:
                return {'available': False}
            
            # Build focused prompt with quality metrics
            prompt = self._build_ai_prompt(tier_4_picks, tier_3_picks, market_ctx)
            
            # Get AI analysis
            ai_response = self._call_grok_api(prompt, xai_key)
            
            return {
                'available': True,
                'market_overview': ai_response.get('market_overview', ''),
                'top_picks_analysis': ai_response.get('top_picks', ''),
                'risk_assessment': ai_response.get('risk_assessment', ''),
                'entry_timing': ai_response.get('entry_timing', '')
            }
            
        except Exception as e:
            print(f"⚠️ AI review unavailable: {e}")
            return {'available': False}
    
    def _build_ai_prompt(self, tier_4: List, tier_3: List, market: Dict) -> str:
        """Build focused AI prompt with quality metrics"""
        
        prompt = f"""Analyze these premium quality stock recommendations from a 4-strategy consensus system.

**Market Context:**
- Regime: {market.get('regime', 'Unknown')}
- VIX: {market.get('vix', 'N/A')}
- Trend: {market.get('trend', 'Unknown')}

**Top Consensus Picks (4/4 Agreement - HIGHEST CONVICTION):**
"""
        
        for pick in tier_4:
            symbol = pick['symbol']
            fund = pick.get('fundamentals', {})
            mom = pick.get('momentum', {})
            risk = pick.get('risk', {})
            
            prompt += f"""
{symbol}: Quality Score {pick['quality_score']}/100
- Fundamentals: {fund.get('grade', 'N/A')} (P/E: {fund.get('pe_ratio', 'N/A')}, Revenue Growth: {fund.get('revenue_growth', 'N/A')}%, Margin: {fund.get('profit_margin', 'N/A')}%)
- Momentum: {mom.get('grade', 'N/A')} (Trend: {mom.get('price_trend', 'N/A')}, RSI: {mom.get('rsi', 'N/A')})
- Risk: {risk.get('grade', 'N/A')} ({risk.get('risk_level', 'N/A')} - Beta: {risk.get('beta', 'N/A')})
- Price: ${pick.get('current_price', 0):.2f}
"""
        
        if tier_3:
            prompt += "\n**Strong Picks (3/4 Agreement):**\n"
            for pick in tier_3[:3]:
                prompt += f"- {pick['symbol']}: Quality {pick['quality_score']}/100, Score {pick['consensus_score']}/100\n"
        
        prompt += """
**Provide concise analysis:**
1. Market Overview (2-3 sentences): Current market conditions and timing
2. Top Pick Analysis (3-4 sentences): Best opportunities from 4/4 consensus, key strengths
3. Risk Assessment (2 sentences): Main risks to watch
4. Entry Timing (1-2 sentences): Best approach for entering positions now

Keep response focused and actionable for conservative investors.
"""
        
        return prompt
    
    def _call_grok_api(self, prompt: str, api_key: str) -> Dict:
        """Call Grok API for analysis"""
        try:
            import requests
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'grok-beta',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 800,
                    'temperature': 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # Parse response sections
                return self._parse_ai_response(content)
            else:
                print(f"⚠️ Grok API error: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"⚠️ Grok API call failed: {e}")
            return {}
    
    def _parse_ai_response(self, content: str) -> Dict:
        """Parse AI response into sections"""
        sections = {
            'market_overview': '',
            'top_picks': '',
            'risk_assessment': '',
            'entry_timing': ''
        }
        
        # Simple parsing (AI usually structures well)
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            lower = line.lower()
            if 'market overview' in lower:
                current_section = 'market_overview'
            elif 'top pick' in lower or 'best opportunit' in lower:
                current_section = 'top_picks'
            elif 'risk' in lower:
                current_section = 'risk_assessment'
            elif 'entry timing' in lower or 'timing' in lower:
                current_section = 'entry_timing'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def _prepare_final_results(self, consensus: List, market: Dict, ai: Dict) -> Dict:
        """Prepare final results structure"""
        
        # Count tiers
        tier_counts = {4: 0, 3: 0, 2: 0}
        for pick in consensus:
            tier_counts[pick['strategies_agreeing']] = tier_counts.get(pick['strategies_agreeing'], 0) + 1
        
        return {
            'consensus_recommendations': consensus,
            'market_analysis': market,
            'ai_insights': ai,
            'total_stocks_analyzed': len(self.base_results),
            'stocks_4_of_4': tier_counts[4],
            'stocks_3_of_4': tier_counts[3],
            'stocks_2_of_4': tier_counts[2],
            'analysis_type': 'PREMIUM_QUALITY_CONSENSUS',
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'denylist_excluded': len(self._denylist_excluded),
            'metrics_used': '15 quality metrics (not 200+ indicators)'
        }
    
    def _export_results(self, consensus: List, results: Dict):
        """Export results to Excel"""
        try:
            from excel_export import export_analysis_to_excel
            
            # Convert consensus to export format
            export_data = []
            for pick in consensus:
                export_data.append({
                    'symbol': pick['symbol'],
                    'recommendation': pick['recommendation'],
                    'overall_score': pick['consensus_score'],
                    'strategies_agreeing': f"{pick['strategies_agreeing']}/4",
                    'quality_score': pick['quality_score'],
                    'current_price': pick['current_price'],
                    'fundamentals': pick.get('fundamentals', {}),
                    'momentum': pick.get('momentum', {}),
                    'risk': pick.get('risk', {}),
                    'tier': pick['tier']
                })
            
            filename, msg = export_analysis_to_excel(
                export_data,
                analysis_params='Premium Ultimate Strategy - 4-Perspective Consensus'
            )
            
            if filename:
                print(f"\n📊 Results exported to: {filename}")
            
        except Exception as e:
            print(f"⚠️ Export failed: {e}")
    
    # Helper methods
    def _analyze_market_conditions(self) -> Dict:
        """Analyze market conditions"""
        ctx = {'status': 'NEUTRAL', 'vix': 15.0, 'trend': 'SIDEWAYS', 'regime': 'normal'}
        
        try:
            from market_context_signals import get_market_context_signals
            signals = get_market_context_signals()
            if isinstance(signals, dict):
                ctx.update(signals)
        except:
            pass
        
        return ctx
    
    def _load_symbol_denylist(self) -> set:
        """Load symbol denylist"""
        try:
            import os
            deny = set()
            
            # From env var
            env_val = os.environ.get('SMARTTRADE_DENYLIST', '')
            if env_val:
                deny.update(s.strip().upper() for s in env_val.split(',') if s.strip())
            
            # From file
            if os.path.exists('symbol_denylist.txt'):
                with open('symbol_denylist.txt', 'r') as f:
                    for line in f:
                        line = line.strip().upper()
                        if line and not line.startswith('#'):
                            deny.add(line)
            
            return deny
        except:
            return set()
    
    def _apply_symbol_denylist(self, universe: List[str]) -> tuple:
        """Apply denylist to universe"""
        if not self._symbol_denylist:
            return universe, []
        
        excluded = [s for s in universe if s.upper() in self._symbol_denylist]
        filtered = [s for s in universe if s.upper() not in self._symbol_denylist]
        
        if excluded:
            print(f"🚫 Excluded {len(excluded)} symbols from denylist")
        
        return filtered, excluded
    
    def _empty_results(self) -> Dict:
        """Return empty results"""
        return {
            'consensus_recommendations': [],
            'market_analysis': {},
            'ai_insights': {'available': False},
            'total_stocks_analyzed': 0,
            'stocks_4_of_4': 0,
            'stocks_3_of_4': 0,
            'stocks_2_of_4': 0,
            'analysis_type': 'PREMIUM_QUALITY_CONSENSUS',
            'error': 'No results generated'
        }
    
    def display_ultimate_strategy_results(self, results: Dict):
        """
        Display Premium Ultimate Strategy results in Streamlit UI
        
        Shows:
        - Market analysis summary
        - Consensus recommendations by tier (4/4, 3/4, 2/4)
        - Quality breakdowns
        - AI insights (if available)
        """
        
        if not results or not results.get('consensus_recommendations'):
            st.error("❌ No consensus recommendations found!")
            return
        
        consensus = results['consensus_recommendations']
        market = results.get('market_analysis', {})
        ai_insights = results.get('ai_insights', {})
        
        # Header
        st.markdown("---")
        st.markdown("## 🎯 Premium Ultimate Strategy Results")
        st.markdown(f"**Analysis Type**: {results.get('metrics_used', '15 Quality Metrics')}")
        st.markdown(f"**Analysis Date**: {results.get('analysis_date', 'N/A')}")
        
        # Market Overview
        st.markdown("### 📊 Market Context")
        col1, col2, col3 = st.columns(3)
        with col1:
            regime = market.get('regime', 'Unknown').upper()
            regime_color = '🟢' if regime == 'NORMAL' else '🟡' if regime == 'CAUTION' else '🔴'
            st.metric("Market Regime", f"{regime_color} {regime}")
        with col2:
            vix = market.get('vix', 'N/A')
            st.metric("VIX", vix)
        with col3:
            trend = market.get('trend', 'Unknown')
            st.metric("Market Trend", trend)
        
        # Consensus Summary
        st.markdown("### 🏆 Consensus Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Analyzed", results.get('total_stocks_analyzed', 0))
        with col2:
            count_4 = results.get('stocks_4_of_4', 0)
            st.metric("4/4 Agreement", count_4, help="STRONG BUY - All perspectives agree")
        with col3:
            count_3 = results.get('stocks_3_of_4', 0)
            st.metric("3/4 Agreement", count_3, help="BUY - Strong majority")
        with col4:
            count_2 = results.get('stocks_2_of_4', 0)
            st.metric("2/4 Agreement", count_2, help="WEAK BUY - Split decision")
        
        # AI Insights (if available)
        if ai_insights.get('available'):
            st.markdown("### 🤖 AI Market Analysis")
            
            if ai_insights.get('market_overview'):
                st.markdown("**Market Overview:**")
                st.info(ai_insights['market_overview'])
            
            if ai_insights.get('top_picks_analysis'):
                st.markdown("**Top Picks Analysis:**")
                st.success(ai_insights['top_picks_analysis'])
            
            if ai_insights.get('risk_assessment'):
                st.markdown("**Risk Assessment:**")
                st.warning(ai_insights['risk_assessment'])
            
            if ai_insights.get('entry_timing'):
                st.markdown("**Entry Timing:**")
                st.info(ai_insights['entry_timing'])
        
        # 4/4 Agreement (STRONG BUY)
        tier_4 = [p for p in consensus if p['strategies_agreeing'] == 4]
        if tier_4:
            st.markdown("### 🌟 4/4 Agreement - STRONG BUY (Highest Conviction)")
            st.markdown(f"*All 4 investment perspectives agree on these {len(tier_4)} stocks*")
            
            for pick in tier_4[:10]:  # Show top 10
                with st.expander(f"**{pick['symbol']}** - Quality Score: {pick['quality_score']}/100 | ${pick.get('current_price', 0):.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Quality Breakdown:**")
                        fund = pick.get('fundamentals', {})
                        mom = pick.get('momentum', {})
                        st.markdown(f"- Fundamentals: **{fund.get('grade', 'N/A')}** ({fund.get('score', 0):.0f}/100)")
                        st.markdown(f"- Momentum: **{mom.get('grade', 'N/A')}** ({mom.get('score', 0):.0f}/100)")
                        risk = pick.get('risk', {})
                        st.markdown(f"- Risk: **{risk.get('grade', 'N/A')}** ({risk.get('score', 0):.0f}/100)")
                        sent = pick.get('sentiment', {})
                        st.markdown(f"- Sentiment: **{sent.get('grade', 'N/A')}** ({sent.get('score', 0):.0f}/100)")
                    
                    with col2:
                        st.markdown("**Consensus Details:**")
                        st.markdown(f"- Recommendation: **{pick['recommendation']}**")
                        st.markdown(f"- Confidence: **{pick['confidence']*100:.0f}%**")
                        st.markdown(f"- Consensus Score: **{pick['consensus_score']}/100**")
                        st.markdown(f"- Perspectives: {', '.join(pick.get('agreeing_perspectives', []))}")
        
        # 3/4 Agreement (BUY)
        tier_3 = [p for p in consensus if p['strategies_agreeing'] == 3]
        if tier_3:
            st.markdown("### ⭐ 3/4 Agreement - BUY (Strong Majority)")
            st.markdown(f"*3 out of 4 perspectives agree on these {len(tier_3)} stocks*")
            
            # Show condensed table
            table_data = []
            for pick in tier_3[:15]:  # Top 15
                table_data.append({
                    'Symbol': pick['symbol'],
                    'Quality': f"{pick['quality_score']}/100",
                    'Recommendation': pick['recommendation'],
                    'Consensus': f"{pick['consensus_score']}/100",
                    'Price': f"${pick.get('current_price', 0):.2f}",
                    'Fund': pick.get('fundamentals', {}).get('grade', 'N/A'),
                    'Mom': pick.get('momentum', {}).get('grade', 'N/A'),
                    'Risk': pick.get('risk', {}).get('grade', 'N/A')
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
        
        # 2/4 Agreement (WEAK BUY)
        tier_2 = [p for p in consensus if p['strategies_agreeing'] == 2]
        if tier_2:
            with st.expander(f"⚡ 2/4 Agreement - WEAK BUY ({len(tier_2)} stocks)"):
                table_data = []
                for pick in tier_2[:20]:  # Top 20
                    table_data.append({
                        'Symbol': pick['symbol'],
                        'Quality': f"{pick['quality_score']}/100",
                        'Recommendation': pick['recommendation'],
                        'Perspectives': ', '.join(pick.get('agreeing_perspectives', [])[:2])
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True)
        
        # Download button for full results
        st.markdown("---")
        st.markdown("### 📥 Export Options")
        st.info("Results have been automatically exported to Excel. Check your project directory for the file.")


if __name__ == "__main__":
    print("Premium Ultimate Strategy Analyzer")
    print("Uses 15 quality metrics instead of 200+ indicators")
    print("Requires AdvancedTradingAnalyzer instance to run")
