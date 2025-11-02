"""
Centralized runtime settings loader.
- Loads .env if python-dotenv is installed
- Mirrors Streamlit secrets into os.environ (non-destructive)
- Provides init() to be called at app start; also runs on import for convenience

This keeps secrets out of the repo while ensuring the app works locally and in CI.
"""
from __future__ import annotations
import os

_KEYS = [
    "XAI_API_KEY",
    "XAI_MODEL",
    "XAI_BASE_URL",
    "ALPHA_VANTAGE_API_KEY",
    "FINNHUB_API_KEY",
    "IEX_CLOUD_API_KEY",
    "POLYGON_API_KEY",
    "TWELVE_DATA_API_KEY",
]

def _load_dotenv_if_available():
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        # Fallback: minimal .env loader (KEY=VALUE per line)
        try:
            repo_root = os.path.dirname(__file__)
            env_path = os.path.join(repo_root, '.env')
            if os.path.isfile(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        s = line.strip()
                        if not s or s.startswith('#'):
                            continue
                        if '=' not in s:
                            continue
                        k, v = s.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

def _merge_streamlit_secrets():
    try:
        import streamlit as st  # type: ignore
        if hasattr(st, "secrets"):
            for k in _KEYS:
                if k not in os.environ and k in st.secrets:
                    val = st.secrets.get(k)
                    if val:
                        os.environ[k] = str(val)
    except Exception:
        pass

def init():
    _load_dotenv_if_available()
    _merge_streamlit_secrets()

# Run on import for convenience
init()
