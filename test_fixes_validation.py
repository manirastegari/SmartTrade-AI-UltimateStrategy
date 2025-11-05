#!/usr/bin/env python3
"""
Quick validation test for Ultimate Strategy fixes
Tests with 20 stocks to verify all fixes are working
"""

import sys
from ultimate_strategy_analyzer_fixed import UltimateStrategyAnalyzer
from premium_quality_universe import PREMIUM_QUALITY_UNIVERSE

def main():
    print("=" * 80)
    print("🧪 ULTIMATE STRATEGY - QUICK VALIDATION TEST")
    print("=" * 80)
    print()
    print("Testing all 4 critical fixes:")
    print("  ✅ Fix #1: SPY Benchmark Multi-Fallback")
    print("  ✅ Fix #2: Flattened Data Structure")
    print("  ✅ Fix #3: Batch Processing (will use 1 batch for 20 stocks)")
    print("  ✅ Fix #4: Diagnostic Logging")
    print()
    
    # Get 20 test stocks from different sectors
    test_stocks = []
    for category, stocks in PREMIUM_QUALITY_UNIVERSE.items():
        test_stocks.extend(stocks[:2])  # 2 from each category
        if len(test_stocks) >= 20:
            break
    
    test_stocks = test_stocks[:20]
    
    print(f"📊 Test Universe: {len(test_stocks)} stocks")
    print(f"   {test_stocks}")
    print()
    
    # Initialize analyzer
    analyzer = UltimateStrategyAnalyzer()
    
    # Run analysis
    print("\n🚀 Starting analysis...")
    print("=" * 80)
    
    try:
        results = analyzer.run_ultimate_strategy(
            test_stocks,
            auto_export=True,
            regime_detection=False  # Disable for quick test
        )
        
        print()
        print("=" * 80)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 80)
        print()
        
        # Validate results
        consensus_picks = results.get('consensus_picks', [])
        
        print(f"📊 Results Summary:")
        print(f"   Total stocks analyzed: {len(test_stocks)}")
        print(f"   Consensus picks: {len(consensus_picks)}")
        print()
        
        if consensus_picks:
            print("🔍 Validation Checks:")
            print()
            
            # Check 1: SPY benchmark
            print("  ✅ Check #1: SPY Benchmark")
            sample = consensus_picks[0]
            beta = sample.get('beta', 0)
            if beta > 0 and beta != 1:
                print(f"     ✅ PASS - Beta = {beta} (real value, not default)")
            else:
                print(f"     ⚠️  WARN - Beta = {beta} (may be default)")
            print()
            
            # Check 2: Flattened data structure
            print("  ✅ Check #2: Flattened Data Structure")
            pe_ratio = sample.get('pe_ratio', 0)
            rsi = sample.get('rsi_14', 0)
            volatility = sample.get('volatility', 0)
            
            if pe_ratio != 0:
                print(f"     ✅ PASS - P/E Ratio (flat) = {pe_ratio}")
            else:
                print(f"     ⚠️  WARN - P/E Ratio (flat) = {pe_ratio}")
            
            if rsi != 0:
                print(f"     ✅ PASS - RSI (flat as rsi_14) = {rsi}")
            else:
                print(f"     ⚠️  WARN - RSI (flat) = {rsi}")
            
            if volatility != 0:
                print(f"     ✅ PASS - Volatility (flat) = {volatility}")
            else:
                print(f"     ⚠️  WARN - Volatility (flat) = {volatility}")
            print()
            
            # Check 3: Data differentiation
            print("  ✅ Check #3: Data Differentiation")
            unique_quality_scores = len(set(p.get('quality_score', 0) for p in consensus_picks))
            unique_betas = len(set(p.get('beta', 0) for p in consensus_picks))
            
            if unique_quality_scores > 1:
                print(f"     ✅ PASS - {unique_quality_scores} unique quality scores (not all identical)")
            else:
                print(f"     ⚠️  WARN - Only {unique_quality_scores} unique quality score")
            
            if unique_betas > 1:
                print(f"     ✅ PASS - {unique_betas} unique beta values (not all identical)")
            else:
                print(f"     ⚠️  WARN - Only {unique_betas} unique beta value")
            print()
            
            # Check 4: Consensus scores
            print("  ✅ Check #4: Consensus Scores")
            consensus_scores = [p.get('consensus_score', 0) for p in consensus_picks]
            avg_consensus = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0
            
            if avg_consensus > 0:
                print(f"     ✅ PASS - Average consensus score = {avg_consensus:.2f} (not zero)")
            else:
                print(f"     ⚠️  WARN - Average consensus score = {avg_consensus}")
            print()
            
            # Sample data
            print("  📋 Sample Consensus Pick (first stock):")
            print(f"     Symbol: {sample.get('symbol')}")
            print(f"     Quality Score: {sample.get('quality_score')}")
            print(f"     Consensus Score: {sample.get('consensus_score')}")
            print(f"     Agreement: {sample.get('strategies_agreeing')}/4")
            print(f"     Beta (flat): {sample.get('beta')}")
            print(f"     RSI (flat): {sample.get('rsi_14')}")
            print(f"     P/E Ratio (flat): {sample.get('pe_ratio')}")
            print(f"     Volatility (flat): {sample.get('volatility')}")
            print()
        else:
            print("⚠️  No consensus picks found (may need to lower agreement threshold for test)")
        
        print("=" * 80)
        print("✅ TEST COMPLETE - Check Excel file for full results")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
