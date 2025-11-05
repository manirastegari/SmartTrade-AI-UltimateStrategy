#!/usr/bin/env python3
"""
Cleaned High-Potential Stock Universe (Optimized)
NOW USES PREMIUM QUALITY UNIVERSE (700+ low-risk, steady-growth stocks)
Focus: Institutional-grade blue-chip US companies only
"""

SYMBOL_NORMALIZATION_MAP = {
    'BRK.B': 'BRK-B',
    'BRK-B': 'BRK-B',
    'BF.B': 'BF-B',
    'BF-B': 'BF-B',
    'LGF.A': 'LGF-A',
    'LGF-A': 'LGF-A',
    'LGF.B': 'LGF-B',
    'LGF-B': 'LGF-B',
}


def get_cleaned_high_potential_universe():
    """Get premium quality universe with low-risk, steady-growth stocks"""
    
    try:
        from premium_quality_universe import get_premium_universe
        raw_universe = get_premium_universe()
        normalized_universe = _normalize_universe_symbols(raw_universe)
        baseline_count = len(normalized_universe)
        aligned_universe = _ensure_tfsa_questrade_alignment(normalized_universe)
        target_min = max(baseline_count, 680)
        final_universe = sanitize_runtime_universe(aligned_universe, target_min=target_min)
        print(f"✅ Loaded Premium Quality universe: {len(final_universe)} TFSA-ready stocks (low-risk, steady-growth)")
        return final_universe
    except ImportError:
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
    seen = set()
    out = []
    for symbol in (universe or []):
        normalized = _normalize_symbol(symbol)
        if normalized and normalized not in seen:
            seen.add(normalized)
            out.append(normalized)
    return out


def _normalize_symbol(symbol):
    if not symbol:
        return ''
    sym = str(symbol).strip().upper()
    return SYMBOL_NORMALIZATION_MAP.get(sym, sym)


def _ensure_tfsa_questrade_alignment(universe):
    valid_list, valid_set = _load_valid_questrade_symbols()
    if not valid_list:
        return universe
    replacements = _build_tfsa_replacement_map()
    filtered = []
    seen = set()
    replacements_applied = []
    unresolved = set()

    fallback_iter = iter(valid_list)

    def next_fallback():
        while True:
            try:
                candidate = next(fallback_iter)
            except StopIteration:
                return None
            if candidate not in seen:
                return candidate

    for symbol in universe:
        replacement_used = None
        candidate = None

        if symbol in valid_set and symbol not in seen:
            candidate = symbol
        else:
            mapped = replacements.get(symbol)
            if mapped and mapped in valid_set and mapped not in seen:
                candidate = mapped
                replacement_used = mapped
            if candidate is None:
                fallback = next_fallback()
                if fallback:
                    candidate = fallback
                    replacement_used = fallback
            if candidate is None:
                if symbol not in seen:
                    candidate = symbol
                    if symbol not in valid_set:
                        unresolved.add(symbol)
                else:
                    if symbol not in valid_set:
                        unresolved.add(symbol)
                    continue

        if candidate in seen:
            fallback = next_fallback()
            if fallback:
                candidate = fallback
                replacement_used = fallback
            elif symbol not in seen:
                candidate = symbol
                replacement_used = None
                if symbol not in valid_set:
                    unresolved.add(symbol)
            else:
                if symbol not in valid_set:
                    unresolved.add(symbol)
                continue

        filtered.append(candidate)
        seen.add(candidate)
        if replacement_used and candidate != symbol:
            replacements_applied.append((symbol, candidate))

    if replacements_applied:
        print(f"🔁 TFSA/Questrade replacements applied: {len(replacements_applied)}")
        for old, new in replacements_applied[:5]:
            print(f"   {old} → {new}")
        if len(replacements_applied) > 5:
            print(f"   ... {len(replacements_applied) - 5} additional replacements")
    if unresolved:
        print(f"⚠️ {len(unresolved)} symbols could not be validated against TFSA/Questrade lists and were kept as-is")
    return filtered


def _load_valid_questrade_symbols():
    try:
        from questrade_valid_universe import get_questrade_valid_universe
        valid_universe = _normalize_universe_symbols(get_questrade_valid_universe())
        return valid_universe, set(valid_universe)
    except Exception:
        return [], set()


def _build_tfsa_replacement_map():
    mapping = {}
    try:
        from tfsa_questrade_fixes import get_symbol_corrections, get_tfsa_friendly_replacements
        for fetcher in (get_symbol_corrections, get_tfsa_friendly_replacements):
            try:
                data = fetcher()
            except Exception:
                data = None
            if not isinstance(data, dict):
                continue
            for old, new in data.items():
                normalized_old = _normalize_symbol(old)
                normalized_new = _normalize_symbol(new) if new else ''
                if normalized_old and normalized_new:
                    mapping[normalized_old] = normalized_new
    except Exception:
        pass
    return mapping


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
