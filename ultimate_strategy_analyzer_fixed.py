#!/usr/bin/env python3
"""
Premium Ultimate Strategy Analyzer
Simplified, focused approach using 15 quality metrics instead of 200+ indicators

Uses 5 investment perspectives applied to quality scores:
1. Institutional Consensus (stability + quality)
2. Hedge Fund Alpha (momentum + growth)
3. Quant Value Hunter (value + fundamentals)
4. Risk-Managed Core (safety + risk metrics)
5. Investment Bank (analyst + fundamentals)

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
from rate_limit_manager import rate_limit_manager
from macro_economic_analyzer import MacroEconomicAnalyzer

# ML Enhancement
try:
    from ml_meta_predictor import MLMetaPredictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML Meta-Predictor not available - running without ML enhancement")

# AI Universe Selector (NEW - Phase 1)
try:
    from ai_universe_selector import AIUniverseSelector
    AI_SELECTOR_AVAILABLE = True
except ImportError:
    AI_SELECTOR_AVAILABLE = False
    print("⚠️ AI Universe Selector not available - running with full fixed universe")

# AI Market & Pick Validator (NEW)
try:
    from ai_market_validator import AIMarketValidator
    AI_VALIDATOR_AVAILABLE = True
except ImportError:
    AI_VALIDATOR_AVAILABLE = False
    print("⚠️ AI Market Validator not available - running without AI validation")

# AI Top Picks Selector (NEW)
try:
    from ai_top_picks_selector import AITopPicksSelector, format_ai_picks_display
    AI_PICKS_AVAILABLE = True
except ImportError:
    AI_PICKS_AVAILABLE = False
    print("⚠️ AI Top Picks Selector not available - running without AI top picks")

# AI Catalyst & News Analyzer (NEW)
try:
    from ai_catalyst_analyzer import AIStockCatalystAnalyzer, format_catalyst_display, enhance_picks_with_catalysts
    AI_CATALYST_AVAILABLE = True
except ImportError:
    AI_CATALYST_AVAILABLE = False
    print("⚠️ AI Catalyst Analyzer not available - running without catalyst analysis")

# Market Timing Signal (NEW)
try:
    from market_timing_signal import MarketTimingSignal
    MARKET_TIMING_AVAILABLE = True
except ImportError:
    MARKET_TIMING_AVAILABLE = False
    print("⚠️ Market Timing Signal not available - running without market timing")

# Market Day Advisor (NEW - Phase 2)
try:
    from market_day_advisor import MarketDayAdvisor
    MARKET_DAY_ADVISOR_AVAILABLE = True
except ImportError:
    MARKET_DAY_ADVISOR_AVAILABLE = False
    # print("⚠️ Market Day Advisor not available - running without skip warnings")

# Short-Term Momentum Scanner (NEW - Phase 2)
try:
    from short_term_momentum import ShortTermMomentum
    SHORT_TERM_MOMENTUM_AVAILABLE = True
except ImportError:
    SHORT_TERM_MOMENTUM_AVAILABLE = False
    # print("⚠️ Short-Term Momentum Scanner not available - running without swing trade detection")


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
        
        # Initialize ML meta-predictor
        self.ml_predictor = None
        self.needs_real_training = False
        
        if ML_AVAILABLE:
            print("🤖 Initializing ML Meta-Predictor...")
            self.ml_predictor = MLMetaPredictor()
            
            # Try to load real models first
            if self.ml_predictor.load_models():
                print("✅ ML Enhancement enabled - Loaded REAL market models")
            else:
                print("⚠️ Real ML models not found - ML will remain disabled until trained on REAL data")
                self.needs_real_training = True
        
        # Initialize AI Universe Selector (NEW Phase 1)
        self.ai_selector = None
        if AI_SELECTOR_AVAILABLE:
            print("🌍 Initializing AI Universe Selector...")
            self.ai_selector = AIUniverseSelector()
            if self.ai_selector.enabled:
                print("✅ AI Universe Selection enabled - will pre-scan market for best sectors")
            else:
                print("⚠️ AI Universe Selection disabled - Grok API key not found")

        # Initialize AI Market & Pick Validator (NEW)
        self.ai_validator = None
        if AI_VALIDATOR_AVAILABLE:
            print("🧠 Initializing AI Market & Pick Validator...")
            self.ai_validator = AIMarketValidator()
            if self.ai_validator.enabled:
                print("✅ AI Validator enabled - will analyze market conditions and validate picks")
            else:
                print("⚠️ AI Validator disabled - Grok API key not found")
        
        if AI_PICKS_AVAILABLE:
            print("🎯 Initializing AI Top Picks Selector...")
            self.ai_picks_selector = AITopPicksSelector()
            if self.ai_picks_selector.enabled:
                print("✅ AI Top Picks enabled - will select best opportunities using complete intelligence")
            else:
                print("⚠️ AI Top Picks will use algorithmic fallback - Grok API key not found")
        
        # Initialize Macro Economic Analyzer (NEW)
        self.macro_analyzer = MacroEconomicAnalyzer()
        print("🌍 Initializing Macro-Economic Analyzer (Yields, DXY, VIX)...")
        
        # Initialize AI Catalyst Analyzer (NEW)
        self.catalyst_analyzer = None
        if AI_CATALYST_AVAILABLE:
            print("🔍 Initializing AI Catalyst & News Analyzer...")
            self.catalyst_analyzer = AIStockCatalystAnalyzer()
            if self.catalyst_analyzer.enabled:
                print("✅ AI Catalyst Analysis enabled - will analyze news, catalysts, and risks for top picks")
            else:
                print("⚠️ AI Catalyst Analysis will use fallback - Grok API key not found")
        
        # Initialize Market Timing Signal (NEW)
        self.market_timing = None
        if MARKET_TIMING_AVAILABLE:
            self.market_timing = MarketTimingSignal()
            print("📊 Market Timing Signal enabled - will provide clear BUY/WAIT/SELL signals")
        
        # Initialize Market Day Advisor (NEW - Phase 2)
        self.market_day_advisor = None
        if MARKET_DAY_ADVISOR_AVAILABLE:
            self.market_day_advisor = MarketDayAdvisor()
            print("🚦 Market Day Advisor enabled - will provide Skip Today warnings")
        
        # Initialize Short-Term Momentum Scanner (NEW - Phase 2)
        self.momentum_scanner = None
        if SHORT_TERM_MOMENTUM_AVAILABLE:
            self.momentum_scanner = ShortTermMomentum()
            print("📈 Short-Term Momentum Scanner enabled - swing trade detection active")
        
        # Guardrails DISABLED - Premium universe pre-screened
        self.guard_enabled = False
        
        # Symbol hygiene
        self._symbol_denylist = self._load_symbol_denylist()
        self._denylist_excluded = []
        
        print("✅ Premium Ultimate Strategy initialized")
        print("   Using 15 quality metrics instead of 200+ indicators")

        # Global trading mode (NORMAL / DEFENSIVE / NO_NEW_TRADES / AGGRESSIVE)
        self.global_trading_mode = None
    
    def run_ultimate_strategy(self, progress_callback=None, *, auto_export: bool = True):
        """
        Run Premium Ultimate Strategy
        
        1. Analyze all stocks with 15 quality metrics
        2. Apply 5 investment perspectives
        3. Find consensus (3/5, 4/5, 5/5 agreement)
        4. Optional AI review and market analysis
        
        Returns:
            dict: Consensus recommendations with quality breakdowns
        """
        from datetime import datetime
        self.analysis_start_time = datetime.now()
        
        if progress_callback:
            progress_callback("Starting Premium Ultimate Strategy...", 0)
        
        # STEP 1: Smart Universe Selection (AI Phase 1)
        full_universe = []
        ai_market_reasoning = ""
        ai_focus_sectors = []
        
        if self.ai_selector and self.ai_selector.enabled:
            if progress_callback:
                progress_callback("🤖 AI performing global market scan...", 2)
            
            try:
                # Target ~150 best stocks for the current market condition
                selection_result = self.ai_selector.select_universe(target_size=150)
                full_universe = selection_result.get('universe', [])
                ai_market_reasoning = selection_result.get('reasoning', '')
                ai_focus_sectors = selection_result.get('focus_sectors', [])
                
                print(f"✅ AI Universe Selection: Using {len(full_universe)} stocks")
                print(f"   Reasoning: {ai_market_reasoning}")
                
            except Exception as e:
                print(f"⚠️ AI Universe Selection failed: {e}. Falling back to full list.")
                full_universe = self.analyzer._get_expanded_stock_universe()
        else:
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
        print(f"   Perspectives: 5 investment styles for consensus")
        print(f"{'='*80}\n")
        
        # STEP 1.5: Train ML on Real Data (if needed)
        analyzer_enable_training = bool(getattr(self.analyzer, 'enable_training', True))
        analyzer_data_mode = str(getattr(self.analyzer, 'data_mode', '') or '').lower()
        if self.needs_real_training and self.ml_predictor and analyzer_enable_training and analyzer_data_mode != 'light':
            self._train_ml_on_real_data(full_universe, progress_callback)
        
        # STEP 2: Analyze market conditions
        if progress_callback:
            progress_callback("Analyzing market conditions (finding regime)...", 10)
        
        # Get base market analysis
        market_analysis = self._analyze_market_conditions()
        
        # Prepare context from what we ALREADY know (to avoid re-fetching failures)
        macro_context_args = {
            'vix': market_analysis.get('vix_level'),
            'spy_trend': 'UP' if market_analysis.get('spy_return_1d', 0) > 0 else 'DOWN' # Simple proxy from 1d return
        }
        
        # Get REAL Macro Logic (Yields, DXY) + Merge with known VIX
        macro_context = self.macro_analyzer.analyze_macro_context(external_context=macro_context_args)
        if macro_context:
            print(f"   Using Macro Context: {macro_context.get('summary')}")
            # Merge macro data into market_analysis
            market_analysis.update(macro_context)
            market_analysis['macro_regime'] = macro_context.get('regime')
            market_analysis['macro_score'] = macro_context.get('macro_score')
        
        # Inject AI Phase 1 Context
        if ai_market_reasoning:
            market_analysis['ai_phase1_reasoning'] = ai_market_reasoning
            market_analysis['ai_focus_sectors'] = ai_focus_sectors
        
        # STEP 2.25: MARKET TIMING SIGNAL (NEW - Critical for actionable decisions)
        market_timing_signal = None
        if self.market_timing:
            if progress_callback:
                progress_callback("Generating market timing signal...", 11)
            
            market_timing_signal = self.market_timing.analyze_market_conditions(market_analysis)
            
            # Display market timing signal prominently
            print(self.market_timing.format_for_display(market_timing_signal))
            
            # Store for later use
            market_analysis['timing_signal'] = market_timing_signal
            
        # STEP 2.3: MARKET DAY ADVISOR (NEW - Phase 2 - Skip Today Warnings)
        self.market_day_assessment = None
        if self.market_day_advisor:
            if progress_callback:
                progress_callback("Generating trading day assessment...", 12)
            
            self.market_day_assessment = self.market_day_advisor.analyze_trading_conditions(market_analysis)
            
            # Display Market Day Assessment prominently
            print(self.market_day_advisor.format_for_display(self.market_day_assessment))
            
            # Store in market_analysis for Excel/UI
            market_analysis['day_assessment'] = self.market_day_assessment
            
            # If SKIP is recommended, still continue but flag it
            if self.market_day_assessment.get('skip_today'):
                print("\n" + "⚠️ " * 20)
                print("🔴 SKIP TODAY RECOMMENDED - Consider waiting for better conditions!")
                print("⚠️ " * 20 + "\n")

        
        # STEP 2.5: AI Market Tradability Check (NEW)
        self.market_tradability = None  # Reset at start of run
        market_tradability = {}
        if self.ai_validator and self.ai_validator.enabled:
            if progress_callback:
                progress_callback("AI analyzing if now is good time to trade...", 12)
            
            print(f"\n{'='*80}")
            print("🧠 AI MARKET TRADABILITY ANALYSIS")
            print(f"{'='*80}")
            market_tradability = self.ai_validator.analyze_market_tradability(market_analysis) or {}
            if not market_tradability.get('trade_recommendation'):
                market_tradability = self.ai_validator._default_market_analysis()
            
            print(f"AI Trade Recommendation: {market_tradability.get('trade_recommendation', 'UNKNOWN')}")
            print(f"Confidence: {market_tradability.get('confidence', 0)}%")
            print(f"Brief: {market_tradability.get('brief_summary', 'N/A')}")
            print(f"{'='*80}\n")
            self.market_tradability = market_tradability or {}
        else:
            if self.ai_validator:
                # AI validator imported but API key missing – use informative fallback
                self.market_tradability = self.ai_validator._default_market_analysis()
            else:
                # AI validator module unavailable – provide static guidance instead of N/A
                self.market_tradability = {
                    'trade_recommendation': 'NEUTRAL',
                    'confidence': 45,
                    'brief_summary': 'AI validator unavailable in this runtime - relying on quant signals only.',
                    'reasoning': 'Install Grok/XAI integration and provide XAI_API_KEY for live guidance.',
                    'key_risks': ['AI validation module missing'],
                    'opportunities': ['Use quant consensus outputs']
                }
            market_tradability = self.market_tradability
        
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
            progress_callback("Applying 5 investment perspectives...", 70)
        
        print(f"\n{'='*80}")
        print("📊 Applying 5 Investment Perspectives to Quality Scores")
        print(f"{'='*80}")
        
        self.strategy_results = {
            'institutional': self._apply_institutional_perspective(self.base_results),
            'hedge_fund': self._apply_hedge_fund_perspective(self.base_results),
            'quant_value': self._apply_quant_value_perspective(self.base_results),
            'risk_managed': self._apply_risk_managed_perspective(self.base_results),
            'investment_bank': self._apply_investment_bank_perspective(self.base_results)
        }
        
        # STEP 5: Find consensus
        if progress_callback:
            progress_callback("Finding consensus recommendations...", 80)
        
        consensus_picks = self._find_consensus(self.strategy_results, market_analysis)
        
        # STEP 6: Apply regime filters (relaxed for premium stocks)
        if progress_callback:
            progress_callback("Applying market regime filters...", 85)
        
        consensus_picks, regime_removed = self._apply_regime_filters(
            consensus_picks, market_analysis
        )
        
        # STEP 6.5: AI Pick Validation (NEW - Critical!)
        pick_validation = {}
        if self.ai_validator and self.ai_validator.enabled and consensus_picks:
            if progress_callback:
                progress_callback("AI validating picks with news, sentiment, risks...", 87)
            
            print(f"\n{'='*80}")
            print("🧠 AI PICK VALIDATION (News, Sentiment, Hidden Risks)")
            print(f"{'='*80}")
            
            # Get top tier picks for validation
            top_picks = [p for p in consensus_picks if p['strategies_agreeing'] >= 3][:10]
            
            # Create context object from Phase 1 data (injected into market_analysis earlier)
            ai_phase1_ctx = {
                'ai_market_reasoning': market_analysis.get('ai_phase1_reasoning'),
                'ai_focus_sectors': market_analysis.get('ai_focus_sectors')
            }
            pick_validation = self.ai_validator.validate_picks(top_picks, market_analysis, ai_phase1_ctx)
            
            print(f"Overall AI Validation: {pick_validation.get('overall_validation', 'UNKNOWN')}")
            print(f"Summary: {pick_validation.get('summary', 'N/A')}")
            
            # Merge AI validation into consensus picks
            validated_by_symbol = {
                v['symbol']: v 
                for v in pick_validation.get('validated_picks', [])
            }
            
            for pick in consensus_picks:
                if pick['symbol'] in validated_by_symbol:
                    ai_val = validated_by_symbol[pick['symbol']]
                    pick['ai_validation'] = ai_val.get('ai_validation', 'NEUTRAL')
                    pick['ai_risk_level'] = ai_val.get('risk_level', 'MEDIUM')
                    pick['ai_profit_potential'] = ai_val.get('profit_potential', 'MEDIUM')
                    pick['ai_news_sentiment'] = ai_val.get('news_sentiment', 'NEUTRAL')
                    pick['ai_hidden_risks'] = ', '.join(ai_val.get('hidden_risks', []))
                    pick['ai_verdict'] = ai_val.get('brief_verdict', 'No AI validation')
                    
                    print(f"  {pick['symbol']}: {pick['ai_validation']} - {pick['ai_verdict'][:60]}...")
            
            print(f"{'='*80}\n")
        
        # STEP 6.75: AI CATALYST & NEWS ANALYSIS (NEW - deep dive for top tier)
        catalyst_results = []
        if self.catalyst_analyzer and consensus_picks:
            print(f"\n{'='*80}")
            print("🔍 STEP 6.75: AI CATALYST & NEWS ANALYSIS")
            print(f"{'='*80}\n")
            print("Analyzing catalysts, news, and risks for TOP TIER stocks...")
            print("(Prioritizing 5/5 agreement and highest quality picks)")
            
            try:
                # Analyze top tier stocks (highest agreement first, max 10 total)
                catalyst_results = self.catalyst_analyzer.batch_analyze_catalysts(
                    stocks=consensus_picks,
                    market_context=market_analysis,
                    max_stocks=10  # Focus on top 10 for API efficiency
                )
                
                # Display catalyst analysis
                if catalyst_results:
                    print(format_catalyst_display(catalyst_results))
                    
                    # Enhance picks with catalyst data
                    consensus_picks = enhance_picks_with_catalysts(consensus_picks, catalyst_results)
                    print("✅ Catalyst data merged into picks")
                
            except Exception as e:
                print(f"⚠️ Catalyst analysis failed: {e}")
        
        # Store consensus recommendations
        self.consensus_recommendations = consensus_picks
        
        # STEP 7: Optional: Get AI review for top picks
        if progress_callback:
            progress_callback("Generating AI insights...", 90)
        
        ai_insights = self._get_ai_market_review(
            consensus_picks, market_analysis, self.base_results
        )
        
        # STEP 7.5: AI TOP PICKS SELECTION (NEW - combines ALL intelligence layers)
        
        # Calculate Base Ultimate Score (Pre-AI) for ALL picks
        # This ensures we have a score even if AI fails or for validation
        print(f"📊 Calculating Ultimate Scores for {len(consensus_picks)} candidates...")
        for pick in consensus_picks:
            try:
                qual_score = float(pick.get('quality_score', 0) or 0)
                cons_score = float(pick.get('consensus_score', 0) or 0)
                ml_prob = pick.get('ml_probability')
                
                if ml_prob is not None:
                    # Full scoring with ML
                    ml_score = float(ml_prob) * 100.0
                    uv_score = (qual_score * 0.40) + (cons_score * 0.30) + (ml_score * 0.30)
                else:
                    # Fallback without ML (re-weight)
                    uv_score = (qual_score * 0.60) + (cons_score * 0.40)
                
                pick['ultimate_score'] = uv_score
            except Exception:
                pick['ultimate_score'] = float(pick.get('quality_score', 0) or 0)

        ai_top_picks = None
        if self.ai_picks_selector and consensus_picks:
            print(f"\n{'='*80}")
            print("🎯 STEP 7.5: AI TOP PICKS SELECTION")
            print(f"{'='*80}\n")
            print(f"🤖 Analyzing {len(consensus_picks)} consensus picks to select BEST opportunities...")
            print("   Combining: Quality + Consensus + ML + AI Validation")
            
            try:
                ai_top_picks = self.ai_picks_selector.select_top_picks(
                    consensus_picks=consensus_picks,
                    market_context=market_analysis,
                    max_picks=10  # Top 10 AI-selected picks
                )
                
                # Display AI top picks (BRIEF format)
                print(format_ai_picks_display(ai_top_picks))
                
            except Exception as e:
                print(f"⚠️ AI top picks selection failed: {e}")
                ai_top_picks = None

        ai_top_pick_lookup = {}
        if ai_top_picks and ai_top_picks.get('ai_top_picks'):
            ai_top_pick_lookup = {pick.get('symbol'): pick for pick in ai_top_picks.get('ai_top_picks', [])}

        for pick in consensus_picks:
            ai_info = ai_top_pick_lookup.get(pick.get('symbol')) if ai_top_pick_lookup else None
            if ai_info:
                pick['ai_top_pick_flag'] = True
                pick['ai_top_pick_rank'] = ai_info.get('rank')
                pick['ai_top_pick_action'] = ai_info.get('action')
                pick['ai_top_pick_position'] = ai_info.get('position_size')
                pick['ai_top_pick_entry'] = ai_info.get('entry_timing')
                pick['ai_top_pick_reason'] = ai_info.get('why_selected')
            else:
                pick.setdefault('ai_top_pick_flag', False)
                pick.setdefault('ai_top_pick_rank', None)
                pick.setdefault('ai_top_pick_action', None)
                pick.setdefault('ai_top_pick_position', None)
                pick.setdefault('ai_top_pick_entry', None)
                pick.setdefault('ai_top_pick_reason', None)
        
        # STEP 8: Prepare final results
        if progress_callback:
            progress_callback("Preparing final results...", 95)
        
        final_results = self._prepare_final_results(
            consensus_picks, market_analysis, ai_insights, ai_top_picks
        )
        
        # STEP 9: Auto-export if requested
        if auto_export:
            if consensus_picks:
                try:
                    print(f"\n📊 Exporting {len(consensus_picks)} consensus picks to Excel...")
                    from excel_export import export_analysis_to_excel
                    self._export_results(consensus_picks, final_results)
                except Exception as e:
                    print(f"⚠️ Excel export failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⚠️ No consensus picks to export - check if analysis found any 2+ agreement stocks")
        
        if progress_callback:
            progress_callback("Analysis complete!", 100)
        
        return final_results

    def _train_ml_on_real_data(self, universe: List[str], progress_callback=None):
        """
        Train ML models on real data from a subset of the universe.
        Uses 'time travel' validation: trains on data from 30 days ago vs today's price.
        """
        print(f"\n{'='*80}")
        print("🎓 TRAINING ML MODELS ON REAL DATA")
        print(f"{'='*80}")
        
        try:
            analyzer_enable_training = bool(getattr(self.analyzer, 'enable_training', True))
            analyzer_data_mode = str(getattr(self.analyzer, 'data_mode', '') or '').lower()
        except Exception:
            analyzer_enable_training = True
            analyzer_data_mode = ''

        if not analyzer_enable_training or analyzer_data_mode == 'light':
            print("⚠️ ML training skipped (training disabled or light mode).")
            return

        if len(universe) < 50:
            print("⚠️ ML training skipped (universe too small to collect enough real samples).")
            return

        # Select a representative subset (top 60 liquid stocks for speed/reliability)
        training_subset = universe[:60]
        
        if progress_callback:
            progress_callback("Fetching real data for ML training...", 9)
            
        print(f"   Fetching history for {len(training_subset)} stocks to calibrate AI...")
        
        training_data = []
        valid_count = 0
        
        for i, symbol in enumerate(training_subset):
            try:
                # Get comprehensive data
                stock_data = self.analyzer.data_fetcher.get_comprehensive_stock_data(symbol)
                if not stock_data or 'data' not in stock_data:
                    continue
                    
                hist = stock_data['data']
                if len(hist) < 90: # Need enough history (60 days + 30 days target)
                    continue
                
                # Time Travel: Go back 30 days
                # We want to predict returns over the NEXT 30 days
                lookback_days = 30
                target_idx = len(hist) - lookback_days
                
                if target_idx < 60:
                    continue
                    
                # Slice history to represent "the past"
                past_hist = hist.iloc[:target_idx]
                
                # Calculate the ACTUAL return that happened (the target)
                past_price = hist['Close'].iloc[target_idx-1] # Price at end of "past"
                current_price = hist['Close'].iloc[-1]        # Price today
                
                if past_price <= 0:
                    continue
                    
                actual_forward_return = ((current_price - past_price) / past_price) * 100
                
                # Analyze the "past" state to get features
                # We use the same analyzer but with truncated history
                past_analysis = self.premium_analyzer.analyze_stock(
                    symbol, 
                    hist_data=past_hist, 
                    info=stock_data.get('info', {})
                )
                
                if past_analysis and past_analysis.get('success'):
                    # Attach the known target
                    past_analysis['forward_return'] = actual_forward_return
                    training_data.append(past_analysis)
                    valid_count += 1
                    print(f"   + Added training sample: {symbol} (Target: {actual_forward_return:+.1f}%)", end='\r')
                    
            except Exception:
                continue
                
        print(f"\n   Collected {valid_count} valid training samples.")
        
        if len(training_data) >= 50:
            self.ml_predictor.train_with_real_data(training_data)
            self.needs_real_training = False
        else:
            print("⚠️ Could not collect enough real data to train ML reliably. ML disabled for this run.")
            self.needs_real_training = True

    def _determine_global_trading_mode(self, market_analysis: Dict) -> str:
        """Determine high-level trading mode from market timing + AI tradability.

        Modes:
            AGGRESSIVE   – very favorable, low VIX, strong signals
            NORMAL       – default
            DEFENSIVE    – caution / mixed signals
            NO_NEW_TRADES – avoid new entries, protect capital
        """
        try:
            timing = market_analysis.get('timing_signal') or {}
            tradability = getattr(self, 'ai_validator', None)
            # ai_validator stores only class; actual market_tradability dict is attached later
            market_tradability = getattr(self, 'market_tradability', None)

            action = str(timing.get('action', '')).upper()
            signal = str(timing.get('signal', '')).upper()
            vix_raw = market_analysis.get('vix', None)
            vix = float(vix_raw) if vix_raw is not None else None
            trade_rec = str(market_tradability.get('trade_recommendation', '')).upper() if isinstance(market_tradability, dict) else ''

            # Hard no-trade conditions
            if action == 'SELL' or trade_rec == 'AVOID':
                return 'NO_NEW_TRADES'

            # Defensive conditions (also default to defensive if VIX is unavailable)
            if vix is None:
                return 'DEFENSIVE'
            if action == 'WAIT' or signal in ('WAIT', 'CAUTION') or trade_rec == 'CAUTION' or vix >= 25:
                return 'DEFENSIVE'

            # Aggressive only when everything lines up
            if action == 'BUY' and trade_rec == 'FAVORABLE' and vix < 18:
                return 'AGGRESSIVE'

            return 'NORMAL'
        except Exception:
            return 'NORMAL'

    def _compute_entry_score(self, pick: Dict, market_analysis: Dict) -> float:
        """Compute regime-aware entry score (0-100) for a single pick.

        Combines: quality, consensus, ML, AI validation, catalyst score, and regime.
        Higher = more suitable for new entries *today*.
        """
        try:
            # Base components
            quality = float(pick.get('quality_score', 0) or 0)
            consensus = float(pick.get('consensus_score', 0) or 0)
            ml_prob_raw = pick.get('ml_probability', None)
            has_ml_probability = ml_prob_raw is not None

            if has_ml_probability:
                try:
                    ml_prob = float(ml_prob_raw)
                except (TypeError, ValueError):
                    ml_prob = 0.0
                ml_prob = max(0.0, min(1.0, ml_prob))
                ml_score = ml_prob * 100.0
            else:
                # Neutral fallback so missing ML predictions do not penalize entry timing
                ml_prob = None
                neutral_component = (quality + consensus) / 2.0 if (quality or consensus) else 70.0
                ml_score = max(60.0, min(95.0, neutral_component))

            # Store whether ML insights were available for downstream tightening logic
            pick['_entry_score_has_ml'] = has_ml_probability
            catalyst_score = float(pick.get('catalyst_score', 50) or 50)  # 0-100, default neutral
            agreement = int(pick.get('strategies_agreeing', 0) or 0)

            # Normalize and weight components
            base = 0.0
            base += 0.30 * quality
            base += 0.25 * consensus
            base += 0.25 * ml_score
            base += 0.10 * catalyst_score
            base += 0.10 * (25 * max(0, agreement - 2))  # 0,25,50,75 for 2/3/4/5

            # AI validation modifiers
            ai_val = str(pick.get('ai_validation', '')).upper()
            ai_risk = str(pick.get('ai_risk_level', '')).upper()
            earnings = str(pick.get('earnings_outlook', '')).upper()

            if ai_val == 'CONFIRMED':
                base += 5
            elif ai_val == 'REJECTED':
                base -= 25

            if ai_risk == 'LOW':
                base += 5
            elif ai_risk == 'HIGH':
                base -= 10

            if earnings == 'MISS':
                base -= 15

            # Regime modifiers
            mode = self.global_trading_mode or 'NORMAL'
            momentum_score = float(pick.get('momentum', {}).get('score', 0) or 0)
            
            # SMART AGGRESSION: Momentum Leader Check
            # If momentum is elite (>90), we ignore Defensive mode penalties
            is_momentum_leader = momentum_score >= 90
            
            if mode == 'DEFENSIVE':
                if is_momentum_leader:
                    base += 5  # Bonus for relative strength
                else:
                    base -= 15 # Standard penalty for defensive mode
            elif mode == 'NO_NEW_TRADES':
                base -= 40
            elif mode == 'AGGRESSIVE':
                base += 5

            # Clamp to 0-100
            # If ML data was missing we slightly uplift the score to preserve historic behaviour
            if not has_ml_probability:
                base += 4.0

            return float(max(0.0, min(100.0, base)))
        except Exception:
            return float(pick.get('ultimate_score', 0) or 0)
    
    def _run_quality_analysis(self, symbols: List[str], progress_callback=None) -> Dict:
        """
        Run quality analysis on all stocks using PremiumStockAnalyzer with batch processing.
        If data fetches fail (delisted/unavailable symbols), automatically backfill with
        TFSA-friendly replacements so the analyzed universe stays at full strength.
        """
        import time
        import time
        import gc
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {}
        total = len(symbols)
        batch_size = 50  # Process 50 stocks per batch
        failed_symbols: List[str] = []

        print(f"\n📊 Analyzing {total} stocks with 15 quality metrics...")
        print(f"🔄 Using batch processing: {batch_size} stocks per batch with 15s rest periods (Parallelized)")

        def analyze_symbol(symbol: str, global_idx: Optional[int] = None, total_count: Optional[int] = None) -> bool:
            """Shared analysis routine so we can reuse it when backfilling."""
            try:
                # Removed progress_callback from thread to prevent Streamlit context errors
                
                # Smart Rate Limiting (Exponential Backoff)
                rate_limit_manager.acquire('YAHOO')
                
                try:
                    stock_data = self.analyzer.data_fetcher.get_comprehensive_stock_data(symbol)
                    rate_limit_manager.success('YAHOO')
                except Exception as e:
                    if '429' in str(e) or 'Too Many Requests' in str(e):
                        rate_limit_manager.handle_error('YAHOO', 429)
                        print(f"   ⚠️ Rate limit hit for {symbol}, backing off...")
                        return False # Retry logic is handled by backoff + failed_symbols list checks later? 
                        # Actually just failing here means it goes to failed_symbols.
                    raise e
                
                if not stock_data or 'data' not in stock_data:
                    failed_symbols.append(symbol)
                    return False

                hist_data = stock_data.get('data')
                info = stock_data.get('info', {})

                quality_result = self.premium_analyzer.analyze_stock(
                    symbol, hist_data=hist_data, info=info
                )

                if quality_result and quality_result.get('success'):
                    results[symbol] = quality_result

                    if global_idx and total_count and global_idx % 20 == 0:
                        print(f"   ✅ Analyzed {global_idx}/{total_count} stocks")
                        sample = results[symbol]
                        # Reduced logging verbosity
                        # print(f"      📋 Sample {symbol} quality_score: {sample.get('quality_score', 'MISSING')}")
                    return True

                failed_symbols.append(symbol)
                # Log failures occasionally
                if quality_result and not quality_result.get('success') and global_idx and global_idx % 50 == 0:
                    error_msg = quality_result.get('error', 'Unknown error')
                    print(f"   ⚠️ {symbol}: {error_msg}")
                return False

            except Exception as exc:
                failed_symbols.append(symbol)
                print(f"   ⚠️ Error analyzing {symbol}: {exc}")
                return False

        # Process in batches with parallel execution
        with ThreadPoolExecutor(max_workers=4) as executor:  # Slightly increased workers
            for batch_start in range(0, total, batch_size):
                batch_end = min(batch_start + batch_size, total)
                batch_symbols = symbols[batch_start:batch_end]
                batch_num = (batch_start // batch_size) + 1
                total_batches = (total + batch_size - 1) // batch_size

                print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch_symbols)} stocks)...")
                
                # Submit batch to thread pool WITHOUT Streamlit context hack
                # We map future -> (symbol, index)
                futures = {}
                for idx, symbol in enumerate(batch_symbols, start=batch_start):
                    # We pass global_idx for logging purposes inside, but NOT for UI
                    futures[executor.submit(analyze_symbol, symbol, idx + 1, total)] = (symbol, idx + 1)
                
                # Wait for batch to complete and update progress in MAIN thread
                completed_in_batch = 0
                for future in as_completed(futures):
                    sym, g_idx = futures[future]
                    completed_in_batch += 1
                    
                    # Update UI from main thread
                    if progress_callback and g_idx % 5 == 0: # Update every 5 stocks
                        pct = int(15 + (g_idx / max(total, 1) * 55))
                        pct = min(70, pct)
                        progress_callback(f"Analyzing {sym} ({g_idx}/{total})...", pct)
                    
                    try:
                        future.result()
                    except Exception as e:
                        print(f"   ⚠️ Thread error for {sym}: {e}")

                # Explicitly clear memory after each batch
                gc.collect()

                # No manual sleep needed - Smart Rate Limiter handles it dynamically
                # if batch_end < total:
                #     print("😴 Resting 15 seconds before next batch (avoiding rate limits)...")
                #     time.sleep(15)

        print(f"\n✅ Quality analysis complete: {len(results)}/{total} stocks successful")

        # Attempt to backfill missing symbols to maintain full universe size
        target_min = max(total, 680)
        if len(results) < target_min:
            needed = target_min - len(results)
            print(f"🔁 {needed} symbols missing due to data gaps — sourcing replacements...")

            candidate_pool: List[str] = []
            try:
                from cleaned_high_potential_universe import sanitize_runtime_universe, _get_reserve_pool, _load_valid_questrade_symbols  # type: ignore

                updated_universe = sanitize_runtime_universe(symbols, failed_symbols=failed_symbols, target_min=target_min)
                for sym in updated_universe:
                    if sym not in results and sym not in symbols and sym not in candidate_pool:
                        candidate_pool.append(sym)
                        if len(candidate_pool) >= needed:
                            break

                if len(candidate_pool) < needed:
                    extra_candidates, _ = _load_valid_questrade_symbols()
                    for sym in extra_candidates:
                        if sym not in results and sym not in symbols and sym not in candidate_pool:
                            candidate_pool.append(sym)
                            if len(candidate_pool) >= needed:
                                break

                if len(candidate_pool) < needed:
                    for sym in _get_reserve_pool():
                        if sym not in results and sym not in candidate_pool:
                            candidate_pool.append(sym)
                            if len(candidate_pool) >= needed:
                                break

            except Exception as exc:
                print(f"⚠️ Unable to access replacement universes: {exc}")

            if len(candidate_pool) < needed:
                try:
                    from questrade_valid_universe import get_questrade_valid_universe
                    for sym in get_questrade_valid_universe():
                        if sym not in results and sym not in symbols and sym not in candidate_pool:
                            candidate_pool.append(sym)
                            if len(candidate_pool) >= needed:
                                break
                except Exception as exc:
                    print(f"⚠️ Unable to extend candidate pool from Questrade universe: {exc}")

            candidate_pool = candidate_pool[:needed]

            if candidate_pool:
                print(f"🔧 Backfilling with {len(candidate_pool)} replacement symbols...")
                start_idx = total
                for offset, symbol in enumerate(candidate_pool, 1):
                    analyze_symbol(symbol, global_idx=start_idx + offset, total_count=target_min)

                print(f"✅ Backfill complete. Total analyzed: {len(results)} stocks")
            else:
                print("⚠️ Replacement pool empty – final universe smaller than target")

        final_count = len(results)
        if final_count < target_min:
            print(f"⚠️ Final analyzed count {final_count} remains below target {target_min}. Review TFSA alignment lists or data availability logs.")
        else:
            print(f"✅ Final analyzed count {final_count} meets or exceeds target {target_min}")

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
            
            # Institutional threshold: prefer quality (slightly relaxed)
            if inst_score >= 60:
                picks.append({
                    'symbol': symbol,
                    'score': round(inst_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if inst_score >= 70 else 'WEAK BUY',
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
            
            # Hedge fund threshold: relaxed slightly (60→55) to enable 5/5 agreement
            if hf_score >= 55:
                picks.append({
                    'symbol': symbol,
                    'score': round(hf_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if hf_score >= 65 else 'WEAK BUY',
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
            
            # Value threshold: prefer quality fundamentals (slightly relaxed)
            if value_score >= 60:
                picks.append({
                    'symbol': symbol,
                    'score': round(value_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if value_score >= 70 else 'WEAK BUY',
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
            
            # Risk-managed threshold: relaxed (65→58) to enable 5/5 agreement
            if risk_score >= 58:
                picks.append({
                    'symbol': symbol,
                    'score': round(risk_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if risk_score >= 75 else 'WEAK BUY',
                    'perspective': 'Risk-Managed',
                    'risk_level': result['risk']['risk_level'],
                    'beta': result['risk'].get('beta'),
                    'current_price': result['current_price']
                })
        
        picks.sort(key=lambda x: x['score'], reverse=True)
        print(f"   Risk-Managed Core: {len(picks)} picks (focus: safety + low risk)")
        return picks
    
    def _apply_investment_bank_perspective(self, quality_results: Dict) -> List[Dict]:
        """
        Perspective 5: Investment Bank Level
        Focus: Analyst consensus, strong fundamentals, and earnings quality.
        The "Wall Street" view.
        """
        picks = []
        
        for symbol, result in quality_results.items():
            if not result.get('success'):
                continue
                
            # Investment Bank Criteria (Analyst focus)
            # 1. Strong Fundamental Score (Quality)
            # 2. High Analyst Rating/Coverage (Wall Street Banking)
            # TUNED: Relaxed thresholds to enable 5/5 agreement on quality stocks
            
            fund_score = result['fundamentals']['score']
            # Use sentiment score as a proxy for analyst consensus/coverage
            analyst_score = result['sentiment']['score'] 
            
            if (fund_score >= 60 and analyst_score >= 50) or (fund_score >= 70):
                
                # Calculate composite score for this strategy
                ib_score = (fund_score * 0.5) + (analyst_score * 0.5)
                
                picks.append({
                    'symbol': symbol,
                    'score': round(ib_score, 2),
                    'quality_score': result['quality_score'],
                    'recommendation': 'BUY' if ib_score >= 65 else 'WEAK BUY',
                    'perspective': 'Investment Bank',
                    'fundamentals_grade': result['fundamentals']['grade'],
                    'analyst_rating': result['sentiment'].get('analyst_rating', 'N/A'),
                    'current_price': result['current_price']
                })
        
        # Sort by score
        picks.sort(key=lambda x: x['score'], reverse=True)
        print(f"   🏦 Investment Bank: {len(picks)} picks (focus: analyst consensus + fundamentals)")
        return picks

    def _find_consensus(self, strategy_results: Dict, market_analysis: Dict = None) -> List[Dict]:
        """
        Find stocks where multiple strategies agree
        
        Args:
            strategy_results: Dict of strategy picks
            market_analysis: Market context for ML enhancement
        
        Returns consensus picks with agreement counts (2/5, 3/5, 4/5, 5/5)
        """
        if market_analysis is None:
            market_analysis = {}
            
        print(f"\n{'='*80}")
        print("🎯 Finding Consensus Picks (Multi-Strategy Agreement)")
        print(f"{'='*80}")
        
        # Collect all picks by symbol
        symbol_map = defaultdict(list)
        
        for s in strategy_results.get('institutional', []):
            symbol_map[s['symbol']].append({'name': 'institutional', 'score': s['score'], 'data': self.base_results.get(s['symbol'], {})})
        for s in strategy_results.get('hedge_fund', []):
            symbol_map[s['symbol']].append({'name': 'hedge_fund', 'score': s['score'], 'data': self.base_results.get(s['symbol'], {})})
        for s in strategy_results.get('quant_value', []):
            symbol_map[s['symbol']].append({'name': 'quant_value', 'score': s['score'], 'data': self.base_results.get(s['symbol'], {})})
        for s in strategy_results.get('risk_managed', []):
            symbol_map[s['symbol']].append({'name': 'risk_managed', 'score': s['score'], 'data': self.base_results.get(s['symbol'], {})})
        for s in strategy_results.get('investment_bank', []):
            symbol_map[s['symbol']].append({'name': 'investment_bank', 'score': s['score'], 'data': self.base_results.get(s['symbol'], {})})
        
        # Build consensus list
        consensus_picks = []
        for symbol, strategies in symbol_map.items():
            count = len(strategies)
            
            # Require at least 2 strategies to agree (2/5)
            if count >= 2:
                # Calculate consensus score (average of strategy scores)
                avg_score = np.mean([s['score'] for s in strategies])
                
                # Determine primary reasons
                reasons = set()
                for s in strategies:
                    if s['name'] == 'institutional': reasons.add("Institutional Quality")
                    if s['name'] == 'hedge_fund': reasons.add("Hedge Fund Momentum")
                    if s['name'] == 'quant_value': reasons.add("Deep Value")
                    if s['name'] == 'risk_managed': reasons.add("Low Risk")
                    if s['name'] == 'investment_bank': reasons.add("Wall St Consensus")
                    
                # Get base data from one of the results
                base_data = strategies[0]['data']
                
                # Flatten nested data structure for Excel compatibility
                fundamentals = base_data.get('fundamentals', {})
                momentum = base_data.get('momentum', {})
                risk = base_data.get('risk', {})
                technical = base_data.get('technical', {})
                sentiment = base_data.get('sentiment', {})
                
                consensus_picks.append({
                    'symbol': symbol,
                    'strategies_agreeing': count,
                    'agreeing_perspectives': [s['name'] for s in strategies],
                    'consensus_score': round(avg_score, 2),
                    'quality_score': base_data.get('quality_score', 0),
                    'recommendation': self._consensus_recommendation(count, avg_score, base_data.get('quality_score', 0)).get('recommendation'),
                    'confidence': self._consensus_recommendation(count, avg_score, base_data.get('quality_score', 0)).get('confidence'),
                    'sector': base_data.get('sector', 'Unknown'),
                    
                    # Flattened fundamentals for Excel
                    'pe_ratio': fundamentals.get('pe_ratio'),
                    'revenue_growth': fundamentals.get('revenue_growth'),
                    'profit_margin': fundamentals.get('profit_margin'),
                    'roe': fundamentals.get('roe'),
                    'debt_equity': fundamentals.get('debt_equity'),
                    'fundamentals_score': fundamentals.get('score'),
                    'fundamentals_grade': fundamentals.get('grade'),
                    
                    # Flattened momentum for Excel
                    'rsi_14': momentum.get('rsi'),
                    'price_trend': momentum.get('price_trend', 'neutral'),
                    'relative_strength': momentum.get('relative_strength'),
                    'volume_trend': momentum.get('volume_trend'),
                    'momentum_score': momentum.get('score'),
                    'momentum_grade': momentum.get('grade'),
                    'ma_50': momentum.get('ma_50'),
                    'ma_200': momentum.get('ma_200'),
                    'volume_ratio': momentum.get('volume_ratio'),
                    
                    # Flattened risk metrics for Excel
                    'beta': risk.get('beta', 1),
                    'volatility': risk.get('volatility'),
                    'sharpe_ratio': risk.get('sharpe_ratio'),
                    'max_drawdown': risk.get('max_drawdown'),
                    'var_95': risk.get('var_95'),
                    'risk_score': risk.get('score'),
                    'risk_grade': risk.get('grade'),
                    'risk_level': risk.get('risk_level', 'Unknown'),
                    
                    # Flattened technical indicators for Excel
                    'macd': technical.get('macd'),
                    'macd_signal': technical.get('macd_signal'),
                    'macd_hist': technical.get('macd_hist'),
                    'bollinger_position': technical.get('bollinger_position'),
                    'support_level': technical.get('support'),
                    'resistance_level': technical.get('resistance'),
                    'technical_score': technical.get('score'),
                    'technical_grade': technical.get('grade'),
                    'bollinger_upper': technical.get('bollinger_upper'),
                    'bollinger_lower': technical.get('bollinger_lower'),
                    'volume_sma': technical.get('volume_sma'),
                    
                    # Flattened sentiment for Excel
                    'sentiment_score': sentiment.get('score'),
                    'sentiment_grade': sentiment.get('grade'),
                    'target_upside': sentiment.get('target_upside'),
                    'institutional_ownership': sentiment.get('institutional_ownership'),
                    'analyst_rating': sentiment.get('analyst_rating'),
                    
                    # Keep nested data for backward compatibility
                    'fundamentals': fundamentals,
                    'momentum': momentum,
                    'risk': risk,
                    'technical': technical,
                    'sentiment': sentiment,
                    
                    'current_price': base_data.get('current_price', 0),
                    'tier': f"{count}/5"
                })
        
        # Sort by agreement count, then score
        consensus_picks.sort(key=lambda x: (x['strategies_agreeing'], x['consensus_score']), reverse=True)
        
    # ML Enhancement: Add ML predictions to consensus picks
        ml_ready = bool(self.ml_predictor and ML_AVAILABLE and getattr(self.ml_predictor, 'is_trained', False))
        if ml_ready:
            print(f"\n🤖 Enhancing {len(consensus_picks)} consensus picks with ML predictions...")
            for pick in consensus_picks:
                try:
                    # Add market context to pick for ML feature extraction
                    pick['market_context'] = market_analysis
                    
                    ml_result = self.ml_predictor.predict(pick)
                    pick['ml_expected_return'] = ml_result['expected_return']
                    pick['ml_probability'] = ml_result['probability']
                    pick['ml_confidence'] = ml_result['confidence']
                    pick['ml_feature_importance'] = ml_result.get('feature_importance', {})
                    
                    # Calculate Ultimate Score: 40% Quality + 30% Consensus + 30% ML
                    quality_component = pick.get('quality_score', 0) * 0.40
                    consensus_component = pick.get('consensus_score', 0) * 0.30
                    ml_component = (ml_result['probability'] * 100) * 0.30
                    
                    pick['ultimate_score'] = round(quality_component + consensus_component + ml_component, 2)
                    
                    # Adjust consensus confidence with ML confidence
                    original_conf = pick['confidence']
                    ml_conf = ml_result['confidence']
                    # Weighted average: 60% original, 40% ML
                    pick['confidence'] = round(original_conf * 0.6 + ml_conf * 0.4, 3)
                    
                except Exception as e:
                    print(f"   ⚠️ ML prediction failed for {pick['symbol']}: {e}")
                    pick['ml_expected_return'] = None
                    pick['ml_probability'] = None
                    pick['ml_confidence'] = None
                    pick['ml_feature_importance'] = {}
            
            # Re-sort by ML-enhanced metrics
            # Primary: strategies agreeing, Secondary: ML probability * consensus score
            consensus_picks.sort(
                key=lambda x: (
                    x['strategies_agreeing'],
                    (x.get('ml_probability', 0.5) * x['consensus_score'])
                ),
                reverse=True
            )
            print(f"✅ ML enhancement complete - picks re-ranked by ML probability")
        elif self.ml_predictor and ML_AVAILABLE:
            print("⚠️ ML enhancement skipped (no trained real models loaded)")
        
        # Compute global trading mode and per-pick entry score (regime-aware)
        self.global_trading_mode = self._determine_global_trading_mode(market_analysis)
        for pick in consensus_picks:
            pick['entry_score'] = self._compute_entry_score(pick, market_analysis)

        downgraded_counts = {'strong_buy_to_buy': 0, 'buy_to_weak': 0, 'weak_to_hold': 0}
        for pick in consensus_picks:
            ml_prob_raw = pick.get('ml_probability')
            has_ml = ml_prob_raw is not None
            ml_prob = None
            if has_ml:
                try:
                    ml_prob = float(ml_prob_raw)
                except (TypeError, ValueError):
                    ml_prob = None
                if ml_prob is not None:
                    ml_prob = max(0.0, min(1.0, ml_prob))

            entry_score = None
            entry_score_val = pick.get('entry_score')
            if entry_score_val is not None:
                try:
                    entry_score = float(entry_score_val)
                except (TypeError, ValueError):
                    entry_score = None

            def _downgrade_needed(ml_threshold: float, entry_threshold: float, fallback_threshold: float) -> bool:
                if has_ml and ml_prob is not None:
                    entry_low = entry_score is not None and entry_score < entry_threshold
                    # Only downgrade when BOTH signals are weak; tolerate single weak reads
                    if entry_score is None:
                        return ml_prob < max(0.0, ml_threshold - 0.05)
                    return (ml_prob < ml_threshold) and entry_low
                if entry_score is not None:
                    return entry_score < fallback_threshold
                return False

            if pick.get('recommendation') == 'STRONG BUY':
                if _downgrade_needed(0.60, 78.0, 64.0):
                    pick['recommendation'] = 'BUY'
                    pick['confidence'] = min(pick.get('confidence', 0.90), 0.88)
                    downgraded_counts['strong_buy_to_buy'] += 1
            elif pick.get('strategies_agreeing') == 3 and pick.get('recommendation') == 'BUY':
                if _downgrade_needed(0.54, 70.0, 58.0):
                    pick['recommendation'] = 'WEAK BUY'
                    pick['confidence'] = min(pick.get('confidence', 0.83), 0.78)
                    downgraded_counts['buy_to_weak'] += 1
            elif pick.get('strategies_agreeing') == 2 and pick.get('recommendation') == 'WEAK BUY':
                if _downgrade_needed(0.48, 62.0, 53.0):
                    pick['recommendation'] = 'HOLD'
                    pick['confidence'] = min(pick.get('confidence', 0.72), 0.68)
                    downgraded_counts['weak_to_hold'] += 1

        if any(downgraded_counts.values()):
            print("\n⚖️ Recommendation tightening applied:")
            if downgraded_counts['strong_buy_to_buy']:
                print(f"   • {downgraded_counts['strong_buy_to_buy']} symbols downgraded from STRONG BUY to BUY (ML/entry filters)")
            if downgraded_counts['buy_to_weak']:
                print(f"   • {downgraded_counts['buy_to_weak']} symbols downgraded from BUY to WEAK BUY")
            if downgraded_counts['weak_to_hold']:
                print(f"   • {downgraded_counts['weak_to_hold']} symbols downgraded from WEAK BUY to HOLD")

        # Diagnostic: Sample first consensus pick data structure
        if consensus_picks:
            sample = consensus_picks[0]
            print(f"\n🔍 DIAGNOSTIC - Sample consensus pick data structure:")
            print(f"   Symbol: {sample.get('symbol')}")
            print(f"   Quality Score: {sample.get('quality_score')}")
            print(f"   Consensus Score: {sample.get('consensus_score')}")
            if ML_AVAILABLE and 'ml_probability' in sample:
                print(f"   ML Probability: {sample.get('ml_probability', 0):.2%}")
                print(f"   ML Expected Return: {sample.get('ml_expected_return', 0):.2f}%")
            print(f"   Beta (flat): {sample.get('beta', 'MISSING')}")
            print(f"   RSI (flat as rsi_14): {sample.get('rsi_14', 'MISSING')}")
            print(f"   P/E Ratio (flat): {sample.get('pe_ratio', 'MISSING')}")
            print(f"   Revenue Growth (flat): {sample.get('revenue_growth', 'MISSING')}")
            print(f"   Nested risk dict exists: {bool(sample.get('risk'))}")
            print(f"   Nested momentum dict exists: {bool(sample.get('momentum'))}")
            print(f"   Nested fundamentals dict exists: {bool(sample.get('fundamentals'))}")
        
        # Print summary
        tier_counts = {5: 0, 4: 0, 3: 0, 2: 0}
        for pick in consensus_picks:
            tier_counts[pick['strategies_agreeing']] = tier_counts.get(pick['strategies_agreeing'], 0) + 1
        
        print(f"\n📊 Consensus Summary:")
        print(f"   5/5 Agreement (ULTIMATE BUY): {tier_counts[5]} stocks")
        print(f"   4/5 Agreement (STRONG BUY): {tier_counts[4]} stocks")
        print(f"   3/5 Agreement (BUY): {tier_counts[3]} stocks")
        print(f"   2/5 Agreement (WEAK BUY): {tier_counts[2]} stocks")
        print(f"   Total Consensus: {len(consensus_picks)} stocks")
        
        return consensus_picks
    
    def _consensus_recommendation(self, agreement: int, avg_score: float, quality_score: Optional[float] = None) -> Dict:
        """Determine recommendation based on agreement, consensus strength, and underlying quality."""
        quality_score = quality_score or 0.0

        if agreement == 5:
            if avg_score >= 80 and quality_score >= 78:
                return {
                    'recommendation': 'ULTIMATE BUY',
                    'confidence': 0.98,
                    'risk_level': 'Lowest',
                    'action': 'Buy Aggressively'
                }
            else:
                return {
                    'recommendation': 'STRONG BUY',
                    'confidence': 0.92,
                    'risk_level': 'Low',
                    'action': 'Buy'
                }
        elif agreement == 4:
            if avg_score >= 75 and quality_score >= 70:
                return {
                    'recommendation': 'STRONG BUY',
                    'confidence': 0.90,
                    'risk_level': 'Low',
                    'action': 'Buy'
                }
            else:
                return {
                    'recommendation': 'BUY',
                    'confidence': 0.85,
                    'risk_level': 'Low-Medium',
                    'action': 'Buy'
                }
        elif agreement == 3:
            if avg_score >= 70 and quality_score >= 65:
                return {
                    'recommendation': 'BUY',
                    'confidence': 0.80,
                    'risk_level': 'Medium',
                    'action': 'Accumulate'
                }
            else:
                return {
                    'recommendation': 'WEAK BUY',
                    'confidence': 0.70,
                    'risk_level': 'Medium-High',
                    'action': 'Accumulate'
                }
        elif agreement == 2:
            if avg_score >= 65 and quality_score >= 60:
                return {
                    'recommendation': 'WEAK BUY',
                    'confidence': 0.65,
                    'risk_level': 'High',
                    'action': 'Watch / Speculate'
                }
            else:
                return {
                    'recommendation': 'HOLD',
                    'confidence': 0.55,
                    'risk_level': 'Very High',
                    'action': 'Watch'
                }
        else: # 1 agreement or less (should be filtered out by _find_consensus)
            return {
                'recommendation': 'HOLD',
                'confidence': 0.50,
                'risk_level': 'Very High',
                'action': 'Watch'
            }
    
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
            
            # Only activate in caution regime - DISABLED for premium universe
            # Premium stocks are pre-screened for quality, don't need additional filtering
            if regime != 'caution':
                return list(consensus_list or []), []
            
            # RELAXED: Return all consensus picks in caution regime  
            # Premium universe is already quality-filtered
            print(f"\n⚠️ CAUTION REGIME detected - but keeping all premium consensus picks")
            return list(consensus_list or []), []
            
            # OLD STRICT FILTERS (disabled for premium universe)
            # print(f"\n⚠️ CAUTION REGIME: Applying relaxed filters")
            
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
            tier_5_picks = [p for p in consensus_picks if p['strategies_agreeing'] == 5][:5]
            tier_4_picks = [p for p in consensus_picks if p['strategies_agreeing'] == 4][:5]
            
            if not tier_5_picks and not tier_4_picks:
                return {'available': False}
            
            # Build focused prompt with quality metrics
            prompt = self._build_ai_prompt(tier_5_picks, tier_4_picks, market_ctx)

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
    
    def _build_ai_prompt(self, tier_5: List, tier_4: List, market: Dict) -> str:
        """Build comprehensive AI prompt synthesizing quant, ML, and market context"""
        
        # Calculate portfolio-level ML statistics
        ml_available_count = sum(1 for p in tier_5 if p.get('ml_probability') is not None)
        avg_ml_prob = np.mean([p.get('ml_probability', 0) for p in tier_5 if p.get('ml_probability') is not None]) if ml_available_count > 0 else 0
        avg_ml_return = np.mean([p.get('ml_expected_return', 0) for p in tier_5 if p.get('ml_expected_return') is not None]) if ml_available_count > 0 else 0
        
        prompt = f"""Analyze these premium quality stock recommendations from an AI-enhanced 5-strategy consensus system.

**ANALYSIS METHODOLOGY:**
This analysis combines THREE layers:
1. Quant Engine: 15 quality metrics (fundamentals, momentum, risk, technical, sentiment)
2. 5-Perspective Consensus: Institutional, Hedge Fund, Quant Value, Risk-Managed, Investment Bank strategies  
3. ML Ensemble: 6 models (LightGBM, XGBoost, CatBoost, RF, GB, Neural Net) with 30 features

**MARKET CONTEXT:**
- Regime: {market.get('regime', 'Unknown')}
- VIX: {market.get('vix', 'N/A')} ({['Low', 'Normal', 'Elevated', 'High'][min(3, int(market.get('vix', 15) / 15))]} volatility)
- Trend: {market.get('trend', 'Unknown')}
- Status: {market.get('status', 'Unknown')}

**PORTFOLIO-LEVEL ML INSIGHTS:**
- ML-Enhanced Picks: {ml_available_count}/{len(tier_5)}
- Average ML Probability: {avg_ml_prob:.1%}
- Average ML Expected Return: {avg_ml_return:+.1f}%
- ML Confidence Range: {min([p.get('ml_confidence', 0) for p in tier_5 if p.get('ml_confidence') is not None] or [0]):.1%} - {max([p.get('ml_confidence', 0) for p in tier_5 if p.get('ml_confidence') is not None] or [0]):.1%}

**TOP CONSENSUS PICKS (5/5 Agreement - ULTIMATE CONVICTION):**
"""
        
        for pick in tier_5:
            symbol = pick['symbol']
            fund = pick.get('fundamentals', {})
            mom = pick.get('momentum', {})
            risk = pick.get('risk', {})
            
            # ML enhancement section
            ml_section = ""
            if ML_AVAILABLE and pick.get('ml_probability') is not None:
                ml_prob = pick.get('ml_probability', 0)
                ml_return = pick.get('ml_expected_return', 0)
                ml_conf = pick.get('ml_confidence', 0)
                ml_features = pick.get('ml_feature_importance', {})
                ultimate_score = pick.get('ultimate_score', 0)
                
                # Get top 3 features driving ML prediction
                top_features = sorted(ml_features.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
                feature_str = ", ".join([f"{k}: {v:.2f}" for k, v in top_features]) if top_features else "N/A"
                
                ml_section = f"""- ML Prediction: {ml_prob:.1%} probability, {ml_return:+.1f}% expected return (confidence: {ml_conf:.1%})
  Key ML Drivers: {feature_str}
- Ultimate Score: {ultimate_score:.1f}/100 (40% Quality + 30% Consensus + 30% ML)
"""
            
            prompt += f"""
{symbol}: Quality Score {pick['quality_score']}/100
- Fundamentals: {fund.get('grade', 'N/A')} (P/E: {fund.get('pe_ratio', 'N/A')}, Revenue Growth: {fund.get('revenue_growth', 'N/A')}%, Margin: {fund.get('profit_margin', 'N/A')}%)
- Momentum: {mom.get('grade', 'N/A')} (Trend: {mom.get('price_trend', 'N/A')}, RSI: {mom.get('rsi', 'N/A')})
- Risk: {risk.get('grade', 'N/A')} ({risk.get('risk_level', 'N/A')} - Beta: {risk.get('beta', 'N/A')})
{ml_section}- Price: ${pick.get('current_price', 0):.2f}
"""
        
        if tier_4:
            prompt += "\n**Strong Picks (4/5 Agreement):**\n"
            for pick in tier_4[:3]:
                ml_info = f" | ML: {pick.get('ml_probability', 0):.0%}" if pick.get('ml_probability') is not None else ""
                prompt += f"- {pick['symbol']}: Quality {pick['quality_score']}/100, Score {pick['consensus_score']}/100{ml_info}\n"
        
        prompt += """
**Provide comprehensive AI synthesis:**
1. Market Overview (3-4 sentences): 
   - Current market conditions and regime assessment
   - How VIX level affects entry timing
   - Overall market sentiment and trend alignment

2. Top Pick Analysis (4-6 sentences):
   - Best opportunities from 5/5 consensus with ML confirmation
   - Why ML models show high conviction (reference top ML drivers)
   - Quality metrics that support these picks
   - Entry strategy for each pick

3. Portfolio Construction (2-3 sentences):
   - Diversification across sectors in top picks
   - Position sizing recommendations based on ML confidence levels
   - Overall portfolio risk vs expected return profile

4. Risk Assessment (3-4 sentences):
   - Main macro risks given current regime and VIX
   - Stock-specific risks in top picks
   - How ML confidence levels inform risk management
   - Warning signs to watch for position exits

5. Entry Timing (2-3 sentences):
   - Optimal entry approach given market conditions
   - Whether to enter all at once or scale in
   - Technical timing considerations

Respond strictly as a JSON object with keys: `market_overview`, `top_picks`, `portfolio_construction`, `risk_assessment`, `entry_timing`.
"""
        
        return prompt
    
    def _call_grok_api(self, prompt: str, api_key: str) -> Dict:
        """Call Grok API for analysis"""
        try:
            from xai_client import XAIClient

            client = XAIClient(api_key=api_key)
            if not client.is_configured():
                print("⚠️ Grok API key missing")
                return {}

            system_prompt = (
                "You are an institutional-grade AI trading strategist combining quantitative analysis, "
                "machine learning predictions, and market context. Provide conservative, actionable insights "
                "that synthesize all three layers. Return JSON only."
            )

            response = client.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1200,  # Increased for comprehensive analysis
            )

            if not isinstance(response, dict):
                return {}

            # Remove metadata we added when parsing
            response.pop("model_used", None)

            # Fallback to legacy parsing if keys missing
            expected = {"market_overview", "top_picks", "portfolio_construction", "risk_assessment", "entry_timing"}
            if expected.issubset(response.keys()):
                return response
            
            # Try legacy format
            legacy_expected = {"market_overview", "top_picks", "risk_assessment", "entry_timing"}
            if legacy_expected.issubset(response.keys()):
                # Add empty portfolio_construction
                response['portfolio_construction'] = ''
                return response

            # If the model ignored JSON request, parse text result
            raw_text = response.get("raw") if "raw" in response else str(response)
            return self._parse_ai_response(raw_text)

        except Exception as e:
            print(f"⚠️ Grok API call failed: {e}")
            return {}
    
    def _parse_ai_response(self, content: str) -> Dict:
        """Parse AI response into sections"""
        sections = {
            'market_overview': '',
            'top_picks': '',
            'portfolio_construction': '',
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
            elif 'portfolio' in lower:
                current_section = 'portfolio_construction'
            elif 'risk' in lower:
                current_section = 'risk_assessment'
            elif 'entry timing' in lower or 'timing' in lower:
                current_section = 'entry_timing'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def _calculate_trade_levels(self, pick: Dict) -> Dict:
        """Calculate concrete trade levels based on technicals and volatility"""
        try:
            current_price = pick.get('current_price', 0)
            if not current_price:
                return {}
                
            volatility = pick.get('volatility', 0.02) # Daily volatility proxy if available
            atr = current_price * (volatility if volatility else 0.02)
            
            support = pick.get('technical', {}).get('support')
            resistance = pick.get('technical', {}).get('resistance')
            
            # 1. Suggestion Buy Price
            # If strong uptrend, buy at market or slight dip. If weak, wait for deeper dip.
            score = pick.get('entry_score', 80)
            if score >= 85:
                buy_price = current_price # Buy Market
                buy_range_low = current_price * 0.995
                buy_range_high = current_price * 1.005
            else:
                buy_price = current_price * 0.99 # Limit order slightly below
                buy_range_low = current_price * 0.98
                buy_range_high = current_price * 1.00
                
            # 2. Stop Loss
            # Below support or 2x ATR
            if support and support < current_price:
                stop_loss = min(support * 0.99, current_price - (2 * atr))
            else:
                stop_loss = current_price - (2.5 * atr) # Default trailing stop logic
                
            # 3. Take Profit
            # At resistance or R:R ratio
            risk = buy_price - stop_loss
            target_rr = 2.0 # Target 2:1 Reward:Risk minimum
            min_target = buy_price + (risk * target_rr)
            
            if resistance and resistance > buy_price:
                # If resistance is far enough, use it. If too close, look higher.
                if resistance > min_target:
                    take_profit = resistance * 0.99 # Front-run resistance
                else:
                    take_profit = min_target # Breakout target
            else:
                take_profit = min_target
                
            # Formatting
            return {
                'buy_price': round(buy_price, 2),
                'buy_zone': f"${buy_range_low:.2f} - ${buy_range_high:.2f}",
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
                'risk_reward': round((take_profit - buy_price) / (buy_price - stop_loss), 2) if buy_price > stop_loss else 0
            }
        except Exception:
            return {}

    def _prepare_final_results(self, consensus: List, market: Dict, ai: Dict, ai_top_picks: Dict = None) -> Dict:
        """Prepare final results structure"""
        
        # Calculate Timing
        end_time = datetime.now()
        start_time = getattr(self, 'analysis_start_time', end_time)
        duration = (end_time - start_time).total_seconds() / 60
        
        # Inject Trade Levels into Consensus Picks
        for pick in consensus:
            levels = self._calculate_trade_levels(pick)
            pick.update(levels)

        # Inject Trade Levels into AI Top Picks (if they exist)
        if ai_top_picks and 'ai_top_picks' in ai_top_picks:
            for pick in ai_top_picks['ai_top_picks']:
                # Find matching consensus pick to reuse calculations if possible, or recalculate
                match = next((p for p in consensus if p['symbol'] == pick.get('symbol')), None)
                if match:
                    # Copy calculated levels
                    for key in ['buy_price', 'buy_zone', 'stop_loss', 'take_profit', 'risk_reward']:
                        if key in match:
                            pick[key] = match[key]
                else:
                    # Recalculate if not in consensus (rare)
                    # We might need price/volatility which might be missing in simple AI pick dict
                    # Try to find in all results
                    full_data = self.base_results.get(pick.get('symbol'), {})
                    if full_data:
                        # Create a temporary enriched dict for calculation
                        temp_pick = dict(pick)
                        temp_pick.update(full_data)
                        levels = self._calculate_trade_levels(temp_pick)
                        pick.update(levels)
            
        # Count tiers
        tier_counts = {5: 0, 4: 0, 3: 0, 2: 0}
        for pick in consensus:
            tier_counts[pick['strategies_agreeing']] = tier_counts.get(pick['strategies_agreeing'], 0) + 1
        
        # CRITICAL FIX: Include ALL analyzed stocks, not just consensus

        # Prepare complete analysis for Excel export
        all_analyzed = []
        for symbol, quality_data in self.base_results.items():
            # Flatten data structure for Excel
            fundamentals = quality_data.get('fundamentals', {})
            momentum = quality_data.get('momentum', {})
            risk = quality_data.get('risk', {})
            technical = quality_data.get('technical', {})
            sentiment = quality_data.get('sentiment', {})
            
            all_analyzed.append({
                'symbol': symbol,
                'sector': quality_data.get('sector', 'Unknown'),
                'quality_score': quality_data.get('quality_score'),
                'current_price': quality_data.get('current_price'),
                
                # Fundamentals - flattened
                'pe_ratio': fundamentals.get('pe_ratio'),
                'revenue_growth': fundamentals.get('revenue_growth'),
                'profit_margin': fundamentals.get('profit_margin'),
                'roe': fundamentals.get('roe'),
                'debt_equity': fundamentals.get('debt_equity'),
                'fundamentals_score': fundamentals.get('score'),
                'fundamentals_grade': fundamentals.get('grade', 'N/A'),
                
                # Momentum - flattened
                'rsi_14': momentum.get('rsi'),
                'price_trend': momentum.get('price_trend', 'N/A'),
                'volume_trend': momentum.get('volume_trend', 'N/A'),
                'momentum_score': momentum.get('score'),
                'momentum_grade': momentum.get('grade', 'N/A'),
                'ma_50': momentum.get('ma_50'),
                'ma_200': momentum.get('ma_200'),
                'volume_ratio': momentum.get('volume_ratio'),
                
                # Risk - flattened
                'beta': risk.get('beta'),
                'volatility': risk.get('volatility'),
                'sharpe_ratio': risk.get('sharpe_ratio'),
                'max_drawdown': risk.get('max_drawdown'),
                'var_95': risk.get('var_95'),
                'risk_score': risk.get('score'),
                'risk_grade': risk.get('grade', 'N/A'),
                'risk_level': risk.get('risk_level', 'N/A'),
                
                # Technical - flattened
                'macd': technical.get('macd'),
                'macd_signal': technical.get('macd_signal'),
                'macd_hist': technical.get('macd_hist'),
                'bollinger_position': technical.get('bollinger_position'),
                'bollinger_upper': technical.get('bollinger_upper'),
                'bollinger_lower': technical.get('bollinger_lower'),
                'support_level': technical.get('support'),
                'resistance_level': technical.get('resistance'),
                'volume_sma': technical.get('volume_sma'),
                'technical_score': technical.get('score'),
                'technical_grade': technical.get('grade', 'N/A'),
                
                # Sentiment - flattened
                'sentiment_score': sentiment.get('score'),
                'sentiment_grade': sentiment.get('grade', 'N/A'),
                'target_upside': sentiment.get('target_upside'),
                'institutional_ownership': sentiment.get('institutional_ownership'),
                'analyst_rating': sentiment.get('analyst_rating'),
                
                # Keep nested dicts for backward compatibility
                'fundamentals': fundamentals,
                'momentum': momentum,
                'risk': risk,
                'technical': technical,
                'sentiment': sentiment
            })
        
        return {
            'consensus_recommendations': consensus,
            'all_analyzed_stocks': all_analyzed,  # NEW: Complete dataset
            'market_analysis': market,
            'market_tradability': getattr(self, 'market_tradability', None),  # AI market validation
            'global_trading_mode': getattr(self, 'global_trading_mode', None),  # NEW: regime-aware trading mode
            'ai_top_picks': ai_top_picks,  # AI-selected best opportunities (NEW)
            'ai_insights': ai,
            'total_stocks_analyzed': len(self.base_results),
            'consensus_picks_count': len(consensus),
            'stocks_5_of_5': tier_counts[5],
            'stocks_4_of_5': tier_counts[4],
            'stocks_3_of_5': tier_counts[3],
            'stocks_2_of_5': tier_counts[2],
            'analysis_type': 'PREMIUM_QUALITY_CONSENSUS',
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_start_time': getattr(self, 'analysis_start_time', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_duration_minutes': round((datetime.now() - getattr(self, 'analysis_start_time', datetime.now())).total_seconds() / 60, 1),
            'denylist_excluded': len(self._denylist_excluded),
            'metrics_used': '15 quality metrics (not 200+ indicators)'
        }
    
    def _export_results(self, consensus: List, results: Dict):
        """Export results to Excel - including ALL analyzed stocks"""
        try:
            from excel_export import export_analysis_to_excel
            
            # CRITICAL FIX: Export ALL analyzed stocks, not just consensus
            all_analyzed = results.get('all_analyzed_stocks', [])
            
            # Convert consensus to export format (preserve rich metrics)
            consensus_export = []
            for pick in consensus:
                export_pick = dict(pick)
                export_pick['overall_score'] = pick.get('consensus_score')
                export_pick['consensus_score'] = pick.get('consensus_score')
                export_pick['strategies_agreeing_display'] = f"{pick.get('strategies_agreeing', 0)}/5"
                export_pick['confidence_pct'] = round(pick.get('confidence', 0) * 100, 2)
                consensus_export.append(export_pick)
            
            # Extract market timing signal from results
            market_timing_signal = results.get('market_analysis', {}).get('timing_signal')
            
            # Extract AI Universe Context (NEW)
            ai_universe_context = None
            market_analysis = results.get('market_analysis', {})
            if market_analysis.get('ai_phase1_reasoning'):
                ai_universe_context = {
                    'reasoning': market_analysis.get('ai_phase1_reasoning', ''),
                    'focus_sectors': market_analysis.get('ai_focus_sectors', [])
                }
            
            # Extract Day Assessment (NEW - Phase 2)
            day_assessment = market_analysis.get('day_assessment')
            
            # Export with BOTH datasets + AI validation + market timing + timing data
            filename, msg = export_analysis_to_excel(
                consensus_export,  # Consensus picks for main tabs
                all_stocks_data=all_analyzed,  # NEW: All 613 stocks for complete tab
                analysis_params=f'Premium Ultimate Strategy - {len(all_analyzed)} stocks analyzed, {len(consensus)} consensus picks',
                market_tradability=results.get('market_tradability'),  # AI market validation
                market_timing_signal=market_timing_signal,  # Market timing signal
                ai_universe_context=ai_universe_context, # AI Phase 1 Context
                ai_top_picks=results.get('ai_top_picks'), # AI Top Picks
                analysis_start_time=results.get('analysis_start_time'),
                analysis_end_time=results.get('analysis_end_time'),
                analysis_duration_minutes=results.get('analysis_duration_minutes'),
                day_assessment=day_assessment  # NEW: Trading Day Assessment
            )
            
            if filename:
                print(f"\n📊 Results exported to: {filename}")
                print(f"   ✅ All {len(all_analyzed)} analyzed stocks included")
                print(f"   ✅ {len(consensus)} consensus picks highlighted")
                if market_timing_signal:
                    print(f"   ✅ Market timing signal: {market_timing_signal.get('action', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️ Export failed: {e}")
            # Fallback: try simpler export
            try:
                import pandas as pd
                from datetime import datetime
                
                # Export all analyzed stocks to CSV as backup
                if results.get('all_analyzed_stocks'):
                    df = pd.DataFrame(results['all_analyzed_stocks'])
                    filename = f"ultimate_strategy_all_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    df.to_csv(filename, index=False)
                    print(f"📊 Backup export to: {filename}")
            except Exception as csv_e:
                print(f"⚠️ Backup export also failed: {csv_e}")
    
    # Helper methods
    def _analyze_market_conditions(self) -> Dict:
        """Analyze market conditions using live macro + breadth signals."""
        ctx: Dict[str, object] = {
            'status': 'NEUTRAL',
            'trend': 'sideways',
            'regime': 'neutral',
        }

        # 1) Pull cached macro context from the data fetcher (SPY/VIX, yields, etc.)
        data_fetcher = getattr(self.analyzer, 'data_fetcher', None)
        if data_fetcher is not None:
            try:
                macro_ctx = data_fetcher.get_market_context()
                if isinstance(macro_ctx, dict):
                    ctx.update(macro_ctx)
            except Exception as macro_err:
                print(f"⚠️ Market context fetch failed: {macro_err}")

        # 2) Overlay breadth/leadership regime signals (SOXX vs QQQ, etc.)
        try:
            from market_context_signals import get_market_context_signals
            signals = get_market_context_signals()
            if isinstance(signals, dict):
                ctx.update(signals)
        except Exception as signals_err:
            print(f"⚠️ Market regime signals unavailable: {signals_err}")

        # 3) Normalize key fields so downstream consumers see real data instead of defaults
        vix_level = ctx.get('vix_proxy') or ctx.get('vix')
        if vix_level is None:
            ctx['vix'] = None
        else:
            ctx['vix'] = float(vix_level)

        spy_return = ctx.get('spy_return_1d')

        # Basic trend inference from daily SPY change if no explicit label provided
        existing_trend = str(ctx.get('trend', '')).lower()
        if not existing_trend or existing_trend == 'sideways':
            if spy_return is None:
                ctx['trend'] = 'sideways'
            elif spy_return > 0.005:
                ctx['trend'] = 'up'
            elif spy_return < -0.005:
                ctx['trend'] = 'down'
            else:
                ctx['trend'] = 'sideways'

        # Map regime labels from various helpers into consistent wording for MarketTimingSignal
        raw_regime = str(ctx.get('regime', 'neutral')).lower()
        if 'risk-on' in raw_regime or 'bull' in raw_regime:
            ctx['regime'] = 'bullish'
        elif 'caution' in raw_regime or 'bear' in raw_regime:
            ctx['regime'] = 'caution'
        else:
            ctx['regime'] = 'neutral'

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
            'stocks_5_of_5': 0,
            'stocks_4_of_5': 0,
            'stocks_3_of_5': 0,
            'stocks_2_of_5': 0,
            'analysis_type': 'PREMIUM_QUALITY_CONSENSUS',
            'error': 'No results generated'
        }
    
    def display_ultimate_strategy_results(self, results: Dict):
        """
        Display Premium Ultimate Strategy results in Streamlit UI
        
        Shows:
        - Total stocks analyzed (ALL 613)
        - Consensus picks (filtered by 2+ agreement)
        - Market analysis summary
        - Consensus recommendations by tier (5/5, 4/5, 3/5, 2/5)
        - Quality breakdowns
        - AI insights (if available)
        """
        
        if not results or not results.get('consensus_recommendations'):
            st.error("❌ No consensus recommendations found!")
            # But show if we have base analysis
            total_analyzed = results.get('total_stocks_analyzed', 0)
            if total_analyzed > 0:
                st.warning(f"⚠️ Analyzed {total_analyzed} stocks, but none met consensus criteria (2+ strategy agreement)")
            return
        
        consensus = results['consensus_recommendations']
        all_analyzed = results.get('all_analyzed_stocks', [])
        market = results.get('market_analysis', {})
        ai_insights = results.get('ai_insights', {})
        
        # CRITICAL FIX: Show BOTH total analyzed AND consensus picks clearly
        st.markdown("---")
        st.markdown("## 🎯 Premium Ultimate Strategy Results")
        
        # Key Statistics - Make it VERY clear
        st.markdown("### 📊 Analysis Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = results.get('total_stocks_analyzed', 0)
            st.metric("🔍 Total Stocks Analyzed", total)
            st.caption("Complete quality analysis")
        
        with col2:
            consensus_count = results.get('consensus_picks_count', len(consensus))
            st.metric("✅ Consensus Picks", consensus_count)
            st.caption("2+ strategies agreeing")
        
        with col3:
            tier_5 = results.get('stocks_5_of_5', 0)
            st.metric("👑 5/5 Agreement", tier_5)
            st.caption("Ultimate conviction")
        
        with col4:
            tier_4 = results.get('stocks_4_of_5', 0)
            st.metric("🏆 4/5 Agreement", tier_4)
            st.caption("Highest conviction")
        
        st.info(f"""
        **Analysis Method**: {results.get('metrics_used', '15 Quality Metrics')}
        
        **Understanding the Results:**
        - **Total Analyzed ({total})**: All stocks received comprehensive quality analysis
        - **Consensus Picks ({consensus_count})**: Stocks where 2 or more investment perspectives agree
        - **Filtering is intentional**: Only showing highest-quality opportunities with multi-strategy validation
        """)
        
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
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Analyzed", results.get('total_stocks_analyzed', 0))
        with col2:
            count_5 = results.get('stocks_5_of_5', 0)
            st.metric("5/5 Agreement", count_5, help="ULTIMATE BUY - All perspectives agree")
        with col3:
            count_4 = results.get('stocks_4_of_5', 0)
            st.metric("4/5 Agreement", count_4, help="STRONG BUY - Strong majority")
        with col4:
            count_3 = results.get('stocks_3_of_5', 0)
            st.metric("3/5 Agreement", count_3, help="BUY - Majority agreement")
        with col5:
            count_2 = results.get('stocks_2_of_5', 0)
            st.metric("2/5 Agreement", count_2, help="WEAK BUY - Split decision")
        
        # AI Market Tradability (NEW - shows if good time to trade)
        market_tradability = results.get('market_tradability')
        if market_tradability:
            st.markdown("### 🤖 AI Market Tradability Analysis")
            
            recommendation = market_tradability.get('trade_recommendation', 'N/A')
            confidence = market_tradability.get('confidence', 0)
            brief_summary = market_tradability.get('brief_summary', '')
            
            # Color-coded recommendation
            if recommendation == 'FAVORABLE':
                st.success(f"✅ **{recommendation}** (Confidence: {confidence}%)")
                st.info(brief_summary)
            elif recommendation == 'CAUTION':
                st.warning(f"⚠️ **{recommendation}** (Confidence: {confidence}%)")
                st.warning(brief_summary)
            elif recommendation == 'AVOID':
                st.error(f"🛑 **{recommendation}** (Confidence: {confidence}%)")
                st.error(brief_summary)
            else:
                st.info(f"ℹ️ **{recommendation}** (Confidence: {confidence}%)")
                st.info(brief_summary)
            
            # Show detailed reasoning in expander
            with st.expander("📋 Detailed AI Analysis"):
                reasoning = market_tradability.get('reasoning', '')
                if reasoning:
                    st.markdown("**Reasoning:**")
                    st.write(reasoning)
                
                risks = market_tradability.get('key_risks', [])
                if risks:
                    st.markdown("**Key Risks:**")
                    for risk in risks:
                        st.markdown(f"- ⚠️ {risk}")
                
                opportunities = market_tradability.get('opportunities', [])
                if opportunities:
                    st.markdown("**Opportunities:**")
                    for opp in opportunities:
                        st.markdown(f"- ✅ {opp}")
        
        # AI Top Picks (NEW - shows best opportunities combining all intelligence)
        ai_top_picks = results.get('ai_top_picks')
        if ai_top_picks and ai_top_picks.get('ai_top_picks'):
            st.markdown("### 🎯 AI TOP PICKS - Ultimate Strategy Recommendation")
            
            # Brief summary
            st.success(f"💡 **KEY INSIGHT:** {ai_top_picks.get('key_insight', 'Focus on highest conviction picks')}")
            st.info(ai_top_picks.get('brief_summary', ''))
            
            # Top picks table
            picks_list = ai_top_picks.get('ai_top_picks', [])
            
            if picks_list:
                # Create a visually appealing table
                for pick in picks_list:
                    rank = pick.get('rank', 0)
                    symbol = pick.get('symbol', 'N/A')
                    ai_score = pick.get('ai_score', 0)
                    action = pick.get('action', 'HOLD')
                    position_size = pick.get('position_size', 'Small')
                    entry_timing = pick.get('entry_timing', 'Wait')
                    why = pick.get('why_selected', 'N/A')
                    
                    # Action color
                    if action == 'STRONG BUY' or action == 'ULTIMATE BUY':
                        action_color = 'success'
                        emoji = '🚀'
                    elif action == 'BUY':
                        action_color = 'info'
                        emoji = '✅'
                    else:
                        action_color = 'warning'
                        emoji = '⚠️'
                    
                    # Display each pick
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 3, 2, 3])
                        
                        with col1:
                            st.markdown(f"### {emoji} #{rank}")
                        
                        with col2:
                            st.markdown(f"**{symbol}**")
                            st.caption(f"AI Score: {ai_score:.1f}/100")
                        
                        with col3:
                            if action_color == 'success':
                                st.success(action)
                            elif action_color == 'info':
                                st.info(action)
                            else:
                                st.warning(action)
                            st.caption(f"{position_size} position")
                        
                        # Find matching pick to get price
                        matching_pick = next((p for p in consensus if p['symbol'] == symbol), None)
                        current_price = matching_pick.get('current_price', 0) if matching_pick else 0
                        
                        with col4:
                            st.markdown(f"*{why}*")
                            st.caption(f"Entry: {entry_timing} | Price: ${current_price:.2f}")
                        
                        st.markdown("---")
            
            st.caption(f"📊 AI analyzed {ai_top_picks.get('total_analyzed', 0)} picks and recommended {ai_top_picks.get('total_recommended', 0)} top opportunities")
        
        # AI Catalyst Analysis (NEW - shows news, earnings, catalysts for top picks)
        catalyst_data = results.get('catalyst_analysis')
        if catalyst_data and catalyst_data.get('stocks_analyzed'):
            st.markdown("### 🔍 AI Catalyst & News Analysis")
            
            st.info(f"""
            **Deep Analysis**: AI analyzed {catalyst_data.get('stocks_analyzed', 0)} top-tier stocks for:
            - Recent news & earnings
            - Growth catalysts
            - Specific risks
            - Earnings outlook
            - Market sentiment
            """)
            
            # Get stocks with catalyst data (sorted by catalyst score)
            catalyst_stocks = [
                p for p in consensus 
                if p.get('catalyst_score') is not None
            ]
            catalyst_stocks.sort(key=lambda x: x.get('catalyst_score', 0), reverse=True)
            
            # Display top stocks with catalyst analysis
            for stock in catalyst_stocks[:10]:  # Show top 10 with catalyst data
                symbol = stock.get('symbol', 'N/A')
                catalyst_score = stock.get('catalyst_score', 0)
                earnings_outlook = stock.get('earnings_outlook', 'UNKNOWN')
                catalyst_summary = stock.get('catalyst_summary', '')
                growth_catalysts = stock.get('growth_catalysts', [])
                catalyst_risks = stock.get('catalyst_risks', [])
                recent_news = stock.get('recent_news', [])
                
                # Catalyst score color
                if catalyst_score >= 85:
                    score_color = 'success'
                    emoji = '🚀'
                elif catalyst_score >= 70:
                    score_color = 'info'
                    emoji = '📈'
                elif catalyst_score >= 50:
                    score_color = 'warning'
                    emoji = '⚠️'
                else:
                    score_color = 'error'
                    emoji = '🔴'
                
                # Earnings outlook emoji
                if earnings_outlook == 'BEAT':
                    earnings_emoji = '✅'
                elif earnings_outlook == 'MEET':
                    earnings_emoji = '➡️'
                elif earnings_outlook == 'MISS':
                    earnings_emoji = '❌'
                else:
                    earnings_emoji = '❓'
                
                with st.expander(f"{emoji} **{symbol}** - Catalyst Score: {catalyst_score:.0f}/100 | Earnings: {earnings_emoji} {earnings_outlook}"):
                    # Brief summary
                    if catalyst_summary:
                        st.markdown(f"**📝 Summary:** {catalyst_summary}")
                    
                    # Growth catalysts
                    if growth_catalysts:
                        st.markdown("**🚀 Growth Catalysts:**")
                        for catalyst in growth_catalysts[:3]:  # Top 3
                            st.markdown(f"- ✨ {catalyst}")
                    
                    # Risks
                    if catalyst_risks:
                        st.markdown("**⚠️ Key Risks:**")
                        for risk in catalyst_risks[:3]:  # Top 3
                            st.markdown(f"- 🛑 {risk}")
                    
                    # Recent news
                    if recent_news:
                        st.markdown("**📰 Recent News:**")
                        for news_item in recent_news[:3]:  # Top 3
                            if isinstance(news_item, dict):
                                headline = news_item.get('headline', '')
                                impact = news_item.get('impact', 'neutral')
                                importance = news_item.get('importance', 'medium')
                                
                                # Impact emoji
                                if impact == 'positive':
                                    impact_emoji = '📈'
                                elif impact == 'negative':
                                    impact_emoji = '📉'
                                else:
                                    impact_emoji = '➡️'
                                
                                st.markdown(f"- {impact_emoji} {headline}")
                            else:
                                st.markdown(f"- 📰 {news_item}")
            
            st.caption(f"💡 Catalyst analysis uses AI to identify specific growth drivers and risks for each stock")
        
        # AI Insights (legacy - if available)
        if ai_insights.get('available'):
            st.markdown("### 🤖 AI Quick Signals")

            def _clip(message: str, limit: int = 140) -> str:
                text = (message or '').strip()
                return text if len(text) <= limit else text[:limit - 1].rstrip() + '…'

            quick_signals = []
            if ai_insights.get('market_overview'):
                quick_signals.append(f"Market: {_clip(ai_insights['market_overview'])}")
            if ai_insights.get('top_picks_analysis'):
                quick_signals.append(f"Top Picks: {_clip(ai_insights['top_picks_analysis'])}")
            if ai_insights.get('risk_assessment'):
                quick_signals.append(f"Risk: {_clip(ai_insights['risk_assessment'])}")
            if ai_insights.get('entry_timing'):
                quick_signals.append(f"Timing: {_clip(ai_insights['entry_timing'])}")

            if quick_signals:
                st.info(" • ".join(quick_signals[:4]))
        
        # 5/5 Agreement (ULTIMATE BUY)
        tier_5 = [p for p in consensus if p['strategies_agreeing'] == 5]
        if tier_5:
            st.markdown("### 🏆 5/5 Agreement - ULTIMATE BUY (Highest Conviction)")
            st.markdown(f"*All 5 investment perspectives agree on these {len(tier_5)} stocks*")
            
            for pick in tier_5[:10]:  # Show top 10
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
                        
                        # AI Validation (NEW)
                        ai_val = pick.get('ai_validation')
                        if ai_val:
                            st.markdown("---")
                            st.markdown("**🤖 AI Validation:**")
                            
                            # Color-coded validation status
                            if ai_val == 'CONFIRMED':
                                st.success(f"✅ {ai_val}")
                            elif ai_val == 'REJECTED':
                                st.error(f"❌ {ai_val}")
                            else:
                                st.info(f"ℹ️ {ai_val}")
                            
                            # Risk and profit potential
                            ai_risk = pick.get('ai_risk_level', 'N/A')
                            ai_profit = pick.get('ai_profit_potential', 'N/A')
                            ai_sentiment = pick.get('ai_news_sentiment', 'N/A')
                            
                            st.markdown(f"- Risk: **{ai_risk}**")
                            st.markdown(f"- Profit Potential: **{ai_profit}**")
                            st.markdown(f"- News Sentiment: **{ai_sentiment}**")
                            
                            # AI verdict
                            ai_verdict = pick.get('ai_verdict', '')
                            if ai_verdict and ai_verdict != 'No AI validation':
                                st.markdown(f"- *{ai_verdict}*")

        # 4/5 Agreement (STRONG BUY)
        tier_4 = [p for p in consensus if p['strategies_agreeing'] == 4]
        if tier_4:
            st.markdown("### 🌟 4/5 Agreement - STRONG BUY (High Conviction)")
            st.markdown(f"*4 out of 5 perspectives agree on these {len(tier_4)} stocks*")
            
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
                        
                        ai_val = pick.get('ai_validation')
                        if ai_val:
                            st.markdown("---")
                            st.markdown("**🤖 AI Validation:**")
                            if ai_val == 'CONFIRMED':
                                st.success(f"✅ {ai_val}")
                            elif ai_val == 'REJECTED':
                                st.error(f"❌ {ai_val}")
                            else:
                                st.info(f"ℹ️ {ai_val}")
                            
                            ai_risk = pick.get('ai_risk_level', 'N/A')
                            ai_profit = pick.get('ai_profit_potential', 'N/A')
                            ai_sentiment = pick.get('ai_news_sentiment', 'N/A')
                            st.markdown(f"- Risk: **{ai_risk}**")
                            st.markdown(f"- Profit Potential: **{ai_profit}**")
                            st.markdown(f"- News Sentiment: **{ai_sentiment}**")
                            
                            ai_verdict = pick.get('ai_verdict', '')
                            if ai_verdict and ai_verdict != 'No AI validation':
                                st.markdown(f"- *{ai_verdict}*")

        # 3/5 Agreement (BUY)
        tier_3 = [p for p in consensus if p['strategies_agreeing'] == 3]
        if tier_3:
            st.markdown("### ⭐ 3/5 Agreement - BUY (Strong Majority)")
            st.markdown(f"*3 out of 5 perspectives agree on these {len(tier_3)} stocks*")
            
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
        
        # 2/5 Agreement (WEAK BUY)
        tier_2 = [p for p in consensus if p['strategies_agreeing'] == 2]
        if tier_2:
            with st.expander(f"⚡ 2/5 Agreement - WEAK BUY ({len(tier_2)} stocks)"):
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
