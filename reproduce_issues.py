
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
            print(f"Calling get_better_fundamentals for {symbol}...")
            fund = fetcher.get_better_fundamentals(symbol)
            print(f"Fundamentals retrieved.")
            
            result = analyzer.analyze_stock(symbol)
            if result.get('success'):
                print(f"✅ Success: Quality Score {result.get('quality_score')}")
            else:
                print(f"❌ Failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Exception: {e}")

test_vix_fetching()
test_fundamental_data()

print("\n--- Testing Parallel Batch Processing ---")
try:
    from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
    from advanced_data_fetcher import AdvancedDataFetcher
    fetcher = AdvancedDataFetcher()
    analyzer = FixedUltimateStrategyAnalyzer(fetcher)
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]
    print(f"Running batch analysis on {len(symbols)} symbols...")
    start_time = time.time()
    analyzer._run_quality_analysis(symbols)
    end_time = time.time()
    print(f"✅ Batch analysis completed in {end_time - start_time:.2f}s")
except Exception as e:
    print(f"⚠️ Batch processing test skipped/failed: {e}")
