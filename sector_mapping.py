"""
Comprehensive sector mapping for 700+ stocks.
Used as fallback when yfinance info['sector'] is unavailable (e.g., light data mode).
Covers S&P 500, TFSA-ready universe, and common mid/small-caps.
"""

SECTOR_MAP = {
    # ═══════════════════════════════════════════════════════
    # TECHNOLOGY
    # ═══════════════════════════════════════════════════════
    # Mega-cap / Software / Cloud
    'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'GOOG': 'Technology',
    'META': 'Technology', 'NVDA': 'Technology', 'CRM': 'Technology', 'ORCL': 'Technology',
    'ADBE': 'Technology', 'CSCO': 'Technology', 'NOW': 'Technology', 'IBM': 'Technology',
    'INTU': 'Technology', 'ACN': 'Technology', 'SNPS': 'Technology', 'CDNS': 'Technology',
    'ADSK': 'Technology', 'WDAY': 'Technology', 'TEAM': 'Technology', 'PANW': 'Technology',
    'CRWD': 'Technology', 'FTNT': 'Technology', 'ZS': 'Technology', 'NET': 'Technology',
    'DDOG': 'Technology', 'OKTA': 'Technology', 'HUBS': 'Technology', 'MDB': 'Technology',
    'SHOP': 'Technology', 'DOCU': 'Technology', 'BILL': 'Technology', 'VEEV': 'Technology',
    'PAYC': 'Technology', 'PCTY': 'Technology', 'MANH': 'Technology', 'TYL': 'Technology',
    'PTC': 'Technology', 'SSNC': 'Technology', 'BSY': 'Technology', 'CDW': 'Technology',
    'IT': 'Technology', 'EPAM': 'Technology', 'GLOB': 'Technology', 'CVLT': 'Technology',
    'FFIV': 'Technology', 'JKHY': 'Technology', 'AKAM': 'Technology', 'VRSN': 'Technology',
    'GEN': 'Technology', 'CHKP': 'Technology', 'GDDY': 'Technology', 'PATH': 'Technology',
    'SPOT': 'Technology', 'ZM': 'Technology', 'COIN': 'Technology', 'DASH': 'Technology',
    'RBLX': 'Technology', 'U': 'Technology', 'CFLT': 'Technology', 'S': 'Technology',
    'WK': 'Technology', 'CWAN': 'Technology', 'GTLB': 'Technology', 'ESTC': 'Technology',
    'PD': 'Technology', 'FROG': 'Technology', 'AI': 'Technology',
    # Semiconductors
    'AVGO': 'Technology', 'TXN': 'Technology', 'QCOM': 'Technology', 'AMD': 'Technology',
    'INTC': 'Technology', 'AMAT': 'Technology', 'ADI': 'Technology', 'LRCX': 'Technology',
    'KLAC': 'Technology', 'MRVL': 'Technology', 'NXPI': 'Technology', 'MCHP': 'Technology',
    'ON': 'Technology', 'MPWR': 'Technology', 'ENTG': 'Technology', 'TER': 'Technology',
    'SMCI': 'Technology', 'ANET': 'Technology', 'DELL': 'Technology', 'HPQ': 'Technology',
    'HPE': 'Technology', 'STX': 'Technology', 'WDC': 'Technology', 'GLW': 'Technology',
    'ZBRA': 'Technology', 'TRMB': 'Technology', 'KEYS': 'Technology', 'CTSH': 'Technology',
    'MSI': 'Technology', 'FICO': 'Technology',
    # Payments / Fintech (classified as Technology)
    'V': 'Technology', 'MA': 'Technology', 'PYPL': 'Technology', 'FIS': 'Technology',
    'FISV': 'Technology', 'GPN': 'Technology', 'PAYX': 'Technology', 'BR': 'Technology',
    'SNOW': 'Technology', 'PLTR': 'Technology',
    # Quantum Computing
    'IONQ': 'Technology', 'RGTI': 'Technology', 'ARQQ': 'Technology',

    # ═══════════════════════════════════════════════════════
    # CONSUMER DISCRETIONARY
    # ═══════════════════════════════════════════════════════
    'AMZN': 'Consumer Discretionary', 'TSLA': 'Consumer Discretionary',
    'HD': 'Consumer Discretionary', 'LOW': 'Consumer Discretionary',
    'NKE': 'Consumer Discretionary', 'SBUX': 'Consumer Discretionary',
    'MCD': 'Consumer Discretionary', 'CMG': 'Consumer Discretionary',
    'TJX': 'Consumer Discretionary', 'ROST': 'Consumer Discretionary',
    'BURL': 'Consumer Discretionary', 'BKNG': 'Consumer Discretionary',
    'ABNB': 'Consumer Discretionary', 'EXPE': 'Consumer Discretionary',
    'HLT': 'Consumer Discretionary', 'MAR': 'Consumer Discretionary',
    'IHG': 'Consumer Discretionary', 'RCL': 'Consumer Discretionary',
    'CCL': 'Consumer Discretionary', 'NCLH': 'Consumer Discretionary',
    'DIS': 'Consumer Discretionary', 'NFLX': 'Consumer Discretionary',
    'LULU': 'Consumer Discretionary', 'DECK': 'Consumer Discretionary',
    'ONON': 'Consumer Discretionary', 'CROX': 'Consumer Discretionary',
    'COLM': 'Consumer Discretionary', 'RL': 'Consumer Discretionary',
    'TPR': 'Consumer Discretionary', 'PVH': 'Consumer Discretionary',
    'VFC': 'Consumer Discretionary',
    'GM': 'Consumer Discretionary', 'F': 'Consumer Discretionary',
    'HMC': 'Consumer Discretionary', 'TM': 'Consumer Discretionary',
    'BBY': 'Consumer Discretionary', 'TSCO': 'Consumer Discretionary',
    'DG': 'Consumer Discretionary', 'DLTR': 'Consumer Discretionary',
    'FIVE': 'Consumer Discretionary', 'ULTA': 'Consumer Discretionary',
    'RH': 'Consumer Discretionary', 'WSM': 'Consumer Discretionary',
    'DKS': 'Consumer Discretionary', 'BOOT': 'Consumer Discretionary',
    'DRI': 'Consumer Discretionary', 'YUM': 'Consumer Discretionary',
    'DPZ': 'Consumer Discretionary', 'TXRH': 'Consumer Discretionary',
    'EAT': 'Consumer Discretionary', 'CAKE': 'Consumer Discretionary',
    'WEN': 'Consumer Discretionary', 'QSR': 'Consumer Discretionary',
    'BLMN': 'Consumer Discretionary', 'SHAK': 'Consumer Discretionary',
    'CAVA': 'Consumer Discretionary', 'BROS': 'Consumer Discretionary',
    'CNK': 'Consumer Discretionary', 'WYNN': 'Consumer Discretionary',
    'LVS': 'Consumer Discretionary', 'MGM': 'Consumer Discretionary',
    'ROKU': 'Consumer Discretionary', 'TTWO': 'Consumer Discretionary',
    'EA': 'Consumer Discretionary', 'UBER': 'Consumer Discretionary',
    'LYFT': 'Consumer Discretionary', 'POOL': 'Consumer Discretionary',
    'GPC': 'Consumer Discretionary', 'IPAR': 'Consumer Discretionary',
    'NWL': 'Consumer Discretionary',
    # EV
    'RIVN': 'Consumer Discretionary', 'LCID': 'Consumer Discretionary',
    'NIO': 'Consumer Discretionary', 'XPEV': 'Consumer Discretionary',
    'LI': 'Consumer Discretionary',

    # ═══════════════════════════════════════════════════════
    # CONSUMER STAPLES
    # ═══════════════════════════════════════════════════════
    'KO': 'Consumer Staples', 'PEP': 'Consumer Staples', 'PG': 'Consumer Staples',
    'COST': 'Consumer Staples', 'WMT': 'Consumer Staples', 'CL': 'Consumer Staples',
    'KMB': 'Consumer Staples', 'CHD': 'Consumer Staples', 'CLX': 'Consumer Staples',
    'MDLZ': 'Consumer Staples', 'KHC': 'Consumer Staples', 'GIS': 'Consumer Staples',
    'CPB': 'Consumer Staples', 'SJM': 'Consumer Staples', 'CAG': 'Consumer Staples',
    'MKC': 'Consumer Staples', 'HSY': 'Consumer Staples', 'TSN': 'Consumer Staples',
    'HRL': 'Consumer Staples', 'MNST': 'Consumer Staples', 'KDP': 'Consumer Staples',
    'STZ': 'Consumer Staples', 'TAP': 'Consumer Staples', 'BF-B': 'Consumer Staples',
    'PM': 'Consumer Staples', 'MO': 'Consumer Staples', 'EL': 'Consumer Staples',
    'KR': 'Consumer Staples', 'SYY': 'Consumer Staples', 'TGT': 'Consumer Staples',
    'BJ': 'Consumer Staples', 'CASY': 'Consumer Staples', 'FLO': 'Consumer Staples',
    'CALM': 'Consumer Staples', 'JJSF': 'Consumer Staples', 'SMPL': 'Consumer Staples',
    'GO': 'Consumer Staples', 'ELF': 'Consumer Staples',

    # ═══════════════════════════════════════════════════════
    # HEALTHCARE
    # ═══════════════════════════════════════════════════════
    'UNH': 'Healthcare', 'JNJ': 'Healthcare', 'LLY': 'Healthcare', 'ABBV': 'Healthcare',
    'MRK': 'Healthcare', 'PFE': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare',
    'DHR': 'Healthcare', 'AMGN': 'Healthcare', 'BMY': 'Healthcare', 'GILD': 'Healthcare',
    'VRTX': 'Healthcare', 'REGN': 'Healthcare', 'ISRG': 'Healthcare', 'SYK': 'Healthcare',
    'BSX': 'Healthcare', 'MDT': 'Healthcare', 'BDX': 'Healthcare', 'EW': 'Healthcare',
    'IDXX': 'Healthcare', 'DXCM': 'Healthcare', 'IQV': 'Healthcare', 'ZBH': 'Healthcare',
    'BAX': 'Healthcare', 'HOLX': 'Healthcare', 'STE': 'Healthcare', 'RMD': 'Healthcare',
    'ALGN': 'Healthcare', 'PODD': 'Healthcare', 'HCA': 'Healthcare', 'HUM': 'Healthcare',
    'CNC': 'Healthcare', 'CI': 'Healthcare', 'CVS': 'Healthcare', 'ELV': 'Healthcare',
    'MOH': 'Healthcare', 'BIIB': 'Healthcare', 'ALNY': 'Healthcare', 'MRNA': 'Healthcare',
    'GEHC': 'Healthcare', 'WST': 'Healthcare', 'BRKR': 'Healthcare', 'VTRS': 'Healthcare',
    'PBH': 'Healthcare', 'PRGO': 'Healthcare', 'OGN': 'Healthcare', 'TEVA': 'Healthcare',
    'JAZZ': 'Healthcare', 'INCY': 'Healthcare', 'EXAS': 'Healthcare', 'UTHR': 'Healthcare',
    'NBIX': 'Healthcare', 'COO': 'Healthcare', 'TFX': 'Healthcare', 'MMSI': 'Healthcare',
    'HAE': 'Healthcare', 'CRL': 'Healthcare', 'MEDP': 'Healthcare', 'LH': 'Healthcare',
    'DGX': 'Healthcare', 'ENSG': 'Healthcare', 'ACHC': 'Healthcare', 'LMAT': 'Healthcare',
    'NVCR': 'Healthcare', 'ICUI': 'Healthcare', 'OMCL': 'Healthcare', 'TECH': 'Healthcare',
    'QDEL': 'Healthcare', 'GMED': 'Healthcare',

    # ═══════════════════════════════════════════════════════
    # FINANCIALS
    # ═══════════════════════════════════════════════════════
    'JPM': 'Financials', 'BAC': 'Financials', 'WFC': 'Financials',
    'GS': 'Financials', 'MS': 'Financials', 'C': 'Financials',
    'AXP': 'Financials', 'BLK': 'Financials', 'SCHW': 'Financials',
    'BRK-B': 'Financials', 'PGR': 'Financials', 'TRV': 'Financials',
    'ALL': 'Financials', 'CB': 'Financials', 'AON': 'Financials',
    'ADP': 'Financials', 'MSCI': 'Financials', 'SPGI': 'Financials',
    'ICE': 'Financials', 'CME': 'Financials', 'MCO': 'Financials',
    'VRSK': 'Financials', 'COF': 'Financials', 'USB': 'Financials',
    'PNC': 'Financials', 'TFC': 'Financials', 'BK': 'Financials',
    'STT': 'Financials', 'MTB': 'Financials', 'FITB': 'Financials',
    'HBAN': 'Financials', 'RF': 'Financials', 'KEY': 'Financials',
    'CFG': 'Financials', 'ZION': 'Financials', 'BX': 'Financials',
    'KKR': 'Financials', 'APO': 'Financials', 'ARES': 'Financials',
    'TROW': 'Financials', 'IVZ': 'Financials', 'BEN': 'Financials',
    'NDAQ': 'Financials', 'CBOE': 'Financials', 'MKTX': 'Financials',
    'AIG': 'Financials', 'MET': 'Financials', 'PRU': 'Financials',
    'AFL': 'Financials', 'WTW': 'Financials', 'CINF': 'Financials',
    'RYAN': 'Financials', 'ERIE': 'Financials', 'WAL': 'Financials',
    'WTFC': 'Financials', 'UBSI': 'Financials', 'ONB': 'Financials',
    'UMBF': 'Financials', 'FFIN': 'Financials', 'CBSH': 'Financials',
    'FULT': 'Financials', 'BPOP': 'Financials', 'OZK': 'Financials',
    'SFNC': 'Financials', 'FHN': 'Financials', 'FNF': 'Financials',
    'CNA': 'Financials', 'KNSL': 'Financials', 'HIG': 'Financials',
    'LPLA': 'Financials', 'GL': 'Financials', 'AIZ': 'Financials',
    'AJG': 'Financials', 'WRB': 'Financials', 'SIGI': 'Financials',
    'RLI': 'Financials', 'AFG': 'Financials', 'MMC': 'Financials',

    # ═══════════════════════════════════════════════════════
    # INDUSTRIALS
    # ═══════════════════════════════════════════════════════
    'GE': 'Industrials', 'CAT': 'Industrials', 'DE': 'Industrials',
    'HON': 'Industrials', 'BA': 'Industrials', 'RTX': 'Industrials',
    'LMT': 'Industrials', 'NOC': 'Industrials', 'GD': 'Industrials',
    'LHX': 'Industrials', 'TDG': 'Industrials', 'HWM': 'Industrials',
    'HEI': 'Industrials', 'TXT': 'Industrials', 'UNP': 'Industrials',
    'UPS': 'Industrials', 'FDX': 'Industrials', 'NSC': 'Industrials',
    'EMR': 'Industrials', 'ITW': 'Industrials', 'MMM': 'Industrials',
    'ETN': 'Industrials', 'PH': 'Industrials', 'ROK': 'Industrials',
    'DOV': 'Industrials', 'IR': 'Industrials', 'XYL': 'Industrials',
    'FLS': 'Industrials', 'ROP': 'Industrials', 'CMI': 'Industrials',
    'PCAR': 'Industrials', 'OSK': 'Industrials', 'FAST': 'Industrials',
    'CSX': 'Industrials', 'ODFL': 'Industrials', 'SAIA': 'Industrials',
    'XPO': 'Industrials', 'JBHT': 'Industrials', 'CHRW': 'Industrials',
    'URI': 'Industrials', 'VMC': 'Industrials', 'MLM': 'Industrials',
    'GNRC': 'Industrials', 'AME': 'Industrials', 'TT': 'Industrials',
    'HUBB': 'Industrials', 'PWR': 'Industrials', 'OTIS': 'Industrials',
    'CARR': 'Industrials', 'LDOS': 'Industrials', 'HII': 'Industrials',
    'MTZ': 'Industrials', 'UFPI': 'Industrials', 'AIT': 'Industrials',
    'RRX': 'Industrials', 'LSTR': 'Industrials', 'EXPD': 'Industrials',
    'KNX': 'Industrials', 'ARMK': 'Industrials', 'AOS': 'Industrials',
    'BLD': 'Industrials', 'OC': 'Industrials', 'J': 'Industrials',
    'WCC': 'Industrials', 'MLI': 'Industrials', 'CR': 'Industrials',
    'FN': 'Industrials', 'TILE': 'Industrials', 'AIR': 'Industrials',
    'LPX': 'Industrials', 'MHO': 'Industrials', 'KBH': 'Industrials',
    'TPH': 'Industrials',

    # ═══════════════════════════════════════════════════════
    # ENERGY
    # ═══════════════════════════════════════════════════════
    'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy',
    'PSX': 'Energy', 'VLO': 'Energy', 'MPC': 'Energy', 'SLB': 'Energy',
    'OXY': 'Energy', 'FANG': 'Energy', 'DVN': 'Energy', 'HAL': 'Energy',
    'BKR': 'Energy', 'APA': 'Energy', 'CTRA': 'Energy',
    'WMB': 'Energy', 'KMI': 'Energy', 'OKE': 'Energy', 'LNG': 'Energy',
    'TRGP': 'Energy', 'EPD': 'Energy', 'ET': 'Energy', 'NOV': 'Energy',
    'FTI': 'Energy', 'CHRD': 'Energy', 'CNX': 'Energy', 'AR': 'Energy',
    'PR': 'Energy', 'MGY': 'Energy', 'SM': 'Energy', 'MTDR': 'Energy',
    'BTU': 'Energy', 'ARLP': 'Energy', 'VAL': 'Energy', 'RIG': 'Energy',
    'HP': 'Energy',
    # Clean Energy
    'ENPH': 'Energy', 'SEDG': 'Energy', 'RUN': 'Energy',
    'PLUG': 'Energy', 'FCEL': 'Energy', 'BE': 'Energy',
    'BLDP': 'Energy', 'CHPT': 'Energy', 'ENVX': 'Energy', 'QS': 'Energy',

    # ═══════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════
    'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'AEP': 'Utilities',
    'EXC': 'Utilities', 'XEL': 'Utilities', 'SRE': 'Utilities', 'D': 'Utilities',
    'ED': 'Utilities', 'EIX': 'Utilities', 'PEG': 'Utilities', 'WEC': 'Utilities',
    'ES': 'Utilities', 'FE': 'Utilities', 'AES': 'Utilities', 'PCG': 'Utilities',
    'CMS': 'Utilities', 'EVRG': 'Utilities', 'NI': 'Utilities', 'PNW': 'Utilities',
    'AEE': 'Utilities', 'CNP': 'Utilities', 'DTE': 'Utilities', 'ETR': 'Utilities',
    'PPL': 'Utilities', 'LNT': 'Utilities', 'AWK': 'Utilities', 'AWR': 'Utilities',
    'WTRG': 'Utilities', 'ATO': 'Utilities',

    # ═══════════════════════════════════════════════════════
    # COMMUNICATION SERVICES
    # ═══════════════════════════════════════════════════════
    'T': 'Communication Services', 'VZ': 'Communication Services',
    'TMUS': 'Communication Services', 'CMCSA': 'Communication Services',
    'CHTR': 'Communication Services', 'WBD': 'Communication Services',
    'FOXA': 'Communication Services', 'FOX': 'Communication Services',
    'OMC': 'Communication Services', 'NYT': 'Communication Services',
    'NWSA': 'Communication Services', 'SIRI': 'Communication Services',

    # ═══════════════════════════════════════════════════════
    # MATERIALS
    # ═══════════════════════════════════════════════════════
    'LIN': 'Materials', 'APD': 'Materials', 'SHW': 'Materials', 'ECL': 'Materials',
    'NEM': 'Materials', 'FCX': 'Materials', 'DD': 'Materials', 'DOW': 'Materials',
    'EMN': 'Materials', 'ALB': 'Materials', 'FMC': 'Materials', 'IFF': 'Materials',
    'PPG': 'Materials', 'RPM': 'Materials', 'SEE': 'Materials', 'AVY': 'Materials',
    'PKG': 'Materials', 'IP': 'Materials', 'SCCO': 'Materials', 'AA': 'Materials',
    'NUE': 'Materials', 'STLD': 'Materials', 'RS': 'Materials', 'CLF': 'Materials',
    'HUN': 'Materials', 'AXTA': 'Materials', 'NGVT': 'Materials', 'SLGN': 'Materials',
    'CCK': 'Materials', 'AMCR': 'Materials', 'SON': 'Materials', 'GPK': 'Materials',
    'AEM': 'Materials', 'CMC': 'Materials', 'MT': 'Materials', 'TECK': 'Materials',
    'KWR': 'Materials',

    # ═══════════════════════════════════════════════════════
    # REAL ESTATE
    # ═══════════════════════════════════════════════════════
    'AMT': 'Real Estate', 'PLD': 'Real Estate', 'EQIX': 'Real Estate',
    'PSA': 'Real Estate', 'O': 'Real Estate', 'WELL': 'Real Estate',
    'AVB': 'Real Estate', 'EQR': 'Real Estate', 'DLR': 'Real Estate',
    'SBAC': 'Real Estate', 'CCI': 'Real Estate', 'VICI': 'Real Estate',
    'VTR': 'Real Estate', 'EXR': 'Real Estate', 'MAA': 'Real Estate',
    'UDR': 'Real Estate', 'ESS': 'Real Estate', 'CPT': 'Real Estate',
    'REG': 'Real Estate', 'KIM': 'Real Estate', 'BXP': 'Real Estate',
    'VNO': 'Real Estate', 'SLG': 'Real Estate', 'CUBE': 'Real Estate',
    'NSA': 'Real Estate', 'REXR': 'Real Estate', 'FR': 'Real Estate',
    'STAG': 'Real Estate', 'TRNO': 'Real Estate', 'SUI': 'Real Estate',
    'ELS': 'Real Estate', 'BRX': 'Real Estate', 'NNN': 'Real Estate',
    'ADC': 'Real Estate', 'HIW': 'Real Estate', 'CUZ': 'Real Estate',
    'CTRE': 'Real Estate', 'DOC': 'Real Estate', 'HR': 'Real Estate',
    'LTC': 'Real Estate', 'FRT': 'Real Estate',
}


def get_sector(symbol: str) -> str:
    """Look up sector for a stock symbol. Returns 'Unknown' if not found."""
    return SECTOR_MAP.get(symbol, 'Unknown')
