# ⚡ Quick Start - Automated Daily Scheduler

## 🚀 Setup in 3 Commands

```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
pip3 install -r requirements.txt
./setup_scheduler.sh
```

**Done!** The scheduler is now running and will execute at 6am ET every weekday.

---

## 📊 What You Get

- **Daily Analysis**: Runs automatically at 6:00 AM Eastern Time
- **Smart Scheduling**: Skips weekends and market holidays
- **Excel Reports**: Professional reports with timestamps in `daily_results/`
- **GitHub Backup**: Automatic commits and pushes
- **Full Logging**: Complete activity tracking

---

## 🔍 Quick Commands

### Check Status
```bash
launchctl list | grep smarttrade
```

### View Live Log
```bash
tail -f automated_scheduler.log
```

### See Results
```bash
ls -lh daily_results/
```

### Stop Scheduler
```bash
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

### Start Scheduler
```bash
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

---

## 📅 Schedule

- **Time**: 6:00 AM Eastern Time
- **Days**: Monday - Friday
- **Skips**: Weekends + US market holidays

---

## 📁 Output Files

```
daily_results/
└── UltimateStrategy_Daily_YYYYMMDD_HHMMSS.xlsx
    ├── Analysis_Info (with start/end timestamps)
    ├── Consensus_Recommendations
    ├── Market_Analysis
    ├── Sector_Analysis
    └── Strategy_Summary
```

---

## 🔧 Troubleshooting

**Scheduler not running?**
```bash
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

**Git push fails?**
```bash
git config --list | grep user
ssh -T git@github.com
```

**Check logs for errors:**
```bash
tail -50 scheduler_stderr.log
```

---

## 📖 Full Documentation

- **Setup Guide**: `AUTOMATED_SCHEDULER_SETUP.md`
- **README**: `AUTOMATED_SCHEDULER_README.md`

---

**That's it! Your Ultimate Strategy now runs automatically every weekday at 6am! 🎉**
