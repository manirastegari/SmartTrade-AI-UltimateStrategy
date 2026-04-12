#!/usr/bin/env python3
"""
One-time utility: seed the results/ directory with data from existing
Excel reports so the viewer has content on first deploy.
Run once locally, then delete this script or ignore it.
"""

import os, json, shutil
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent
RESULTS_DIR = REPO / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Find all SmartTrade_Premium_Analysis_*.xlsx in repo root
xlsx_files = sorted(REPO.glob("SmartTrade_Premium_Analysis_*.xlsx"), key=os.path.getmtime)

print(f"Found {len(xlsx_files)} Excel reports to seed.")

for xlsx in xlsx_files:
    # Parse timestamp from filename: SmartTrade_Premium_Analysis_YYYYMMDD_HHMMSS.xlsx
    parts = xlsx.stem.split("_")
    if len(parts) >= 5:
        date_str = parts[3]
        time_str = parts[4]
        timestamp = f"{date_str}_{time_str}"
        run_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    else:
        timestamp = xlsx.stem[-15:]
        run_date = "unknown"

    # Copy Excel to results/
    dest_xlsx = RESULTS_DIR / f"report_{timestamp}.xlsx"
    if not dest_xlsx.exists():
        shutil.copy2(str(xlsx), str(dest_xlsx))
        print(f"  Copied: {xlsx.name} -> {dest_xlsx.name}")

    # Create a minimal JSON stub
    json_path = RESULTS_DIR / f"run_{timestamp}.json"
    if not json_path.exists():
        stub = {
            "run_date": run_date,
            "run_timestamp": f"{run_date}T00:00:00",
            "elapsed_minutes": 0,
            "total_analyzed": 614,
            "consensus_count": 0,
            "tier_5_count": 0,
            "tier_4_count": 0,
            "tier_3_count": 0,
            "market_timing": {
                "signal": "N/A",
                "action": "N/A",
                "confidence": 0,
                "position_sizing": "N/A",
                "vix_level": None,
                "market_regime": "N/A",
                "reason": "Historical report — no JSON data available",
            },
            "ai_tradability": {"recommendation": "N/A", "confidence": 0, "summary": "Historical report"},
            "ai_top_picks": [],
            "ai_key_insight": "",
            "ai_reasoning_trace": "",
            "tier_5_picks": [],
            "tier_4_picks": [],
            "tier_3_picks": [],
            "excel_file": dest_xlsx.name,
        }
        with open(json_path, "w") as f:
            json.dump(stub, f, indent=2)
        print(f"  Created stub: {json_path.name}")

# Update latest.json to point to most recent
if xlsx_files:
    parts = xlsx_files[-1].stem.split("_")
    if len(parts) >= 5:
        timestamp = f"{parts[3]}_{parts[4]}"
        run_date = f"{parts[3][:4]}-{parts[3][4:6]}-{parts[3][6:8]}"
    else:
        timestamp = xlsx_files[-1].stem[-15:]
        run_date = "unknown"
    
    latest = {
        "run_id": timestamp,
        "json_file": f"run_{timestamp}.json",
        "excel_file": f"report_{timestamp}.xlsx",
        "date": run_date,
    }
    with open(RESULTS_DIR / "latest.json", "w") as f:
        json.dump(latest, f, indent=2)
    print(f"\nUpdated latest.json -> {timestamp}")

print("Done! Results seeded.")
