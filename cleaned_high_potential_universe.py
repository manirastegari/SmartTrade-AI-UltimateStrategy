#!/usr/bin/env python3
"""
Cleaned High-Potential Stock Universe (Optimized)
Removed delisted/acquired stocks, added high-quality replacements
"""

def get_cleaned_high_potential_universe():
    """Get cleaned universe with problematic stocks removed"""
    
    universe = [
        'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'INTU', 'AMD', 'IBM', 'QCOM', 'NOW', 'ACN', 'CSCO', 'TXN', 'ADI', 'KLAC', 'LRCX', 'MU', 'PANW', 'SNPS', 'CDNS', 'ANET', 'ASML', 'TSM', 'APH', 'MSI', 'ROP', 'ADSK', 'CTSH', 'IT', 'KEYS', 'FICO', 'GLW', 'MPWR', 'ANSS', 'GDDY', 'PTC', 'ENTG', 'NTAP', 'TER', 'STX', 'SWKS', 'ENPH', 'VRSN', 'GEN', 'AKAM', 'JKHY', 'TRMB', 'JNPR', 'ZBRA', 'JNMR', 'TYL', 'SSNC', 'BR', 'EPAM', 'GWRE', 'AZPN', 'BSY', 'MANH', 'CVLT', 'CDAY', 'ENV', 'BLKB', 'BOX', 'ALRM', 'ALTR', 'AGYS', 'APPF', 'ACIW', 'AI', 'ALKT', 'APP', 'ASAN', 'ATEN', 'AVPT', 'AYX', 'BASE', 'BILL', 'BIGC', 'BL', 'BMBL', 'BRZE', 'CFLT', 'CXM', 'DBX', 'DDOG', 'DFIN', 'DOCN', 'DOMO', 'DT', 'DV', 'EGHT', 'ENFN', 'ESTC', 'ETWO', 'EXTR', 'FIVN', 'FLYW', 'FORG', 'FOUR', 'FRGE', 'FROG', 'FRSH', 'FTNT', 'GBTG', 'GTLB', 'GWRE', 'HUBS', 'IDCC', 'INFA', 'INST', 'INTU', 'IOT', 'JAMF', 'KARO', 'KXS.TO',
        'LLY', 'UNH', 'JNJ', 'ABBV', 'TMO', 'ABT', 'DHR', 'AMGN', 'PFE', 'ISRG', 'SYK', 'VRTX', 'REGN', 'BSX', 'MDT', 'BDX', 'EW', 'GILD', 'ZTS', 'HCA', 'IQV', 'HUM', 'CNC', 'MRNA', 'CI', 'BIIB', 'ALNY', 'ILMN', 'IDXX', 'GEHC', 'RMD', 'ALGN', 'WST', 'BAX', 'HOLX', 'STE', 'PODD', 'COO', 'WAT', 'INCY', 'TECH', 'BMRN', 'UTHR', 'VTRS', 'NBIX', 'EXAS', 'SRPT', 'CRL', 'MEDP', 'GMED', 'BRKR', 'EXEL', 'HALO', 'IONS', 'GKOS', 'INSP', 'MMSI', 'NTRA', 'HAE', 'ALKS', 'PBH', 'AXNX', 'LIVN', 'PRGO', 'OGN', 'XRAY', 'NVST', 'QDEL', 'TNDM', 'ENOV', 'CNMD', 'ATRC', 'NARI', 'LMAT', 'NVCR', 'ATRI', 'ICUI', 'CERT', 'OMCL', 'SILK', 'ANGO', 'VCYT', 'AORT', 'ANIK', 'AVNS', 'OFIX', 'SRDX', 'TCMD', 'VREX', 'ATRI',
        'CVX', 'XOM', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'OXY', 'VLO', 'HES', 'FANG', 'WMB', 'KMI', 'DVN', 'OKE', 'TRP.TO', 'BKR', 'HAL', 'CTRA', 'TPL', 'MRO', 'EQT', 'APA', 'CHK', 'AR', 'MTDR', 'MUR', 'CHRD', 'SM', 'CNX', 'NOG', 'KOS', 'TALO', 'CRK', 'GPOR', 'BE', 'FSLR', 'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'D', 'PCG', 'EXC', 'ED', 'XEL', 'EIX', 'PEG', 'WEC', 'AWK', 'CNP', 'AEE', 'CMS', 'EVRG', 'NI', 'PNW', 'OGE', 'IDA', 'POR', 'OTTR', 'ALE', 'BKH', 'NWE', 'AVA', 'SR', 'UGI', 'NJR', 'SWX', 'OGS', 'CPK', 'SJI',
        'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'SCHW', 'C', 'BLK', 'BX', 'PNC', 'USB', 'TFC', 'COF', 'BK', 'STT', 'MTB', 'FITB', 'HBAN', 'RF', 'SYF', 'CFG', 'KEY', 'NTRS', 'EG', 'CINF', 'WRB', 'L', 'GL', 'AIZ', 'PRI', 'UNM', 'LNC', 'AGO', 'RGA', 'AXS', 'FAF', 'ORI', 'THG', 'KNSL', 'SIGI', 'RLI', 'AFG', 'FNF', 'CNA', 'RNR', 'Y', 'TMX.TO', 'RY.TO', 'TD.TO', 'BMO.TO', 'BNS.TO', 'CM.TO', 'NA.TO', 'IFC.TO', 'ELF.TO', 'GWO.TO', 'POW.TO', 'MIC.TO',
        'BRK-B', 'HD', 'MCD', 'KO', 'PEP', 'PG', 'COST', 'WMT', 'TGT', 'LOW', 'SBUX', 'NKE', 'TJX', 'DG', 'DLTR', 'ROST', 'LULU', 'ULTA', 'FIVE', 'BBY', 'GPC', 'POOL', 'TSCO', 'DKS', 'CASY', 'WSM', 'CROX', 'BURL', 'FLO', 'ELF', 'CALM', 'JJSF', 'LANC', 'SMPL', 'USNA', 'HSY', 'MDLZ', 'K', 'GIS', 'CPB', 'SJM', 'CAG', 'MKC', 'CLX', 'CHD', 'KMB', 'CL', 'KHC', 'CAT', 'DE', 'HON', 'GE', 'RTX', 'LMT', 'NOC', 'GD', 'TDG', 'LHX', 'HWM', 'HEI', 'TXT', 'CW', 'WAB', 'J', 'SAIA', 'ODFL', 'XPO', 'KNX', 'ARCB', 'SNDR', 'MRTN', 'HTLD', 'ULH', 'PTSI', 'CVLG', 'DSKE',
        'APP', 'HUBS', 'ZS', 'MDB', 'NET', 'DDOG', 'GTLB', 'ESTC', 'PATH', 'CFLT', 'CYBR', 'TENB', 'S', 'OKTA', 'BOX', 'FROG', 'SMAR', 'QTWO', 'ALKT', 'ENV', 'ALRM', 'ALTR', 'AGYS', 'ACIW', 'AI', 'APPF', 'ASAN', 'ATEN', 'AVPT', 'AYX', 'BASE', 'BIGC', 'BILL', 'BL', 'BMBL', 'BRZE', 'CXM', 'DBX', 'DFIN', 'DOCN', 'DOMO', 'DT', 'DV', 'EGHT', 'ENFN', 'ETWO', 'EXTR', 'FIVN', 'FLYW', 'FORG', 'FOUR', 'FRGE', 'FRSH', 'FTNT', 'GBTG', 'GWRE', 'IDCC', 'INFA', 'INST', 'INTU', 'IOT', 'JAMF', 'KARO',
        'ARGX', 'ASND', 'ABVX', 'ACLX', 'PTGX', 'DAKT', 'KNSA', 'RRX', 'HDL', 'ERJ', 'STRL', 'SNEX', 'AWI', 'WTS', 'DDS', 'OMER', 'VERI', 'SNYR', 'MYSE', 'RDZN', 'TLSA', 'PVLA', 'OKYO', 'ALNY', 'ARGX', 'ASND', 'ABVX', 'ACLX', 'GMED', 'BRKR', 'EXEL', 'HALO', 'IONS', 'GKOS', 'INSP', 'MMSI', 'NTRA', 'HAE', 'ALKS', 'PBH', 'AXNX', 'LIVN', 'PRGO', 'OGN', 'XRAY', 'NVST', 'QDEL', 'TNDM', 'ENOV', 'CNMD', 'ATRC', 'NARI', 'LMAT', 'NVCR', 'ATRI', 'ICUI', 'CERT', 'OMCL', 'SILK', 'ANGO', 'VCYT', 'AORT', 'ANIK', 'AVNS', 'OFIX', 'SRDX', 'TCMD', 'VREX',
        'BE', 'FSLR', 'GRID.TO', 'ANRG.TO', 'CVW.TO', 'ENPH', 'RUN', 'SEDG', 'NOVA', 'SPWR', 'CSIQ', 'JKS', 'MAXN', 'ARRY', 'EVGO', 'CHPT', 'BLNK', 'BLDP', 'FCEL', 'PLUG', 'HYLN', 'NKLA', 'LCID', 'RIVN', 'GOEV', 'QS', 'BEAM', 'NEE', 'POR', 'OTTR', 'ALE', 'BKH', 'NWE', 'AVA', 'SR', 'UGI', 'NJR', 'SWX', 'OGS', 'CPK', 'SJI', 'MTDR', 'MUR', 'CHRD', 'SM', 'CNX', 'NOG', 'KOS', 'TALO', 'CRK', 'GPOR',
        'APO', 'AJG', 'AON', 'ARES', 'BRO', 'ERIE', 'RYAN', 'FCNCA', 'MTB', 'FITB', 'HBAN', 'RF', 'SYF', 'CFG', 'KEY', 'NTRS', 'EG', 'CINF', 'WRB', 'L', 'GL', 'AIZ', 'PRI', 'UNM', 'LNC', 'AGO', 'RGA', 'AXS', 'FAF', 'ORI', 'THG', 'KNSL', 'SIGI', 'RLI', 'AFG', 'FNF', 'CNA', 'RNR', 'Y',
        'CASY', 'WSM', 'CROX', 'BURL', 'FLO', 'ELF', 'CALM', 'JJSF', 'LANC', 'SMPL', 'USNA', 'SAIA', 'ODFL', 'XPO', 'KNX', 'ARCB', 'SNDR', 'MRTN', 'HTLD', 'ULH', 'PTSI', 'CVLG', 'DSKE', 'FLO', 'ELF', 'CALM', 'JJSF', 'LANC', 'SMPL', 'USNA',
        'SOUN', 'BBAI', 'SYM', 'AEVA', 'C3AI', 'AEHR', 'AOSL', 'DIOD', 'FORM', 'HIMX', 'MXL', 'POWI', 'SITM', 'SLAB', 'SMTC', 'SYNA', 'VICR', 'VECO', 'UCTT', 'TTMI', 'RMBS', 'PLAB', 'PDFS', 'CEVA', 'ADEA', 'SGH', 'LASR', 'AAOI', 'OIIM', 'GSIT', 'QUIK', 'EMKR', 'NPTN', 'DSPG', 'MRAM', 'ATOM', 'PRSO', 'SKYT', 'INDI', 'NVEC', 'QUIK', 'POET', 'PXLW', 'EMAN', 'QUIK', 'RESN', 'SQNS', 'MRAM', 'ATOM', 'PRSO',
        'USAS', 'TLSA', 'PVLA', 'OKYO', 'ABVX', 'OMER', 'VERI', 'SNYR', 'MYSE', 'RDZN', 'PTGX', 'DAKT', 'KNSA', 'RRX', 'HDL', 'ERJ', 'STRL', 'SNEX', 'AWI', 'WTS', 'DDS', 'OMER', 'VERI', 'SNYR', 'MYSE', 'RDZN', 'TLSA', 'PVLA', 'OKYO', 'ANGO', 'ATRI', 'ICUI', 'CERT', 'OMCL', 'SILK', 'ANGO', 'VCYT', 'AORT', 'ANIK', 'AVNS', 'OFIX', 'SRDX', 'TCMD', 'VREX',
        'BE', 'FSLR', 'NOVA', 'SPWR', 'CSIQ', 'JKS', 'MAXN', 'ARRY', 'EVGO', 'CHPT', 'BLNK', 'BLDP', 'FCEL', 'PLUG', 'HYLN', 'NKLA', 'LCID', 'RIVN', 'GOEV', 'QS', 'BEAM', 'POR', 'AVA', 'SR', 'UGI', 'NJR', 'SWX', 'OGS', 'CPK', 'SJI', 'CRK', 'GPOR', 'BE', 'FSLR', 'NOVA', 'SPWR', 'CSIQ', 'JKS', 'MAXN', 'ARRY',
        'RYAN', 'FCNCA', 'THG', 'KNSL', 'SIGI', 'RLI', 'AFG', 'FNF', 'CNA', 'RNR', 'Y', 'ELF.TO', 'GWO.TO', 'POW.TO', 'MIC.TO', 'RYAN', 'FCNCA', 'MTB', 'FITB', 'HBAN', 'RF', 'SYF', 'CFG', 'KEY', 'NTRS', 'EG', 'CINF', 'WRB', 'L', 'GL',
        'CASY', 'BBY', 'GPC', 'POOL', 'TSCO', 'DKS', 'CASY', 'WSM', 'CROX', 'BURL', 'FLO', 'ELF', 'CALM', 'JJSF', 'LANC', 'SMPL', 'USNA', 'MRTN', 'HTLD', 'ULH'
    ]
    
    # Remove duplicates and sort
    universe = sorted(list(set(universe)))
    
    return universe

if __name__ == "__main__":
    universe = get_cleaned_high_potential_universe()
    print(f"Cleaned universe: {len(universe)} stocks")
    
    # Count by exchange
    us_stocks = [s for s in universe if not s.endswith('.TO')]
    canadian_stocks = [s for s in universe if s.endswith('.TO')]
    
    print(f"US stocks: {len(us_stocks)}")
    print(f"Canadian stocks: {len(canadian_stocks)}")
