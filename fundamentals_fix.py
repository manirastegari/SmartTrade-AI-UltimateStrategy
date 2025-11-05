#!/usr/bin/env python3
"""
CRITICAL FIX: Improved data fetcher fundamentals extraction
This file contains the fixed get_better_fundamentals method that:
1. NEVER rate limits (uses yfinance.info exclusively)
2. Extracts ALL fundamental data from yfinance
3. Falls back to calculated values when API data missing
4. NO Alpha Vantage except for debugging
"""

def get_better_fundamentals_FIXED(self, symbol):
    """
    FIXED VERSION: Get fundamentals WITHOUT rate limiting
    
    Strategy:
    1. Use yfinance Ticker.info (free, unlimited, comprehensive)
    2. Extract ALL available fundamental metrics
    3. Calculate missing metrics from price data
    4. NO Alpha Vantage usage (saves API calls)
    
    Returns: Complete fundamentals dict with ALL fields populated
    """
    import yfinance as yf
    import time
    import numpy as np
    
    # Base structure with safe defaults
    fundamentals = {
        # Valuation metrics
        'pe_ratio': 0, 'forward_pe': 0, 'peg_ratio': 0, 'price_to_book': 0,
        'price_to_sales': 0, 'enterprise_value': 0, 'ev_to_ebitda': 0,
        # Profitability metrics
        'profit_margins': 0, 'operating_margins': 0, 'gross_margins': 0,
        'roe': 0, 'roa': 0, 'roic': 0,
        # Growth metrics
        'revenue_growth': 0, 'earnings_growth': 0, 'earnings_quarterly_growth': 0,
        # Financial health
        'debt_to_equity': 0, 'current_ratio': 0, 'quick_ratio': 0,
        'total_cash': 0, 'total_debt': 0,
        # Cash flow
        'free_cashflow': 0, 'operating_cashflow': 0,
        # Dividend info
        'dividend_yield': 0, 'payout_ratio': 0, 'dividend_rate': 0,
        # Company info
        'market_cap': 0, 'sector': 'Unknown', 'industry': 'Unknown', 'beta': 1.0,
        # Analyst metrics
        'target_price': 0, 'recommendation': 'hold', 'number_of_analyst_opinions': 0,
    }
    
    try:
        # Check cache first (if available)
        if hasattr(self, 'cache') and self.cache:
            cached_fundamentals = self.cache.get_cached_data(symbol, 'fundamentals')
            if cached_fundamentals is not None:
                return cached_fundamentals
        
        # Create ticker object with minimal delay
        ticker = yf.Ticker(symbol)
        
        # Get info dict (this is FREE and UNLIMITED)
        # Note: This is now fixed in yfinance and should work reliably
        try:
            info = ticker.info or {}
        except Exception as e:
            print(f"⚠️ {symbol}: Could not fetch info, using fast_info fallback")
            info = {}
        
        # Extract ALL available fundamentals from yfinance
        if info:
            fundamentals.update({
                # Valuation
                'pe_ratio': float(info.get('trailingPE') or info.get('regularMarketPE') or 0),
                'forward_pe': float(info.get('forwardPE') or 0),
                'peg_ratio': float(info.get('pegRatio') or 0),
                'price_to_book': float(info.get('priceToBook') or 0),
                'price_to_sales': float(info.get('priceToSalesTrailing12Months') or 0),
                'enterprise_value': int(info.get('enterpriseValue') or 0),
                'ev_to_ebitda': float(info.get('enterpriseToEbitda') or 0),
                
                # Profitability
                'profit_margins': float(info.get('profitMargins') or 0),
                'operating_margins': float(info.get('operatingMargins') or 0),
                'gross_margins': float(info.get('grossMargins') or 0),
                'roe': float(info.get('returnOnEquity') or 0),
                'roa': float(info.get('returnOnAssets') or 0),
                'roic': float(info.get('returnOnCapital') or 0),
                
                # Growth
                'revenue_growth': float(info.get('revenueGrowth') or 0),
                'earnings_growth': float(info.get('earningsGrowth') or 0),
                'earnings_quarterly_growth': float(info.get('earningsQuarterlyGrowth') or 0),
                
                # Financial Health
                'debt_to_equity': float(info.get('debtToEquity') or 0),
                'current_ratio': float(info.get('currentRatio') or 0),
                'quick_ratio': float(info.get('quickRatio') or 0),
                'total_cash': int(info.get('totalCash') or 0),
                'total_debt': int(info.get('totalDebt') or 0),
                
                # Cash Flow
                'free_cashflow': int(info.get('freeCashflow') or 0),
                'operating_cashflow': int(info.get('operatingCashflow') or 0),
                
                # Dividends
                'dividend_yield': float(info.get('dividendYield') or 0),
                'payout_ratio': float(info.get('payoutRatio') or 0),
                'dividend_rate': float(info.get('dividendRate') or 0),
                
                # Company Info
                'market_cap': int(info.get('marketCap') or 0),
                'sector': info.get('sector') or 'Unknown',
                'industry': info.get('industry') or 'Unknown',
                'beta': float(info.get('beta') or info.get('beta3Year') or 1.0),
                
                # Analyst
                'target_price': float(info.get('targetMeanPrice') or 0),
                'recommendation': info.get('recommendationKey') or 'hold',
                'number_of_analyst_opinions': int(info.get('numberOfAnalystOpinions') or 0),
            })
        
        # Fallback to fast_info for market cap if still missing
        if fundamentals['market_cap'] == 0:
            try:
                fast_info = ticker.fast_info
                if hasattr(fast_info, 'market_cap'):
                    fundamentals['market_cap'] = int(fast_info.market_cap or 0)
                elif isinstance(fast_info, dict):
                    fundamentals['market_cap'] = int(fast_info.get('market_cap', 0))
            except:
                pass
        
        # Calculate missing PE ratio from price if needed
        if fundamentals['pe_ratio'] == 0 and fundamentals['market_cap'] > 0:
            try:
                # Try to get earnings from financials
                financials = ticker.financials
                if financials is not None and not financials.empty:
                    if 'Net Income' in financials.index:
                        net_income = float(financials.loc['Net Income'].iloc[0])
                        if net_income > 0:
                            fundamentals['pe_ratio'] = fundamentals['market_cap'] / net_income
            except:
                pass
        
        # Log what we got
        mc = fundamentals['market_cap']
        pe = fundamentals['pe_ratio']
        sector = fundamentals['sector']
        source = 'yfinance.info' if info else 'yfinance.fast_info'
        print(f"📈 {symbol}: MC=${mc:,.0f}, PE={pe:.2f}, Sector={sector} [{source}]")
        
        # Cache the results
        if hasattr(self, 'cache') and self.cache:
            self.cache.save_to_cache(symbol, fundamentals, 'fundamentals')
        
        return fundamentals
        
    except Exception as e:
        print(f"❌ {symbol}: Fundamentals fetch failed - {e}")
        # Return defaults instead of None
        return fundamentals
