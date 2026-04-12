#!/usr/bin/env python3
"""
SmartTrade AI — Public Viewer App
Deployed on Streamlit Cloud. Shows pre-computed analysis results,
past reports, and tracks visitors.
"""

import streamlit as st
import json
import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import sqlite3

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartTrade AI — Ultimate Strategy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

RESULTS_DIR = Path(__file__).resolve().parent / "results"
VISITORS_DB = Path(__file__).resolve().parent / "visitors.db"

# ─── Visitor Tracking ─────────────────────────────────────────────────────────

def init_visitors_db():
    """Initialize SQLite database for visitor tracking."""
    conn = sqlite3.connect(str(VISITORS_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            visit_time TEXT,
            user_agent TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visit_counter (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_visits INTEGER DEFAULT 0
        )
    """)
    conn.execute("INSERT OR IGNORE INTO visit_counter (id, total_visits) VALUES (1, 0)")
    conn.commit()
    conn.close()


def record_visit():
    """Record a visitor and increment counter."""
    try:
        # Get visitor info from Streamlit headers
        headers = st.context.headers if hasattr(st, 'context') and hasattr(st.context, 'headers') else {}
        ip = headers.get("X-Forwarded-For", headers.get("X-Real-Ip", "Unknown"))
        if isinstance(ip, str) and "," in ip:
            ip = ip.split(",")[0].strip()
        user_agent = headers.get("User-Agent", "Unknown")
        visit_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        conn = sqlite3.connect(str(VISITORS_DB))
        conn.execute(
            "INSERT INTO visitors (ip, visit_time, user_agent) VALUES (?, ?, ?)",
            (ip, visit_time, user_agent[:200])
        )
        conn.execute("UPDATE visit_counter SET total_visits = total_visits + 1 WHERE id = 1")
        conn.commit()
        conn.close()
    except Exception:
        pass  # Don't crash the app if tracking fails


def get_visitor_stats():
    """Get visitor count and recent visitors."""
    try:
        conn = sqlite3.connect(str(VISITORS_DB))
        total = conn.execute("SELECT total_visits FROM visit_counter WHERE id = 1").fetchone()
        total_count = total[0] if total else 0
        recent = conn.execute(
            "SELECT ip, visit_time FROM visitors ORDER BY id DESC LIMIT 50"
        ).fetchall()
        conn.close()
        return total_count, recent
    except Exception:
        return 0, []


# ─── Data Loading ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_latest_results():
    """Load the most recent analysis results."""
    latest_path = RESULTS_DIR / "latest.json"
    if not latest_path.exists():
        return None, None

    with open(latest_path) as f:
        pointer = json.load(f)

    json_file = RESULTS_DIR / pointer.get("json_file", "")
    if not json_file.exists():
        return None, None

    with open(json_file) as f:
        data = json.load(f)

    return data, pointer


@st.cache_data(ttl=300)
def load_all_runs():
    """Load metadata for all past runs."""
    runs = []
    for fp in sorted(RESULTS_DIR.glob("run_*.json"), reverse=True):
        try:
            with open(fp) as f:
                d = json.load(f)
            runs.append({
                "file": fp.name,
                "date": d.get("run_date", "?"),
                "timestamp": d.get("run_timestamp", ""),
                "total_analyzed": d.get("total_analyzed", 0),
                "consensus_count": d.get("consensus_count", 0),
                "tier_5": d.get("tier_5_count", 0),
                "tier_4": d.get("tier_4_count", 0),
                "signal": d.get("market_timing", {}).get("action", "N/A"),
                "excel": d.get("excel_file", ""),
            })
        except Exception:
            continue
    return runs


def load_run_data(json_filename: str):
    """Load a specific run's data."""
    fp = RESULTS_DIR / json_filename
    if fp.exists():
        with open(fp) as f:
            return json.load(f)
    return None


# ─── UI Helpers ───────────────────────────────────────────────────────────────

SIGNAL_COLORS = {
    "STRONG_BUY": "#00c853", "BUY": "#00c853",
    "CAUTIOUS_BUY": "#ffd600", "WAIT": "#ff9100",
    "HOLD": "#ff6d00", "TAKE_PROFITS": "#d50000", "CRISIS": "#b71c1c",
}


def signal_badge(signal: str, action: str, confidence: int):
    color = SIGNAL_COLORS.get(signal, "#9e9e9e")
    st.markdown(
        f"""<div style="background:{color}; color:#fff; padding:16px 24px;
        border-radius:12px; text-align:center; margin-bottom:16px;">
        <h2 style="margin:0; color:#fff;">{action}</h2>
        <p style="margin:4px 0 0; font-size:1.1em; color:rgba(255,255,255,0.9);">
        Signal: {signal} · Confidence: {confidence}%</p>
        </div>""",
        unsafe_allow_html=True,
    )


def render_picks_table(picks: list, title: str):
    """Render a formatted table of picks."""
    if not picks:
        st.info(f"No {title} picks in this run.")
        return

    df = pd.DataFrame(picks)

    # Select columns that exist
    display_cols = [c for c in [
        "symbol", "quality_score", "consensus_score", "recommendation",
        "sector", "current_price", "buy_price", "stop_loss", "take_profit",
        "risk_reward_ratio", "earnings_risk", "mfi_signal"
    ] if c in df.columns]

    st.dataframe(
        df[display_cols].style.format({
            "quality_score": "{:.1f}",
            "consensus_score": "{:.1f}",
            "current_price": "${:.2f}",
            "buy_price": "${:.2f}",
            "stop_loss": "${:.2f}",
            "take_profit": "${:.2f}",
            "risk_reward_ratio": "{:.1f}",
        }, na_rep="—"),
        use_container_width=True,
        hide_index=True,
    )


# ─── Main App ────────────────────────────────────────────────────────────────

def main():
    # Record visit (once per session)
    init_visitors_db()
    if "visit_recorded" not in st.session_state:
        record_visit()
        st.session_state["visit_recorded"] = True

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:10px 0 20px;">
        <h1 style="margin:0;">📊 SmartTrade AI — Ultimate Strategy</h1>
        <p style="color:#888; font-size:1.1em; margin-top:4px;">
        AI-powered 5-perspective consensus stock analysis · Updated twice weekly
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("📅 Past Reports")
        all_runs = load_all_runs()
        if not all_runs:
            st.info("No analysis runs found yet. The first scheduled run will populate results.")
            selected_run = None
        else:
            run_options = {f"{r['date']} — {r['signal']}": r['file'] for r in all_runs}
            selected_label = st.selectbox("Select a run:", list(run_options.keys()))
            selected_run = run_options.get(selected_label)

        st.divider()
        st.caption("Analysis runs automatically on **Tuesday & Thursday** at **10:30 AM ET** (30 min after market open).")
        st.caption("Built with ❤️ by SmartTrade AI")

    # ── Load data ─────────────────────────────────────────────────────────
    if selected_run:
        data = load_run_data(selected_run)
    else:
        data, _ = load_latest_results()

    if not data:
        st.warning("⏳ No analysis results available yet. The first scheduled run will generate results automatically.")
        st.info("The Ultimate Strategy analysis runs **twice a week** (Tuesday & Thursday at 10:30 AM ET).")
        _render_visitor_section()
        return

    # ── Market Overview ───────────────────────────────────────────────────
    timing = data.get("market_timing", {})
    tradability = data.get("ai_tradability", {})

    signal_badge(
        timing.get("signal", "N/A"),
        timing.get("action", "N/A"),
        timing.get("confidence", 0),
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Run Date", data.get("run_date", "N/A"))
    with col2:
        st.metric("📈 VIX Level", f"{timing.get('vix_level', 'N/A')}")
    with col3:
        st.metric("🔢 Stocks Analyzed", f"{data.get('total_analyzed', 0)}")
    with col4:
        st.metric("✅ Consensus Picks", f"{data.get('consensus_count', 0)}")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("🏆 5/5 Agreement", f"{data.get('tier_5_count', 0)}")
    with col6:
        st.metric("💪 4/5 Agreement", f"{data.get('tier_4_count', 0)}")
    with col7:
        st.metric("📊 3/5 Agreement", f"{data.get('tier_3_count', 0)}")
    with col8:
        regime = timing.get("market_regime", "N/A")
        st.metric("🌍 Regime", regime.upper() if isinstance(regime, str) else "N/A")

    # ── AI Insights ───────────────────────────────────────────────────────
    st.divider()

    with st.expander("🧠 AI Market Analysis & Reasoning", expanded=False):
        ai_col1, ai_col2 = st.columns(2)
        with ai_col1:
            st.markdown(f"**AI Trade Recommendation:** {tradability.get('recommendation', 'N/A')}")
            st.markdown(f"**AI Confidence:** {tradability.get('confidence', 0)}%")
            st.markdown(f"**Summary:** {tradability.get('summary', 'N/A')}")
        with ai_col2:
            st.markdown(f"**Position Sizing:** {timing.get('position_sizing', 'N/A')}")
            st.markdown(f"**Reason:** {timing.get('reason', 'N/A')}")

        trace = data.get("ai_reasoning_trace", "")
        if trace:
            st.markdown("---")
            st.markdown(f"**AI Reasoning Trace:** {trace}")
        insight = data.get("ai_key_insight", "")
        if insight:
            st.markdown(f"**Key Insight:** {insight}")

    # ── AI Top Picks ──────────────────────────────────────────────────────
    ai_picks = data.get("ai_top_picks", [])
    if ai_picks:
        st.subheader("🎯 AI Top Picks")
        for p in ai_picks:
            rank = p.get("rank", "?")
            symbol = p.get("symbol", "?")
            action = p.get("action", "N/A")
            macro_fit = p.get("macro_fit", "N/A")
            why = p.get("why_selected", "")
            size = p.get("position_size", "N/A")

            color = "#00c853" if "BUY" in str(action).upper() else "#ffd600" if "HOLD" in str(action).upper() else "#ff6d00"
            st.markdown(
                f"""<div style="background:#1e1e2f; border-left:4px solid {color};
                padding:12px 16px; margin-bottom:8px; border-radius:6px;">
                <strong>#{rank} {symbol}</strong> — <span style="color:{color};">{action}</span>
                · Macro Fit: {macro_fit} · Size: {size}<br/>
                <span style="color:#aaa;">{why}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    # ── Consensus Picks ───────────────────────────────────────────────────
    st.divider()

    tab5, tab4, tab3 = st.tabs(["🏆 5/5 Ultimate Buy", "💪 4/5 Strong Buy", "📊 3/5 Buy"])

    with tab5:
        render_picks_table(data.get("tier_5_picks", []), "5/5 Agreement")

    with tab4:
        render_picks_table(data.get("tier_4_picks", []), "4/5 Agreement")

    with tab3:
        render_picks_table(data.get("tier_3_picks", []), "3/5 Agreement")

    # ── Download Excel ────────────────────────────────────────────────────
    st.divider()
    excel_name = data.get("excel_file", "")
    if excel_name:
        excel_path = RESULTS_DIR / excel_name
        if excel_path.exists():
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📥 Download Full Excel Report",
                    data=f.read(),
                    file_name=excel_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        else:
            st.caption("Excel report not available for this run.")
    else:
        st.caption("No Excel report for this run.")

    # ── Past Reports Quick Access ─────────────────────────────────────────
    st.divider()
    st.subheader("📁 All Past Reports")

    all_runs = load_all_runs()
    if all_runs:
        runs_df = pd.DataFrame(all_runs)
        display_runs = runs_df[["date", "signal", "total_analyzed", "consensus_count", "tier_5", "tier_4"]].copy()
        display_runs.columns = ["Date", "Signal", "Analyzed", "Consensus", "5/5", "4/5"]
        st.dataframe(display_runs, use_container_width=True, hide_index=True)

        # Download links for past Excel reports
        for run in all_runs:
            if run.get("excel"):
                ep = RESULTS_DIR / run["excel"]
                if ep.exists():
                    with open(ep, "rb") as f:
                        st.download_button(
                            label=f"📥 {run['date']} Report",
                            data=f.read(),
                            file_name=run["excel"],
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{run['file']}",
                        )

    # ── Visitor Section ───────────────────────────────────────────────────
    _render_visitor_section()


def _render_visitor_section():
    """Render visitor counter and IP/time log at the bottom."""
    st.divider()
    st.subheader("👥 Visitor Log")

    total_count, recent_visitors = get_visitor_stats()

    st.metric("Total Visits", f"{total_count:,}")

    if recent_visitors:
        visitor_data = []
        for ip, vtime in recent_visitors:
            # Mask last octet for privacy
            parts = ip.split(".") if ip else []
            masked_ip = ".".join(parts[:3] + ["***"]) if len(parts) == 4 else ip
            visitor_data.append({"IP Address": masked_ip, "Visit Time": vtime})

        vdf = pd.DataFrame(visitor_data)
        st.dataframe(vdf, use_container_width=True, hide_index=True, height=300)
    else:
        st.info("No visitor data yet.")

    st.caption("IP addresses are partially masked for privacy. Times shown in UTC.")


if __name__ == "__main__":
    main()
