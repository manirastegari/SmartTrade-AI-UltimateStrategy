#!/usr/bin/env python3
"""Test the new multi-source VIX fetching."""

import sys
import os
sys.path.insert(0, os.getcwd())

# Ensure .env is loaded
try:
    import settings
except:
    pass

from advanced_data_fetcher import AdvancedDataFetcher

def test_vix_sources():
    print("=" * 60)
    print("🧪 Testing Multi-Source VIX Fetching")
    print("=" * 60)
    
    # Check API keys are loaded
    polygon_key = os.environ.get('POLYGON_API_KEY')
    twelve_data_key = os.environ.get('TWELVE_DATA_API_KEY')
    finnhub_key = os.environ.get('FINNHUB_API_KEY')
    av_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    
    print(f"\n📋 API Keys Status:")
    print(f"   POLYGON_API_KEY: {'✅ Set' if polygon_key else '❌ Missing'}")
    print(f"   TWELVE_DATA_API_KEY: {'✅ Set' if twelve_data_key else '❌ Missing'}")
    print(f"   FINNHUB_API_KEY: {'✅ Set' if finnhub_key else '❌ Missing'}")
    print(f"   ALPHA_VANTAGE_API_KEY: {'✅ Set' if av_key else '❌ Missing'}")
    
    print("\n🔄 Fetching VIX from market context...")
    fetcher = AdvancedDataFetcher(data_mode="light")
    ctx = fetcher.get_market_context(force_refresh=True)
    
    vix = ctx.get('vix_proxy')
    vix_source = ctx.get('vix_source')
    
    print(f"\n📊 Results:")
    print(f"   VIX Value: {vix}")
    print(f"   VIX Source: {vix_source}")
    
    if vix is None:
        print("\n❌ FAIL: VIX is None - all sources failed")
    elif vix == 20.0 and vix_source == "default":
        print("\n❌ FAIL: VIX is hardcoded 20.0 default")
    else:
        print(f"\n✅ PASS: Got real VIX data ({vix:.2f}) from {vix_source}")

if __name__ == "__main__":
    test_vix_sources()
