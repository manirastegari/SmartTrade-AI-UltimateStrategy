#!/usr/bin/env python3
"""
Earnings Calendar Filter
Identifies stocks with upcoming earnings to avoid high-risk entry timing

Uses FREE data from Yahoo Finance to detect:
- Upcoming earnings dates
- Recently reported earnings
- Earnings surprise history

Integration: Warns against buying stocks 5 days before/after earnings
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class EarningsCalendarFilter:
    """
    Filter stocks based on earnings timing.
    Helps avoid high-volatility periods around earnings announcements.
    """
    
    # How many days before earnings to avoid buying
    PRE_EARNINGS_BUFFER = 5
    
    # How many days after earnings to wait (let dust settle)
    POST_EARNINGS_BUFFER = 2
    
    def __init__(self, cache_ttl_hours: int = 4):
        """
        Initialize earnings filter.
        
        Args:
            cache_ttl_hours: How long to cache earnings data (hours)
        """
        self._cache: Dict[str, Dict] = {}
        self._cache_ts: Dict[str, datetime] = {}
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
    def _get_cached_or_fetch(self, symbol: str) -> Optional[Dict]:
        """Get earnings data from cache or fetch from Yahoo."""
        now = datetime.now()
        
        # Check cache
        if symbol in self._cache:
            cache_age = now - self._cache_ts.get(symbol, datetime.min)
            if cache_age < self.cache_ttl:
                return self._cache[symbol]
        
        # Fetch from Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            
            # Get calendar (includes earnings date)
            try:
                calendar = ticker.calendar
            except Exception:
                calendar = None
            
            # Get earnings history
            try:
                earnings_history = ticker.earnings_history
            except Exception:
                earnings_history = None
            
            result = {
                'calendar': calendar,
                'earnings_history': earnings_history,
                'fetched_at': now.isoformat(),
            }
            
            # Cache result
            self._cache[symbol] = result
            self._cache_ts[symbol] = now
            
            return result
            
        except Exception as e:
            return None
    
    def get_earnings_info(self, symbol: str) -> Dict:
        """
        Get detailed earnings information for a symbol.
        
        Returns:
            dict with: next_earnings_date, days_until_earnings, 
                      recent_surprises, is_safe_to_buy, warning_message
        """
        result = {
            'symbol': symbol,
            'next_earnings_date': None,
            'days_until_earnings': None,
            'is_safe_to_buy': True,
            'warning_message': None,
            'recent_surprises': [],
            'earnings_quality': 'UNKNOWN',
        }
        
        data = self._get_cached_or_fetch(symbol)
        if not data:
            return result
        
        today = datetime.now().date()
        
        # Parse calendar for next earnings date
        calendar = data.get('calendar')
        if calendar is not None:
            try:
                # Calendar can be DataFrame or dict
                if isinstance(calendar, pd.DataFrame):
                    if 'Earnings Date' in calendar.index:
                        earnings_dates = calendar.loc['Earnings Date']
                        if isinstance(earnings_dates, pd.Series) and len(earnings_dates) > 0:
                            next_date = pd.to_datetime(earnings_dates.iloc[0])
                            if pd.notna(next_date):
                                result['next_earnings_date'] = next_date.strftime('%Y-%m-%d')
                                result['days_until_earnings'] = (next_date.date() - today).days
                elif isinstance(calendar, dict):
                    if 'Earnings Date' in calendar:
                        ed = calendar['Earnings Date']
                        if isinstance(ed, (list, tuple)) and len(ed) > 0:
                            next_date = pd.to_datetime(ed[0])
                            if pd.notna(next_date):
                                result['next_earnings_date'] = next_date.strftime('%Y-%m-%d')
                                result['days_until_earnings'] = (next_date.date() - today).days
            except Exception:
                pass
        
        # Determine if safe to buy
        days_until = result['days_until_earnings']
        if days_until is not None:
            if 0 <= days_until <= self.PRE_EARNINGS_BUFFER:
                result['is_safe_to_buy'] = False
                result['warning_message'] = f"⚠️ Earnings in {days_until} days - HIGH VOLATILITY RISK"
            elif -self.POST_EARNINGS_BUFFER <= days_until < 0:
                result['is_safe_to_buy'] = False
                result['warning_message'] = f"⚠️ Earnings reported {abs(days_until)} days ago - WAIT FOR DUST TO SETTLE"
            elif days_until <= 10:
                result['warning_message'] = f"📅 Earnings approaching in {days_until} days"
        
        # Analyze earnings history for quality
        earnings_history = data.get('earnings_history')
        if earnings_history is not None and isinstance(earnings_history, pd.DataFrame) and len(earnings_history) > 0:
            try:
                # Calculate surprise stats
                if 'epsActual' in earnings_history.columns and 'epsEstimate' in earnings_history.columns:
                    history = earnings_history.dropna(subset=['epsActual', 'epsEstimate'])
                    
                    beats = 0
                    misses = 0
                    surprises = []
                    
                    for _, row in history.head(4).iterrows():  # Last 4 quarters
                        actual = float(row['epsActual'])
                        estimate = float(row['epsEstimate'])
                        
                        if estimate != 0:
                            surprise_pct = ((actual - estimate) / abs(estimate)) * 100
                            surprises.append(round(surprise_pct, 1))
                            
                            if actual > estimate:
                                beats += 1
                            elif actual < estimate:
                                misses += 1
                    
                    result['recent_surprises'] = surprises
                    
                    # Determine earnings quality
                    if beats >= 3:
                        result['earnings_quality'] = 'CONSISTENT_BEATER'
                    elif beats >= 2 and misses == 0:
                        result['earnings_quality'] = 'RELIABLE'
                    elif misses >= 2:
                        result['earnings_quality'] = 'UNRELIABLE'
                    else:
                        result['earnings_quality'] = 'MIXED'
                        
            except Exception:
                pass
        
        return result
    
    def filter_safe_entries(self, symbols: List[str]) -> Tuple[List[str], List[Dict]]:
        """
        Filter list of symbols to those safe to buy (no imminent earnings).
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            (safe_symbols, warnings) - Safe symbols to trade and warnings for filtered ones
        """
        safe = []
        warnings = []
        
        for symbol in symbols:
            info = self.get_earnings_info(symbol)
            
            if info['is_safe_to_buy']:
                safe.append(symbol)
            else:
                warnings.append({
                    'symbol': symbol,
                    'reason': info['warning_message'],
                    'earnings_date': info['next_earnings_date'],
                    'days_until': info['days_until_earnings'],
                })
        
        return safe, warnings
    
    def get_batch_earnings_status(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get earnings status for multiple symbols efficiently.
        
        Returns:
            dict mapping symbol to earnings info
        """
        return {symbol: self.get_earnings_info(symbol) for symbol in symbols}


def get_earnings_filter() -> EarningsCalendarFilter:
    """Get singleton earnings filter instance."""
    return EarningsCalendarFilter()


if __name__ == "__main__":
    # Test the filter
    print("=" * 60)
    print("EARNINGS CALENDAR FILTER - TEST")
    print("=" * 60)
    
    filter = EarningsCalendarFilter()
    
    # Test with some popular stocks
    test_symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA']
    
    print(f"\n📅 Checking earnings for: {test_symbols}")
    print("-" * 60)
    
    for symbol in test_symbols:
        info = filter.get_earnings_info(symbol)
        
        status = "✅ SAFE" if info['is_safe_to_buy'] else "⚠️ AVOID"
        earnings_date = info['next_earnings_date'] or "Unknown"
        days = info['days_until_earnings']
        quality = info['earnings_quality']
        
        print(f"\n{symbol}: {status}")
        print(f"   Next Earnings: {earnings_date} ({days} days)" if days else f"   Next Earnings: {earnings_date}")
        print(f"   Earnings Quality: {quality}")
        if info['recent_surprises']:
            print(f"   Recent Surprises: {info['recent_surprises']}%")
        if info['warning_message']:
            print(f"   {info['warning_message']}")
