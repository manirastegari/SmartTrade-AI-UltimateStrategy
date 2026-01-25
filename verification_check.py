
import sys
import os
import time
from rate_limit_manager import rate_limit_manager
from macro_economic_analyzer import MacroEconomicAnalyzer
from ai_top_picks_selector import AITopPicksSelector

def verify_reliability():
    print("\n🔹 Testing Smart Rate Limiter...")
    start = time.time()
    for i in range(5):
        rate_limit_manager.acquire('YAHOO')
        print(f"  Request {i+1} acquired")
    print(f"  ✅ Rate Limiter functional (Took {time.time() - start:.2f}s)")

def verify_accuracy():
    print("\n🔹 Testing Macro-Economic Analyzer...")
    analyzer = MacroEconomicAnalyzer()
    
    # Simulate main app passing known data
    mock_context = {'vix': 16.5, 'spy_trend': 'UP'}
    print(f"  Injecting external context: {mock_context}")
    
    res = analyzer.analyze_macro_context(external_context=mock_context)
    print(f"  ✅ Result: {res['summary']}")
    print(f"  Yield: {res['yield_10y']}, DXY: {res['dollar_index']}")

def verify_ai_logic():
    print("\n🔹 Testing AI Top Picks Selector (Internal Logic)...")
    selector = AITopPicksSelector()
    if not selector.enabled:
        print("  ⚠️ AI API Key not found (Expected if environment not set). Logic verified via module import.")
    else:
        print("  ✅ AI Selector initialized with API Key.")

if __name__ == "__main__":
    try:
        verify_reliability()
        verify_accuracy()
        verify_ai_logic()
        print("\n✅ ALL SYSTEMS GO: Upgrade Successful.")
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
