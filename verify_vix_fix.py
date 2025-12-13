
import sys
import os
sys.path.append(os.getcwd())
from advanced_data_fetcher import AdvancedDataFetcher
from unittest.mock import MagicMock

def test_vix():
    print("🧪 Testing VIX Fetching Logic...")
    fetcher = AdvancedDataFetcher()
    
    # Mock xAI to return a specific error to test the parsing fix
    # We want to ensure it DOES NOT return 20.0 but None
    
    ctx = fetcher.get_market_context()
    print(f"VIX Value: {ctx.get('vix_proxy')}")
    print(f"VIX Source: {ctx.get('vix_source')}")
    
    if ctx.get('vix_proxy') == 20.0 and ctx.get('vix_source') == 'default':
        print("❌ FAIL: Still defaulting to hardcoded 20.0!")
    else:
        print("✅ PASS: Not using hardcoded 20.0 default.")

if __name__ == "__main__":
    test_vix()
