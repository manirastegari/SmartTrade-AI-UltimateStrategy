"""
Test that method fix resolves the get_price_data error.
"""

from advanced_data_fetcher import AdvancedDataFetcher
from premium_stock_analyzer import PremiumStockAnalyzer
from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer

def test_data_fetcher_methods():
    """Test that data fetcher has correct methods."""
    print("=" * 60)
    print("Testing AdvancedDataFetcher Methods")
    print("=" * 60)
    
    fetcher = AdvancedDataFetcher()
    
    # Check for correct method
    assert hasattr(fetcher, 'get_comprehensive_stock_data'), "❌ Missing get_comprehensive_stock_data method"
    print("✅ get_comprehensive_stock_data method exists")
    
    # Check that wrong methods don't exist
    assert not hasattr(fetcher, 'get_price_data'), "❌ Should not have get_price_data method"
    print("✅ Confirmed get_price_data not present (as expected)")
    
    assert not hasattr(fetcher, 'get_fundamental_data'), "❌ Should not have get_fundamental_data method"
    print("✅ Confirmed get_fundamental_data not present (as expected)")
    
    print("\n✅ Data fetcher methods validated!")
    return True


def test_premium_analyzer_integration():
    """Test that premium analyzer works with real data."""
    print("\n" + "=" * 60)
    print("Testing Premium Analyzer with Real Data")
    print("=" * 60)
    
    fetcher = AdvancedDataFetcher()
    analyzer = PremiumStockAnalyzer(fetcher)
    
    # Test with AAPL
    print("\n📊 Testing AAPL...")
    result = analyzer.analyze_stock('AAPL')
    
    if result:
        print(f"✅ AAPL analysis successful!")
        print(f"   Quality Score: {result.get('quality_score', 0):.2f}/100")
        print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        print(f"   Metrics calculated: {len(result.get('fundamentals', {}))} fundamental metrics")
        
        # Verify all major components exist
        if ('fundamentals' in result and 'momentum' in result and 
            'risk' in result and 'sentiment' in result):
            print("   ✅ All 4 metric categories present")
            return True
        else:
            print("   ⚠️ Some metric categories missing")
            return False
    else:
        print("❌ AAPL analysis failed")
        return False


def test_ultimate_strategy_small_universe():
    """Test Ultimate Strategy with 5 stocks."""
    print("\n" + "=" * 60)
    print("Testing Ultimate Strategy (5-Stock Sample)")
    print("=" * 60)
    
    # Small test universe
    test_symbols = ['AAPL', 'MSFT', 'JNJ', 'JPM', 'WMT']
    
    fetcher = AdvancedDataFetcher()
    strategy = FixedUltimateStrategyAnalyzer(fetcher)
    
    # Override universe method to return our test symbols
    original_method = strategy.analyzer.data_fetcher
    
    # Create a mock analyzer with _get_expanded_stock_universe
    class MockAnalyzer:
        def __init__(self, data_fetcher):
            self.data_fetcher = data_fetcher
        
        def _get_expanded_stock_universe(self):
            return test_symbols
    
    strategy.analyzer = MockAnalyzer(fetcher)
    
    print(f"\n📊 Analyzing {len(test_symbols)} stocks...")
    
    def progress(msg, pct):
        """Simple progress callback"""
        if pct % 20 == 0:
            print(f"   [{pct}%] {msg}")
    
    results = strategy.run_ultimate_strategy(progress_callback=progress, auto_export=False)
    
    if results:
        quality_df = results.get('quality_analysis')
        consensus = results.get('consensus_recommendations', {})
        
        print(f"\n✅ Analysis Complete!")
        print(f"   Quality stocks analyzed: {len(quality_df) if quality_df is not None else 0}")
        print(f"   Consensus picks (4/4): {len(consensus.get('unanimous', []))}")
        print(f"   Consensus picks (3/4): {len(consensus.get('strong', []))}")
        print(f"   Consensus picks (2/4): {len(consensus.get('moderate', []))}")
        
        if quality_df is not None and len(quality_df) > 0:
            print("\n📈 Top Quality Stock:")
            top = quality_df.iloc[0]
            print(f"   {top['Symbol']}: {top.get('Quality_Score', top.get('quality_score', 0)):.2f}/100")
            print(f"   Recommendation: {top.get('Recommendation', top.get('recommendation', 'N/A'))}")
            return True
        else:
            print("\n⚠️ No quality results!")
            return False
    else:
        print("\n❌ Analysis failed - no results")
        return False


if __name__ == "__main__":
    print("\n🔧 METHOD FIX VALIDATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Check methods
        test1 = test_data_fetcher_methods()
        
        # Test 2: Premium analyzer
        test2 = test_premium_analyzer_integration()
        
        # Test 3: Full strategy
        test3 = test_ultimate_strategy_small_universe()
        
        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Method validation: {'PASS' if test1 else 'FAIL'}")
        print(f"{'✅' if test2 else '❌'} Premium analyzer: {'PASS' if test2 else 'FAIL'}")
        print(f"{'✅' if test3 else '❌'} Ultimate strategy: {'PASS' if test3 else 'FAIL'}")
        
        if test1 and test2 and test3:
            print("\n🎉 ALL TESTS PASSED - Method fix successful!")
            print("\n✅ Ready to run: streamlit run professional_trading_app.py")
        else:
            print("\n❌ Some tests failed - needs investigation")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
