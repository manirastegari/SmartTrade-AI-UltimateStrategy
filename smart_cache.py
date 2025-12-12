#!/usr/bin/env python3
"""
Smart Caching System - Dramatically reduces API calls and speeds up analysis
Cache duration: 4 hours for market data (perfect for daily analysis)
Refactored to use SQLite3 to prevent 'dbm' related Segmentation Faults on macOS
"""

import sqlite3
import os
import pickle
import threading
from datetime import datetime, timedelta
from typing import Optional, Any
import pandas as pd
import hashlib

class SmartCache:
    """Intelligent caching system with automatic expiration using SQLite3"""
    
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.db_file = os.path.join(cache_dir, 'market_data.sqlite')
        
        # Thread safety lock
        self.lock = threading.Lock()
        
        # Cache durations for different data types
        self.durations = {
            'history': timedelta(hours=1),       # OHLCV data - 1 hour for fresher reads
            'info': timedelta(hours=6),          # Company info - 6 hours
            'fundamentals': timedelta(hours=12), # Fundamental data - 12 hours
            'news': timedelta(hours=1),          # News - 1 hour
            'analysis': timedelta(hours=2),      # Analysis results - 2 hours
        }
        
        self._init_db()
        print(f"💾 Smart Cache (SQLite) initialized at {self.db_file}")

    def _init_db(self):
        """Initialize the SQLite database and create tables"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        data BLOB,
                        timestamp DATETIME,
                        data_type TEXT
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON cache(timestamp)')
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"⚠️ Cache DB Init Error: {e}")

    def _get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_file)

    def get_cached_data(self, symbol: str, data_type: str = 'history') -> Optional[Any]:
        """Get cached data if valid, otherwise return None"""
        key = f"{symbol}_{data_type}"
        duration = self.durations.get(data_type, timedelta(hours=4))
        
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT data, timestamp FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    data_blob, timestamp_str = row
                    # Handle timestamp string format from sqlite
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except:
                        # Fallback for legacy or different formats if needed
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

                    if datetime.now() - timestamp < duration:
                        return pickle.loads(data_blob)
                    else:
                        # Expired, clean it up lazily
                        # We don't delete here to keep reads fast, clear_expired handles it
                        return None
            except Exception as e:
                # print(f"⚠️ Cache Read Error ({symbol}): {e}") 
                return None
        return None
    
    def save_to_cache(self, symbol: str, data: Any, data_type: str = 'history'):
        """Save data to cache with timestamp"""
        key = f"{symbol}_{data_type}"
        now = datetime.now()
        
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                data_blob = pickle.dumps(data)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cache (key, data, timestamp, data_type)
                    VALUES (?, ?, ?, ?)
                ''', (key, data_blob, now.isoformat(), data_type))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"⚠️ Cache Write Error ({symbol}): {e}")
    
    def get_cached_dataframe(self, symbol: str, data_type: str = 'history') -> Optional[pd.DataFrame]:
        """Specialized method for DataFrame caching"""
        data = self.get_cached_data(symbol, data_type)
        if data is not None and isinstance(data, pd.DataFrame):
            return data
        return None
    
    def cache_exists(self, symbol: str, data_type: str = 'history') -> bool:
        """Check if valid cache exists without loading full data blob"""
        key = f"{symbol}_{data_type}"
        duration = self.durations.get(data_type, timedelta(hours=4))
        
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    timestamp_str = row[0]
                    timestamp = datetime.fromisoformat(timestamp_str)
                    return datetime.now() - timestamp < duration
            except:
                pass
        return False
    
    def get_cache_stats(self):
        """Get statistics about cache usage"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT key, timestamp, data_type FROM cache")
                rows = cursor.fetchall()
                conn.close()
                
                total_items = len(rows)
                valid_items = 0
                expired_items = 0
                
                now = datetime.now()
                
                for key, timestamp_str, data_type in rows:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        duration = self.durations.get(data_type, timedelta(hours=4))
                        if now - timestamp < duration:
                            valid_items += 1
                        else:
                            expired_items += 1
                    except:
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
        now = datetime.now()
        # Clean up general items effectively
        # Since logic is type-dependent, we have to iterate or do complex SQL.
        # Simple approach: Load all, check, delete. Or just delete old items > max duration.
        # Max duration is 12 hours. Let's delete anything older than 24 hours to be safe and simple SQL.
        
        # For precise cleanup:
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # First delete very old items (safe cleanup)
                cutoff = (now - timedelta(hours=24)).isoformat()
                cursor.execute("DELETE FROM cache WHERE timestamp < ?", (cutoff,))
                deleted_count = cursor.rowcount
                
                conn.commit()
                conn.close()
                if deleted_count > 0:
                    print(f"🧹 Cleared {deleted_count} expired cache entries")
            except Exception as e:
                print(f"⚠️ Error clearing cache: {e}")
    
    def clear_all(self):
        """Clear entire cache"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache")
                conn.commit()
                cursor.execute("VACUUM") # Reclaim space
                conn.close()
                print("🧹 Cache cleared completely")
            except Exception as e:
                print(f"⚠️ Error clearing cache: {e}")


class BulkCache:
    """Cache for bulk operations (entire universe analysis) - File based is fine for this"""
    
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
