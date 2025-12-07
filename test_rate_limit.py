
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.append(os.getcwd())

from advanced_data_fetcher import AdvancedDataFetcher

def test_thread_safety():
    print("--- Testing Thread-Safe Rate Limiting ---")
    
    fetcher = AdvancedDataFetcher()
    
    # Mock the actual fetch methods to return immediately so we only measure the rate limit delay
    def mock_fetch(*args, **kwargs):
        return None
        
    # We need to monkeypatch the internal methods called by _fetch_yfinance_with_fallback
    # But _fetch_yfinance_with_fallback calls self.cache.get... first.
    # We can just set fetcher.cache to None to skip cache.
    fetcher.cache = None
    fetcher.cost_effective_data = None # Skip cost effective to hit the rate limited part
    
    # Monkeypatch the fallback methods to avoid network calls
    fetcher._try_yahoo_direct_api = mock_fetch
    fetcher._try_ticker_history = mock_fetch
    fetcher._try_yf_download = mock_fetch
    fetcher._try_different_periods = mock_fetch
    fetcher._fetch_stooq_history = mock_fetch
    fetcher._try_alpha_vantage_free = mock_fetch
    
    # We want to make 5 calls in parallel.
    # Delay is 0.8s.
    # Total time should be at least 4 * 0.8 = 3.2s (first one is immediate).
    
    start_time = time.time()
    
    def worker(i):
        # print(f"Worker {i} starting")
        fetcher._fetch_yfinance_with_fallback("DUMMY")
        # print(f"Worker {i} finished")
        return time.time()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, i) for i in range(5)]
        results = [f.result() for f in futures]
        
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Made 5 parallel calls with 0.8s delay.")
    print(f"Total duration: {duration:.4f}s")
    
    # Expected: ~3.2s minimum. Allow some buffer.
    if duration >= 3.0:
        print("✅ PASS: Rate limiting is working correctly (duration >= 3.0s)")
    else:
        print("❌ FAIL: Rate limiting failed (duration < 3.0s) - Lock might be missing or broken")

if __name__ == "__main__":
    test_thread_safety()
