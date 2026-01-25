
"""
Smart Rate Limit Manager
Handles API rate limits with exponential backoff, jitter, and automated token bucket management.
"""
import time
import random
import logging
from collections import deque, defaultdict
from typing import Dict, Optional, Callable, Any
from functools import wraps

logger = logging.getLogger('SmartTrade.RateLimitManager')

class SmartRateLimiter:
    """
    Advanced rate limiter with exponential backoff and jitter.
    Supports both pre-emptive rate limiting and reactive backoff on 429 errors.
    """
    
    def __init__(self):
        # Default limits per provider (can be overridden)
        self.limits: Dict[str, int] = {
            'YAHOO': 120,      # Liberal limit for Yahoo (2 requests/sec avg)
            'ALPHA_VANTAGE': 5,
            'FINNHUB': 30,
            'POLYGON': 5,
            'GROK': 10        # xAI/Grok limit
        }
        
        # Tracking windows
        self._minute_windows: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=200))
        self._backoff_until: Dict[str, float] = defaultdict(float)
        self._consecutive_errors: Dict[str, int] = defaultdict(int)
        
    def acquire(self, provider: str = 'YAHOO', weight: int = 1) -> None:
        """
        Acquire permission to make a request.
        Blocks if rate limit exceeded or in backoff period.
        """
        provider = provider.upper()
        limit = self.limits.get(provider, 60)
        
        # 1. Check Backoff
        now = time.time()
        if now < self._backoff_until[provider]:
            wait_time = self._backoff_until[provider] - now
            time.sleep(wait_time)
            now = time.time()
        
        # 2. Check Rate Limit (Sliding Window)
        window = self._minute_windows[provider]
        
        # Clean old timestamps
        while window and window[0] <= now - 60.0:
            window.popleft()
            
        # If at limit, wait
        if len(window) + weight > limit:
            # Calculate wait time: Time until oldest expires + buffer
            wait_time = (window[0] + 60.0 - now) + 0.1
            if wait_time > 0:
                time.sleep(wait_time)
                now = time.time()
                
                # Re-clean after sleep
                while window and window[0] <= now - 60.0:
                    window.popleft()
        
        # Record new request(s)
        for _ in range(weight):
            window.append(now)
            
    def handle_error(self, provider: str = 'YAHOO', error_code: int = 429) -> None:
        """
        Report an error to trigger backoff.
        Only triggers on 429 (Too Many Requests) or 5xx server errors.
        """
        provider = provider.upper()
        
        if error_code == 429 or 500 <= error_code < 600:
            self._consecutive_errors[provider] += 1
            count = self._consecutive_errors[provider]
            
            # Exponential Backoff: 2^n * (base=5s) + jitter
            base_wait = 5 * (2 ** (min(count, 4) - 1)) # 5, 10, 20, 40 max base
            jitter = random.uniform(0, 0.3 * base_wait)
            wait_time = base_wait + jitter
            
            self._backoff_until[provider] = time.time() + wait_time
            logger.warning(f"⚠️ {provider} rate limited/error ({error_code}). Backing off for {wait_time:.1f}s")
            
    def success(self, provider: str = 'YAHOO') -> None:
        """Report successful request to reset error counters."""
        self._consecutive_errors[provider.upper()] = 0

# Global instance
rate_limit_manager = SmartRateLimiter()

def rate_limit(provider: str = 'YAHOO'):
    """Decorator to automatically handle rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rate_limit_manager.acquire(provider)
            try:
                result = func(*args, **kwargs)
                rate_limit_manager.success(provider)
                return result
            except Exception as e:
                # Check for 429 in exception
                if '429' in str(e) or 'Too Many Requests' in str(e):
                    rate_limit_manager.handle_error(provider, 429)
                raise e
        return wrapper
    return decorator
