#!/usr/bin/env python3
"""
SmartTrade AI — Public Results Dashboard
Deployed on Streamlit Cloud. Automatically displays pre-computed
analysis results, past reports, and tracks visitors.
No user interaction required — everything is read-only.
Analysis runs automatically via GitHub Actions (Tue/Thu 10:30 AM ET).
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import sqlite3

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartTrade AI — Ultimate Strategy Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

RESULTS_DIR = Path(__file__).resolve().parent / "results"
VISITORS_DB = Path(__file__).resolve().parent / "visitors.db"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stMetric { background: #1e1e2f; padding: 12px; border-radius: 10px; }
    .stMetric label { font-size: 0.85em !important; }
    .signal-banner {
        padding: 20px 30px; border-radius: 14px; text-align: center;
        margin-bottom: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .signal-banner h2 { margin: 0; color: #fff; font-size: 1.8em; }
    .signal-banner p { margin: 6px 0 0; color: rgba(255,255,255,0.85); font-size: 1.05em; }
    .pick-card {
        background: #1e1e2f; border-left: 4px solid; padding: 14px 18px;
        margin-bottom: 10px; border-radius: 8px;
    }
    .pick-card strong { font-size: 1.05em; }
    .pick-card .why { color: #aaa; margin-top: 4px; }
    .report-row {
        background: #1a1a2e; padding: 10px 16px; border-radius: 8px;
        margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
    }
    .footer-section {
        background: #111122; padding: 20px; border-radius: 12px;
        margin-top: 20px;
    }
    .schedule-note {
        background: #1a2e1a; border: 1px solid #2d5a2d; padding: 12px 18px;
        border-radius: 8px; color: #8fbc8f; text-align: center; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

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
        pass


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
def load_all_runs():
    """Load metadata for all past runs, newest first."""
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
                "data": d,
            })
        except Exception:
            continue
    return runs


# ─── UI Components ────────────────────────────────────────────────────────────

SIGNAL_COLORS = {
    "STRONG_BUY": "#00c853", "BUY": "#00c853",
    "CAUTIOUS_BUY": "#ffd600", "BUY WITH CAUTION": "#ffd600",
    "WAIT": "#ff9100", "HOLD": "#ff6d00",
    "TAKE_PROFITS": "#d50000", "CRISIS": "#b71c1c",
}


def render_signal_banner(signal, action, confidence):
    color = SIGNAL_COLORS.get(signal, SIGNAL_COLORS.get(action, "#9e9e9e"))
    st.markdown(
        f"""<div class="signal-banner" style="background:linear-gradient(135deg, {color}, {color}aa);">
        <h2>{action}</h2>
        <p>Signal: {signal} · Confidence: {confidence}%</p>
        </div>""",
        unsafe_allow_html=True,
    )


def render_picks_table(picks):
    if not picks:
        st.caption("No picks in this tier for this run.")
        return

    df = pd.DataFrame(picks)
    cols = [c for c in [
        "symbol", "quality_score", "consensus_score", "recommendation",
        "sector", "current_price", "buy_price", "stop_loss", "take_profit",
        "risk_reward_ratio", "earnings_risk", "mfi_signal"
    ] if c in df.columns]

    fmt = {}
    for c in cols:
        if c in ("quality_score", "consensus_score", "risk_reward_ratio"):
            fmt[c] = "{:.1f}"
        elif c in ("current_price", "buy_price", "stop_loss", "take_profit"):
            fmt[c] = "${:.2f}"

    st.dataframe(
        df[cols].style.format(fmt, na_rep="—"),
        use_container_width=True, hide_index=True,
    )


# ─── Main Dashboard ──────────────────────────────────────────────────────────

def main():
    # Track visit (once per session)
    init_visitors_db()
    if "visit_recorded" not in st.session_state:
        record_visit()
        st.session_state["visit_recorded"] = True

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:8px 0 16px;">
        <h1 style="margin:0;">📊 SmartTrade AI — Ultimate Strategy</h1>
        <p style="color:#888; font-size:1.05em; margin:4px 0 0;">
        AI-powered 5-strategy consensus stock analysis · Fully automated · Updated every Tue & Thu
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="schedule-note">🕐 Analysis runs <strong>automatically</strong> every '
        '<strong>Tuesday & Thursday at 10:30 AM ET</strong> (30 min after market open)</div>',
        unsafe_allow_html=True,
    )

    # ── Load all runs ─────────────────────────────────────────────────────
    all_runs = load_all_runs()
    if not all_runs:
        st.warning("⏳ No analysis results yet. The first automated run will populate this dashboard.")
        _render_visitor_footer()
        return

    # Show latest run by default
    data = all_runs[0]["data"]

    # ── Market Signal Banner ──────────────────────────────────────────────
    timing = data.get("market_timing", {})
    tradability = data.get("ai_tradability", {})

    render_signal_banner(
        timing.get("signal", "N/A"),
        timing.get("action", "N/A"),
        timing.get("confidence", 0),
    )

    # ── Key Metrics Row ───────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📅 Run Date", data.get("run_date", "N/A"))
    c2.metric("📈 VIX", f"{timing.get('vix_level', 'N/A')}")
    c3.metric("🔢 Analyzed", f"{data.get('total_analyzed', 0):,}")
    c4.metric("🏆 5/5 Picks", data.get("tier_5_count", 0))
    c5.metric("💪 4/5 Picks", data.get("tier_4_count", 0))
    c6.metric("📊 3/5 Picks", data.get("tier_3_count", 0))

    # ── AI Insights ───────────────────────────────────────────────────────
    st.divider()
    col_ai1, col_ai2 = st.columns([2, 1])
    with col_ai1:
        st.markdown("### 🧠 AI Market Assessment")
        st.markdown(f"**Recommendation:** {tradability.get('recommendation', 'N/A')}")
        st.markdown(f"**Confidence:** {tradability.get('confidence', 0)}%")
        summary = tradability.get("summary", "")
        if summary:
            st.markdown(f"_{summary}_")
        insight = data.get("ai_key_insight", "")
        if insight:
            st.info(f"**Key Insight:** {insight}")
    with col_ai2:
        st.markdown("### ⚙️ Conditions")
        regime = timing.get("market_regime", "N/A")
        st.markdown(f"**Regime:** {regime.upper() if isinstance(regime, str) else 'N/A'}")
        st.markdown(f"**Position Sizing:** {timing.get('position_sizing', 'N/A')}")
        reason = timing.get("reason", "")
        if reason:
            st.caption(reason)

    # ── AI Top Picks ──────────────────────────────────────────────────────
    ai_picks = data.get("ai_top_picks", [])
    if ai_picks:
        st.divider()
        st.markdown("### 🎯 AI Top Picks")
        for p in ai_picks:
            action = p.get("action", "N/A")
            color = "#00c853" if "BUY" in str(action).upper() else "#ffd600" if "HOLD" in str(action).upper() else "#ff6d00"
            st.markdown(
                f"""<div class="pick-card" style="border-color:{color};">
                <strong>#{p.get('rank','?')} {p.get('symbol','?')}</strong>
                — <span style="color:{color};">{action}</span>
                · Macro Fit: {p.get('macro_fit','N/A')} · Size: {p.get('position_size','N/A')}
                <div class="why">{p.get('why_selected','')}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # ── Consensus Picks (tabs) ────────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Consensus Stock Picks")

    tab5, tab4, tab3 = st.tabs([
        f"🏆 5/5 Ultimate Buy ({data.get('tier_5_count', 0)})",
        f"💪 4/5 Strong Buy ({data.get('tier_4_count', 0)})",
        f"📊 3/5 Buy ({data.get('tier_3_count', 0)})",
    ])
    with tab5:
        render_picks_table(data.get("tier_5_picks", []))
    with tab4:
        render_picks_table(data.get("tier_4_picks", []))
    with tab3:
        render_picks_table(data.get("tier_3_picks", []))

    # ── Excel Download (current run) ──────────────────────────────────────
    excel_name = all_runs[0].get("excel", "")
    if excel_name:
        excel_path = RESULTS_DIR / excel_name
        if excel_path.exists():
            with open(excel_path, "rb") as ef:
                st.download_button(
                    "📥 Download Full Excel Report (Latest)",
                    data=ef.read(), file_name=excel_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    # ── Past Reports Archive ──────────────────────────────────────────────
    st.divider()
    st.markdown("### 📁 Past Analysis Reports")

    archive_data = []
    for run in all_runs:
        archive_data.append({
            "Date": run["date"],
            "Market Signal": run["signal"],
            "Stocks Analyzed": run["total_analyzed"],
            "Consensus Picks": run["consensus_count"],
            "5/5 Picks": run["tier_5"],
            "4/5 Picks": run["tier_4"],
        })
    st.dataframe(
        pd.DataFrame(archive_data),
        use_container_width=True, hide_index=True,
    )

    # Download buttons for each past report
    dl_cols = st.columns(min(len(all_runs), 4))
    for i, run in enumerate(all_runs):
        if run.get("excel"):
            ep = RESULTS_DIR / run["excel"]
            if ep.exists():
                with open(ep, "rb") as ef:
                    dl_cols[i % len(dl_cols)].download_button(
                        f"📥 {run['date']}",
                        data=ef.read(), file_name=run["excel"],
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{run['file']}",
                    )

    # ── Visitor Log Footer ────────────────────────────────────────────────
    _render_visitor_footer()


def _render_visitor_footer():
    """Visitor counter and IP/time log at the bottom of the page."""
    st.divider()

    total_count, recent_visitors = get_visitor_stats()

    st.markdown(
        f"""<div class="footer-section">
        <h3 style="margin-top:0;">👥 Visitor Log &nbsp;·&nbsp;
        <span style="color:#00c853;">{total_count:,} total visits</span></h3>
        </div>""",
        unsafe_allow_html=True,
    )

    if recent_visitors:
        visitor_data = []
        for ip, vtime in recent_visitors:
            parts = ip.split(".") if ip else []
            masked = ".".join(parts[:3] + ["***"]) if len(parts) == 4 else ip
            visitor_data.append({"IP Address": masked, "Visit Time (UTC)": vtime})

        st.dataframe(
            pd.DataFrame(visitor_data),
            use_container_width=True, hide_index=True, height=250,
        )
    else:
        st.caption("No visitor data recorded yet.")

    st.caption("IP addresses are partially masked for privacy · Times shown in UTC · Page auto-refreshes every 5 minutes")


if __name__ == "__main__":
    main()
