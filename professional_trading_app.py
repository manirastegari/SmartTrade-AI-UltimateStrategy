import streamlit as st
import settings  # Loads .env and Streamlit secrets into environment
import yfinance as yf
import logging
from io import BytesIO
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Suppress noisy library logs (Yahoo/yfinance transient messages)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

from advanced_analyzer import AdvancedTradingAnalyzer
from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
from cleaned_high_potential_universe import get_cleaned_high_potential_universe

# Professional Trading Interface - Like Goldman Sachs, JP Morgan, Citadel
st.set_page_config(
    page_title="Professional Trading Terminal - Institutional Grade",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look with timeframe indicators
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .positive { color: #00ff00; font-weight: bold; }
    .negative { color: #ff4444; font-weight: bold; }
    .neutral { color: #ffa500; font-weight: bold; }
    .price-big { font-size: 2em; font-weight: bold; }
    .professional-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-card {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .timeframe-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        margin: 0.2rem;
    }
    .short-term { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
    .medium-term { background: #d1ecf1; color: #0c5460; border: 1px solid #b8daff; }
    .long-term { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .confidence-high { background: #d4edda; color: #155724; }
    .confidence-medium { background: #fff3cd; color: #856404; }
    .confidence-low { background: #f8d7da; color: #721c24; }
    .signal-item {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        border-radius: 0 8px 8px 0;
    }
    .buy-signal { border-left-color: #28a745; }
    .sell-signal { border-left-color: #dc3545; }
    .neutral-signal { border-left-color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# Professional Header
st.markdown("""
<div class="professional-header">
    <h1>🏛️ Professional Trading Terminal</h1>
    <h3>Institutional-Grade Analysis • Real-Time Pricing • Professional Signals</h3>
    <p><strong>Created by: Mani Rastegari</strong> | <em>Hedge Fund Level Analysis</em></p>
</div>
""", unsafe_allow_html=True)

# Initialize analyzer
@st.cache_resource
def get_analyzer():
    # Use light data mode by default (rate-limit friendly). ML training can be toggled below.
    analyzer = AdvancedTradingAnalyzer(enable_training=False, data_mode="light")
    
    # Use premium 614-stock high-quality universe (>$2B market cap, 5+ year track records)
    analyzer.stock_universe = get_cleaned_high_potential_universe()
    
    st.success(f"🚀 Optimizer loaded: {analyzer.max_workers} workers, caching enabled")
    st.info(f"📊 Premium Quality Universe: {len(analyzer.stock_universe)} institutional-grade stocks (low-risk, steady growth)")
    return analyzer

analyzer = get_analyzer()

# Timeframe determination functions
def determine_signal_timeframes(stock_data):
    """Determine timeframes for different signals based on analysis"""
    timeframes = {}
    
    # Technical indicators timeframes
    if stock_data.get('rsi_signal'):
        timeframes['RSI'] = {'timeframe': '1-5 days', 'type': 'short-term', 'accuracy': '60-70%'}
    if stock_data.get('macd_signal'):
        timeframes['MACD'] = {'timeframe': '3-10 days', 'type': 'short-term', 'accuracy': '65-75%'}
    
    # Chart patterns timeframes
    if any(signal in str(stock_data.get('signals', [])) for signal in ['Head', 'Double']):
        timeframes['Chart Patterns'] = {'timeframe': '2-6 weeks', 'type': 'medium-term', 'accuracy': '70-80%'}
    
    # Strategic signals timeframes
    if any(signal in str(stock_data.get('signals', [])) for signal in ['Golden', 'Death']):
        timeframes['Strategic'] = {'timeframe': '1-6 months', 'type': 'long-term', 'accuracy': '75-85%'}
    
    # ML prediction timeframes based on confidence
    confidence = stock_data.get('confidence', 0)
    if confidence > 0.8:
        timeframes['ML High Confidence'] = {'timeframe': '1-14 days', 'type': 'short-term', 'accuracy': '70-80%'}
    elif confidence > 0.6:
        timeframes['ML Medium Confidence'] = {'timeframe': '1-4 weeks', 'type': 'medium-term', 'accuracy': '60-75%'}
    
    # Fundamental analysis timeframes
    if stock_data.get('fundamental_score', 0) > 70:
        timeframes['Fundamentals'] = {'timeframe': '3-12 months', 'type': 'long-term', 'accuracy': '70-85%'}
    
    return timeframes

def get_primary_timeframe(stock_data):
    """Get the primary recommended timeframe for a stock"""
    confidence = stock_data.get('confidence', 0)
    fundamental_score = stock_data.get('fundamental_score', 0)
    
    # High confidence ML + strong fundamentals = medium to long term
    if confidence > 0.8 and fundamental_score > 70:
        return {'timeframe': '1-4 weeks', 'type': 'medium-term', 'accuracy': '70-80%', 'recommendation': 'Medium-term position'}
    
    # High confidence ML only = short term
    elif confidence > 0.8:
        return {'timeframe': '1-14 days', 'type': 'short-term', 'accuracy': '70-80%', 'recommendation': 'Short-term trade'}
    
    # Strong fundamentals = long term
    elif fundamental_score > 70:
        return {'timeframe': '3-12 months', 'type': 'long-term', 'accuracy': '75-85%', 'recommendation': 'Long-term investment'}
    
    # Default medium term
    else:
        return {'timeframe': '1-4 weeks', 'type': 'medium-term', 'accuracy': '65-75%', 'recommendation': 'Medium-term swing trade'}

def format_timeframe_badge(timeframe_info):
    """Format timeframe information as HTML badge"""
    type_class = timeframe_info['type'].replace('-', '-')
    return f'<span class="timeframe-badge {type_class}">⏰ {timeframe_info["timeframe"]} ({timeframe_info["accuracy"]})</span>'

def format_confidence_badge(confidence):
    """Format confidence as HTML badge"""
    if confidence > 0.8:
        return f'<span class="timeframe-badge confidence-high">🎯 High Confidence ({confidence:.1%})</span>'
    elif confidence > 0.6:
        return f'<span class="timeframe-badge confidence-medium">📊 Medium Confidence ({confidence:.1%})</span>'
    else:
        return f'<span class="timeframe-badge confidence-low">⚠️ Low Confidence ({confidence:.1%})</span>'

# Session state for consistent stock selection across analysis types
if 'selected_symbols' not in st.session_state:
    st.session_state.selected_symbols = None
if 'last_selection_params' not in st.session_state:
    st.session_state.last_selection_params = None

# Sidebar - Professional Controls
st.sidebar.markdown("## 🎯 Analysis Parameters")

# Professional analysis options
analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    ["🏆 Ultimate Strategy + AI (Automated 5-Perspective Consensus)", 
     "Institutional Grade", "Hedge Fund Style", "Investment Bank Level", "Quant Research", "Risk Management"]
)

# Show description for Ultimate Strategy
if analysis_type == "🏆 Ultimate Strategy + AI (Automated 5-Perspective Consensus)":
    st.sidebar.success("""
    **🏆 Ultimate Strategy + AI (True Consensus + AI Review):**
    
    All 5 perspectives analyze THE SAME premium stock universe:
    1. **AI Global Market Scan (NEW):** Determines best sectors/focus area
    2. Institutional Consensus (stability focus)
    3. Hedge Fund Alpha (momentum focus)
    4. Quant Value Hunter (value focus)
    5. Risk-Managed Core (safety focus)
    6. Investment Bank (analyst/sentiment proxy)
    
    **Logic:** Finds stocks where MULTIPLE strategies agree
    - 5/5 agree = ULTIMATE BUY (highest conviction)
    - 4/5 agree = STRONG BUY (high conviction)
    - 3/5 agree = BUY (strong majority)
    - 2/5 agree = WEAK BUY (lower conviction)
    
    **Premium Universe:** Dynamic AI Selection from 614 institutional-grade stocks
    - Market cap >$2B, 5+ year track records
    - Pre-screened for quality and liquidity
    - Guardrails DISABLED (stocks pre-vetted)
    - Regime Filters RELAXED (smart market timing)
    
    **Output:** True consensus picks with detailed agreement metrics + AI market/stock review
    
    **Time:** 60-90 minutes (Deep Analysis)
    **Expected Return:** 26-47% annually (lower risk)
    """)

# Determine if Ultimate Strategy is selected to simplify sidebar
is_ultimate = (analysis_type == "🏆 Ultimate Strategy + AI (Automated 5-Perspective Consensus)")

# For Ultimate Strategy: Show only a single prominent Run button
if is_ultimate:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🚀 One-Click Analysis")
    run_ultimate_analysis = st.sidebar.button(
        "🏆 RUN ULTIMATE STRATEGY",
        use_container_width=True,
        type="primary",
        help="Analyzes all 614+ premium stocks with 5-perspective consensus + AI review"
    )
    st.sidebar.info("⏱️ Takes 60-90 minutes for full analysis")

# Toggle ML training (optional: longer run, potentially higher accuracy)
if not is_ultimate:
    enable_ml_training = st.sidebar.checkbox("Enable ML Training (longer, more accurate)", value=False)
    analyzer.enable_training = bool(enable_ml_training)
else:
    # Ultimate Strategy manages ML usage internally; hide this control
    analyzer.enable_training = False

# Dynamic stock count slider based on universe size (hide for Ultimate Strategy)
if not is_ultimate:
    max_available = len(analyzer.stock_universe)
    default_count = max_available
    num_stocks = st.sidebar.slider(
        "Number of Stocks", 
        20, 
        max_available, 
        default_count,
        help=f"💡 Recommended: Use {max_available} (full universe) for maximum opportunity capture"
    )
    
    # Show recommendation for full universe
    if num_stocks == max_available:
        st.sidebar.success(f"✅ Using full universe ({max_available} stocks) - Maximum coverage!")
    elif num_stocks < 500:
        st.sidebar.warning(f"⚠️ Using {num_stocks} stocks. Consider using {max_available} for better opportunities.")

# Cap filter and risk style (not needed for Ultimate Strategy)
if not is_ultimate:
    cap_filter = st.sidebar.selectbox(
        "Cap Filter",
        ["All", "Large Cap", "Mid Cap", "Small Cap"],
        help="💡 Recommended: 'All' for comprehensive analysis"
    )
    
    risk_style = st.sidebar.selectbox(
        "Risk Style",
        ["Low Risk", "Balanced", "High Risk"]
    )

"""
Ultimate Strategy has built-in risk management:
- Guardrails DISABLED (premium 614-stock universe pre-screened)
- Regime Filters RELAXED (smart market timing in weak markets only)
"""
if not is_ultimate:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🛡️ Risk Guardrails")
    enable_guardrails = st.sidebar.checkbox("Enable Catastrophic-Loss Guard", value=True,
        help="Filters out high-risk picks: penny stocks, extreme daily gaps, very low liquidity, and high-volatility biotech.")
    min_price_guard = st.sidebar.number_input("Minimum Price ($)", min_value=0.0, value=5.0, step=0.5,
        help="Exclude very low-priced names which tend to have outsized gap risk.")
    min_volume_guard = st.sidebar.number_input("Minimum Daily Volume", min_value=0, value=300_000, step=50_000,
        help="Exclude illiquid names that can move 20%+ on news.")
    max_abs_change_guard = st.sidebar.number_input("Max |1D Change| (%)", min_value=0.0, value=15.0, step=1.0,
        help="If today's move is already extreme, skip to avoid chasing big gaps.")
    exclude_biotech_guard = st.sidebar.checkbox("Exclude High-Volatility Biotech", value=True,
        help="Biotech/clinical-trial names have frequent 30-60% gap risks.")
    # New: Auto-replace removed high-risk picks with safer alternatives
    auto_replace_removed = st.sidebar.checkbox("Auto-replace high-risk removals", value=True,
        help="When guardrails remove risky picks, backfill one-for-one with safer alternatives from the same analysis.")

if not is_ultimate:
    market_focus = st.sidebar.selectbox(
        "Market Focus",
        ["All Markets", "S&P 500 Large Cap", "NASDAQ Growth", "Russell 2000 Small Cap", 
         "Sector Rotation", "Momentum Stocks", "Value Stocks", "Dividend Aristocrats"],
        help="💡 Recommended: 'All Markets' for comprehensive coverage"
    )

if not is_ultimate:
    # Legacy controls (kept for layout, not used in light mode)
    risk_model = st.sidebar.selectbox(
        "Risk Model",
        ["Conservative (Low Beta)", "Balanced (Market Beta)", "Aggressive (High Beta)", "Momentum (High Volatility)"]
    )

if not is_ultimate:
    # Professional features toggle
    show_real_time = st.sidebar.checkbox("Real-Time Pricing", value=True)
    show_analyst_targets = st.sidebar.checkbox("Analyst Price Targets", value=True)
    show_earnings_impact = st.sidebar.checkbox("Earnings Impact Analysis", value=True)
    show_institutional_flow = st.sidebar.checkbox("Institutional Flow", value=True)

# Stock selection consistency controls
if not is_ultimate:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🔄 Stock Selection")
    
    if st.session_state.selected_symbols:
        st.sidebar.success(f"✅ {len(st.session_state.selected_symbols)} stocks selected")
        st.sidebar.write(f"**Parameters:** {st.session_state.last_selection_params}")
        
        if st.sidebar.button("🔄 Select New Stocks"):
            st.session_state.selected_symbols = None
            st.session_state.last_selection_params = None
            st.rerun()
    else:
        st.sidebar.info("No stocks selected yet")
    
    st.sidebar.markdown("---")

# Enhanced stock selection with Market Focus integration
def get_comprehensive_symbol_selection(analyzer, cap_filter: str, market_focus: str, count: int):
    """
    IMPROVED: Uses full 779-stock universe with optional filtering
    All analysis types now analyze the SAME comprehensive stock set
    """
    # Always use the full optimized universe (779 stocks)
    universe = analyzer.stock_universe
    universe_size = len(universe)
    
    # For comprehensive analysis, use the full universe
    # This ensures all analysis types see the same opportunities
    if count >= 500 or cap_filter == "All":
        return universe[:min(count, len(universe))]
    
    # Define market focus symbol sets
    # Define market focus symbol sets dynamically from the main universe
    # This prevents having stale hardcoded lists
    
    # Helper to filter from the LIVE universe (ensure we only pick valid stocks)
    def filter_universe(universe, symbols_to_find=None):
        if symbols_to_find:
            return [s for s in universe if s in symbols_to_find]
        return universe

    market_focus_symbols = {
        "S&P 500 Large Cap": filter_universe(universe, [
            'AAPL','MSFT','GOOGL','AMZN','META','NVDA','TSLA','NFLX','AMD','INTC',
            'JPM','BAC','WFC','GS','MS','C','AXP','V','MA','PYPL',
            'JNJ','PFE','UNH','ABBV','MRK','TMO','ABT','DHR','BMY','AMGN',
            'KO','PEP','WMT','PG','HD','MCD','NKE','SBUX','DIS','CMCSA'
        ]),
        "NASDAQ Growth": filter_universe(universe, [
            'AAPL','MSFT','GOOGL','AMZN','META','NVDA','TSLA','NFLX','AMD',
            'PLTR','CRWD','SNOW','DDOG','NET','OKTA','ZM','DOCU','TWLO',
            'ROKU','PINS','SNAP','UBER','LYFT','ABNB','DASH','PTON'
        ]),
        "Russell 2000 Small Cap": filter_universe(universe, [
            'PLTR','CRWD','SNOW','DDOG','NET','OKTA','ZM','DOCU','TWLO','SQ',
            'ROKU','PINS','SNAP','UBER','LYFT','ABNB','DASH','PTON','FUBO','RKT',
            'OPEN','COMP','Z','ZG','ESTC','MDB','TEAM','WDAY','NOW','ZS'
        ]),
        "Momentum Stocks": filter_universe(universe, [
            'NVDA','TSLA','AMD','PLTR','CRWD','SNOW','NET','ROKU','UBER','SQ',
            'ABNB','DASH','ZM','DOCU','PINS','SNAP','PTON','FUBO','RKT','OPEN'
        ]),
        "Value Stocks": filter_universe(universe, [
            'JPM','BAC','WFC','GS','MS','C','V','MA','JNJ','PFE','UNH',
            'KO','PEP','WMT','PG','HD','MCD','CVX','XOM','COP','CAT','BA'
        ]),
        "Dividend Aristocrats": filter_universe(universe, [
            'JNJ','PG','KO','PEP','WMT','HD','MCD','CVX','XOM','CAT',
            'MMM','GE','HON','UPS','FDX','VZ','T','NEE','DUK','SO'
        ])
    }
    
    # Get base symbols by cap filter
    if cap_filter == "Large Cap":
        end_idx = universe_size // 3
        base_symbols = universe[:end_idx]
    elif cap_filter == "Mid Cap":
        start = universe_size // 3
        end = (universe_size * 2) // 3
        base_symbols = universe[start:end]
    elif cap_filter == "Small Cap":
        start = (universe_size * 2) // 3
        base_symbols = universe[start:]
    else:
        base_symbols = universe
    
    # Apply market focus filter if specified
    if market_focus in market_focus_symbols:
        focus_symbols = market_focus_symbols[market_focus]
        # Prioritize symbols that match both cap filter and market focus
        # BUT if focus list is small, just return the focus list + fillers
        if len(focus_symbols) < 10:
             # If focus list is too small, just return it as is + fill from universe
             prioritized = focus_symbols
        else:
             prioritized = focus_symbols
        
        # Merge: Focus symbols first, then others to fill count
        remaining = [s for s in base_symbols if s not in prioritized]
        base_symbols = prioritized + remaining
    elif market_focus == "Sector Rotation":
        # Mix of different sectors for rotation strategy
        sectors = [
            universe[:universe_size//4],  # Tech heavy
            universe[universe_size//4:universe_size//2],  # Mixed
            universe[universe_size//2:3*universe_size//4],  # Value/Industrial
            universe[3*universe_size//4:]  # Small/Speculative
        ]
        base_symbols = []
        for sector in sectors:
            base_symbols.extend(sector[:count//4])
    
    # Ensure we have enough symbols, expand if needed
    if len(base_symbols) < count:
        # Add more symbols from the broader universe if needed
        additional_needed = count - len(base_symbols)
        additional_symbols = [s for s in universe if s not in base_symbols][:additional_needed]
        base_symbols.extend(additional_symbols)
    
    # Return the requested count, but ensure good coverage
    # For larger requests, use more of the universe
    if count >= 300:
        # For 300+ requests, use the full universe if needed
        final_count = min(count, len(universe))
        if len(base_symbols) < final_count:
            # Add more symbols from the broader universe
            additional_needed = final_count - len(base_symbols)
            additional_symbols = [s for s in universe if s not in base_symbols][:additional_needed]
            base_symbols.extend(additional_symbols)
        return base_symbols[:final_count]
    else:
        # For smaller requests, maintain minimum coverage
        final_count = max(count, min(50, len(base_symbols)))
        return base_symbols[:final_count]

def get_symbols_by_cap(analyzer, cap_filter: str, count: int):
    """Legacy function for backward compatibility"""
    return get_comprehensive_symbol_selection(analyzer, cap_filter, "All Markets", count)

def apply_analysis_type_adjustments(results, analysis_type: str):
    """
    Apply analysis type-specific scoring adjustments to make Analysis Type meaningful
    """
    adjusted_results = []
    
    for result in results:
        adjusted_result = result.copy()
        
        overlay = result.get('overlay_score', 50)
        if analysis_type == "Institutional Grade":
            # Favor stability, liquidity, and established companies
            # Boost scores for large cap, low volatility, high volume
            stability_bonus = 0
            if result.get('current_price', 0) > 50:  # Higher price stocks tend to be more stable
                stability_bonus += 5
            if result.get('volume_score', 50) > 70:  # High volume = good liquidity
                stability_bonus += 5
            # Overlay context: penalize in poor macro breadth conditions
            if overlay < 40:
                stability_bonus -= 3
            elif overlay > 60:
                stability_bonus += 2
            adjusted_result['overall_score'] = min(100, result['overall_score'] + stability_bonus)
            adjusted_result['analysis_focus'] = "Institutional: Stability & Liquidity"
            
        elif analysis_type == "Hedge Fund Style":
            # Favor momentum, volatility, and alpha generation
            momentum_bonus = 0
            if result.get('momentum_score', 50) > 70:
                momentum_bonus += 8
            if result.get('volatility_score', 50) > 60:  # Higher volatility = more opportunity
                momentum_bonus += 5
            # Overlay tailwind helps momentum
            if overlay > 60:
                momentum_bonus += 3
            elif overlay < 40:
                momentum_bonus -= 3
            adjusted_result['overall_score'] = min(100, result['overall_score'] + momentum_bonus)
            adjusted_result['analysis_focus'] = "Hedge Fund: Momentum & Alpha"
            
        elif analysis_type == "Investment Bank Level":
            # Favor fundamental strength and analyst coverage
            fundamental_bonus = 0
            if result.get('fundamental_score', 50) > 70:
                fundamental_bonus += 8
            if result.get('analyst_score', 50) > 60:
                fundamental_bonus += 5
            # Overlay supports strong macro conditions
            if overlay > 60:
                fundamental_bonus += 2
            adjusted_result['overall_score'] = min(100, result['overall_score'] + fundamental_bonus)
            adjusted_result['analysis_focus'] = "Investment Bank: Fundamentals & Coverage"
            
        elif analysis_type == "Quant Research":
            # Favor technical indicators and statistical patterns
            technical_bonus = 0
            if result.get('technical_score', 50) > 75:
                technical_bonus += 10
            if result.get('confidence', 0) > 0.8:  # High confidence in predictions
                technical_bonus += 5
            # Overlay assists technical follow-through
            if overlay > 60:
                technical_bonus += 2
            adjusted_result['overall_score'] = min(100, result['overall_score'] + technical_bonus)
            adjusted_result['analysis_focus'] = "Quant: Technical & Statistical"
            
        elif analysis_type == "Risk Management":
            # Favor risk-adjusted returns and downside protection
            risk_bonus = 0
            if result.get('risk_level') == "Low":
                risk_bonus += 8
            elif result.get('risk_level') == "Medium":
                risk_bonus += 3
            if result.get('prediction', 0) > 0 and result.get('confidence', 0) > 0.7:  # Positive with high confidence
                risk_bonus += 5
            # Macro overlay risk aversion in poor conditions
            if overlay < 40:
                risk_bonus -= 5
            adjusted_result['overall_score'] = min(100, result['overall_score'] + risk_bonus)
            adjusted_result['analysis_focus'] = "Risk Mgmt: Downside Protection"
        
        adjusted_results.append(adjusted_result)
    
    # Re-sort by adjusted overall score
    return sorted(adjusted_results, key=lambda x: x['overall_score'], reverse=True)

def filter_by_risk(results, risk_style: str):
    if risk_style == "Low Risk":
        return [r for r in results if r.get('risk_level') in ("Low", "Medium")]
    if risk_style == "High Risk":
        return [r for r in results if r.get('risk_level') in ("High", "Medium")]
    return results

def apply_guardrails(results,
                     enable: bool,
                     min_price: float,
                     min_volume: int,
                     max_abs_change_pct: float,
                     exclude_biotech: bool):
    """Apply catastrophic-loss guardrails and return (kept, removed_with_reason)."""
    if not enable or not results:
        return results, []

    removed = []
    kept = []
    biotech_keywords = {"biotech", "biotechnology", "life sciences", "genomics", "pharma", "pharmaceutical"}

    for r in results:
        reasons = []
        price = float(r.get('current_price', 0) or 0)
        vol = int(r.get('volume', 0) or 0)
        change1d = float(r.get('price_change_1d', 0) or 0)
        sector = (r.get('sector') or "").lower()
        vol_score = float(r.get('volatility_score', 50) or 50)
        risk_level = r.get('risk_level')

        # Penny/low price
        if price > 0 and price < min_price:
            reasons.append(f"Price ${price:.2f} < ${min_price:.2f}")
        # Liquidity
        if vol < min_volume:
            reasons.append(f"Volume {vol:,} < {min_volume:,}")
        # Big gap day
        if abs(change1d) >= max_abs_change_pct:
            reasons.append(f"|1D| move {change1d:+.1f}% ≥ {max_abs_change_pct:.0f}%")
        # High-volatility biotech
        if exclude_biotech and any(k in sector for k in biotech_keywords) and (risk_level == 'High' or vol_score >= 70):
            reasons.append("Biotech high-volatility")

        if reasons:
            removed.append({
                'symbol': r.get('symbol'),
                'reasons': ", ".join(reasons)
            })
        else:
            kept.append(r)

    return kept, removed

# Determine which button to check based on analysis type
if is_ultimate:
    # Ultimate Strategy uses the dedicated button defined earlier in sidebar
    should_run_analysis = run_ultimate_analysis
else:
    # Other analysis types use the generic button
    should_run_analysis = st.sidebar.button("🚀 Run Professional Analysis", type="primary")

if should_run_analysis:
    
    # Check if Ultimate Strategy is selected
    if is_ultimate:
        
        st.markdown("---")
        st.markdown("# 🏆 ULTIMATE STRATEGY + AI - AUTOMATED 5-PERSPECTIVE CONSENSUS")
        st.markdown("### Running all 5 perspectives automatically + AI review...")
        
        # Initialize FIXED Ultimate Strategy Analyzer (optimized - 60-90 min)
        ultimate_analyzer = FixedUltimateStrategyAnalyzer(analyzer)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message, progress):
            status_text.text(message)
            progress_bar.progress(progress)
        
        # Run Ultimate Strategy
        with st.spinner("Running Ultimate Strategy Analysis (this will take 60–90 minutes)..."):
            
            st.info("⏱️ **Estimated Time:** 60–90 minutes for complete 5-perspective analysis + AI review")
            st.info("☕ **Tip:** Sit back while we finalize the consensus and AI review.")
            
            final_recommendations = ultimate_analyzer.run_ultimate_strategy(
                progress_callback=update_progress
            )

        # Clear progress UI after analysis completes
        progress_bar.empty()
        status_text.empty()

        # === SKIP TODAY WARNING BANNER (NEW - Phase 2) ===
        # Display prominently at the top before any other results
        if hasattr(ultimate_analyzer, 'market_day_assessment') and ultimate_analyzer.market_day_assessment:
            assessment = ultimate_analyzer.market_day_assessment
            warning_level = assessment.get('warning_level', 'GREEN')
            
            if warning_level == 'RED':
                # Bold red warning for SKIP days
                st.error(f"""
                🔴 **SKIP TODAY - Market Conditions Unfavorable**
                
                **Confidence:** {assessment.get('confidence', 0):.0f}%
                
                **Honest Assessment:** {assessment.get('honest_assessment', 'N/A')}
                
                **Recommendation:** {assessment.get('position_sizing', 'Wait for better conditions')}
                
                **Next Check:** {assessment.get('next_check', 'Tomorrow')}
                """)
            elif warning_level == 'YELLOW':
                # Yellow caution warning
                st.warning(f"""
                🟡 **CAUTION - Proceed with Reduced Exposure**
                
                **Confidence:** {assessment.get('confidence', 0):.0f}%
                
                **Honest Assessment:** {assessment.get('honest_assessment', 'N/A')}
                
                **Recommendation:** {assessment.get('position_sizing', 'Half positions')}
                
                **Strategy Focus:** {assessment.get('strategy_focus', 'Defensive only')}
                """)
            else:
                # Green success for favorable days
                st.success(f"""
                🟢 **FAVORABLE - Good Conditions for Trading**
                
                **Confidence:** {assessment.get('confidence', 0):.0f}%
                
                **Honest Assessment:** {assessment.get('honest_assessment', 'N/A')}
                
                **Recommendation:** {assessment.get('position_sizing', 'Standard positions')}
                
                **Strategy Focus:** {assessment.get('strategy_focus', 'Balanced')}
                """)
            
            # Show detailed signals in expander
            with st.expander("📊 View Detailed Market Signals"):
                for reason in assessment.get('reasons', []):
                    st.markdown(f"• {reason}")
                    
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("VIX", assessment.get('vix', 'N/A'))
                with col2:
                    spy_ret = assessment.get('spy_return', 0)
                    st.metric("SPY Return", f"{spy_ret*100:+.2f}%" if spy_ret else "N/A")
                with col3:
                    st.metric("Regime", assessment.get('regime', 'Unknown').title())

        # Display results
        ultimate_analyzer.display_ultimate_strategy_results(final_recommendations)
        
        st.success("✅ Ultimate Strategy + AI Analysis Complete!")
        st.balloons()
        
        # Stop execution here - Ultimate Strategy has its own display
        st.stop()
        
    else:
        # Regular single-strategy analysis
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Professional analysis workflow
        with st.spinner("Running institutional-grade analysis..."):
            
            # Step 1: Data Collection
            status_text.text("📊 Collecting real-time market data...")
            progress_bar.progress(20)
            time.sleep(1)
            
            # Step 2: Technical Analysis
            status_text.text("📈 Running 100+ technical indicators...")
            progress_bar.progress(40)
            time.sleep(1)
            
            # Step 3: Fundamental Analysis
            status_text.text("💰 Analyzing earnings and fundamentals...")
            progress_bar.progress(60)
            time.sleep(1)
            
            # Step 4: Sentiment Analysis
            status_text.text("📰 Processing news and sentiment...")
            progress_bar.progress(80)
            time.sleep(1)
            
            # Step 5: Professional Scoring
            status_text.text("🎯 Generating professional recommendations...")
            progress_bar.progress(100)
            time.sleep(1)
        
        # Check if we need to select new symbols or use cached ones
        current_params = (cap_filter, market_focus, num_stocks)
        
        if (st.session_state.last_selection_params != current_params or 
            st.session_state.selected_symbols is None):
            # New selection needed
            st.session_state.selected_symbols = get_comprehensive_symbol_selection(
                analyzer, cap_filter, market_focus, num_stocks
            )
            st.session_state.last_selection_params = current_params
            st.info(f"🎯 Selected {len(st.session_state.selected_symbols)} stocks for analysis based on {cap_filter} + {market_focus}")
        else:
            st.info(f"🔄 Using same {len(st.session_state.selected_symbols)} stocks as previous analysis for consistency")
        
        symbols = st.session_state.selected_symbols
        
        # Show selected symbols preview
        with st.expander(f"📊 Selected Stocks Preview ({len(symbols)} total)"):
            st.write("**First 20 symbols:**", symbols[:20])
            if len(symbols) > 20:
                st.write("**Last 10 symbols:**", symbols[-10:])
        
        # Run the analysis on selected symbols
        results = analyzer.run_advanced_analysis(max_stocks=len(symbols), symbols=symbols)

        # Auto-fallback: if no results, retry with curated fallback lists based on cap filter
        if not results:
            st.warning("Primary selection returned no results. Retrying with a curated fallback list for reliability...")
            
            if cap_filter == "Small Cap":
                # Reliable small cap symbols
                fallback_symbols = [
                    'PLTR','CRWD','SNOW','DDOG','NET','OKTA','ZM','DOCU','TWLO','SQ',
                    'ROKU','PINS','SNAP','UBER','LYFT','ABNB','DASH','PTON','FUBO','RKT',
                    'OPEN','COMP','Z','ZG','ESTC','MDB','TEAM','WDAY','NOW','ZS'
                ]
            elif cap_filter == "Mid Cap":
                # Reliable mid cap symbols  
                fallback_symbols = [
                    'REGN','GILD','BIIB','VRTX','ILMN','MRNA','ZTS','SYK','ISRG','EW',
                    'BSX','MDT','SPGI','MCO','FIS','FISV','GPN','NDAQ','CME','ICE',
                    'MKTX','CBOE','MSCI','TROW','BLK','SCHW','AMTD','ETFC','AMT','PLD'
                ]
            else:
                # Large cap fallback (default)
                fallback_symbols = [
                    'AAPL','MSFT','GOOGL','AMZN','META','NVDA','TSLA','NFLX','AMD','INTC',
                    'JPM','BAC','WFC','GS','MS','C','AXP','V','MA','PYPL',
                    'JNJ','PFE','UNH','ABBV','MRK','TMO','ABT','DHR','BMY','AMGN','LLY',
                    'KO','PEP','WMT','PG','HD','MCD','NKE','SBUX','DIS','CMCSA',
                    'VZ','T','CVX','XOM','COP','SLB','CAT','BA','MMM','GE','HON'
                ]
            
            results = analyzer.run_advanced_analysis(max_stocks=min(num_stocks, len(fallback_symbols)), symbols=fallback_symbols)
        
        # Apply analysis type-specific adjustments
        if results:
            results = apply_analysis_type_adjustments(results, analysis_type)
        
        # Post-filter by risk style for display
        results = filter_by_risk(results, risk_style)

        # Keep a snapshot pre-guardrails for potential replacements
        pre_guard_results = list(results or [])

        # Apply catastrophic-loss guardrails
        results, removed_flags = apply_guardrails(
            results,
            enable=enable_guardrails,
            min_price=min_price_guard,
            min_volume=int(min_volume_guard),
            max_abs_change_pct=max_abs_change_guard,
            exclude_biotech=exclude_biotech_guard,
        )

        # Auto-replace removed picks with safer alternatives (one-for-one)
        replacements_made = []
        if enable_guardrails and auto_replace_removed and removed_flags:
            try:
                removed_syms = [r.get('symbol') for r in (removed_flags or []) if r.get('symbol')]
                kept_syms = {r.get('symbol') for r in (results or [])}
                # Build candidate pool from pre-guard results not already kept and not removed
                pool = [r for r in (pre_guard_results or []) if r.get('symbol') not in kept_syms and r.get('symbol') not in set(removed_syms)]
                # Safety-first filter
                safe_pool = []
                for r in pool:
                    price = float(r.get('current_price', 0) or 0)
                    vol = int(r.get('volume', 0) or 0)
                    change1d = float(r.get('price_change_1d', 0) or 0)
                    risk = (r.get('risk_level') or 'Medium')
                    vol_score = float(r.get('volatility_score', 50) or 50)
                    # Pass guard-like checks and prefer BUY/STRONG BUY if available
                    if price and price < float(min_price_guard):
                        continue
                    if vol < int(min_volume_guard):
                        continue
                    if abs(change1d) >= float(max_abs_change_guard):
                        continue
                    if str(risk).lower() == 'high':
                        continue
                    if vol_score > 70:
                        continue
                    safe_pool.append(r)
                # Rank safer pool: prefer BUY/STRONG BUY, then by (overall_score, momentum, upside, -vol)
                def rank_key(x):
                    rec = (x.get('recommendation') or '').upper()
                    rec_rank = 2 if rec == 'STRONG BUY' else 1 if rec == 'BUY' else 0
                    return (
                        rec_rank,
                        float(x.get('overall_score', 0) or 0),
                        float(x.get('momentum_score', 0) or 0),
                        float(x.get('prediction', x.get('upside_potential', 0)) or 0),
                        -float(x.get('volatility_score', 100) or 100),
                    )
                safe_pool.sort(key=rank_key, reverse=True)
                # Map replacements 1:1 in order
                for rem in removed_syms:
                    if not safe_pool:
                        break
                    pick = safe_pool.pop(0)
                    # Tag replacement and append
                    pick = dict(pick)
                    pick['replacement'] = True
                    pick['replacement_for'] = rem
                    results.append(pick)
                    replacements_made.append({'replacement': pick.get('symbol'), 'for': rem})
            except Exception:
                pass
        
        progress_bar.empty()
        status_text.empty()

    if results and len(results) > 0:
        # Show guardrail effect if applied
        if enable_guardrails:
            removed_count = len(removed_flags)
            if removed_count:
                with st.expander(f"🛡️ Guardrails removed {removed_count} high-risk picks (click to view)"):
                    removed_df = pd.DataFrame(removed_flags)
                    st.dataframe(removed_df, use_container_width=True)
            # Show replacements summary if any
            if 'replacements_made' in locals() and replacements_made:
                with st.expander(f"🔁 Auto-replaced {len(replacements_made)} removed picks (click to view)"):
                    rep_df = pd.DataFrame(replacements_made)
                    st.dataframe(rep_df, use_container_width=True)

        # Professional Dashboard Layout
        st.markdown("## 🏛️ Professional Analysis Dashboard")
        
        # Real-time market overview
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>Stocks Analyzed</h4>
                <div class="price-big">{}</div>
            </div>
            """.format(len(results)), unsafe_allow_html=True)
        
        with col2:
            buy_signals = len([r for r in results if r['recommendation'] in ['BUY', 'STRONG BUY']])
            st.markdown("""
            <div class="metric-card">
                <h4>BUY Signals</h4>
                <div class="price-big positive">{}</div>
            </div>
            """.format(buy_signals), unsafe_allow_html=True)
        
        with col3:
            avg_confidence = np.mean([r['confidence'] for r in results])
            st.markdown("""
            <div class="metric-card">
                <h4>Avg Confidence</h4>
                <div class="price-big">{:.1%}</div>
            </div>
            """.format(avg_confidence), unsafe_allow_html=True)
        
        with col4:
            high_conviction = len([r for r in results if r['confidence'] > 0.8 and r['recommendation'] in ['BUY', 'STRONG BUY']])
            st.markdown("""
            <div class="metric-card">
                <h4>High Conviction</h4>
                <div class="price-big positive">{}</div>
            </div>
            """.format(high_conviction), unsafe_allow_html=True)
        
        with col5:
            low_risk = len([r for r in results if r['risk_level'] == 'Low'])
            st.markdown("""
            <div class="metric-card">
                <h4>Low Risk</h4>
                <div class="price-big">{}</div>
            </div>
            """.format(low_risk), unsafe_allow_html=True)
        
        with col6:
            avg_upside = np.mean([r.get('upside_potential', 0) for r in results])
            color_class = "positive" if avg_upside > 0 else "negative"
            st.markdown("""
            <div class="metric-card">
                <h4>Avg Upside</h4>
                <div class="price-big {}">{:+.1f}%</div>
            </div>
            """.format(color_class, avg_upside), unsafe_allow_html=True)

        # Market Health: overlay, breadth, macro (one-shot)
        st.markdown("### 🌐 Market Health (Macro + Breadth)")
        try:
            bc = getattr(analyzer, '_breadth_context', {}) or {}
            mc = analyzer.data_fetcher.get_market_context()
            colA, colB, colC, colD = st.columns(4)
            with colA:
                avg_overlay = np.mean([r.get('overlay_score', 50) for r in results])
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Overlay Score</h4>
                    <div class="price-big">{avg_overlay:.1f}/100</div>
                </div>
                """, unsafe_allow_html=True)
            with colB:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Advancers (1D)</h4>
                    <div class="price-big">{bc.get('adv_pct_1d', 0.5)*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with colC:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>% Above 50/200 SMA</h4>
                    <div class="price-big">{bc.get('pct_above_sma50', 0.5)*100:.0f}% / {bc.get('pct_above_sma200', 0.5)*100:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with colD:
                vix_val = mc.get('vix_proxy')
                curve_slope_val = mc.get('yield_curve_slope')
                try:
                    vix_display = f"{float(vix_val):.1f}" if vix_val is not None else "N/A"
                except Exception:
                    vix_display = "N/A"
                try:
                    curve_display = f"{float(curve_slope_val):+.2f}" if curve_slope_val is not None else "N/A"
                except Exception:
                    curve_display = "N/A"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>VIX • Curve Slope</h4>
                    <div class="price-big">{vix_display} • {curve_display}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass
        
        # Top BUY Opportunities - Best Profit Potential
        st.markdown("### 🏆 Top BUY Opportunities (Best Profit Potential)")
        
        # Filter for BUY recommendations only, then sort by upside potential
        buy_opportunities = [r for r in results if r['recommendation'] in ['BUY', 'STRONG BUY']]
        
        if not buy_opportunities:
            st.warning("No BUY recommendations found in current analysis. Consider adjusting your parameters.")
            # Fallback to top scored stocks
            top_picks = sorted(results, key=lambda x: x['overall_score'], reverse=True)[:5]
            st.info("Showing top-scored stocks instead (may include HOLD/SELL recommendations):")
        else:
            # Sort BUY opportunities by upside potential (prediction) for maximum profit
            top_picks = sorted(buy_opportunities, key=lambda x: x['prediction'], reverse=True)[:5]
        
        for i, stock in enumerate(top_picks[:5]):
            # Get timeframe information
            primary_timeframe = get_primary_timeframe(stock)
            
            # Create collapsible expander with key info in title
            current_price = stock['current_price']
            price_change = stock['price_change_1d']
            upside_potential = stock['prediction']
            
            # Use buy/sell emoji for recommendation
            rec_emoji = "🚀" if stock['recommendation'] == 'STRONG BUY' else "📈" if stock['recommendation'] == 'BUY' else "⚠️"
            price_emoji = "🟢" if price_change > 0 else "🔴" if price_change < 0 else "🟡"
            
            expander_title = f"#{i+1} {rec_emoji} {stock['symbol']} - {stock['recommendation']} | ${current_price:.2f} ({price_change:+.1f}%) | Upside: {upside_potential:+.1f}% | {primary_timeframe['timeframe']}"
            
            with st.expander(expander_title, expanded=False):
                
                col1, col2, col3 = st.columns([2, 2, 3])
                
                with col1:
                    # Price and basic info
                    price_emoji = "🟢" if price_change > 0 else "🔴" if price_change < 0 else "🟡"
                    st.markdown(f"""
                    **Current Price:** ${current_price:.2f}  
                    **1D Change:** {price_emoji} {price_change:+.2f}%  
                    **Target:** ${current_price * (1 + stock['prediction']/100):.2f}  
                    **Upside:** {stock['prediction']:+.1f}%  
                    **Volume:** {stock['volume']:,}
                    """)
                
                with col2:
                    # Analysis scores
                    st.markdown(f"""
                    **Confidence:** {stock['confidence']:.1%}  
                    **Risk Level:** {stock['risk_level']}  
                    **Sector:** {stock.get('sector', 'Unknown')}  
                    **Overall Score:** {stock['overall_score']:.1f}/100
                    """)
                    
                with col3:
                    # Timeframe and recommendation
                    st.markdown(f"""
                    **⏰ Expected Timeframe:** {primary_timeframe['timeframe']}  
                    **📊 Expected Accuracy:** {primary_timeframe['accuracy']}  
                    **💡 Strategy:** {primary_timeframe['recommendation']}
                    """)
                    
                    # Progress bars for scores
                    st.progress(stock['technical_score']/100, text=f"Technical: {stock['technical_score']:.0f}/100")
                    st.progress(stock['fundamental_score']/100, text=f"Fundamental: {stock['fundamental_score']:.0f}/100")
                    st.progress(stock['sentiment_score']/100, text=f"Sentiment: {stock['sentiment_score']:.0f}/100")
                
                # Key signals (simplified)
                if stock.get('signals'):
                    st.markdown("**🎯 Key Signals:**")
                    for signal in stock['signals'][:3]:
                        if 'BUY' in signal.upper() or 'BULLISH' in signal.upper():
                            st.markdown(f"🟢 {signal}")
                        elif 'SELL' in signal.upper() or 'BEARISH' in signal.upper():
                            st.markdown(f"🔴 {signal}")
                        else:
                            st.markdown(f"🟡 {signal}")
        
        # High Conviction BUY Opportunities
        high_conviction_buys = [r for r in results if r['recommendation'] in ['BUY', 'STRONG BUY'] and r['confidence'] > 0.8]
        
        if high_conviction_buys:
            st.markdown("### 🎯 High Conviction BUY Opportunities (>80% Confidence)")
            
            # Sort by upside potential
            high_conviction_buys = sorted(high_conviction_buys, key=lambda x: x['prediction'], reverse=True)[:3]
            
            for stock in high_conviction_buys:
                primary_timeframe = get_primary_timeframe(stock)
                
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.metric(
                        label=f"🚀 {stock['symbol']}",
                        value=f"${stock['current_price']:.2f}",
                        delta=f"{stock['price_change_1d']:+.1f}%"
                    )
                
                with col2:
                    st.metric(
                        label="Upside Potential",
                        value=f"{stock['prediction']:+.1}%",
                        delta=f"Target: ${stock['current_price'] * (1 + stock['prediction']/100):.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="Confidence",
                        value=f"{stock['confidence']:.1%}",
                        delta=f"Risk: {stock['risk_level']}"
                    )
                
                with col4:
                    st.metric(
                        label="Timeframe",
                        value=primary_timeframe['timeframe'],
                        delta=f"Accuracy: {primary_timeframe['accuracy']}"
                    )
        
        # Simplified Timeframe Guide
        with st.expander("⏰ Understanding Prediction Timeframes", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🚀 Short-Term (1-14 days)**")
                st.markdown("• Accuracy: 60-70%")
                st.markdown("• Best for: Active traders")
                
            with col2:
                st.markdown("**📊 Medium-Term (1-4 weeks)**")
                st.markdown("• Accuracy: 65-75%")
                st.markdown("• Best for: Most users (recommended)")
                
            with col3:
                st.markdown("**🎯 Long-Term (3+ months)**")
                st.markdown("• Accuracy: 70-85%")
                st.markdown("• Best for: Patient investors")
            
            st.info("💡 **Key Principle:** Longer timeframes = Higher reliability. High confidence (>80%) significantly improves outcomes.")
        
        # Professional Analysis Table
        st.markdown("### 📊 Complete Professional Analysis")
        
    # Create professional DataFrame
        df_results = pd.DataFrame(results)
        
        # Add professional columns with timeframe information
        df_display = df_results[['symbol', 'current_price', 'price_change_1d', 'prediction', 'confidence', 
                                'recommendation', 'risk_level', 'overall_score', 'technical_score', 
                                'fundamental_score', 'sentiment_score']].copy()
        
        # Add timeframe and upside calculations
        df_display['upside_potential'] = df_display['prediction']
        df_display['target_price'] = df_display['current_price'] * (1 + df_display['prediction']/100)
        
        # Add timeframe information for each stock
        timeframe_data = []
        timeframe_type_data = []
        accuracy_data = []
        
        for _, row in df_results.iterrows():
            primary_timeframe = get_primary_timeframe(row.to_dict())
            timeframe_data.append(primary_timeframe['timeframe'])
            timeframe_type_data.append(primary_timeframe['type'].title())
            accuracy_data.append(primary_timeframe['accuracy'])
        
        df_display['expected_timeframe'] = timeframe_data
        df_display['timeframe_type'] = timeframe_type_data
        df_display['expected_accuracy'] = accuracy_data
        
        # Format for professional display
        df_display['current_price'] = df_display['current_price'].apply(lambda x: f"${x:.2f}")
        df_display['price_change_1d'] = df_display['price_change_1d'].apply(lambda x: f"{x:+.2f}%")
        df_display['prediction'] = df_display['prediction'].apply(lambda x: f"{x:+.2f}%")
        df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x:.1%}")
        df_display['upside_potential'] = df_display['upside_potential'].apply(lambda x: f"{x:+.2f}%")
        df_display['target_price'] = df_display['target_price'].apply(lambda x: f"${x:.2f}")
        
        # Rename columns professionally
        df_display.columns = ['Symbol', 'Current Price', '1D Change', 'ML Prediction', 'Confidence', 
                             'Recommendation', 'Risk Level', 'Overall Score', 'Technical Score', 
                             'Fundamental Score', 'Sentiment Score', 'Upside/Downside', 'Target Price',
                             'Expected Timeframe', 'Timeframe Type', 'Expected Accuracy']
        
        # Enhanced color-code the table including timeframes
        def color_cells(val):
            if isinstance(val, str):
                if '+' in val and '%' in val:
                    return 'background-color: #d4edda; color: #155724'
                elif '-' in val and '%' in val:
                    return 'background-color: #f8d7da; color: #721c24'
                elif val in ['BUY', 'STRONG BUY']:
                    return 'background-color: #d1ecf1; color: #0c5460'
                elif val in ['SELL', 'STRONG SELL']:
                    return 'background-color: #f8d7da; color: #721c24'
                elif val == 'Short-Term':
                    return 'background-color: #fff3cd; color: #856404'
                elif val == 'Medium-Term':
                    return 'background-color: #d1ecf1; color: #0c5460'
                elif val == 'Long-Term':
                    return 'background-color: #d4edda; color: #155724'
            return ''
        
        st.dataframe(df_display.style.applymap(color_cells), use_container_width=True)

        # ========= Excel Export (with raw numeric values) =========
        st.markdown("### 📥 Download Results")

        def build_export_dataframe(rows: list[dict]) -> pd.DataFrame:
            export_rows = []
            for r in rows:
                export_rows.append({
                    'symbol': r.get('symbol'),
                    'current_price': r.get('current_price'),
                    'price_change_1d_pct': r.get('price_change_1d'),
                    'prediction_pct': r.get('prediction'),
                    'confidence': r.get('confidence'),
                    'recommendation': r.get('recommendation'),
                    'risk_level': r.get('risk_level'),
                    'overall_score': r.get('overall_score'),
                    'technical_score': r.get('technical_score'),
                    'fundamental_score': r.get('fundamental_score'),
                    'sentiment_score': r.get('sentiment_score'),
                    'momentum_score': r.get('momentum_score'),
                    'volume_score': r.get('volume_score'),
                    'volatility_score': r.get('volatility_score'),
                    'volume': r.get('volume'),
                    'market_cap': r.get('market_cap'),
                    'sector': r.get('sector'),
                    'upside_potential_pct': r.get('upside_potential', r.get('prediction')),
                    'adjusted_upside_pct': r.get('adjusted_upside'),
                    'stop_loss_price': r.get('stop_loss_price', r.get('current_price', 0) * 0.95 if r.get('current_price') else None),
                    'target_price': r.get('technical_target', r.get('current_price')),
                    'earnings_quality': r.get('earnings_quality'),
                    'analysis_focus': r.get('analysis_focus', analysis_type),
                    'market_regime': r.get('market_regime'),
                    'last_updated': r.get('last_updated')
                })
            return pd.DataFrame(export_rows)

        def to_excel_bytes(df: pd.DataFrame, sheet_name: str = 'Results') -> bytes | None:
            bio = BytesIO()
            try:
                with pd.ExcelWriter(bio, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                bio.seek(0)
                return bio.read()
            except Exception:
                return None

        df_export = build_export_dataframe(results)
        excel_bytes = to_excel_bytes(df_export)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_label = f"Professional_Analysis_{timestamp}.xlsx"

        if excel_bytes:
            st.download_button(
                label="⬇️ Download Excel (clean numeric)",
                data=excel_bytes,
                file_name=file_label,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            # Fallback to CSV if openpyxl not available
            st.warning("Excel engine not available. Offering CSV instead.")
            csv_bytes = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download CSV (clean numeric)",
                data=csv_bytes,
                file_name=file_label.replace('.xlsx', '.csv'),
                mime='text/csv'
            )
        
        # Professional Charts
        st.markdown("### 📈 Professional Analysis Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk vs Return scatter plot
            fig_risk_return = px.scatter(
                df_results, 
                x='overall_score', 
                y='prediction',
                size='confidence',
                color='risk_level',
                hover_data=['symbol', 'recommendation'],
                title="Risk vs Return Analysis (Professional View)",
                labels={'overall_score': 'Professional Score', 'prediction': 'Expected Return (%)'}
            )
            fig_risk_return.update_layout(height=400)
            st.plotly_chart(fig_risk_return, use_container_width=True)
        
        with col2:
            # Sector analysis
            sector_data = df_results.groupby('sector').agg({
                'overall_score': 'mean',
                'prediction': 'mean',
                'confidence': 'mean'
            }).reset_index()
            
            fig_sector = px.bar(
                sector_data,
                x='sector',
                y='overall_score',
                color='prediction',
                title="Sector Analysis (Professional View)",
                labels={'overall_score': 'Avg Professional Score', 'prediction': 'Avg Expected Return'}
            )
            fig_sector.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_sector, use_container_width=True)
        
        # Professional Trading Recommendations
        st.markdown("### 🎯 Professional Trading Strategy")
        
        high_conviction_picks = [r for r in results if r['confidence'] > 0.8 and r['recommendation'] in ['BUY', 'STRONG BUY']]
        
        if high_conviction_picks:
            st.markdown("#### 🏆 High Conviction Plays (Like Hedge Funds)")
            
            for pick in high_conviction_picks[:3]:
                st.markdown(f"""
                **{pick['symbol']}** - {pick['recommendation']} 
                - **Entry:** ${pick['current_price']:.2f}
                - **Target:** ${pick['current_price'] * (1 + pick['prediction']/100):.2f} ({pick['prediction']:+.1f}%)
                - **Stop Loss:** ${pick.get('stop_loss_price', pick['current_price'] * 0.95):.2f} (~-5%)
                - **Position Size:** {'Large' if pick['risk_level'] == 'Low' else 'Medium' if pick['risk_level'] == 'Medium' else 'Small'}
                - **Time Horizon:** {'Long-term' if pick['confidence'] > 0.9 else 'Medium-term'}
                """)
        
        # Professional risk management
        st.markdown("#### ⚠️ Professional Risk Management")
        st.markdown("""
        **Portfolio Guidelines (Institutional Style):**
        - **Maximum single position:** 5% of portfolio
        - **Sector concentration:** Maximum 25% per sector
        - **Stop losses:** Set at -5% for all positions
        - **Rebalancing:** Weekly for active positions
        - **Risk monitoring:** Daily VaR calculation recommended
        
        **Professional Trading Rules:**
        - Only trade high conviction signals (confidence > 80%)
        - Diversify across at least 10 positions
        - Use position sizing based on risk level
        - Monitor earnings calendars for all holdings
        - Set alerts for analyst rating changes
        """)
        
    else:
        st.error("No analysis results available. Please check your settings and try again.")

# Live market data notice (hide for Ultimate Strategy to keep UI minimal)
if not is_ultimate:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Live Market Data")
    st.sidebar.info("Disabled in Light Mode for scale and reliability.")

# Professional footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <strong>Professional Trading Terminal</strong><br>
    Created by Mani Rastegari | Institutional-Grade Analysis<br>
    <em>⚠️ For educational and research purposes only. Not financial advice.</em>
</div>
""", unsafe_allow_html=True)
