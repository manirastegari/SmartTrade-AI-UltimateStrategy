# 🤖 Automated Daily Scheduler Setup Guide

## Overview

The **Automated Daily Scheduler** runs the Ultimate Strategy analysis automatically every weekday at **6:00 AM Eastern Time**. It:

- ✅ Runs Monday-Friday only (skips weekends)
- ✅ Detects and skips US market holidays
- ✅ Exports results to Excel with start/end timestamps
- ✅ Automatically pushes results to GitHub
- ✅ Logs all activities for monitoring
- ✅ Uses only free APIs and resources

---

## 📋 Prerequisites

1. **Python 3.12+** installed
2. **Git** configured with GitHub credentials
3. **All dependencies** installed from `requirements.txt`
4. **GitHub repository** set up and accessible

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
pip3 install -r requirements.txt
```

### Step 2: Configure Git (if not already done)

```bash
# Set up Git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify GitHub access
git remote -v
```

### Step 3: Test the Scheduler Manually

```bash
# Run a test to ensure everything works
python3 automated_daily_scheduler.py
```

**Note:** The first run will schedule the job for 6am the next weekday. To test immediately, you can modify the schedule time temporarily.

---

## 🔧 macOS Setup (Recommended)

### Option 1: Using launchd (Runs on Boot)

Create a launchd plist file to run the scheduler automatically:

1. **Create the plist file:**

```bash
nano ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

2. **Paste this content:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.smarttrade.scheduler</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy/automated_daily_scheduler.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy</string>
    
    <key>StandardOutPath</key>
    <string>/Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy/scheduler_stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy/scheduler_stderr.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

3. **Load the service:**

```bash
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

4. **Verify it's running:**

```bash
launchctl list | grep smarttrade
```

5. **To stop the service:**

```bash
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

### Option 2: Using Terminal (Manual Start)

Simply run the scheduler in a terminal window:

```bash
cd /Users/manirastegari/maniProject/SmartTrade-AI-UltimateStrategy
python3 automated_daily_scheduler.py
```

**Keep the terminal window open** for the scheduler to continue running.

---

## 📊 How It Works

### Daily Workflow

1. **6:00 AM Eastern Time** - Scheduler wakes up
2. **Market Check** - Verifies it's a weekday and not a holiday
3. **Ultimate Strategy** - Runs 4-strategy consensus analysis (2-3 hours)
4. **Excel Export** - Creates detailed report with timestamps
5. **GitHub Push** - Commits and pushes results to repository
6. **Logging** - Records all activities in `automated_scheduler.log`

### File Structure

```
SmartTrade-AI-UltimateStrategy/
├── automated_daily_scheduler.py      # Main scheduler script
├── automated_scheduler.log           # Activity log
├── daily_results/                    # Excel reports directory
│   └── UltimateStrategy_Daily_YYYYMMDD_HHMMSS.xlsx
├── scheduler_stdout.log              # Standard output (launchd)
└── scheduler_stderr.log              # Error output (launchd)
```

### Excel Report Format

Each daily report includes:

- **Analysis_Info**: Start/end timestamps, duration, summary stats
- **Consensus_Recommendations**: Final buy/sell recommendations
- **Market_Analysis**: Overall market conditions
- **Sector_Analysis**: Sector performance breakdown
- **Strategy_Summary**: Results from all 4 strategies

---

## 🔍 Monitoring

### Check Logs

```bash
# View scheduler activity log
tail -f automated_scheduler.log

# View launchd output (if using launchd)
tail -f scheduler_stdout.log
tail -f scheduler_stderr.log
```

### Verify Daily Results

```bash
# List all daily reports
ls -lh daily_results/

# View latest report
open daily_results/$(ls -t daily_results/ | head -1)
```

### Check GitHub

Visit your GitHub repository to see the daily commits:
```
https://github.com/yourusername/SmartTrade-AI-UltimateStrategy/commits/main
```

---

## 🛠️ Troubleshooting

### Issue: Scheduler not running

**Solution:**
```bash
# Check if launchd service is loaded
launchctl list | grep smarttrade

# Reload the service
launchctl unload ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
launchctl load ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

### Issue: Git push fails

**Solution:**
```bash
# Verify Git credentials
git config --list

# Test GitHub connection
ssh -T git@github.com

# Or use HTTPS with personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/yourusername/SmartTrade-AI-UltimateStrategy.git
```

### Issue: Python not found

**Solution:**
```bash
# Find Python path
which python3

# Update plist file with correct path
nano ~/Library/LaunchAgents/com.smarttrade.scheduler.plist
```

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --upgrade

# Verify installation
python3 -c "import schedule, pytz, pandas; print('OK')"
```

---

## 📅 Market Holidays Detected

The scheduler automatically skips these US market holidays:

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

**Plus all weekends (Saturday & Sunday)**

---

## ⚙️ Configuration

### Change Schedule Time

Edit `automated_daily_scheduler.py`:

```python
# Change from 6am to 8am
schedule.every().day.at("08:00").do(self.daily_job)
```

### Change Results Directory

```python
# In __init__ method
self.results_dir = self.project_path / "custom_results_folder"
```

### Disable GitHub Push

Comment out the push in `daily_job()`:

```python
# success = self.push_to_github(excel_file)
```

---

## 🔐 Security Best Practices

### GitHub Authentication

**Option 1: SSH Key (Recommended)**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy and add to GitHub Settings > SSH Keys
```

**Option 2: Personal Access Token**
```bash
# Create token at: https://github.com/settings/tokens
# Use in remote URL
git remote set-url origin https://YOUR_TOKEN@github.com/yourusername/repo.git
```

### File Permissions

```bash
# Secure the plist file
chmod 644 ~/Library/LaunchAgents/com.smarttrade.scheduler.plist

# Secure log files
chmod 600 automated_scheduler.log
```

---

## 📈 Performance Notes

- **Analysis Duration**: 2-3 hours (4 strategies × 300-700 stocks each)
- **Excel File Size**: ~5-10 MB per report
- **Disk Space**: ~150-300 MB per month (30 reports)
- **Network Usage**: Minimal (only for data fetching and git push)
- **CPU Usage**: High during analysis, idle otherwise
- **Memory Usage**: ~2-4 GB during analysis

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Configure Git authentication
3. ✅ Test manual run
4. ✅ Set up launchd service
5. ✅ Monitor first automated run
6. ✅ Review daily results in GitHub

---

## 📞 Support

If you encounter issues:

1. Check `automated_scheduler.log` for errors
2. Verify all dependencies are installed
3. Test Git push manually
4. Ensure market is open (weekday, not holiday)

**Created by: Mani Rastegari**  
**Email: mani.rastegari@gmail.com**

---

## 📝 Notes

- The scheduler uses **Eastern Time (ET)** for all operations
- All analysis uses **free APIs only** (no rate limits)
- Results are **real-time data**, not fake/simulated
- Excel reports include **full timestamps** for tracking
- GitHub commits are **automatic** with descriptive messages

**Happy Automated Trading! 🚀📈💎**
