"""
ClipScutter Automation - Main Script
====================================

This script automates the ClipScutter web interface to:
1. Read clip ranges from CSV file
2. Create clips with premium trial account
3. Handle YouTube URL changes efficiently
4. Download all created clips

Author: Automated ClipScutter Bot
Version: 1.0
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clipscutter_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ClipData:
    """Data class to store clip information"""
    start_time: str
    end_time: str
    youtube_url: str
    
    def __str__(self) -> str:
        return f"Clip: {self.start_time}-{self.end_time} from {self.youtube_url}"

class ClipScutterAutomation:
    """Main automation class for ClipScutter operations"""
    
    def __init__(self, headless: bool = False):
        """
        Initialize the automation bot
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.headless = headless
        self.current_youtube_url = None
        self.clips_created = 0
        
    def setup_driver(self) -> None:
        """Setup Chrome WebDriver with optimal configuration"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Optimize for performance and stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Download preferences for automatic file downloads
            prefs = {
                "download.default_directory": "/Users/rahul/Desktop/FREELANCING/20$_clipcut/downloads",
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Use webdriver-manager to automatically handle ChromeDriver
            logger.info("Setting up ChromeDriver using webdriver-manager...")
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("WebDriver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise
    
    def _ensure_driver_initialized(self) -> None:
        """Ensure that driver and wait are properly initialized"""
        if self.driver is None or self.wait is None:
            self.setup_driver()
    
    def read_csv_file(self, csv_path: str) -> List[ClipData]:
        """
        Read and parse the CSV file containing clip ranges
        
        Args:
            csv_path (str): Path to the CSV file
            
        Returns:
            List[ClipData]: List of clip data objects
        """
        clips = []
        try:
            with open(csv_path, 'r', newline='') as file:
                csv_reader = csv.reader(file)
                for row_num, row in enumerate(csv_reader, 1):
                    if len(row) >= 3:
                        clip = ClipData(
                            start_time=row[0].strip(),
                            end_time=row[1].strip(),
                            youtube_url=row[2].strip()
                        )
                        clips.append(clip)
                        logger.info(f"Row {row_num}: {clip}")
                    else:
                        logger.warning(f"Row {row_num}: Invalid format - {row}")
            
            logger.info(f"Successfully loaded {len(clips)} clips from CSV")
            return clips
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def group_clips_by_url(self, clips: List[ClipData]) -> Dict[str, List[ClipData]]:
        """
        Group clips by YouTube URL for efficient processing
        
        Args:
            clips (List[ClipData]): List of all clips
            
        Returns:
            Dict[str, List[ClipData]]: Clips grouped by YouTube URL
        """
        grouped = {}
        for clip in clips:
            if clip.youtube_url not in grouped:
                grouped[clip.youtube_url] = []
            grouped[clip.youtube_url].append(clip)
        
        logger.info(f"Grouped clips into {len(grouped)} different YouTube URLs")
        for url, url_clips in grouped.items():
            logger.info(f"  {url}: {len(url_clips)} clips")
        
        return grouped
    
    def navigate_to_clipscutter(self) -> None:
        """Navigate to ClipScutter homepage"""
        try:
            self._ensure_driver_initialized()
            self.driver.get("https://www.clipscutter.com")  # type: ignore
            logger.info("Navigated to ClipScutter homepage")
            time.sleep(1)  # Reduced from 2 to 1
        except Exception as e:
            logger.error(f"Failed to navigate to ClipScutter: {e}")
            raise
    
    def setup_premium_trial(self) -> None:
        """Setup premium trial account if needed"""
        try:
            # Look for premium trial or account setup elements
            # This would need to be customized based on actual ClipScutter interface
            logger.info("Setting up premium trial account...")
            
            # Wait for page to load completely
            time.sleep(1.5)  # Reduced from 3 to 1.5
            
            # Check if we need to create an account or sign in
            try:
                sign_up_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign Up') or contains(text(), 'Premium') or contains(text(), 'Trial')]"))
                )
                sign_up_button.click()
                logger.info("Clicked premium trial signup")
                time.sleep(1)  # Reduced from 2 to 1
            except TimeoutException:
                logger.info("No premium trial setup needed or already configured")
                
        except Exception as e:
            logger.warning(f"Premium trial setup may have failed: {e}")
            # Continue anyway as this might not be critical
    
    def input_youtube_url(self, youtube_url: str) -> None:
        """
        Input YouTube URL into ClipScutter
        
        Args:
            youtube_url (str): YouTube URL to process
        """
        try:
            self._ensure_driver_initialized()
            # Find and clear the YouTube URL input field
            url_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='url' or @placeholder*='youtube' or @placeholder*='URL']"))
            )
            url_input.clear()
            url_input.send_keys(youtube_url)
            
            logger.info(f"Entered YouTube URL: {youtube_url}")
            
            # Click the submit/process button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Process') or contains(text(), 'Submit') or contains(text(), 'Load')]"))
            )
            submit_button.click()
            
            logger.info("Clicked submit button for YouTube URL")
            
            # Wait for the video to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//video | //iframe | //*[contains(@class, 'video')]"))
            )
            
            logger.info("Video loaded successfully")
            time.sleep(1.5)  # Reduced from 3 to 1.5
            
        except Exception as e:
            logger.error(f"Failed to input YouTube URL: {e}")
            raise
    
    def set_quality_to_1080p(self) -> None:
        """Set video quality to 1080p"""
        try:
            # Look for quality selector dropdown
            quality_selector = self.driver.find_element(By.XPATH, "//select[contains(@class, 'quality') or contains(@name, 'quality')] | //div[contains(@class, 'quality')]")
            
            if quality_selector.tag_name == 'select':
                select = Select(quality_selector)
                select.select_by_visible_text("1080p")
            else:
                # If it's a div-based dropdown
                quality_selector.click()
                time.sleep(1)
                quality_option = self.driver.find_element(By.XPATH, "//option[contains(text(), '1080p')] | //*[contains(text(), '1080p')]")
                quality_option.click()
            
            logger.info("Set quality to 1080p")
            time.sleep(1)
            
        except NoSuchElementException:
            logger.warning("Quality selector not found, using default quality")
        except Exception as e:
            logger.warning(f"Failed to set quality to 1080p: {e}")
    
    def create_clip(self, start_time: str, end_time: str) -> bool:
        """
        Create a single clip with given start and end times
        
        Args:
            start_time (str): Start time in format HH:MM:SS
            end_time (str): End time in format HH:MM:SS
            
        Returns:
            bool: True if clip created successfully
        """
        try:
            # Find start time input
            start_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder*='start' or @name*='start' or @id*='start']"))
            )
            start_input.clear()
            start_input.send_keys(start_time)
            
            # Find end time input
            end_input = self.driver.find_element(By.XPATH, "//input[@placeholder*='end' or @name*='end' or @id*='end']")
            end_input.clear()
            end_input.send_keys(end_time)
            
            logger.info(f"Set clip times: {start_time} to {end_time}")
            
            # Click create button
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Cut') or contains(text(), 'Generate')]"))
            )
            create_button.click()
            
            logger.info("Clicked create clip button")
            
            # Wait for clip creation to complete
            time.sleep(2.5)  # Reduced from 5 to 2.5
            
            # Check for success indicators
            try:
                success_indicator = self.driver.find_element(By.XPATH, "//*[contains(text(), 'success') or contains(text(), 'created') or contains(text(), 'ready')]")
                logger.info("Clip created successfully")
                self.clips_created += 1
                return True
            except NoSuchElementException:
                logger.warning("No clear success indicator found, assuming clip was created")
                self.clips_created += 1
                return True
                
        except Exception as e:
            logger.error(f"Failed to create clip {start_time}-{end_time}: {e}")
            return False
    
    def process_clips_for_url(self, youtube_url: str, clips: List[ClipData]) -> None:
        """
        Process all clips for a specific YouTube URL
        
        Args:
            youtube_url (str): YouTube URL
            clips (List[ClipData]): List of clips for this URL
        """
        try:
            logger.info(f"Processing {len(clips)} clips for URL: {youtube_url}")
            
            # If this is a new URL, input it
            if self.current_youtube_url != youtube_url:
                if self.current_youtube_url is not None:
                    # Navigate back to homepage for new URL
                    self.navigate_to_clipscutter()
                    time.sleep(1)  # Reduced from 2 to 1
                
                self.input_youtube_url(youtube_url)
                self.set_quality_to_1080p()
                self.current_youtube_url = youtube_url
            
            # Process all clips for this URL
            for i, clip in enumerate(clips, 1):
                logger.info(f"Creating clip {i}/{len(clips)}: {clip.start_time}-{clip.end_time}")
                
                success = self.create_clip(clip.start_time, clip.end_time)
                if success:
                    logger.info(f"Successfully created clip {i}/{len(clips)}")
                else:
                    logger.error(f"Failed to create clip {i}/{len(clips)}")
                
                # Small delay between clips
                time.sleep(1)  # Reduced from 2 to 1
            
            logger.info(f"Completed processing all clips for {youtube_url}")
            
        except Exception as e:
            logger.error(f"Error processing clips for {youtube_url}: {e}")
            raise
    
    def download_all_clips(self) -> None:
        """Download all created clips from the clips page"""
        try:
            logger.info("Navigating to clips download page...")
            
            # Navigate to clips page
            self.driver.get("https://www.clipscutter.com/clips")
            time.sleep(1.5)  # Reduced from 3 to 1.5
            
            # Find all download buttons/links
            download_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'download') or contains(text(), 'Download')] | //button[contains(text(), 'Download')]")
            
            logger.info(f"Found {len(download_elements)} clips to download")
            
            for i, element in enumerate(download_elements, 1):
                try:
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    
                    # Click download
                    element.click()
                    logger.info(f"Started download {i}/{len(download_elements)}")
                    
                    # Wait between downloads to avoid overwhelming the server
                    time.sleep(1.5)  # Reduced from 3 to 1.5
                    
                except Exception as e:
                    logger.error(f"Failed to download clip {i}: {e}")
                    continue
            
            logger.info("Completed downloading all clips")
            
        except Exception as e:
            logger.error(f"Error during clip download process: {e}")
            raise
    
    def run_automation(self, csv_path: str) -> None:
        """
        Main method to run the complete automation process
        
        Args:
            csv_path (str): Path to the CSV file with clip data
        """
        try:
            logger.info("Starting ClipScutter automation...")
            
            # Setup
            self.setup_driver()
            
            # Read and group clips
            clips = self.read_csv_file(csv_path)
            grouped_clips = self.group_clips_by_url(clips)
            
            # Navigate to ClipScutter and setup premium trial
            self.navigate_to_clipscutter()
            self.setup_premium_trial()
            
            # Process clips grouped by URL for efficiency
            for youtube_url, url_clips in grouped_clips.items():
                self.process_clips_for_url(youtube_url, url_clips)
            
            # Download all created clips
            self.download_all_clips()
            
            logger.info(f"Automation completed! Created {self.clips_created} clips total.")
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")

def main():
    """Main entry point"""
    try:
        # Initialize automation
        automation = ClipScutterAutomation(headless=False)  # Set to True for headless mode
        
        # Run the automation
        csv_path = "/Users/rahul/Desktop/FREELANCING/20$_clipcut/clip_ranges.csv"
        automation.run_automation(csv_path)
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())