#!/usr/bin/env python3
"""
Quick Test for Critical Fixes
Tests: AI Integration, VIX Calculation, Fundamental Data Loading
"""

import sys
import os
from datetime import datetime

print("🧪 TESTING CRITICAL FIXES")
print("=" * 70)

# Test 1: AI Catalyst Analyzer Integration
print("\n1️⃣ TESTING AI CATALYST ANALYZER...")
try:
    from ai_catalyst_analyzer import AIStockCatalystAnalyzer
    
    # Initialize analyzer
    analyzer = AIStockCatalystAnalyzer()
    print("✅ AI Catalyst Analyzer initialized")
    
    # Test with a simple stock
    test_stock = {
        'symbol': 'AAPL',
        'sector': 'Technology',
        'current_price': 175.0,
        'quality_score': 85
    }
    market_context = {
        'vix': 18.5,
        'spy_return_1d': 0.005,
        'regime': 'bullish',
        'trend': 'up'
    }
    
    print(f"   Testing catalyst analysis for {test_stock['symbol']}...")
    result = analyzer.analyze_stock_catalysts(
        stock=test_stock,
        market_context=market_context
    )
    
    if result and result.get('catalyst_score', 0) > 0:
        print(f"✅ AI Catalyst Analysis WORKING: score={result.get('catalyst_score', 0)}")
        print(f"   Outlook: {result.get('earnings_outlook', 'N/A')}")
        print(f"   Risk: {result.get('risk_assessment', 'N/A')}")
    else:
        print(f"❌ AI Catalyst Analysis FAILED: {result}")
        
except Exception as e:
    print(f"❌ AI Catalyst Analyzer test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: AI Top Picks Selector Integration
print("\n2️⃣ TESTING AI TOP PICKS SELECTOR...")
try:
    from ai_top_picks_selector import AITopPicksSelector
    
    # Initialize selector
    selector = AITopPicksSelector()
    print("✅ AI Top Picks Selector initialized")
    
    # Test with sample consensus picks
    sample_picks = [
        {
            'symbol': 'AAPL',
            'quality_score': 85,
            'momentum_score': 78,
            'risk_score': 82,
            'agreement_level': 4,
            'sector': 'Technology'
        },
        {
            'symbol': 'MSFT',
            'quality_score': 88,
            'momentum_score': 80,
            'risk_score': 85,
            'agreement_level': 4,
            'sector': 'Technology'
        }
    ]
    
    market_context = {
        'vix': 18.5,
        'spy_return_1d': 0.005,
        'regime': 'bullish',
        'trend': 'up'
    }
    
    print(f"   Testing top picks selection with {len(sample_picks)} stocks...")
    result = selector.select_top_picks(
        consensus_picks=sample_picks,
        market_context=market_context,
        max_picks=2
    )
    
    if result and result.get('ai_top_picks'):
        print(f"✅ AI Top Picks Selection WORKING: {len(result['ai_top_picks'])} picks")
        for pick in result['ai_top_picks']:
            print(f"   - {pick.get('symbol')}: {pick.get('why_selected', 'N/A')[:50]}...")
    else:
        print(f"❌ AI Top Picks Selection FAILED: {result}")
        
except Exception as e:
    print(f"❌ AI Top Picks Selector test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: VIX Calculation (no artificial cap)
print("\n3️⃣ TESTING VIX CALCULATION...")
try:
    from advanced_data_fetcher import AdvancedDataFetcher
    
    # Initialize data fetcher
    fetcher = AdvancedDataFetcher(data_mode='light')
    print("✅ Data Fetcher initialized")
    
    print("   Fetching market context (VIX, SPY)...")
    context = fetcher.get_market_context()
    
    if context:
        vix = context.get('vix_proxy', 'N/A')
        spy_ret = context.get('spy_return_1d', 'N/A')
        vix_source = context.get('vix_source', 'unknown')
        
        print(f"✅ Market context retrieved:")
        print(f"   VIX: {vix} (source: {vix_source})")
        print(f"   SPY 1D Return: {spy_ret}")
        
        # Check if VIX is realistic (not capped at 50.0)
        if isinstance(vix, (int, float)):
            if vix == 50.0:
                print(f"⚠️  VIX exactly 50.0 - might still be capped")
            elif 10 <= vix <= 80:
                print(f"✅ VIX value is realistic ({vix})")
            else:
                print(f"⚠️  VIX value unusual: {vix}")
    else:
        print(f"❌ Market context retrieval failed")
        
except Exception as e:
    print(f"❌ VIX calculation test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Fundamental Data Loading
print("\n4️⃣ TESTING FUNDAMENTAL DATA LOADING...")
try:
    from premium_stock_analyzer import PremiumStockAnalyzer
    from advanced_data_fetcher import AdvancedDataFetcher
    
    # Initialize analyzer with data fetcher
    fetcher = AdvancedDataFetcher(data_mode='light')
    analyzer = PremiumStockAnalyzer(data_mode='light', data_fetcher=fetcher)
    print("✅ Premium Analyzer initialized")
    
    test_symbol = "AAPL"
    print(f"   Analyzing {test_symbol} fundamentals...")
    
    result = analyzer.analyze_stock(test_symbol)
    
    if result and result.get('status') == 'success':
        metrics = result.get('metrics', {})
        fundamentals = metrics.get('fundamentals', {})
        
        pe_ratio = fundamentals.get('pe_ratio', 'N/A')
        revenue_growth = fundamentals.get('revenue_growth', 'N/A')
        
        print(f"✅ Fundamental data retrieved:")
        print(f"   P/E Ratio: {pe_ratio}")
        print(f"   Revenue Growth: {revenue_growth}")
        
        if pe_ratio != 'N/A' and revenue_growth != 'N/A':
            print(f"✅ Fundamental data loading WORKING")
        else:
            print(f"⚠️  Some fundamental data missing (might be rate limited)")
    else:
        print(f"❌ Fundamental analysis failed: {result.get('reason', 'Unknown')}")
        
except Exception as e:
    print(f"❌ Fundamental data test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("🏁 CRITICAL FIXES TEST COMPLETE")
print("\nSUMMARY:")
print("- AI Catalyst Analyzer: Check output above")
print("- AI Top Picks Selector: Check output above")
print("- VIX Calculation: Check output above")
print("- Fundamental Data: Check output above")
print("\nIf all tests pass, fixes are working correctly!")
