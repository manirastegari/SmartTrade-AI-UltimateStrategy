#!/usr/bin/env python3
"""
Automated Daily Scheduler for SmartTrade AI Ultimate Strategy
Runs at 6am Eastern Time every weekday (Mon-Fri)
Exports results to Excel with timestamps and pushes to GitHub
"""

import schedule
import time
import logging
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import pandas as pd
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomatedUltimateStrategyScheduler:
    """
    Automated scheduler for running Ultimate Strategy daily at 6am Eastern
    """
    
    def __init__(self, project_path: str = None):
        """
        Initialize the scheduler
        
        Args:
            project_path: Path to the project directory (default: current directory)
        """
        self.project_path = Path(project_path) if project_path else Path(__file__).parent
        self.eastern_tz = pytz.timezone('US/Eastern')
        self.results_dir = self.project_path / "daily_results"
        self.results_dir.mkdir(exist_ok=True)
        
        logger.info(f"Scheduler initialized. Project path: {self.project_path}")
        logger.info(f"Results directory: {self.results_dir}")
    
    def is_market_open_day(self) -> bool:
        """
        Check if today is a market open day (Mon-Fri, excluding holidays)
        
        Returns:
            bool: True if market is open, False otherwise
        """
        now = datetime.now(self.eastern_tz)
        
        # Check if weekend (Saturday=5, Sunday=6)
        if now.weekday() >= 5:
            logger.info(f"Today is {now.strftime('%A')} - Market closed (weekend)")
            return False
        
        # Check for major US market holidays
        holidays = self._get_market_holidays(now.year)
        today_date = now.date()
        
        if today_date in holidays:
            logger.info(f"Today is a market holiday: {holidays[today_date]}")
            return False
        
        logger.info(f"Today is {now.strftime('%A')} - Market is open")
        return True
    
    def _get_market_holidays(self, year: int) -> dict:
        """
        Get major US market holidays for the given year
        
        Args:
            year: Year to get holidays for
            
        Returns:
            dict: Dictionary of date -> holiday name
        """
        holidays = {}
        
        # New Year's Day
        new_years = datetime(year, 1, 1).date()
        if new_years.weekday() < 5:  # Weekday
            holidays[new_years] = "New Year's Day"
        
        # Martin Luther King Jr. Day (3rd Monday in January)
        mlk_day = self._get_nth_weekday(year, 1, 0, 3)  # 3rd Monday
        holidays[mlk_day] = "Martin Luther King Jr. Day"
        
        # Presidents' Day (3rd Monday in February)
        presidents_day = self._get_nth_weekday(year, 2, 0, 3)
        holidays[presidents_day] = "Presidents' Day"
        
        # Good Friday (Friday before Easter - complex calculation)
        # Simplified: typically in March/April
        
        # Memorial Day (Last Monday in May)
        memorial_day = self._get_last_weekday(year, 5, 0)
        holidays[memorial_day] = "Memorial Day"
        
        # Juneteenth (June 19)
        juneteenth = datetime(year, 6, 19).date()
        if juneteenth.weekday() < 5:
            holidays[juneteenth] = "Juneteenth"
        
        # Independence Day (July 4)
        independence_day = datetime(year, 7, 4).date()
        if independence_day.weekday() < 5:
            holidays[independence_day] = "Independence Day"
        
        # Labor Day (1st Monday in September)
        labor_day = self._get_nth_weekday(year, 9, 0, 1)
        holidays[labor_day] = "Labor Day"
        
        # Thanksgiving (4th Thursday in November)
        thanksgiving = self._get_nth_weekday(year, 11, 3, 4)
        holidays[thanksgiving] = "Thanksgiving"
        
        # Christmas (December 25)
        christmas = datetime(year, 12, 25).date()
        if christmas.weekday() < 5:
            holidays[christmas] = "Christmas"
        
        return holidays
    
    def _get_nth_weekday(self, year: int, month: int, weekday: int, n: int):
        """Get the nth occurrence of a weekday in a month"""
        first_day = datetime(year, month, 1)
        first_weekday = (weekday - first_day.weekday()) % 7
        return (first_day + timedelta(days=first_weekday + (n - 1) * 7)).date()
    
    def _get_last_weekday(self, year: int, month: int, weekday: int):
        """Get the last occurrence of a weekday in a month"""
        # Start from the last day of the month
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Go backwards to find the weekday
        while last_day.weekday() != weekday:
            last_day -= timedelta(days=1)
        
        return last_day.date()
    
    def run_ultimate_strategy(self) -> Optional[str]:
        """
        Run the Ultimate Strategy analysis
        
        Returns:
            str: Path to the generated Excel file, or None if failed
        """
        start_time = datetime.now(self.eastern_tz)
        logger.info("=" * 80)
        logger.info(f"Starting Ultimate Strategy Analysis at {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info("=" * 80)
        
        try:
            # Import the analyzer modules
            import sys
            sys.path.insert(0, str(self.project_path))
            
            from advanced_analyzer import AdvancedTradingAnalyzer
            from ultimate_strategy_analyzer_improved import ImprovedUltimateStrategyAnalyzer
            
            # Initialize analyzers
            logger.info("Initializing IMPROVED analyzers (true consensus logic)...")
            analyzer = AdvancedTradingAnalyzer(enable_training=True, data_mode="light")
            ultimate_analyzer = ImprovedUltimateStrategyAnalyzer(analyzer)
            
            # Progress callback
            def progress_callback(message: str, progress: int):
                logger.info(f"[{progress}%] {message}")
            
            # Run the analysis
            logger.info("Running Ultimate Strategy (this will take 2-3 hours)...")
            final_recommendations = ultimate_analyzer.run_ultimate_strategy(
                progress_callback=progress_callback
            )
            
            end_time = datetime.now(self.eastern_tz)
            duration = end_time - start_time
            
            logger.info("=" * 80)
            logger.info(f"Analysis completed at {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Total duration: {duration}")
            logger.info(f"Total recommendations: {len(final_recommendations.get('consensus_recommendations', []))}")
            logger.info("=" * 80)
            
            # Export to Excel with timestamps
            excel_file = self._export_to_excel_with_timestamps(
                final_recommendations,
                start_time,
                end_time
            )
            
            return excel_file
            
        except Exception as e:
            logger.error(f"Error running Ultimate Strategy: {str(e)}", exc_info=True)
            return None
    
    def _export_to_excel_with_timestamps(
        self,
        results: dict,
        start_time: datetime,
        end_time: datetime
    ) -> str:
        """
        Export results to Excel with start and end timestamps
        
        Args:
            results: Analysis results
            start_time: Analysis start time
            end_time: Analysis end time
            
        Returns:
            str: Path to the Excel file
        """
        timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"UltimateStrategy_Daily_{timestamp_str}.xlsx"
        
        logger.info(f"Exporting results to Excel: {filename}")
        
        try:
            # Get consensus recommendations
            recommendations = results.get('consensus_recommendations', [])
            
            if not recommendations:
                logger.warning("No recommendations to export")
                return None
            
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                
                # Sheet 1: Analysis Info with Timestamps
                info_data = {
                    'Metric': [
                        'Analysis Type',
                        'Start Date',
                        'Start Time',
                        'End Date', 
                        'End Time',
                        'Duration (hours)',
                        'Total Stocks Analyzed',
                        'Total Recommendations',
                        'Strong Buy Count',
                        'Buy Count',
                        'Market Status',
                        'Generated By'
                    ],
                    'Value': [
                        'Ultimate Strategy - 4-Strategy Consensus',
                        start_time.strftime('%Y-%m-%d'),
                        start_time.strftime('%H:%M:%S %Z'),
                        end_time.strftime('%Y-%m-%d'),
                        end_time.strftime('%H:%M:%S %Z'),
                        f"{(end_time - start_time).total_seconds() / 3600:.2f}",
                        results.get('total_analyzed', 'N/A'),
                        len(recommendations),
                        len([r for r in recommendations if r.get('recommendation') == 'STRONG BUY']),
                        len([r for r in recommendations if r.get('recommendation') == 'BUY']),
                        results.get('market_analysis', {}).get('status', 'N/A'),
                        'SmartTrade AI Automated Scheduler'
                    ]
                }
                info_df = pd.DataFrame(info_data)
                info_df.to_excel(writer, sheet_name='Analysis_Info', index=False)
                
                # Sheet 2: Consensus Recommendations
                if recommendations:
                    recs_df = pd.DataFrame(recommendations)
                    recs_df.to_excel(writer, sheet_name='Consensus_Recommendations', index=False)
                
                # Sheet 3: Market Analysis
                market_data = results.get('market_analysis', {})
                if market_data:
                    market_df = pd.DataFrame([market_data])
                    market_df.to_excel(writer, sheet_name='Market_Analysis', index=False)
                
                # Sheet 4: Sector Analysis
                sector_data = results.get('sector_analysis', {})
                if sector_data:
                    sector_df = pd.DataFrame([sector_data])
                    sector_df.to_excel(writer, sheet_name='Sector_Analysis', index=False)
                
                # Sheet 5: Strategy Results Summary
                strategy_results = results.get('strategy_results', {})
                if strategy_results:
                    strategy_summary = []
                    for strategy_name, strategy_data in strategy_results.items():
                        if isinstance(strategy_data, list):
                            strategy_summary.append({
                                'Strategy': strategy_name,
                                'Total Stocks': len(strategy_data),
                                'Strong Buy': len([s for s in strategy_data if s.get('recommendation') == 'STRONG BUY']),
                                'Buy': len([s for s in strategy_data if s.get('recommendation') == 'BUY'])
                            })
                    if strategy_summary:
                        strategy_df = pd.DataFrame(strategy_summary)
                        strategy_df.to_excel(writer, sheet_name='Strategy_Summary', index=False)
            
            logger.info(f"✅ Excel file created successfully: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}", exc_info=True)
            return None
    
    def push_to_github(self, excel_file: str) -> bool:
        """
        Push the Excel file to GitHub
        
        Args:
            excel_file: Path to the Excel file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not excel_file or not os.path.exists(excel_file):
            logger.error(f"Excel file not found: {excel_file}")
            return False
        
        logger.info("Pushing results to GitHub...")
        
        try:
            # Change to project directory
            os.chdir(self.project_path)
            
            # Git add the file
            logger.info(f"Adding file to git: {excel_file}")
            subprocess.run(['git', 'add', excel_file], check=True)
            
            # Git commit
            commit_message = f"Automated Ultimate Strategy Analysis - {datetime.now(self.eastern_tz).strftime('%Y-%m-%d %H:%M %Z')}"
            logger.info(f"Committing with message: {commit_message}")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Git push
            logger.info("Pushing to GitHub...")
            subprocess.run(['git', 'push'], check=True)
            
            logger.info("✅ Successfully pushed to GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error pushing to GitHub: {str(e)}", exc_info=True)
            return False
    
    def daily_job(self):
        """
        Main job that runs daily at 6am Eastern
        """
        logger.info("\n" + "=" * 80)
        logger.info("DAILY JOB TRIGGERED")
        logger.info("=" * 80)
        
        # Check if market is open
        if not self.is_market_open_day():
            logger.info("Market is closed today. Skipping analysis.")
            return
        
        # Run the analysis
        excel_file = self.run_ultimate_strategy()
        
        if excel_file:
            # Push to GitHub
            success = self.push_to_github(excel_file)
            
            if success:
                logger.info("✅ Daily job completed successfully!")
            else:
                logger.warning("⚠️ Analysis completed but GitHub push failed")
        else:
            logger.error("❌ Daily job failed - no results generated")
    
    def start_scheduler(self):
        """
        Start the scheduler to run daily at 6am Eastern
        """
        logger.info("=" * 80)
        logger.info("AUTOMATED ULTIMATE STRATEGY SCHEDULER STARTED")
        logger.info("=" * 80)
        logger.info(f"Schedule: Daily at 6:00 AM Eastern Time (Mon-Fri only)")
        logger.info(f"Project Path: {self.project_path}")
        logger.info(f"Results Directory: {self.results_dir}")
        logger.info("=" * 80)
        
        # Schedule the job for 6am Eastern
        schedule.every().day.at("06:00").do(self.daily_job)
        
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        logger.info(f"Next run scheduled for: {schedule.next_run()}")
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}", exc_info=True)


def main():
    """
    Main entry point for the scheduler
    """
    # Get project path from environment or use current directory
    project_path = os.environ.get('SMARTTRADE_PROJECT_PATH', os.path.dirname(__file__))
    
    # Create and start scheduler
    scheduler = AutomatedUltimateStrategyScheduler(project_path)
    scheduler.start_scheduler()


if __name__ == "__main__":
    main()
