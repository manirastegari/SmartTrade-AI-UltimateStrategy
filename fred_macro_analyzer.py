#!/usr/bin/env python3
"""
FRED Macro Economic Analyzer
Integrates Federal Reserve Economic Data for market timing signals

Uses FREE FRED API to analyze:
- Yield Curve (recession predictor)
- VIX alternative estimates
- Economic momentum indicators
- Inflation signals

API: https://fred.stlouisfed.org/docs/api/fred/
Free tier: 120 requests/minute
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd
import numpy as np


class FREDMacroAnalyzer:
    """
    Fetch and analyze macroeconomic indicators from FRED.
    Provides market timing signals based on economic conditions.
    """
    
    # Key FRED indicators for market timing
    INDICATORS = {
        # Yield Curve (recession predictor)
        'T10Y2Y': 'Treasury 10Y-2Y Spread (Yield Curve)',
        'T10Y3M': 'Treasury 10Y-3M Spread',
        
        # VIX alternatives when direct VIX unavailable
        'VIXCLS': 'CBOE VIX Index',
        
        # Economic momentum
        'UNRATE': 'Unemployment Rate',
        'CPIAUCSL': 'Consumer Price Index (Inflation)',
        'INDPRO': 'Industrial Production Index',
        'PAYEMS': 'Total Nonfarm Payrolls',
        
        # Financial conditions
        'DCOILWTICO': 'Crude Oil WTI Price',
        'GOLDAMGBD228NLBM': 'Gold Price',
        'DGS10': '10-Year Treasury Rate',
        'DGS2': '2-Year Treasury Rate',
        'DFF': 'Federal Funds Rate',
        
        # Credit conditions
        'BAMLH0A0HYM2': 'High Yield Spread (ICE BofA)',
        'DRTSCILM': 'Bank Credit Conditions',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED analyzer.
        
        Args:
            api_key: FRED API key (get free at https://fred.stlouisfed.org/docs/api/api_key.html)
                     Can also set FRED_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        self.base_url = 'https://api.stlouisfed.org/fred'
        self._cache = {}
        self._cache_ts = {}
        
        if self.api_key:
            print("✅ FRED API key detected - macro analysis enabled")
        else:
            print("⚠️ No FRED_API_KEY set - using fallback estimates only")
    
    def is_configured(self) -> bool:
        """Check if FRED API is available."""
        return bool(self.api_key)
    
    def _fetch_series(self, series_id: str, days: int = 365) -> Optional[pd.DataFrame]:
        """Fetch a FRED data series."""
        if not self.api_key:
            return None
            
        # Check cache (10 minute TTL)
        cache_key = f"{series_id}_{days}"
        if cache_key in self._cache:
            age = (datetime.now() - self._cache_ts.get(cache_key, datetime.min)).seconds
            if age < 600:  # 10 minutes
                return self._cache[cache_key]
        
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'observation_start': start_date,
                'observation_end': end_date,
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                return None
                
            data = resp.json()
            if 'observations' not in data:
                return None
                
            observations = data['observations']
            if not observations:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            df = df.set_index('date')
            
            # Cache result
            self._cache[cache_key] = df
            self._cache_ts[cache_key] = datetime.now()
            
            return df
            
        except Exception as e:
            print(f"⚠️ FRED fetch error for {series_id}: {e}")
            return None
    
    def get_yield_curve_signal(self) -> Dict:
        """
        Analyze yield curve for recession/expansion signals.
        
        Returns:
            dict with: spread, signal, confidence, recession_probability
        """
        result = {
            'spread': None,
            'signal': 'UNKNOWN',
            'confidence': 50,
            'recession_probability': 0.5,
            'description': 'Yield curve data unavailable'
        }
        
        # Try 10Y-2Y spread first (most watched)
        spread_df = self._fetch_series('T10Y2Y', days=90)
        if spread_df is not None and len(spread_df) > 0:
            latest = float(spread_df['value'].iloc[-1])
            avg_30d = float(spread_df['value'].tail(30).mean())
            
            result['spread'] = latest
            
            # Interpret the yield curve
            if latest < -0.5:
                result['signal'] = 'STRONG_RECESSION_WARNING'
                result['confidence'] = 90
                result['recession_probability'] = 0.85
                result['description'] = 'Deeply inverted yield curve - high recession risk'
            elif latest < 0:
                result['signal'] = 'RECESSION_WARNING'
                result['confidence'] = 75
                result['recession_probability'] = 0.65
                result['description'] = 'Inverted yield curve - elevated recession risk'
            elif latest < 0.5:
                result['signal'] = 'CAUTION'
                result['confidence'] = 60
                result['recession_probability'] = 0.35
                result['description'] = 'Flat yield curve - slow growth expected'
            elif latest < 1.5:
                result['signal'] = 'NORMAL'
                result['confidence'] = 70
                result['recession_probability'] = 0.15
                result['description'] = 'Normal yield curve - healthy expansion'
            else:
                result['signal'] = 'STRONG_GROWTH'
                result['confidence'] = 80
                result['recession_probability'] = 0.05
                result['description'] = 'Steep yield curve - strong growth ahead'
            
            # Add trend
            if len(spread_df) >= 30:
                trend = latest - avg_30d
                result['trend'] = 'IMPROVING' if trend > 0.1 else 'WORSENING' if trend < -0.1 else 'STABLE'
        
        return result
    
    def get_vix_from_fred(self) -> Optional[float]:
        """Get VIX directly from FRED as fallback when other sources fail."""
        vix_df = self._fetch_series('VIXCLS', days=10)
        if vix_df is not None and len(vix_df) > 0:
            return float(vix_df['value'].iloc[-1])
        return None
    
    def get_inflation_signal(self) -> Dict:
        """
        Analyze inflation for investment positioning.
        
        Returns:
            dict with: cpi_yoy, signal, description
        """
        result = {
            'cpi_yoy': None,
            'signal': 'UNKNOWN',
            'description': 'Inflation data unavailable'
        }
        
        cpi_df = self._fetch_series('CPIAUCSL', days=400)
        if cpi_df is not None and len(cpi_df) >= 12:
            latest = float(cpi_df['value'].iloc[-1])
            year_ago = float(cpi_df['value'].iloc[-12])
            yoy_change = ((latest - year_ago) / year_ago) * 100
            
            result['cpi_yoy'] = round(yoy_change, 2)
            
            if yoy_change > 6:
                result['signal'] = 'HIGH_INFLATION'
                result['description'] = 'High inflation - favor value, commodities, TIPS'
            elif yoy_change > 3:
                result['signal'] = 'ELEVATED_INFLATION'
                result['description'] = 'Elevated inflation - consider inflation hedges'
            elif yoy_change > 2:
                result['signal'] = 'TARGET_INFLATION'
                result['description'] = 'Target inflation - balanced allocation appropriate'
            else:
                result['signal'] = 'LOW_INFLATION'
                result['description'] = 'Low inflation - favor growth stocks'
        
        return result
    
    def get_employment_signal(self) -> Dict:
        """
        Analyze employment for economic health signals.
        
        Returns:
            dict with: unemployment_rate, signal, description
        """
        result = {
            'unemployment_rate': None,
            'signal': 'UNKNOWN',
            'description': 'Employment data unavailable'
        }
        
        unrate_df = self._fetch_series('UNRATE', days=400)
        if unrate_df is not None and len(unrate_df) >= 12:
            latest = float(unrate_df['value'].iloc[-1])
            avg_12m = float(unrate_df['value'].tail(12).mean())
            
            result['unemployment_rate'] = latest
            
            if latest < 4:
                if latest > avg_12m + 0.5:
                    result['signal'] = 'RISING_FROM_LOW'
                    result['description'] = 'Unemployment rising from low base - early warning'
                else:
                    result['signal'] = 'STRONG_LABOR'
                    result['description'] = 'Strong labor market - supports consumer spending'
            elif latest < 5:
                result['signal'] = 'HEALTHY'
                result['description'] = 'Healthy employment levels'
            elif latest < 7:
                result['signal'] = 'SOFTENING'
                result['description'] = 'Softening labor market - be cautious'
            else:
                result['signal'] = 'WEAK'
                result['description'] = 'Weak labor market - recession conditions'
        
        return result
    
    def get_fed_policy_signal(self) -> Dict:
        """
        Analyze Fed policy direction.
        
        Returns:
            dict with: fed_funds_rate, signal, description
        """
        result = {
            'fed_funds_rate': None,
            'signal': 'UNKNOWN',
            'description': 'Fed funds data unavailable'
        }
        
        dff_df = self._fetch_series('DFF', days=180)
        if dff_df is not None and len(dff_df) >= 30:
            latest = float(dff_df['value'].iloc[-1])
            avg_30d = float(dff_df['value'].tail(30).mean())
            avg_90d = float(dff_df['value'].tail(90).mean()) if len(dff_df) >= 90 else avg_30d
            
            result['fed_funds_rate'] = latest
            
            # Determine policy direction
            if latest > avg_90d + 0.25:
                result['signal'] = 'TIGHTENING'
                result['description'] = 'Fed tightening - headwind for risk assets'
            elif latest < avg_90d - 0.25:
                result['signal'] = 'EASING'
                result['description'] = 'Fed easing - tailwind for risk assets'
            else:
                result['signal'] = 'NEUTRAL'
                result['description'] = 'Fed on hold - focus on fundamentals'
            
            result['trend'] = 'UP' if latest > avg_30d else 'DOWN' if latest < avg_30d else 'FLAT'
        
        return result
    
    def get_macro_summary(self) -> Dict:
        """
        Get comprehensive macro analysis summary.
        
        Returns:
            dict with all macro signals combined into a trading recommendation
        """
        yield_curve = self.get_yield_curve_signal()
        inflation = self.get_inflation_signal()
        employment = self.get_employment_signal()
        fed_policy = self.get_fed_policy_signal()
        vix = self.get_vix_from_fred()
        
        # Calculate overall macro score (0-100)
        scores = []
        
        # Yield curve score
        if yield_curve['signal'] == 'STRONG_GROWTH':
            scores.append(90)
        elif yield_curve['signal'] == 'NORMAL':
            scores.append(75)
        elif yield_curve['signal'] == 'CAUTION':
            scores.append(50)
        elif yield_curve['signal'] == 'RECESSION_WARNING':
            scores.append(30)
        elif yield_curve['signal'] == 'STRONG_RECESSION_WARNING':
            scores.append(10)
        
        # Employment score
        if employment['signal'] == 'STRONG_LABOR':
            scores.append(85)
        elif employment['signal'] == 'HEALTHY':
            scores.append(75)
        elif employment['signal'] == 'RISING_FROM_LOW':
            scores.append(55)
        elif employment['signal'] == 'SOFTENING':
            scores.append(40)
        elif employment['signal'] == 'WEAK':
            scores.append(20)
        
        # Fed policy score (from equity perspective)
        if fed_policy['signal'] == 'EASING':
            scores.append(85)
        elif fed_policy['signal'] == 'NEUTRAL':
            scores.append(60)
        elif fed_policy['signal'] == 'TIGHTENING':
            scores.append(40)
        
        # VIX score
        if vix is not None:
            if vix < 15:
                scores.append(85)
            elif vix < 20:
                scores.append(70)
            elif vix < 25:
                scores.append(55)
            elif vix < 35:
                scores.append(35)
            else:
                scores.append(20)
        
        macro_score = np.mean(scores) if scores else 50
        
        # Determine overall recommendation
        if macro_score >= 75:
            recommendation = 'BULLISH'
            stance = 'Risk-on positioning appropriate'
        elif macro_score >= 60:
            recommendation = 'NEUTRAL_BULLISH'
            stance = 'Moderate risk exposure'
        elif macro_score >= 45:
            recommendation = 'NEUTRAL'
            stance = 'Balanced allocation'
        elif macro_score >= 30:
            recommendation = 'NEUTRAL_BEARISH'
            stance = 'Reduce risk exposure'
        else:
            recommendation = 'BEARISH'
            stance = 'Defensive positioning'
        
        return {
            'macro_score': round(macro_score, 1),
            'recommendation': recommendation,
            'stance': stance,
            'yield_curve': yield_curve,
            'inflation': inflation,
            'employment': employment,
            'fed_policy': fed_policy,
            'vix': vix,
            'timestamp': datetime.now().isoformat(),
        }


def get_fred_analyzer() -> FREDMacroAnalyzer:
    """Get singleton FRED analyzer instance."""
    return FREDMacroAnalyzer()


if __name__ == "__main__":
    # Test the analyzer
    print("=" * 60)
    print("FRED MACRO ECONOMIC ANALYZER - TEST")
    print("=" * 60)
    
    analyzer = FREDMacroAnalyzer()
    
    if analyzer.is_configured():
        summary = analyzer.get_macro_summary()
        print(f"\n📊 Macro Score: {summary['macro_score']}")
        print(f"📈 Recommendation: {summary['recommendation']}")
        print(f"💼 Stance: {summary['stance']}")
        
        print(f"\n📐 Yield Curve:")
        print(f"   Spread: {summary['yield_curve']['spread']}")
        print(f"   Signal: {summary['yield_curve']['signal']}")
        
        print(f"\n💹 VIX: {summary['vix']}")
        
        print(f"\n👷 Employment:")
        print(f"   Rate: {summary['employment']['unemployment_rate']}")
        print(f"   Signal: {summary['employment']['signal']}")
    else:
        print("\n⚠️ FRED API key not configured")
        print("   Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("   Set: export FRED_API_KEY=your_key")
