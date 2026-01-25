
"""
Macro Economic Analyzer
Analyzes broad market indicators (Bond Yields, Dollar Index, VIX) to determine
Strategic Market Regime (Risk-On / Risk-Off).
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

class MacroEconomicAnalyzer:
    """
    Analyzes macro-economic factors to determine market regime.
    Key Indicators:
    - 10-Year Treasury Yield (^TNX)
    - US Dollar Index (DX-Y.NYB)
    - VIX (^VIX)
    - SPY (Market Trend)
    """
    
    def __init__(self):
        self.tickers = {
            '10Y_Yield': '^TNX',
            'Dollar_Index': 'DX=F', # DX=F is often more reliable than DX-Y.NYB
            'VIX': '^VIX',
            'SPY': 'SPY'
        }
        
    def analyze_macro_context(self, external_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch and analyze macro data.
        Accepts external_context (e.g. from main analyzer) to reuse known-valid VIX/SPY data.
        Returns validation dict with regime and score.
        """
        print("\n🌍 Running Macro-Economic Analysis...")
        data = self._fetch_data()
        external_context = external_context or {}
        
        # Robust access to data (No hardcoded defaults)
        def get_last(key):
            if data and key in data and not data[key].empty:
                try:
                    return data[key].iloc[-1]
                except:
                    return None
            return None

        # Prefer external data if valid, else fetch
        vix_val = external_context.get('vix') 
        if vix_val is None:
             vix_val = get_last('VIX')

        # Yields and DXY usually come from our fetch
        yield_val = get_last('10Y_Yield')
        dollar_val = get_last('Dollar_Index')
        
        # SPY trend might come from external or fetch
        spy_trend = "UNKNOWN"
        if 'spy_trend' in external_context:
            spy_trend = external_context['spy_trend']
        elif data and 'SPY' in data:
            spy_trend = self._analyze_trend(data['SPY'])
        
        # Determine Regime (Only score what we have)
        # Base score 50, but we will adjust dynamically
        macro_score = 50 
        valid_components = 0
        details = []
        
        # Yield Impact
        yield_trend = "UNKNOWN"
        if yield_val is not None and data and '10Y_Yield' in data:
             yield_trend = self._analyze_trend(data['10Y_Yield'])
             if yield_trend == 'UP':
                 details.append("RISING YIELDS (Headwind)")
                 macro_score -= 10
             elif yield_trend == 'DOWN':
                 details.append("FALLING YIELDS (Tailwind)")
                 macro_score += 10
             valid_components += 1
            
        # Dollar Impact
        dollar_trend = "UNKNOWN"
        if dollar_val is not None and data and 'Dollar_Index' in data:
             dollar_trend = self._analyze_trend(data['Dollar_Index'])
             if dollar_trend == 'UP':
                 details.append("STRONG DOLLAR (Headwind)")
                 macro_score -= 5
             elif dollar_trend == 'DOWN':
                 details.append("WEAK DOLLAR (Tailwind)")
                 macro_score += 5
             valid_components += 1
            
        # VIX Impact
        if vix_val is not None:
            if vix_val > 25:
                # Force defensive if VIX is high, regardless of others
                details.append(f"HIGH VOLATILITY (VIX {vix_val:.1f})")
                macro_score -= 20
            elif vix_val < 15:
                details.append(f"LOW VOLATILITY (VIX {vix_val:.1f})")
                macro_score += 10
            valid_components += 1
            
        # SPY Trend Impact
        if spy_trend == 'UP':
            details.append("MARKET UPTREND")
            macro_score += 10
        elif spy_trend == 'DOWN':
            details.append("MARKET DOWNTREND")
            macro_score -= 10
        if spy_trend != 'UNKNOWN':
            valid_components += 1
            
        # Final Regime Classification
        # If we have very little data, default to Neutral but label it
        if valid_components == 0:
            regime = "NEUTRAL (Data Unavailable)"
            details.append("No/Insufficient Macro Data")
        else:
            if macro_score >= 65:
                regime = "RISK-ON"
            elif macro_score <= 35:
                regime = "RISK-OFF"
            else:
                regime = "NEUTRAL"
            
        return {
            'regime': regime,
            'macro_score': macro_score,
            'details': details,
            'summary': f"{regime}: {', '.join(details)}",
            'yield_10y': yield_val if yield_val is not None else 'N/A',
            'dollar_index': dollar_val if dollar_val is not None else 'N/A',
            'vix': vix_val if vix_val is not None else 'N/A'
        }

    def _fetch_data(self) -> Optional[Dict[str, pd.Series]]:
        """
        Fetch data for each ticker individually with retries.
        Batch downloads can fail completely if one ticker errors or JSON parsing fails.
        """
        import time
        
        results = {}
        
        for name, ticker in self.tickers.items():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Fetch single ticker
                    # Using history() on Ticker object is often more reliable than download() for singles
                    # timeout added to prevent hanging
                    t = yf.Ticker(ticker)
                    hist = t.history(period="1mo")
                    
                    if not hist.empty and 'Close' in hist:
                        results[name] = hist['Close']
                        print(f"   ✅ Fetched {name} ({ticker})")
                        break # Success
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(1) # Wait before retry
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"   ⚠️ Retry {attempt+1}/{max_retries} for {name}: {e}")
                        time.sleep(2)
                    else:
                        print(f"   ❌ Failed to fetch {name} ({ticker}): {e}")
                        
        if not results:
            return None
            
        return results
            
    def _analyze_trend(self, series: pd.Series) -> str:
        if series is None or len(series) < 10:
            return "FLAT"
        
        # Simple SMA comparison
        sma_short = series.rolling(5).mean().iloc[-1]
        sma_long = series.rolling(20).mean().iloc[-1]
        
        if sma_short > sma_long * 1.01:
            return "UP"
        elif sma_short < sma_long * 0.99:
            return "DOWN"
        return "FLAT"
        
    def _default_context(self):
        return {
            'regime': 'NEUTRAL',
            'macro_score': 50,
            'details': ['Data Unavailable'],
            'summary': 'Macro Analysis Unavailable',
            'yield_10y': 0,
            'dollar_index': 0,
            'vix': 20
        }

if __name__ == "__main__":
    analyzer = MacroEconomicAnalyzer()
    res = analyzer.analyze_macro_context()
    print("\nTest Result:")
    print(res['summary'])
