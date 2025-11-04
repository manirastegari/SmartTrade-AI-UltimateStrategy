#!/usr/bin/env python3
"""
Test Full Ultimate Strategy - Small Universe
Test with 20 stocks to verify complete flow works
"""

from advanced_analyzer import AdvancedTradingAnalyzer
from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
from premium_quality_universe import get_premium_universe

# Get full universe and take first 20 for testing
full_universe = get_premium_universe()
test_universe = full_universe[:20]  # Test with first 20 stocks

print("\n" + "="*80)
print("🧪 TESTING FULL ULTIMATE STRATEGY - 20 STOCK SAMPLE")
print("="*80)
print(f"\n📊 Test Universe ({len(test_universe)} stocks):")
print(f"   {test_universe}")
print()

# Initialize analyzer (like the app does)
print("🔧 Initializing Advanced Trading Analyzer...")
analyzer = AdvancedTradingAnalyzer(enable_training=False, data_mode="light")
analyzer.stock_universe = test_universe  # Use test universe

print(f"✅ Loaded {len(analyzer.stock_universe)} stocks for testing")
print()

# Initialize Ultimate Strategy
print("🔧 Initializing Ultimate Strategy Analyzer...")
ultimate = FixedUltimateStrategyAnalyzer(analyzer)

print("✅ Ultimate Strategy initialized")
print()

# Run Ultimate Strategy
print("="*80)
print("🚀 RUNNING ULTIMATE STRATEGY")
print("="*80)
print()

try:
    results = ultimate.run_ultimate_strategy(
        progress_callback=None,
        auto_export=False  # Don't export during test
    )
    
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    
    if results:
        print(f"\n✅ Analysis completed successfully!")
        print(f"   Base Results: {len(ultimate.base_results)} stocks analyzed")
        print(f"   Consensus Picks: {len(ultimate.consensus_recommendations)} stocks")
        
        if ultimate.consensus_recommendations:
            print(f"\n🎯 Top Consensus Picks:")
            for i, pick in enumerate(ultimate.consensus_recommendations[:10], 1):
                symbol = pick.get('symbol', 'N/A')
                agreement = pick.get('strategies_agreeing', 0)
                score = pick.get('consensus_score', 0)
                recommendation = pick.get('recommendation', 'N/A')
                print(f"   {i}. {symbol:6s} - {agreement}/4 agreement - Score: {score:.2f} - {recommendation}")
        
        # Strategy breakdown
        print(f"\n📈 Strategy Results:")
        for strategy, picks in ultimate.strategy_results.items():
            print(f"   {strategy:30s}: {len(picks)} picks")
        
        print(f"\n✅ TEST PASSED - Ultimate Strategy is working!")
        
    else:
        print("\n❌ TEST FAILED - No results returned!")
        print(f"   Base Results: {len(ultimate.base_results)} stocks")
        print(f"   Strategy Results: {len(ultimate.strategy_results)} strategies")
        
except Exception as e:
    print(f"\n❌ TEST FAILED with exception:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ Test Complete")
print("="*80)
