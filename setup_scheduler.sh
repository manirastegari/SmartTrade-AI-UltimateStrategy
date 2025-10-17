#!/bin/bash
# Setup script for SmartTrade AI Automated Daily Scheduler

set -e  # Exit on error

echo "=================================================="
echo "SmartTrade AI - Automated Scheduler Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Project Directory: $SCRIPT_DIR"
echo ""

# Step 1: Check Python version
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python 3 found: $PYTHON_VERSION${NC}"
    PYTHON_PATH=$(which python3)
    echo "  Path: $PYTHON_PATH"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.12+${NC}"
    exit 1
fi
echo ""

# Step 2: Check Git
echo -e "${YELLOW}Step 2: Checking Git configuration...${NC}"
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓ Git found${NC}"
    GIT_USER=$(git config user.name || echo "Not set")
    GIT_EMAIL=$(git config user.email || echo "Not set")
    echo "  User: $GIT_USER"
    echo "  Email: $GIT_EMAIL"
    
    if [ "$GIT_USER" = "Not set" ] || [ "$GIT_EMAIL" = "Not set" ]; then
        echo -e "${YELLOW}  Warning: Git user/email not configured${NC}"
        echo "  Run: git config --global user.name 'Your Name'"
        echo "  Run: git config --global user.email 'your.email@example.com'"
    fi
else
    echo -e "${RED}✗ Git not found. Please install Git${NC}"
    exit 1
fi
echo ""

# Step 3: Install Python dependencies
echo -e "${YELLOW}Step 3: Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Step 4: Create daily_results directory
echo -e "${YELLOW}Step 4: Creating results directory...${NC}"
mkdir -p daily_results
echo -e "${GREEN}✓ Directory created: daily_results/${NC}"
echo ""

# Step 5: Test imports
echo -e "${YELLOW}Step 5: Testing Python imports...${NC}"
python3 -c "import schedule, pytz, pandas, openpyxl; print('✓ All imports successful')" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All required packages available${NC}"
else
    echo -e "${RED}✗ Import test failed${NC}"
    exit 1
fi
echo ""

# Step 6: Setup launchd service
echo -e "${YELLOW}Step 6: Setting up launchd service...${NC}"
PLIST_FILE="$HOME/Library/LaunchAgents/com.smarttrade.scheduler.plist"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Update the plist file with correct paths
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.smarttrade.scheduler</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_DIR/automated_daily_scheduler.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/scheduler_stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/scheduler_stderr.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>SMARTTRADE_PROJECT_PATH</key>
        <string>$SCRIPT_DIR</string>
    </dict>
</dict>
</plist>
EOF

echo -e "${GREEN}✓ Plist file created: $PLIST_FILE${NC}"
echo ""

# Step 7: Load the service
echo -e "${YELLOW}Step 7: Loading launchd service...${NC}"
# Unload if already loaded
launchctl unload "$PLIST_FILE" 2>/dev/null || true
# Load the service
launchctl load "$PLIST_FILE"
echo -e "${GREEN}✓ Service loaded${NC}"
echo ""

# Step 8: Verify service is running
echo -e "${YELLOW}Step 8: Verifying service status...${NC}"
if launchctl list | grep -q "com.smarttrade.scheduler"; then
    echo -e "${GREEN}✓ Service is running${NC}"
else
    echo -e "${RED}✗ Service not found in launchctl list${NC}"
fi
echo ""

# Summary
echo "=================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "The scheduler is now running and will:"
echo "  • Run Ultimate Strategy at 6:00 AM Eastern Time"
echo "  • Skip weekends and market holidays"
echo "  • Export results to Excel with timestamps"
echo "  • Automatically push to GitHub"
echo ""
echo "Monitoring:"
echo "  • Activity log: tail -f automated_scheduler.log"
echo "  • Stdout log: tail -f scheduler_stdout.log"
echo "  • Stderr log: tail -f scheduler_stderr.log"
echo "  • Results: ls -lh daily_results/"
echo ""
echo "Management:"
echo "  • Stop: launchctl unload $PLIST_FILE"
echo "  • Start: launchctl load $PLIST_FILE"
echo "  • Status: launchctl list | grep smarttrade"
echo ""
echo "Next scheduled run will be at 6:00 AM Eastern on the next weekday."
echo ""
echo -e "${GREEN}Happy Automated Trading! 🚀📈${NC}"
