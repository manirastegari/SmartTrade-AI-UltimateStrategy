#!/usr/bin/env python3
"""
Lightweight News + SEC Filings fetcher (free sources)

Purpose: Provide a compact context to the AI review to better capture
momentum, catalysts, and fresh filings without heavy/paid APIs.

Sources (no keys required):
- Google News RSS (query-based): https://news.google.com/rss/search?q=...
- SEC EDGAR Atom feed by ticker: https://www.sec.gov/cgi-bin/browse-edgar

Notes:
- Designed to run on a small subset of symbols (Tier 1/2 leaders) to avoid
  rate limits and reduce latency. Default delays are gentle and can be tuned.
"""

from __future__ import annotations

import time
import html
import urllib.parse
from typing import Dict, List, Optional

import requests
import xml.etree.ElementTree as ET


def _fetch_xml(url: str, timeout: int = 10) -> Optional[str]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) NewsSEC/1.0",
            "Accept": "application/xml,text/xml,application/rss+xml,application/atom+xml;q=0.9,*/*;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        pass
    return None


def _parse_rss_titles(xml_text: str, limit: int = 5) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    try:
        root = ET.fromstring(xml_text)
        # RSS 2.0 typically: rss/channel/item
        for item in root.findall('.//item'):
            title_el = item.find('title')
            pub_el = item.find('pubDate')
            title = title_el.text.strip() if title_el is not None and title_el.text else ''
            published = pub_el.text.strip() if pub_el is not None and pub_el.text else ''
            if title:
                items.append({"title": html.unescape(title), "published": published})
            if len(items) >= limit:
                break
    except Exception:
        pass
    return items


def _parse_atom_entries(xml_text: str, limit: int = 5) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    try:
        root = ET.fromstring(xml_text)
        # Atom typically: feed/entry
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall('.//atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            updated_el = entry.find('atom:updated', ns)
            title = title_el.text.strip() if title_el is not None and title_el.text else ''
            published = updated_el.text.strip() if updated_el is not None and updated_el.text else ''
            if title:
                entries.append({"title": html.unescape(title), "published": published})
            if len(entries) >= limit:
                break
    except Exception:
        pass
    return entries


def fetch_market_headlines(query: str = "stock market today", *, limit: int = 5, delay_s: float = 0.0) -> List[Dict[str, str]]:
    """Fetch general market headlines via Google News RSS."""
    try:
        q = urllib.parse.quote_plus(query)
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        xml_text = _fetch_xml(url)
        if delay_s:
            time.sleep(delay_s)
        if xml_text:
            return _parse_rss_titles(xml_text, limit=limit)
    except Exception:
        pass
    return []


def fetch_symbol_news(symbols: List[str], *, per_symbol: int = 3, delay_s: float = 0.4) -> Dict[str, List[Dict[str, str]]]:
    """Fetch a few headlines per symbol via Google News RSS (query: "<SYM> stock")."""
    out: Dict[str, List[Dict[str, str]]] = {}
    for sym in symbols:
        try:
            q = urllib.parse.quote_plus(f"{sym} stock")
            url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
            xml_text = _fetch_xml(url)
            if xml_text:
                out[sym] = _parse_rss_titles(xml_text, limit=per_symbol)
            else:
                out[sym] = []
        except Exception:
            out[sym] = []
        if delay_s:
            time.sleep(delay_s)
    return out


def fetch_sec_filings(symbols: List[str], *, per_symbol: int = 2, delay_s: float = 0.5) -> Dict[str, List[Dict[str, str]]]:
    """Fetch recent SEC filings via EDGAR Atom feed by ticker (best-effort).

    Note: EDGAR accepts ticker in CIK param for many issuers; if unavailable,
    this will simply return empty for that symbol.
    """
    out: Dict[str, List[Dict[str, str]]] = {}
    for sym in symbols:
        try:
            # EDGAR Atom feed by ticker
            url = (
                "https://www.sec.gov/cgi-bin/browse-edgar?"
                f"action=getcompany&CIK={urllib.parse.quote_plus(sym)}&owner=exclude&count=10&output=atom"
            )
            xml_text = _fetch_xml(url, timeout=12)
            if xml_text:
                entries = _parse_atom_entries(xml_text, limit=per_symbol)
                # Try to extract form type from title when present
                cleaned: List[Dict[str, str]] = []
                for e in entries:
                    title = e.get("title", "")
                    form = ""
                    # Common patterns: "8-K - NVIDIA CORP", "10-Q - ..."
                    for k in ("8-K", "10-Q", "10-K", "13F", "S-1", "S-3", "6-K"):
                        if k in title:
                            form = k
                            break
                    cleaned.append({"title": title, "published": e.get("published", ""), "form": form})
                out[sym] = cleaned
            else:
                out[sym] = []
        except Exception:
            out[sym] = []
        if delay_s:
            time.sleep(delay_s)
    return out


def build_compact_context_for_ai(symbols: List[str], *, market_headlines: int = 5, per_symbol_news: int = 3, per_symbol_filings: int = 2) -> Dict[str, object]:
    """Fetch market + per-symbol context and return a compact dict for AI prompt."""
    market = fetch_market_headlines(limit=market_headlines)
    news = fetch_symbol_news(symbols, per_symbol=per_symbol_news)
    filings = fetch_sec_filings(symbols, per_symbol=per_symbol_filings)

    def _format_headlines(items: List[Dict[str, str]]) -> List[str]:
        return [i.get("title", "") for i in items if i.get("title")][:market_headlines]

    return {
        "market_news_summary": _format_headlines(market),
        "symbol_news": {k: _format_headlines(v) for k, v in news.items()},
        "sec_filings_summary": filings,
    }


__all__ = [
    "fetch_market_headlines",
    "fetch_symbol_news",
    "fetch_sec_filings",
    "build_compact_context_for_ai",
]
