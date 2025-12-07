
import sys
import os
import pandas as pd
import time

print("Starting reproduction script...")

# Add project root to path
sys.path.append(os.getcwd())

print("Importing AdvancedDataFetcher...")
try:
    from advanced_data_fetcher import AdvancedDataFetcher
    print("Imported AdvancedDataFetcher")
except Exception as e:
    print(f"Failed to import AdvancedDataFetcher: {e}")

print("Importing PremiumStockAnalyzer...")
try:
    from premium_stock_analyzer import PremiumStockAnalyzer
    print("Imported PremiumStockAnalyzer")
except Exception as e:
    print(f"Failed to import PremiumStockAnalyzer: {e}")

def test_vix_fetching():
    print("\n--- Testing VIX Fetching ---")
    fetcher = AdvancedDataFetcher()
    
    # Try to trigger the VIX logic
    # It seems to be part of get_market_context or similar, but let's see what methods are available
    # Based on the file view, it might be in a method called get_market_volatility or similar
    # I'll try to find the method name from the file content I just read or will read
    
    # For now, let's just try to fetch ^VIX directly using yfinance to see if that works
    import yfinance as yf
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        print(f"Direct yfinance ^VIX fetch:\n{hist.tail()}")
    except Exception as e:
        print(f"Direct yfinance ^VIX fetch failed: {e}")

def test_fundamental_data():
    print("\n--- Testing Fundamental Data Fetching ---")
    fetcher = AdvancedDataFetcher()
    analyzer = PremiumStockAnalyzer(data_fetcher=fetcher)
    
    # Test a few symbols that failed in the logs
    symbols = ["UNH", "JNJ", "ABBV", "MRK"]
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        try:
            result = analyzer.analyze_stock(symbol)
            if result.get('success'):
                print(f"✅ Success: Quality Score {result.get('quality_score')}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                # Check if we can see the raw info
                data = fetcher.get_comprehensive_stock_data(symbol)
                info = data.get('info', {})
                print(f"   Raw Info keys: {list(info.keys())[:5]}")
                if '_fundamental_error' in info:
                    print(f"   Fundamental Error: {info['_fundamental_error']}")
        except Exception as e:
            print(f"❌ Exception: {e}")

test_vix_fetching()
test_fundamental_data()

print("\n--- Testing Parallel Batch Processing ---")
try:
    from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
    # Mock the analyzer to avoid full initialization overhead if possible, 
    # but we need the real method. We'll just instantiate it.
    # Note: This might require API keys or other setup.
    # If it fails to init, we'll skip.
    analyzer = FixedUltimateStrategyAnalyzer()
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]
    print(f"Running batch analysis on {len(symbols)} symbols...")
    start_time = time.time()
    analyzer._run_quality_analysis(symbols)
    end_time = time.time()
    print(f"✅ Batch analysis completed in {end_time - start_time:.2f}s")
except Exception as e:
    print(f"⚠️ Batch processing test skipped/failed: {e}")
