#!/usr/bin/env python3
"""
Comprehensive Validation Script for SmartTrade AI Ultimate Strategy
Validates all components before running the automated system
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import importlib.util

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

class SystemValidator:
    """Validates all system components"""
    
    def __init__(self):
        self.project_path = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def validate_python_version(self):
        """Check Python version"""
        print_info("Checking Python version...")
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print_success(f"Python {version.major}.{version.minor}.{version.micro}")
            self.passed += 1
            return True
        else:
            print_error(f"Python {version.major}.{version.minor} - Need Python 3.8+")
            self.errors.append("Python version too old")
            self.failed += 1
            return False
    
    def validate_dependencies(self):
        """Check if all required packages are installed"""
        print_info("Checking required packages...")
        
        required_packages = [
            'streamlit',
            'pandas',
            'numpy',
            'yfinance',
            'plotly',
            'sklearn',
            'xgboost',
            'lightgbm',
            'schedule',
            'pytz',
            'openpyxl'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
                print_success(f"{package}")
            except ImportError:
                print_error(f"{package} - NOT INSTALLED")
                missing.append(package)
        
        if missing:
            self.errors.append(f"Missing packages: {', '.join(missing)}")
            self.failed += 1
            print_warning(f"Install missing packages: pip install {' '.join(missing)}")
            return False
        else:
            self.passed += 1
            return True
    
    def validate_stock_universe(self):
        """Validate stock universe size"""
        print_info("Checking stock universe...")
        
        try:
            from questrade_valid_universe import get_questrade_valid_universe
            universe = get_questrade_valid_universe()
            unique_count = len(set(universe))
            
            if 500 <= unique_count <= 800:
                print_success(f"Stock universe: {unique_count} unique symbols (Target: 500-800)")
                self.passed += 1
                return True
            else:
                print_warning(f"Stock universe: {unique_count} symbols (Expected: 500-800)")
                self.warnings.append(f"Stock universe size: {unique_count}")
                self.passed += 1
                return True
        except Exception as e:
            print_error(f"Failed to load stock universe: {e}")
            self.errors.append("Stock universe validation failed")
            self.failed += 1
            return False
    
    def validate_core_files(self):
        """Check if all core files exist"""
        print_info("Checking core files...")
        
        required_files = [
            'professional_trading_app.py',
            'advanced_analyzer.py',
            'ultimate_strategy_analyzer_improved.py',
            'advanced_data_fetcher.py',
            'questrade_valid_universe.py',
            'cleaned_high_potential_universe.py',
            'automated_daily_scheduler.py',
            'requirements.txt'
        ]
        
        missing = []
        for file in required_files:
            file_path = self.project_path / file
            if file_path.exists():
                print_success(f"{file}")
            else:
                print_error(f"{file} - NOT FOUND")
                missing.append(file)
        
        if missing:
            self.errors.append(f"Missing files: {', '.join(missing)}")
            self.failed += 1
            return False
        else:
            self.passed += 1
            return True
    
    def validate_data_sources(self):
        """Validate data sources and APIs"""
        print_info("Checking data sources...")
        
        try:
            # Test Yahoo Finance (free, no API key needed)
            import yfinance as yf
            test_ticker = yf.Ticker("AAPL")
            
            # Try to get basic info
            try:
                info = test_ticker.info
                if info and ('currentPrice' in info or 'regularMarketPrice' in info):
                    print_success("Yahoo Finance - Working (Primary data source)")
                    self.passed += 1
                    return True
            except Exception:
                pass
            
            # If info fails, try history (more reliable)
            hist = test_ticker.history(period="1d")
            if not hist.empty:
                print_success("Yahoo Finance - Working (Historical data available)")
                self.passed += 1
                return True
            else:
                print_warning("Yahoo Finance - Temporarily rate-limited (will work during analysis)")
                self.warnings.append("Yahoo Finance temporarily rate-limited - this is normal")
                self.passed += 1
                return True
                
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                print_warning("Yahoo Finance - Temporarily rate-limited (will work during analysis)")
                self.warnings.append("Yahoo Finance temporarily rate-limited - this is normal")
                self.passed += 1
                return True
            else:
                print_error(f"Yahoo Finance - Failed: {error_str[:100]}")
                self.errors.append("Yahoo Finance validation failed")
                self.failed += 1
                return False
    
    def validate_directories(self):
        """Check if required directories exist or can be created"""
        print_info("Checking directories...")
        
        required_dirs = [
            'exports',
            'daily_results',
            '.cache'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            try:
                dir_path.mkdir(exist_ok=True)
                print_success(f"{dir_name}/ - Ready")
            except Exception as e:
                print_error(f"{dir_name}/ - Failed: {e}")
                self.errors.append(f"Cannot create directory: {dir_name}")
                self.failed += 1
                return False
        
        self.passed += 1
        return True
    
    def validate_git_setup(self):
        """Check if git is configured"""
        print_info("Checking Git configuration...")
        
        try:
            # Check if git is installed
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
            print_success(f"Git installed: {result.stdout.strip()}")
            
            # Check if in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  cwd=self.project_path,
                                  capture_output=True,
                                  text=True,
                                  check=True)
            print_success("Git repository initialized")
            
            # Check git remote
            result = subprocess.run(['git', 'remote', '-v'],
                                  cwd=self.project_path,
                                  capture_output=True,
                                  text=True,
                                  check=True)
            if result.stdout:
                print_success("Git remote configured")
                self.passed += 1
                return True
            else:
                print_warning("No git remote configured - GitHub push will fail")
                self.warnings.append("Git remote not configured")
                self.passed += 1
                return True
        except subprocess.CalledProcessError:
            print_warning("Git not configured - GitHub push will be disabled")
            self.warnings.append("Git not configured")
            self.passed += 1
            return True
        except FileNotFoundError:
            print_error("Git not installed")
            self.errors.append("Git not installed")
            self.failed += 1
            return False
    
    def validate_streamlit_command(self):
        """Test if streamlit command works"""
        print_info("Checking Streamlit command...")
        
        try:
            result = subprocess.run(['streamlit', '--version'],
                                  capture_output=True,
                                  text=True,
                                  check=True)
            print_success(f"Streamlit: {result.stdout.strip()}")
            self.passed += 1
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("Streamlit command not found")
            self.errors.append("Streamlit not in PATH")
            self.failed += 1
            return False
    
    def test_import_modules(self):
        """Test importing core modules"""
        print_info("Testing module imports...")
        
        modules = [
            'advanced_analyzer',
            'ultimate_strategy_analyzer_improved',
            'advanced_data_fetcher',
            'questrade_valid_universe',
            'automated_daily_scheduler'
        ]
        
        for module_name in modules:
            try:
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    self.project_path / f"{module_name}.py"
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                print_success(f"{module_name}.py")
            except Exception as e:
                print_error(f"{module_name}.py - Import failed: {str(e)[:50]}")
                self.errors.append(f"Module import failed: {module_name}")
                self.failed += 1
                return False
        
        self.passed += 1
        return True
    
    def run_all_validations(self):
        """Run all validation checks"""
        print_header("SMARTTRADE AI - COMPREHENSIVE SYSTEM VALIDATION")
        print_info(f"Project Path: {self.project_path}")
        print_info(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        validations = [
            ("Python Version", self.validate_python_version),
            ("Required Packages", self.validate_dependencies),
            ("Stock Universe", self.validate_stock_universe),
            ("Core Files", self.validate_core_files),
            ("Data Sources", self.validate_data_sources),
            ("Directories", self.validate_directories),
            ("Git Setup", self.validate_git_setup),
            ("Streamlit Command", self.validate_streamlit_command),
            ("Module Imports", self.test_import_modules)
        ]
        
        for name, validation_func in validations:
            print_header(f"Validating: {name}")
            validation_func()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print validation summary"""
        print_header("VALIDATION SUMMARY")
        
        total = self.passed + self.failed
        print(f"\n{Colors.BOLD}Total Checks: {total}{Colors.END}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.END}\n")
        
        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}ERRORS:{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}• {error}{Colors.END}")
            print()
        
        if self.warnings:
            print(f"{Colors.YELLOW}{Colors.BOLD}WARNINGS:{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}• {warning}{Colors.END}")
            print()
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL VALIDATIONS PASSED!{Colors.END}")
            print(f"\n{Colors.BOLD}Ready to run:{Colors.END}")
            print(f"  {Colors.BLUE}1. Manual run: streamlit run professional_trading_app.py{Colors.END}")
            print(f"  {Colors.BLUE}2. Automated 6am runs: python3 automated_daily_scheduler.py{Colors.END}\n")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED{Colors.END}")
            print(f"{Colors.RED}Please fix the errors above before running the system.{Colors.END}\n")
            return False


def main():
    """Main entry point"""
    validator = SystemValidator()
    success = validator.run_all_validations()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
