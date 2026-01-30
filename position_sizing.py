#!/usr/bin/env python3
"""
Position Sizing Module
Risk-based position sizing for optimal portfolio construction

Implements:
- Volatility-based sizing (ATR or historical vol)
- Kelly Criterion (optimal growth position sizes)
- Fixed fractional sizing (risk per trade)
- Correlation-aware portfolio weights

Goal: Maximize returns while controlling drawdowns
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PositionSize:
    """Position sizing recommendation."""
    symbol: str
    shares: int
    dollar_amount: float
    weight_pct: float
    risk_per_trade: float
    sizing_method: str
    rationale: str


class PositionSizer:
    """
    Calculate optimal position sizes based on risk management principles.
    """
    
    # Maximum single position as % of portfolio
    MAX_POSITION_PCT = 5.0
    
    # Minimum single position as % of portfolio
    MIN_POSITION_PCT = 1.0
    
    # Default risk per trade as % of portfolio
    DEFAULT_RISK_PCT = 1.0
    
    def __init__(self, 
                 portfolio_value: float,
                 max_position_pct: float = 5.0,
                 risk_per_trade_pct: float = 1.0):
        """
        Initialize position sizer.
        
        Args:
            portfolio_value: Total portfolio value in dollars
            max_position_pct: Maximum single position as % of portfolio
            risk_per_trade_pct: Risk per trade as % of portfolio
        """
        self.portfolio_value = portfolio_value
        self.max_position_pct = max_position_pct
        self.risk_per_trade_pct = risk_per_trade_pct
    
    def size_by_volatility(self, 
                           symbol: str,
                           current_price: float,
                           volatility: float,
                           target_vol_contribution: float = 0.5) -> PositionSize:
        """
        Size position based on volatility contribution.
        Higher volatility stocks get smaller positions.
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            volatility: Annualized volatility (as decimal, e.g., 0.30 for 30%)
            target_vol_contribution: Target volatility contribution as % of portfolio
            
        Returns:
            PositionSize recommendation
        """
        # Normalize volatility (cap at reasonable values)
        vol = max(0.10, min(1.0, volatility))  # 10% to 100%
        
        # Calculate position size inversely proportional to volatility
        # Base allocation assumes 20% volatility stock
        base_vol = 0.20
        vol_adjustment = base_vol / vol
        
        # Calculate raw weight
        raw_weight = self.max_position_pct * vol_adjustment * (target_vol_contribution / 0.5)
        
        # Apply limits
        weight_pct = max(self.MIN_POSITION_PCT, min(self.max_position_pct, raw_weight))
        
        dollar_amount = self.portfolio_value * (weight_pct / 100)
        shares = int(dollar_amount / current_price) if current_price > 0 else 0
        
        return PositionSize(
            symbol=symbol,
            shares=shares,
            dollar_amount=round(shares * current_price, 2),
            weight_pct=round(weight_pct, 2),
            risk_per_trade=round(weight_pct * vol * 0.5, 2),  # Approx risk at 1 std dev
            sizing_method='VOLATILITY_BASED',
            rationale=f"Vol {vol*100:.1f}% → Weight {weight_pct:.1f}%"
        )
    
    def size_by_atr_stop(self,
                         symbol: str,
                         current_price: float,
                         atr: float,
                         stop_atr_multiple: float = 2.0) -> PositionSize:
        """
        Size position based on ATR-based stop loss.
        Risk per trade is fixed; position size adjusts to volatility.
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            atr: Average True Range (dollar amount)
            stop_atr_multiple: How many ATRs for stop loss
            
        Returns:
            PositionSize recommendation
        """
        if current_price <= 0 or atr <= 0:
            return self._empty_position(symbol, 'INVALID_INPUTS')
        
        # Calculate risk per share (stop loss distance)
        risk_per_share = atr * stop_atr_multiple
        
        # Calculate dollar risk allowed
        risk_dollars = self.portfolio_value * (self.risk_per_trade_pct / 100)
        
        # Calculate shares
        shares = int(risk_dollars / risk_per_share) if risk_per_share > 0 else 0
        
        # Calculate weight
        dollar_amount = shares * current_price
        weight_pct = (dollar_amount / self.portfolio_value) * 100
        
        # Apply maximum position limit
        if weight_pct > self.max_position_pct:
            weight_pct = self.max_position_pct
            dollar_amount = self.portfolio_value * (weight_pct / 100)
            shares = int(dollar_amount / current_price)
        
        return PositionSize(
            symbol=symbol,
            shares=shares,
            dollar_amount=round(shares * current_price, 2),
            weight_pct=round(weight_pct, 2),
            risk_per_trade=self.risk_per_trade_pct,
            sizing_method='ATR_STOP_BASED',
            rationale=f"ATR ${atr:.2f} × {stop_atr_multiple} = ${risk_per_share:.2f} risk/share"
        )
    
    def size_by_kelly(self,
                      symbol: str,
                      current_price: float,
                      win_rate: float,
                      avg_win: float,
                      avg_loss: float,
                      kelly_fraction: float = 0.25) -> PositionSize:
        """
        Size position using Kelly Criterion (fractional Kelly for safety).
        
        Kelly % = W - [(1-W) / R]
        where W = win rate, R = avg win / avg loss
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade % (positive)
            avg_loss: Average losing trade % (positive)
            kelly_fraction: Fraction of full Kelly to use (0.25 = quarter Kelly)
            
        Returns:
            PositionSize recommendation
        """
        if win_rate <= 0 or avg_loss <= 0 or avg_win <= 0:
            return self._empty_position(symbol, 'INVALID_KELLY_INPUTS')
        
        # Calculate Kelly percentage
        r = avg_win / avg_loss  # Win/loss ratio
        kelly_pct = win_rate - ((1 - win_rate) / r)
        
        # Apply Kelly fraction and limits
        if kelly_pct <= 0:
            # Negative Kelly means don't bet
            return PositionSize(
                symbol=symbol,
                shares=0,
                dollar_amount=0,
                weight_pct=0,
                risk_per_trade=0,
                sizing_method='KELLY_NO_BET',
                rationale=f"Negative Kelly ({kelly_pct*100:.1f}%) - skip trade"
            )
        
        adjusted_kelly = kelly_pct * kelly_fraction * 100  # Convert to percentage
        weight_pct = max(self.MIN_POSITION_PCT, min(self.max_position_pct, adjusted_kelly))
        
        dollar_amount = self.portfolio_value * (weight_pct / 100)
        shares = int(dollar_amount / current_price) if current_price > 0 else 0
        
        return PositionSize(
            symbol=symbol,
            shares=shares,
            dollar_amount=round(shares * current_price, 2),
            weight_pct=round(weight_pct, 2),
            risk_per_trade=round(weight_pct * avg_loss / 100, 2),
            sizing_method=f'KELLY_{kelly_fraction:.0%}',
            rationale=f"Kelly {kelly_pct*100:.1f}% × {kelly_fraction:.0%} → {weight_pct:.1f}%"
        )
    
    def size_equal_weight(self,
                          symbol: str,
                          current_price: float,
                          num_positions: int) -> PositionSize:
        """
        Simple equal-weight sizing.
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            num_positions: Total number of positions in portfolio
            
        Returns:
            PositionSize recommendation
        """
        if num_positions <= 0:
            return self._empty_position(symbol, 'NO_POSITIONS')
        
        weight_pct = min(100 / num_positions, self.max_position_pct)
        dollar_amount = self.portfolio_value * (weight_pct / 100)
        shares = int(dollar_amount / current_price) if current_price > 0 else 0
        
        return PositionSize(
            symbol=symbol,
            shares=shares,
            dollar_amount=round(shares * current_price, 2),
            weight_pct=round(weight_pct, 2),
            risk_per_trade=round(weight_pct / 10, 2),  # Rough estimate
            sizing_method='EQUAL_WEIGHT',
            rationale=f"1/{num_positions} = {weight_pct:.1f}%"
        )
    
    def _empty_position(self, symbol: str, reason: str) -> PositionSize:
        """Return empty position with reason."""
        return PositionSize(
            symbol=symbol,
            shares=0,
            dollar_amount=0,
            weight_pct=0,
            risk_per_trade=0,
            sizing_method='SKIP',
            rationale=reason
        )
    
    def recommend_position_size(self,
                                symbol: str,
                                current_price: float,
                                volatility: Optional[float] = None,
                                atr: Optional[float] = None,
                                quality_score: Optional[float] = None,
                                consensus_score: Optional[float] = None) -> PositionSize:
        """
        Recommend optimal position size based on available data.
        Uses best available sizing method.
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            volatility: Annualized volatility (optional)
            atr: ATR value (optional)
            quality_score: Quality score 0-100 (optional)
            consensus_score: Consensus score 0-100 (optional)
            
        Returns:
            PositionSize recommendation
        """
        # Adjust risk per trade based on quality
        adjusted_risk = self.risk_per_trade_pct
        if quality_score is not None:
            # Higher quality = can risk more
            quality_multiplier = 0.5 + (quality_score / 100) * 1.0  # 0.5x to 1.5x
            adjusted_risk *= quality_multiplier
        
        if consensus_score is not None:
            # Higher consensus = more confidence
            consensus_multiplier = 0.5 + (consensus_score / 100) * 1.0
            adjusted_risk *= consensus_multiplier
        
        # Cap adjusted risk
        adjusted_risk = min(adjusted_risk, 3.0)  # Max 3% risk per trade
        
        # Choose sizing method based on available data
        if atr is not None and atr > 0:
            sizer = PositionSizer(
                self.portfolio_value,
                self.max_position_pct,
                adjusted_risk
            )
            return sizer.size_by_atr_stop(symbol, current_price, atr)
        
        elif volatility is not None and volatility > 0:
            return self.size_by_volatility(symbol, current_price, volatility)
        
        else:
            # Fallback to conservative equal weight
            return self.size_equal_weight(symbol, current_price, 20)


def calculate_portfolio_positions(picks: List[Dict],
                                  portfolio_value: float,
                                  max_positions: int = 20,
                                  max_position_pct: float = 5.0) -> List[PositionSize]:
    """
    Calculate position sizes for a list of consensus picks.
    
    Args:
        picks: List of pick dicts with symbol, quality_score, volatility, etc.
        portfolio_value: Total portfolio value
        max_positions: Maximum number of positions
        max_position_pct: Maximum single position %
        
    Returns:
        List of PositionSize recommendations
    """
    sizer = PositionSizer(
        portfolio_value=portfolio_value,
        max_position_pct=max_position_pct,
        risk_per_trade_pct=1.0
    )
    
    positions = []
    
    for pick in picks[:max_positions]:
        symbol = pick.get('symbol', '')
        price = pick.get('current_price', 0)
        vol = pick.get('volatility', None)
        quality = pick.get('quality_score', None)
        consensus = pick.get('consensus_score', None)
        
        # Get ATR if available
        risk_data = pick.get('risk', {})
        atr = None  # Would need to calculate from enhanced data
        
        pos = sizer.recommend_position_size(
            symbol=symbol,
            current_price=price,
            volatility=vol,
            atr=atr,
            quality_score=quality,
            consensus_score=consensus
        )
        
        positions.append(pos)
    
    return positions


if __name__ == "__main__":
    # Test position sizing
    print("=" * 60)
    print("POSITION SIZING MODULE - TEST")
    print("=" * 60)
    
    portfolio = 100000  # $100k portfolio
    sizer = PositionSizer(portfolio, max_position_pct=5.0, risk_per_trade_pct=1.0)
    
    # Test different sizing methods
    print(f"\nPortfolio: ${portfolio:,.0f}")
    print("-" * 60)
    
    # Volatility-based sizing
    print("\n📊 VOLATILITY-BASED SIZING:")
    for symbol, price, vol in [('AAPL', 180, 0.25), ('NVDA', 800, 0.45), ('JNJ', 160, 0.15)]:
        pos = sizer.size_by_volatility(symbol, price, vol)
        print(f"   {symbol}: {pos.shares} shares (${pos.dollar_amount:,.0f}) = {pos.weight_pct}%")
        print(f"      {pos.rationale}")
    
    # ATR-based sizing
    print("\n📐 ATR-BASED SIZING:")
    for symbol, price, atr in [('AAPL', 180, 3.50), ('TSLA', 250, 12.00), ('KO', 60, 1.00)]:
        pos = sizer.size_by_atr_stop(symbol, price, atr)
        print(f"   {symbol}: {pos.shares} shares (${pos.dollar_amount:,.0f}) = {pos.weight_pct}%")
        print(f"      {pos.rationale}")
    
    # Kelly sizing
    print("\n🎰 KELLY CRITERION SIZING:")
    pos = sizer.size_by_kelly('TEST', 100, win_rate=0.60, avg_win=15, avg_loss=10)
    print(f"   60% WR, 1.5 R/R: {pos.weight_pct}%")
    print(f"      {pos.rationale}")
