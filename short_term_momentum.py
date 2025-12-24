#!/usr/bin/env python3
"""
Short-Term Momentum Scanner
Identifies stocks with potential for 1-3 week swing trades using technical signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class ShortTermMomentum:
    """
    Scans for short-term momentum opportunities (1-3 week timeframe).
    Uses technical signals that historically precede short-term price moves.
    """
    
    def __init__(self):
        # RSI thresholds
        self.rsi2_oversold = 10      # RSI(2) below this = extreme oversold
        self.rsi2_reversal = 20      # RSI(2) turning up from below this
        self.rsi14_oversold = 30     # Standard RSI oversold
        self.rsi14_overbought = 70   # Standard RSI overbought
        
        # Breakout thresholds
        self.volume_surge_ratio = 1.5  # Volume 1.5x average = surge
        self.breakout_threshold = 0.02 # 2% above resistance = breakout
        
        # Relative strength
        self.rs_outperform_threshold = 0.03  # 3% better than SPY over 5 days
        
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI for given period"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def detect_rsi_reversal(self, df: pd.DataFrame) -> Dict:
        """
        Detect RSI(2) reversal signals (Connors RSI strategy).
        High win rate for short-term bounces.
        """
        if df is None or len(df) < 10:
            return {'signal': False, 'score': 0, 'detail': 'Insufficient data'}
        
        try:
            close = df['Close']
            rsi2 = self.calculate_rsi(close, period=2)
            rsi14 = self.calculate_rsi(close, period=14)
            
            current_rsi2 = rsi2.iloc[-1]
            prev_rsi2 = rsi2.iloc[-2]
            current_rsi14 = rsi14.iloc[-1]
            
            # Strong signal: RSI(2) was below 10 and is now turning up
            if prev_rsi2 < self.rsi2_oversold and current_rsi2 > prev_rsi2:
                return {
                    'signal': True,
                    'signal_type': 'STRONG_REVERSAL',
                    'score': 90,
                    'detail': f'RSI(2) reversal from {prev_rsi2:.1f} to {current_rsi2:.1f}',
                    'rsi2': current_rsi2,
                    'rsi14': current_rsi14
                }
            
            # Moderate signal: RSI(2) below 20 and turning up
            elif prev_rsi2 < self.rsi2_reversal and current_rsi2 > prev_rsi2:
                return {
                    'signal': True,
                    'signal_type': 'MODERATE_REVERSAL',
                    'score': 70,
                    'detail': f'RSI(2) upturn from {prev_rsi2:.1f} to {current_rsi2:.1f}',
                    'rsi2': current_rsi2,
                    'rsi14': current_rsi14
                }
            
            # Weak signal: RSI(14) oversold
            elif current_rsi14 < self.rsi14_oversold:
                return {
                    'signal': True,
                    'signal_type': 'OVERSOLD',
                    'score': 50,
                    'detail': f'RSI(14) oversold at {current_rsi14:.1f}',
                    'rsi2': current_rsi2,
                    'rsi14': current_rsi14
                }
            
            return {'signal': False, 'score': 0, 'detail': 'No RSI signal'}
            
        except Exception as e:
            return {'signal': False, 'score': 0, 'detail': f'RSI calculation error: {str(e)[:50]}'}
    
    def detect_breakout(self, df: pd.DataFrame) -> Dict:
        """
        Detect price breakouts above recent resistance with volume confirmation.
        """
        if df is None or len(df) < 25:
            return {'signal': False, 'score': 0, 'detail': 'Insufficient data'}
        
        try:
            close = df['Close']
            volume = df['Volume']
            high = df['High']
            
            current_price = close.iloc[-1]
            current_volume = volume.iloc[-1]
            
            # 20-day high (resistance)
            resistance_20d = high.iloc[-21:-1].max()
            
            # Average volume
            avg_volume = volume.iloc[-21:-1].mean()
            
            # Volume ratio
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Check for breakout
            breakout_pct = (current_price - resistance_20d) / resistance_20d
            
            if breakout_pct > self.breakout_threshold and volume_ratio >= self.volume_surge_ratio:
                return {
                    'signal': True,
                    'signal_type': 'STRONG_BREAKOUT',
                    'score': 85,
                    'detail': f'Breakout +{breakout_pct*100:.1f}% above 20d high with {volume_ratio:.1f}x volume',
                    'breakout_pct': breakout_pct,
                    'volume_ratio': volume_ratio
                }
            elif breakout_pct > 0 and volume_ratio >= self.volume_surge_ratio:
                return {
                    'signal': True,
                    'signal_type': 'VOLUME_SURGE',
                    'score': 65,
                    'detail': f'Near breakout with {volume_ratio:.1f}x volume surge',
                    'breakout_pct': breakout_pct,
                    'volume_ratio': volume_ratio
                }
            elif breakout_pct > self.breakout_threshold:
                return {
                    'signal': True,
                    'signal_type': 'BREAKOUT_NO_VOLUME',
                    'score': 45,
                    'detail': f'Breakout +{breakout_pct*100:.1f}% but low volume ({volume_ratio:.1f}x)',
                    'breakout_pct': breakout_pct,
                    'volume_ratio': volume_ratio
                }
            
            return {'signal': False, 'score': 0, 'detail': 'No breakout signal'}
            
        except Exception as e:
            return {'signal': False, 'score': 0, 'detail': f'Breakout detection error: {str(e)[:50]}'}
    
    def calculate_relative_strength(self, stock_df: pd.DataFrame, spy_df: pd.DataFrame) -> Dict:
        """
        Calculate relative strength vs SPY over various timeframes.
        Stocks outperforming in down markets are leaders.
        """
        if stock_df is None or len(stock_df) < 10:
            return {'signal': False, 'score': 0, 'detail': 'Insufficient stock data'}
        if spy_df is None or len(spy_df) < 10:
            return {'signal': False, 'score': 0, 'detail': 'Insufficient SPY data'}
        
        try:
            # 5-day returns
            stock_return_5d = (stock_df['Close'].iloc[-1] / stock_df['Close'].iloc[-6]) - 1
            spy_return_5d = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[-6]) - 1
            
            # Relative strength
            rs_5d = stock_return_5d - spy_return_5d
            
            # 20-day returns for trend confirmation
            stock_return_20d = (stock_df['Close'].iloc[-1] / stock_df['Close'].iloc[-21]) - 1
            spy_return_20d = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[-21]) - 1
            rs_20d = stock_return_20d - spy_return_20d
            
            if rs_5d >= self.rs_outperform_threshold and rs_20d >= 0:
                return {
                    'signal': True,
                    'signal_type': 'STRONG_RS_LEADER',
                    'score': 80,
                    'detail': f'Outperforming SPY by {rs_5d*100:+.1f}% (5d) and {rs_20d*100:+.1f}% (20d)',
                    'rs_5d': rs_5d,
                    'rs_20d': rs_20d
                }
            elif rs_5d >= self.rs_outperform_threshold * 0.5:
                return {
                    'signal': True,
                    'signal_type': 'RS_LEADER',
                    'score': 60,
                    'detail': f'Outperforming SPY by {rs_5d*100:+.1f}% (5d)',
                    'rs_5d': rs_5d,
                    'rs_20d': rs_20d
                }
            
            return {'signal': False, 'score': 0, 'detail': 'Not outperforming SPY'}
            
        except Exception as e:
            return {'signal': False, 'score': 0, 'detail': f'RS calculation error: {str(e)[:50]}'}
    
    def detect_macd_crossover(self, df: pd.DataFrame) -> Dict:
        """
        Detect MACD bullish crossovers.
        """
        if df is None or len(df) < 35:
            return {'signal': False, 'score': 0, 'detail': 'Insufficient data'}
        
        try:
            close = df['Close']
            
            # Calculate MACD
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            # Current and previous values
            current_macd = macd_line.iloc[-1]
            prev_macd = macd_line.iloc[-2]
            current_signal = signal_line.iloc[-1]
            prev_signal = signal_line.iloc[-2]
            
            # Bullish crossover
            if prev_macd < prev_signal and current_macd > current_signal:
                # Crossover below zero line is stronger
                if current_macd < 0:
                    return {
                        'signal': True,
                        'signal_type': 'MACD_BULLISH_CROSS_BELOW_ZERO',
                        'score': 75,
                        'detail': 'MACD bullish crossover below zero line (stronger signal)',
                        'macd': current_macd,
                        'signal_line': current_signal
                    }
                else:
                    return {
                        'signal': True,
                        'signal_type': 'MACD_BULLISH_CROSS',
                        'score': 55,
                        'detail': 'MACD bullish crossover above zero line',
                        'macd': current_macd,
                        'signal_line': current_signal
                    }
            
            return {'signal': False, 'score': 0, 'detail': 'No MACD crossover'}
            
        except Exception as e:
            return {'signal': False, 'score': 0, 'detail': f'MACD calculation error: {str(e)[:50]}'}
    
    def analyze_stock(self, symbol: str, stock_df: pd.DataFrame, 
                      spy_df: pd.DataFrame = None) -> Dict:
        """
        Comprehensive momentum analysis for a single stock.
        Returns combined score and all signals.
        """
        signals = {}
        total_score = 0
        signal_count = 0
        
        # RSI Reversal (25% weight)
        rsi_signal = self.detect_rsi_reversal(stock_df)
        signals['rsi_reversal'] = rsi_signal
        if rsi_signal['signal']:
            total_score += rsi_signal['score'] * 0.25
            signal_count += 1
        
        # Breakout Detection (25% weight)
        breakout_signal = self.detect_breakout(stock_df)
        signals['breakout'] = breakout_signal
        if breakout_signal['signal']:
            total_score += breakout_signal['score'] * 0.25
            signal_count += 1
        
        # Relative Strength (20% weight)
        if spy_df is not None:
            rs_signal = self.calculate_relative_strength(stock_df, spy_df)
            signals['relative_strength'] = rs_signal
            if rs_signal['signal']:
                total_score += rs_signal['score'] * 0.20
                signal_count += 1
        else:
            signals['relative_strength'] = {'signal': False, 'score': 0, 'detail': 'No SPY data'}
        
        # MACD Crossover (15% weight)
        macd_signal = self.detect_macd_crossover(stock_df)
        signals['macd'] = macd_signal
        if macd_signal['signal']:
            total_score += macd_signal['score'] * 0.15
            signal_count += 1
        
        # Determine overall signal strength
        if signal_count >= 3 and total_score >= 60:
            momentum_grade = 'STRONG'
            recommendation = 'SWING BUY'
        elif signal_count >= 2 and total_score >= 40:
            momentum_grade = 'MODERATE'
            recommendation = 'WATCHLIST'
        elif signal_count >= 1 and total_score >= 20:
            momentum_grade = 'WEAK'
            recommendation = 'MONITOR'
        else:
            momentum_grade = 'NONE'
            recommendation = 'NO ACTION'
        
        return {
            'symbol': symbol,
            'momentum_score': round(total_score, 1),
            'signal_count': signal_count,
            'momentum_grade': momentum_grade,
            'recommendation': recommendation,
            'signals': signals,
            'timeframe': '1-3 weeks',
            'analyzed_at': datetime.now().isoformat()
        }
    
    def scan_universe(self, stocks_data: Dict[str, pd.DataFrame], 
                      spy_df: pd.DataFrame = None,
                      min_score: float = 30.0) -> List[Dict]:
        """
        Scan entire universe for momentum opportunities.
        
        Args:
            stocks_data: Dict of symbol -> DataFrame
            spy_df: SPY data for relative strength calculation
            min_score: Minimum score to include in results
            
        Returns:
            List of momentum opportunities sorted by score
        """
        opportunities = []
        
        for symbol, df in stocks_data.items():
            try:
                result = self.analyze_stock(symbol, df, spy_df)
                if result['momentum_score'] >= min_score:
                    opportunities.append(result)
            except Exception as e:
                continue
        
        # Sort by momentum score descending
        opportunities.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        return opportunities
    
    def format_for_display(self, result: Dict) -> str:
        """Format single stock result for display"""
        grade_emoji = {
            'STRONG': '🚀',
            'MODERATE': '📈',
            'WEAK': '📊',
            'NONE': '⏸️'
        }
        
        emoji = grade_emoji.get(result['momentum_grade'], '❓')
        
        output = f"""
{emoji} {result['symbol']} | Score: {result['momentum_score']:.1f} | {result['recommendation']}
   Grade: {result['momentum_grade']} | Signals: {result['signal_count']}/4 | Timeframe: {result['timeframe']}
   
   Signals:
"""
        for signal_name, signal_data in result['signals'].items():
            status = '✅' if signal_data['signal'] else '❌'
            output += f"   {status} {signal_name.replace('_', ' ').title()}: {signal_data['detail']}\n"
        
        return output
    
    def format_for_excel(self, results: List[Dict]) -> pd.DataFrame:
        """Format results for Excel export"""
        rows = []
        for r in results:
            row = {
                'Symbol': r['symbol'],
                'Momentum Score': r['momentum_score'],
                'Grade': r['momentum_grade'],
                'Recommendation': r['recommendation'],
                'Signal Count': f"{r['signal_count']}/4",
                'Timeframe': r['timeframe'],
                'RSI Signal': r['signals']['rsi_reversal']['detail'] if r['signals']['rsi_reversal']['signal'] else '-',
                'Breakout Signal': r['signals']['breakout']['detail'] if r['signals']['breakout']['signal'] else '-',
                'RS Signal': r['signals']['relative_strength']['detail'] if r['signals']['relative_strength']['signal'] else '-',
                'MACD Signal': r['signals']['macd']['detail'] if r['signals']['macd']['signal'] else '-'
            }
            rows.append(row)
        
        return pd.DataFrame(rows)


# Quick test
if __name__ == "__main__":
    print("🧪 Testing Short-Term Momentum Scanner\n")
    
    # Create synthetic test data
    import numpy as np
    
    dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
    
    # Simulated stock with reversal pattern
    np.random.seed(42)
    base_price = 100
    prices = [base_price]
    for i in range(49):
        # Create a downtrend then reversal pattern
        if i < 40:
            change = np.random.normal(-0.005, 0.02)
        else:
            change = np.random.normal(0.015, 0.02)
        prices.append(prices[-1] * (1 + change))
    
    test_df = pd.DataFrame({
        'Open': prices,
        'High': [p * 1.01 for p in prices],
        'Low': [p * 0.99 for p in prices],
        'Close': prices,
        'Volume': [1000000 + np.random.randint(-200000, 500000) for _ in prices]
    }, index=dates)
    
    scanner = ShortTermMomentum()
    result = scanner.analyze_stock('TEST', test_df, None)
    print(scanner.format_for_display(result))
