import os, sys
from datetime import datetime

# Ensure project root in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from advanced_data_fetcher import AdvancedDataFetcher

key_env = os.environ.get('ALPHA_VANTAGE_API_KEY') or os.environ.get('ALPHAVANTAGE_API_KEY')
key_src = 'ENV' if key_env else 'REPO'
print(f"Alpha Vantage key source: {key_src}")

fetcher = AdvancedDataFetcher(data_mode="light")

mask = lambda k: (k[:4] + '*'*(len(k)-8) + k[-4:]) if k and len(k) >= 8 else 'N/A'
print(f"Fetcher key present: {'YES' if bool(getattr(fetcher, 'alpha_vantage_key', None)) else 'NO'}")
if getattr(fetcher, 'alpha_vantage_key', None):
    print(f"Key (masked): {mask(fetcher.alpha_vantage_key)}")

for sym in ["AAPL", "MSFT", "IBM"]:
    print(f"\n[AV fallback] Trying {sym}...")
    df = fetcher._try_alpha_vantage_free(sym)
    if df is None or getattr(df, 'empty', True):
        print(f"  ❌ No data from Alpha Vantage for {sym}")
    else:
        last_dt = df.index[-1].strftime('%Y-%m-%d')
        last_close = float(df['Close'].iloc[-1])
        print(f"  ✅ Rows: {len(df)} | Last: {last_dt} Close={last_close:.2f}")

print("\nDone.")
