#!/usr/bin/env python3
"""
Questrade TFSA Valid Stock Universe
ONLY stocks that are:
1. Tradeable on Questrade
2. Have valid data
3. Liquid (high volume)
4. Not delisted/acquired
"""

def get_questrade_valid_universe():
    """Get 800+ valid, tradeable stocks for Questrade TFSA"""
    
    universe = [
        # === MEGA CAP TECH (Top 20) ===
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL',
        'ADBE', 'CRM', 'INTC', 'AMD', 'QCOM', 'CSCO', 'IBM', 'INTU', 'NOW', 'ACN',
        
        # === LARGE CAP TECH ===
        'TXN', 'AMAT', 'ADI', 'LRCX', 'KLAC', 'SNPS', 'CDNS', 'PANW', 'ANET', 'MU',
        'MRVL', 'MCHP', 'NXPI', 'ON', 'SWKS', 'QRVO', 'MPWR', 'ENTG', 'TER', 'STX',
        'WDC', 'SMCI', 'TSM', 'ASML', 'UMC', 'GFS', 'SLAB', 'CRUS', 'DIOD', 'SITM',
        
        # === SOFTWARE & CLOUD ===
        'MSFT', 'ORCL', 'CRM', 'ADBE', 'INTU', 'NOW', 'WDAY', 'TEAM', 'DDOG', 'SNOW',
        'NET', 'ZS', 'CRWD', 'OKTA', 'MDB', 'ESTC', 'PATH', 'CFLT', 'CYBR', 'TENB',
        'S', 'BOX', 'DBX', 'DOCN', 'DOMO', 'DT', 'DV', 'BILL', 'BL', 'ASAN',
        
        # === SEMICONDUCTORS ===
        'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MU',
        'MRVL', 'MCHP', 'ADI', 'NXPI', 'ON', 'SWKS', 'QRVO', 'MPWR', 'CRUS', 'SLAB',
        'DIOD', 'SITM', 'SYNA', 'VECO', 'UCTT', 'TTMI', 'RMBS', 'PLAB', 'CEVA', 'MXL',
        
        # === HEALTHCARE & BIOTECH ===
        'LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'AMGN', 'PFE',
        'ISRG', 'SYK', 'VRTX', 'REGN', 'BSX', 'MDT', 'BDX', 'EW', 'GILD', 'ZTS',
        'HCA', 'IQV', 'HUM', 'CNC', 'MRNA', 'CI', 'BIIB', 'ALNY', 'ILMN', 'IDXX',
        'RMD', 'ALGN', 'WST', 'BAX', 'STE', 'PODD', 'COO', 'WAT', 'TECH', 'BMRN',
        'UTHR', 'VTRS', 'NBIX', 'SRPT', 'CRL', 'MEDP', 'MMSI', 'NTRA', 'ALKS', 'PBH',
        'LIVN', 'PRGO', 'OGN', 'XRAY', 'NVST', 'QDEL', 'TNDM', 'CNMD', 'ATRC', 'LMAT',
        'NVCR', 'CERT', 'OMCL', 'ANGO', 'VCYT', 'AORT', 'ANIK', 'AVNS', 'OFIX', 'SRDX',
        'TCMD', 'VREX', 'ARGX', 'ASND', 'ABVX', 'ACLX', 'PTGX', 'OMER', 'BEAM',
        
        # === FINANCIALS ===
        'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'SCHW', 'C', 'BLK',
        'BX', 'PNC', 'USB', 'TFC', 'COF', 'BK', 'STT', 'MTB', 'RF', 'SYF',
        'CFG', 'KEY', 'NTRS', 'EG', 'CINF', 'WRB', 'L', 'AIZ', 'PRI', 'UNM',
        'LNC', 'AGO', 'RGA', 'AXS', 'ORI', 'THG', 'KNSL', 'SIGI', 'RLI', 'AFG',
        'CNA', 'RNR', 'APO', 'AJG', 'AON', 'ARES', 'BRO', 'RYAN',
        
        # === ENERGY ===
        'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'OXY', 'VLO', 'FANG',
        'WMB', 'KMI', 'DVN', 'OKE', 'BKR', 'HAL', 'CTRA', 'TPL', 'APA', 'AR',
        'MTDR', 'MUR', 'CHRD', 'SM', 'CNX', 'NOG', 'KOS', 'TALO', 'CRK',
        
        # === UTILITIES ===
        'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'D', 'PCG', 'EXC', 'ED', 'XEL',
        'EIX', 'PEG', 'WEC', 'AWK', 'CNP', 'AEE', 'CMS', 'NI', 'PNW', 'OGE',
        'POR', 'OTTR', 'ALE', 'BKH', 'NWE', 'AVA', 'SR', 'UGI', 'NJR', 'SWX',
        'OGS', 'CPK',
        
        # === CONSUMER DISCRETIONARY ===
        'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'BKNG',
        'LULU', 'ULTA', 'BBY', 'POOL', 'TSCO', 'DKS', 'CASY', 'WSM', 'CROX', 'BURL',
        'CALM', 'SMPL', 'USNA', 'ROST', 'DLTR', 'DG', 'COST', 'WMT',
        
        # === CONSUMER STAPLES ===
        'PG', 'KO', 'PEP', 'COST', 'WMT', 'MDLZ', 'K', 'GIS', 'CPB', 'SJM',
        'CAG', 'MKC', 'CLX', 'CHD', 'KMB', 'CL', 'KHC', 'HSY',
        
        # === INDUSTRIALS ===
        'CAT', 'DE', 'HON', 'GE', 'RTX', 'LMT', 'NOC', 'GD', 'TDG', 'LHX',
        'HWM', 'TXT', 'CW', 'WAB', 'SAIA', 'ODFL', 'XPO', 'KNX', 'ARCB', 'SNDR',
        'MRTN', 'ULH', 'CVLG', 'J',
        
        # === MATERIALS ===
        'LIN', 'APD', 'SHW', 'ECL', 'DD', 'DOW', 'FCX', 'NEM', 'NUE', 'STLD',
        
        # === REAL ESTATE ===
        'AMT', 'PLD', 'EQIX', 'PSA', 'SPG', 'O', 'WELL', 'DLR', 'AVB', 'EQR',
        
        # === COMMUNICATION SERVICES ===
        'GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'CHTR', 'EA', 'TTWO',
        'RBLX', 'MTCH', 'PINS', 'SNAP', 'ROKU', 'SPOT',
        
        # === EMERGING TECH ===
        'AI', 'PLTR', 'SOUN', 'BBAI', 'SYM', 'AEVA', 'AEHR', 'AOSL', 'FORM', 'POWI',
        'SMTC', 'VICR', 'PDFS', 'ADEA', 'LASR', 'AAOI', 'QUIK', 'MRAM', 'ATOM', 'PRSO',
        'SKYT', 'NVEC', 'POET', 'PXLW', 'SQNS',
        
        # === CLEAN ENERGY ===
        'BE', 'FSLR', 'ENPH', 'RUN', 'SEDG', 'SPWR', 'CSIQ', 'MAXN', 'ARRY', 'EVGO',
        'CHPT', 'BLNK', 'BLDP', 'FCEL', 'PLUG', 'LCID', 'RIVN', 'QS',
        
        # === CANADIAN STOCKS (Questrade-tradeable) ===
        'RY.TO', 'TD.TO', 'BMO.TO', 'BNS.TO', 'CM.TO', 'NA.TO', 'TRP.TO', 'KXS.TO',
        'POW.TO', 'ANRG.TO',
        
        # === ADDITIONAL HIGH-QUALITY STOCKS ===
        'MSCI', 'SPGI', 'MCO', 'FIS', 'FISV', 'GPN', 'FLT', 'JKHY', 'NDAQ', 'CME',
        'ICE', 'MKTX', 'CBOE', 'KEYS', 'FICO', 'GLW', 'GDDY', 'PTC', 'NTAP', 'ENPH',
        'VRSN', 'GEN', 'AKAM', 'TRMB', 'ZBRA', 'TYL', 'SSNC', 'BR', 'EPAM', 'GWRE',
        'BSY', 'MANH', 'CVLT', 'ENV', 'BLKB', 'ALRM', 'AGYS', 'APPF', 'ACIW', 'ALKT',
        'APP', 'ATEN', 'AVPT', 'BASE', 'BMBL', 'BRZE', 'CXM', 'DFIN', 'DAKT', 'KNSA',
        'RRX', 'ERJ', 'STRL', 'SNEX', 'AWI', 'WTS', 'DDS', 'VERI', 'SNYR', 'MYSE',
        'RDZN', 'TLSA', 'PVLA', 'OKYO', 'KARO',
        
        # === ADDITIONAL SEMICONDUCTORS ===
        'AMAT', 'LRCX', 'KLAC', 'MU', 'MRVL', 'MCHP', 'ADI', 'NXPI', 'ON', 'SWKS',
        'QRVO', 'MPWR', 'CRUS', 'SLAB', 'DIOD', 'SITM', 'SYNA', 'VECO', 'UCTT', 'TTMI',
        'RMBS', 'PLAB', 'CEVA', 'MXL',
        
        # === ADDITIONAL SOFTWARE ===
        'WDAY', 'TEAM', 'HUBS', 'ZS', 'MDB', 'NET', 'DDOG', 'GTLB', 'ESTC', 'PATH',
        'CFLT', 'CYBR', 'TENB', 'S', 'OKTA', 'BOX', 'QTWO', 'ALKT', 'ENV', 'ALRM',
        'AGYS', 'ACIW', 'APPF', 'ASAN', 'ATEN', 'AVPT', 'BASE', 'BILL', 'BL', 'BMBL',
        'BRZE', 'CXM', 'DBX', 'DFIN', 'DOCN', 'DOMO', 'DT', 'DV',
        
        # === ADDITIONAL HEALTHCARE ===
        'GEHC', 'HOLX', 'INCY', 'EXAS', 'GMED', 'BRKR', 'EXEL', 'IONS', 'GKOS', 'INSP',
        'HAE', 'ENOV', 'ICUI',
        
        # === ADDITIONAL FINANCIALS ===
        'FITB', 'HBAN', 'GL', 'FAF', 'FNF', 'ERIE',
        
        # === ADDITIONAL CONSUMER ===
        'FIVE', 'GPC', 'JJSF', 'LANC',
        
        # === ADDITIONAL INDUSTRIALS ===
        'HEI', 'HTLD',
        
        # === ADDITIONAL MATERIALS ===
        'IFF', 'PPG', 'EMN', 'AA', 'X',
        
        # === ADDITIONAL REAL ESTATE ===
        'CBRE', 'CSGP', 'IRM',
        
        # === ADDITIONAL COMMUNICATION ===
        'PARA', 'WBD', 'FOXA', 'FOX', 'NWSA', 'NWS', 'NYT', 'LYV', 'MSGS', 'MSG',
        
        # === ADDITIONAL ENERGY ===
        'HES', 'EQT',
        
        # === ADDITIONAL UTILITIES ===
        'EVRG', 'IDA',
        
        # === ADDITIONAL TECH ===
        'FTNT', 'IT', 'ADSK', 'CTSH', 'AKAM', 'JKHY', 'TRMB', 'ZBRA', 'TYL', 'SSNC',
        'BR', 'EPAM', 'GWRE', 'BSY', 'MANH', 'CVLT', 'ENV', 'BLKB', 'ALRM',
    ]
    
    # Ensure premium institutional-grade universe is TFSA-approved by default
    try:
        from premium_quality_universe import get_premium_universe
        universe.extend(get_premium_universe())
    except Exception:
        pass
    
    # Remove duplicates and sort
    universe = sorted(list(set(universe)))
    
    # Remove any invalid symbols found in logs
    invalid_symbols = {
        'WOLF', 'ANSS', 'ALTR', 'ATRI', 'AXNX', 'AYX', 'AZPN', 'BIGC', 'C3AI', 'CDAY',
        'CHK', 'CVW.TO', 'DSKE', 'DSPG', 'EGHT', 'ENFN', 'ETWO', 'EXTR', 'FCNCA', 'FIVN',
        'FLYW', 'FORG', 'FOUR', 'FRGE', 'FROG', 'FRSH', 'GBTG', 'GOEV', 'GPOR', 'GRID.TO',
        'GSIT', 'HALO', 'HDL', 'HIMX', 'HYLN', 'INDI', 'IOT', 'JAMF', 'JKS', 'JNMR',
        'JNPR', 'LANC', 'MIC.TO', 'MRO', 'NARI', 'NKLA', 'NOVA', 'NPTN', 'OIIM', 'PTSI',
        'RESN', 'SGH', 'SILK', 'SJI', 'SMAR', 'TMX.TO', 'Y', 'VIXY'
    }
    
    universe = [s for s in universe if s not in invalid_symbols]
    
    return universe

if __name__ == "__main__":
    universe = get_questrade_valid_universe()
    print(f"Questrade Valid Universe: {len(universe)} stocks")
    
    # Count by exchange
    us_stocks = [s for s in universe if not s.endswith('.TO')]
    canadian_stocks = [s for s in universe if s.endswith('.TO')]
    
    print(f"US stocks: {len(us_stocks)}")
    print(f"Canadian stocks: {len(canadian_stocks)}")
    
    # Print first 20
    print(f"\nFirst 20 stocks:")
    for i, stock in enumerate(universe[:20], 1):
        print(f"{i}. {stock}")
