#!/usr/bin/env python3
"""
Cleaned High-Potential Stock Universe (Optimized)
NOW USES PREMIUM QUALITY UNIVERSE (700+ low-risk, steady-growth stocks)
Focus: Institutional-grade blue-chip US companies only
"""

def get_cleaned_high_potential_universe():
    """Get premium quality universe with low-risk, steady-growth stocks"""
    
    # Import the PREMIUM quality universe (700+ institutional-grade stocks)
    try:
        from premium_quality_universe import get_premium_universe
        universe = get_premium_universe()
        universe = _normalize_universe_symbols(universe)
        print(f"✅ Loaded Premium Quality universe: {len(universe)} stocks (low-risk, steady-growth)")
        return universe
    except ImportError:
        # Fallback to S&P 500 blue chips if premium universe unavailable
        print("⚠️ Warning: Premium universe not available, using S&P 500 blue-chip fallback")
        return _get_sp500_bluechip_fallback()


def _get_sp500_bluechip_fallback():
    """Fallback S&P 500 blue-chip universe (200 highest quality stocks)"""
    return [
        # Tech Giants
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'AVGO', 'ORCL', 'ADBE',
        'CRM', 'INTU', 'CSCO', 'IBM', 'NOW', 'ACN', 'QCOM', 'TXN', 'AMAT', 'LRCX',
        
        # Healthcare & Pharma
        'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR', 'AMGN',
        'BMY', 'GILD', 'VRTX', 'ISRG', 'SYK', 'BSX', 'MDT', 'BDX', 'REGN', 'CVS',
        
        # Financials
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'SCHW', 'BLK', 'V', 'MA',
        'AXP', 'USB', 'PNC', 'TFC', 'COF', 'BRK-B', 'PGR', 'TRV', 'MMC', 'AON',
        
        # Consumer Staples
        'KO', 'PEP', 'PG', 'WMT', 'COST', 'MDLZ', 'CL', 'KMB', 'MCD', 'SBUX',
        
        # Consumer Discretionary
        'HD', 'LOW', 'TJX', 'NKE', 'LULU', 'TGT', 'DG', 'MAR', 'HLT',
        
        # Industrials
        'RTX', 'LMT', 'BA', 'NOC', 'GE', 'HON', 'CAT', 'DE', 'UNP', 'UPS',
        'FDX', 'NSC', 'CSX', 'ETN', 'EMR', 'ITW', 'MMM',
        
        # Energy
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'MPC', 'VLO', 'OXY',
        
        # Utilities
        'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'D', 'EXC', 'XEL', 'WEC',
        
        # Materials
        'LIN', 'APD', 'SHW', 'ECL', 'NEM', 'FCX', 'NUE', 'DD',
        
        # Real Estate
        'AMT', 'PLD', 'EQIX', 'PSA', 'O', 'SPG', 'WELL', 'AVB',
        
        # Communications
        'T', 'VZ', 'TMUS', 'DIS', 'NFLX', 'CMCSA', 'EA', 'TTWO',
        
        # Software & Cloud
        'PANW', 'SNPS', 'CDNS', 'ADSK', 'WDAY', 'FTNT', 'TEAM', 'VEEV',
        
        # Semiconductors
        'ADI', 'KLAC', 'MU', 'MCHP', 'NXPI', 'MRVL', 'MPWR', 'ON',
        
        # Healthcare Services
        'HCA', 'HUM', 'CNC', 'CI', 'ELV', 'IQV', 'LH', 'DGX',
        
        # Payments & Fintech
        'FI', 'FIS', 'FISV', 'PAYX', 'ADP', 'BR',
        
        # Insurance - Extended
        'ALL', 'AFL', 'MET', 'PRU', 'CB', 'AIG', 'CINF',
        
        # Industrial - Extended
        'PH', 'ROK', 'DOV', 'IR', 'XYL', 'FLS', 'ROP', 'CMI', 'PCAR'
    ]


def _normalize_universe_symbols(universe):
    """Normalize known symbol quirks for yfinance and data fetch stability."""
    mapping = {
        'BRK.B': 'BRK-B',
        'BRK-B': 'BRK-B',
        'BF.B': 'BF-B',
        'BF-B': 'BF-B',
    }
    seen = set()
    out = []
    for s in (universe or []):
        t = mapping.get(s, s)
        t = t.strip().upper()
        if t and t not in seen:
            out.append(t)
            seen.add(t)
    return out


def sanitize_runtime_universe(universe, failed_symbols=None, target_min=680):
    """At runtime, drop symbols that failed across all sources and backfill from a reserve pool."""
    failed_set = set([s.strip().upper() for s in (failed_symbols or []) if isinstance(s, str)])
    filtered = [s for s in universe if s.upper() not in failed_set]
    
    reserve = _get_reserve_pool()
    seen = set([s.upper() for s in filtered])
    
    for sym in reserve:
        if len(filtered) >= target_min:
            break
        sym_upper = sym.upper()
        if sym_upper not in seen:
            filtered.append(sym)
            seen.add(sym_upper)
    
    return filtered


def _get_reserve_pool():
    """Premium reserve pool of ultra-stable blue chips for backfilling"""
    return [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'AVGO', 'ORCL', 'ADBE', 'CRM',
        'V', 'MA', 'KO', 'PEP', 'PG', 'COST', 'WMT', 'HD', 'LOW', 'TJX',
        'LIN', 'APD', 'SHW', 'ECL', 'NEM', 'FCX',
        'UNH', 'LLY', 'JNJ', 'ABBV', 'MRK', 'GE', 'CAT', 'DE', 'HON',
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'BRK-B',
        'PGR', 'TRV', 'ALL', 'CB', 'MMC', 'AON',
        'ADP', 'MSCI', 'SPGI', 'ICE', 'CME', 'MCO', 'VRSK',
        'NEE', 'DUK', 'SO', 'AEP', 'EXC', 'XEL',
        'RTX', 'LMT', 'NOC', 'GD', 'UNP', 'UPS', 'FDX', 'NSC',
        'XOM', 'CVX', 'COP', 'EOG', 'PSX', 'VLO', 'MPC'
    ]
