"""
Lightweight market context signals with minimal free API usage.

Features:
- SOXX/QQQ relative strength (ratio trend) as sector leadership proxy.
- QQQ and SOXX above/below SMA50/200 booleans.
- Optional capped intraday VWAP status for a small set of symbols.

Data sources: yfinance (free). Token-light and rate-limit friendly.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import math
import time


def _safe_import_yf():
	try:
		import yfinance as yf  # type: ignore
		return yf
	except Exception:
		return None


def _fetch_history(symbol: str, period: str = "3mo", interval: str = "1d"):
	yf = _safe_import_yf()
	if yf is None:
		return None
	try:
		df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
		if df is None or df.empty:
			return None
		return df
	except Exception:
		return None


def _sma(series, window: int) -> Optional[float]:
	try:
		if series is None or len(series) < window:
			return None
		return float(series[-window:].mean())
	except Exception:
		return None


def _linear_regression_slope(y_values) -> Optional[float]:
	"""Return slope of y over x=range(len(y))."""
	try:
		n = len(y_values)
		if n < 3:
			return None
		x = list(range(n))
		sum_x = sum(x)
		sum_y = float(sum(y_values))
		sum_xy = sum(x[i] * float(y_values[i]) for i in range(n))
		sum_x2 = sum(v * v for v in x)
		denom = (n * sum_x2 - sum_x * sum_x)
		if denom == 0:
			return None
		slope = (n * sum_xy - sum_x * sum_y) / denom
		return float(slope)
	except Exception:
		return None


def get_soxx_qqq_signals(period_days: int = 60) -> Dict:
	"""
	Compute semiconductor relative strength vs QQQ, and SMA checks for both.
	Uses daily data for low API impact.
	"""
	out = {
		"soxx_qqq_ratio_slope": None,
		"soxx_qqq_is_rising": None,
		"qqq_above_sma50": None,
		"qqq_above_sma200": None,
		"soxx_above_sma50": None,
		"soxx_above_sma200": None,
	}

	# Try primary tickers, then fallbacks to reduce noisy failures (avoid DataFrame truthiness)
	soxx = _fetch_history("SOXX", period="6mo", interval="1d")
	if soxx is None:
		soxx = _fetch_history("SMH", period="6mo", interval="1d")
	qqq = _fetch_history("QQQ", period="6mo", interval="1d")
	if qqq is None:
		qqq = _fetch_history("SPY", period="6mo", interval="1d")
	if soxx is None or qqq is None:
		return out

	try:
		soxx_close = soxx["Close"].dropna()
		qqq_close = qqq["Close"].dropna()
		# Align index intersection
		idx = soxx_close.index.intersection(qqq_close.index)
		soxx_close = soxx_close.loc[idx]
		qqq_close = qqq_close.loc[idx]
		if len(idx) < 20:
			return out
		# Ratio and slope over the last `period_days` (cap to available)
		window = min(period_days, len(idx))
		ratio = (soxx_close / qqq_close).tail(window)
		slope = _linear_regression_slope(list(ratio.values))
		out["soxx_qqq_ratio_slope"] = slope
		out["soxx_qqq_is_rising"] = (slope is not None and slope > 0)

		# SMA checks
		qqq_sma50 = _sma(qqq_close, 50)
		qqq_sma200 = _sma(qqq_close, 200)
		soxx_sma50 = _sma(soxx_close, 50)
		soxx_sma200 = _sma(soxx_close, 200)
		last_qqq = float(qqq_close.iloc[-1])
		last_soxx = float(soxx_close.iloc[-1])

		out["qqq_above_sma50"] = (qqq_sma50 is not None and last_qqq > qqq_sma50)
		out["qqq_above_sma200"] = (qqq_sma200 is not None and last_qqq > qqq_sma200)
		out["soxx_above_sma50"] = (soxx_sma50 is not None and last_soxx > soxx_sma50)
		out["soxx_above_sma200"] = (soxx_sma200 is not None and last_soxx > soxx_sma200)
	except Exception:
		return out

	return out


def summarize_regime(signals: Dict) -> Dict:
	"""Return a compact regime label/suggestion based on signals."""
	s = signals or {}
	rising = bool(s.get("soxx_qqq_is_rising"))
	q50 = s.get("qqq_above_sma50")
	q200 = s.get("qqq_above_sma200")
	sx50 = s.get("soxx_above_sma50")
	sx200 = s.get("soxx_above_sma200")

	score = 0
	for v in (rising, q50, q200, sx50, sx200):
		score += 1 if v else 0

	if score >= 4:
		return {
			"regime": "Risk-On",
			"hint": "Semis leading; OK to size up on confirmed breakouts; favor tech momentum.",
		}
	if score >= 2:
		return {
			"regime": "Neutral",
			"hint": "Selective longs; confirm with VWAP/ORH; avoid extended names.",
		}
	return {
		"regime": "Caution",
		"hint": "Prefer defensive posture; wait for VWAP reclaims and broadening.",
	}


def get_market_context_signals() -> Dict:
	"""High-level wrapper returning signals + regime summary."""
	sig = get_soxx_qqq_signals()
	summary = summarize_regime(sig)
	return {**sig, **summary}


def get_intraday_vwap_status(symbols: List[str], max_symbols: int = 10, sleep_s: float = 0.12) -> Dict[str, Dict]:
	"""
	Compute simple intraday VWAP status for a small set of symbols.
	- Uses yfinance 1m bars for current session; falls back silently if unavailable.
	- Returns dict: {symbol: {"above_vwap": bool, "vwap": float, "last": float}}
	"""
	yf = _safe_import_yf()
	out: Dict[str, Dict] = {}
	if yf is None:
		return out
	symbols = list(dict.fromkeys([s for s in symbols if s]))[:max_symbols]
	for sym in symbols:
		try:
			df = yf.download(sym, period="1d", interval="1m", progress=False, auto_adjust=True)
			if df is None or df.empty or "Volume" not in df.columns:
				continue
			# Typical price per bar
			tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
			vol = df["Volume"].astype(float)
			vwap = float((tp * vol).sum() / max(vol.sum(), 1.0))
			last = float(df["Close"].iloc[-1])
			out[sym] = {
				"above_vwap": last >= vwap,
				"vwap": vwap,
				"last": last,
			}
		except Exception:
			# skip symbol on any error
			pass
		time.sleep(sleep_s)
	return out


__all__ = [
	"get_soxx_qqq_signals",
	"get_market_context_signals",
	"get_intraday_vwap_status",
	"summarize_regime",
]

