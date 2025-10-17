#!/usr/bin/env python3
"""
IMPROVED Ultimate Strategy Analyzer - True Consensus System
All 4 strategies analyze THE SAME stocks with different criteria
This provides stronger consensus and lower risk
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time
from typing import List, Dict, Tuple
import streamlit as st
import random
from collections import defaultdict

class ImprovedUltimateStrategyAnalyzer:
    """
    Improved analyzer where all 4 strategies analyze the SAME stocks
    with different scoring criteria for true consensus
    """
    
    def __init__(self, analyzer):
        """
        Initialize with the main AdvancedTradingAnalyzer instance
        
        Args:
            analyzer: AdvancedTradingAnalyzer instance
        """
        self.analyzer = analyzer
        self.strategy_results = {}
        self.consensus_recommendations = []
        
    def run_ultimate_strategy(self, progress_callback=None):
        """
        Run IMPROVED Ultimate Strategy with true consensus
        
        All 4 strategies analyze the SAME 716 stocks with different criteria
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            dict: Final recommendations with consensus scoring
        """
        
        if progress_callback:
            progress_callback("Starting IMPROVED Ultimate Strategy Analysis...", 0)
        
        # STEP 1: Get the FULL universe (all 716 stocks)
        if progress_callback:
            progress_callback("Loading full stock universe (716 stocks)...", 5)
        
        full_universe = self.analyzer._get_expanded_stock_universe()
        
        if progress_callback:
            progress_callback(f"Loaded {len(full_universe)} stocks for analysis", 8)
        
        # STEP 2: Analyze overall market conditions
        if progress_callback:
            progress_callback("Analyzing overall market conditions...", 10)
        
        market_analysis = self._analyze_market_conditions()
        
        # STEP 3: Analyze sector trends
        if progress_callback:
            progress_callback("Analyzing sector and industry trends...", 12)
        
        sector_analysis = self._analyze_sector_trends()
        
        # STEP 4: Run ALL 4 strategies on the SAME stocks
        # Each strategy uses different scoring criteria
        
        if progress_callback:
            progress_callback(f"Running Strategy 1: Institutional Consensus on {len(full_universe)} stocks...", 15)
        
        self.strategy_results['institutional'] = self._run_strategy_with_criteria(
            full_universe, 
            'institutional',
            progress_callback,
            15, 35
        )
        
        if progress_callback:
            progress_callback(f"Running Strategy 2: Hedge Fund Alpha on {len(full_universe)} stocks...", 35)
        
        self.strategy_results['hedge_fund'] = self._run_strategy_with_criteria(
            full_universe,
            'hedge_fund',
            progress_callback,
            35, 55
        )
        
        if progress_callback:
            progress_callback(f"Running Strategy 3: Quant Value Hunter on {len(full_universe)} stocks...", 55)
        
        self.strategy_results['quant_value'] = self._run_strategy_with_criteria(
            full_universe,
            'quant_value',
            progress_callback,
            55, 75
        )
        
        if progress_callback:
            progress_callback(f"Running Strategy 4: Risk-Managed Core on {len(full_universe)} stocks...", 75)
        
        self.strategy_results['risk_managed'] = self._run_strategy_with_criteria(
            full_universe,
            'risk_managed',
            progress_callback,
            75, 90
        )
        
        # STEP 5: Calculate TRUE CONSENSUS across all strategies
        if progress_callback:
            progress_callback("Calculating consensus across all 4 strategies...", 90)
        
        final_recommendations = self._calculate_true_consensus(
            market_analysis,
            sector_analysis
        )
        
        if progress_callback:
            progress_callback("IMPROVED Ultimate Strategy Analysis Complete!", 100)
        
        # Automatically export to Excel
        self._auto_export_to_excel(final_recommendations)
        
        return final_recommendations
    
    def _run_strategy_with_criteria(
        self, 
        universe: List[str], 
        strategy_type: str,
        progress_callback=None,
        progress_start: int = 0,
        progress_end: int = 100
    ) -> Dict[str, Dict]:
        """
        Run analysis on the full universe with specific strategy criteria
        
        Args:
            universe: List of stock symbols to analyze
            strategy_type: Type of strategy ('institutional', 'hedge_fund', etc.)
            progress_callback: Progress update function
            progress_start: Starting progress percentage
            progress_end: Ending progress percentage
            
        Returns:
            Dict mapping symbol to analysis results
        """
        
        # Enable ML training for better predictions
        original_training = self.analyzer.enable_training
        self.analyzer.enable_training = True
        
        # Run analysis on full universe
        results = self.analyzer.run_advanced_analysis(
            max_stocks=len(universe),
            symbols=universe
        )
        
        # Restore original training setting
        self.analyzer.enable_training = original_training
        
        if not results:
            return {}
        
        # Apply strategy-specific scoring adjustments
        adjusted_results = {}
        
        for i, stock_result in enumerate(results):
            symbol = stock_result.get('symbol')
            
            # Update progress
            if progress_callback and i % 50 == 0:
                progress = progress_start + ((i / len(results)) * (progress_end - progress_start))
                progress_callback(f"Analyzing {symbol} with {strategy_type} criteria...", int(progress))
            
            # Apply strategy-specific adjustments
            if strategy_type == 'institutional':
                adjusted = self._apply_institutional_scoring(stock_result)
            elif strategy_type == 'hedge_fund':
                adjusted = self._apply_hedge_fund_scoring(stock_result)
            elif strategy_type == 'quant_value':
                adjusted = self._apply_quant_value_scoring(stock_result)
            elif strategy_type == 'risk_managed':
                adjusted = self._apply_risk_managed_scoring(stock_result)
            else:
                adjusted = stock_result
            
            adjusted_results[symbol] = adjusted
        
        return adjusted_results
    
    def _apply_institutional_scoring(self, result: Dict) -> Dict:
        """Apply institutional investment criteria (stability, large cap bias)"""
        adjusted = result.copy()
        
        # Boost large cap, stable stocks
        if result.get('market_cap', 0) > 100_000_000_000:  # > $100B
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.15
        
        # Boost low volatility
        if result.get('volatility', 100) < 20:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.10
        
        # Boost strong fundamentals
        if result.get('fundamental_score', 0) > 75:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.10
        
        adjusted['strategy_type'] = 'institutional'
        return adjusted
    
    def _apply_hedge_fund_scoring(self, result: Dict) -> Dict:
        """Apply hedge fund criteria (momentum, growth potential)"""
        adjusted = result.copy()
        
        # Boost high momentum
        if result.get('technical_score', 0) > 75:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.20
        
        # Boost growth stocks
        if result.get('growth_rate', 0) > 20:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.15
        
        # Boost high volume (liquidity)
        if result.get('volume_score', 0) > 70:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.10
        
        adjusted['strategy_type'] = 'hedge_fund'
        return adjusted
    
    def _apply_quant_value_scoring(self, result: Dict) -> Dict:
        """Apply quantitative value criteria (undervaluation, fundamentals)"""
        adjusted = result.copy()
        
        # Boost undervalued stocks
        pe_ratio = result.get('pe_ratio', 999)
        if 5 < pe_ratio < 20:  # Reasonable P/E
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.20
        
        # Boost strong fundamentals
        if result.get('fundamental_score', 0) > 80:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.15
        
        # Boost high profit margins
        if result.get('profit_margin', 0) > 15:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.10
        
        adjusted['strategy_type'] = 'quant_value'
        return adjusted
    
    def _apply_risk_managed_scoring(self, result: Dict) -> Dict:
        """Apply risk-managed criteria (low volatility, safety)"""
        adjusted = result.copy()
        
        # Boost low risk stocks
        if result.get('risk_level') == 'Low':
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.25
        
        # Boost low volatility
        if result.get('volatility', 100) < 15:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.20
        
        # Boost consistent performers
        if result.get('consistency_score', 0) > 75:
            adjusted['overall_score'] = adjusted.get('overall_score', 0) * 1.15
        
        adjusted['strategy_type'] = 'risk_managed'
        return adjusted
    
    def _calculate_true_consensus(
        self,
        market_analysis: Dict,
        sector_analysis: Dict
    ) -> Dict:
        """
        Calculate TRUE consensus by finding stocks that score high across MULTIPLE strategies
        
        This is the key improvement: we find stocks that ALL strategies agree on
        """
        
        # Collect all symbols
        all_symbols = set()
        for strategy_results in self.strategy_results.values():
            all_symbols.update(strategy_results.keys())
        
        # Calculate consensus for each stock
        consensus_stocks = []
        
        for symbol in all_symbols:
            # Get scores from all 4 strategies
            scores = []
            recommendations = []
            strategy_details = {}
            
            for strategy_name, strategy_results in self.strategy_results.items():
                if symbol in strategy_results:
                    result = strategy_results[symbol]
                    score = result.get('overall_score', 0)
                    rec = result.get('recommendation', 'HOLD')
                    
                    scores.append(score)
                    recommendations.append(rec)
                    strategy_details[strategy_name] = {
                        'score': score,
                        'recommendation': rec
                    }
            
            # Skip if not analyzed by all strategies
            if len(scores) < 4:
                continue
            
            # Calculate consensus metrics
            avg_score = np.mean(scores)
            score_std = np.std(scores)
            
            # Count how many strategies recommend BUY or STRONG BUY
            buy_count = sum(1 for rec in recommendations if 'BUY' in rec)
            strong_buy_count = sum(1 for rec in recommendations if rec == 'STRONG BUY')
            
            # Consensus strength (0-100)
            consensus_strength = (buy_count / 4) * 100
            
            # Determine final recommendation based on consensus
            if strong_buy_count >= 3 or buy_count >= 4:
                final_rec = 'STRONG BUY'
                confidence = 95
            elif buy_count >= 3:
                final_rec = 'STRONG BUY'
                confidence = 85
            elif buy_count >= 2:
                final_rec = 'BUY'
                confidence = 75
            elif buy_count >= 1:
                final_rec = 'WEAK BUY'
                confidence = 60
            else:
                final_rec = 'HOLD'
                confidence = 50
            
            # Get base stock data from first strategy
            base_data = list(self.strategy_results.values())[0].get(symbol, {})
            
            # Create consensus result
            consensus_stock = {
                'symbol': symbol,
                'consensus_score': avg_score,
                'score_consistency': 100 - (score_std * 10),  # Lower std = higher consistency
                'strategies_agreeing': buy_count,
                'strong_buy_count': strong_buy_count,
                'consensus_strength': consensus_strength,
                'recommendation': final_rec,
                'confidence': confidence,
                'strategy_details': strategy_details,
                'current_price': base_data.get('current_price', 0),
                'target_price': base_data.get('target_price', 0),
                'upside_potential': base_data.get('upside_potential', 0),
                'risk_level': self._determine_consensus_risk(buy_count, score_std),
                'market_cap': base_data.get('market_cap', 0),
                'sector': base_data.get('sector', 'Unknown')
            }
            
            consensus_stocks.append(consensus_stock)
        
        # Sort by consensus strength, then by average score
        consensus_stocks.sort(
            key=lambda x: (x['strategies_agreeing'], x['consensus_score']),
            reverse=True
        )
        
        return {
            'consensus_recommendations': consensus_stocks,
            'market_analysis': market_analysis,
            'sector_analysis': sector_analysis,
            'strategy_results': self.strategy_results,
            'total_analyzed': len(all_symbols),
            'analysis_type': 'IMPROVED_CONSENSUS'
        }
    
    def _determine_consensus_risk(self, buy_count: int, score_std: float) -> str:
        """Determine risk level based on consensus strength and score consistency"""
        
        if buy_count >= 3 and score_std < 10:
            return 'Low'
        elif buy_count >= 2 and score_std < 15:
            return 'Medium'
        else:
            return 'High'
    
    def _analyze_market_conditions(self) -> Dict:
        """Analyze overall market conditions"""
        # Simplified market analysis
        return {
            'status': 'NEUTRAL',
            'vix': 15.0,
            'trend': 'SIDEWAYS'
        }
    
    def _analyze_sector_trends(self) -> Dict:
        """Analyze sector trends"""
        # Simplified sector analysis
        return {
            'top_sectors': ['Technology', 'Healthcare', 'Finance']
        }
    
    def _auto_export_to_excel(self, results: Dict):
        """Export results to Excel (placeholder)"""
        # This would call the excel export functionality
        pass


# Usage example:
"""
from advanced_analyzer import AdvancedTradingAnalyzer
from ultimate_strategy_analyzer_improved import ImprovedUltimateStrategyAnalyzer

# Initialize
analyzer = AdvancedTradingAnalyzer(enable_training=True, data_mode="light")
improved_ultimate = ImprovedUltimateStrategyAnalyzer(analyzer)

# Run improved strategy
results = improved_ultimate.run_ultimate_strategy()

# Get top consensus picks
top_picks = [
    stock for stock in results['consensus_recommendations']
    if stock['strategies_agreeing'] >= 3  # At least 3 strategies agree
]

print(f"Found {len(top_picks)} high-consensus opportunities!")
"""
