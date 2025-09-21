#!/usr/bin/env python3
"""
ClipScutter Automation - Main Execution Script
==============================================

This is the main entry point for the ClipScutter automation system.
It orchestrates the entire process of reading CSV, creating clips, and downloading them.

Features:
- Premium trial account setup
- Efficient YouTube URL handling
- Bulk clip creation with 1080p quality
- Automatic clip downloading ($20 feature)
- Comprehensive error handling and logging
- Production-ready code with clean functions

Usage:
    python run_automation.py
    python run_automation.py --headless
    python run_automation.py --csv-file /path/to/clips.csv
    python run_automation.py --download-only
    python run_automation.py --help

Author: Automated ClipScutter Bot
Version: 1.0
Date: September 2025
"""

import sys
import os
import argparse
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Import our custom modules
try:
    from config import CONFIG
    from csv_reader import CSVReader, ClipData
    from web_automation import ClipScutterWebAutomation
    from download_clips import ClipDownloader
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required files are in the same directory")
    sys.exit(1)

# Import Selenium and other dependencies
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.common.exceptions import WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    print(f"Error importing Selenium: {e}")
    print("Install requirements with: pip install -r requirements.txt")
    sys.exit(1)

class ClipScutterRunner:
    """Main runner class that orchestrates the entire automation process"""
    
    def __init__(self, args):
        """
        Initialize the runner with command line arguments
        
        Args:
            args: Parsed command line arguments
        """
        self.args = args
        self.config = CONFIG
        self.logger = self.setup_logging()
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.automation = None
        self.web_automation: Optional[ClipScutterWebAutomation] = None
        self.downloader: Optional[ClipDownloader] = None
        
        # Statistics
        self.stats = {
            'start_time': time.time(),
            'total_clips': 0,
            'clips_created': 0,
            'clips_downloaded': 0,
            'failed_clips': 0,
            'unique_urls': 0
        }
    
    def setup_logging(self) -> logging.Logger:
        """
        Setup comprehensive logging system
        
        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logs directory
        self.config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        log_format = logging.Formatter(
            fmt=self.config.LOG_FORMAT,
            datefmt=self.config.LOG_DATE_FORMAT
        )
        
        # Setup file handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            filename=self.config.LOG_FILE,
            maxBytes=self.config.MAX_LOG_FILE_SIZE,
            backupCount=self.config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(log_format)
        file_handler.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        
        # Configure root logger
        logger = logging.getLogger('ClipScutterAutomation')
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        return logger
    
    def setup_webdriver(self) -> bool:
        """
        Setup Chrome WebDriver with optimal configuration
        
        Returns:
            bool: True if setup successful
        """
        try:
            self.logger.info("Setting up Chrome WebDriver...")
            
            chrome_options = Options()
            
            # Apply headless mode - DISABLED by user preference
            # Force visible browser mode
            self.logger.info("Running in visible browser mode (headless disabled)")
            
            # Add Chrome options from config
            for option in self.config.CHROME_OPTIONS:
                chrome_options.add_argument(option)
            
            # Set window size
            chrome_options.add_argument(f"--window-size={self.config.BROWSER_WINDOW_SIZE[0]},{self.config.BROWSER_WINDOW_SIZE[1]}")
            
            # Configure download preferences
            chrome_options.add_experimental_option("prefs", self.config.CHROME_DOWNLOAD_PREFS)
            
            # Disable automation indicators
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to automatically handle ChromeDriver
            self.logger.info("Setting up ChromeDriver using webdriver-manager...")
            service = Service(ChromeDriverManager().install())
            
            # Initialize WebDriver with service
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Remove webdriver property to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts - Optimized for speed
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(3)  # Reduced from 5 to 3 seconds
            
            # Initialize WebDriverWait
            self.wait = WebDriverWait(self.driver, self.config.ELEMENT_WAIT_TIMEOUT)
            
            self.logger.info("WebDriver setup completed successfully")
            return True
            
        except WebDriverException as e:
            self.logger.error(f"WebDriver setup failed: {e}")
            self.logger.error("Make sure Chrome browser and ChromeDriver are installed")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during WebDriver setup: {e}")
            return False
    
    def initialize_modules(self) -> bool:
        """
        Initialize all automation modules
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing automation modules...")
            
            # Ensure driver and wait are initialized
            if self.driver is None or self.wait is None:
                raise RuntimeError("WebDriver not initialized. Call setup_webdriver() first.")
            
            # Initialize web automation helper
            self.web_automation = ClipScutterWebAutomation(self.driver, self.wait)
            
            # Initialize clip downloader
            self.downloader = ClipDownloader(
                self.driver, 
                self.wait, 
                str(self.config.DOWNLOADS_DIR)
            )
            
            self.logger.info("All modules initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Module initialization failed: {e}")
            return False
    
    def read_and_validate_csv(self, csv_path: str) -> Optional[Dict]:
        """
        Read and validate the CSV file
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Dict with clips data or None if failed
        """
        try:
            self.logger.info(f"Reading CSV file: {csv_path}")
            
            # Check if file exists
            if not Path(csv_path).exists():
                self.logger.error(f"CSV file not found: {csv_path}")
                return None
            
            # Initialize CSV reader
            csv_reader = CSVReader(csv_path)
            
            # Read clips
            clips = csv_reader.read_csv()
            if not clips:
                self.logger.error("No valid clips found in CSV file")
                return None
            
            # Group clips by URL
            grouped_clips = csv_reader.group_clips_by_url(clips)
            
            # Get statistics
            stats = csv_reader.get_statistics()
            
            # Update our stats
            self.stats['total_clips'] = len(clips)
            self.stats['unique_urls'] = len(grouped_clips)
            
            self.logger.info(f"Successfully loaded {len(clips)} clips from {len(grouped_clips)} unique URLs")
            self.logger.info(f"Total estimated duration: {stats['total_duration_formatted']}")
            
            return {
                'clips': clips,
                'grouped_clips': grouped_clips,
                'stats': stats
            }
        except Exception as e:
            self.logger.error(f"Failed to read CSV file: {e}")
            return None
    
    def _ensure_modules_initialized(self) -> None:
        """Ensure all required modules are initialized"""
        if self.web_automation is None:
            raise RuntimeError("Web automation module not initialized")
        if self.downloader is None:
            raise RuntimeError("Downloader module not initialized")
    
    def perform_login(self) -> bool:
        """
        Perform login to ClipScutter
        
        Returns:
            bool: True if login successful
        """
        try:
            if not self.config.ENABLE_AUTO_LOGIN:
                self.logger.info("Auto-login disabled in config")
                return True
            
            self.logger.info("Starting login process...")
            
            # Ensure modules are initialized
            self._ensure_modules_initialized()
            
            # Perform login
            success = self.web_automation.perform_login(  # type: ignore
                self.config.LOGIN_EMAIL,
                self.config.LOGIN_PASSWORD
            )
            
            if success:
                self.logger.info("Login successful!")
                return True
            else:
                self.logger.error("Login failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Login process error: {e}")
            return False

    def setup_premium_trial(self) -> bool:
        """
        Setup premium trial account or detect existing login
        
        Returns:
            bool: True if premium trial setup successful or not needed
        """
        try:
            if not self.config.ENABLE_PREMIUM_TRIAL:
                self.logger.info("Premium trial setup disabled in config - assuming user is already logged in")
                return True
            
            self.logger.info("Checking account status...")
            
            # Navigate to homepage
            if not self.web_automation.navigate_to_homepage():
                return False
            
            # Check premium/login status
            success = self.web_automation.setup_premium_trial()
            
            if success:
                self.logger.info("Account status check successful - ready to proceed")
            else:
                self.logger.info("Continuing with current account status")
            
            return True  # Always continue
            
        except Exception as e:
            self.logger.info(f"Account status check completed: {e}")
            return True  # Always continue
    
    def process_all_clips(self, grouped_clips: Dict[str, List[ClipData]]) -> bool:
        """
        Process all clips grouped by YouTube URL
        
        Args:
            grouped_clips: Dictionary of clips grouped by URL
            
        Returns:
            bool: True if processing completed
        """
        try:
            # Ensure modules are initialized before processing
            self._ensure_modules_initialized()
            
            self.logger.info(f"Starting to process {len(grouped_clips)} unique YouTube URLs")
            
            url_count = 0
            total_urls = len(grouped_clips)
            
            for youtube_url, clips in grouped_clips.items():
                url_count += 1
                self.logger.info(f"Processing URL {url_count}/{total_urls}: {youtube_url}")
                self.logger.info(f"  {len(clips)} clips to create")
                
                # Check if we need to load a new URL
                if not self.web_automation.check_if_same_video_loaded(youtube_url):
                    if self.web_automation.current_url is not None:
                        # Go back to homepage for new URL
                        self.logger.info("Loading new YouTube URL - returning to homepage")
                        self.web_automation.reset_for_new_video()
                        time.sleep(self.config.DELAY_BETWEEN_CLIPS)
                    else:
                        # First URL, we're already on homepage
                        self.logger.info("Loading first YouTube URL")
                    
                    # Input the new YouTube URL
                    if not self.web_automation.input_youtube_url(youtube_url):
                        self.logger.error(f"Failed to input YouTube URL: {youtube_url}")
                        continue
                    
                    # Set quality to 1080p (with null check)
                    if hasattr(self.web_automation, 'set_quality_to_1080p'):
                        self.web_automation.set_quality_to_1080p()
                    
                    time.sleep(self.config.DELAY_AFTER_URL_INPUT)
                else:
                    self.logger.info(f"Same YouTube URL as previous - staying on current page")
                
                # Process all clips for this URL efficiently - NO going back to homepage for same URL!
                clips_created_for_url = 0
                for i, clip in enumerate(clips, 1):
                    self.logger.info(f"  Creating clip {i}/{len(clips)}: {clip.start_time}-{clip.end_time}")
                    
                    # For clips after the first one, navigate to Controls section to access time inputs
                    navigate_to_controls = (i > 1)  # True for 2nd clip and beyond
                    
                    # For same URL clips, we DON'T need to go back to homepage - just create the next clip!
                    # This is the efficiency improvement requested by the user
                    
                    success = self.web_automation.create_clip(clip.start_time, clip.end_time, navigate_to_controls=navigate_to_controls)
                    
                    if success:
                        clips_created_for_url += 1
                        self.stats['clips_created'] += 1
                        self.logger.info(f"  ✓ Clip {i}/{len(clips)} created successfully")
                        
                        # Wait a bit after successful clip creation before moving to next
                        time.sleep(3)
                    else:
                        self.stats['failed_clips'] += 1
                        self.logger.error(f"  ✗ Failed to create clip {i}/{len(clips)}")
                    
                    # Delay between clips
                    time.sleep(self.config.DELAY_BETWEEN_CLIPS)
                
                self.logger.info(f"Completed URL {url_count}/{total_urls}: {clips_created_for_url}/{len(clips)} clips created")
            
            self.logger.info(f"Clip creation completed: {self.stats['clips_created']}/{self.stats['total_clips']} clips created")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing clips: {e}")
            return False
    
    def download_all_clips(self) -> bool:
        """
        Download all created clips
        
        Returns:
            bool: True if download process completed
        """
        try:
            if self.args.skip_download:
                self.logger.info("Skipping download as requested")
                return True
            
            self.logger.info("Starting clip download process...")
            
            # Download all clips
            result = self.downloader.download_all_clips()
            
            if result['success']:
                self.stats['clips_downloaded'] = result['downloaded']
                self.logger.info(f"Download completed: {result['downloaded']}/{result['total_clips']} clips downloaded")
                
                if result['failed'] > 0:
                    self.logger.warning(f"{result['failed']} clips failed to download")
                    self.logger.warning(f"Failed clips: {result.get('failed_clips', [])}")
                
                return True
            else:
                self.logger.error(f"Download process failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during download process: {e}")
            return False
    
    def download_clips_only(self) -> bool:
        """
        Download clips only (skip creation)
        
        Returns:
            bool: True if download successful
        """
        try:
            self.logger.info("Download-only mode: Downloading existing clips...")
            
            # Setup WebDriver
            if not self.setup_webdriver():
                return False
            
            # Initialize downloader
            self.downloader = ClipDownloader(
                self.driver,
                WebDriverWait(self.driver, self.config.ELEMENT_WAIT_TIMEOUT),
                str(self.config.DOWNLOADS_DIR)
            )
            
            # Download clips
            result = self.downloader.download_all_clips()
            
            if result['success']:
                self.logger.info(f"Download-only completed: {result['downloaded']} clips downloaded")
                return True
            else:
                self.logger.error(f"Download-only failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Download-only mode failed: {e}")
            return False
    
    def print_final_summary(self) -> None:
        """Print final summary of the automation run"""
        end_time = time.time()
        duration = end_time - self.stats['start_time']
        
        self.logger.info("=" * 60)
        self.logger.info("AUTOMATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total execution time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        self.logger.info(f"Total clips in CSV: {self.stats['total_clips']}")
        self.logger.info(f"Unique YouTube URLs: {self.stats['unique_urls']}")
        self.logger.info(f"Clips created successfully: {self.stats['clips_created']}")
        self.logger.info(f"Clips downloaded: {self.stats['clips_downloaded']}")
        self.logger.info(f"Failed clips: {self.stats['failed_clips']}")
        
        if self.stats['total_clips'] > 0:
            success_rate = (self.stats['clips_created'] / self.stats['total_clips']) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        self.logger.info(f"Downloads directory: {self.config.DOWNLOADS_DIR}")
        self.logger.info(f"Log file: {self.config.LOG_FILE}")
        self.logger.info("=" * 60)
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def run(self) -> int:
        """
        Main execution method
        
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            self.logger.info("Starting ClipScutter Automation")
            self.logger.info(f"Configuration: {self.config.__class__.__name__}")
            
            # Handle download-only mode
            if self.args.download_only:
                success = self.download_clips_only()
                return 0 if success else 1
            
            # Read and validate CSV
            csv_data = self.read_and_validate_csv(self.args.csv_file)
            if not csv_data:
                return 1
            
            # Setup WebDriver
            if not self.setup_webdriver():
                return 1
            
            # Initialize modules
            if not self.initialize_modules():
                return 1
            
            # Initialize modules first
            if not self.initialize_modules():
                return 1
            
            # Navigate directly to login page first
            self.logger.info("🔐 Step 1: Navigating directly to login page...")
            if not self.web_automation.navigate_to_login_page():
                self.logger.error("Failed to navigate to ClipScutter login page")
                return 1
            
            # Perform login
            self.logger.info("🔑 Step 2: Performing login...")
            if not self.perform_login():
                self.logger.error("Login failed - cannot continue")
                return 1
            
            # After successful login, navigate to homepage
            self.logger.info("🏠 Step 3: Navigating to homepage after successful login...")
            if not self.web_automation.navigate_to_homepage():
                self.logger.error("Failed to navigate to homepage after login")
                return 1
            
            # Setup premium trial or check login status (now redundant but keeping for compatibility)
            if not self.setup_premium_trial():
                self.logger.warning("Account setup had issues, but continuing anyway")
            
            # Process all clips
            if not self.process_all_clips(csv_data['grouped_clips']):
                self.logger.error("Clip processing failed")
                return 1
            
            # Download clips (the $20 feature)
            if not self.download_all_clips():
                self.logger.warning("Clip download failed, but automation completed")
            
            self.logger.info("Automation completed successfully!")
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Automation interrupted by user")
            return 1
        except Exception as e:
            self.logger.error(f"Automation failed with error: {e}")
            return 1
        finally:
            self.print_final_summary()
            self.cleanup()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ClipScutter Automation - Automated clip creation and downloading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_automation.py                           # Run with default settings
  python run_automation.py --headless              # Run in headless mode
  python run_automation.py --csv-file custom.csv   # Use custom CSV file
  python run_automation.py --download-only         # Only download existing clips
  python run_automation.py --skip-download         # Skip the download phase
  
For support, check the logs in the logs/ directory.
        """
    )
    
    parser.add_argument(
        '--csv-file',
        default=str(CONFIG.CSV_FILE),
        help=f'Path to CSV file with clip ranges (default: {CONFIG.CSV_FILE})'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    parser.add_argument(
        '--download-only',
        action='store_true',
        help='Only download existing clips, skip creation'
    )
    
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip the download phase'
    )
    
    parser.add_argument(
        '--config-env',
        choices=['development', 'production', 'testing'],
        default='development',
        help='Configuration environment to use'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ClipScutter Automation v1.0'
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Set environment for configuration
        os.environ['CLIPSCUTTER_ENV'] = args.config_env
        
        # Validate configuration
        CONFIG.validate_config()
        
        # Run automation
        runner = ClipScutterRunner(args)
        exit_code = runner.run()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()