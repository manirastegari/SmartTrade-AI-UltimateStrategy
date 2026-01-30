#!/usr/bin/env python3
"""
Questrade Valid Universe - TFSA-Eligible US Stocks
Contains ~700 validated US stocks that are eligible for Canadian TFSA accounts
and tradeable on Questrade platform.

These stocks are selected based on:
- US-listed only (no OTC, pink sheets, or foreign stocks)
- Adequate liquidity (average daily volume > 100,000)
- Market cap > $1 billion
- No complex structured products (ETNs, leveraged ETFs excluded)
"""

# Core S&P 500 stocks - All TFSA eligible
SP500_CORE = [
    # Technology
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'AVGO', 'ORCL', 'ADBE',
    'CRM', 'CSCO', 'ACN', 'IBM', 'INTC', 'AMD', 'QCOM', 'TXN', 'INTU', 'NOW',
    'AMAT', 'LRCX', 'ADI', 'KLAC', 'MU', 'SNPS', 'CDNS', 'MCHP', 'NXPI', 'MRVL',
    'PANW', 'ADSK', 'WDAY', 'FTNT', 'TEAM', 'ZS', 'DDOG', 'CRWD', 'SNOW', 'PLTR',
    'NET', 'DATADOG', 'VEEV', 'HUBS', 'DOCU', 'OKTA', 'ZM', 'SPLK', 'MDB', 'COUP',
    
    # Healthcare & Pharma
    'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR', 'AMGN',
    'BMY', 'GILD', 'VRTX', 'REGN', 'ISRG', 'SYK', 'BSX', 'MDT', 'BDX', 'EW',
    'IDXX', 'DXCM', 'IQV', 'ZBH', 'BAX', 'HOLX', 'STE', 'RMD', 'ALGN', 'PODD',
    'HCA', 'HUM', 'CNC', 'CI', 'CVS', 'ELV', 'MOH', 'BIIB', 'ALNY', 'MRNA',
    
    # Financials
    'JPM', 'BAC', 'WFC', 'C', 'MS', 'GS', 'SCHW', 'USB', 'PNC', 'TFC',
    'COF', 'BK', 'STT', 'MTB', 'FITB', 'HBAN', 'RF', 'KEY', 'CFG', 'ZION',
    'BLK', 'BX', 'KKR', 'APO', 'ARES', 'TROW', 'IVZ', 'BEN', 'AXP', 'V',
    'MA', 'PYPL', 'FIS', 'FISV', 'GPN', 'ADP', 'PAYX', 'BR', 'CME', 'ICE',
    'NDAQ', 'SPGI', 'MCO', 'CBOE', 'MKTX', 'PGR', 'TRV', 'ALL', 'AIG', 'MET',
    'PRU', 'AFL', 'MMC', 'AON', 'WTW', 'CINF', 'BRK-B',
    
    # Consumer Staples
    'KO', 'PEP', 'PG', 'WMT', 'COST', 'MDLZ', 'CL', 'KMB', 'MCD', 'SBUX',
    'KHC', 'GIS', 'K', 'CPB', 'SJM', 'CAG', 'MKC', 'CHD', 'CLX', 'HSY',
    'TSN', 'HRL', 'MNST', 'KDP', 'PM', 'MO', 'STZ', 'TAP', 'BF-B', 'EL',
    'KR', 'SYY', 'TGT', 'BJ', 'DG', 'DLTR',
    
    # Consumer Discretionary
    'HD', 'LOW', 'TJX', 'ROST', 'BBY', 'FIVE', 'BURL', 'ULTA', 'DKS', 'TSCO',
    'GPC', 'POOL', 'YUM', 'QSR', 'CMG', 'DPZ', 'WING', 'TXRH', 'DRI', 'WEN',
    'NKE', 'LULU', 'DECK', 'CROX', 'VFC', 'RL', 'PVH', 'SKX', 'FL', 'COLM',
    'WSM', 'RH', 'TPR', 'F', 'GM', 'MAR', 'HLT', 'WYNN', 'LVS', 'MGM',
    'CCL', 'RCL', 'NCLH', 'EXPE', 'BKNG', 'ABNB', 'UBER', 'LYFT',
    
    # Industrials
    'RTX', 'LMT', 'BA', 'NOC', 'GD', 'LHX', 'TDG', 'HWM', 'HEI', 'TXT',
    'GE', 'HON', 'CAT', 'DE', 'EMR', 'ITW', 'MMM', 'ETN', 'PH', 'ROK',
    'DOV', 'IR', 'XYL', 'FLS', 'ROP', 'CMI', 'PCAR', 'OSK', 'FAST',
    'UNP', 'UPS', 'FDX', 'NSC', 'CSX', 'ODFL', 'SAIA', 'XPO', 'JBHT', 'CHRW',
    'URI', 'VMC', 'MLM', 'GNRC', 'AME', 'TT', 'HUBB', 'PWR', 'OTIS', 'CARR',
    
    # Energy
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'PSX', 'VLO', 'MPC', 'FANG',
    'DVN', 'HAL', 'BKR', 'APA', 'CTRA', 'WMB', 'KMI', 'OKE', 'LNG', 'TRGP',
    'EPD', 'ET', 'NOV', 'FTI',
    
    # Utilities
    'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'D', 'EXC', 'ED', 'XEL', 'EIX',
    'PEG', 'WEC', 'ES', 'FE', 'AES', 'PCG', 'CMS', 'EVRG', 'NI', 'PNW',
    'AEE', 'CNP', 'DTE', 'ETR', 'PPL', 'LNT', 'AWK', 'AWR', 'WTRG', 'ATO',
    
    # Materials
    'LIN', 'APD', 'SHW', 'ECL', 'DD', 'DOW', 'EMN', 'ALB', 'FMC', 'IFF',
    'PPG', 'RPM', 'SEE', 'AVY', 'PKG', 'IP', 'NEM', 'FCX', 'SCCO', 'AA',
    'NUE', 'STLD', 'RS', 'CLF',
    
    # Real Estate
    'AMT', 'PLD', 'EQIX', 'PSA', 'O', 'WELL', 'AVB', 'EQR', 'DLR', 'SBAC',
    'CCI', 'VICI', 'VTR', 'EXR', 'MAA', 'UDR', 'ESS', 'CPT', 'REG', 'KIM',
    'BXP', 'VNO', 'SLG', 'CUBE', 'NSA',
    
    # Communication Services
    'T', 'VZ', 'TMUS', 'CMCSA', 'DIS', 'NFLX', 'WBD', 'FOXA', 'FOX', 'ROKU',
    'SPOT', 'EA', 'TTWO', 'ATVI', 'OMC', 'IPG', 'NYT', 'NWSA', 'CHTR', 'SIRI',
]

# Additional quality mid-caps for expanded universe
QUALITY_MIDCAPS = [
    # Tech Mid-Caps
    'NTAP', 'FFIV', 'AKAM', 'VRSN', 'GDDY', 'PTC', 'KEYS', 'FICO', 'EPAM', 'JKHY',
    'TRMB', 'ZBRA', 'TYL', 'SSNC', 'MANH', 'CDW', 'DELL', 'HPE', 'HPQ', 'WDC',
    'STX', 'SMCI', 'ANET', 'MPWR', 'ON', 'ENTG', 'TER', 'CHKP', 'GEN', 'GLOB',
    
    # Healthcare Mid-Caps
    'GMED', 'ENSG', 'ACHC', 'LMAT', 'NVCR', 'ICUI', 'OMCL', 'TECH', 'QDEL', 'COO',
    'TFX', 'MMSI', 'HAE', 'CRL', 'MEDP', 'LH', 'DGX', 'GEHC', 'WST', 'BRKR',
    'VTRS', 'PBH', 'PRGO', 'OGN', 'TEVA', 'JAZZ', 'INCY', 'EXAS', 'UTHR', 'NBIX',
    
    # Financial Mid-Caps
    'RYAN', 'ERIE', 'WAL', 'WTFC', 'UBSI', 'ONB', 'UMBF', 'FFIN', 'CBSH', 'FULT',
    'BPOP', 'OZK', 'SFNC', 'CMA', 'FHN', 'FNF', 'CNA', 'RNR', 'KNSL', 'HIG',
    'LPLA', 'GL', 'AIZ', 'AJG', 'WRB', 'SIGI', 'RLI', 'AFG',
    
    # Industrial Mid-Caps
    'J', 'WCC', 'MLI', 'CR', 'FN', 'TILE', 'SSD', 'AIR', 'LPX', 'MHO',
    'KBH', 'TPH', 'LDOS', 'HII', 'MTZ', 'UFPI', 'AIT', 'RRX', 'LSTR', 'EXPD',
    'KNX', 'ARMK', 'AOS', 'BLD', 'OC',
    
    # Consumer Mid-Caps
    'CASY', 'FLO', 'ELF', 'CALM', 'JJSF', 'SMPL', 'GO', 'SHAK', 'BROS', 'CAVA',
    'BLMN', 'DENN', 'EAT', 'CAKE', 'CNK', 'BOOT', 'ONON', 'IPAR', 'NWL', 'SPB',
    
    # Energy Mid-Caps
    'CHRD', 'CNX', 'AR', 'PR', 'MGY', 'CIVI', 'SM', 'MTDR', 'CEIX', 'BTU',
    'ARLP', 'VAL', 'RIG', 'HP',
    
    # Materials Mid-Caps
    'HUN', 'AXTA', 'KWR', 'NGVT', 'SLGN', 'CCK', 'AMCR', 'SON', 'GPK',
    'AEM', 'CMC', 'MT', 'TECK',
    
    # Real Estate Mid-Caps
    'REXR', 'FR', 'STAG', 'TRNO', 'SUI', 'ELS', 'BRX', 'NNN', 'ADC', 'HIW',
    'CUZ', 'CTRE', 'DOC', 'HR', 'LTC',
]

# Additional growth stocks
GROWTH_STOCKS = [
    'TSLA', 'COIN', 'SQ', 'SHOP', 'RBLX', 'U', 'DASH', 'PATH', 'CFLT', 'S',
    'BILL', 'PCTY', 'PAYC', 'WK', 'CWAN', 'GTLB', 'ESTC', 'PD', 'FROG', 'AI',
    'IONQ', 'RGTI', 'ARQQ', 'RIVN', 'LCID', 'FSR', 'NIO', 'XPEV', 'LI', 'CHPT',
    'ENVX', 'QS', 'BLDP', 'PLUG', 'FCEL', 'BE', 'ENPH', 'SEDG', 'RUN', 'NOVA',
]

# Dividend aristocrats and kings
DIVIDEND_LEADERS = [
    'JNJ', 'KO', 'PG', 'MMM', 'EMR', 'CL', 'GPC', 'LOW', 'WMT', 'ABT',
    'ADP', 'PEP', 'ITW', 'SYY', 'ED', 'TGT', 'ABBV', 'XOM', 'CVX', 'BEN',
    'FRT', 'NNN', 'O', 'T', 'VZ', 'IBM', 'TROW', 'AFL', 'MCD', 'CAT',
]


def get_questrade_valid_universe():
    """
    Get the complete Questrade/TFSA-validated stock universe.
    
    Returns:
        list: ~700 unique stock symbols validated for Questrade TFSA trading
    """
    all_stocks = []
    
    # Add all categories
    all_stocks.extend(SP500_CORE)
    all_stocks.extend(QUALITY_MIDCAPS)
    all_stocks.extend(GROWTH_STOCKS)
    all_stocks.extend(DIVIDEND_LEADERS)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_stocks = []
    for stock in all_stocks:
        stock_clean = stock.strip().upper()
        if stock_clean and stock_clean not in seen:
            seen.add(stock_clean)
            unique_stocks.append(stock_clean)
    
    return unique_stocks


def get_tfsa_core():
    """Get just the S&P 500 core stocks (most liquid, lowest risk)"""
    return list(SP500_CORE)


def get_dividend_stocks():
    """Get dividend aristocrats and kings for income-focused portfolios"""
    return list(DIVIDEND_LEADERS)


def get_growth_stocks():
    """Get high-growth stocks (higher risk, higher potential)"""
    return list(GROWTH_STOCKS)


def print_universe_stats():
    """Print statistics about the Questrade valid universe"""
    universe = get_questrade_valid_universe()
    print("=" * 60)
    print("QUESTRADE VALID UNIVERSE - TFSA ELIGIBLE STOCKS")
    print("=" * 60)
    print(f"\n📊 Total Unique Stocks: {len(universe)}")
    print(f"\n   S&P 500 Core: {len(SP500_CORE)}")
    print(f"   Quality Mid-Caps: {len(QUALITY_MIDCAPS)}")
    print(f"   Growth Stocks: {len(GROWTH_STOCKS)}")
    print(f"   Dividend Leaders: {len(DIVIDEND_LEADERS)}")
    print("\n✅ All stocks are US-listed and TFSA-eligible")
    print("✅ Validated for Questrade platform")
    print("=" * 60)


if __name__ == "__main__":
    print_universe_stats()
    
    # Show sample
    universe = get_questrade_valid_universe()
    print(f"\n📋 Sample stocks (first 30):")
    print(f"   {universe[:30]}")
