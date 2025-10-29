#!/usr/bin/env python3
"""
Quick test to validate Alpha+ portfolio build and Excel export wiring
without running the full Ultimate Strategy (no network calls required).
"""
from datetime import datetime, timedelta

from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer


def main():
    # Create analyzer with no underlying AdvancedTradingAnalyzer (not needed here)
    ua = FixedUltimateStrategyAnalyzer(analyzer=None)

    # Provide base_results with minimal fields used by Alpha+ logic
    ua.base_results = {
        'AAA': {
            'current_price': 50.0, 'momentum_score': 78, 'volatility_score': 35, 'upside_potential': 22,
            'risk_level': 'Low', 'sector': 'Technology', 'technical_target': 62.0
        },
        'BBB': {
            'current_price': 25.0, 'momentum_score': 65, 'volatility_score': 45, 'upside_potential': 18,
            'risk_level': 'Medium', 'sector': 'Healthcare', 'technical_target': 30.0
        },
        'CCC': {
            'current_price': 12.0, 'momentum_score': 72, 'volatility_score': 60, 'upside_potential': 28,
            'risk_level': 'Medium', 'sector': 'Industrials', 'technical_target': 15.0
        },
        'DDD': {
            'current_price': 6.0, 'momentum_score': 80, 'volatility_score': 55, 'upside_potential': 35,
            'risk_level': 'High', 'sector': 'Consumer Discretionary', 'technical_target': 8.0
        },
        'EEE': {
            'current_price': 120.0, 'momentum_score': 60, 'volatility_score': 20, 'upside_potential': 10,
            'risk_level': 'Low', 'sector': 'Technology', 'technical_target': 132.0
        },
    }

    # Fabricate consensus recommendations
    consensus = [
        {'symbol': 'AAA', 'consensus_score': 85, 'strategies_agreeing': 4, 'strong_buy_count': 3,
         'recommendation': 'STRONG BUY', 'confidence': 95, 'risk_level': 'Low', 'current_price': 50.0,
         'upside_potential': 22, 'sector': 'Technology', 'target_price': 62.0},
        {'symbol': 'BBB', 'consensus_score': 77, 'strategies_agreeing': 3, 'strong_buy_count': 2,
         'recommendation': 'STRONG BUY', 'confidence': 88, 'risk_level': 'Medium', 'current_price': 25.0,
         'upside_potential': 18, 'sector': 'Healthcare', 'target_price': 30.0},
        {'symbol': 'CCC', 'consensus_score': 72, 'strategies_agreeing': 2, 'strong_buy_count': 1,
         'recommendation': 'BUY', 'confidence': 75, 'risk_level': 'Medium', 'current_price': 12.0,
         'upside_potential': 28, 'sector': 'Industrials', 'target_price': 15.0},
        {'symbol': 'DDD', 'consensus_score': 70, 'strategies_agreeing': 2, 'strong_buy_count': 0,
         'recommendation': 'BUY', 'confidence': 70, 'risk_level': 'High', 'current_price': 6.0,
         'upside_potential': 35, 'sector': 'Consumer Discretionary', 'target_price': 8.0},
        {'symbol': 'EEE', 'consensus_score': 80, 'strategies_agreeing': 3, 'strong_buy_count': 3,
         'recommendation': 'STRONG BUY', 'confidence': 90, 'risk_level': 'Low', 'current_price': 120.0,
         'upside_potential': 10, 'sector': 'Technology', 'target_price': 132.0},
    ]

    # Build Alpha+
    alpha = ua._build_profit_optimized_portfolio(consensus)
    print("Alpha+ summary:", alpha.get('summary'))
    print("Alpha+ picks (first 3):", (alpha.get('picks') or [])[:3])

    # Prepare export results
    ua.analysis_start_time = datetime.now() - timedelta(minutes=5)
    ua.analysis_end_time = datetime.now()
    results = {
        'consensus_recommendations': consensus,
        'market_analysis': {'status': 'NEUTRAL'},
        'sector_analysis': {'top_sectors': ['Technology']},
        'strategy_results': {},
        'total_stocks_analyzed': 5,
        'requested_universe_count': 5,
        'skipped_count': 0,
        'skipped_symbols': [],
        'failures': [],
        'replacement_suggestions': [],
        'stocks_4_of_4': 1,
        'stocks_3_of_4': 2,
        'stocks_2_of_4': 2,
        'stocks_1_of_4': 0,
        'removed_by_guardrails': [],
        'alpha_plus_portfolio': alpha,
        'analysis_type': 'FIXED_OPTIMIZED_CONSENSUS'
    }

    # Export and verify
    filename = ua._auto_export_to_excel(results)
    print("Exported:", filename)

    # Try to list sheet names
    try:
        import pandas as pd
        xl = pd.ExcelFile(filename)
        print("Sheets:", xl.sheet_names)
        assert 'AlphaPlus_Portfolio' in xl.sheet_names, "AlphaPlus sheet missing"
        assert 'All_Consensus_Picks' in xl.sheet_names, "Consensus sheet missing"
        print("✅ Excel contains AlphaPlus_Portfolio and All_Consensus_Picks sheets")
    except Exception as e:
        print("⚠️ Could not verify Excel sheets:", e)


if __name__ == "__main__":
    main()
