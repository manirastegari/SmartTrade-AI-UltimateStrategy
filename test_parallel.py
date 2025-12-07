
import sys
import os
import time
import logging

# Add project root to path
sys.path.append(os.getcwd())

# Suppress logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

print("Starting parallel processing test...")

try:
    from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
    
    # Mock data fetcher to avoid actual network calls and speed up test
    class MockFetcher:
        def get_comprehensive_stock_data(self, symbol):
            time.sleep(0.1) # Simulate network delay
            return {
                'data': None, # Will trigger fallback or failure, but that's fine for testing threading
                'info': {'marketCap': 1000000000}
            }
            
    # Create a mock analyzer that has a data_fetcher attribute
    class MockAnalyzer:
        def __init__(self):
            self.data_fetcher = MockFetcher()
            
    mock_analyzer_instance = MockAnalyzer()
    analyzer = FixedUltimateStrategyAnalyzer(mock_analyzer_instance)
    
    # We'll just run it with a few symbols. If it fails to fetch, it handles it.
    # We just want to see if the threading logic crashes.
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    print(f"Running batch analysis on {len(symbols)} symbols...")
    start_time = time.time()
    analyzer._run_quality_analysis(symbols)
    end_time = time.time()
    print(f"✅ Batch analysis completed in {end_time - start_time:.2f}s")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
