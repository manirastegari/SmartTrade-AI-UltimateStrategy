#!/usr/bin/env python3
"""
Scheduled Runner for SmartTrade AI Ultimate Strategy.
Runs the full analysis headlessly, saves results as JSON + Excel,
and commits them to the repo for the viewer app.
Designed to be triggered by GitHub Actions on a cron schedule.
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

RESULTS_DIR = REPO_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

def run_analysis():
    """Run the full Ultimate Strategy analysis and save results."""
    print(f"\n{'='*80}")
    print(f"🚀 SMARTTRADE AI - SCHEDULED ANALYSIS RUN")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*80}\n")

    start_time = time.time()

    # ── imports ──────────────────────────────────────────────────────────
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")

    from advanced_analyzer import AdvancedTradingAnalyzer
    from ultimate_strategy_analyzer_fixed import FixedUltimateStrategyAnalyzer
    from cleaned_high_potential_universe import get_cleaned_high_potential_universe

    # ── initialize ──────────────────────────────────────────────────────
    print("🔧 Initializing analyzers...")
    analyzer = AdvancedTradingAnalyzer(enable_training=False, data_mode="light")
    analyzer.stock_universe = get_cleaned_high_potential_universe()
    ultimate = FixedUltimateStrategyAnalyzer(analyzer)

    # ── run ──────────────────────────────────────────────────────────────
    print("📊 Running Ultimate Strategy analysis...")
    results = ultimate.run_ultimate_strategy()

    elapsed = round((time.time() - start_time) / 60, 1)
    print(f"\n✅ Analysis complete in {elapsed} minutes")

    # ── save results ────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_date = datetime.now().strftime("%Y-%m-%d")

    # 1) Save JSON summary (lightweight, for the viewer app)
    summary = build_summary(results, run_date, elapsed)
    json_path = RESULTS_DIR / f"run_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"📄 Saved JSON summary: {json_path.name}")

    # 2) Move Excel report into results/ if one was generated
    xlsx_files = sorted(REPO_ROOT.glob("SmartTrade_Premium_Analysis_*.xlsx"), key=os.path.getmtime)
    if xlsx_files:
        latest_xlsx = xlsx_files[-1]
        dest = RESULTS_DIR / f"report_{timestamp}.xlsx"
        shutil.move(str(latest_xlsx), str(dest))
        summary['excel_file'] = dest.name
        # Re-save JSON with excel filename
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"📊 Saved Excel report: {dest.name}")

    # 3) Update latest pointer
    latest_path = RESULTS_DIR / "latest.json"
    with open(latest_path, "w") as f:
        json.dump({"run_id": timestamp, "json_file": json_path.name, "excel_file": summary.get("excel_file", ""), "date": run_date}, f, indent=2)
    print(f"📌 Updated latest pointer")

    # 4) Prune old results (keep last 20 runs)
    prune_old_results(max_keep=20)

    print(f"\n🏁 Scheduled run complete. Results in: {RESULTS_DIR}")
    return summary


def build_summary(results: dict, run_date: str, elapsed_minutes: float) -> dict:
    """Extract a JSON-serializable summary from the full results dict."""
    consensus = results.get("consensus_recommendations", [])
    market = results.get("market_analysis", {})
    timing = market.get("timing_signal", {})
    tradability = results.get("market_tradability", {})
    ai_top = results.get("ai_top_picks", {})

    # Build tier lists
    tier_5 = [p for p in consensus if p.get("strategies_agreeing") == 5]
    tier_4 = [p for p in consensus if p.get("strategies_agreeing") == 4]
    tier_3 = [p for p in consensus if p.get("strategies_agreeing") == 3]

    def pick_summary(pick):
        return {
            "symbol": pick.get("symbol"),
            "quality_score": pick.get("quality_score"),
            "consensus_score": pick.get("consensus_score"),
            "recommendation": pick.get("recommendation"),
            "sector": pick.get("sector", "Unknown"),
            "current_price": pick.get("current_price"),
            "strategies_agreeing": pick.get("strategies_agreeing"),
            "buy_price": pick.get("buy_price"),
            "stop_loss": pick.get("stop_loss"),
            "take_profit": pick.get("take_profit"),
            "risk_reward_ratio": pick.get("risk_reward_ratio"),
            "earnings_risk": pick.get("earnings_risk"),
            "earnings_date": pick.get("earnings_date"),
            "mfi": pick.get("mfi"),
            "mfi_signal": pick.get("mfi_signal"),
        }

    ai_picks_list = []
    if ai_top and ai_top.get("ai_top_picks"):
        for p in ai_top["ai_top_picks"][:10]:
            ai_picks_list.append({
                "rank": p.get("rank"),
                "symbol": p.get("symbol"),
                "action": p.get("action"),
                "macro_fit": p.get("macro_fit"),
                "why_selected": p.get("why_selected"),
                "position_size": p.get("position_size"),
            })

    return {
        "run_date": run_date,
        "run_timestamp": datetime.now().isoformat(),
        "elapsed_minutes": elapsed_minutes,
        "total_analyzed": results.get("total_stocks_analyzed", 0),
        "consensus_count": results.get("consensus_picks_count", 0),
        "tier_5_count": len(tier_5),
        "tier_4_count": len(tier_4),
        "tier_3_count": len(tier_3),
        "market_timing": {
            "signal": timing.get("signal", "N/A"),
            "action": timing.get("action", "N/A"),
            "confidence": timing.get("confidence", 0),
            "position_sizing": timing.get("position_sizing", "N/A"),
            "vix_level": timing.get("vix_level"),
            "market_regime": timing.get("market_regime", "N/A"),
            "reason": timing.get("brief_reason", ""),
        },
        "ai_tradability": {
            "recommendation": tradability.get("trade_recommendation", "N/A") if tradability else "N/A",
            "confidence": tradability.get("confidence", 0) if tradability else 0,
            "summary": tradability.get("brief_summary", "") if tradability else "",
        },
        "ai_top_picks": ai_picks_list,
        "ai_key_insight": ai_top.get("key_insight", "") if ai_top else "",
        "ai_reasoning_trace": ai_top.get("reasoning_trace", "") if ai_top else "",
        "tier_5_picks": [pick_summary(p) for p in tier_5[:30]],
        "tier_4_picks": [pick_summary(p) for p in tier_4[:30]],
        "tier_3_picks": [pick_summary(p) for p in tier_3[:20]],
        "excel_file": "",  # filled in later
    }


def prune_old_results(max_keep: int = 20):
    """Remove oldest run files, keeping only the most recent N runs."""
    json_files = sorted(RESULTS_DIR.glob("run_*.json"), key=os.path.getmtime)
    xlsx_files = sorted(RESULTS_DIR.glob("report_*.xlsx"), key=os.path.getmtime)

    for flist in (json_files, xlsx_files):
        while len(flist) > max_keep:
            old = flist.pop(0)
            old.unlink(missing_ok=True)
            print(f"🗑️ Pruned old result: {old.name}")


if __name__ == "__main__":
    run_analysis()
