#!/usr/bin/env python3
"""
Premium Stock Quality Analyzer
Simplified, focused approach for institutional-grade stocks
Uses 15 key metrics instead of 200+ noisy indicators

Focus: Low-risk, high-quality stocks with steady growth
Universe: 614 premium institutional-grade companies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Tuple, Optional
import warnings
import time
warnings.filterwarnings('ignore')


class PremiumStockAnalyzer:
    """
    Premium Stock Quality Analyzer - Simplified & Focused
    
    Uses only 15 key metrics:
    - Fundamentals (40%): P/E, Revenue Growth, Margins, ROE, Debt/Equity
    - Momentum (30%): Price Trend, RSI, Volume, Relative Strength
    - Risk (20%): Beta, Max Drawdown, Sharpe Ratio
    - Sentiment (10%): Institutional Ownership, Analyst Ratings, News Sentiment
    """
    
    def __init__(self, data_mode='light', data_fetcher=None):
        self.data_mode = data_mode
        self.data_fetcher = data_fetcher  # Optional: use existing data fetcher with caching
        self.quality_weights = {
            'fundamentals': 0.40,
            'momentum': 0.30,
            'risk': 0.20,
            'sentiment': 0.10
        }
        
    def analyze_stock(self, symbol: str, hist_data: Optional[pd.DataFrame] = None, 
                     info: Optional[Dict] = None) -> Dict:
        """
        Analyze a single stock using 15 premium quality metrics.
        
        Args:
            symbol: Stock ticker
            hist_data: Historical price data (pandas DataFrame)
            info: Fundamental data (dict)
            
        Returns:
            dict with quality score, metrics, tier classification
        """
        try:
            # If data not provided, fetch it
            if hist_data is None or info is None:
                stock_data = self.data_fetcher.get_comprehensive_stock_data(symbol)
                if not stock_data or 'data' not in stock_data:
                    return self._empty_result(symbol, "No historical data available")
                hist_data = stock_data.get('data')  # Changed from 'hist' to 'data'
                info = stock_data.get('info', {})
            
            # CRITICAL FIX: If info is empty (market_cap=0), try direct yfinance as fallback.
            # If the fallback fails, continue with neutral fundamentals rather than aborting.
            if not info or info.get('marketCap', 0) == 0:
                fallback_error = None
                try:
                    import yfinance as yf
                    import time
                    import random
                    
                    # Balanced rate limiting - fast enough but avoids 429 blocks
                    delay = random.uniform(0.5, 1.2)  # Random delay 0.5-1.2 seconds per stock
                    time.sleep(delay)
                    
                    ticker = yf.Ticker(symbol)
                    
                    # Try with retry logic
                    max_retries = 2
                    for attempt in range(max_retries):
                        try:
                            raw_info = ticker.info
                            if raw_info and raw_info.get('marketCap', 0) > 0:
                                # Map yfinance fields to our format
                                info = {
                                    'marketCap': raw_info.get('marketCap', 0),
                                    'trailingPE': raw_info.get('trailingPE', 0),
                                    'forwardPE': raw_info.get('forwardPE', 0),
                                    'sector': raw_info.get('sector', 'Unknown'),
                                    'beta': raw_info.get('beta', 1.0),
                                    'debtToEquity': raw_info.get('debtToEquity', 0),
                                    'priceToBook': raw_info.get('priceToBook', 0),
                                    'dividendYield': raw_info.get('dividendYield', 0),
                                    'profitMargins': raw_info.get('profitMargins', 0),
                                    'revenueGrowth': raw_info.get('revenueGrowth', 0),
                                    'returnOnEquity': raw_info.get('returnOnEquity', 0),
                                }
                                break  # Success
                        except Exception as retry_e:
                            if '429' in str(retry_e) and attempt < max_retries - 1:
                                # Rate limited - exponential backoff
                                wait_time = (attempt + 1) * 3  # 3, 6 seconds
                                print(f"⚠️ {symbol}: Rate limited, waiting {wait_time}s...")
                                time.sleep(wait_time)
                            else:
                                raise  # Give up
                except Exception as e:
                    fallback_error = e
                    if '429' not in str(e):
                        print(f"⚠️ {symbol}: Fundamental data error ({e})")
                finally:
                    if not info or info.get('marketCap', 0) == 0:
                        # Ensure we have a dict with neutral defaults so analysis still runs.
                        info = info or {}
                        info.setdefault('marketCap', 0)
                        info.setdefault('sector', 'Unknown')
                        info.setdefault('beta', info.get('beta', 1.0) or 1.0)
                        info.setdefault('_fundamentals_missing', True)
                        if fallback_error:
                            info.setdefault('_fundamental_error', str(fallback_error))
            
            # Calculate all 15 metrics
            fundamentals = self._calculate_fundamentals(info, hist_data)
            momentum = self._calculate_momentum(hist_data, symbol)
            risk = self._calculate_risk(hist_data, info)
            technical = self._calculate_technical(hist_data)
            # Use latest close as definitive price reference
            current_price = float(hist_data['Close'].iloc[-1]) if not hist_data.empty else info.get('currentPrice', 0)
            sentiment = self._calculate_sentiment(info, current_price=current_price)
            
            # Calculate overall quality score
            quality_score = (
                fundamentals['score'] * self.quality_weights['fundamentals'] +
                momentum['score'] * self.quality_weights['momentum'] +
                risk['score'] * self.quality_weights['risk'] +
                sentiment['score'] * self.quality_weights['sentiment']
            )
            
            # Determine recommendation
            recommendation, confidence = self._determine_recommendation(
                quality_score, fundamentals, momentum, risk, sentiment
            )
            
            return {
                'symbol': symbol,
                'quality_score': round(quality_score, 2),
                'recommendation': recommendation,
                'confidence': round(confidence, 2),
                'fundamentals': fundamentals,
                'momentum': momentum,
                'risk': risk,
                'technical': technical,
                'sentiment': sentiment,
                'current_price': current_price,
                'sector': info.get('sector', 'Unknown'),
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'success': True
            }
            
        except Exception as e:
            return self._empty_result(symbol, str(e))
    
    def _calculate_fundamentals(self, info: Dict, hist: pd.DataFrame) -> Dict:
        """
        Calculate 5 fundamental metrics (40% weight)
        1. P/E Ratio (valuation)
        2. Revenue Growth (business health)
        3. Profit Margins (quality)
        4. ROE (efficiency)
        5. Debt/Equity (financial strength)
        """
        fundamentals = {}
        scores = []
        
        # 1. P/E Ratio (lower is better for value, but not too low)
        pe = info.get('trailingPE', info.get('forwardPE', 0))
        if pe and pe > 0:
            # Ideal P/E: 15-25 for quality stocks
            if 15 <= pe <= 25:
                pe_score = 100
            elif 10 <= pe < 15 or 25 < pe <= 30:
                pe_score = 80
            elif 5 <= pe < 10 or 30 < pe <= 40:
                pe_score = 60
            else:
                pe_score = 40
        else:
            pe = None
            pe_score = 50  # Neutral if not available
        
        fundamentals['pe_ratio'] = pe
        fundamentals['pe_score'] = pe_score
        scores.append(pe_score)
        
        # 2. Revenue Growth (higher is better)
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth:
            revenue_growth_pct = revenue_growth * 100
            if revenue_growth_pct >= 20:
                rev_score = 100
            elif revenue_growth_pct >= 10:
                rev_score = 85
            elif revenue_growth_pct >= 5:
                rev_score = 70
            elif revenue_growth_pct >= 0:
                rev_score = 50
            else:
                rev_score = 30
        else:
            revenue_growth_pct = None
            rev_score = 50
        
        fundamentals['revenue_growth'] = revenue_growth_pct
        fundamentals['revenue_growth_score'] = rev_score
        scores.append(rev_score)
        
        # 3. Profit Margins (higher is better)
        profit_margin = info.get('profitMargins', 0)
        if profit_margin:
            profit_margin_pct = profit_margin * 100
            if profit_margin_pct >= 20:
                margin_score = 100
            elif profit_margin_pct >= 15:
                margin_score = 85
            elif profit_margin_pct >= 10:
                margin_score = 70
            elif profit_margin_pct >= 5:
                margin_score = 50
            else:
                margin_score = 30
        else:
            profit_margin_pct = None
            margin_score = 50
        
        fundamentals['profit_margin'] = profit_margin_pct
        fundamentals['margin_score'] = margin_score
        scores.append(margin_score)
        
        # 4. ROE - Return on Equity (higher is better)
        roe = info.get('returnOnEquity', 0)
        if roe:
            roe_pct = roe * 100
            if roe_pct >= 20:
                roe_score = 100
            elif roe_pct >= 15:
                roe_score = 85
            elif roe_pct >= 10:
                roe_score = 70
            elif roe_pct >= 5:
                roe_score = 50
            else:
                roe_score = 30
        else:
            roe_pct = None
            roe_score = 50
        
        fundamentals['roe'] = roe_pct
        fundamentals['roe_score'] = roe_score
        scores.append(roe_score)
        
        # 5. Debt/Equity (lower is better)
        debt_equity = info.get('debtToEquity', 0)
        if debt_equity is not None and debt_equity >= 0:
            if debt_equity <= 30:
                de_score = 100
            elif debt_equity <= 50:
                de_score = 85
            elif debt_equity <= 100:
                de_score = 70
            elif debt_equity <= 150:
                de_score = 50
            else:
                de_score = 30
        else:
            debt_equity = None
            de_score = 50
        
        fundamentals['debt_equity'] = debt_equity
        fundamentals['debt_equity_score'] = de_score
        scores.append(de_score)
        
        # Overall fundamental score
        fundamentals['score'] = np.mean(scores)
        fundamentals['grade'] = self._score_to_grade(fundamentals['score'])
        
        return fundamentals
    
    def _calculate_momentum(self, hist: pd.DataFrame, symbol: str) -> Dict:
        """
        Calculate 4 momentum metrics (30% weight)
        1. Price Trend (50/200 MA crossover)
        2. RSI (single period - 14 days)
        3. Volume Trend (accumulation/distribution)
        4. Relative Strength vs SPY
        """
        momentum = {}
        scores = []
        
        if len(hist) < 200:
            # Not enough data
            return {
                'score': 50,
                'grade': 'C',
                'price_trend': None,
                'rsi': None,
                'volume_trend': None,
                'relative_strength': None
            }
        
        # 1. Price Trend - 50/200 MA
        ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma_200 = hist['Close'].rolling(200).mean().iloc[-1]
        current_price = hist['Close'].iloc[-1]
        
        # Golden Cross: 50 MA > 200 MA and price above both
        if ma_50 > ma_200:
            if current_price > ma_50:
                trend_score = 100  # Strong uptrend
            else:
                trend_score = 70  # Uptrend but price below 50 MA
        else:
            if current_price > ma_50:
                trend_score = 60  # Death cross but price above 50 MA
            else:
                trend_score = 30  # Downtrend
        
        momentum['price_trend'] = 'Uptrend' if ma_50 > ma_200 else 'Downtrend'
        momentum['ma_50'] = round(ma_50, 2)
        momentum['ma_200'] = round(ma_200, 2)
        momentum['trend_score'] = trend_score
        scores.append(trend_score)
        
        # 2. RSI - 14 period (single calculation, not 4 variants!)
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_current = rsi.iloc[-1]
        
        # RSI scoring: 40-60 = neutral, 30-40 = oversold (buy), 60-70 = overbought (caution)
        if 40 <= rsi_current <= 55:
            rsi_score = 100  # Ideal range
        elif 30 <= rsi_current < 40 or 55 < rsi_current <= 60:
            rsi_score = 85  # Slightly oversold/overbought
        elif 60 < rsi_current <= 70:
            rsi_score = 60  # Overbought
        elif rsi_current < 30:
            rsi_score = 70  # Oversold - potential buy
        else:
            rsi_score = 40  # Extremely overbought
        
        momentum['rsi'] = round(rsi_current, 2)
        momentum['rsi_score'] = rsi_score
        scores.append(rsi_score)
        
        # 3. Volume Trend - comparing recent volume to average
        vol_20 = hist['Volume'].rolling(20).mean().iloc[-1]
        vol_recent = hist['Volume'].iloc[-5:].mean()
        
        vol_ratio = vol_recent / vol_20 if vol_20 > 0 else 1
        
        if vol_ratio >= 1.5:
            vol_score = 100  # Strong accumulation
        elif vol_ratio >= 1.2:
            vol_score = 85
        elif vol_ratio >= 0.8:
            vol_score = 70  # Normal
        else:
            vol_score = 50  # Low volume
        
        momentum['volume_trend'] = 'High' if vol_ratio >= 1.2 else 'Normal' if vol_ratio >= 0.8 else 'Low'
        momentum['volume_ratio'] = round(vol_ratio, 2)
        momentum['volume_score'] = vol_score
        scores.append(vol_score)
        
        # 4. Relative Strength vs SPY
        try:
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period='1y')
            
            if not spy_hist.empty and len(spy_hist) > 20:
                # Calculate 3-month returns
                stock_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1) * 100 if len(hist) >= 63 else 0
                spy_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-63] - 1) * 100 if len(spy_hist) >= 63 else 0
                
                relative_strength = stock_return - spy_return
                
                if relative_strength >= 10:
                    rs_score = 100  # Significantly outperforming
                elif relative_strength >= 5:
                    rs_score = 85
                elif relative_strength >= 0:
                    rs_score = 70
                elif relative_strength >= -5:
                    rs_score = 50
                else:
                    rs_score = 30  # Underperforming
                
                momentum['relative_strength'] = round(relative_strength, 2)
                momentum['relative_strength_score'] = rs_score
                scores.append(rs_score)
            else:
                momentum['relative_strength'] = None
                momentum['relative_strength_score'] = 50
                scores.append(50)
        except:
            momentum['relative_strength'] = None
            momentum['relative_strength_score'] = 50
            scores.append(50)
        
        # Overall momentum score
        momentum['score'] = np.mean(scores)
        momentum['grade'] = self._score_to_grade(momentum['score'])
        
        return momentum
    
    def _calculate_risk(self, hist: pd.DataFrame, info: Dict) -> Dict:
        """
        Calculate 3 risk metrics (20% weight)
        1. Beta (market volatility)
        2. Max Drawdown (downside risk)
        3. Sharpe Ratio (risk-adjusted returns)
        """
        risk = {}
        scores = []
        
        # 1. Beta - lower is better for low-risk stocks
        beta = info.get('beta', 1.0)
        if beta is not None:
            if beta <= 0.8:
                beta_score = 100  # Low volatility
            elif beta <= 1.0:
                beta_score = 85
            elif beta <= 1.2:
                beta_score = 70
            elif beta <= 1.5:
                beta_score = 50
            else:
                beta_score = 30  # High volatility
        else:
            beta = 1.0
            beta_score = 70
        
        risk['beta'] = round(beta, 2)
        risk['beta_score'] = beta_score
        scores.append(beta_score)
        
        returns = hist['Close'].pct_change().dropna()

        # Annualized volatility (percent)
        if len(returns) >= 21:
            annualized_vol = returns.std() * np.sqrt(252) * 100
            if annualized_vol <= 20:
                vol_score = 100
            elif annualized_vol <= 30:
                vol_score = 85
            elif annualized_vol <= 40:
                vol_score = 70
            elif annualized_vol <= 55:
                vol_score = 50
            else:
                vol_score = 30
        else:
            annualized_vol = None
            vol_score = 50

        risk['volatility'] = round(annualized_vol, 2) if annualized_vol is not None else None
        scores.append(vol_score)

        # 2. Max Drawdown - lower is better
        if len(hist) >= 252:
            cumulative = (1 + hist['Close'].pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            if max_drawdown >= -10:
                dd_score = 100  # Very low drawdown
            elif max_drawdown >= -15:
                dd_score = 85
            elif max_drawdown >= -20:
                dd_score = 70
            elif max_drawdown >= -30:
                dd_score = 50
            else:
                dd_score = 30  # High drawdown risk
        else:
            max_drawdown = None
            dd_score = 50
        
        risk['max_drawdown'] = round(max_drawdown, 2) if max_drawdown is not None else None
        risk['drawdown_score'] = dd_score
        scores.append(dd_score)
        
        # 3. Sharpe Ratio - higher is better
        if len(returns) >= 252:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            
            if sharpe >= 1.5:
                sharpe_score = 100  # Excellent risk-adjusted returns
            elif sharpe >= 1.0:
                sharpe_score = 85
            elif sharpe >= 0.5:
                sharpe_score = 70
            elif sharpe >= 0:
                sharpe_score = 50
            else:
                sharpe_score = 30
        else:
            sharpe = None
            sharpe_score = 50
        
        risk['sharpe_ratio'] = round(sharpe, 2) if sharpe else None
        risk['sharpe_score'] = sharpe_score
        scores.append(sharpe_score)

        # 4. Historical Value at Risk (95%)
        if len(returns) >= 252:
            var_95 = np.percentile(returns, 5) * 100
            if var_95 >= -5:
                var_score = 100
            elif var_95 >= -10:
                var_score = 85
            elif var_95 >= -15:
                var_score = 70
            elif var_95 >= -20:
                var_score = 50
            else:
                var_score = 30
        else:
            var_95 = None
            var_score = 50

        risk['var_95'] = round(var_95, 2) if var_95 is not None else None
        scores.append(var_score)
        
        # Overall risk score (inverse - lower risk = higher score)
        risk['score'] = np.mean(scores)
        risk['grade'] = self._score_to_grade(risk['score'])
        risk['risk_level'] = 'Low' if risk['score'] >= 75 else 'Medium' if risk['score'] >= 50 else 'High'
        
        return risk

    def _calculate_technical(self, hist: pd.DataFrame) -> Dict:
        """Calculate focused technical metrics (supporting Excel export)"""
        if hist is None or hist.empty or len(hist) < 50:
            return {
                'score': 50,
                'grade': 'C',
                'macd': None,
                'macd_signal': None,
                'macd_hist': None,
                'bollinger_position': None,
                'bollinger_upper': None,
                'bollinger_lower': None,
                'support': None,
                'resistance': None,
                'volume_sma': None
            }

        close = hist['Close']

        ema_fast = close.ewm(span=12, adjust=False).mean()
        ema_slow = close.ewm(span=26, adjust=False).mean()
        macd_series = ema_fast - ema_slow
        macd_signal_series = macd_series.ewm(span=9, adjust=False).mean()

        macd = macd_series.iloc[-1]
        macd_signal = macd_signal_series.iloc[-1]
        macd_hist = macd - macd_signal
        if macd > macd_signal:
            macd_score = 100 if macd_hist > 0 else 80
        elif macd_hist > -0.1:
            macd_score = 60
        else:
            macd_score = 40

        rolling = close.rolling(window=20)
        ma20 = rolling.mean().iloc[-1]
        std20 = rolling.std().iloc[-1]
        upper_band = ma20 + 2 * std20
        lower_band = ma20 - 2 * std20
        current_price = close.iloc[-1]
        band_range = upper_band - lower_band if upper_band and lower_band else None
        if band_range and band_range != 0:
            bollinger_position = ((current_price - lower_band) / band_range) * 100
            bollinger_score = 100 if 40 <= bollinger_position <= 60 else 80 if 30 <= bollinger_position <= 70 else 60
        else:
            bollinger_position = None
            bollinger_score = 60

        support = close.rolling(window=50).min().iloc[-1]
        resistance = close.rolling(window=50).max().iloc[-1]
        volume_sma = hist['Volume'].rolling(window=20).mean().iloc[-1]

        technical_score = np.mean([macd_score, bollinger_score])
        technical_grade = self._score_to_grade(technical_score)

        def safe_round(value, digits=2):
            if value is None or (isinstance(value, float) and np.isnan(value)):
                return None
            return round(float(value), digits)

        return {
            'score': technical_score,
            'grade': technical_grade,
            'macd': safe_round(macd, 4),
            'macd_signal': safe_round(macd_signal, 4),
            'macd_hist': safe_round(macd_hist, 4),
            'bollinger_position': safe_round(bollinger_position, 2) if bollinger_position is not None else None,
            'bollinger_upper': safe_round(upper_band, 2),
            'bollinger_lower': safe_round(lower_band, 2),
            'support': safe_round(support, 2),
            'resistance': safe_round(resistance, 2),
            'volume_sma': safe_round(volume_sma, 0)
        }
    
    def _calculate_sentiment(self, info: Dict, current_price: Optional[float] = None) -> Dict:
        """
        Calculate 3 sentiment metrics (10% weight)
        1. Institutional Ownership Trend
        2. Analyst Ratings Consensus
        3. Recommendation Strength
        """
        sentiment = {}
        scores = []
        
        # 1. Institutional Ownership (higher is better for quality stocks)
        inst_ownership = info.get('institutionalOwnership', info.get('heldPercentInstitutions', 0))
        if inst_ownership:
            inst_pct = inst_ownership * 100 if inst_ownership < 1 else inst_ownership
            if inst_pct >= 70:
                inst_score = 100  # Strong institutional confidence
            elif inst_pct >= 50:
                inst_score = 85
            elif inst_pct >= 30:
                inst_score = 70
            else:
                inst_score = 50
        else:
            inst_pct = None
            inst_score = 50
        
        sentiment['institutional_ownership'] = round(inst_pct, 2) if inst_pct else None
        sentiment['institutional_score'] = inst_score
        scores.append(inst_score)
        
        # 2. Analyst Ratings
        recommendation = info.get('recommendationKey', info.get('recommendationMean', 'hold'))
        target_price = info.get('targetMeanPrice', 0)
        if not current_price:
            current_price = info.get('currentPrice', 0)
        
        # Map recommendation to score
        rec_map = {
            'strong_buy': 100,
            'buy': 85,
            'hold': 50,
            'sell': 30,
            'strong_sell': 10
        }
        if isinstance(recommendation, (int, float)):
            # recommendationMean scale: 1 (strong buy) to 5 (sell)
            if recommendation <= 1.5:
                analyst_score = 100
            elif recommendation <= 2.0:
                analyst_score = 85
            elif recommendation <= 3.0:
                analyst_score = 70
            elif recommendation <= 4.0:
                analyst_score = 50
            else:
                analyst_score = 30
            sentiment['analyst_rating'] = f"mean_{recommendation:.1f}"
        else:
            sentiment['analyst_rating'] = str(recommendation).upper()
            analyst_score = rec_map.get(str(recommendation).lower(), 50)
        
        sentiment['analyst_score'] = analyst_score
        scores.append(analyst_score)
        
        # 3. Target Price Upside
        if target_price and current_price and target_price > 0 and current_price > 0:
            upside = ((target_price - current_price) / current_price) * 100
            
            if upside >= 20:
                upside_score = 100
            elif upside >= 10:
                upside_score = 85
            elif upside >= 5:
                upside_score = 70
            elif upside >= 0:
                upside_score = 50
            else:
                upside_score = 30
        else:
            upside = None
            upside_score = 50
        
        sentiment['target_upside'] = round(upside, 2) if upside else None
        sentiment['upside_score'] = upside_score
        scores.append(upside_score)
        
        # Overall sentiment score
        sentiment['score'] = np.mean(scores)
        sentiment['grade'] = self._score_to_grade(sentiment['score'])
        
        return sentiment
    
    def _determine_recommendation(self, quality_score: float, fundamentals: Dict, 
                                  momentum: Dict, risk: Dict, sentiment: Dict) -> Tuple[str, float]:
        """
        Determine stock recommendation based on quality score and individual components
        
        Returns: (recommendation, confidence)
        """
        # Base recommendation on quality score
        if quality_score >= 80:
            base_rec = 'STRONG BUY'
            base_conf = 0.90
        elif quality_score >= 70:
            base_rec = 'BUY'
            base_conf = 0.80
        elif quality_score >= 60:
            base_rec = 'WEAK BUY'
            base_conf = 0.70
        elif quality_score >= 50:
            base_rec = 'HOLD'
            base_conf = 0.60
        else:
            base_rec = 'AVOID'
            base_conf = 0.50
        
        # Adjust confidence based on consistency across metrics
        scores = [fundamentals['score'], momentum['score'], risk['score'], sentiment['score']]
        score_std = np.std(scores)
        
        # Lower std = higher confidence (metrics agree)
        if score_std < 10:
            confidence = min(0.95, base_conf + 0.10)
        elif score_std < 15:
            confidence = base_conf
        else:
            confidence = max(0.50, base_conf - 0.10)
        
        # Downgrade if risk is high
        if risk['risk_level'] == 'High' and base_rec in ['STRONG BUY', 'BUY']:
            base_rec = 'WEAK BUY' if base_rec == 'BUY' else 'BUY'
            confidence *= 0.9
        
        return base_rec, confidence
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'D'
    
    def _empty_result(self, symbol: str, error: str) -> Dict:
        """Return empty result structure for failed analysis"""
        return {
            'symbol': symbol,
            'quality_score': 0,
            'recommendation': 'ERROR',
            'confidence': 0,
            'error': error,
            'success': False
        }
    
    def batch_analyze(self, symbols: List[str], progress_callback=None) -> List[Dict]:
        """
        Analyze multiple stocks in batch
        
        Args:
            symbols: List of stock symbols
            progress_callback: Optional callback function(current, total, symbol)
        
        Returns:
            List of analysis results
        """
        results = []
        total = len(symbols)
        
        for idx, symbol in enumerate(symbols, 1):
            if progress_callback:
                progress_callback(idx, total, symbol)
            
            result = self.analyze_stock(symbol)
            results.append(result)
        
        return results


# Convenience function for quick analysis
def analyze_premium_stock(symbol: str) -> Dict:
    """Quick analysis of a single premium stock"""
    analyzer = PremiumStockAnalyzer()
    return analyzer.analyze_stock(symbol)


if __name__ == "__main__":
    # Test with a few premium stocks
    print("=" * 80)
    print("PREMIUM STOCK QUALITY ANALYZER - TEST")
    print("=" * 80)
    
    test_symbols = ['AAPL', 'MSFT', 'JNJ', 'JPM', 'WMT']
    
    analyzer = PremiumStockAnalyzer()
    
    for symbol in test_symbols:
        print(f"\n📊 Analyzing {symbol}...")
        time.sleep(2)  # Rate limit protection
        result = analyzer.analyze_stock(symbol)
        
        if result['success']:
            print(f"   Quality Score: {result['quality_score']}/100 ({result['recommendation']})")
            print(f"   Confidence: {result['confidence']*100:.0f}%")
            print(f"   Fundamentals: {result['fundamentals']['grade']} ({result['fundamentals']['score']:.1f})")
            print(f"   Momentum: {result['momentum']['grade']} ({result['momentum']['score']:.1f})")
            print(f"   Risk: {result['risk']['grade']} ({result['risk']['score']:.1f}) - {result['risk']['risk_level']}")
            print(f"   Sentiment: {result['sentiment']['grade']} ({result['sentiment']['score']:.1f})")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("✅ Test complete - Premium analyzer using 15 focused metrics!")
    print("=" * 80)
