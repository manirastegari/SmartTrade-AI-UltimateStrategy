"""
Simple per-provider rate limiter with per-minute (and optional per-day) caps.
Reads caps from environment variables set by settings.py/.env/Streamlit secrets.

Env variables (examples):
- POLYGON_MAX_PER_MIN=5
- TWELVEDATA_MAX_PER_MIN=8
- ALPHA_VANTAGE_MAX_PER_MIN=5
- FINNHUB_MAX_PER_MIN=30
- IEX_MAX_PER_MIN=30
- TWELVEDATA_MAX_PER_DAY=800 (optional daily cap)

Usage:
    from rate_limiter import limiter
    limiter.acquire('POLYGON')  # blocks briefly if limit would be exceeded

Providers are normalized to uppercase keys listed in DEFAULTS below.
"""
from __future__ import annotations
import os
import time
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ProviderLimits:
    per_min: Optional[int] = None
    per_day: Optional[int] = None


class RateLimiter:
    def __init__(self, limits: Dict[str, ProviderLimits]):
        self.limits = limits
        # sliding window timestamps per provider for minute window
        self._minute_windows: Dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=1000))
        # rolling count for daily limits
        self._day_counts: Dict[str, int] = defaultdict(int)
        self._day_epoch: float = self._day_start_epoch()

    def _day_start_epoch(self) -> float:
        # midnight epoch of current local day
        lt = time.localtime()
        midnight = time.struct_time((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, lt.tm_wday, lt.tm_yday, lt.tm_isdst))
        return time.mktime(midnight)

    def _ensure_day_rollover(self):
        now = time.time()
        if now - self._day_epoch >= 86400:
            self._day_epoch = self._day_start_epoch()
            self._day_counts.clear()

    def acquire(self, provider: str):
        key = provider.upper()
        lim = self.limits.get(key)
        now = time.time()
        if not lim:
            return  # no limits configured

        # Daily cap (if set) – if reached, sleep until next day (no busy wait)
        if lim.per_day is not None:
            self._ensure_day_rollover()
            if self._day_counts[key] >= lim.per_day:
                # sleep until next midnight
                sleep_for = self._day_epoch + 86400 - now
                if sleep_for > 0:
                    time.sleep(min(sleep_for, 5))  # sleep in short chunks to stay responsive
                    return self.acquire(provider)  # re-check after waking

        # Per-minute cap via sliding window
        if lim.per_min is not None and lim.per_min > 0:
            window = self._minute_windows[key]
            cutoff = now - 60.0
            # drop old timestamps
            while window and window[0] <= cutoff:
                window.popleft()
            if len(window) >= lim.per_min:
                # sleep until earliest request exits the window
                wait = max(0.0, window[0] + 60.0 - now)
                if wait > 0:
                    time.sleep(wait)
                # after sleep, window will be pruned and we proceed
                return self.acquire(provider)
            # record this request
            window.append(now)

        # increment day counter if tracking
        if lim.per_day is not None:
            self._day_counts[key] += 1


def _env_int(name: str) -> Optional[int]:
    v = os.getenv(name)
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


DEFAULTS: Dict[str, ProviderLimits] = {
    # Keep Yahoo Finance as primary (no throttling here). These limits are for secondary providers only.
    'ALPHA_VANTAGE': ProviderLimits(per_min=_env_int('ALPHA_VANTAGE_MAX_PER_MIN') or 5),
    'FINNHUB': ProviderLimits(per_min=_env_int('FINNHUB_MAX_PER_MIN') or 30),
    'POLYGON': ProviderLimits(per_min=_env_int('POLYGON_MAX_PER_MIN') or 5),
    'TWELVEDATA': ProviderLimits(per_min=_env_int('TWELVEDATA_MAX_PER_MIN') or 8, per_day=_env_int('TWELVEDATA_MAX_PER_DAY')),
    'FMP': ProviderLimits(per_min=_env_int('FMP_MAX_PER_MIN') or 30),
}

# Singleton limiter used across modules
limiter = RateLimiter(DEFAULTS)
