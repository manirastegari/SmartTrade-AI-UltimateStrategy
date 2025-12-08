#!/usr/bin/env python3
"""
Smart Caching System - Dramatically reduces API calls and speeds up analysis
Cache duration: 4 hours for market data (perfect for daily analysis)
"""

import shelve
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, Any
import pandas as pd
import hashlib


class SmartCache:
    """Intelligent caching system with automatic expiration"""
    
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, 'market_data.db')
        
        # Cache durations for different data types
        self.durations = {
            'history': timedelta(hours=1),       # OHLCV data - 1 hour for fresher reads
            'info': timedelta(hours=6),          # Company info - 6 hours
            'fundamentals': timedelta(hours=12), # Fundamental data - 12 hours
            'news': timedelta(hours=1),          # News - 1 hour
            'analysis': timedelta(hours=2),      # Analysis results - 2 hours
        }
        
        print(f"💾 Smart Cache initialized at {self.cache_dir}")
    
    def get_cached_data(self, symbol: str, data_type: str = 'history') -> Optional[Any]:
        """Get cached data if valid, otherwise return None"""
        try:
            with shelve.open(self.cache_file) as cache:
                key = f"{symbol}_{data_type}"
                if key in cache:
                    data, timestamp = cache[key]
                    duration = self.durations.get(data_type, timedelta(hours=4))
                    
                    if datetime.now() - timestamp < duration:
                        # Cache hit!
                        return data
                    else:
                        # Cache expired
                        del cache[key]
        except (dbm.error, shelve.Error, Exception) as e: # Modified to catch dbm.error and shelve.Error
            # Handle corrupt cache or overflow
            print(f"⚠️ Cache read error for {symbol} ({str(e)}). Resetting cache.")
            try:
                # Attempt to clear the corrupted cache file and its associated files
                if os.path.exists(self.cache_file):
                    os.remove(self.cache_file)
                # Also remove sidecar files if they exist (common with some dbm implementations)
                for ext in ['.dat', '.bak', '.dir', '.pag']: # Added .pag for some dbm implementations
                    if os.path.exists(self.cache_file + ext):
                        os.remove(self.cache_file + ext)
            except Exception as clear_e:
                print(f"⚠️ Error clearing corrupted cache: {clear_e}")
        
        return None
    
    def save_to_cache(self, symbol: str, data: Any, data_type: str = 'history'):
        """Save data to cache with timestamp"""
        try:
            with shelve.open(self.cache_file) as cache:
                key = f"{symbol}_{data_type}"
                cache[key] = (data, datetime.now())
        except Exception as e:
            print(f"⚠️ Cache write error for {symbol}: {e}")
    
    def get_cached_dataframe(self, symbol: str, data_type: str = 'history') -> Optional[pd.DataFrame]:
        """Specialized method for DataFrame caching"""
        data = self.get_cached_data(symbol, data_type)
        if data is not None and isinstance(data, pd.DataFrame):
            return data
        return None
    
    def cache_exists(self, symbol: str, data_type: str = 'history') -> bool:
        """Check if valid cache exists without loading data"""
        try:
            with shelve.open(self.cache_file) as cache:
                key = f"{symbol}_{data_type}"
                if key in cache:
                    _, timestamp = cache[key]
                    duration = self.durations.get(data_type, timedelta(hours=4))
                    return datetime.now() - timestamp < duration
        except:
            pass
        return False
    
    def get_cache_stats(self):
        """Get statistics about cache usage"""
        try:
            with shelve.open(self.cache_file) as cache:
                total_items = len(cache)
                valid_items = 0
                expired_items = 0
                
                for key in list(cache.keys()):
                    _, timestamp = cache[key]
                    data_type = key.split('_')[-1]
                    duration = self.durations.get(data_type, timedelta(hours=4))
                    
                    if datetime.now() - timestamp < duration:
                        valid_items += 1
                    else:
                        expired_items += 1
                
                return {
                    'total_items': total_items,
                    'valid_items': valid_items,
                    'expired_items': expired_items,
                    'hit_rate': f"{(valid_items/total_items)*100:.1f}%" if total_items > 0 else "0%"
                }
        except:
            return {'total_items': 0, 'valid_items': 0, 'expired_items': 0, 'hit_rate': '0%'}
    
    def clear_expired(self):
        """Remove expired cache entries"""
        try:
            with shelve.open(self.cache_file) as cache:
                expired_keys = []
                
                for key in list(cache.keys()):
                    _, timestamp = cache[key]
                    data_type = key.split('_')[-1]
                    duration = self.durations.get(data_type, timedelta(hours=4))
                    
                    if datetime.now() - timestamp >= duration:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del cache[key]
                
                print(f"🧹 Cleared {len(expired_keys)} expired cache entries")
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
    
    def clear_all(self):
        """Clear entire cache"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                print("🧹 Cache cleared completely")
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")


class BulkCache:
    """Cache for bulk operations (entire universe analysis)"""
    
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_hash(self, symbols: list) -> str:
        """Generate hash for symbol list"""
        symbol_str = '|'.join(sorted(symbols))
        return hashlib.md5(symbol_str.encode()).hexdigest()[:12]
    
    def save_bulk_results(self, symbols: list, results: list, analysis_type: str = 'ultimate'):
        """Save results from bulk analysis"""
        try:
            hash_id = self.get_hash(symbols)
            filename = os.path.join(self.cache_dir, f"bulk_{analysis_type}_{hash_id}.pkl")
            
            cache_data = {
                'symbols': symbols,
                'results': results,
                'timestamp': datetime.now(),
                'analysis_type': analysis_type
            }
            
            with open(filename, 'wb') as f:
                pickle.dump(cache_data, f)
            
            print(f"💾 Bulk results cached: {len(results)} stocks")
        except Exception as e:
            print(f"⚠️ Bulk cache save error: {e}")
    
    def load_bulk_results(self, symbols: list, analysis_type: str = 'ultimate', 
                         max_age_hours: int = 8) -> Optional[list]:
        """Load cached bulk results if available and fresh"""
        try:
            hash_id = self.get_hash(symbols)
            filename = os.path.join(self.cache_dir, f"bulk_{analysis_type}_{hash_id}.pkl")
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check age
            age = datetime.now() - cache_data['timestamp']
            if age < timedelta(hours=max_age_hours):
                print(f"✅ Loaded cached bulk analysis ({age.seconds//3600}h old)")
                return cache_data['results']
            else:
                print(f"⏰ Cached bulk analysis too old ({age.seconds//3600}h)")
                return None
                
        except Exception as e:
            print(f"⚠️ Bulk cache load error: {e}")
            return None
