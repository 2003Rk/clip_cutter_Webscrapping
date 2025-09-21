"""
Clip Downloader for ClipScutter Automation
==========================================

This module handles downloading all clips from the ClipScutter clips page.
This is the premium $20 feature that automatically downloads all created clips.

Author: Automated ClipScutter Bot
Version: 1.0
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
import time
import logging
import os
from typing import List, Dict, Optional
import requests
from urllib.parse import urlparse, urljoin
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ClipDownloader:
    """Automated clip downloader for ClipScutter"""
    
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait, download_dir: Optional[str] = None):
        """
        Initialize the clip downloader
        
        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
            download_dir: Directory to save downloads
        """
        self.driver = driver
        self.wait = wait
        self.download_dir = download_dir or "/Users/rahul/Desktop/FREELANCING/20$_clipcut/downloads"
        self.downloaded_clips = []
        self.failed_downloads = []
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        logger.info(f"Download directory: {self.download_dir}")
    
    def navigate_to_clips_page(self) -> bool:
        """
        Navigate to the clips page where all created clips are listed
        
        Returns:
            bool: True if navigation successful
        """
        try:
            clips_url = "https://www.clipscutter.com/clips"
            logger.info(f"Navigating to clips page: {clips_url}")
            
            self.driver.get(clips_url)
            
            # Wait for page to load
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1.5)  # Reduced from 3 to 1.5
            
            logger.info("Successfully navigated to clips page")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to clips page: {e}")
            return False
    
    def find_all_clip_elements(self) -> List[Dict]:
        """
        Find all clip elements on the clips page
        
        Returns:
            List[Dict]: List of clip information dictionaries
        """
        clips = []
        
        try:
            # Look for Material-UI download buttons with the specific class from your HTML
            logger.info("Looking for Material-UI download buttons...")
            
            # Primary selectors for your specific download buttons
            button_selectors = [
                # Your specific download button structure
                "//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]",
                "//button[contains(@class, 'MuiIconButton') and contains(@title, 'Download')]",
                "//button[contains(@class, 'MuiIconButton') and .//svg[contains(@viewBox, '24 24') and .//path[contains(@d, 'M8 10C8 7.79086')]]]",
                
                # Backup selectors for download buttons
                "//button[contains(@title, 'Download') or contains(@aria-label, 'Download')]",
                "//button[.//svg[.//path[contains(@d, 'download') or contains(@d, 'Download')]]]",
                "//button[contains(@class, 'downloadIcon')]",
                "//button[contains(@class, 'download')]",
                "*[contains(@class, 'cutterClipsListItem_action')]/button",
                
                # Fallback to three-dot menu buttons
                "//button[.//svg[@data-testid='MoreVertIcon']]",  # MoreVertIcon
                "//button[contains(@aria-label, 'more') or contains(@aria-label, 'More')]",  # aria-label
                "//button[.//svg[contains(@class, 'MoreVert')]]",  # Class name
                "//button[.//span[text()='⋮']]",  # Unicode three dots
                "//button[.//span[contains(text(), '...')]]",  # Text three dots
                "//*[@role='button'][.//svg[@data-testid='MoreVertIcon']]",  # Any role=button element
                "//div[@role='button'][.//svg[@data-testid='MoreVertIcon']]",  # Div with role=button
                "//button[contains(@class, 'MuiIconButton') and .//svg]",  # Material-UI IconButton
                "//button[.//svg[contains(@viewBox, '24') and contains(., 'M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z')]]",  # SVG path for more vert
                "//button[.//svg/path[contains(@d, 'M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z')]]",  # Direct path match
                # Look for any button near download-related text
                "//button[ancestor::*[contains(text(), 'download') or contains(text(), 'Download')]]",
                "//button[following-sibling::*[contains(text(), 'download')] or preceding-sibling::*[contains(text(), 'download')]]"
            ]
            
            download_buttons = []
            
            # Try each selector
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    if buttons:
                        logger.info(f"Found {len(buttons)} buttons with selector: {selector}")
                        download_buttons.extend(buttons)
                        # If we found buttons with the primary download selector, prioritize them
                        if "cutterClipsListItem_downloadIcon" in selector:
                            logger.info("✅ Found ClipScutter-specific download buttons!")
                            break
                except Exception as e:
                    logger.debug(f"Selector failed: {selector} - {e}")
            
            # Remove duplicates based on element reference
            unique_buttons = []
            for button in download_buttons:
                if button not in unique_buttons:
                    unique_buttons.append(button)
            
            more_buttons = unique_buttons
            
            if more_buttons:
                logger.info(f"Found {len(more_buttons)} unique three-dot menu buttons")
                
                for index, button in enumerate(more_buttons, 1):
                    try:
                        # Create clip info for this menu button
                        clip_info = {
                            'index': index,
                            'title': f"Clip_{index}",
                            'download_button': button,
                            'download_url': None,
                            'menu_type': 'material_ui_dropdown'
                        }
                        clips.append(clip_info)
                        logger.info(f"Added clip {index} with Material-UI three-dot menu")
                        
                    except Exception as e:
                        logger.error(f"Failed to process three-dot menu {index}: {e}")
                        continue
                        
                return clips
            
            # Fallback: Multiple strategies to find clip elements
            logger.info("No Material-UI menus found, trying fallback methods...")
            clip_selectors = [
                "//div[contains(@class, 'clip')]",
                "//div[contains(@class, 'video')]",
                "//div[contains(@class, 'item')]",
                "//article",
                "//div[.//a[contains(@href, 'download')]]",
                "//div[.//button[contains(text(), 'Download')]]"
            ]
            
            clip_elements = []
            for selector in clip_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        clip_elements = elements
                        logger.info(f"Found {len(elements)} clip elements using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not clip_elements:
                logger.warning("No clip elements found on the page")
                return clips
            
            # Extract information from each clip element
            for i, element in enumerate(clip_elements):
                try:
                    clip_info = self.extract_clip_info(element, i + 1)
                    if clip_info:
                        clips.append(clip_info)
                except Exception as e:
                    logger.warning(f"Failed to extract info from clip {i + 1}: {e}")
                    continue
            
            logger.info(f"Successfully identified {len(clips)} clips for download")
            return clips
            
        except Exception as e:
            logger.error(f"Error finding clip elements: {e}")
            return clips
    
    def extract_clip_info(self, element: WebElement, index: int) -> Optional[Dict]:
        """
        Extract clip information from a clip element
        
        Args:
            element: WebElement containing clip information
            index: Clip index for naming
            
        Returns:
            Dict: Clip information or None if extraction fails
        """
        try:
            clip_info = {
                'index': index,
                'element': element,
                'title': f"clip_{index:03d}",
                'download_url': None,
                'download_button': None
            }
            
            # Try to find clip title/name
            title_selectors = [
                ".//h1 | .//h2 | .//h3 | .//h4",
                ".//*[contains(@class, 'title')]",
                ".//*[contains(@class, 'name')]",
                ".//span[contains(@class, 'clip')]"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = element.find_element(By.XPATH, selector)
                    title_text = title_element.text.strip()
                    if title_text:
                        # Clean title for filename
                        clean_title = "".join(c for c in title_text if c.isalnum() or c in (' ', '-', '_')).strip()
                        if clean_title:
                            clip_info['title'] = clean_title[:50]  # Limit length
                        break
                except Exception:
                    continue
            
            # Try to find download button or link
            download_selectors = [
                ".//a[contains(@href, 'download')]",
                ".//button[contains(text(), 'Download')]",
                ".//a[contains(text(), 'Download')]",
                ".//button[contains(@class, 'download')]",
                ".//a[contains(@class, 'download')]"
            ]
            
            for selector in download_selectors:
                try:
                    download_element = element.find_element(By.XPATH, selector)
                    
                    if download_element.tag_name == 'a':
                        href = download_element.get_attribute('href')
                        if href:
                            clip_info['download_url'] = href
                    
                    clip_info['download_button'] = download_element
                    break
                    
                except Exception:
                    continue
            
            if not clip_info['download_button'] and not clip_info['download_url']:
                logger.warning(f"No download option found for clip {index}")
                return None
            
            logger.debug(f"Extracted clip info: {clip_info['title']}")
            return clip_info
            
        except Exception as e:
            logger.error(f"Failed to extract clip info for element {index}: {e}")
            return None
    
    def download_clip_via_button(self, clip_info: Dict) -> bool:
        """
        Download clip by clicking the download button
        
        Args:
            clip_info: Clip information dictionary
            
        Returns:
            bool: True if download initiated successfully
        """
        try:
            logger.info(f"Downloading clip via button: {clip_info['title']}")
            
            # Check if this is a Material-UI dropdown menu
            if clip_info.get('menu_type') == 'material_ui_dropdown':
                return self.download_via_material_ui_menu(clip_info)
            
            # Original button click logic for other button types
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clip_info['download_button'])
            time.sleep(0.5)  # Reduced from 1 to 0.5
            
            # Click download button
            try:
                clip_info['download_button'].click()
            except Exception:
                # Try JavaScript click if regular click fails
                self.driver.execute_script("arguments[0].click();", clip_info['download_button'])
            
            logger.info(f"Clicked download button for: {clip_info['title']}")
            time.sleep(1)  # Reduced from 2 to 1 - Wait for download to start
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download clip via button: {e}")
            return False
    
    def download_via_material_ui_menu(self, clip_info: Dict) -> bool:
        """
        Download clip via Material-UI three-dot menu dropdown
        
        Args:
            clip_info: Clip information dictionary with menu button
            
        Returns:
            bool: True if download initiated successfully
        """
        try:
            menu_button = clip_info['download_button']
            logger.info(f"Opening Material-UI dropdown menu for: {clip_info['title']}")
            
            # Scroll menu button into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_button)
            time.sleep(0.3)
            
            # Click the three-dot menu button to open dropdown
            try:
                menu_button.click()
            except Exception:
                # Try JavaScript click if regular click fails
                self.driver.execute_script("arguments[0].click();", menu_button)
            
            logger.info("✅ Opened three-dot menu dropdown")
            time.sleep(0.5)  # Wait for menu to appear
            
            # Look for the download option in the dropdown menu
            download_selectors = [
                "//li[contains(@class, 'MuiMenuItem') and .//svg[@data-testid='DownloadIcon']]",
                "//li[contains(@class, 'MuiMenuItem') and contains(., 'Download')]",
                "//div[contains(@class, 'menu') and contains(., 'Download')]//li",
                "//li[@role='menuitem' and contains(., 'Download')]",
                "//*[@role='menuitem' and .//span[text()='Download']]"
            ]
            
            download_option = None
            for selector in download_selectors:
                try:
                    options = self.driver.find_elements(By.XPATH, selector)
                    for option in options:
                        if option.is_displayed():
                            download_option = option
                            break
                    if download_option:
                        break
                except Exception:
                    continue
            
            if download_option:
                logger.info("🎯 Found download option in dropdown menu")
                
                # Click the download option
                try:
                    download_option.click()
                except Exception:
                    # Try JavaScript click if regular click fails
                    self.driver.execute_script("arguments[0].click();", download_option)
                
                logger.info(f"✅ Clicked download option for: {clip_info['title']}")
                time.sleep(1)  # Wait for download to start
                
                return True
            else:
                logger.error("❌ Could not find download option in dropdown menu")
                
                # Try to close the menu by clicking elsewhere
                try:
                    self.driver.find_element(By.TAG_NAME, "body").click()
                except Exception:
                    pass
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to download via Material-UI menu: {e}")
            
            # Try to close any open menus
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except Exception:
                pass
            
            return False
    
    def download_clip_via_url(self, clip_info: Dict) -> bool:
        """
        Download clip directly via URL using requests
        
        Args:
            clip_info: Clip information dictionary
            
        Returns:
            bool: True if download successful
        """
        try:
            if not clip_info['download_url']:
                return False
            
            logger.info(f"Downloading clip via URL: {clip_info['title']}")
            
            # Get cookies from browser for authenticated download
            cookies = self.driver.get_cookies()
            session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # Download the file
            response = requests.get(
                clip_info['download_url'],
                cookies=session_cookies,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            # Determine file extension from Content-Type or URL
            content_type = response.headers.get('content-type', '')
            if 'video/mp4' in content_type:
                extension = '.mp4'
            elif 'video/webm' in content_type:
                extension = '.webm'
            elif 'video/avi' in content_type:
                extension = '.avi'
            else:
                # Try to get extension from URL
                parsed_url = urlparse(clip_info['download_url'])
                path = Path(parsed_url.path)
                extension = path.suffix if path.suffix else '.mp4'
            
            # Create filename
            filename = f"{clip_info['title']}{extension}"
            filepath = os.path.join(self.download_dir, filename)
            
            # Ensure unique filename
            counter = 1
            while os.path.exists(filepath):
                base_name = f"{clip_info['title']}_{counter}"
                filename = f"{base_name}{extension}"
                filepath = os.path.join(self.download_dir, filename)
                counter += 1
            
            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download clip via URL: {e}")
            return False
    
    def download_all_clips(self) -> Dict:
        """
        Download all clips from the clips page
        
        Returns:
            Dict: Download results summary
        """
        try:
            logger.info("Starting bulk clip download process...")
            
            # Navigate to clips page
            if not self.navigate_to_clips_page():
                return {"success": False, "error": "Failed to navigate to clips page"}
            
            # Find all clips
            clips = self.find_all_clip_elements()
            
            if not clips:
                logger.warning("No clips found to download")
                return {"success": True, "total_clips": 0, "downloaded": 0, "failed": 0}
            
            logger.info(f"Found {len(clips)} clips to download")
            
            # Download each clip
            downloaded_count = 0
            failed_count = 0
            
            for clip_info in clips:
                try:
                    logger.info(f"Processing clip {clip_info['index']}/{len(clips)}: {clip_info['title']}")
                    
                    # Try button download first, then URL download
                    success = False
                    
                    if clip_info['download_button']:
                        success = self.download_clip_via_button(clip_info)
                        
                        if success:
                            downloaded_count += 1
                            self.downloaded_clips.append(clip_info['title'])
                        else:
                            # If button download failed, try URL download
                            if clip_info['download_url']:
                                success = self.download_clip_via_url(clip_info)
                                if success:
                                    downloaded_count += 1
                                    self.downloaded_clips.append(clip_info['title'])
                    
                    elif clip_info['download_url']:
                        success = self.download_clip_via_url(clip_info)
                        if success:
                            downloaded_count += 1
                            self.downloaded_clips.append(clip_info['title'])
                    
                    if not success:
                        failed_count += 1
                        self.failed_downloads.append(clip_info['title'])
                        logger.error(f"Failed to download clip: {clip_info['title']}")
                    
                    # Wait between downloads to avoid overwhelming the server
                    time.sleep(3)
                    
                except Exception as e:
                    failed_count += 1
                    self.failed_downloads.append(clip_info.get('title', f'clip_{clip_info["index"]}'))
                    logger.error(f"Error downloading clip {clip_info['index']}: {e}")
                    continue
            
            # Save download report
            self.save_download_report(len(clips), downloaded_count, failed_count)
            
            result = {
                "success": True,
                "total_clips": len(clips),
                "downloaded": downloaded_count,
                "failed": failed_count,
                "downloaded_clips": self.downloaded_clips,
                "failed_clips": self.failed_downloads
            }
            
            logger.info(f"Download process completed: {downloaded_count}/{len(clips)} clips downloaded successfully")
            return result
            
        except Exception as e:
            logger.error(f"Bulk download process failed: {e}")
            return {"success": False, "error": str(e)}
    
    def save_download_report(self, total: int, downloaded: int, failed: int) -> None:
        """
        Save a download report to file
        
        Args:
            total: Total number of clips
            downloaded: Number of successfully downloaded clips
            failed: Number of failed downloads
        """
        try:
            report = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_clips": total,
                "downloaded_successfully": downloaded,
                "failed_downloads": failed,
                "success_rate": f"{(downloaded/total*100):.1f}%" if total > 0 else "0%",
                "downloaded_clips": self.downloaded_clips,
                "failed_clips": self.failed_downloads,
                "download_directory": self.download_dir
            }
            
            report_path = os.path.join(self.download_dir, "download_report.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Download report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save download report: {e}")
    
    def fast_download_latest_clip(self) -> bool:
        """
        Fast download method for the latest clip using optimized selectors
        Designed for immediate use after clip creation
        
        Returns:
            bool: True if download initiated successfully
        """
        try:
            logger.info("Attempting to download the latest clip...")
            
            # Ultra-fast selector based on your exact HTML structure
            fast_selectors = [
                # Exact class from your HTML
                "//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]",
                # CSS equivalent for speed
                "button.cutterClipsListItem_downloadIcon__gik8o",
                # Backup with title attribute
                "//button[@title='Download' and contains(@class, 'MuiIconButton-root')]"
            ]
            
            for i, selector in enumerate(fast_selectors):
                try:
                    logger.info(f"Trying fast selector {i+1}: {selector[:50]}...")
                    
                    if selector.startswith('//'):
                        # XPath selector
                        download_buttons = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector 
                        download_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if download_buttons:
                        logger.info(f"Found {len(download_buttons)} download buttons with fast selector")
                        
                        # Get the first (latest) download button
                        latest_button = download_buttons[0]
                        
                        logger.info("Found working download button with fast selector")
                        logger.info("Attempting to click download button...")
                        
                        # Quick scroll into view
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", latest_button)
                        time.sleep(0.2)  # Minimal wait
                        
                        # Try direct click first
                        try:
                            latest_button.click()
                            logger.info("Successfully clicked download button (direct click)")
                        except Exception:
                            # Fallback to JavaScript click
                            self.driver.execute_script("arguments[0].click();", latest_button)
                            logger.info("Successfully clicked download button (JavaScript click)")
                        
                        logger.info("Download should start - waiting for download to begin...")
                        time.sleep(0.5)  # Minimal wait for download to start
                        
                        logger.info("Clip downloaded successfully!")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Fast selector {i+1} failed: {e}")
                    continue
            
            logger.error("All fast selectors failed")
            return False
            
        except Exception as e:
            logger.error(f"Fast download method failed: {e}")
            return False
    
    def clean_filename(self, filename: str) -> str:
        """
        Clean filename for cross-platform compatibility
        
        Args:
            filename: Original filename
            
        Returns:
            str: Cleaned filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip()

def main():
    """Test the clip downloader"""
    # This would normally be called from the main automation script
    # Here for testing purposes only
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Download preferences
    download_dir = "/Users/rahul/Desktop/FREELANCING/20$_clipcut/downloads"
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        # Use webdriver-manager for ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        # Test the downloader
        downloader = ClipDownloader(driver, wait, download_dir)
        result = downloader.download_all_clips()
        
        logger.info(f"Test download result: {result}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()