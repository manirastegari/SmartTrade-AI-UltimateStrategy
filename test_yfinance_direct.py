"""Quick test to verify fundamental data fetching works"""
import yfinance as yf
import time

test_symbols = ['AAPL', 'MSFT', 'GOOGL']

print("Testing direct yfinance .info fetch:\n")

for symbol in test_symbols:
    print(f"📊 {symbol}...")
    try:
        time.sleep(0.3)
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        market_cap = info.get('marketCap', 0)
        pe = info.get('trailingPE', 0)
        sector = info.get('sector', 'Unknown')
        
        print(f"   Market Cap: ${market_cap:,}")
        print(f"   P/E Ratio: {pe:.2f}" if pe else "   P/E Ratio: N/A")
        print(f"   Sector: {sector}")
        print(f"   ✅ Success\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

print("=" * 60)
print("If you see valid market caps above, the fix will work!")
