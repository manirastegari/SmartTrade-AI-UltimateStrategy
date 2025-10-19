#!/usr/bin/env python3
"""
Cleaned High-Potential Stock Universe (Optimized)
Removed delisted/acquired stocks, added high-quality replacements
NOW USES QUESTRADE-VALID UNIVERSE (800+ stocks)
"""

def get_cleaned_high_potential_universe():
    """Get cleaned universe with problematic stocks removed - uses Questrade-valid universe"""
    
    # Import the Questrade-valid universe
    try:
        from questrade_valid_universe import get_questrade_valid_universe
        return get_questrade_valid_universe()
    except ImportError:
        # Fallback to a minimal safe universe
        print("⚠️ Warning: Could not import questrade_valid_universe, using fallback")
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

if __name__ == "__main__":
    universe = get_cleaned_high_potential_universe()
    print(f"Cleaned universe: {len(universe)} stocks")
    
    # Count by exchange
    us_stocks = [s for s in universe if not s.endswith('.TO')]
    canadian_stocks = [s for s in universe if s.endswith('.TO')]
    
    print(f"US stocks: {len(us_stocks)}")
    print(f"Canadian stocks: {len(canadian_stocks)}")
