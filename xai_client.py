#!/usr/bin/env python3
"""
xAI Client - Grok Chat Completions wrapper for post-analysis review

Usage:
	from xai_client import XAIClient
	client = XAIClient()
	ai_review = client.analyze_ultimate_strategy(consensus_recs, market, sector)

Notes:
- Reads API key from env var XAI_API_KEY or api_keys.XAI_API_KEY if present.
- Defaults model to 'grok-4-fast-reasoning' (cheap + strong). Override via XAI_MODEL.
- Returns a structured dict suitable for UI and Excel export.
"""

from __future__ import annotations

import os
import json
import time
from typing import Any, Dict, List, Optional

import requests


class XAIClient:
	"""Thin client for xAI Grok chat completions."""

	def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 60):
		# Prefer environment variables, fallback to repo api_keys.py if present
		key = api_key or os.getenv("XAI_API_KEY")
		if not key:
			try:
				from api_keys import XAI_API_KEY as KEY_FROM_REPO  # type: ignore
				key = KEY_FROM_REPO
			except Exception:
				key = None

		self.api_key = key
		# Default to a strong and cost-effective model per your guidance
		self.model = model or os.getenv("XAI_MODEL", "grok-4-fast-reasoning")
		# xAI typically uses an OpenAI-compatible endpoint path
		self.base_url = base_url or os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
		self.timeout = timeout

	def is_configured(self) -> bool:
		return bool(self.api_key)

	def _headers(self) -> Dict[str, str]:
		return {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
		}

	def _safe_json(self, text: str) -> Dict[str, Any]:
		"""Try to parse JSON robustly; fallback to wrapping raw text."""
		try:
			return json.loads(text)
		except Exception:
			# Try to extract a JSON block from common fenced formats
			try:
				import re
				m = re.search(r"\{[\s\S]*\}\s*$", text)
				if m:
					return json.loads(m.group(0))
			except Exception:
				pass
		return {"raw": text}

	def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 2000) -> Dict[str, Any]:
		"""Call xAI chat completions with provided messages."""
		if not self.is_configured():
			raise RuntimeError("XAI API key not configured. Set XAI_API_KEY or add XAI_API_KEY to api_keys.py")

		url = f"{self.base_url}/chat/completions"
		payload = {
			"model": self.model,
			"messages": messages,
			"temperature": temperature,
			"max_tokens": max_tokens,
			# Encourage JSON output
			"response_format": {"type": "json_object"},
		}

		try:
			resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
			resp.raise_for_status()
		except requests.HTTPError as e:
			# Graceful fallback: if the selected model is unavailable, try a compatible cheaper/fast variant
			try:
				status = e.response.status_code if e.response is not None else None
				body = e.response.text if e.response is not None else ""
			except Exception:
				status, body = None, ""
			if (self.model == "grok-4-fast-reasoning") and (status in (400, 404, 422) or "model" in body.lower()):
				alt_model = "grok-4-fast-non-reasoning"
				payload_alt = dict(payload)
				payload_alt["model"] = alt_model
				alt = requests.post(url, headers=self._headers(), json=payload_alt, timeout=self.timeout)
				alt.raise_for_status()
				data = alt.json()
				try:
					content = data["choices"][0]["message"]["content"]
				except Exception:
					content = json.dumps(data)
				out = self._safe_json(content)
				# annotate chosen model
				out["model_used"] = alt_model
				return out
			raise

		data = resp.json()
		try:
			content = data["choices"][0]["message"]["content"]
		except Exception:
			content = json.dumps(data)

		out = self._safe_json(content)
		out["model_used"] = self.model
		return out

	def analyze_ultimate_strategy(
		self,
		consensus_recs: List[Dict[str, Any]],
		market_analysis: Optional[Dict[str, Any]] = None,
		sector_analysis: Optional[Dict[str, Any]] = None,
		*,
		top_n: int = 25,
		tiers: Optional[Dict[str, List[Dict[str, Any]]]] = None,
		market_news_summary: Optional[List[str]] = None,
		symbol_news: Optional[Dict[str, List[str]]] = None,
		sec_filings_summary: Optional[Dict[str, List[Dict[str, str]]]] = None,
	) -> Dict[str, Any]:
		"""Ask xAI to produce a professional AI review of the run results.

		Returns a dict with keys including: summary, market_assessment, timeframe_guidance,
		fundamentals_review, technical_review, ai_picks (list of {symbol, rationale, risk, reward, timeframe, confidence}).
		"""
		if not self.is_configured():
			return {
				"enabled": False,
				"reason": "XAI_API_KEY not configured",
			}

		# Prepare a compact payload for the model
		# Always include a top list for global ranking, but also pass tiered groups when provided.
		top = sorted(consensus_recs, key=lambda r: (r.get("strategies_agreeing", 0), r.get("consensus_score", 0)), reverse=True)[:top_n]
		def _slim(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
			out: List[Dict[str, Any]] = []
			for s in items:
				out.append({
					"symbol": s.get("symbol"),
					"consensus_score": round(float(s.get("consensus_score", 0)), 2),
					"strategies_agreeing": int(s.get("strategies_agreeing", 0)),
					"strong_buy_count": int(s.get("strong_buy_count", 0)),
					"recommendation": s.get("recommendation"),
					"confidence": int(s.get("confidence", 0)),
					"risk_level": s.get("risk_level"),
					"upside_potential": float(s.get("upside_potential", 0)),
					"sector": s.get("sector"),
				})
			return out

		slim_top = _slim(top)
		slim_tiers = None
		if tiers:
			slim_tiers = {
				"tier1": _slim(tiers.get("tier1", [])),
				"tier2": _slim(tiers.get("tier2", [])),
				"tier3": _slim(tiers.get("tier3", [])),
				"alpha_plus": _slim(tiers.get("alpha_plus", [])),
			}

		system = {
			"role": "system",
			"content": (
				"You are an institutional-grade trading analyst AI. Provide conservative, professional, and actionable analysis. "
				"Your goal: deliver extremely low-risk, high-reward recommendations, with risk controls and timeframes. "
				"Use knowledge of news, sentiment, volume, institutional flow, SEC filings, geopolitics, tariffs, and industry momentum. "
				"Respond in strict JSON with keys: summary, market_assessment, timeframe_guidance, fundamentals_review, "
				"technical_review, ai_picks (array of objects: symbol, rationale, timeframe, risk, reward, confidence, notes)."
			)
		}
		# Trim context to keep tokens efficient
		def _trim_list(lst: Optional[List[str]], n: int) -> List[str]:
			return list(lst[:n]) if isinstance(lst, list) else []
		def _trim_map(m: Optional[Dict[str, List[str]]], n: int) -> Dict[str, List[str]]:
			if not isinstance(m, dict):
				return {}
			return {k: _trim_list(v, n) for k, v in m.items()}

		user = {
			"role": "user",
			"content": json.dumps({
				"task": "Post-run Ultimate Strategy review",
				"market_analysis": market_analysis or {},
				"sector_analysis": sector_analysis or {},
				"top_consensus": slim_top,
				"tiers": slim_tiers,
				"news_context": {
					"market_headlines": _trim_list(market_news_summary, 6),
					"symbol_news": _trim_map(symbol_news, 3),
					"sec_filings": sec_filings_summary or {},
				},
				"instructions": {
					"assess_market_suitability": True,
					"determine_timeframes": ["short-term (days)", "swing (weeks)", "position (months)"],
					"verify_fundamentals": True,
					"evaluate_chart_patterns": True,
					"evaluate_technicals": ["RSI", "MACD", "MAs", "Breakouts"],
					"target_outcome": "very low-risk and high-reward picks with stop-loss/take-profit guidance",
				},
			})
		}

		try:
			result = self.chat([system, user])
			result["enabled"] = True
			result["model"] = self.model
			result["generated_at"] = int(time.time())
			return result
		except Exception as e:
			return {
				"enabled": False,
				"reason": f"xAI request failed: {e}",
			}


__all__ = ["XAIClient"]

