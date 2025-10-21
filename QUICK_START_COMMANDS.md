# 🚀 Quick Start Commands - SmartTrade AI

## ✅ System Status
- **Stock Universe**: 540 symbols ✅
- **Data Sources**: Yahoo Finance (FREE) ✅
- **All Components**: Validated ✅
- **Bugs Fixed**: Timestamps & Consensus Count ✅

---

## 🎯 **RUN THE APP**

### **1. Manual Run (Interactive UI)**
```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
streamlit run professional_trading_app.py
```
- Opens browser at `http://localhost:8501`
- Click "Run Ultimate Strategy"
- Analyzes 540 stocks
- Duration: 15-30 minutes
- Results saved to `exports/`

---

### **2. Automated Daily 6 AM Runs**
```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
python3 automated_daily_scheduler.py
```
- Runs at 6:00 AM Eastern Time
- Mon-Fri only (skips weekends/holidays)
- Results saved to `daily_results/`
- Auto-pushes to GitHub

---

### **3. Background Automation (Keeps Running)**
```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
nohup python3 automated_daily_scheduler.py > scheduler.out 2>&1 &
```
- Runs in background
- Survives terminal close
- Check status: `ps aux | grep automated_daily_scheduler`
- Stop: `kill <PID>`

---

## 🔍 **MONITORING**

### Check Logs
```bash
# Real-time monitoring
tail -f automated_scheduler.log

# Last 50 lines
tail -50 automated_scheduler.log

# Check for errors
grep ERROR automated_scheduler.log
```

### Check Results
```bash
# List recent Excel files
ls -lht exports/ | head -5
ls -lht daily_results/ | head -5

# Open latest result
open exports/Ultimate_Strategy_Results_*.xlsx
```

### Check if Scheduler is Running
```bash
ps aux | grep automated_daily_scheduler
```

---

## ✅ **VALIDATION**

### Run System Check
```bash
python3 COMPREHENSIVE_VALIDATION.py
```

**Expected:**
```
✅ Python 3.12.5
✅ All packages installed
✅ Stock universe: 540 symbols
✅ All core files present
✅ Yahoo Finance working
✅ Directories ready
✅ Git configured
✅ Streamlit working
✅ All modules import successfully

✅ ALL VALIDATIONS PASSED!
```

---

## 🛠️ **TROUBLESHOOTING**

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Update Git Config
```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

### Check Stock Universe
```bash
python3 -c "from questrade_valid_universe import get_questrade_valid_universe; print(f'Stocks: {len(set(get_questrade_valid_universe()))}')"
```

### Test Data Source
```bash
python3 -c "import yfinance as yf; ticker = yf.Ticker('AAPL'); print(ticker.history(period='1d'))"
```

---

## 📊 **WHAT YOU GET**

### Excel File Contains:
1. **Summary Sheet**: Start/end times, stock counts, recommendations
2. **All Consensus Picks**: All stocks with 2+ strategy agreement
3. **Tier 1 (4/4)**: Strongest recommendations
4. **Tier 2 (3/4)**: Strong recommendations
5. **Tier 3 (2/4)**: Moderate recommendations

### Example Output:
```
Analysis Start Time:       20251019 060000
Analysis End Time:         20251019 062530
Total Stocks Analyzed:     540
Stocks with 4/4 Agreement: 2
Total Consensus Picks:     2
```

---

## 🎯 **ONE-LINER COMMANDS**

```bash
# Validate system
python3 COMPREHENSIVE_VALIDATION.py

# Run manual analysis
streamlit run professional_trading_app.py

# Start 6 AM automation
python3 automated_daily_scheduler.py

# Background automation
nohup python3 automated_daily_scheduler.py > scheduler.out 2>&1 &

# Check logs
tail -f automated_scheduler.log

# List results
ls -lht exports/ | head -5

# Check if running
ps aux | grep automated_daily_scheduler

# Stop scheduler
kill $(ps aux | grep automated_daily_scheduler | grep -v grep | awk '{print $2}')
```

---

## 📅 **AUTOMATION SCHEDULE**

- **Time**: 6:00 AM Eastern Time
- **Days**: Monday - Friday
- **Skips**: Weekends and US market holidays
- **Duration**: 15-30 minutes per run
- **Output**: Excel file + GitHub push

---

## ✅ **READY TO GO!**

Your command:
```bash
streamlit run professional_trading_app.py
```

**Happy Trading! 📈💰**
