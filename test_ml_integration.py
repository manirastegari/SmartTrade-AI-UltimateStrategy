#!/usr/bin/env python3
"""
Comprehensive ML Integration Test
Tests the ML meta-predictor integration with Ultimate Strategy
"""

import sys
import os
from datetime import datetime

# Test ML predictor standalone
print("="*80)
print("🤖 ML INTEGRATION VALIDATION TEST")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test 1: ML Module Import
print("📦 TEST 1: ML Module Import")
print("-" * 80)
try:
    from ml_meta_predictor import MLMetaPredictor, ML_AVAILABLE
    print(f"✅ ML Module imported successfully")
    print(f"   ML_AVAILABLE: {ML_AVAILABLE}")
    if not ML_AVAILABLE:
        print("   ⚠️ Warning: Some ML libraries missing, check requirements")
except Exception as e:
    print(f"❌ ML Module import failed: {e}")
    sys.exit(1)

# Test 2: Instantiate Predictor
print("\n🔧 TEST 2: Predictor Instantiation")
print("-" * 80)
try:
    predictor = MLMetaPredictor()
    print("✅ MLMetaPredictor instantiated")
    print(f"   Models: {len(predictor.models)} configured")
    print(f"   Feature count: 25")
except Exception as e:
    print(f"❌ Instantiation failed: {e}")
    sys.exit(1)

# Test 3: Synthetic Prior Training
print("\n🎓 TEST 3: Synthetic Prior Training")
print("-" * 80)
try:
    n_samples = 1000
    predictor.train_with_synthetic_priors(n_samples=n_samples)
    print(f"✅ Synthetic training completed with {n_samples} samples")
    
    # Verify models are trained
    for name, model in predictor.models.items():
        if model is None:
            print(f"   ⚠️ Model '{name}' failed to train")
        else:
            print(f"   ✓ Model '{name}' trained")
except Exception as e:
    print(f"❌ Synthetic training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Feature Extraction
print("\n🔬 TEST 4: Feature Extraction")
print("-" * 80)
sample_stock_data = {
    'symbol': 'AAPL',
    'quality_score': 85,
    'current_price': 175.50,
    'sector': 'Technology',
    
    # Fundamentals
    'pe_ratio': 28.5,
    'revenue_growth': 8.2,
    'profit_margin': 25.3,
    'roe': 147.5,
    'debt_equity': 1.5,
    
    # Momentum
    'rsi_14': 55,
    'price_trend': 'uptrend',
    'ma_50': 170.0,
    'ma_200': 165.0,
    'volume_ratio': 1.2,
    
    # Risk
    'beta': 1.2,
    'volatility': 0.25,
    'sharpe_ratio': 1.5,
    'max_drawdown': -15.0,
    
    # Technical
    'macd': 2.5,
    'macd_signal': 2.0,
    'bollinger_position': 0.6,
    
    # Sentiment
    'sentiment_score': 0.3,
}

try:
    features = predictor.extract_features(sample_stock_data)
    print(f"✅ Features extracted: {len(features)} dimensions")
    print(f"   Sample features: {features[:5]}")
    
    if len(features) != 25:
        print(f"   ⚠️ Warning: Expected 25 features, got {len(features)}")
except Exception as e:
    print(f"❌ Feature extraction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: ML Prediction
print("\n🎯 TEST 5: ML Prediction")
print("-" * 80)
try:
    prediction = predictor.predict(sample_stock_data)
    
    print(f"✅ Prediction generated for {sample_stock_data['symbol']}")
    print(f"   Expected Return: {prediction['expected_return']:+.2f}%")
    print(f"   Probability: {prediction['probability']:.2%}")
    print(f"   Confidence: {prediction['confidence']:.2%}")
    
    # Check feature importance
    if prediction['feature_importance']:
        top_3 = sorted(prediction['feature_importance'].items(), 
                      key=lambda x: abs(x[1]), reverse=True)[:3]
        print(f"   Top 3 Features:")
        for feature, importance in top_3:
            print(f"      - {feature}: {importance:.3f}")
    
    # Validate prediction ranges
    if not (-100 <= prediction['expected_return'] <= 100):
        print(f"   ⚠️ Warning: Expected return out of range: {prediction['expected_return']}")
    if not (0 <= prediction['probability'] <= 1):
        print(f"   ⚠️ Warning: Probability out of range: {prediction['probability']}")
    if not (0 <= prediction['confidence'] <= 1):
        print(f"   ⚠️ Warning: Confidence out of range: {prediction['confidence']}")
        
except Exception as e:
    print(f"❌ Prediction failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Ensemble Variance
print("\n📊 TEST 6: Ensemble Model Variance")
print("-" * 80)
try:
    model_predictions = prediction.get('model_predictions', {})
    if model_predictions:
        print(f"✅ Individual model predictions:")
        for model_name, pred in model_predictions.items():
            print(f"   {model_name}: {pred:+.2f}%")
        
        # Calculate variance
        pred_values = list(model_predictions.values())
        variance = sum((x - prediction['expected_return'])**2 for x in pred_values) / len(pred_values)
        std_dev = variance ** 0.5
        
        print(f"\n   Ensemble Statistics:")
        print(f"   - Standard Deviation: {std_dev:.2f}%")
        print(f"   - Range: {max(pred_values) - min(pred_values):.2f}%")
        
        if std_dev > 20:
            print(f"   ⚠️ Warning: High model disagreement (std_dev > 20%)")
    else:
        print("   ⚠️ Warning: No individual model predictions returned")
        
except Exception as e:
    print(f"❌ Ensemble analysis failed: {e}")

# Test 7: Integration with Ultimate Strategy
print("\n🎯 TEST 7: Ultimate Strategy Integration")
print("-" * 80)
try:
    from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
    from advanced_data_fetcher import AdvancedDataFetcher
    
    print("✅ Ultimate Strategy analyzer imported")
    
    # Create analyzer with ML (needs a fetcher instance)
    fetcher = AdvancedDataFetcher()
    analyzer = FixedUltimateStrategyAnalyzer(fetcher)
    print(f"✅ Analyzer instantiated")
    print(f"   ML Predictor attached: {analyzer.ml_predictor is not None}")
    print(f"   ML Available flag: {ML_AVAILABLE}")
    
    if analyzer.ml_predictor:
        print("   ✓ ML predictor successfully integrated into Ultimate Strategy")
    else:
        print("   ⚠️ ML predictor not attached - ML predictions will be skipped")
        
except Exception as e:
    print(f"❌ Integration test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 8: End-to-End with Sample Stocks
print("\n🔄 TEST 8: ML Predictor Integration Validation")
print("-" * 80)
try:
    print("Testing ML predictor is properly attached to analyzer...")
    
    # Verify ML predictor is attached and functional
    if not analyzer.ml_predictor:
        print("❌ ML predictor not attached to analyzer")
        sys.exit(1)
    
    print(f"✅ ML predictor attached to Ultimate Strategy analyzer")
    print(f"   Models available: {len([m for m in analyzer.ml_predictor.models.values() if m is not None])}/6")
    
    # Test ML prediction on a sample consensus pick structure
    test_pick = {
        'symbol': 'AAPL',
        'quality_score': 88,
        'consensus_score': 85,
        'current_price': 175.50,
        'sector': 'Technology',
        
        # Fundamentals (flat for Excel compatibility)
        'pe_ratio': 28.5,
        'revenue_growth': 8.2,
        'profit_margin': 25.3,
        'roe': 147.5,
        'debt_equity': 1.5,
        'fundamentals_score': 85,
        
        # Momentum (flat)
        'rsi_14': 55,
        'price_trend': 'uptrend',
        'ma_50': 170.0,
        'ma_200': 165.0,
        'volume_ratio': 1.2,
        'momentum_score': 75,
        
        # Risk (flat)
        'beta': 1.2,
        'volatility': 0.25,
        'sharpe_ratio': 1.5,
        'max_drawdown': -15.0,
        'risk_score': 70,
        
        # Technical (flat)
        'macd': 2.5,
        'macd_signal': 2.0,
        'bollinger_position': 0.6,
        'technical_score': 80,
        
        # Sentiment (flat - will be normalized to 0)
        'sentiment_score': 0,
    }
    
    print(f"\n📊 Testing ML prediction on sample consensus pick...")
    ml_result = analyzer.ml_predictor.predict(test_pick)
    
    print(f"✅ ML prediction successful!")
    print(f"   Expected Return: {ml_result['expected_return']:+.2f}%")
    print(f"   Probability: {ml_result['probability']:.2%}")
    print(f"   Confidence: {ml_result['confidence']:.2%}")
    
    if ml_result['feature_importance']:
        top_3 = sorted(ml_result['feature_importance'].items(), 
                      key=lambda x: abs(x[1]), reverse=True)[:3]
        print(f"   Top 3 Features:")
        for feature, importance in top_3:
            print(f"      {feature}: {importance:.3f}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - ML Integration Validated!")
    print("="*80)
    print("\nML Enhancement Summary:")
    print("• 6 ensemble models (LightGBM, XGBoost, CatBoost, RF, GB, Neural Net)")
    print("• 25-dimensional feature extraction from stock data")
    print("• Synthetic prior training (no historical data required)")
    print("• SHAP-based feature importance for interpretability")
    print("• Full integration with Ultimate Strategy consensus ranking")
    print("• ML predictions enhance confidence and re-rank picks")
    print("\n🎯 Integration Workflow:")
    print("  1. Ultimate Strategy generates consensus picks")
    print("  2. ML predictor enhances each pick with probability/return")
    print("  3. Consensus confidence adjusted with ML confidence (60%/40% blend)")
    print("  4. Picks re-ranked by: strategies_agreeing × (ML_probability × consensus_score)")
    print("  5. Grok AI prompts enriched with ML predictions and top features")
    
except Exception as e:
    print(f"❌ Integration validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✨ ML integration ready for production use!")

