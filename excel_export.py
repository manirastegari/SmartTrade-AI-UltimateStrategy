#!/usr/bin/env python3
"""
Excel Export Functionality for SmartTrade AI
Professional reporting and portfolio management
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import subprocess
from openpyxl.utils import get_column_letter

def push_to_github(filename):
    """
    Automatically commit and push Excel results to GitHub
    
    Args:
        filename: The Excel file to commit
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the directory of the Excel file
        file_dir = os.path.dirname(os.path.abspath(filename)) if os.path.dirname(filename) else os.getcwd()
        file_name = os.path.basename(filename)
        
        # Git add the file
        subprocess.run(['git', 'add', file_name], cwd=file_dir, check=True, capture_output=True)
        
        # Git commit
        commit_message = f"Auto-export: {file_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=file_dir, check=True, capture_output=True)
        
        # Git push
        subprocess.run(['git', 'push'], cwd=file_dir, check=True, capture_output=True)
        
        print(f"✅ Successfully pushed {file_name} to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        # Git command failed - might be nothing to commit or network issue
        if b'nothing to commit' in e.stderr or b'nothing added to commit' in e.stderr:
            print(f"⚠️ No changes to commit for {filename}")
        else:
            print(f"⚠️ Git push failed: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"⚠️ Git push error: {str(e)}")
        return False

def export_analysis_to_excel(results, analysis_params=None, filename=None, auto_push_github=True, all_stocks_data=None):
    """Export analysis results to Excel with multiple sheets
    
    Optimized for Premium Quality Universe (614 institutional-grade stocks)
    
    Args:
        results: Consensus/filtered recommendations list
        analysis_params: Analysis parameters string
        filename: Output filename (optional)
        auto_push_github: Auto-commit to GitHub (default True)
        all_stocks_data: Complete list of ALL analyzed stocks (NEW - for full dataset export)
    """
    
    if not results and not all_stocks_data:
        return None, "No results to export"
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SmartTrade_Premium_Analysis_{timestamp}.xlsx"
    
    try:
        # Create Excel writer object
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Sheet 1: Summary Dashboard
            create_summary_sheet(results, writer, analysis_params, all_stocks_count=len(all_stocks_data) if all_stocks_data else None)
            
            # Sheet 2: ALL ANALYZED STOCKS (NEW - Critical for user visibility)
            if all_stocks_data:
                create_all_analyzed_sheet(all_stocks_data, writer)
            
            # Sheet 3: Strong Buy Recommendations (consensus picks)
            create_recommendations_sheet(results, writer, 'STRONG BUY')
            
            # Sheet 4: All Buy Signals (consensus picks)
            create_recommendations_sheet(results, writer, ['STRONG BUY', 'BUY', 'WEAK BUY'], 'All_Buy_Signals')
            
            # Sheet 5: Detailed Analysis (consensus picks)
            create_detailed_analysis_sheet(results, writer)
            
            # Sheet 6: Technical Indicators (consensus picks)
            create_technical_sheet(results, writer)
            
            # Sheet 7: Risk Analysis (consensus picks)
            create_risk_analysis_sheet(results, writer)
            
            # Sheet 8: Sector Analysis (consensus picks)
            create_sector_analysis_sheet(results, writer)
            
            # Sheet 9: Performance Metrics (consensus picks)
            create_performance_sheet(results, writer)
        
        # Auto-push to GitHub if requested
        if auto_push_github:
            push_to_github(filename)
        
        total_analyzed = len(all_stocks_data) if all_stocks_data else len(results)
        consensus_count = len(results) if results else 0
        return filename, f"Successfully exported {total_analyzed} analyzed stocks ({consensus_count} consensus picks) to {filename}"
        
    except Exception as e:
        return None, f"Export failed: {str(e)}"

def create_summary_sheet(results, writer, analysis_params, all_stocks_count=None):
    """Create summary dashboard sheet
    
    Args:
        results: Consensus picks list
        writer: Excel writer
        analysis_params: Analysis parameters string
        all_stocks_count: Total number of stocks analyzed (NEW - to show complete picture)
    """
    
    # Check if this is consensus format
    is_consensus = isinstance(results, list) and results and 'strategies_agreeing' in results[0]
    
    if is_consensus:
        # New consensus format
        total_stocks = len(results)
        strong_buy = len([r for r in results if r.get('recommendation') == 'STRONG BUY'])
        buy = len([r for r in results if r.get('recommendation') == 'BUY'])
        weak_buy = len([r for r in results if r.get('recommendation') == 'WEAK BUY'])
        hold = len([r for r in results if r.get('recommendation') == 'HOLD'])
        sell_signals = 0  # Not used in consensus
        
        # Consensus-specific stats
        tier_4 = len([r for r in results if r.get('strategies_agreeing') == 4])
        tier_3 = len([r for r in results if r.get('strategies_agreeing') == 3])
        tier_2 = len([r for r in results if r.get('strategies_agreeing') == 2])
        
        avg_quality = np.mean([r.get('quality_score', 0) for r in results]) if results else 0
        top_performer = max(results, key=lambda x: x.get('quality_score', 0)).get('symbol', 'N/A') if results else 'N/A'
        
        # CRITICAL FIX: Show both total analyzed and consensus picks
        total_analyzed_display = all_stocks_count if all_stocks_count else total_stocks
        consensus_picks_display = total_stocks
        
        # Create consensus summary
        summary_data = {
            'Metric': [
                'Analysis Date',
                'Analysis Type',
                'Universe Type',
                'Total Stocks Analyzed',
                'Consensus Picks (2+ Agreement)',
                '━━━━━━━━━━━━━━━━━━━━━━━━━━',
                '4/4 Agreement (STRONG BUY)',
                '3/4 Agreement (BUY)',
                '2/4 Agreement (WEAK BUY)',
                'Average Quality Score',
                'Top Performer',
                '━━━━━━━━━━━━━━━━━━━━━━━━━━',
                'Methodology',
                'Risk Management',
                'Analysis Parameters'
            ],
            'Value': [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Premium Ultimate Strategy - 4-Perspective Consensus',
                'Premium Quality Universe (614 institutional-grade stocks)',
                f"{total_analyzed_display} stocks (complete analysis)",
                f"{consensus_picks_display} stocks (filtered by multi-strategy agreement)",
                '',  # Separator
                f"{tier_4} stocks (all perspectives agree)",
                f"{tier_3} stocks (strong majority)",
                f"{tier_2} stocks (split decision)",
                f"{avg_quality:.1f}/100",
                f"{top_performer} ({max([r.get('quality_score', 0) for r in results]):.0f}/100)" if results else 'N/A',
                '',  # Separator
                '15 Quality Metrics: Fundamentals 40%, Momentum 30%, Risk 20%, Sentiment 10%',
                'Guardrails: DISABLED (pre-screened) | Regime Filters: RELAXED',
                str(analysis_params) if analysis_params else 'Premium Ultimate Strategy - 4-Perspective Consensus'
            ]
        }
    else:
        # Old format
        total_stocks = len(results)
        strong_buy = len([r for r in results if r.get('recommendation') == 'STRONG BUY'])
        buy = len([r for r in results if r.get('recommendation') == 'BUY'])
        weak_buy = len([r for r in results if r.get('recommendation') == 'WEAK BUY'])
        hold = len([r for r in results if r.get('recommendation') == 'HOLD'])
        sell_signals = len([r for r in results if r.get('recommendation', '').endswith('SELL')])
        
        summary_data = {
            'Metric': [
                'Analysis Date',
                'Universe Type',
                'Total Stocks Analyzed',
                'Strong Buy Recommendations',
                'Buy Recommendations', 
                'Weak Buy Recommendations',
                'Hold Recommendations',
                'Sell Signals',
                'Success Rate (%)',
                'Average Score',
                'Top Performer',
                'Risk Management',
                'Analysis Parameters'
            ],
            'Value': [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Premium Quality Universe (614 institutional-grade stocks)',
                total_stocks,
                strong_buy,
                buy,
                weak_buy,
                hold,
                sell_signals,
                f"{(strong_buy + buy + weak_buy) / total_stocks * 100:.1f}%" if total_stocks > 0 else "0%",
                f"{np.mean([r.get('overall_score', 0) for r in results]):.1f}",
                max(results, key=lambda x: x.get('overall_score', 0)).get('symbol', 'N/A') if results else 'N/A',
                'Guardrails: DISABLED (pre-screened) | Regime Filters: RELAXED',
                str(analysis_params) if analysis_params else 'Ultimate Strategy 4-Perspective Consensus'
            ]
        }
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

def create_all_analyzed_sheet(all_stocks_data, writer):
    """
    Create sheet showing ALL analyzed stocks (not just consensus picks)
    
    CRITICAL: This shows the complete 613-stock analysis
    Args:
        all_stocks_data: List of dict with all analyzed stocks and their metrics
        writer: Excel writer object
    """
    if not all_stocks_data:
        return
    
    # Prepare data for Excel
    excel_data = []
    
    for stock in all_stocks_data:
        excel_data.append({
            'Symbol': stock.get('symbol', 'N/A'),
            'Sector': stock.get('sector', 'Unknown'),
            'Quality Score': stock.get('quality_score', 0),
            'Current Price': stock.get('current_price', 0),
            
            # Fundamentals
            'P/E Ratio': stock.get('pe_ratio'),
            'Revenue Growth %': stock.get('revenue_growth'),
            'Profit Margin %': stock.get('profit_margin'),
            'ROE %': stock.get('roe'),
            'Debt/Equity': stock.get('debt_equity'),
            'Fund Score': stock.get('fundamentals_score'),
            'Fund Grade': stock.get('fundamentals_grade', 'N/A'),
            
            # Momentum
            'RSI': stock.get('rsi_14'),
            'Price Trend': stock.get('price_trend', 'N/A'),
            'Volume Trend': stock.get('volume_trend', 'N/A'),
            'Momentum Score': stock.get('momentum_score'),
            'Momentum Grade': stock.get('momentum_grade', 'N/A'),
            'MA 50': stock.get('ma_50'),
            'MA 200': stock.get('ma_200'),
            'Volume Ratio': stock.get('volume_ratio'),
            
            # Risk
            'Beta': stock.get('beta'),
            'Volatility %': stock.get('volatility'),
            'Sharpe Ratio': stock.get('sharpe_ratio'),
            'Max Drawdown %': stock.get('max_drawdown'),
            'VaR 95%': stock.get('var_95'),
            'Risk Score': stock.get('risk_score'),
            'Risk Grade': stock.get('risk_grade', 'N/A'),
            'Risk Level': stock.get('risk_level', 'N/A'),
            
            # Technical
            'MACD': stock.get('macd'),
            'MACD Signal': stock.get('macd_signal'),
            'MACD Histogram': stock.get('macd_hist'),
            'Bollinger Position %': stock.get('bollinger_position'),
            'Bollinger Upper': stock.get('bollinger_upper'),
            'Bollinger Lower': stock.get('bollinger_lower'),
            'Support Level': stock.get('support_level'),
            'Resistance Level': stock.get('resistance_level'),
            'Volume SMA': stock.get('volume_sma'),
            'Technical Score': stock.get('technical_score'),
            
            # Sentiment
            'Sentiment Score': stock.get('sentiment_score'),
            'Sentiment Grade': stock.get('sentiment_grade', 'N/A'),
            'Target Upside %': stock.get('target_upside'),
            'Institutional Ownership %': stock.get('institutional_ownership'),
            'Analyst Rating': stock.get('analyst_rating', 'N/A')
        })
    
    # Create DataFrame
    df = pd.DataFrame(excel_data)
    
    # Sort by quality score (highest first)
    df = df.sort_values('Quality Score', ascending=False)
    
    # Write to Excel
    df.to_excel(writer, sheet_name='All_Analyzed_Stocks', index=False)
    
    # Get the worksheet
    worksheet = writer.sheets['All_Analyzed_Stocks']
    
    # Auto-adjust column widths
    for idx, col in enumerate(df.columns, start=1):
        max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
        column_letter = get_column_letter(idx)
        worksheet.column_dimensions[column_letter].width = min(max_len, 30)
    
    # Add conditional formatting for Quality Score
    from openpyxl.styles import PatternFill
    from openpyxl.formatting.rule import CellIsRule
    
    # Green for high scores (80+)
    green_fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
    worksheet.conditional_formatting.add(f'B2:B{len(df)+1}', 
        CellIsRule(operator='greaterThan', formula=['80'], fill=green_fill))
    
    # Yellow for medium scores (60-79)
    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    worksheet.conditional_formatting.add(f'B2:B{len(df)+1}', 
        CellIsRule(operator='between', formula=['60', '79'], fill=yellow_fill))
    
    # Red for low scores (<60)
    red_fill = PatternFill(start_color='FFB6C1', end_color='FFB6C1', fill_type='solid')
    worksheet.conditional_formatting.add(f'B2:B{len(df)+1}', 
        CellIsRule(operator='lessThan', formula=['60'], fill=red_fill))

def create_recommendations_sheet(results, writer, recommendation_types, sheet_name=None):
    """Create recommendations sheet (supports both old and new consensus format)"""
    
    if isinstance(recommendation_types, str):
        recommendation_types = [recommendation_types]
        sheet_name = sheet_name or recommendation_types[0].replace(' ', '_')
    else:
        sheet_name = sheet_name or 'Recommendations'
    
    # Filter results
    filtered_results = [r for r in results if r.get('recommendation') in recommendation_types]
    
    if not filtered_results:
        # Create empty sheet with message
        empty_df = pd.DataFrame({'Message': ['No recommendations found for the selected criteria']})
        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
        return
    
    # Create recommendations data (handle both old and new consensus formats)
    recommendations_data = []
    for result in filtered_results:
        # Check if this is consensus format (has strategies_agreeing)
        is_consensus = 'strategies_agreeing' in result
        
        if is_consensus:
            # New Premium Ultimate Strategy format
            fund = result.get('fundamentals', {})
            mom = result.get('momentum', {})
            risk = result.get('risk', {})
            sent = result.get('sentiment', {})
            
            recommendations_data.append({
                'Symbol': result.get('symbol', ''),
                'Recommendation': result.get('recommendation', ''),
                'Agreement': f"{result.get('strategies_agreeing', 0)}/4",
                'Quality Score': result.get('quality_score', 0),
                'Consensus Score': result.get('consensus_score', 0),
                'Confidence': f"{result.get('confidence', 0) * 100:.0f}%",
                'Current Price': f"${result.get('current_price', 0):.2f}",
                'Fundamentals': f"{fund.get('grade', 'N/A')} ({fund.get('score', 0):.0f})",
                'Momentum': f"{mom.get('grade', 'N/A')} ({mom.get('score', 0):.0f})",
                'Risk': f"{risk.get('grade', 'N/A')} ({risk.get('score', 0):.0f})",
                'Sentiment': f"{sent.get('grade', 'N/A')} ({sent.get('score', 0):.0f})",
                'Perspectives': ', '.join(result.get('agreeing_perspectives', [])),
                'P/E Ratio': fund.get('pe_ratio', 'N/A'),
                'Revenue Growth': f"{fund.get('revenue_growth', 0)*100:.1f}%" if fund.get('revenue_growth') else 'N/A',
                'Beta': risk.get('beta', 'N/A')
            })
        else:
            # Old format
            recommendations_data.append({
                'Symbol': result.get('symbol', ''),
                'Company': result.get('company_name', ''),
                'Recommendation': result.get('recommendation', ''),
                'Current Price': f"${result.get('current_price', 0):.2f}",
                'Predicted Return': f"{result.get('prediction', 0) * 100:.1f}%",
                'Overall Score': result.get('overall_score', 0),
                'Technical Score': result.get('technical_score', 0),
                'Fundamental Score': result.get('fundamental_score', 0),
                'Risk Level': result.get('risk_level', ''),
                'Sector': result.get('sector', ''),
                'Market Cap': result.get('market_cap', 0),
                'Volume': result.get('volume', 0),
                'P/E Ratio': result.get('pe_ratio', 0),
                'Confidence': f"{result.get('confidence', 0) * 100:.1f}%"
            })
    
    recommendations_df = pd.DataFrame(recommendations_data)
    
    # Sort by appropriate column
    if recommendations_data and 'Quality Score' in recommendations_data[0]:
        recommendations_df = recommendations_df.sort_values('Quality Score', ascending=False)
    elif 'Overall Score' in recommendations_df.columns:
        recommendations_df = recommendations_df.sort_values('Overall Score', ascending=False)
    
    recommendations_df.to_excel(writer, sheet_name=sheet_name, index=False)

def create_detailed_analysis_sheet(results, writer):
    """Create detailed analysis sheet with all metrics"""
    if not results:
        empty_df = pd.DataFrame({'Message': ['No analysis results available']})
        empty_df.to_excel(writer, sheet_name='Detailed_Analysis', index=False)
        return

    detailed_data = []
    is_consensus = 'fundamentals' in results[0]

    for result in results:
        if is_consensus:
            fund = result.get('fundamentals', {})
            mom = result.get('momentum', {})
            risk = result.get('risk', {})
            tech = result.get('technical', {})
            sent = result.get('sentiment', {})

            detailed_data.append({
                'Symbol': result.get('symbol', ''),
                'Recommendation': result.get('recommendation', ''),
                'Agreement': f"{result.get('strategies_agreeing', 0)}/4",
                'Consensus Score': result.get('consensus_score', result.get('overall_score', 0)),
                'Quality Score': result.get('quality_score', 0),
                'Confidence %': result.get('confidence', 0) * 100,
                'Sector': result.get('sector', 'Unknown'),
                'Current Price': result.get('current_price', 0),
                'Fundamentals Score': fund.get('score', 0),
                'Fundamentals Grade': fund.get('grade', 'N/A'),
                'P/E Ratio': fund.get('pe_ratio'),
                'Revenue Growth %': fund.get('revenue_growth'),
                'Profit Margin %': fund.get('profit_margin'),
                'ROE %': fund.get('roe'),
                'Debt/Equity': fund.get('debt_equity'),
                'Momentum Score': mom.get('score', 0),
                'Momentum Grade': mom.get('grade', 'N/A'),
                'RSI': mom.get('rsi'),
                'Price Trend': mom.get('price_trend'),
                'Volume Trend': mom.get('volume_trend'),
                'Relative Strength %': mom.get('relative_strength'),
                'MA 50': mom.get('ma_50'),
                'MA 200': mom.get('ma_200'),
                'Technical Score': tech.get('score', 0),
                'Technical Grade': tech.get('grade', 'N/A'),
                'MACD': tech.get('macd'),
                'MACD Signal': tech.get('macd_signal'),
                'MACD Histogram': tech.get('macd_hist'),
                'Bollinger Position %': tech.get('bollinger_position'),
                'Support Level': tech.get('support'),
                'Resistance Level': tech.get('resistance'),
                'Risk Score': risk.get('score', 0),
                'Risk Grade': risk.get('grade', 'N/A'),
                'Risk Level': risk.get('risk_level', ''),
                'Volatility %': risk.get('volatility'),
                'Max Drawdown %': risk.get('max_drawdown'),
                'VaR 95% %': risk.get('var_95'),
                'Sharpe Ratio': risk.get('sharpe_ratio'),
                'Sentiment Score': sent.get('score', 0),
                'Sentiment Grade': sent.get('grade', 'N/A'),
                'Target Upside %': sent.get('target_upside'),
                'Institutional Ownership %': sent.get('institutional_ownership'),
                'Analyst Rating': sent.get('analyst_rating', 'N/A')
            })
        else:
            detailed_data.append({
                'Symbol': result.get('symbol', ''),
                'Company': result.get('company_name', ''),
                'Recommendation': result.get('recommendation', ''),
                'Current Price': result.get('current_price', 0),
                'Predicted Return %': result.get('prediction', 0) * 100,
                'Confidence %': result.get('confidence', 0) * 100,
                'Overall Score': result.get('overall_score', 0),
                'Technical Score': result.get('technical_score', 0),
                'Fundamental Score': result.get('fundamental_score', 0),
                'Sentiment Score': result.get('sentiment_score', 0),
                'Risk Level': result.get('risk_level', ''),
                'Sector': result.get('sector', ''),
                'Market Cap': result.get('market_cap', 0),
                'Volume': result.get('volume', 0),
                'P/E Ratio': result.get('pe_ratio', 0),
                'P/B Ratio': result.get('pb_ratio', 0),
                'ROE %': result.get('roe', 0),
                'Debt/Equity': result.get('debt_equity', 0),
                'Revenue Growth %': result.get('revenue_growth', 0),
                'Earnings Growth %': result.get('earnings_growth', 0),
                'RSI': result.get('rsi', 0),
                'MACD Signal': result.get('macd_signal', ''),
                '50-Day MA': result.get('ma_50', 0),
                '200-Day MA': result.get('ma_200', 0),
                'Bollinger Position': result.get('bollinger_position', ''),
                'Support Level': result.get('support', 0),
                'Resistance Level': result.get('resistance', 0)
            })

    detailed_df = pd.DataFrame(detailed_data)
    sort_column = 'Consensus Score' if is_consensus else 'Overall Score'
    if sort_column in detailed_df.columns:
        detailed_df = detailed_df.sort_values(sort_column, ascending=False)
    detailed_df.to_excel(writer, sheet_name='Detailed_Analysis', index=False)

def create_technical_sheet(results, writer):
    """Create technical indicators sheet"""
    if not results:
        empty_df = pd.DataFrame({'Message': ['No technical data available']})
        empty_df.to_excel(writer, sheet_name='Technical_Indicators', index=False)
        return

    technical_data = []
    is_consensus = 'technical' in results[0]

    for result in results:
        if is_consensus:
            tech = result.get('technical', {})
            mom = result.get('momentum', {})
            current_price = result.get('current_price', 0)
            ma50 = mom.get('ma_50') or result.get('ma_50') or 0
            ma200 = mom.get('ma_200') or result.get('ma_200') or 0

            def pct_diff(price, ma):
                if not price or not ma:
                    return None
                return ((price / ma) - 1) * 100

            technical_data.append({
                'Symbol': result.get('symbol', ''),
                'RSI': mom.get('rsi'),
                'Price Trend': mom.get('price_trend'),
                'MACD': tech.get('macd'),
                'MACD Signal': tech.get('macd_signal'),
                'MACD Histogram': tech.get('macd_hist'),
                'Bollinger Position %': tech.get('bollinger_position'),
                'Bollinger Upper': tech.get('bollinger_upper'),
                'Bollinger Lower': tech.get('bollinger_lower'),
                'Support': tech.get('support'),
                'Resistance': tech.get('resistance'),
                'Volume SMA': tech.get('volume_sma'),
                'Volume Trend': mom.get('volume_trend'),
                'Price vs MA50 %': pct_diff(current_price, ma50),
                'Price vs MA200 %': pct_diff(current_price, ma200),
                'Momentum Score': result.get('momentum_score', mom.get('score')),
                'Technical Score': tech.get('score'),
                'Technical Grade': tech.get('grade', 'N/A')
            })
        else:
            signals = result.get('signals', {})
            current_price = result.get('current_price', 0)
            ma50 = result.get('ma_50', 0)
            ma200 = result.get('ma_200', 0)

            technical_data.append({
                'Symbol': result.get('symbol', ''),
                'RSI': result.get('rsi', 0),
                'RSI Signal': signals.get('rsi_signal', ''),
                'MACD': result.get('macd', 0),
                'MACD Signal': signals.get('macd_signal', ''),
                'Stochastic %K': result.get('stoch_k', 0),
                'Stochastic %D': result.get('stoch_d', 0),
                'Williams %R': result.get('williams_r', 0),
                'CCI': result.get('cci', 0),
                'ADX': result.get('adx', 0),
                'Bollinger Upper': result.get('bb_upper', 0),
                'Bollinger Lower': result.get('bb_lower', 0),
                'Bollinger Position': result.get('bollinger_position', ''),
                'Volume SMA': result.get('volume_sma', 0),
                'Price vs MA50': f"{((current_price / ma50 - 1) * 100):.1f}%" if ma50 else None,
                'Price vs MA200': f"{((current_price / ma200 - 1) * 100):.1f}%" if ma200 else None,
                'Support': result.get('support', 0),
                'Resistance': result.get('resistance', 0),
                'Technical Score': result.get('technical_score', 0)
            })

    technical_df = pd.DataFrame(technical_data)
    sort_col = 'Technical Score' if 'Technical Score' in technical_df.columns else None
    if sort_col:
        technical_df = technical_df.sort_values(sort_col, ascending=False)
    technical_df.to_excel(writer, sheet_name='Technical_Indicators', index=False)

def create_risk_analysis_sheet(results, writer):
    """Create risk analysis sheet"""
    if not results:
        empty_df = pd.DataFrame({'Message': ['No risk data available']})
        empty_df.to_excel(writer, sheet_name='Risk_Analysis', index=False)
        return

    risk_data = []
    is_consensus = 'risk' in results[0]

    for result in results:
        if is_consensus:
            risk = result.get('risk', {})
            fund = result.get('fundamentals', {})
            risk_data.append({
                'Symbol': result.get('symbol', ''),
                'Risk Level': risk.get('risk_level', result.get('risk_level', 'Unknown')),
                'Risk Score': risk.get('score', 0),
                'Risk Grade': risk.get('grade', 'N/A'),
                'Beta': risk.get('beta'),
                'Volatility %': risk.get('volatility'),
                'Sharpe Ratio': risk.get('sharpe_ratio'),
                'Max Drawdown %': risk.get('max_drawdown'),
                'VaR 95% %': risk.get('var_95'),
                'Debt/Equity': fund.get('debt_equity'),
                'Recommendation': result.get('recommendation', ''),
                'Consensus Score': result.get('consensus_score', result.get('overall_score', 0))
            })
        else:
            risk_data.append({
                'Symbol': result.get('symbol', ''),
                'Risk Level': result.get('risk_level', ''),
                'Beta': result.get('beta', 0),
                'Volatility': result.get('volatility', 0),
                'Sharpe Ratio': result.get('sharpe_ratio', 0),
                'Max Drawdown': result.get('max_drawdown', 0),
                'VaR (95%)': result.get('var_95', 0),
                'Debt/Equity': result.get('debt_equity', 0),
                'Current Ratio': result.get('current_ratio', 0),
                'Quick Ratio': result.get('quick_ratio', 0),
                'Interest Coverage': result.get('interest_coverage', 0),
                'Recommendation': result.get('recommendation', ''),
                'Overall Score': result.get('overall_score', 0)
            })

    risk_df = pd.DataFrame(risk_data)
    sort_col = 'Risk Score' if 'Risk Score' in risk_df.columns else None
    if sort_col:
        risk_df = risk_df.sort_values(sort_col, ascending=False)
    risk_df.to_excel(writer, sheet_name='Risk_Analysis', index=False)

def create_sector_analysis_sheet(results, writer):
    """Create sector analysis sheet"""
    if not results:
        empty_df = pd.DataFrame({'Message': ['No sector data available']})
        empty_df.to_excel(writer, sheet_name='Sector_Analysis', index=False)
        return

    sector_summary = {}
    consensus_format = 'consensus_score' in results[0] or 'overall_score' in results[0]

    for result in results:
        sector = result.get('sector', 'Unknown')
        sector_stats = sector_summary.setdefault(sector, {
            'count': 0,
            'strong_buy': 0,
            'buy': 0,
            'score_total': 0,
            'stocks': []
        })

        sector_stats['count'] += 1
        score_val = result.get('consensus_score') if consensus_format else result.get('overall_score', 0)
        sector_stats['score_total'] += score_val if score_val is not None else 0
        sector_stats['stocks'].append(result.get('symbol', ''))

        recommendation = result.get('recommendation', '')
        if recommendation == 'STRONG BUY':
            sector_stats['strong_buy'] += 1
        elif recommendation in ('BUY', 'WEAK BUY'):
            sector_stats['buy'] += 1

    sector_data = []
    for sector, data in sector_summary.items():
        count = data['count'] or 1
        sector_data.append({
            'Sector': sector,
            'Total Stocks': data['count'],
            'Strong Buy': data['strong_buy'],
            'Buy / Weak Buy': data['buy'],
            'Buy Rate %': f"{(data['strong_buy'] + data['buy']) / count * 100:.1f}%",
            'Avg Score': data['score_total'] / count,
            'Top Stocks': ', '.join(data['stocks'][:5])
        })

    sector_df = pd.DataFrame(sector_data)
    if 'Avg Score' in sector_df.columns:
        sector_df = sector_df.sort_values('Avg Score', ascending=False)
    sector_df.to_excel(writer, sheet_name='Sector_Analysis', index=False)

def create_performance_sheet(results, writer):
    """Create performance metrics sheet"""
    if not results:
        empty_df = pd.DataFrame({'Metric': ['No data available'], 'Value': ['']})
        empty_df.to_excel(writer, sheet_name='Performance_Metrics', index=False)
        return

    consensus_mode = 'consensus_score' in results[0] or 'quality_score' in results[0]

    if consensus_mode:
        scores = [r.get('consensus_score', 0) for r in results]
        quality_scores = [r.get('quality_score', 0) for r in results]
        confidences = [r.get('confidence', 0) * 100 for r in results]

        performance_data = {
            'Metric': [
                'Total Consensus Picks',
                'Average Consensus Score',
                'Median Consensus Score',
                'Consensus Score Std Dev',
                'Top 10% Consensus Threshold',
                'Bottom 10% Consensus Threshold',
                'Average Quality Score',
                'Median Quality Score',
                'Average Confidence %',
                '4/4 Agreement Count',
                '3/4 Agreement Count',
                '2/4 Agreement Count',
                'Strong Buy Count',
                'Buy Count',
                'Weak Buy Count',
                'Low Risk Count',
                'Medium Risk Count',
                'High Risk Count'
            ],
            'Value': [
                len(results),
                f"{np.mean(scores):.2f}",
                f"{np.median(scores):.2f}",
                f"{np.std(scores):.2f}",
                f"{np.percentile(scores, 90):.2f}",
                f"{np.percentile(scores, 10):.2f}",
                f"{np.mean(quality_scores):.2f}",
                f"{np.median(quality_scores):.2f}",
                f"{np.mean(confidences):.1f}%",
                len([r for r in results if r.get('strategies_agreeing') == 4]),
                len([r for r in results if r.get('strategies_agreeing') == 3]),
                len([r for r in results if r.get('strategies_agreeing') == 2]),
                len([r for r in results if r.get('recommendation') == 'STRONG BUY']),
                len([r for r in results if r.get('recommendation') == 'BUY']),
                len([r for r in results if r.get('recommendation') == 'WEAK BUY']),
                len([r for r in results if r.get('risk_level') == 'Low']),
                len([r for r in results if r.get('risk_level') == 'Medium']),
                len([r for r in results if r.get('risk_level') == 'High'])
            ]
        }
    else:
        scores = [r.get('overall_score', 0) for r in results]
        predictions = [r.get('prediction', 0) for r in results]

        performance_data = {
            'Metric': [
                'Total Stocks Analyzed',
                'Average Overall Score',
                'Median Overall Score',
                'Standard Deviation',
                'Top 10% Threshold',
                'Bottom 10% Threshold',
                'Average Predicted Return',
                'Max Predicted Return',
                'Min Predicted Return',
                'Strong Buy Count',
                'Buy Count',
                'Hold Count',
                'Sell Count',
                'High Risk Count',
                'Medium Risk Count',
                'Low Risk Count'
            ],
            'Value': [
                len(results),
                f"{np.mean(scores):.2f}",
                f"{np.median(scores):.2f}",
                f"{np.std(scores):.2f}",
                f"{np.percentile(scores, 90):.2f}",
                f"{np.percentile(scores, 10):.2f}",
                f"{np.mean(predictions) * 100:.2f}%",
                f"{np.max(predictions) * 100:.2f}%",
                f"{np.min(predictions) * 100:.2f}%",
                len([r for r in results if r.get('recommendation') == 'STRONG BUY']),
                len([r for r in results if r.get('recommendation') == 'BUY']),
                len([r for r in results if r.get('recommendation') == 'HOLD']),
                len([r for r in results if 'SELL' in r.get('recommendation', '')]),
                len([r for r in results if r.get('risk_level') == 'High']),
                len([r for r in results if r.get('risk_level') == 'Medium']),
                len([r for r in results if r.get('risk_level') == 'Low'])
            ]
        }

    performance_df = pd.DataFrame(performance_data)
    performance_df.to_excel(writer, sheet_name='Performance_Metrics', index=False)

def add_excel_export_to_streamlit(results):
    """Add Excel export functionality to Streamlit app"""
    
    import streamlit as st
    
    if results and len(results) > 0:
        st.markdown("---")
        st.subheader("📊 Export Results")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**Export your analysis results to Excel for further analysis and portfolio management.**")
        
        with col2:
            export_filename = st.text_input("Filename (optional)", placeholder="SmartTrade_Analysis")
        
        with col3:
            if st.button("📥 Export to Excel", type="primary"):
                # Add timestamp if no filename provided
                if not export_filename:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_filename = f"SmartTrade_Analysis_{timestamp}"
                
                # Ensure .xlsx extension
                if not export_filename.endswith('.xlsx'):
                    export_filename += '.xlsx'
                
                # Export to Excel
                filename, message = export_analysis_to_excel(results, filename=export_filename)
                
                if filename:
                    st.success(f"✅ {message}")
                    
                    # Provide download link
                    if os.path.exists(filename):
                        with open(filename, 'rb') as f:
                            st.download_button(
                                label="📥 Download Excel File",
                                data=f.read(),
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                else:
                    st.error(f"❌ {message}")
        
        # Show export details
        with st.expander("📋 Export Details"):
            st.markdown("""
            **Excel file includes 8 sheets:**
            - **Summary**: Overview and key metrics
            - **Strong Buy**: Top recommendations only
            - **All Buy Signals**: All buy recommendations
            - **Detailed Analysis**: Complete analysis data
            - **Technical Indicators**: All technical metrics
            - **Risk Analysis**: Risk assessment data
            - **Sector Analysis**: Sector breakdown
            - **Performance Metrics**: Statistical analysis
            """)

if __name__ == "__main__":
    # Test the export functionality
    sample_results = [
        {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'recommendation': 'STRONG BUY',
            'current_price': 175.50,
            'prediction': 0.15,
            'confidence': 0.85,
            'overall_score': 85,
            'technical_score': 80,
            'fundamental_score': 90,
            'risk_level': 'Medium',
            'sector': 'Technology'
        }
    ]
    
    filename, message = export_analysis_to_excel(sample_results)
    print(f"Test export: {message}")
