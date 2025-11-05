#!/usr/bin/env python3
"""Diagnose yfinance.info data availability"""

import yfinance as yf
import json

symbol = 'AAPL'
print(f"\n{'='*60}")
print(f"Diagnosing yfinance.info for {symbol}")
print(f"{'='*60}\n")

ticker = yf.Ticker(symbol)

try:
    info = ticker.info
    print(f"✅ ticker.info retrieved successfully")
    print(f"   Type: {type(info)}")
    print(f"   Keys count: {len(info) if isinstance(info, dict) else 'N/A'}")
    
    if isinstance(info, dict):
        # Check for critical fields
        critical_fields = {
            'marketCap': info.get('marketCap'),
            'trailingPE': info.get('trailingPE'),
            'priceToBook': info.get('priceToBook'),
            'returnOnEquity': info.get('returnOnEquity'),
            'debtToEquity': info.get('debtToEquity'),
            'revenueGrowth': info.get('revenueGrowth'),
            'profitMargins': info.get('profitMargins'),
            'beta': info.get('beta'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
        }
        
        print(f"\nCritical Fields:")
        for field, value in critical_fields.items():
            status = "✅" if value not in [None, '', 0] else "❌"
            print(f"  {status} {field}: {value}")
        
        # Sample of all available keys
        print(f"\n📋 First 20 available keys:")
        for i, key in enumerate(list(info.keys())[:20]):
            print(f"  {i+1}. {key}")
            
except Exception as e:
    print(f"❌ ticker.info failed: {e}")

print(f"\n{'='*60}\n")
