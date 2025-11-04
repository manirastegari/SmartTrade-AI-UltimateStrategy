#!/usr/bin/env python3
"""
Test Premium Stock Analyzer - Validate it returns proper results
"""

from premium_stock_analyzer import PremiumStockAnalyzer
from advanced_analyzer import AdvancedTradingAnalyzer

# Initialize properly like the app does
print("\n🔧 Initializing analyzer...")
analyzer = AdvancedTradingAnalyzer(enable_training=False, data_mode="light")

# Initialize premium analyzer with the data fetcher
print("🔧 Initializing premium analyzer...")
premium_analyzer = PremiumStockAnalyzer(data_fetcher=analyzer.data_fetcher)

# Test with a few known good stocks
test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'KO']

print("\n" + "="*80)
print("🧪 TESTING PREMIUM STOCK ANALYZER")
print("="*80)

for symbol in test_symbols:
    print(f"\n📊 Testing {symbol}...")
    result = premium_analyzer.analyze_stock(symbol)
    
    if result:
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Quality Score: {result.get('quality_score', 0)}")
            print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
            print(f"   Fundamentals Score: {result.get('fundamentals', {}).get('score', 0)}")
            print(f"   Momentum Score: {result.get('momentum', {}).get('score', 0)}")
            print(f"   Risk Score: {result.get('risk', {}).get('score', 0)}")
            print(f"   Sentiment Score: {result.get('sentiment', {}).get('score', 0)}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
    else:
        print(f"   ❌ Result is None!")

print("\n" + "="*80)
print("✅ Test complete")
print("="*80)
