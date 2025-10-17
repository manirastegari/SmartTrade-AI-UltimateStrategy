# 🤖 Automated Daily Ultimate Strategy Scheduler

## 🎯 Overview

This automated scheduler runs the **Ultimate Strategy** analysis every weekday at **6:00 AM Eastern Time**, exports results to Excel with detailed timestamps, and automatically pushes to GitHub.

### ✨ Key Features

- ✅ **Automatic Daily Execution** - Runs at 6am ET every weekday
- ✅ **Smart Market Detection** - Skips weekends and US market holidays
- ✅ **Complete Analysis** - Runs all 4 strategies (2-3 hours)
- ✅ **Excel Reports** - Professional reports with start/end timestamps
- ✅ **GitHub Integration** - Auto-commits and pushes results
- ✅ **Comprehensive Logging** - Full activity tracking
- ✅ **100% Free** - Uses only free APIs and resources
- ✅ **Real Data** - No fake/simulated data, all real-time

---

## 🚀 Quick Setup (3 Minutes)

### One-Command Setup

```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
./setup_scheduler.sh
```

This will:
1. ✅ Check Python and Git
2. ✅ Install dependencies
3. ✅ Create results directory
4. ✅ Configure launchd service
5. ✅ Start the scheduler

### Manual Setup

If you prefer manual setup:

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Copy plist to LaunchAgents
cp com.smarttrade.scheduler.plist ~/Library/LaunchAgents/

# 3. Load the service
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

---

## 📊 How It Works

### Daily Workflow

```
6:00 AM ET → Market Check → Ultimate Strategy → Excel Export → GitHub Push
   ↓              ↓                ↓                  ↓              ↓
Schedule      Weekday?      4 Strategies      Timestamps      Auto-commit
             No Holiday?    (2-3 hours)       + Details       + Push
```

### What Gets Analyzed

1. **Strategy 1**: Institutional Consensus (716 stocks)
2. **Strategy 2**: Hedge Fund Alpha (500 stocks)
3. **Strategy 3**: Quant Value Hunter (500 stocks)
4. **Strategy 4**: Risk-Managed Core (300 stocks)

**Total**: ~2000 stock analyses → Consensus recommendations

### Excel Report Contents

Each daily report includes:

| Sheet | Description |
|-------|-------------|
| **Analysis_Info** | Start time, end time, duration, summary stats |
| **Consensus_Recommendations** | Final buy/sell recommendations |
| **Market_Analysis** | Overall market conditions (bullish/bearish/neutral) |
| **Sector_Analysis** | Sector performance breakdown |
| **Strategy_Summary** | Results from all 4 individual strategies |

### Example Report Name

```
UltimateStrategy_Daily_20241016_060000.xlsx
```

Format: `UltimateStrategy_Daily_YYYYMMDD_HHMMSS.xlsx`

---

## 📅 Schedule Details

### When It Runs

- **Time**: 6:00 AM Eastern Time (ET)
- **Days**: Monday - Friday only
- **Excludes**: Weekends (Sat-Sun) and US market holidays

### Market Holidays Detected

The scheduler automatically skips:

- New Year's Day
- Martin Luther King Jr. Day
- Presidents' Day
- Good Friday
- Memorial Day
- Juneteenth
- Independence Day
- Labor Day
- Thanksgiving
- Christmas

---

## 🔍 Monitoring & Management

### Check Status

```bash
# Is the scheduler running?
launchctl list | grep smarttrade

# View live activity log
tail -f automated_scheduler.log

# View stdout/stderr
tail -f scheduler_stdout.log
tail -f scheduler_stderr.log
```

### View Results

```bash
# List all daily reports
ls -lh daily_results/

# Open latest report
open daily_results/$(ls -t daily_results/ | head -1)

# Count total reports
ls daily_results/ | wc -l
```

### Check GitHub

```bash
# View recent commits
git log --oneline -10

# Or visit GitHub
open https://github.com/yourusername/SmartTrade-AI-UltimateStrategy/commits/main
```

### Stop/Start Service

```bash
# Stop the scheduler
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist

# Start the scheduler
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist

# Restart (stop + start)
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

---

## 🛠️ Configuration

### Change Schedule Time

Edit `automated_daily_scheduler.py`:

```python
# Line ~380: Change from 6am to 8am
schedule.every().day.at("08:00").do(self.daily_job)
```

Then restart the service:

```bash
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

### Change Results Directory

Edit `automated_daily_scheduler.py`:

```python
# Line ~43: Change directory name
self.results_dir = self.project_path / "my_custom_results"
```

### Disable GitHub Push

Edit `automated_daily_scheduler.py`:

```python
# Line ~365: Comment out the push
# success = self.push_to_github(excel_file)
```

---

## 🔐 GitHub Authentication

### Option 1: SSH Key (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "mani.rastegari@gmail.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

### Option 2: Personal Access Token

```bash
# 1. Create token at: https://github.com/settings/tokens
# 2. Select scopes: repo (all)
# 3. Update remote URL:
git remote set-url origin https://YOUR_TOKEN@github.com/yourusername/SmartTrade-AI-UltimateStrategy.git
```

### Test Authentication

```bash
# For SSH
ssh -T git@github.com

# For HTTPS
git ls-remote origin
```

---

## 📈 Performance & Resources

### Analysis Duration

- **Total Time**: 2-3 hours
- **Strategy 1**: ~45 minutes (716 stocks)
- **Strategy 2**: ~40 minutes (500 stocks)
- **Strategy 3**: ~40 minutes (500 stocks)
- **Strategy 4**: ~30 minutes (300 stocks)

### System Resources

| Resource | Usage |
|----------|-------|
| **CPU** | High during analysis, idle otherwise |
| **Memory** | 2-4 GB during analysis |
| **Disk** | ~5-10 MB per report |
| **Network** | Minimal (data fetch + git push) |

### Monthly Storage

- **Reports**: ~30 files × 7 MB = ~210 MB/month
- **Logs**: ~50 MB/month
- **Total**: ~260 MB/month

---

## 🚨 Troubleshooting

### Issue: Scheduler not running

```bash
# Check if loaded
launchctl list | grep smarttrade

# Check logs for errors
tail -50 scheduler_stderr.log

# Reload service
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

### Issue: Git push fails

```bash
# Test git manually
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
git status
git push

# Check credentials
git config --list | grep user

# Verify remote
git remote -v
```

### Issue: Import errors

```bash
# Reinstall dependencies
pip3 install -r requirements.txt --upgrade

# Test imports
python3 -c "import schedule, pytz, pandas, openpyxl; print('OK')"
```

### Issue: Python path wrong

```bash
# Find correct Python path
which python3

# Update plist file
nano ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
# Change <string>/usr/local/bin/python3</string> to your path
```

### Issue: No results generated

```bash
# Check if market is open
python3 -c "from automated_daily_scheduler import AutomatedUltimateStrategyScheduler; s = AutomatedUltimateStrategyScheduler(); print(s.is_market_open_day())"

# Run manually to see errors
python3 automated_daily_scheduler.py
```

---

## 📋 File Structure

```
SmartTrade-AI-UltimateStrategy/
│
├── automated_daily_scheduler.py          # Main scheduler script
├── setup_scheduler.sh                    # One-command setup script
├── com.smarttrade.scheduler.plist        # launchd configuration
│
├── automated_scheduler.log               # Activity log
├── scheduler_stdout.log                  # Standard output
├── scheduler_stderr.log                  # Error output
│
├── daily_results/                        # Excel reports directory
│   ├── UltimateStrategy_Daily_20241016_060000.xlsx
│   ├── UltimateStrategy_Daily_20241017_060000.xlsx
│   └── ...
│
└── AUTOMATED_SCHEDULER_SETUP.md          # Detailed setup guide
```

---

## 🎯 Usage Examples

### Run Immediately (Test)

```bash
# Temporarily change schedule to run in 1 minute
python3 -c "
from automated_daily_scheduler import AutomatedUltimateStrategyScheduler
import schedule
import time

scheduler = AutomatedUltimateStrategyScheduler()
schedule.every(1).minutes.do(scheduler.daily_job)

print('Running in 1 minute...')
while True:
    schedule.run_pending()
    time.sleep(1)
"
```

### Manual One-Time Run

```bash
python3 -c "
from automated_daily_scheduler import AutomatedUltimateStrategyScheduler

scheduler = AutomatedUltimateStrategyScheduler()
scheduler.daily_job()
"
```

### Check Next Run Time

```bash
python3 -c "
import schedule
schedule.every().day.at('06:00').do(lambda: None)
print(f'Next run: {schedule.next_run()}')
"
```

---

## 📊 Expected Output

### Console Output

```
================================================================================
AUTOMATED ULTIMATE STRATEGY SCHEDULER STARTED
================================================================================
Schedule: Daily at 6:00 AM Eastern Time (Mon-Fri only)
Project Path: /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
Results Directory: /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy/daily_results
================================================================================
Scheduler is running. Press Ctrl+C to stop.
Next run scheduled for: 2024-10-17 06:00:00
```

### Daily Job Output

```
================================================================================
DAILY JOB TRIGGERED
================================================================================
Today is Monday - Market is open
================================================================================
Starting Ultimate Strategy Analysis at 2024-10-16 06:00:00 EDT
================================================================================
Initializing analyzers...
Running Ultimate Strategy (this will take 2-3 hours)...
[5%] Analyzing overall market conditions...
[10%] Analyzing sector and industry trends...
[20%] Running Strategy 1: Institutional Consensus (300 stocks)...
[40%] Running Strategy 2: Hedge Fund Alpha (300 stocks)...
[60%] Running Strategy 3: Quant Value Hunter (300 stocks)...
[80%] Running Strategy 4: Risk-Managed Core (300 stocks)...
[90%] Generating market-aware recommendations...
[100%] Ultimate Strategy Analysis Complete!
================================================================================
Analysis completed at 2024-10-16 08:45:23 EDT
Total duration: 2:45:23
Total recommendations: 47
================================================================================
Exporting results to Excel: daily_results/UltimateStrategy_Daily_20241016_060000.xlsx
✅ Excel file created successfully
Pushing results to GitHub...
✅ Successfully pushed to GitHub
✅ Daily job completed successfully!
```

---

## 🔔 Notifications (Optional)

### macOS Notifications

Add to `automated_daily_scheduler.py`:

```python
import subprocess

def send_notification(title, message):
    subprocess.run([
        'osascript', '-e',
        f'display notification "{message}" with title "{title}"'
    ])

# In daily_job():
send_notification("SmartTrade AI", "Daily analysis started")
# ... after completion ...
send_notification("SmartTrade AI", "Daily analysis complete!")
```

### Email Notifications

Add to `automated_daily_scheduler.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your@email.com'
    msg['To'] = 'your@email.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your@email.com', 'your_app_password')
        server.send_message(msg)
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Scheduler service is loaded: `launchctl list | grep smarttrade`
- [ ] Python dependencies installed: `pip3 list | grep -E "schedule|pytz|pandas|openpyxl"`
- [ ] Git configured: `git config --list | grep user`
- [ ] GitHub authentication works: `git push` (test manually)
- [ ] Results directory exists: `ls -ld daily_results/`
- [ ] Logs are being written: `ls -lh automated_scheduler.log`
- [ ] Next run scheduled: Check `automated_scheduler.log`

---

## 📞 Support

**Created by: Mani Rastegari**  
**Email: mani.rastegari@gmail.com**

For issues:
1. Check `automated_scheduler.log` for errors
2. Verify all dependencies are installed
3. Test Git push manually
4. Ensure market is open (weekday, not holiday)
5. Review this documentation

---

## 📝 Notes

- **Timezone**: All times are in Eastern Time (ET)
- **Free APIs**: Uses only Yahoo Finance (no rate limits)
- **Real Data**: 100% real-time market data, no simulations
- **Timestamps**: All reports include start/end times
- **GitHub**: Automatic commits with descriptive messages
- **Reliability**: Handles network errors and retries automatically

---

## 🎉 Success!

Your SmartTrade AI Ultimate Strategy is now fully automated!

Every weekday at 6am, you'll get:
- ✅ Complete 4-strategy analysis
- ✅ Professional Excel report with timestamps
- ✅ Automatic GitHub backup
- ✅ Comprehensive activity logs

**Set it and forget it! 🚀📈💎**

---

*Last Updated: October 2024*  
*Version: 1.0*
