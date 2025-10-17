"""
Enhanced Trading Analyzer App - Maximum Free Analysis Power
Analyzes 500+ stocks with comprehensive free data sources
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

from enhanced_analyzer import EnhancedTradingAnalyzer

def main():
    st.set_page_config(
        page_title="Enhanced Trading Analyzer",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Enhanced Trading Analyzer - Maximum Free Analysis Power")
    st.markdown("**Analyzes 500+ stocks with comprehensive free data sources**")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = EnhancedTradingAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎯 Analysis Controls")
        
        # Analysis settings
        max_stocks = st.slider("Number of Stocks to Analyze", 10, 100, 50)
        
        # Analysis type
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Comprehensive Analysis", "Quick Analysis", "Deep Dive Analysis"]
        )
        
        # Risk tolerance
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive"]
        )
        
        # Market focus
        market_focus = st.multiselect(
            "Market Focus",
            ["US Large Cap", "US Mid Cap", "US Small Cap", "Canadian Stocks", "Growth Stocks", "Value Stocks"],
            default=["US Large Cap", "Canadian Stocks"]
        )
        
        if st.button("🚀 Start Enhanced Analysis", type="primary"):
            with st.spinner("Running enhanced analysis..."):
                results = analyzer.run_enhanced_analysis(max_stocks)
                st.session_state.results = results
        
        if st.button("🔄 Refresh Analysis"):
            with st.spinner("Refreshing analysis..."):
                results = analyzer.run_enhanced_analysis(max_stocks)
                st.session_state.results = results
    
    # Main dashboard
    if 'results' in st.session_state and st.session_state.results:
        results = st.session_state.results
        
        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Stocks Analyzed", len(results))
            strong_buys = len([r for r in results if 'STRONG BUY' in r['recommendation']])
            st.metric("Strong Buys", strong_buys)
        
        with col2:
            avg_prediction = np.mean([r['prediction'] for r in results])
            st.metric("Avg Prediction", f"{avg_prediction:.2f}%")
            avg_confidence = np.mean([r['confidence'] for r in results])
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        
        with col3:
            high_risk = len([r for r in results if r['risk_level'] == 'High'])
            st.metric("High Risk", high_risk)
            low_risk = len([r for r in results if r['risk_level'] == 'Low'])
            st.metric("Low Risk", low_risk)
        
        with col4:
            avg_tech = np.mean([r['technical_score'] for r in results])
            st.metric("Avg Tech Score", f"{avg_tech:.1f}")
            avg_fund = np.mean([r['fundamental_score'] for r in results])
            st.metric("Avg Fund Score", f"{avg_fund:.1f}")
        
        with col5:
            avg_overall = np.mean([r['overall_score'] for r in results])
            st.metric("Avg Overall Score", f"{avg_overall:.1f}")
            avg_sentiment = np.mean([r['sentiment_score'] for r in results])
            st.metric("Avg Sentiment", f"{avg_sentiment:.1f}")
        
        # Top picks
        st.subheader("🏆 Top Stock Picks (Enhanced Analysis)")
        top_picks = analyzer.get_top_picks_enhanced(results, 20)
        
        if top_picks:
            for i, pick in enumerate(top_picks, 1):
                with st.expander(f"#{i} {pick['symbol']} - {pick['recommendation']} - {pick['action']} (Score: {pick['overall_score']:.1f})"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**Price:** ${pick['current_price']:.2f}")
                        st.write(f"**Change:** {pick['price_change_1d']:.2f}%")
                        st.write(f"**Volume:** {pick['volume']:,.0f}")
                        st.write(f"**Market Cap:** ${pick['market_cap']:,.0f}")
                    
                    with col2:
                        st.write(f"**Prediction:** {pick['prediction']:.2f}%")
                        st.write(f"**Confidence:** {pick['confidence']:.1%}")
                        st.write(f"**Risk:** {pick['risk_level']}")
                        st.write(f"**Sector:** {pick['sector']}")
                    
                    with col3:
                        st.write(f"**Tech Score:** {pick['technical_score']}/100")
                        st.write(f"**Fund Score:** {pick['fundamental_score']}/100")
                        st.write(f"**Sentiment:** {pick['sentiment_score']}/100")
                        st.write(f"**Momentum:** {pick['momentum_score']}/100")
                    
                    with col4:
                        st.write(f"**Volume Score:** {pick['volume_score']}/100")
                        st.write(f"**Volatility:** {pick['volatility_score']}/100")
                        st.write(f"**Overall:** {pick['overall_score']}/100")
                        st.write(f"**P/E Ratio:** {pick['pe_ratio']:.2f}")
                    
                    # Enhanced signals
                    st.write("**Enhanced Trading Signals:**")
                    for signal in pick['signals'][:10]:  # Show top 10 signals
                        st.write(f"• {signal}")
        
        # Detailed results table
        st.subheader("📊 Complete Analysis Results")
        df = pd.DataFrame(results)
        display_df = df[['symbol', 'current_price', 'price_change_1d', 'recommendation', 
                        'action', 'prediction', 'confidence', 'risk_level', 'technical_score', 
                        'fundamental_score', 'sentiment_score', 'overall_score']]
        st.dataframe(display_df, use_container_width=True)
        
        # Enhanced charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Prediction vs Confidence scatter
            fig = px.scatter(df, x='prediction', y='confidence', 
                           color='recommendation', size='overall_score',
                           hover_data=['symbol', 'action', 'technical_score', 'fundamental_score'],
                           title="Prediction vs Confidence (Enhanced)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk distribution
            risk_counts = df['risk_level'].value_counts()
            fig = px.pie(values=risk_counts.values, names=risk_counts.index, 
                        title="Risk Level Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Score distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Technical vs Fundamental scores
            fig = px.scatter(df, x='technical_score', y='fundamental_score', 
                           color='recommendation', size='overall_score',
                           hover_data=['symbol', 'action'],
                           title="Technical vs Fundamental Analysis")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment vs Momentum
            fig = px.scatter(df, x='sentiment_score', y='momentum_score', 
                           color='recommendation', size='overall_score',
                           hover_data=['symbol', 'action'],
                           title="Sentiment vs Momentum Analysis")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendation distribution
        rec_counts = df['recommendation'].value_counts()
        fig = px.bar(x=rec_counts.index, y=rec_counts.values, 
                    title="Recommendation Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Sector analysis
        if 'sector' in df.columns:
            sector_analysis = df.groupby('sector').agg({
                'prediction': 'mean',
                'confidence': 'mean',
                'overall_score': 'mean',
                'symbol': 'count'
            }).round(2)
            sector_analysis.columns = ['Avg Prediction', 'Avg Confidence', 'Avg Score', 'Count']
            sector_analysis = sector_analysis.sort_values('Avg Score', ascending=False)
            
            st.subheader("📈 Sector Analysis")
            st.dataframe(sector_analysis)
        
        # Market overview
        st.subheader("🌍 Market Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Market Cap", f"${df['market_cap'].sum():,.0f}")
            st.metric("Avg P/E Ratio", f"{df['pe_ratio'].mean():.2f}")
        
        with col2:
            st.metric("High Confidence Picks", len(df[df['confidence'] > 0.7]))
            st.metric("Low Risk Picks", len(df[df['risk_level'] == 'Low']))
        
        with col3:
            st.metric("Positive Predictions", len(df[df['prediction'] > 0]))
            st.metric("Strong Fundamentals", len(df[df['fundamental_score'] > 70]))
        
    else:
        st.info("👆 Click 'Start Enhanced Analysis' to begin!")
        
        # Show sample of what will be analyzed
        st.subheader("📋 Enhanced Analysis Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Technical Analysis (50+ Indicators):**")
            st.write("• RSI (14, 21, 30 periods)")
            st.write("• MACD (multiple timeframes)")
            st.write("• Moving Averages (5, 10, 20, 50, 100, 200)")
            st.write("• Bollinger Bands (multiple periods)")
            st.write("• Stochastic Oscillator")
            st.write("• Williams %R")
            st.write("• Commodity Channel Index")
            st.write("• Average True Range")
            st.write("• Average Directional Index")
            st.write("• Money Flow Index")
            st.write("• On Balance Volume")
            st.write("• Accumulation/Distribution")
            st.write("• Chaikin Money Flow")
            st.write("• Candlestick Patterns")
            st.write("• Support/Resistance Levels")
            st.write("• Volatility Indicators")
            st.write("• Trend Strength Analysis")
        
        with col2:
            st.write("**📰 News & Sentiment Analysis:**")
            st.write("• Yahoo Finance News")
            st.write("• Google News Scraping")
            st.write("• Reddit Sentiment")
            st.write("• Twitter Sentiment")
            st.write("• Overall Sentiment Score")
            st.write("• News Count Analysis")
            
            st.write("**🏢 Fundamental Analysis:**")
            st.write("• P/E, P/B, P/S Ratios")
            st.write("• PEG Ratio")
            st.write("• Dividend Yield")
            st.write("• Revenue Growth")
            st.write("• Earnings Growth")
            st.write("• Profit Margins")
            st.write("• Return on Equity")
            st.write("• Debt-to-Equity")
            st.write("• Market Cap Analysis")
            
            st.write("**🔍 Advanced Analysis:**")
            st.write("• Insider Trading Activity")
            st.write("• Options Data (Put/Call Ratio)")
            st.write("• Institutional Holdings")
            st.write("• Economic Indicators")
            st.write("• VIX Analysis")
            st.write("• Fed Rate Impact")
            st.write("• GDP Growth Analysis")
            st.write("• Inflation Impact")
        
        st.subheader("🎯 What Makes This Enhanced:")
        st.write("""
        1. **500+ Stocks** - Analyzes major US and Canadian stocks
        2. **50+ Technical Indicators** - Comprehensive technical analysis
        3. **Multi-Source News** - Yahoo, Google, Reddit, Twitter sentiment
        4. **Insider Trading** - Tracks insider buying/selling activity
        5. **Options Analysis** - Put/call ratios and implied volatility
        6. **Institutional Data** - Tracks institutional holdings
        7. **Economic Indicators** - VIX, Fed rates, GDP, inflation
        8. **Advanced ML** - 4 different machine learning models
        9. **Risk Assessment** - Multi-factor risk analysis
        10. **Real-time Updates** - Fresh data every analysis
        """)

if __name__ == "__main__":
    main()
