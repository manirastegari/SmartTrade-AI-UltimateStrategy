#!/usr/bin/env python3
"""
Cleaned High-Potential Stock Universe (Optimized)
Removed delisted/acquired stocks, added high-quality replacements
NOW USES QUESTRADE-VALID UNIVERSE (800+ stocks)
"""

def get_cleaned_high_potential_universe():
    """Get cleaned universe with problematic stocks removed - uses TFSA/Questrade 750+ optimized universe"""
    
    # Import the TFSA/Questrade optimized universe (750+ stocks)
    try:
        from tfsa_questrade_750_universe import get_full_universe
        universe = get_full_universe()
        print(f"✅ Loaded TFSA/Questrade universe: {len(universe)} stocks")
        return universe
    except ImportError:
        # Fallback to questrade valid universe
        try:
            from questrade_valid_universe import get_questrade_valid_universe
            universe = get_questrade_valid_universe()
            print(f"✅ Loaded Questrade valid universe: {len(universe)} stocks")
            return universe
        except ImportError:
            # Fallback to a minimal safe universe
            print("⚠️ Warning: Could not import universe files, using fallback (100 stocks)")
            return [
                # S&P 500 Top 100 (all valid)
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'AVGO',
                'LLY', 'JPM', 'V', 'UNH', 'XOM', 'MA', 'ORCL', 'HD', 'PG', 'COST',
                'JNJ', 'ABBV', 'NFLX', 'BAC', 'CRM', 'CVX', 'MRK', 'KO', 'ADBE', 'WMT',
                'PEP', 'TMO', 'CSCO', 'MCD', 'ABT', 'ACN', 'LIN', 'AMD', 'INTC', 'QCOM',
                'DHR', 'PM', 'TXN', 'INTU', 'AMGN', 'GE', 'ISRG', 'IBM', 'CAT', 'CMCSA',
                'VZ', 'AMAT', 'RTX', 'HON', 'T', 'SPGI', 'LOW', 'NOW', 'PFE', 'NEE',
                'UNP', 'SYK', 'AXP', 'BKNG', 'PLD', 'MS', 'BLK', 'ETN', 'TJX', 'VRTX',
                'LRCX', 'BSX', 'REGN', 'C', 'GILD', 'SCHW', 'ADI', 'DE', 'PANW', 'MMC',
                'KLAC', 'MU', 'CB', 'SO', 'FI', 'MDLZ', 'DUK', 'EQIX', 'SNPS', 'SLB',
                'PGR', 'ICE', 'BMY', 'PYPL', 'CME', 'APH', 'WM', 'AON', 'MCO', 'USB',
            ]


def sanitize_runtime_universe(universe, failed_symbols=None, target_min=730):
    """At runtime, drop symbols that failed across all sources and backfill from a reserve pool.

    Inputs:
    - universe: list[str] initial universe
    - failed_symbols: list[str] symbols that had 'ALL FREE SOURCES FAILED' or 'No real data' in this run
    - target_min: int desired minimum count after sanitation

    Output:
    - list[str] sanitized universe sized at least target_min (if possible)
    """
    failed_set = set([s.strip() for s in (failed_symbols or []) if isinstance(s, str)])
    # Drop failures
    filtered = [s for s in universe if s not in failed_set]

    # Try to reuse the reserve pool from the TFSA universe module; otherwise fallback to a safe local pool
    reserve = []
    try:
        from tfsa_questrade_750_universe import RESERVE_POOL as _RES
        reserve = list(_RES)
    except Exception:
        reserve = [
            'AAPL','MSFT','NVDA','GOOGL','AMZN','META','AVGO','ORCL','ADBE','CRM',
            'V','MA','KO','PEP','PG','COST','WMT','HD','LOW','TJX',
            'RY.TO','TD.TO','BMO.TO','BNS.TO','CM.TO','NA.TO','ENB.TO','TRP.TO','CNQ.TO','SU.TO',
        ]

    seen = set(filtered)
    for sym in reserve:
        if len(filtered) >= target_min:
            break
        if sym not in seen:
            filtered.append(sym)
            seen.add(sym)

    return filtered

if __name__ == "__main__":
    universe = get_cleaned_high_potential_universe()
    print(f"Cleaned universe: {len(universe)} stocks")
    
    # Count by exchange
    us_stocks = [s for s in universe if not s.endswith('.TO')]
    canadian_stocks = [s for s in universe if s.endswith('.TO')]
    
    print(f"US stocks: {len(us_stocks)}")
    print(f"Canadian stocks: {len(canadian_stocks)}")
