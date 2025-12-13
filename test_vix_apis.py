#!/usr/bin/env python3
"""Test individual VIX API sources."""

import os
import sys
import requests

# Load .env via settings
sys.path.insert(0, os.getcwd())
try:
    import settings
except:
    pass

def test_polygon():
    """Test Polygon.io VIX"""
    print("\n--- Polygon.io VIX ---")
    api_key = os.environ.get('POLYGON_API_KEY')
    if not api_key:
        print("❌ No POLYGON_API_KEY")
        return None
    
    # Try I:VIX (index) and also VIX (simple)
    endpoints = [
        f"https://api.polygon.io/v2/aggs/ticker/I:VIX/prev?adjusted=true&apiKey={api_key}",
        f"https://api.polygon.io/v1/last/crypto/X:VIXUSD?apiKey={api_key}",
    ]
    for url in endpoints:
        try:
            resp = requests.get(url, timeout=10)
            print(f"Status: {resp.status_code}")
            data = resp.json()
            print(f"Response: {data}")
            if data.get('results'):
                vix = data['results'][0].get('c')
                print(f"✅ VIX from Polygon: {vix}")
                return vix
        except Exception as e:
            print(f"Error: {e}")
    return None

def test_twelve_data():
    """Test Twelve Data VIX"""
    print("\n--- Twelve Data VIX ---")
    api_key = os.environ.get('TWELVE_DATA_API_KEY')
    if not api_key:
        print("❌ No TWELVE_DATA_API_KEY")
        return None
    
    # Try "VIX" and "CBOE:VIX"
    symbols = ["VIX", "CBOE:VIX", "VIXY"]
    for sym in symbols:
        try:
            url = f"https://api.twelvedata.com/time_series?symbol={sym}&interval=1day&outputsize=1&apikey={api_key}"
            resp = requests.get(url, timeout=10)
            print(f"Symbol {sym}, Status: {resp.status_code}")
            data = resp.json()
            print(f"Response: {data}")
            if data.get('values') and len(data['values']) > 0:
                vix = float(data['values'][0].get('close', 0))
                print(f"✅ VIX from Twelve Data ({sym}): {vix}")
                return vix
        except Exception as e:
            print(f"Error: {e}")
    return None

def test_finnhub():
    """Test Finnhub VIX"""
    print("\n--- Finnhub VIX ---")
    api_key = os.environ.get('FINNHUB_API_KEY')
    if not api_key:
        print("❌ No FINNHUB_API_KEY")
        return None
    
    # Finnhub uses CBOE:VIX or ^VIX
    symbols = ["VIX", "CBOE_VIX", "^VIX", "VIXY"]
    for sym in symbols:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={sym}&token={api_key}"
            resp = requests.get(url, timeout=10)
            print(f"Symbol {sym}, Status: {resp.status_code}")
            data = resp.json()
            print(f"Response: {data}")
            if data.get('c') and data['c'] > 0:
                print(f"✅ VIX from Finnhub ({sym}): {data['c']}")
                return data['c']
        except Exception as e:
            print(f"Error: {e}")
    return None

def test_alpha_vantage():
    """Test Alpha Vantage VIX (via VIXY)"""
    print("\n--- Alpha Vantage VIX ---")
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        print("❌ No ALPHA_VANTAGE_API_KEY")
        return None
    
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=VIXY&apikey={api_key}"
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Response: {data}")
        quote = data.get('Global Quote', {})
        if quote.get('05. price'):
            vixy_price = float(quote['05. price'])
            vix_approx = vixy_price * 2.0  # Rough approximation
            print(f"✅ VIXY price: ${vixy_price:.2f} → VIX ≈ {vix_approx:.2f}")
            return vix_approx
    except Exception as e:
        print(f"Error: {e}")
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Individual VIX API Sources")
    print("=" * 60)
    
    results = {}
    results['Polygon'] = test_polygon()
    results['Twelve Data'] = test_twelve_data()
    results['Finnhub'] = test_finnhub()
    results['Alpha Vantage'] = test_alpha_vantage()
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    for source, vix in results.items():
        status = f"✅ {vix:.2f}" if vix else "❌ Failed"
        print(f"   {source}: {status}")
