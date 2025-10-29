import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from advanced_data_fetcher import AdvancedDataFetcher

fetcher = AdvancedDataFetcher(data_mode="light")
symbols = ["AAPL", "RY.TO", "REI.UN.TO"]

hist_map = fetcher.get_bulk_history(symbols, period="1mo", interval="1d")

print({s: (None if (hist_map.get(s) is None or getattr(hist_map.get(s), 'empty', True)) else len(hist_map[s])) for s in symbols})

for s in symbols:
    df = hist_map.get(s)
    if df is not None and not df.empty:
        ok, diff = fetcher.spot_check_against_stooq(s, df)
        print(f"spot_check {s}: ok={ok} diff={diff:.4f}")
