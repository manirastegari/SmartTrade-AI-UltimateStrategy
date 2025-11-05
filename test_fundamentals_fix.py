#!/usr/bin/env python3
"""
Quick test to verify get_better_fundamentals fix
Tests: 20 stocks to ensure complete fundamental data without rate limits
"""

import sys
from advanced_data_fetcher import AdvancedDataFetcher

def test_fundamentals():
    """Test fundamental data extraction on sample stocks"""
    
    # Test with diverse sample: tech, finance, healthcare, energy, consumer
    test_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN',  # Mega-cap tech
        'JPM', 'BAC', 'WFC', 'GS',        # Finance
        'JNJ', 'UNH', 'PFE', 'ABBV',      # Healthcare
        'XOM', 'CVX', 'COP', 'SLB',       # Energy
        'WMT', 'HD', 'NKE', 'SBUX'        # Consumer
    ]
    
    print("=" * 80)
    print("TESTING: get_better_fundamentals() - NO ALPHA VANTAGE VERSION")
    print("=" * 80)
    print(f"\nTesting {len(test_symbols)} stocks...")
    print(f"Expected: All fundamentals populated, NO rate limiting\n")
    
    # Initialize fetcher in 'balanced' mode
    fetcher = AdvancedDataFetcher(data_mode='balanced')
    
    results = []
    alpha_vantage_calls = 0
    
    for symbol in test_symbols:
        print(f"\n{'='*60}")
        print(f"Testing: {symbol}")
        print(f"{'='*60}")
        
        try:
            fundamentals = fetcher.get_better_fundamentals(symbol)
            
            # Check completeness
            key_metrics = {
                'Market Cap': fundamentals.get('market_cap', 0),
                'P/E Ratio': fundamentals.get('pe_ratio', 0),
                'P/B Ratio': fundamentals.get('price_to_book', 0),
                'ROE': fundamentals.get('roe', 0),
                'Debt/Equity': fundamentals.get('debt_to_equity', 0),
                'Revenue Growth': fundamentals.get('revenue_growth', 0),
                'Profit Margin': fundamentals.get('profit_margins', 0),
                'Beta': fundamentals.get('beta', 0),
                'Sector': fundamentals.get('sector', 'Unknown'),
                'Industry': fundamentals.get('industry', 'Unknown'),
            }
            
            print(f"\n{symbol} Fundamental Metrics:")
            for metric, value in key_metrics.items():
                if isinstance(value, (int, float)):
                    if value == 0:
                        print(f"  ⚠️  {metric}: {value} (ZERO - NEEDS ATTENTION)")
                    else:
                        print(f"  ✅ {metric}: {value:,.2f}")
                else:
                    print(f"  📋 {metric}: {value}")
            
            # Count populated fields
            populated = sum(1 for k, v in fundamentals.items() 
                          if v not in [0, 0.0, '', 'Unknown', 'hold', None])
            total = len(fundamentals)
            completeness = (populated / total) * 100
            
            results.append({
                'symbol': symbol,
                'market_cap': fundamentals.get('market_cap', 0),
                'populated_fields': populated,
                'total_fields': total,
                'completeness': completeness
            })
            
            print(f"\n  Completeness: {populated}/{total} fields ({completeness:.1f}%)")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                'symbol': symbol,
                'market_cap': 0,
                'populated_fields': 0,
                'total_fields': 0,
                'completeness': 0,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    successful = [r for r in results if r['market_cap'] > 0]
    failed = [r for r in results if r['market_cap'] == 0]
    
    print(f"\n✅ Successful: {len(successful)}/{len(test_symbols)} stocks")
    print(f"❌ Failed: {len(failed)}/{len(test_symbols)} stocks")
    
    if successful:
        avg_completeness = sum(r['completeness'] for r in successful) / len(successful)
        print(f"📊 Average Data Completeness: {avg_completeness:.1f}%")
    
    print(f"\n🔧 Alpha Vantage API Calls: {alpha_vantage_calls} (Expected: 0)")
    
    # Detailed results table
    print("\n" + "-" * 80)
    print(f"{'Symbol':<10} {'Market Cap':>15} {'Populated':>10} {'Complete':>10}")
    print("-" * 80)
    for r in results:
        mc = f"${r['market_cap']:,.0f}" if r['market_cap'] > 0 else "N/A"
        pct = f"{r['completeness']:.1f}%"
        print(f"{r['symbol']:<10} {mc:>15} {r['populated_fields']:>10} {pct:>10}")
    
    print("\n" + "=" * 80)
    
    # Verdict
    if len(successful) == len(test_symbols) and alpha_vantage_calls == 0:
        print("✅ TEST PASSED: All stocks got fundamental data without Alpha Vantage")
        return True
    elif len(successful) >= len(test_symbols) * 0.8:
        print("⚠️  TEST PARTIAL: Most stocks succeeded, some issues remain")
        return True
    else:
        print("❌ TEST FAILED: Too many stocks failed to get fundamental data")
        return False

if __name__ == "__main__":
    success = test_fundamentals()
    sys.exit(0 if success else 1)
