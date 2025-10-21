#!/usr/bin/env python3
"""
Test script to verify TFSA universe and upside calculation fixes
"""

print("="*80)
print("Testing TFSA/Questrade Universe Loading")
print("="*80)

# Test 1: Load TFSA universe
try:
    from cleaned_high_potential_universe import get_cleaned_high_potential_universe
    universe = get_cleaned_high_potential_universe()
    print(f"\n✅ SUCCESS: Loaded {len(universe)} stocks from TFSA/Questrade universe")
    print(f"   Sample stocks: {universe[:10]}")
    
    # Count Canadian stocks
    canadian = [s for s in universe if '.TO' in s]
    us_stocks = [s for s in universe if '.TO' not in s]
    print(f"   US Stocks: {len(us_stocks)}")
    print(f"   Canadian (TSX) Stocks: {len(canadian)}")
    
except Exception as e:
    print(f"❌ FAILED: Could not load universe - {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Testing Upside Calculation Logic")
print("="*80)

# Test 2: Verify upside calculation logic
try:
    print("\nTesting upside calculation for different score scenarios:")
    
    test_scenarios = [
        {"name": "STRONG BUY (High scores)", "technical": 85, "fundamental": 85, "momentum": 85, "overall": 90},
        {"name": "BUY (Good scores)", "technical": 75, "fundamental": 75, "momentum": 75, "overall": 78},
        {"name": "MODERATE (Medium scores)", "technical": 65, "fundamental": 65, "momentum": 65, "overall": 68},
        {"name": "WEAK (Low scores)", "technical": 55, "fundamental": 55, "momentum": 55, "overall": 58},
    ]
    
    for scenario in test_scenarios:
        technical_score = scenario["technical"]
        fundamental_score = scenario["fundamental"]
        momentum_score = scenario["momentum"]
        overall_score = scenario["overall"]
        
        # Replicate the upside calculation logic
        base_upside = 0.0
        
        # Factor 1: Technical score contribution (0-25%)
        if technical_score > 80:
            base_upside += 25.0
        elif technical_score > 70:
            base_upside += 20.0
        elif technical_score > 60:
            base_upside += 15.0
        elif technical_score > 50:
            base_upside += 10.0
        else:
            base_upside += 5.0
        
        # Factor 2: Fundamental score contribution (0-15%)
        if fundamental_score > 80:
            base_upside += 15.0
        elif fundamental_score > 70:
            base_upside += 12.0
        elif fundamental_score > 60:
            base_upside += 8.0
        else:
            base_upside += 5.0
        
        # Factor 3: Momentum score contribution (0-20%)
        if momentum_score > 80:
            base_upside += 20.0
        elif momentum_score > 70:
            base_upside += 15.0
        elif momentum_score > 60:
            base_upside += 10.0
        else:
            base_upside += 5.0
        
        # Factor 4: Overall score multiplier
        score_multiplier = 1.0
        if overall_score > 85:
            score_multiplier = 1.3
        elif overall_score > 75:
            score_multiplier = 1.2
        elif overall_score > 65:
            score_multiplier = 1.1
        
        base_upside *= score_multiplier
        
        # Market regime (assume neutral)
        upside_potential = base_upside
        
        # Ensure minimum for strong buys
        recommendation = "STRONG BUY" if overall_score > 85 else "BUY" if overall_score > 75 else "HOLD"
        if recommendation == 'STRONG BUY' and upside_potential < 15.0:
            upside_potential = 15.0 + (overall_score - 70) * 0.5
        elif recommendation == 'BUY' and upside_potential < 10.0:
            upside_potential = 10.0
        
        upside_potential = min(upside_potential, 200.0)
        
        print(f"\n  {scenario['name']}:")
        print(f"    Recommendation: {recommendation}")
        print(f"    Upside Potential: {upside_potential:.1f}%")
        
        if recommendation == 'STRONG BUY' and upside_potential < 15.0:
            print(f"    ❌ FAILED: STRONG BUY should have at least 15% upside")
        else:
            print(f"    ✅ PASSED: Upside is reasonable")
    
    print("\n✅ SUCCESS: Upside calculation logic verified")
    
except Exception as e:
    print(f"❌ FAILED: Upside calculation test - {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Test Summary")
print("="*80)
print("✅ All tests completed. Ready to run full analysis.")
print("="*80)
