#!/usr/bin/env python3
"""
Quick Validation Test for Ultimate Strategy Fixes
Tests that ALL stocks are analyzed and exported, not just consensus picks
"""

import sys
from advanced_data_fetcher import AdvancedDataFetcher
from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer

# Test with 20 diverse stocks
TEST_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',  # Tech giants
    'META', 'TSLA', 'JPM', 'JNJ', 'UNH',      # Diverse sectors
    'V', 'WMT', 'PG', 'HD', 'DIS',            # Consumer/Retail
    'BAC', 'KO', 'PFE', 'CSCO', 'INTC'        # Finance/Healthcare/Tech
]

class MockAnalyzer:
    """Mock analyzer for testing"""
    def __init__(self):
        self.data_fetcher = AdvancedDataFetcher()
    
    def _get_expanded_stock_universe(self):
        return TEST_SYMBOLS

def main():
    print("=" * 80)
    print("ULTIMATE STRATEGY FIX VALIDATION TEST")
    print("=" * 80)
    print(f"\nTesting with {len(TEST_SYMBOLS)} stocks:")
    print(f"Symbols: {', '.join(TEST_SYMBOLS[:10])}...")
    print("\n" + "-" * 80)
    
    # Run analysis
    print("\n🔍 Running analysis...")
    mock = MockAnalyzer()
    ultimate = FixedUltimateStrategyAnalyzer(mock)
    
    try:
        results = ultimate.run_ultimate_strategy(auto_export=True)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Validation
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS:")
    print("=" * 80)
    
    total = results.get('total_stocks_analyzed', 0)
    consensus = results.get('consensus_picks_count', 0)
    all_data = results.get('all_analyzed_stocks', [])
    
    print(f"\n📊 Analysis Statistics:")
    print(f"   Total Stocks Analyzed: {total}")
    print(f"   Consensus Picks (2+ agreement): {consensus}")
    print(f"   All Analyzed Data Records: {len(all_data)}")
    print(f"   5/5 Agreement: {results.get('stocks_5_of_5', 0)}")
    print(f"   4/5 Agreement: {results.get('stocks_4_of_5', 0)}")
    print(f"   3/5 Agreement: {results.get('stocks_3_of_5', 0)}")
    print(f"   2/5 Agreement: {results.get('stocks_2_of_5', 0)}")
    
    # Validation checks
    print(f"\n✅ VALIDATION CHECKS:")
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: All stocks analyzed
    if total == len(TEST_SYMBOLS):
        print(f"   ✅ Check 1/5: All {len(TEST_SYMBOLS)} stocks analyzed")
        checks_passed += 1
    else:
        print(f"   ❌ Check 1/5: Expected {len(TEST_SYMBOLS)} analyzed, got {total}")
    
    # Check 2: All analyzed data exported
    if len(all_data) == len(TEST_SYMBOLS):
        print(f"   ✅ Check 2/5: All {len(TEST_SYMBOLS)} stocks in export data")
        checks_passed += 1
    else:
        print(f"   ❌ Check 2/5: Expected {len(TEST_SYMBOLS)} in export, got {len(all_data)}")
    
    # Check 3: Consensus picks are subset
    if consensus <= total and consensus >= 0:
        print(f"   ✅ Check 3/5: Consensus picks ({consensus}) is valid subset of total ({total})")
        checks_passed += 1
    else:
        print(f"   ❌ Check 3/5: Consensus picks ({consensus}) invalid vs total ({total})")
    
    # Check 4: Data structure has required fields
    if all_data and len(all_data) > 0:
        sample = all_data[0]
        required_fields = ['symbol', 'quality_score', 'pe_ratio', 'rsi_14', 'beta', 'volatility']
        has_fields = all(field in sample for field in required_fields)
        
        if has_fields:
            print(f"   ✅ Check 4/5: Data structure has all required fields")
            checks_passed += 1
        else:
            missing = [f for f in required_fields if f not in sample]
            print(f"   ❌ Check 4/5: Missing fields: {missing}")
    else:
        print(f"   ❌ Check 4/5: No data available to check")
    
    # Check 5: Data differentiation
    if all_data and len(all_data) >= 3:
        quality_scores = [s.get('quality_score', 0) for s in all_data[:3]]
        unique_scores = len(set(quality_scores))
        
        if unique_scores > 1:
            print(f"   ✅ Check 5/5: Data is differentiated (not all identical)")
            checks_passed += 1
        else:
            print(f"   ⚠️ Check 5/5: First 3 stocks have same quality score - may indicate data issue")
    else:
        print(f"   ⚠️ Check 5/5: Not enough data to check differentiation")
    
    # Sample data display
    if all_data and len(all_data) > 0:
        print(f"\n📋 SAMPLE DATA (First Stock):")
        sample = all_data[0]
        print(f"   Symbol: {sample.get('symbol')}")
        print(f"   Quality Score: {sample.get('quality_score')}")
        print(f"   Current Price: ${sample.get('current_price', 0):.2f}")
        print(f"   P/E Ratio: {sample.get('pe_ratio', 'N/A')}")
        print(f"   Revenue Growth: {sample.get('revenue_growth', 0):.1f}%")
        print(f"   RSI: {sample.get('rsi_14', 0):.1f}")
        print(f"   Beta: {sample.get('beta', 0):.2f}")
        print(f"   Volatility: {sample.get('volatility', 0):.1f}%")
        print(f"   Fundamentals Grade: {sample.get('fundamentals_grade', 'N/A')}")
        print(f"   Momentum Grade: {sample.get('momentum_grade', 'N/A')}")
        print(f"   Risk Grade: {sample.get('risk_grade', 'N/A')}")
    
    # Final verdict
    print("\n" + "=" * 80)
    print(f"FINAL RESULT: {checks_passed}/{total_checks} checks passed")
    print("=" * 80)
    
    if checks_passed == total_checks:
        print("\n✅ ALL CHECKS PASSED - FIX VERIFIED!")
        print("\nWhat to look for in Excel:")
        print("  1. Summary tab: Should show 'Total Stocks Analyzed: 20'")
        print("  2. Summary tab: Should show 'Consensus Picks: 3-8' (varies)")
        print("  3. 'All_Analyzed_Stocks' tab: Should have 20 rows")
        print("  4. Consensus tabs: Should have 3-8 rows (filtered)")
        print("  5. Each stock should have different metrics (not identical)")
        return True
    elif checks_passed >= 3:
        print("\n⚠️ PARTIAL SUCCESS - Some issues detected")
        print(f"   {checks_passed}/{total_checks} checks passed")
        print("\nPlease review the failed checks above.")
        return False
    else:
        print("\n❌ VALIDATION FAILED - Major issues detected")
        print(f"   Only {checks_passed}/{total_checks} checks passed")
        print("\nThe fix may not have been applied correctly.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
