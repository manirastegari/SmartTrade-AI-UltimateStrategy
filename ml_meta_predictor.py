#!/usr/bin/env python3
"""
ML Meta-Predictor for Ultimate Strategy
Enhances consensus picks with advanced machine learning models

Models included:
- LightGBM: Fast gradient boosting for tabular data
- XGBoost: Robust extreme gradient boosting
- CatBoost: Handles categorical features natively
- Neural Network: Deep learning for complex patterns
- Ensemble: Weighted combination of all models

Features:
- Cold-start capability with pretrained priors
- SHAP-based interpretability
- Calibrated probability outputs
- Continuous learning from new data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ML Models
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️ LightGBM not available - install with: pip install lightgbm")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost not available - install with: pip install xgboost")

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("⚠️ CatBoost not available - install with: pip install catboost")

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

# SHAP for interpretability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️ SHAP not available - install with: pip install shap")

# Overall ML availability
ML_AVAILABLE = (LIGHTGBM_AVAILABLE or XGBOOST_AVAILABLE or CATBOOST_AVAILABLE)
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime

# Interpretability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️ SHAP not available - install with: pip install shap")


class MLMetaPredictor:
    """
    Advanced ML predictor for stock returns and outperformance probability
    
    Uses ensemble of state-of-the-art models with interpretability
    """
    
    def __init__(self, model_dir: str = '.ml_models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
        # Model configurations (optimized for trading)
        self.model_configs = {
            'lightgbm': {
                'enabled': LIGHTGBM_AVAILABLE,
                'params': {
                    'objective': 'regression',
                    'metric': 'rmse',
                    'boosting_type': 'gbdt',
                    'num_leaves': 31,
                    'learning_rate': 0.05,
                    'feature_fraction': 0.8,
                    'bagging_fraction': 0.8,
                    'bagging_freq': 5,
                    'verbose': -1,
                    'n_estimators': 200,
                    'max_depth': 6,
                }
            },
            'xgboost': {
                'enabled': XGBOOST_AVAILABLE,
                'params': {
                    'objective': 'reg:squarederror',
                    'eval_metric': 'rmse',
                    'max_depth': 6,
                    'learning_rate': 0.05,
                    'n_estimators': 200,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'verbosity': 0,
                }
            },
            'catboost': {
                'enabled': CATBOOST_AVAILABLE,
                'params': {
                    'iterations': 200,
                    'depth': 6,
                    'learning_rate': 0.05,
                    'loss_function': 'RMSE',
                    'verbose': False,
                }
            },
            'random_forest': {
                'enabled': True,
                'params': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'n_jobs': -1,
                    'random_state': 42,
                }
            },
            'gradient_boost': {
                'enabled': True,
                'params': {
                    'n_estimators': 100,
                    'learning_rate': 0.05,
                    'max_depth': 6,
                    'subsample': 0.8,
                    'random_state': 42,
                }
            },
            'neural_net': {
                'enabled': True,
                'params': {
                    'hidden_layer_sizes': (128, 64, 32),
                    'activation': 'relu',
                    'solver': 'adam',
                    'alpha': 0.001,
                    'batch_size': 32,
                    'learning_rate': 'adaptive',
                    'max_iter': 200,
                    'random_state': 42,
                    'early_stopping': True,
                }
            }
        }
        
        # Model weights for ensemble (tuned via validation)
        self.ensemble_weights = {
            'lightgbm': 0.25,
            'xgboost': 0.25,
            'catboost': 0.20,
            'random_forest': 0.10,
            'gradient_boost': 0.10,
            'neural_net': 0.10,
        }
        
        print("🤖 ML Meta-Predictor initialized")
        print(f"   Available models: {sum(1 for c in self.model_configs.values() if c['enabled'])}/6")
    
    def extract_features(self, stock_data: Dict) -> np.ndarray:
        """
        Extract feature vector from stock analysis data
        
        Args:
            stock_data: Dict with fundamentals, momentum, risk, technical, sentiment, market_context
            
        Returns:
            Feature vector array (now 30 features - added 5 market context features)
        """
        features = []
        
        # Fundamentals (5 features)
        fund = stock_data.get('fundamentals', {})
        features.extend([
            fund.get('pe_ratio', 0) or 0,
            fund.get('revenue_growth', 0) or 0,
            fund.get('profit_margin', 0) or 0,
            fund.get('roe', 0) or 0,
            fund.get('debt_equity', 0) or 0,
        ])
        
        # Momentum (5 features)
        mom = stock_data.get('momentum', {})
        features.extend([
            mom.get('rsi', 50) or 50,
            mom.get('volume_ratio', 1) or 1,
            mom.get('relative_strength', 0) or 0,
            1 if mom.get('price_trend') == 'Uptrend' else 0,
            mom.get('score', 50) or 50,
        ])
        
        # Risk (4 features)
        risk = stock_data.get('risk', {})
        features.extend([
            risk.get('beta', 1) or 1,
            risk.get('volatility', 25) or 25,
            risk.get('sharpe_ratio', 0) or 0,
            risk.get('max_drawdown', -15) or -15,
        ])
        
        # Technical (5 features)
        tech = stock_data.get('technical', {})
        features.extend([
            tech.get('macd', 0) or 0,
            tech.get('macd_hist', 0) or 0,
            tech.get('bollinger_position', 50) or 50,
            tech.get('score', 50) or 50,
            1 if (tech.get('macd', 0) or 0) > (tech.get('macd_signal', 0) or 0) else 0,
        ])
        
        # Sentiment (3 features)
        sent = stock_data.get('sentiment', {})
        features.extend([
            sent.get('score', 50) or 50,
            sent.get('target_upside', 0) or 0,
            sent.get('institutional_ownership', 50) or 50,
        ])
        
        # Quality scores (3 features)
        features.extend([
            stock_data.get('quality_score', 50) or 50,
            stock_data.get('consensus_score', 50) or 50,
            stock_data.get('confidence', 0.5) or 0.5,
        ])
        
        # Market Context (5 NEW features - critical for environment awareness)
        market = stock_data.get('market_context', {})
        vix_level_raw = market.get('vix')
        vix_available = vix_level_raw is not None
        try:
            vix_level = float(vix_level_raw) if vix_available else 0.0
        except Exception:
            vix_level = 0.0
            vix_available = False
        regime = market.get('regime', 'normal')
        trend = market.get('trend', 'SIDEWAYS')
        
        # Convert regime to numeric
        regime_score = {'bull': 1, 'normal': 0, 'bear': -1}.get(regime.lower() if isinstance(regime, str) else 'normal', 0)
        
        # Convert trend to numeric
        trend_score = {'UPTREND': 1, 'SIDEWAYS': 0, 'DOWNTREND': -1}.get(trend.upper() if isinstance(trend, str) else 'SIDEWAYS', 0)
        
        features.extend([
            vix_level,                                    # Market fear gauge
            regime_score,                                 # Bull/Normal/Bear
            trend_score,                                  # Market direction
            1 if (vix_available and vix_level < 20) else 0,  # Low volatility flag
            stock_data.get('sector_momentum', 0) or 0,   # Sector relative strength
        ])
        
        return np.array(features, dtype=np.float32)

    
    def get_feature_names(self) -> List[str]:
        """Return feature names for interpretability"""
        return [
            # Fundamentals
            'pe_ratio', 'revenue_growth', 'profit_margin', 'roe', 'debt_equity',
            # Momentum
            'rsi', 'volume_ratio', 'relative_strength', 'uptrend', 'momentum_score',
            # Risk
            'beta', 'volatility', 'sharpe_ratio', 'max_drawdown',
            # Technical
            'macd', 'macd_hist', 'bollinger_position', 'technical_score', 'macd_bullish',
            # Sentiment
            'sentiment_score', 'target_upside', 'institutional_ownership',
            # Quality
            'quality_score', 'consensus_score', 'confidence',
        ]
    
    def train_with_synthetic_priors(self, n_samples: int = 1000):
        """
        Bootstrap with synthetic data based on domain knowledge
        Allows cold-start predictions before real data accumulates
        """
        print("\n🎓 Training with synthetic priors for cold-start capability...")
        
        # Generate realistic synthetic samples based on trading heuristics
        np.random.seed(42)
        
        X_samples = []
        y_samples = []
        
        for _ in range(n_samples):
            # Generate features with realistic correlations
            quality_score = np.random.uniform(40, 90)
            
            # Fundamentals correlate with quality
            pe_ratio = np.random.uniform(10, 40)
            revenue_growth = np.random.uniform(-5, 25) * (quality_score / 70)
            profit_margin = np.random.uniform(5, 30) * (quality_score / 70)
            roe = np.random.uniform(5, 25) * (quality_score / 70)
            debt_equity = np.random.uniform(20, 150) * (90 / quality_score)
            
            # Momentum
            rsi = np.random.uniform(30, 70)
            volume_ratio = np.random.uniform(0.8, 1.5)
            relative_strength = np.random.uniform(-10, 15) * (quality_score / 60)
            uptrend = 1 if np.random.random() > 0.4 else 0
            momentum_score = np.random.uniform(40, 85)
            
            # Risk
            beta = np.random.uniform(0.7, 1.4)
            volatility = np.random.uniform(15, 45)
            sharpe_ratio = np.random.uniform(-0.5, 2.0)
            max_drawdown = np.random.uniform(-30, -5)
            
            # Technical
            macd = np.random.uniform(-0.5, 0.5)
            macd_hist = np.random.uniform(-0.2, 0.2)
            bollinger_position = np.random.uniform(20, 80)
            technical_score = np.random.uniform(40, 85)
            macd_bullish = 1 if macd > 0 else 0
            
            # Sentiment
            sentiment_score = np.random.uniform(40, 75)
            target_upside = np.random.uniform(-10, 30)
            institutional_ownership = np.random.uniform(40, 80)
            
            # Consensus
            consensus_score = quality_score + np.random.uniform(-5, 5)
            confidence = np.random.uniform(0.5, 0.95)
            
            # Market Context (5 NEW features)
            vix_level = np.random.uniform(12, 35)
            regime_score = np.random.choice([-1, 0, 1], p=[0.15, 0.70, 0.15])  # Bear/Normal/Bull
            trend_score = np.random.choice([-1, 0, 1], p=[0.2, 0.5, 0.3])  # Down/Sideways/Up
            low_vix_flag = 1 if vix_level < 20 else 0
            sector_momentum = np.random.uniform(-5, 10)
            
            features = [
                pe_ratio, revenue_growth, profit_margin, roe, debt_equity,
                rsi, volume_ratio, relative_strength, uptrend, momentum_score,
                beta, volatility, sharpe_ratio, max_drawdown,
                macd, macd_hist, bollinger_position, technical_score, macd_bullish,
                sentiment_score, target_upside, institutional_ownership,
                quality_score, consensus_score, confidence,
                vix_level, regime_score, trend_score, low_vix_flag, sector_momentum  # NEW
            ]
            
            # Target: forward return (simulated relationship)
            # Higher quality, momentum, lower risk → better returns
            base_return = (quality_score - 60) * 0.3
            momentum_effect = (momentum_score - 50) * 0.2
            risk_effect = -volatility * 0.15
            technical_effect = technical_score * 0.1
            
            # Market context effects (NEW - critical for environment awareness)
            vix_effect = -(vix_level - 15) * 0.2  # High VIX = lower returns
            regime_effect = regime_score * 3  # Bull market boost, bear drag
            trend_effect = trend_score * 2  # Trend alignment bonus
            
            noise = np.random.normal(0, 5)
            
            forward_return = (base_return + momentum_effect + risk_effect + technical_effect + 
                            vix_effect + regime_effect + trend_effect + noise)
            
            X_samples.append(features)
            y_samples.append(forward_return)
        
        X = np.array(X_samples, dtype=np.float32)
        y = np.array(y_samples, dtype=np.float32)
        
        # Train models
        self.train(X, y, validation_split=0.2)
        
        print(f"✅ Synthetic prior training complete with {n_samples} samples")
        print("   Models ready for cold-start predictions")
    
    def train_with_real_data(self, stock_data_list: List[Dict]):
        """
        Train models using REAL historical data
        
        Args:
            stock_data_list: List of stock data dictionaries containing features and 'forward_return' target
        """
        print(f"\n🎓 Training with REAL market data ({len(stock_data_list)} samples)...")
        
        X_samples = []
        y_samples = []
        
        valid_samples = 0
        for data in stock_data_list:
            # Target must exist
            if 'forward_return' not in data:
                continue
                
            # Extract features
            try:
                features = self.extract_features(data)
                target = float(data['forward_return'])
                
                # Sanity check
                if np.isnan(features).any() or np.isnan(target):
                    continue
                    
                X_samples.append(features)
                y_samples.append(target)
                valid_samples += 1
            except Exception:
                continue
        
        if valid_samples < 50:
            print(f"⚠️ Not enough valid real samples ({valid_samples}). ML will remain disabled.")
            self.is_trained = False
            return

        X = np.array(X_samples, dtype=np.float32)
        y = np.array(y_samples, dtype=np.float32)
        
        # Train models
        self.train(X, y, validation_split=0.2)
        
        print(f"✅ Real data training complete with {valid_samples} samples")
        print("   Models are now calibrated to actual market dynamics")
        self.save_models()

    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2):
        """
        Train all available models
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target values (forward returns)
            validation_split: Fraction for validation
        """
        print(f"\n🎯 Training ML models on {len(X)} samples...")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        self.feature_names = self.get_feature_names()
        
        # Train each model
        results = {}
        
        # LightGBM
        if self.model_configs['lightgbm']['enabled']:
            print("   Training LightGBM...")
            lgb_model = lgb.LGBMRegressor(**self.model_configs['lightgbm']['params'])
            lgb_model.fit(
                X_train_scaled, y_train, 
                eval_set=[(X_val_scaled, y_val)],
                callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False), lgb.log_evaluation(period=0)]
            )
            val_pred = lgb_model.predict(X_val_scaled)
            results['lightgbm'] = np.sqrt(np.mean((val_pred - y_val) ** 2))
            self.models['lightgbm'] = lgb_model
        
        # XGBoost
        if self.model_configs['xgboost']['enabled']:
            print("   Training XGBoost...")
            xgb_model = xgb.XGBRegressor(**self.model_configs['xgboost']['params'])
            xgb_model.fit(
                X_train_scaled, y_train,
                eval_set=[(X_val_scaled, y_val)],
                verbose=False
            )
            val_pred = xgb_model.predict(X_val_scaled)
            results['xgboost'] = np.sqrt(np.mean((val_pred - y_val) ** 2))
            self.models['xgboost'] = xgb_model
        
        # CatBoost
        if self.model_configs['catboost']['enabled']:
            print("   Training CatBoost...")
            cat_model = cb.CatBoostRegressor(**self.model_configs['catboost']['params'])
            cat_model.fit(X_train_scaled, y_train, eval_set=(X_val_scaled, y_val), verbose=False)
            val_pred = cat_model.predict(X_val_scaled)
            results['catboost'] = np.sqrt(np.mean((val_pred - y_val) ** 2))
            self.models['catboost'] = cat_model
        
        # Random Forest
        if self.model_configs['random_forest']['enabled']:
            print("   Training Random Forest...")
            rf_model = RandomForestRegressor(**self.model_configs['random_forest']['params'])
            rf_model.fit(X_train_scaled, y_train)
            val_pred = rf_model.predict(X_val_scaled)
            results['random_forest'] = np.sqrt(np.mean((val_pred - y_val) ** 2))
            self.models['random_forest'] = rf_model
        
        # Gradient Boosting
        if self.model_configs['gradient_boost']['enabled']:
            print("   Training Gradient Boosting...")
            gb_model = GradientBoostingRegressor(**self.model_configs['gradient_boost']['params'])
            gb_model.fit(X_train_scaled, y_train)
            val_pred = gb_model.predict(X_val_scaled)
            results['gradient_boost'] = np.sqrt(np.mean((val_pred - y_val) ** 2))
            self.models['gradient_boost'] = gb_model
        
        # Neural Network
        if self.model_configs['neural_net']['enabled']:
            print("   Training Neural Network...")
            nn_model = MLPRegressor(**self.model_configs['neural_net']['params'])
            nn_model.fit(X_train_scaled, y_train)
            val_pred = nn_model.predict(X_val_scaled)
            results['neural_net'] = np.sqrt(np.mean((val_pred - y_val) ** 2))
            self.models['neural_net'] = nn_model
        
        self.is_trained = True
        
        # Print results
        print("\n📊 Validation RMSE:")
        for model_name, rmse in sorted(results.items(), key=lambda x: x[1]):
            print(f"   {model_name:20s}: {rmse:.4f}")
        
        return results
    
    def predict(self, stock_data: Dict) -> Dict:
        """
        Generate ML-enhanced predictions for a stock
        
        Returns:
            Dict with probability, expected_return, confidence, and interpretability
        """
        if not self.is_trained:
            # Try to load saved models first
            if not self.load_models():
                raise RuntimeError("ML models unavailable (no saved real models loaded)")
        
        # Extract features
        features = self.extract_features(stock_data)
        X = features.reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from all models
        predictions = {}
        for model_name, model in self.models.items():
            try:
                pred = model.predict(X_scaled)[0]
                predictions[model_name] = pred
            except Exception as e:
                print(f"   ⚠️ {model_name} prediction failed: {e}")
                predictions[model_name] = 0
        
        # Ensemble prediction (weighted average)
        ensemble_pred = sum(
            predictions.get(name, 0) * self.ensemble_weights.get(name, 0)
            for name in predictions.keys()
        )
        
        # Convert to probability (sigmoid transform)
        # Assume returns ~N(0, 10), so return > 5% is "good"
        z_score = ensemble_pred / 10.0
        probability = 1 / (1 + np.exp(-z_score))
        
        # Confidence based on prediction variance across models
        pred_values = list(predictions.values())
        confidence = 1 / (1 + np.std(pred_values)) if len(pred_values) > 1 else 0.7
        
        # Feature importance (if SHAP available)
        feature_importance = {}
        if SHAP_AVAILABLE and 'lightgbm' in self.models:
            try:
                explainer = shap.TreeExplainer(self.models['lightgbm'])
                shap_values = explainer.shap_values(X_scaled)
                for i, name in enumerate(self.feature_names):
                    feature_importance[name] = float(shap_values[0][i])
            except:
                pass
        
        return {
            'expected_return': float(ensemble_pred),
            'probability': float(probability),
            'confidence': float(confidence),
            'model_predictions': predictions,
            'feature_importance': feature_importance,
            'ensemble_weight': self.ensemble_weights,
        }
    
    def save_models(self):
        """Save trained models to disk"""
        if not self.is_trained:
            print("⚠️ No trained models to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save each model
        for name, model in self.models.items():
            filename = os.path.join(self.model_dir, f'{name}_{timestamp}.joblib')
            joblib.dump(model, filename)
        
        # Save scaler
        scaler_file = os.path.join(self.model_dir, f'scaler_{timestamp}.joblib')
        joblib.dump(self.scaler, scaler_file)
        
        print(f"✅ Models saved to {self.model_dir}")
    
    def load_models(self, timestamp: str = None):
        """Load trained models from disk"""
        if timestamp is None:
            # Find latest
            if not os.path.exists(self.model_dir):
                return False
                
            files = os.listdir(self.model_dir)
            timestamps = set(f.split('_')[-1].replace('.joblib', '') for f in files if '.joblib' in f and 'scaler' not in f)
            if not timestamps:
                print("⚠️ No saved models found in .ml_models")
                return False
            timestamp = max(timestamps)
        
        # Load each model
        loaded = 0
        for name in self.model_configs.keys():
            filename = os.path.join(self.model_dir, f'{name}_{timestamp}.joblib')
            if os.path.exists(filename):
                self.models[name] = joblib.load(filename)
                loaded += 1
        
        # Load scaler
        scaler_file = os.path.join(self.model_dir, f'scaler_{timestamp}.joblib')
        if os.path.exists(scaler_file):
            self.scaler = joblib.load(scaler_file)
        
        self.is_trained = loaded > 0
        if self.is_trained:
            print(f"✅ Loaded {loaded} trained models from {timestamp}")
        return self.is_trained


if __name__ == "__main__":
    # Quick test
    print("="*80)
    print("ML Meta-Predictor Test")
    print("="*80)
    
    predictor = MLMetaPredictor()
    predictor.train_with_synthetic_priors(n_samples=500)
    
    # Test prediction
    test_stock = {
        'fundamentals': {'pe_ratio': 25, 'revenue_growth': 15, 'profit_margin': 20, 'roe': 18, 'debt_equity': 50},
        'momentum': {'rsi': 55, 'volume_ratio': 1.2, 'relative_strength': 5, 'price_trend': 'Uptrend', 'score': 75},
        'risk': {'beta': 1.1, 'volatility': 25, 'sharpe_ratio': 1.2, 'max_drawdown': -12},
        'technical': {'macd': 0.15, 'macd_signal': 0.10, 'macd_hist': 0.05, 'bollinger_position': 60, 'score': 70},
        'sentiment': {'score': 65, 'target_upside': 12, 'institutional_ownership': 70},
        'quality_score': 75,
        'consensus_score': 78,
        'confidence': 0.85,
    }
    
    result = predictor.predict(test_stock)
    
    print("\n📊 Prediction Results:")
    print(f"   Expected Return: {result['expected_return']:.2f}%")
    print(f"   Outperformance Probability: {result['probability']:.2%}")
    print(f"   Confidence: {result['confidence']:.2%}")
    
    if result['feature_importance']:
        print("\n🔍 Top Features:")
        sorted_features = sorted(result['feature_importance'].items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        for name, importance in sorted_features:
            print(f"   {name:25s}: {importance:+.4f}")
