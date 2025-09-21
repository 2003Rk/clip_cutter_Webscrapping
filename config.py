"""
Configuration Settings for ClipScutter Automation
=================================================

This module contains all configuration settings for the ClipScutter automation system.
Modify these settings to customize the behavior of the automation.

Author: Automated ClipScutter Bot
Version: 1.0
"""

import os
from pathlib import Path

class Config:
    """Main configuration class"""
    
    # Base paths
    BASE_DIR = Path("/Users/rahul/Desktop/FREELANCING/20$_clipcut")
    CSV_FILE = BASE_DIR / "clip_ranges.csv"
    DOWNLOADS_DIR = BASE_DIR / "downloads"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Selenium WebDriver settings - ULTRA FAST for URL input and buttons
    HEADLESS_MODE = False  # Always visible browser mode
    BROWSER_WINDOW_SIZE = (1920, 1080)
    PAGE_LOAD_TIMEOUT = 15  # Reduced from 20 to 15 seconds for faster page loads
    ELEMENT_WAIT_TIMEOUT = 8  # Reduced from 10 to 8 seconds for faster element detection
    
    # ClipScutter website URLs
    CLIPSCUTTER_BASE_URL = "https://www.clipscutter.com"
    CLIPSCUTTER_CLIPS_URL = "https://www.clipscutter.com/clips"
    
    # Automation timing settings (in seconds) - ULTRA FAST OPTIMIZATION
    DELAY_BETWEEN_CLIPS = 1.0  # Reduced from 1.5 to 1.0 for faster processing
    DELAY_AFTER_URL_INPUT = 0.5  # Reduced from 1 to 0.5 for faster URL processing
    DELAY_AFTER_CLIP_CREATION = 1.5  # Reduced from 2 to 1.5 for faster clip creation
    DELAY_BETWEEN_DOWNLOADS = 0.5  # Reduced from 1 to 0.5 for faster downloads
    DELAY_FOR_VIDEO_LOAD = 1.5  # Reduced from 2 to 1.5 for faster video loading
    
    # Login credentials
    LOGIN_EMAIL = "rahulkr99222@gmail.com"
    LOGIN_PASSWORD = "Bharat19451#"
    ENABLE_AUTO_LOGIN = True
    
    # Premium trial settings
    ENABLE_PREMIUM_TRIAL = False  # Disabled - will login instead
    PREMIUM_TRIAL_TIMEOUT = 10  # seconds to wait for premium trial setup
    
    # Video quality settings
    PREFERRED_QUALITY = "1080p"
    FALLBACK_QUALITIES = ["1080", "Full HD", "720p", "720", "HD"]
    
    # Download settings
    MAX_DOWNLOAD_RETRIES = 3
    DOWNLOAD_TIMEOUT = 300  # seconds (5 minutes)
    CHUNK_SIZE = 8192  # bytes for streaming downloads
    
    # File naming settings
    MAX_FILENAME_LENGTH = 200
    INVALID_FILENAME_CHARS = '<>:"/\\|?*'
    
    # Logging settings
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = LOGS_DIR / "clipscutter_automation.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Error handling settings
    MAX_RETRIES_PER_CLIP = 3
    CONTINUE_ON_ERROR = True
    SAVE_ERROR_SCREENSHOTS = True
    SCREENSHOT_DIR = BASE_DIR / "error_screenshots"
    
    # Performance settings
    PARALLEL_DOWNLOADS = False  # Set to True for parallel downloading (experimental)
    MAX_PARALLEL_DOWNLOADS = 3
    
    # Browser preferences for downloads - Improved stability
    CHROME_DOWNLOAD_PREFS = {
        "download.default_directory": str(DOWNLOADS_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        "download.extensions_to_open": "",  # Prevent auto-opening files
        "download.open_pdf_in_system_reader": False,  # Prevent PDF opening
        "plugins.always_open_pdf_externally": False  # Keep PDFs in browser
    }
    
    # Chrome options for optimal performance - Speed optimized with stability
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",  # Faster loading
        "--disable-features=TranslateUI",  # Disable translation
        "--disable-ipc-flooding-protection",  # Faster IPC
        "--disable-renderer-backgrounding",  # Keep renderer active
        "--disable-backgrounding-occluded-windows",  # Better performance
        "--disable-component-extensions-with-background-pages",  # Reduce overhead
        "--disable-popup-blocking",  # Prevent popup issues
        "--disable-translate",  # Disable translation
        "--disable-background-timer-throttling",  # Keep timers active
        "--disable-renderer-backgrounding",  # Keep renderer active
        "--disable-backgrounding-occluded-windows",  # Better performance
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    # XPath selectors for web elements (can be customized if ClipScutter changes)
    SELECTORS = {
        "url_input": [
            "//input[@type='url']",
            "//input[contains(@placeholder, 'youtube')]",
            "//input[contains(@placeholder, 'URL')]",
            "//input[contains(@placeholder, 'link')]",
            "//input[contains(@name, 'url')]",
            "//input[contains(@id, 'url')]"
        ],
        "submit_button": [
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Process')]",
            "//button[contains(text(), 'Load')]",
            "//button[contains(text(), 'Go')]",
            "//button[contains(text(), 'Analyze')]",
            "//input[@type='submit']",
            "//button[@type='submit']"
        ],
        "start_time_input": [
            "//input[contains(@placeholder, 'start')]",
            "//input[contains(@name, 'start')]",
            "//input[contains(@id, 'start')]",
            "//input[contains(@class, 'start')]"
        ],
        "end_time_input": [
            "//input[contains(@placeholder, 'end')]",
            "//input[contains(@name, 'end')]",
            "//input[contains(@id, 'end')]",
            "//input[contains(@class, 'end')]"
        ],
        "create_button": [
            "//button[contains(text(), 'Create')]",
            "//button[contains(text(), 'Cut')]",
            "//button[contains(text(), 'Generate')]", 
            "//button[contains(text(), 'Process')]",
            "//button[contains(text(), 'Make Clip')]",
            "//button[contains(text(), 'Download')]",
            "//button[contains(text(), 'Export')]",
            "//button[contains(@class, 'create')]",
            "//button[contains(@class, 'cut')]",
            "//button[contains(@class, 'download')]",
            "//input[@type='submit']",
            "//button[@type='submit']",
            "//div[contains(@class, 'button') and contains(text(), 'Create')]",
            "//div[contains(@class, 'button') and contains(text(), 'Cut')]"
        ],
        "download_button": [
            "//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]",  # Specific selector from user
            "//button[@title='Download']",
            "//button[contains(@class, 'downloadIcon')]",
            "//button[contains(@class, 'cutterClipsListItem_downloadIcon')]",
            ".//button[contains(text(), 'Download')]",
            ".//a[contains(text(), 'Download')]",
            ".//a[contains(@href, 'download')]",
            ".//button[contains(@class, 'download')]",
            ".//a[contains(@class, 'download')]"
        ],
        "premium_button": [
            "//button[contains(text(), 'Premium')]",
            "//button[contains(text(), 'Trial')]",
            "//button[contains(text(), 'Free Trial')]",
            "//a[contains(text(), 'Premium')]",
            "//a[contains(text(), 'Trial')]"
        ],
        "quality_selector": [
            "//select[contains(@class, 'quality')]",
            "//select[contains(@name, 'quality')]",
            "//select[contains(@id, 'quality')]",
            "//button[contains(@class, 'quality')]"
        ]
    }
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DOWNLOADS_DIR,
            cls.LOGS_DIR,
            cls.SCREENSHOT_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check if CSV file exists
        if not cls.CSV_FILE.exists():
            errors.append(f"CSV file not found: {cls.CSV_FILE}")
        
        # Check timeout values
        if cls.PAGE_LOAD_TIMEOUT <= 0:
            errors.append("PAGE_LOAD_TIMEOUT must be positive")
        
        if cls.ELEMENT_WAIT_TIMEOUT <= 0:
            errors.append("ELEMENT_WAIT_TIMEOUT must be positive")
        
        # Check download settings
        if cls.MAX_DOWNLOAD_RETRIES < 1:
            errors.append("MAX_DOWNLOAD_RETRIES must be at least 1")
        
        if cls.DOWNLOAD_TIMEOUT <= 0:
            errors.append("DOWNLOAD_TIMEOUT must be positive")
        
        # Check log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of: {valid_log_levels}")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
        
        return True

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    HEADLESS_MODE = False
    LOG_LEVEL = "DEBUG"
    SAVE_ERROR_SCREENSHOTS = True
    CONTINUE_ON_ERROR = True

class ProductionConfig(Config):
    """Production environment configuration"""
    HEADLESS_MODE = True
    LOG_LEVEL = "INFO"
    SAVE_ERROR_SCREENSHOTS = False
    CONTINUE_ON_ERROR = True

class TestingConfig(Config):
    """Testing environment configuration"""
    HEADLESS_MODE = True
    LOG_LEVEL = "DEBUG"
    MAX_RETRIES_PER_CLIP = 1
    DELAY_BETWEEN_CLIPS = 1
    DELAY_AFTER_CLIP_CREATION = 2

# Auto-select configuration based on environment
def get_config():
    """Get configuration based on environment variable"""
    env = os.getenv('CLIPSCUTTER_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

# Default configuration
CONFIG = get_config()

# Ensure directories exist
CONFIG.create_directories()