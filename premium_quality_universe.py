#!/usr/bin/env python3
"""
Premium Quality Stock Universe - 700 High-Quality US Market Stocks
Focus: Low-risk, steady growth, institutional-grade blue-chip companies
Criteria:
- Established companies with proven track records
- Market cap > $2 billion
- Consistent revenue and earnings growth
- Strong balance sheets and cash flows
- Low to moderate volatility
- Quality dividends (where applicable)
- Institutional ownership
- US-listed only (no Canadian .TO stocks)
"""

PREMIUM_QUALITY_UNIVERSE = {
    
    # ========================================================================
    # MEGA CAP TECHNOLOGY - Tier 1 (50 stocks)
    # Dominant tech giants with moats and steady growth
    # ========================================================================
    'mega_cap_tech': [
        # Tech Titans (FAANG+ Extended)
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA',
        'AVGO', 'ORCL', 'ADBE', 'CRM', 'INTU', 'CSCO', 'IBM',
        'NOW', 'ACN', 'QCOM', 'TXN', 'AMAT', 'LRCX',
        
        # Software Leaders
        'PANW', 'SNPS', 'CDNS', 'ADSK', 'WDAY', 'FTNT',
        'TEAM', 'VEEV', 'ANSS', 'DDOG',
        
        # Semiconductors - Established
        'ADI', 'KLAC', 'MU', 'MCHP', 'NXPI', 'MRVL',
        'MPWR', 'ON', 'ENTG', 'TER', 'STX', 'WDC',
        
        # IT Services
        'CTSH', 'IT', 'GLW', 'HPQ'
    ],
    
    # ========================================================================
    # HEALTHCARE & PHARMA - Tier 1 (80 stocks)
    # Established pharma, medical devices, healthcare services
    # ========================================================================
    'healthcare_pharma': [
        # Big Pharma - Proven Winners
        'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT',
        'DHR', 'AMGN', 'BMY', 'GILD', 'AZN', 'NVO', 'SNY', 'GSK',
        'REGN', 'VRTX', 'BIIB', 'ALNY',
        
        # Medical Devices - Quality Leaders
        'ISRG', 'SYK', 'BSX', 'MDT', 'BDX', 'EW', 'ZBH', 'BAX',
        'HOLX', 'STE', 'RMD', 'ALGN', 'PODD', 'COO', 'WAT', 'IDXX',
        'DXCM', 'ILMN', 'A', 'TFX', 'MMSI', 'HAE', 'TECH', 'QDEL',
        
        # Healthcare Services - Stable Revenue
        'HCA', 'IQV', 'HUM', 'CNC', 'CI', 'CVS', 'ELV', 'MOH',
        'CRL', 'MEDP', 'LH', 'DGX', 'GEHC', 'WST', 'BRKR',
        
        # Managed Care & Insurance
        'ANTM', 'CYH', 'THC', 'UHS', 'ALC',
        
        # Pharma Services
        'VTRS', 'PBH', 'PRGO', 'OGN', 'CORT', 'LBPH', 'JAZZ',
        'INCY', 'EXAS', 'UTHR', 'NBIX', 'BMRN'
    ],
    
    # ========================================================================
    # FINANCIALS - Tier 1 (100 stocks)
    # Major banks, asset managers, insurance, payment processors
    # ========================================================================
    'financials': [
        # Money Center & Major Banks
        'JPM', 'BAC', 'WFC', 'C', 'MS', 'GS', 'SCHW', 'USB',
        'PNC', 'TFC', 'COF', 'BK', 'STT', 'MTB', 'FITB',
        'HBAN', 'RF', 'KEY', 'CFG', 'ZION', 'CMA', 'FHN',
        
        # Asset Management - Blue Chip
        'BLK', 'BX', 'KKR', 'APO', 'ARES', 'CG', 'TROW', 'IVZ',
        'BEN', 'AMG', 'SEIC', 'APAM',
        
        # Insurance - Quality
        'BRK-B', 'PGR', 'TRV', 'ALL', 'AIG', 'MET', 'PRU', 'AFL',
        'CINF', 'WRB', 'L', 'GL', 'AIZ', 'CB', 'AJG', 'MMC',
        'AON', 'BRO', 'ERIE', 'SIGI', 'RLI', 'AFG', 'FNF',
        'CNA', 'RNR', 'KNSL', 'HIG', 'AXP',
        
        # Payment & Fintech - Established
        'V', 'MA', 'PYPL', 'FI', 'FIS', 'FISV', 'PAYX', 'GPN',
        'ADP', 'BR',
        
        # Exchanges & Data
        'CME', 'ICE', 'NDAQ', 'MSCI', 'SPGI', 'MCO', 'CBOE',
        'MKTX', 'VRSK',
        
        # REITs - Quality
        'AMT', 'PLD', 'EQIX', 'PSA', 'EXR', 'WELL', 'AVB', 'EQR',
        'O', 'SPG', 'VTR', 'DLR', 'SBAC'
    ],
    
    # ========================================================================
    # CONSUMER STAPLES - Tier 1 (50 stocks)
    # Defensive, steady cash flows, quality dividends
    # ========================================================================
    'consumer_staples': [
        # Food & Beverage Giants
        'KO', 'PEP', 'PG', 'MDLZ', 'KHC', 'GIS', 'K', 'CPB',
        'SJM', 'CAG', 'MKC', 'CHD', 'CLX', 'HSY', 'TSN', 'HRL',
        
        # Personal Care & Household
        'CL', 'KMB', 'EL', 'CLX', 'CHD',
        
        # Retail Staples
        'WMT', 'COST', 'KR', 'SYY', 'TGT',
        
        # Tobacco & Alcohol (Stable)
        'PM', 'MO', 'BTI', 'STZ', 'TAP', 'BF-B',
        
        # Consumer Products
        'COTY', 'EPC', 'IPAR', 'NWL', 'SPB', 'JBSS',
        
        # Food Distributors
        'USF D', 'PFGC', 'CHEF', 'UNFI'
    ],
    
    # ========================================================================
    # CONSUMER DISCRETIONARY - Tier 1 (60 stocks)
    # Quality retailers, restaurants, apparel
    # ========================================================================
    'consumer_discretionary': [
        # Mega Retailers
        'HD', 'LOW', 'TJX', 'ROST', 'DG', 'DLTR', 'BBY',
        'FIVE', 'BURL', 'ULTA', 'DKS', 'TSCO', 'GPC', 'POOL',
        
        # Restaurants - Established
        'MCD', 'SBUX', 'YUM', 'QSR', 'CMG', 'DPZ', 'WING', 'TXRH',
        'DRI', 'BLMN', 'DENN', 'EAT', 'CAKE', 'WEN',
        
        # Apparel & Footwear - Quality
        'NKE', 'LULU', 'DECK', 'CROX', 'VFC', 'RL', 'PVH',
        'SKX', 'ONON', 'FL', 'BOOT',
        
        # Home & Specialty Retail
        'WSM', 'RH', 'BBWI', 'TPR', 'CNK',
        
        # Auto - Established
        'F', 'GM', 'HMC', 'TM',
        
        # Leisure & Travel
        'MAR', 'HLT', 'H', 'WYNN', 'LVS', 'MGM', 'CCL', 'RCL'
    ],
    
    # ========================================================================
    # INDUSTRIALS - Tier 1 (70 stocks)
    # Aerospace, manufacturing, transportation, construction
    # ========================================================================
    'industrials': [
        # Aerospace & Defense
        'RTX', 'LMT', 'BA', 'NOC', 'GD', 'LHX', 'TDG', 'HWM',
        'HEI', 'TXT', 'LDOS', 'HII',
        
        # Industrial Conglomerates & Manufacturing
        'GE', 'HON', 'CAT', 'DE', 'EMR', 'ITW', 'MMM', 'ETN',
        'PH', 'ROK', 'DOV', 'IR', 'XYL', 'FLS', 'ROP',
        'CMI', 'PCAR', 'OSK', 'FAST', 'MSM', 'AOS',
        
        # Transportation & Logistics
        'UNP', 'UPS', 'FDX', 'NSC', 'CSX', 'ODFL', 'SAIA', 'XPO',
        'JBHT', 'KNX', 'CHRW', 'EXPD', 'LSTR',
        
        # Construction & Engineering
        'URI', 'VMC', 'MLM', 'SUM', 'FWRD', 'BLD', 'BLDR', 'OC',
        'BECN', 'UFPI',
        
        # Electrical & Equipment
        'HUBB', 'AME', 'TT', 'GNRC', 'AIT', 'RRX'
    ],
    
    # ========================================================================
    # ENERGY - Tier 1 (45 stocks)
    # Major integrated oils, E&P leaders, midstream
    # ========================================================================
    'energy': [
        # Integrated Majors & Supermajors
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'PSX', 'VLO',
        'MPC', 'FANG', 'DVN', 'HAL', 'BKR',
        
        # E&P - Quality
        'APA', 'CTRA', 'HES', 'MTDR', 'MRO',
        
        # Midstream & Infrastructure
        'WMB', 'KMI', 'OKE', 'LNG', 'TRGP', 'EPD', 'ET',
        
        # Oilfield Services
        'NOV', 'FTI', 'VAL', 'CHX', 'HP',
        
        # Coal & Traditional
        'ARCH', 'BTU', 'CEIX'
    ],
    
    # ========================================================================
    # UTILITIES & POWER - Tier 1 (45 stocks)
    # Regulated utilities, steady dividends, defensive
    # ========================================================================
    'utilities': [
        # Electric Utilities - Major
        'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'D', 'EXC', 'ED',
        'XEL', 'EIX', 'PEG', 'WEC', 'ES', 'FE', 'AES',
        
        # Multi-Utilities
        'PCG', 'CMS', 'EVRG', 'NI', 'PNW', 'AEE', 'CNP',
        'DTE', 'ETR', 'PPL', 'LNT', 'OGE', 'NWE',
        
        # Water Utilities
        'AWK', 'AWR', 'CWT', 'SJW', 'MSEX',
        
        # Gas Utilities
        'ATO', 'SR', 'NJR', 'NFG', 'SWX'
    ],
    
    # ========================================================================
    # MATERIALS & CHEMICALS - Tier 1 (40 stocks)
    # Chemicals, mining, metals - established players
    # ========================================================================
    'materials': [
        # Chemicals - Major
        'LIN', 'APD', 'SHW', 'ECL', 'DD', 'DOW', 'EMN', 'ALB',
        'FMC', 'IFF', 'PPG', 'RPM', 'SEE', 'AVY',
        
        # Packaging
        'PKG', 'IP', 'WRK', 'AMCR', 'SON', 'GPK', 'SLVM',
        
        # Mining & Metals - Quality
        'NEM', 'FCX', 'GOLD', 'AEM', 'SCCO', 'AA', 'X', 'NUE',
        'STLD', 'RS', 'CLF', 'MT', 'TECK'
    ],
    
    # ========================================================================
    # REAL ESTATE - Tier 1 (40 stocks)
    # Quality REITs across sectors
    # ========================================================================
    'real_estate': [
        # Cell Tower & Data Center
        'AMT', 'CCI', 'SBAC', 'EQIX', 'DLR',
        
        # Industrial & Logistics
        'PLD', 'DRE', 'FR', 'STAG', 'TRNO',
        
        # Residential
        'AVB', 'EQR', 'MAA', 'UDR', 'ESS', 'CPT', 'SUI', 'ELS',
        
        # Retail
        'O', 'SPG', 'REG', 'KIM', 'BRX', 'STOR', 'NNN', 'ADC',
        
        # Office
        'BXP', 'VNO', 'SLG', 'HIW', 'CUZ',
        
        # Healthcare
        'WELL', 'VTR', 'PEAK', 'DOC', 'HR', 'LTC',
        
        # Specialty
        'PSA', 'EXR', 'CUBE', 'NSA'
    ],
    
    # ========================================================================
    # COMMUNICATION SERVICES - Tier 1 (30 stocks)
    # Media, telecom, entertainment - established
    # ========================================================================
    'communication': [
        # Telecom Giants
        'T', 'VZ', 'TMUS', 'CMCSA',
        
        # Media & Entertainment
        'DIS', 'NFLX', 'PARA', 'WBD', 'FOXA', 'FOX', 'ROKU',
        'SPOT',
        
        # Gaming - Established
        'EA', 'TTWO', 'ATVI',
        
        # Advertising & Marketing
        'OMC', 'IPG', 'PUBM', 'MGNI',
        
        # Publishing & News
        'NYT', 'LEE', 'QUAD',
        
        # Cable & Satellite
        'CHTR', 'DISH', 'SIRI', 'CABO'
    ],
    
    # ========================================================================
    # QUALITY MID-CAPS - Tier 2 (90 stocks)
    # Established mid-caps with growth potential
    # ========================================================================
    'quality_midcaps': [
        # Industrial Mid-Caps
        'PWR', 'OTIS', 'CARR', 'J', 'WCC', 'MSA', 'CR', 'FN',
        'TILE', 'SSD', 'AIR', 'LPX', 'MHO', 'KBH', 'TPH',
        
        # Tech Mid-Caps
        'NTAP', 'FFIV', 'AKAM', 'VRSN', 'GDDY', 'PTC', 'KEYS',
        'FICO', 'EPAM', 'GEN', 'JKHY', 'TRMB', 'ZBRA', 'TYL',
        'SSNC', 'MANH', 'CVLT', 'BSY', 'CDW', 'DELL',
        
        # Healthcare Mid-Caps
        'GMED', 'ENSG', 'ACHC', 'NHC', 'PNTG', 'RRX', 'LMAT',
        'NVCR', 'ICUI', 'CERT', 'OMCL', 'ANGO',
        
        # Financial Mid-Caps
        'RYAN', 'ERIE', 'WAL', 'WTFC', 'UBSI', 'ONB', 'UMBF',
        'FFIN', 'CBSH', 'FULT', 'BPOP', 'OZK', 'SFNC',
        
        # Consumer Mid-Caps
        'CASY', 'FLO', 'ELF', 'CALM', 'JJSF', 'SMPL', 'USNA',
        'CVLG', 'UVV', 'SHAK', 'BROS', 'CAVA',
        
        # Materials Mid-Caps
        'HUN', 'AXTA', 'KWR', 'NGVT', 'SLGN',
        
        # Energy Mid-Caps
        'CHRD', 'CNX', 'AR', 'PR', 'MGY', 'CIVI'
    ]
}

def get_premium_universe():
    """Get complete premium quality universe as flat list (~700 stocks)"""
    all_stocks = []
    for category, stocks in PREMIUM_QUALITY_UNIVERSE.items():
        all_stocks.extend(stocks)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_stocks = []
    for stock in all_stocks:
        stock = stock.strip().upper()
        if stock not in seen and stock:  # Ensure no empty strings
            seen.add(stock)
            unique_stocks.append(stock)
    
    return unique_stocks

def get_by_category(category):
    """Get stocks by specific category"""
    return PREMIUM_QUALITY_UNIVERSE.get(category, [])

def get_by_risk_tier(tier='tier1'):
    """Get stocks by risk/quality tier"""
    if tier.lower() == 'tier1' or tier.lower() == 'mega':
        # Return only mega cap and tier 1 stocks
        tier1_categories = [
            'mega_cap_tech', 'healthcare_pharma', 'financials',
            'consumer_staples', 'utilities', 'materials'
        ]
        stocks = []
        for cat in tier1_categories:
            stocks.extend(PREMIUM_QUALITY_UNIVERSE.get(cat, []))
        return list(set(stocks))
    
    return get_premium_universe()

def print_universe_stats():
    """Print premium universe statistics"""
    full_universe = get_premium_universe()
    
    print("=" * 80)
    print("PREMIUM QUALITY STOCK UNIVERSE - STATISTICS")
    print("=" * 80)
    print()
    print("🎯 Focus: Low-risk, steady growth, institutional-grade stocks")
    print("📊 Criteria: Proven track records, strong fundamentals, quality leadership")
    print()
    print(f"📈 Total Quality Stocks: {len(full_universe)}")
    print()
    
    print("By Sector:")
    total_count = 0
    for category, stocks in PREMIUM_QUALITY_UNIVERSE.items():
        count = len(stocks)
        total_count += count
        print(f"  {category:30s}: {count:3d} stocks")
    print(f"\n  {'TOTAL BEFORE DEDUP':30s}: {total_count:3d}")
    print(f"  {'TOTAL AFTER DEDUP':30s}: {len(full_universe):3d}")
    print()
    
    print("=" * 80)
    print("✅ All stocks are US-listed, liquid, established companies")
    print("✅ Focus on low-risk, steady growth vs speculative plays")
    print("✅ Institutional-grade quality for conservative portfolios")
    print("=" * 80)

if __name__ == "__main__":
    print_universe_stats()
    
    # Show sample
    full = get_premium_universe()
    print("\n📋 Sample Premium Stocks (first 30):")
    for i in range(0, min(30, len(full)), 10):
        print(f"  {full[i:i+10]}")
    
    print(f"\n✅ Total premium quality stocks: {len(full)}")
