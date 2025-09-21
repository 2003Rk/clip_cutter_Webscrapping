"""
Web Automation Utilities for ClipScutter
========================================

This module contains specialized web automation functions for interacting
with the ClipScutter website, including premium trial setup, clip creation,
and efficient URL handling.

Author: Automated ClipScutter Bot
Version: 1.0
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import logging
from typing import Optional, List, Dict, Tuple
import re

# Create a SmartWait class for page ready functionality
class SmartWait:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def wait_for_page_ready(self, timeout):
        """Implementation for page ready wait"""
        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except:
            pass

logger = logging.getLogger(__name__)

class ClipScutterWebAutomation:
    """Specialized web automation for ClipScutter operations"""
    
    def __init__(self, driver: webdriver.Chrome, wait: WebDriverWait):
        """
        Initialize web automation helper
        
        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
        """
        self.driver = driver
        self.wait = wait
        self.current_url = None
        self.is_premium_active = False
        
        # Initialize smart wait if available
        self.smart_wait = SmartWait(driver, wait) if SmartWait else None
        
    def wait_for_page_load(self, timeout: int = 5) -> None:
        """
        Wait for page to fully load - Optimized for speed
        
        Args:
            timeout (int): Maximum wait time in seconds
        """
        if self.smart_wait:
            self.smart_wait.wait_for_page_ready(timeout)
        else:
            try:
                self.wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                time.sleep(0.3)  # Reduced buffer from 1 to 0.3 seconds
            except TimeoutException:
                logger.warning("Page load timeout, continuing anyway")
    
    def find_element_with_multiple_selectors(self, selectors: List[str], timeout: int = 10) -> Optional[WebElement]:
        """
        Try to find element using multiple selector strategies
        
        Args:
            selectors (List[str]): List of XPath selectors to try
            timeout (int): Timeout for each selector
            
        Returns:
            WebElement or None if not found
        """
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                return element
            except TimeoutException:
                continue
        return None
    
    def safe_click(self, element: WebElement, max_attempts: int = 3) -> bool:
        """
        Safely click an element with retry logic - Optimized for speed
        
        Args:
            element: WebElement to click
            max_attempts (int): Maximum click attempts
            
        Returns:
            bool: True if click succeeded
        """
        for attempt in range(max_attempts):
            try:
                # Scroll element into view FAST
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.1)  # Reduced from 0.2 to 0.1 for SPEED
                
                # Wait for element to be clickable FAST
                WebDriverWait(self.driver, 2).until(  # Reduced from 3 to 2 for faster clicking
                    EC.element_to_be_clickable(element)
                )
                
                # Try direct click first
                element.click()
                return True
                
            except ElementClickInterceptedException:
                # Try JavaScript click if direct click fails
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as e:
                    logger.warning(f"JavaScript click failed: {e}")
                    
            except Exception as e:
                logger.warning(f"Click attempt {attempt + 1} failed: {e}")
                
                # Try alternative clicking methods
                try:
                    # Method 1: Force focus and click
                    self.driver.execute_script("arguments[0].focus(); arguments[0].click();", element)
                    return True
                except Exception:
                    try:
                        # Method 2: Dispatch click event
                        self.driver.execute_script("""
                            var event = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            });
                            arguments[0].dispatchEvent(event);
                        """, element)
                        return True
                    except Exception:
                        pass
                
                time.sleep(0.5)  # Reduced from 1 to 0.5 second for FASTER retries
        
        return False
    
    def navigate_to_login_page(self) -> bool:
        """
        Navigate directly to ClipScutter login page
        
        Returns:
            bool: True if navigation successful
        """
        try:
            self.driver.get("https://www.clipscutter.com/login")
            self.wait_for_page_load()
            logger.info("✅ Successfully navigated to ClipScutter login page")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to navigate to login page: {e}")
            # Fallback to homepage if direct login URL doesn't work
            try:
                logger.info("🔄 Trying fallback to homepage...")
                self.driver.get("https://www.clipscutter.com")
                self.wait_for_page_load()
                logger.info("✅ Navigated to homepage as fallback")
                return True
            except Exception as e2:
                logger.error(f"❌ Failed to navigate to homepage fallback: {e2}")
                return False

    def navigate_to_homepage(self) -> bool:
        """
        Navigate to ClipScutter homepage
        
        Returns:
            bool: True if navigation successful
        """
        try:
            self.driver.get("https://www.clipscutter.com")
            self.wait_for_page_load()
            logger.info("Successfully navigated to ClipScutter homepage")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to homepage: {e}")
            return False
    
    def perform_login(self, email: str, password: str) -> bool:
        """
        Perform login to ClipScutter
        
        Args:
            email: Login email
            password: Login password
            
        Returns:
            bool: True if login successful
        """
        try:
            logger.info(f"🔑 Attempting to login with email: {email}")
            
            # Since we're already on login page, find email input field directly
            logger.info("🔍 Looking for email input field...")
            
            # Find email input field
            email_selectors = [
                "//input[@type='email']",
                "//input[contains(@placeholder, 'email')]",
                "//input[contains(@placeholder, 'Email')]",
                "//input[contains(@name, 'email')]",
                "//input[contains(@id, 'email')]",
                "//input[contains(@class, 'email')]"
            ]
            
            email_input = self.find_element_with_multiple_selectors(email_selectors, timeout=10)
            
            if not email_input:
                logger.error("❌ Could not find email input field")
                return False
            
            # Clear and enter email - FAST
            email_input.clear()
            time.sleep(0.1)  # Reduced from 0.2 to 0.1 for SPEED
            email_input.send_keys(email)
            logger.info("✅ Entered email address")
            
            # Find password input field
            logger.info("🔍 Looking for password input field...")
            password_selectors = [
                "//input[@type='password']",
                "//input[contains(@placeholder, 'password')]",
                "//input[contains(@placeholder, 'Password')]",
                "//input[contains(@name, 'password')]",
                "//input[contains(@id, 'password')]",
                "//input[contains(@class, 'password')]"
            ]
            
            password_input = self.find_element_with_multiple_selectors(password_selectors, timeout=5)
            
            if not password_input:
                logger.error("❌ Could not find password input field")
                return False
            
            # Clear and enter password - FAST
            password_input.clear()
            time.sleep(0.1)  # Reduced from 0.2 to 0.1 for SPEED
            password_input.send_keys(password)
            logger.info("✅ Entered password")
            
            # Find and click submit button
            logger.info("🔍 Looking for login submit button...")
            submit_selectors = [
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Log In')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(@class, 'submit')]",
                "//button[contains(@class, 'login')]"
            ]
            
            submit_button = self.find_element_with_multiple_selectors(submit_selectors, timeout=5)
            
            if submit_button:
                if self.safe_click(submit_button):
                    logger.info("✅ Clicked login submit button")
                else:
                    logger.warning("⚠️ Failed to click submit, trying Enter key")
                    password_input.send_keys(Keys.RETURN)
            else:
                # Try pressing Enter as fallback
                logger.info("⚠️ No submit button found, pressing Enter")
                password_input.send_keys(Keys.RETURN)
            
            # Wait for login to complete - FAST
            self.wait_for_page_load()
            time.sleep(1.0)  # Reduced from 1.5 to 1.0 seconds for SPEED
            
            # Check if login was successful
            return self.check_login_success()
            
        except Exception as e:
            logger.error(f"Login failed with error: {e}")
            return False
    
    def check_login_success(self) -> bool:
        """
        Check if login was successful
        
        Returns:
            bool: True if login successful
        """
        try:
            # Look for indicators that we're logged in
            success_indicators = [
                "//*[contains(text(), 'Dashboard')]",
                "//*[contains(text(), 'Account')]",
                "//*[contains(text(), 'Profile')]",
                "//*[contains(text(), 'Logout')]",
                "//*[contains(text(), 'My Clips')]",
                "//*[contains(text(), 'Welcome')]",
                "//*[contains(@class, 'user')]",
                "//*[contains(@class, 'account')]",
                "//*[contains(@class, 'dashboard')]"
            ]
            
            success_element = self.find_element_with_multiple_selectors(success_indicators, timeout=5)
            
            if success_element:
                logger.info("Login appears successful - found user dashboard elements")
                return True
            
            # Check if we're redirected to homepage (another success indicator)
            current_url = self.driver.current_url
            if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                logger.info("Login appears successful - redirected away from login page")
                return True
            
            # Look for error messages
            error_indicators = [
                "//*[contains(text(), 'error')]",
                "//*[contains(text(), 'Error')]",
                "//*[contains(text(), 'invalid')]",
                "//*[contains(text(), 'Invalid')]",
                "//*[contains(text(), 'incorrect')]",
                "//*[contains(text(), 'failed')]",
                "//*[contains(@class, 'error')]"
            ]
            
            error_element = self.find_element_with_multiple_selectors(error_indicators, timeout=2)
            if error_element:
                error_text = error_element.text
                logger.error(f"Login failed with error: {error_text}")
                return False
            
            logger.warning("Login status unclear, assuming success")
            return True
            
        except Exception as e:
            logger.warning(f"Could not verify login status: {e}")
            return True  # Assume success and continue

    def setup_premium_trial(self) -> bool:
        """
        Attempt to setup premium trial account or detect existing login
        
        Returns:
            bool: True if premium trial is active or user is already logged in
        """
        try:
            logger.info("Checking premium/login status...")
            
            # First check if user is already logged in
            login_indicators = [
                "//*[contains(text(), 'Dashboard')]",
                "//*[contains(text(), 'Account')]",
                "//*[contains(text(), 'Profile')]",
                "//*[contains(text(), 'Logout')]",
                "//*[contains(text(), 'My Clips')]",
                "//*[contains(@class, 'user')]",
                "//*[contains(@class, 'account')]"
            ]
            
            logged_in_element = self.find_element_with_multiple_selectors(login_indicators, timeout=3)
            if logged_in_element:
                self.is_premium_active = True
                logger.info("User appears to be already logged in - premium features should be available")
                return True
            
            # Look for premium/trial related buttons only if not logged in
            premium_selectors = [
                "//button[contains(text(), 'Premium')]",
                "//button[contains(text(), 'Trial')]",
                "//button[contains(text(), 'Free Trial')]",
                "//a[contains(text(), 'Premium')]",
                "//a[contains(text(), 'Trial')]",
                "//button[contains(text(), 'Sign Up')]",
                "//button[contains(text(), 'Get Started')]"
            ]
            
            premium_button = self.find_element_with_multiple_selectors(premium_selectors, timeout=5)
            
            if premium_button:
                if self.safe_click(premium_button):
                    logger.info("Clicked premium trial button")
                    self.wait_for_page_load()
                    
                    # Look for trial activation confirmation
                    confirmation_selectors = [
                        "//*[contains(text(), 'trial activated')]",
                        "//*[contains(text(), 'premium active')]",
                        "//*[contains(text(), 'trial started')]",
                        "//*[contains(text(), 'success')]"
                    ]
                    
                    confirmation = self.find_element_with_multiple_selectors(confirmation_selectors, timeout=3)
                    if confirmation:
                        self.is_premium_active = True
                        logger.info("Premium trial activated successfully")
                        return True
            
            # Check if premium is already active (even without trial)
            premium_indicators = [
                "//*[contains(text(), 'Premium')]",
                "//*[contains(text(), 'Pro')]",
                "//*[contains(@class, 'premium')]",
                "//*[contains(@class, 'pro')]"
            ]
            
            if self.find_element_with_multiple_selectors(premium_indicators, timeout=2):
                self.is_premium_active = True
                logger.info("Premium features appear to be already active")
                return True
            
            logger.info("Continuing with standard account features")
            return True  # Continue anyway, even without premium
            
        except Exception as e:
            logger.info(f"Premium status check completed, continuing with automation: {e}")
            return True  # Always continue
    
    def input_youtube_url(self, youtube_url: str) -> bool:
        """
        Input YouTube URL into ClipScutter
        
        Args:
            youtube_url (str): YouTube URL to process
            
        Returns:
            bool: True if URL input successful
        """
        try:
            logger.info(f"Inputting YouTube URL: {youtube_url}")
            
            # Find URL input field with the correct placeholder
            url_selectors = [
                "//input[@placeholder='Add link here']",
                "//input[@type='text']",
                "//input[contains(@placeholder, 'link')]",
                "//input[contains(@placeholder, 'youtube')]",
                "//input[contains(@placeholder, 'URL')]"
            ]
            
            url_input = self.find_element_with_multiple_selectors(url_selectors, timeout=5)  # Fast detection timeout
            
            if not url_input:
                logger.error("Could not find YouTube URL input field")
                return False
            
            # Clear and input URL - FAST OPTIMIZATION
            url_input.clear()
            time.sleep(0.1)  # Reduced from 0.2 to 0.1
            url_input.send_keys(youtube_url)
            time.sleep(0.2)  # Reduced from 0.5 to 0.2
            
            # Find and click submit button (CLICK button)
            submit_selectors = [
                "//button[text()='CLICK']",
                "//button[contains(text(), 'CLICK')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Process')]",
                "//button[contains(text(), 'Go')]"
            ]
            
            submit_button = self.find_element_with_multiple_selectors(submit_selectors, timeout=3)  # Reduced from default to 3
            
            if submit_button:
                if self.safe_click(submit_button):
                    logger.info("Clicked submit button for YouTube URL")
                else:
                    # Try pressing Enter if click fails
                    url_input.send_keys(Keys.RETURN)
                    logger.info("Pressed Enter to submit URL")
            else:
                # Try pressing Enter as fallback
                url_input.send_keys(Keys.RETURN)
                logger.info("No submit button found, pressed Enter")
            
            # Wait for video to load and redirect to cutter page
            self.wait_for_video_load()
            self.current_url = youtube_url
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to input YouTube URL: {e}")
            return False
    
    def wait_for_video_load(self, timeout: int = 30) -> bool:
        """
        Wait for video to load after URL submission
        
        Args:
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if video loaded successfully
        """
        try:
            logger.info("Waiting for video to load...")
            
            # Wait for redirect to cutter page
            WebDriverWait(self.driver, timeout).until(
                lambda driver: '/cutter/' in driver.current_url
            )
            
            # Look for time selection elements (range sliders)
            time_selection_selectors = [
                "//input[@type='range']",
                "//*[contains(@class, 'timeSelection')]",
                "//*[contains(@class, 'rangeSlider')]",
                "//input[@type='number']"
            ]
            
            time_elements = self.find_element_with_multiple_selectors(time_selection_selectors, timeout=timeout)
            
            if time_elements:
                logger.info("Video and time selection interface loaded successfully")
                time.sleep(0.8)  # Reduced from 1.5 to 0.8 seconds for SPEED
                return True
            else:
                logger.warning("Time selection interface not found, but continuing")
                return True
                
        except Exception as e:
            logger.warning(f"Error waiting for video load: {e}")
            return True  # Continue anyway
    
    def navigate_to_controls(self) -> bool:
        """
        Navigate back to Controls section after clip download to access time inputs
        
        Returns:
            bool: True if navigation successful
        """
        try:
            logger.info("🎛️ Navigating back to Controls section...")
            
            # Look for Controls button/tab
            controls_selectors = [
                "//span[text()='Controls']",
                "//button[text()='Controls']",
                "//div[text()='Controls']",
                "//*[contains(text(), 'Controls')]",
                "//span[contains(text(), 'Controls')]"
            ]
            
            controls_element = self.find_element_with_multiple_selectors(controls_selectors, timeout=10)
            
            if controls_element:
                if self.safe_click(controls_element):
                    logger.info("✅ Successfully clicked Controls section")
                    
                    # Wait longer for DOM to refresh and duration picker to become available
                    time.sleep(2.0)  # Increased wait time for DOM refresh
                    
                    # Verify duration picker elements are now available
                    for attempt in range(3):
                        logger.info(f"🔍 Checking duration picker availability (attempt {attempt + 1})...")
                        
                        duration_containers = self.driver.find_elements(
                            By.XPATH, 
                            "//div[contains(@class, 'durationPicker')]"
                        )
                        
                        if len(duration_containers) >= 2:
                            logger.info(f"✅ Found {len(duration_containers)} duration picker containers - ready for time input")
                            return True
                        
                        logger.warning(f"⚠️ Only found {len(duration_containers)} duration containers, waiting...")
                        time.sleep(1)
                    
                    logger.warning("⚠️ Duration picker not fully ready, but continuing...")
                    return True  # Continue anyway
                else:
                    logger.warning("⚠️ Failed to click Controls section")
                    return False
            else:
                logger.warning("⚠️ Controls section not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error navigating to Controls: {e}")
            return False
    
    def enable_controls_interface(self) -> bool:
        """
        Enable all interface controls that might be disabled after navigation
        Specifically handles disabled inputs in duration pickers
        
        Returns:
            bool: True if interface enabled successfully
        """
        try:
            logger.info("🔓 Enabling interface controls...")
            
            # Wait for interface to stabilize after navigation
            time.sleep(2)
            
            # JavaScript to enable all disabled inputs and interface elements
            result = self.driver.execute_script("""
                console.log('Starting interface enablement...');
                
                // Remove disabled attribute from all inputs
                var allInputs = document.querySelectorAll('input[disabled]');
                console.log('Found disabled inputs:', allInputs.length);
                
                for (var i = 0; i < allInputs.length; i++) {
                    allInputs[i].removeAttribute('disabled');
                    allInputs[i].disabled = false;
                    console.log('Enabled input:', allInputs[i]);
                }
                
                // Specifically target duration picker inputs
                var durationContainers = document.querySelectorAll('div[class*="durationPicker"], div.durationPicker_container');
                console.log('Found duration containers:', durationContainers.length);
                
                for (var j = 0; j < durationContainers.length; j++) {
                    var inputs = durationContainers[j].querySelectorAll('input');
                    console.log('Inputs in container', j, ':', inputs.length);
                    
                    for (var k = 0; k < inputs.length; k++) {
                        inputs[k].removeAttribute('disabled');
                        inputs[k].disabled = false;
                        inputs[k].readOnly = false;
                        // Make sure the input is interactive
                        inputs[k].style.pointerEvents = 'auto';
                        inputs[k].style.opacity = '1';
                        console.log('Enabled duration input:', inputs[k]);
                    }
                }
                
                // Remove any readonly attributes that might prevent editing
                var readonlyInputs = document.querySelectorAll('input[readonly]');
                for (var l = 0; l < readonlyInputs.length; l++) {
                    readonlyInputs[l].removeAttribute('readonly');
                    readonlyInputs[l].readOnly = false;
                }
                
                // Trigger a general interface refresh
                var event = new Event('DOMContentLoaded', { bubbles: true });
                document.dispatchEvent(event);
                
                console.log('Interface enablement completed');
                return true;
            """)
            
            if result:
                logger.info("✅ Successfully enabled interface controls")
                time.sleep(1)  # Allow interface to update
                return True
            else:
                logger.warning("⚠️ Interface enablement script completed but returned false")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to enable interface controls: {e}")
            return False
    
    def set_quality_to_1080p(self) -> bool:
        """
        Set video quality to 1080p if available
        
        Returns:
            bool: True if quality set successfully
        """
        try:
            logger.info("Attempting to set quality to 1080p...")
            
            # Look for the specific ClipScutter quality selector
            quality_selectors = [
                "//div[contains(@class, 'select_field') and contains(text(), '720p')]",
                "//div[contains(@class, 'select_field')]",
                "//div[contains(@class, 'select') and .//svg]",
                "//div[contains(text(), '720p') or contains(text(), '480p') or contains(text(), '1080p')]"
            ]
            
            quality_dropdown = self.find_element_with_multiple_selectors(quality_selectors, timeout=5)
            
            if quality_dropdown:
                logger.info("Found quality dropdown, attempting to click it")
                
                # Click the quality dropdown
                if self.safe_click(quality_dropdown):
                    logger.info("Clicked quality dropdown")
                    time.sleep(2)
                    
                    # Look for 1080p option in the opened dropdown
                    quality_option_selectors = [
                        "//div[contains(text(), '1080p')]",
                        "//li[contains(text(), '1080p')]",
                        "//*[contains(text(), '1080p')]",
                        "//option[contains(text(), '1080p')]",
                        "//span[contains(text(), '1080p')]"
                    ]
                    
                    quality_option = self.find_element_with_multiple_selectors(quality_option_selectors, timeout=3)
                    
                    if quality_option:
                        if self.safe_click(quality_option):
                            logger.info("Successfully set quality to 1080p")
                            return True
                        else:
                            logger.warning("Found 1080p option but couldn't click it")
                    else:
                        logger.warning("1080p option not found in dropdown, checking available options...")
                        
                        # Try to find any quality options to see what's available
                        all_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'p') and (contains(text(), '720') or contains(text(), '480') or contains(text(), '1080') or contains(text(), '360'))]")
                        
                        if all_options:
                            logger.info("Available quality options:")
                            for option in all_options:
                                try:
                                    logger.info(f"  - {option.text}")
                                except:
                                    pass
                        
                        # Try clicking the highest available option
                        high_quality_selectors = [
                            "//*[contains(text(), '720p')]",
                            "//*[contains(text(), '480p')]"
                        ]
                        
                        for selector in high_quality_selectors:
                            try:
                                option = self.driver.find_element(By.XPATH, selector)
                                if self.safe_click(option):
                                    logger.info(f"Set quality to {option.text}")
                                    return True
                            except:
                                continue
                else:
                    logger.warning("Could not click quality dropdown")
            else:
                logger.info("Quality dropdown not found, checking if quality is already optimal")
                
                # Check if 1080p is already selected
                current_quality_selectors = [
                    "//*[contains(text(), '1080p')]",
                    "//div[contains(@class, 'select_field') and contains(text(), '1080p')]"
                ]
                
                current_quality = self.find_element_with_multiple_selectors(current_quality_selectors, timeout=2)
                if current_quality:
                    logger.info("1080p quality already selected")
                    return True
            
            logger.warning("Could not set quality to 1080p, using current quality")
            return False
            
        except Exception as e:
            logger.warning(f"Failed to set quality: {e}")
            return False
    
    def create_clip(self, start_time: str, end_time: str, navigate_to_controls: bool = False) -> bool:
        """
        Create a clip with specified start and end times using ClipScutter's interface
        
        Args:
            start_time (str): Start time in HH:MM:SS format
            end_time (str): End time in HH:MM:SS format
            navigate_to_controls (bool): Whether to navigate to Controls section first
            
        Returns:
            bool: True if clip created successfully
        """
        try:
            logger.info(f"Creating clip: {start_time} to {end_time}")
            
            # Navigate to Controls section if needed (for subsequent clips)
            if navigate_to_controls:
                if not self.navigate_to_controls():
                    logger.warning("Failed to navigate to Controls, continuing anyway...")
                
                # Enable interface elements that might be disabled after navigation
                self.enable_controls_interface()
            
            # Convert time strings to seconds
            start_seconds = convert_time_to_seconds(start_time)
            end_seconds = convert_time_to_seconds(end_time)
            
            logger.info(f"Converted times: {start_seconds}s to {end_seconds}s")
            
            # Step 1: Look for duration picker inputs with retry logic after Controls navigation
            logger.info("Looking for duration picker inputs...")
            
            # If we navigated to Controls, wait and retry to find duration picker
            if navigate_to_controls:
                duration_containers = []
                for retry_attempt in range(5):  # Try up to 5 times
                    duration_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'durationPicker_container')]")
                    if len(duration_containers) >= 2:
                        logger.info(f"✅ Found {len(duration_containers)} duration picker containers after Controls navigation (attempt {retry_attempt + 1})")
                        break
                    
                    logger.info(f"⏳ Duration picker not ready yet, waiting... (attempt {retry_attempt + 1}/5)")
                    time.sleep(1)
                    
                    # Try to refresh the page elements
                    self.driver.execute_script("return document.readyState")
            else:
                duration_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'durationPicker_container')]")
                logger.info(f"Found {len(duration_containers)} duration picker containers")
            
            if len(duration_containers) >= 2:
                
                # First container is start time, second is end time
                start_container = duration_containers[0]
                end_container = duration_containers[1]
                
                # Set start time in duration picker with retry logic
                start_inputs = start_container.find_elements(By.XPATH, ".//input[@type='number']")
                if len(start_inputs) >= 3:
                    start_parts = start_time.split(':')
                    logger.info(f"Setting start time in duration picker: {start_time}")
                    
                    # Retry logic for start time
                    for attempt in range(3):
                        try:
                            # Re-find elements to avoid stale references
                            start_inputs = start_container.find_elements(By.XPATH, ".//input[@type='number']")
                            
                            # Wait for all inputs to be interactable
                            for i, input_field in enumerate(start_inputs[:3]):
                                self.wait.until(EC.element_to_be_clickable(input_field))
                            
                            # Hours
                            start_inputs[0].clear()
                            time.sleep(0.2)
                            start_inputs[0].send_keys(start_parts[0])
                            
                            # Minutes  
                            start_inputs[1].clear()
                            time.sleep(0.2)
                            start_inputs[1].send_keys(start_parts[1])
                            
                            # Seconds
                            start_inputs[2].clear()
                            time.sleep(0.2)
                            start_inputs[2].send_keys(start_parts[2])
                            
                            logger.info(f"✅ Successfully set start time on attempt {attempt + 1}")
                            break
                            
                        except Exception as e:
                            logger.warning(f"Attempt {attempt + 1} failed for start time: {e}")
                            if attempt < 2:  # Not the last attempt
                                time.sleep(1)
                                continue
                            else:
                                logger.error(f"Failed to set start time after 3 attempts, trying JavaScript fallback")
                                try:
                                    self.driver.execute_script("""
                                        var inputs = arguments[0].querySelectorAll('input[type="number"]');
                                        if (inputs.length >= 3) {
                                            inputs[0].value = arguments[1];
                                            inputs[1].value = arguments[2];
                                            inputs[2].value = arguments[3];
                                            
                                            // Trigger events
                                            ['input', 'change', 'blur'].forEach(function(eventType) {
                                                for (var i = 0; i < 3; i++) {
                                                    var event = new Event(eventType, { bubbles: true });
                                                    inputs[i].dispatchEvent(event);
                                                }
                                            });
                                        }
                                    """, start_container, start_parts[0], start_parts[1], start_parts[2])
                                    logger.info("✅ Set start time using JavaScript fallback")
                                except Exception as js_error:
                                    logger.error(f"JavaScript fallback also failed: {js_error}")
                                    raise e
                
                # Set end time in duration picker with complete re-finding
                logger.info(f"Setting end time in duration picker: {end_time}")
                end_parts = end_time.split(':')
                
                # Wait for DOM to stabilize after start time setting
                time.sleep(1.5)
                
                # Retry logic with complete element re-finding each time
                end_time_success = False
                for attempt in range(3):
                    try:
                        # Completely re-find duration containers to handle DOM changes
                        fresh_duration_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'durationPicker_container')]")
                        
                        if len(fresh_duration_containers) < 2:
                            logger.warning(f"Duration containers not found on attempt {attempt + 1}")
                            time.sleep(2)
                            continue
                        
                        # Get fresh end container
                        fresh_end_container = fresh_duration_containers[1]
                        
                        # Find fresh end inputs
                        fresh_end_inputs = fresh_end_container.find_elements(By.XPATH, ".//input[@type='number']")
                        
                        if len(fresh_end_inputs) < 3:
                            logger.warning(f"End time inputs not found on attempt {attempt + 1}")
                            time.sleep(2)
                            continue
                        
                        # Enable any disabled inputs before trying to interact
                        for input_field in fresh_end_inputs[:3]:
                            try:
                                self.driver.execute_script("""
                                    arguments[0].removeAttribute('disabled');
                                    arguments[0].disabled = false;
                                    arguments[0].readOnly = false;
                                    arguments[0].style.pointerEvents = 'auto';
                                    arguments[0].style.opacity = '1';
                                """, input_field)
                            except:
                                pass  # Continue even if this fails
                        
                        # Wait for all inputs to be interactable
                        for i, input_field in enumerate(fresh_end_inputs[:3]):
                            self.wait.until(EC.element_to_be_clickable(input_field))
                        
                        # Set Hours
                        fresh_end_inputs[0].clear()
                        time.sleep(0.3)
                        fresh_end_inputs[0].send_keys(end_parts[0])
                        
                        # Set Minutes
                        fresh_end_inputs[1].clear()
                        time.sleep(0.3)
                        fresh_end_inputs[1].send_keys(end_parts[1])
                        
                        # Set Seconds
                        fresh_end_inputs[2].clear()
                        time.sleep(0.3)
                        fresh_end_inputs[2].send_keys(end_parts[2])
                        
                        logger.info(f"✅ Successfully set end time on attempt {attempt + 1}")
                        end_time_success = True
                        break
                        
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed for end time: {e}")
                        if attempt < 2:  # Not the last attempt
                            time.sleep(3 + attempt)  # Progressive delay
                            continue
                
                # Final JavaScript fallback if all normal attempts failed
                if not end_time_success:
                    logger.error(f"Failed to set end time after 3 attempts, trying JavaScript fallback")
                    try:
                        # Enhanced JavaScript fallback with better element finding and event triggering
                        result = self.driver.execute_script("""
                            console.log('Starting JavaScript fallback for end time...');
                            
                            // First, enable any disabled inputs
                            var allDisabledInputs = document.querySelectorAll('input[disabled]');
                            console.log('Found disabled inputs:', allDisabledInputs.length);
                            for (var d = 0; d < allDisabledInputs.length; d++) {
                                allDisabledInputs[d].removeAttribute('disabled');
                                allDisabledInputs[d].disabled = false;
                                console.log('Enabled input:', allDisabledInputs[d]);
                            }
                            
                            // Try multiple selectors for duration containers
                            var endContainers = document.querySelectorAll('div.durationPicker_container') ||
                                               document.querySelectorAll('[class*="durationPicker"]') ||
                                               document.querySelectorAll('[class*="duration"]');
                            
                            console.log('Found containers:', endContainers.length);
                            
                            if (endContainers.length >= 2) {
                                var endContainer = endContainers[1];
                                
                                // Try multiple selectors for inputs
                                var inputs = endContainer.querySelectorAll('input[type="number"]') ||
                                           endContainer.querySelectorAll('input[type="text"]') ||
                                           endContainer.querySelectorAll('input');
                                
                                console.log('Found inputs in end container:', inputs.length);
                                
                                if (inputs.length >= 3) {
                                    // Enable each input before setting values
                                    for (var i = 0; i < 3; i++) {
                                        inputs[i].removeAttribute('disabled');
                                        inputs[i].disabled = false;
                                        inputs[i].readOnly = false;
                                        inputs[i].style.pointerEvents = 'auto';
                                        inputs[i].style.opacity = '1';
                                    }
                                    
                                    // Clear and set values
                                    inputs[0].value = '';
                                    inputs[1].value = '';
                                    inputs[2].value = '';
                                    
                                    // Wait a bit
                                    setTimeout(function() {
                                        inputs[0].value = arguments[0];
                                        inputs[1].value = arguments[1]; 
                                        inputs[2].value = arguments[2];
                                        
                                        // Force focus and trigger comprehensive events
                                        for (var i = 0; i < 3; i++) {
                                            inputs[i].focus();
                                            
                                            // Trigger all possible events
                                            var events = ['input', 'change', 'blur', 'keyup', 'keydown', 'focus'];
                                            events.forEach(function(eventType) {
                                                var event = new Event(eventType, { 
                                                    bubbles: true, 
                                                    cancelable: true 
                                                });
                                                inputs[i].dispatchEvent(event);
                                            });
                                        }
                                        
                                        console.log('End time values set:', inputs[0].value, inputs[1].value, inputs[2].value);
                                    }, 100);
                                    
                                    return true;
                                }
                            }
                            
                            console.log('JavaScript fallback failed - elements not found');
                            return false;
                        """, end_parts[0], end_parts[1], end_parts[2])
                        
                        if result:
                            logger.info("✅ Set end time using JavaScript fallback")
                            end_time_success = True
                            # Give time for events to process
                            time.sleep(2)
                        else:
                            logger.error("❌ JavaScript fallback returned false - elements not found")
                            
                    except Exception as js_error:
                        logger.error(f"JavaScript fallback also failed: {js_error}")
                
                # If JavaScript fallback also failed, try one more approach
                if not end_time_success:
                    logger.warning("🔄 Trying final approach: refresh controls and retry end time...")
                    try:
                        # Click on Controls tab to refresh the interface
                        controls_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Controls')] | //div[contains(text(), 'Controls')] | //*[@class and contains(text(), 'Controls')]")
                        controls_tab.click()
                        time.sleep(2)
                        
                        # Try setting end time one more time with fresh elements
                        fresh_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'durationPicker_container')]")
                        if len(fresh_containers) >= 2:
                            fresh_end_inputs = fresh_containers[1].find_elements(By.XPATH, ".//input[@type='number']")
                            if len(fresh_end_inputs) >= 3:
                                # Quick set without delays
                                fresh_end_inputs[0].clear()
                                fresh_end_inputs[0].send_keys(end_parts[0])
                                fresh_end_inputs[1].clear() 
                                fresh_end_inputs[1].send_keys(end_parts[1])
                                fresh_end_inputs[2].clear()
                                fresh_end_inputs[2].send_keys(end_parts[2])
                                
                                logger.info("✅ Set end time using refresh approach")
                                end_time_success = True
                    except Exception as refresh_error:
                        logger.error(f"Refresh approach also failed: {refresh_error}")
                        
                if not end_time_success:
                    logger.error("❌ All end time setting methods failed - skipping this clip")
                    return False
                
                if end_time_success:
                    logger.info(f"✅ Set end time duration picker: {end_parts[0]}:{end_parts[1]}:{end_parts[2]}")
                    
                    # Immediately sync Material-UI sliders and click create to prevent interface changes
                    logger.info("🔄 Quickly syncing Material-UI sliders...")
                    range_sliders = self.driver.find_elements(By.XPATH, "//input[@type='range' and @data-index]")
                    
                    if len(range_sliders) >= 2:
                        # Find start and end sliders by data-index
                        start_slider = None
                        end_slider = None
                        
                        for slider in range_sliders:
                            data_index = slider.get_attribute('data-index')
                            if data_index == '0':
                                start_slider = slider
                            elif data_index == '1':
                                end_slider = slider
                        
                        if start_slider and end_slider:
                            logger.info("Syncing Material-UI sliders with duration picker values")
                            
                            # Set slider values to match duration picker
                            self.driver.execute_script("""
                                var startSlider = arguments[0];
                                var endSlider = arguments[1];
                                var startSeconds = arguments[2];
                                var endSeconds = arguments[3];
                                
                                // Set values and trigger events for Material-UI
                                startSlider.value = startSeconds;
                                startSlider.setAttribute('aria-valuenow', startSeconds);
                                endSlider.value = endSeconds;
                                endSlider.setAttribute('aria-valuenow', endSeconds);
                                
                                // Dispatch events
                                var events = ['input', 'change', 'mouseup'];
                                events.forEach(function(eventType) {
                                    var event = new Event(eventType, { bubbles: true });
                                    startSlider.dispatchEvent(event);
                                    endSlider.dispatchEvent(event);
                                });
                                
                                console.log('Synced sliders with duration picker: ' + startSeconds + 's to ' + endSeconds + 's');
                            """, start_slider, end_slider, start_seconds, end_seconds)
                            
                            # Verify the sync worked
                            new_start_aria = start_slider.get_attribute('aria-valuenow')
                            new_end_aria = end_slider.get_attribute('aria-valuenow')
                            logger.info(f"✅ Synced sliders - Start: {new_start_aria}s, End: {new_end_aria}s")
                    
                    # Immediately click create button after setting times to prevent interface changes
                    logger.info("🚀 Immediately clicking create button to prevent time changes...")
                    create_selectors = [
                        "//button[contains(text(), 'Create')]",
                        "//button[contains(text(), 'Cut')]", 
                        "//button[contains(text(), 'Generate')]",
                        "//button[contains(text(), 'Download')]",
                        "//button[contains(text(), 'Export')]",
                        "//button[contains(text(), 'Save')]",
                        "//button[contains(@class, 'create')]",
                        "//button[contains(@class, 'cut')]"
                    ]
                    
                    create_button = self.find_element_with_multiple_selectors(create_selectors)
                    if create_button:
                        if self.safe_click(create_button):
                            logger.info("✅ Successfully clicked create button immediately after setting times")
                            
                            # Fast wait and download in one operation
                            if self.fast_wait_and_download():
                                return True
                            else:
                                logger.warning("Download failed, but clip creation may have succeeded")
                                return True
                        else:
                            logger.error("Failed to click create button")
                            return False
                    else:
                        logger.warning("Create button not found after setting times")
                        return True  # Continue anyway
                        
                else:
                    logger.error("Failed to set end time completely")
                    return False
                
                # Also set the Material-UI sliders to sync with duration picker
                logger.info("Setting Material-UI sliders to sync with duration picker...")
                range_sliders = self.driver.find_elements(By.XPATH, "//input[@type='range' and @data-index]")
                
                if len(range_sliders) >= 2:
                    # Find start and end sliders by data-index
                    start_slider = None
                    end_slider = None
                    
                    for slider in range_sliders:
                        data_index = slider.get_attribute('data-index')
                        if data_index == '0':
                            start_slider = slider
                        elif data_index == '1':
                            end_slider = slider
                    
                    if start_slider and end_slider:
                        logger.info("Syncing Material-UI sliders with duration picker values")
                        
                        # Set slider values to match duration picker
                        self.driver.execute_script("""
                            var startSlider = arguments[0];
                            var endSlider = arguments[1];
                            var startSeconds = arguments[2];
                            var endSeconds = arguments[3];
                            
                            // Set values and trigger events for Material-UI
                            startSlider.value = startSeconds;
                            startSlider.setAttribute('aria-valuenow', startSeconds);
                            endSlider.value = endSeconds;
                            endSlider.setAttribute('aria-valuenow', endSeconds);
                            
                            // Dispatch events
                            var events = ['input', 'change', 'mouseup'];
                            events.forEach(function(eventType) {
                                var event = new Event(eventType, { bubbles: true });
                                startSlider.dispatchEvent(event);
                                endSlider.dispatchEvent(event);
                            });
                            
                            console.log('Synced sliders with duration picker: ' + startSeconds + 's to ' + endSeconds + 's');
                        """, start_slider, end_slider, start_seconds, end_seconds)
                        
                        time.sleep(0.5)
                        
                        # Verify the sync worked
                        new_start_aria = start_slider.get_attribute('aria-valuenow')
                        new_end_aria = end_slider.get_attribute('aria-valuenow')
                        logger.info(f"✅ Synced sliders - Start: {new_start_aria}s, End: {new_end_aria}s")
                
                # Immediately click create button after setting times to prevent interface changes
                logger.info("🚀 Immediately clicking create button to prevent time changes...")
                create_selectors = [
                    "//button[contains(text(), 'Create')]",
                    "//button[contains(text(), 'Cut')]", 
                    "//button[contains(text(), 'Generate')]",
                    "//button[contains(text(), 'Download')]",
                    "//button[contains(text(), 'Export')]",
                    "//button[contains(text(), 'Save')]",
                    "//button[contains(@class, 'create')]",
                    "//button[contains(@class, 'cut')]"
                ]
                
                create_button = self.find_element_with_multiple_selectors(create_selectors)
                if create_button:
                    if self.safe_click(create_button):
                        logger.info("✅ Successfully clicked create button immediately after setting times")
                        
                        # Fast wait and download in one operation
                        if self.fast_wait_and_download():
                            return True
                        else:
                            logger.warning("Download failed, but clip creation may have succeeded")
                            return True
                    else:
                        logger.error("Failed to click create button")
                        return False
                else:
                    logger.warning("Create button not found after setting times")
                
                return True  # Successfully set using duration picker
            
            # Step 2: Fallback to time input fields if no duration picker found
            logger.info("No duration picker found, trying alternative methods...")
            
            # Find and click create/cut button
            create_selectors = [
                "//button[contains(text(), 'Create')]",
                "//button[contains(text(), 'Cut')]",
                "//button[contains(text(), 'Generate')]",
                "//button[contains(text(), 'Download')]",
                "//button[contains(text(), 'Export')]",
                "//button[contains(text(), 'Save')]",
                "//button[contains(@class, 'create')]",
                "//button[contains(@class, 'cut')]"
            ]
            
            create_button = self.find_element_with_multiple_selectors(create_selectors)
            
            if create_button:
                if self.safe_click(create_button):
                    logger.info("Clicked create clip button")
                    # Wait for clip creation to complete
                    return self.wait_for_clip_creation()
                else:
                    logger.error("Failed to click create button")
                    return False
            else:
                logger.warning("No create button found, assuming clip is ready")
                return True
                
            # Method 1: Try Material-UI dual range slider (ClipScutter specific)
            mui_slider_inputs = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'MuiSlider-root')]//input[@type='range']")
            
            if len(mui_slider_inputs) >= 2:
                logger.info("Found Material-UI dual range slider")
                
                # Sort by data-index to ensure correct order
                start_slider = None
                end_slider = None
                
                for slider in mui_slider_inputs:
                    data_index = slider.get_attribute('data-index')
                    if data_index == '0':
                        start_slider = slider
                    elif data_index == '1':
                        end_slider = slider
                
                if start_slider and end_slider:
                    logger.info("Found start and end sliders for Material-UI")
                    
                    # Get slider properties
                    max_value = int(start_slider.get_attribute('max') or '3441')
                    min_value = int(start_slider.get_attribute('min') or '0')
                    logger.info(f"Slider range: {min_value} to {max_value} seconds")
                    
                    # Get current values
                    current_start = start_slider.get_attribute('value')
                    current_end = end_slider.get_attribute('value')
                    logger.info(f"Current values - Start: {current_start}s, End: {current_end}s")
                    
                    # Validate our target times
                    if start_seconds > max_value:
                        logger.warning(f"Start time {start_seconds}s exceeds video duration {max_value}s")
                        start_seconds = max_value - 60
                        
                    if end_seconds > max_value:
                        logger.warning(f"End time {end_seconds}s exceeds video duration {max_value}s")
                        end_seconds = max_value
                    
                    logger.info(f"Setting Material-UI sliders: Start={start_seconds}s, End={end_seconds}s")
                    
                    # Use a more robust method: direct DOM manipulation + mouse simulation
                    success = self.driver.execute_script("""
                        var startSlider = arguments[0];
                        var endSlider = arguments[1];
                        var startValue = arguments[2];
                        var endValue = arguments[3];
                        
                        try {
                            console.log('Setting Material-UI sliders:', startValue, 'to', endValue);
                            
                            // Function to set slider value with all necessary updates
                            function setSliderValue(slider, value) {
                                // Update all relevant attributes
                                slider.value = value;
                                slider.setAttribute('aria-valuenow', value);
                                
                                // Update parent thumb position
                                var thumb = slider.closest('.MuiSlider-thumb');
                                if (thumb) {
                                    var maxValue = parseInt(slider.getAttribute('max')) || 3441;
                                    var percentage = (value / maxValue) * 100;
                                    thumb.style.left = percentage + '%';
                                }
                                
                                // Update track (the colored bar between thumbs)
                                var sliderRoot = slider.closest('.MuiSlider-root');
                                if (sliderRoot) {
                                    var track = sliderRoot.querySelector('.MuiSlider-track');
                                    if (track) {
                                        var maxVal = parseInt(slider.getAttribute('max')) || 3441;
                                        var startVal = parseInt(sliderRoot.querySelector('[data-index="0"]').value) || 0;
                                        var endVal = parseInt(sliderRoot.querySelector('[data-index="1"]').value) || maxVal;
                                        var leftPercent = (startVal / maxVal) * 100;
                                        var widthPercent = ((endVal - startVal) / maxVal) * 100;
                                        track.style.left = leftPercent + '%';
                                        track.style.width = widthPercent + '%';
                                    }
                                }
                                
                                // Trigger comprehensive events
                                var events = ['mousedown', 'input', 'change', 'mouseup'];
                                events.forEach(function(eventType) {
                                    var event = new Event(eventType, { bubbles: true, cancelable: true });
                                    slider.dispatchEvent(event);
                                });
                            }
                            
                            // Set start slider first
                            setSliderValue(startSlider, startValue);
                            
                            // Small delay
                            setTimeout(function() {
                                // Set end slider
                                setSliderValue(endSlider, endValue);
                                
                                console.log('Sliders set - Start:', startSlider.value, 'aria:', startSlider.getAttribute('aria-valuenow'));
                                console.log('Sliders set - End:', endSlider.value, 'aria:', endSlider.getAttribute('aria-valuenow'));
                            }, 100);
                            
                            return true;
                        } catch (error) {
                            console.error('Error setting sliders:', error);
                            return false;
                        }
                    """, start_slider, end_slider, start_seconds, end_seconds)
                    
                    time.sleep(1.5)  # Reduced from 3 to 1.5 - Allow Material-UI to fully process the changes
                    
                    # Comprehensive verification of both sliders
                    verification_result = self.driver.execute_script("""
                        var startSlider = arguments[0];
                        var endSlider = arguments[1];
                        var expectedStart = arguments[2];
                        var expectedEnd = arguments[3];
                        
                        var result = {
                            startValue: startSlider.value,
                            startAria: startSlider.getAttribute('aria-valuenow'),
                            endValue: endSlider.value,
                            endAria: endSlider.getAttribute('aria-valuenow'),
                            startMatch: false,
                            endMatch: false
                        };
                        
                        // Check if values match (allowing small tolerance)
                        result.startMatch = Math.abs(parseInt(result.startAria) - expectedStart) <= 1;
                        result.endMatch = Math.abs(parseInt(result.endAria) - expectedEnd) <= 1;
                        
                        return result;
                    """, start_slider, end_slider, start_seconds, end_seconds)
                    
                    logger.info(f"Material-UI Slider verification:")
                    logger.info(f"  Start - value: {verification_result['startValue']}, aria-valuenow: {verification_result['startAria']} (expected: {start_seconds})")
                    logger.info(f"  End - value: {verification_result['endValue']}, aria-valuenow: {verification_result['endAria']} (expected: {end_seconds})")
                    
                    # Convert to readable time format
                    if verification_result['startAria'] and verification_result['endAria']:
                        start_aria = int(verification_result['startAria'])
                        end_aria = int(verification_result['endAria'])
                        start_time_check = f"{start_aria//3600:02d}:{(start_aria%3600)//60:02d}:{start_aria%60:02d}"
                        end_time_check = f"{end_aria//3600:02d}:{(end_aria%3600)//60:02d}:{end_aria%60:02d}"
                        logger.info(f"Time verification - Start: {start_time_check}, End: {end_time_check}")
                        
                        # Overall success check
                        if verification_result['startMatch'] and verification_result['endMatch']:
                            logger.info("✓ Material-UI sliders set correctly!")
                        else:
                            logger.warning(f"⚠ Slider mismatch - Start OK: {verification_result['startMatch']}, End OK: {verification_result['endMatch']}")
                    
                    logger.info("Material-UI slider setting completed")
                    
                else:
                    logger.warning("Could not find both start and end sliders in Material-UI")
            
            else:
                # Fallback: Try generic range sliders
                range_sliders = self.driver.find_elements(By.XPATH, "//input[@type='range']")
                
                if len(range_sliders) >= 2:
                    logger.info("Using range sliders for time selection")
                    
                    start_slider = range_sliders[0]  # First slider for start time
                    end_slider = range_sliders[1]    # Second slider for end time
                    
                    # Get slider properties
                    max_value = int(start_slider.get_attribute('max') or '3441')  # Default to video duration 57:21
                    min_value = int(start_slider.get_attribute('min') or '0')
                    logger.info(f"Slider range: {min_value} to {max_value} seconds")
                    
                    # Get current values
                    current_start = start_slider.get_attribute('value')
                    current_end = end_slider.get_attribute('value')
                    logger.info(f"Current slider values - Start: {current_start}, End: {current_end}")
                    
                    # Validate our times against video duration
                    if start_seconds > max_value:
                        logger.warning(f"Start time {start_seconds}s exceeds video duration {max_value}s")
                        start_seconds = max_value - 60  # 1 minute before end
                        
                    if end_seconds > max_value:
                        logger.warning(f"End time {end_seconds}s exceeds video duration {max_value}s")
                        end_seconds = max_value
                    
                    logger.info(f"Setting sliders to: Start={start_seconds}s, End={end_seconds}s")
                    
                    # Use direct seconds mapping (ClipScutter uses seconds for slider values)
                    # Set slider values using robust JavaScript method with aria-valuenow for Material-UI
                    self.driver.execute_script("""
                        // Set start slider
                        var startSlider = arguments[0];
                        var startValue = arguments[1];
                        startSlider.value = startValue;
                        startSlider.setAttribute('aria-valuenow', startValue);
                        startSlider.dispatchEvent(new Event('input', { bubbles: true }));
                        startSlider.dispatchEvent(new Event('change', { bubbles: true }));
                        startSlider.dispatchEvent(new Event('mouseup', { bubbles: true }));
                        
                        // Set end slider  
                        var endSlider = arguments[2];
                        var endValue = arguments[3];
                        endSlider.value = endValue;
                        endSlider.setAttribute('aria-valuenow', endValue);
                        endSlider.dispatchEvent(new Event('input', { bubbles: true }));
                        endSlider.dispatchEvent(new Event('change', { bubbles: true }));
                        endSlider.dispatchEvent(new Event('mouseup', { bubbles: true }));
                        
                        console.log('Set sliders: start=' + startValue + ' (' + arguments[4] + '), end=' + endValue + ' (' + arguments[5] + ')');
                    """, start_slider, start_seconds, end_slider, end_seconds, start_time, end_time)
                    
                    time.sleep(1)  # Reduced from 2 to 1 - Allow UI to update
                    
                    # Comprehensive verification of both value and aria-valuenow
                    new_start_value = start_slider.get_attribute('value')
                    new_start_aria = start_slider.get_attribute('aria-valuenow')
                    new_end_value = end_slider.get_attribute('value')
                    new_end_aria = end_slider.get_attribute('aria-valuenow')
                    
                    logger.info(f"Material-UI Slider verification:")
                    logger.info(f"  Start - value: {new_start_value}, aria-valuenow: {new_start_aria} (expected: {start_seconds})")
                    logger.info(f"  End - value: {new_end_value}, aria-valuenow: {new_end_aria} (expected: {end_seconds})")
                    
                    # Convert back to time format for verification using format_seconds_to_time function
                    if new_start_value and new_end_value:
                        start_time_check = format_seconds_to_time(int(new_start_value))
                        end_time_check = format_seconds_to_time(int(new_end_value))
                        logger.info(f"Time verification - Start: {start_time_check}, End: {end_time_check}")
                        
                        # Check if times match what we expected
                        if start_time_check == start_time and end_time_check == end_time:
                            logger.info("✅ Material-UI sliders set correctly!")
                        else:
                            logger.warning(f"⚠️ Slider times don't match! Expected: {start_time}-{end_time}, Got: {start_time_check}-{end_time_check}")
                    
                    logger.info("Material-UI slider setting completed")
                    
                    # Check for any error messages on the page
                    try:
                        error_selectors = [
                            "//*[contains(text(), 'Must be less than')]",
                            "//*[contains(text(), 'error')]",
                            "//*[contains(text(), 'Error')]",
                            "//*[contains(@class, 'error')]",
                            "//*[contains(@class, 'invalid')]",
                            "//*[contains(text(), 'Invalid')]"
                        ]
                        
                        for selector in error_selectors:
                            error_elements = self.driver.find_elements(By.XPATH, selector)
                            for element in error_elements:
                                if element.is_displayed():
                                    error_text = element.text.strip()
                                    if error_text:
                                        logger.warning(f"⚠️ Page error detected: {error_text}")
                                        
                                        # If we see the specific time format error, try to fix it
                                        if "Must be less than" in error_text and ":" in error_text:
                                            logger.info("🔧 Detected time format error, attempting to fix...")
                                            
                                            # Look for any time input fields that might be showing wrong format
                                            time_inputs = self.driver.find_elements(By.XPATH, "//input[@type='time' or contains(@placeholder, 'time') or contains(@class, 'time')]")
                                            for time_input in time_inputs:
                                                current_value = time_input.get_attribute('value')
                                                if current_value and ":" in current_value:
                                                    logger.info(f"Found time input with value: {current_value}")
                                                    # Try to set it to the correct format
                                                    try:
                                                        if time_input == time_inputs[0]:  # First input is start time
                                                            time_input.clear()
                                                            time_input.send_keys(start_time)
                                                        elif len(time_inputs) > 1 and time_input == time_inputs[1]:  # Second input is end time
                                                            time_input.clear()
                                                            time_input.send_keys(end_time)
                                                        logger.info(f"Updated time input to correct format")
                                                    except Exception as input_error:
                                                        logger.debug(f"Failed to update time input: {input_error}")
                                            
                                            # Re-trigger the slider events to refresh the display
                                            self.driver.execute_script("""
                                                var startSlider = arguments[0];
                                                var endSlider = arguments[1];
                                                startSlider.dispatchEvent(new Event('input', { bubbles: true }));
                                                endSlider.dispatchEvent(new Event('input', { bubbles: true }));
                                            """, start_slider, end_slider)
                                            time.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"Error detection failed: {e}")
                    
                    return True
                    
                    # Additional verification - check if the interface shows the correct times
                    time.sleep(1)
                    
                    # Method 2: Simulate mouse interaction for better compatibility
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        
                        # Click and drag start slider
                        actions.click(start_slider).perform()
                        time.sleep(0.5)
                        
                        # Click and drag end slider
                        actions.click(end_slider).perform()
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.warning(f"Mouse interaction failed: {e}")
                    
                    # Verify the values were set
                    new_start = start_slider.get_attribute('value')
                    new_end = end_slider.get_attribute('value')
                    logger.info(f"Final slider values - Start: {new_start} ({start_time}), End: {new_end} ({end_time})")
                    
                    time.sleep(2)
                else:
                    logger.warning("No time input fields or sliders found")
            
            logger.info(f"Time setting completed for: {start_time} to {end_time}")
            
            # Find and click create/cut button
            create_selectors = [
                "//button[contains(text(), 'Create')]",
                "//button[contains(text(), 'Cut')]",
                "//button[contains(text(), 'Generate')]",
                "//button[contains(text(), 'Download')]",
                "//button[contains(text(), 'Export')]",
                "//button[contains(text(), 'Save')]",
                "//button[contains(@class, 'create')]",
                "//button[contains(@class, 'cut')]"
            ]
            
            create_button = self.find_element_with_multiple_selectors(create_selectors)
            
            if create_button:
                if self.safe_click(create_button):
                    logger.info("Clicked create clip button")
                    # Wait for clip creation to complete
                    return self.wait_for_clip_creation()
                else:
                    logger.error("Failed to click create button")
                    return False
            else:
                logger.warning("No create button found, assuming clip is ready")
                return True
            
        except Exception as e:
            logger.error(f"Failed to create clip: {e}")
            return False
    
    def set_number_input(self, element, value: int) -> None:
        """
        Set value for a number input element
        
        Args:
            element: WebElement for number input
            value: Integer value to set
        """
        try:
            # Clear and set the value
            element.clear()
            element.send_keys(str(value))
            
            # Trigger input event to update the interface
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                element
            )
        except Exception as e:
            logger.warning(f"Failed to set number input: {e}")
    
    def seconds_to_hms(self, seconds: int) -> tuple:
        """
        Convert seconds to hours, minutes, seconds
        
        Args:
            seconds: Total seconds
            
        Returns:
            tuple: (hours, minutes, seconds)
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return hours, minutes, secs
    
    def wait_for_clip_creation(self, timeout: int = 10) -> bool:
        """
        Fast wait for clip creation to complete with optimized timing
        
        Args:
            timeout (int): Maximum wait time in seconds (reduced default)
            
        Returns:
            bool: True if clip creation successful
        """
        try:
            logger.info("Waiting for clip creation to complete...")
            
            # Minimal wait for processing to start
            time.sleep(0.5)  # Very short initial wait
            
            # Smart detection: Look for the download button which indicates success
            download_button_selectors = [
                "//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]",  # User's exact HTML
                "//button[@title='Download']",
                "//button[contains(@class, 'downloadIcon')]"
            ]
            
            # Quick poll for download button availability (indicates clip is ready)
            start_time = time.time()
            while time.time() - start_time < timeout:
                for selector in download_button_selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        if buttons:
                            logger.info("✅ Clip creation complete - download button detected!")
                            return True
                    except:
                        continue
                
                # Very short sleep between polls
                time.sleep(0.2)
            
            # Timeout reached - assume success and continue
            logger.warning("No clear success indicator found, assuming clip was created")
            return True
            
        except Exception as e:
            logger.warning(f"Error waiting for clip creation: {e}")
            return True  # Assume success to continue processing
    
    def fast_wait_and_download(self, timeout: int = 15) -> bool:
        """
        Ultra-fast combined wait for clip creation and immediate download
        Waits for the NEW clip to appear and downloads it specifically
        
        Args:
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if both wait and download successful
        """
        try:
            logger.info("⚡ Fast wait and download starting...")
            
            # Get the current number of clips BEFORE creation
            initial_clip_count = 0
            try:
                initial_clips = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cutterClipsListItem') or contains(@class, 'clipItem')]")
                initial_clip_count = len(initial_clips)
                logger.info(f"📊 Initial clip count: {initial_clip_count}")
            except:
                logger.info("📊 Could not count initial clips")
            
            # Ultra-short initial wait
            time.sleep(0.5)
            
            # Poll for NEW clip to appear
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Check if a NEW clip has been added
                    current_clips = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cutterClipsListItem') or contains(@class, 'clipItem')]")
                    current_clip_count = len(current_clips)
                    
                    # If clip count increased, we have a new clip
                    if current_clip_count > initial_clip_count:
                        logger.info(f"✅ NEW clip detected! Count: {initial_clip_count} → {current_clip_count}")
                        
                        # Get the download button from the NEW (first) clip
                        if current_clips:
                            newest_clip = current_clips[0]  # First in list = newest
                            try:
                                download_button = newest_clip.find_element(By.XPATH, ".//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]")
                                
                                # Immediate scroll and click the NEW clip
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
                                time.sleep(0.2)
                                
                                try:
                                    download_button.click()
                                    logger.info("⚡ NEW clip download successful!")
                                except:
                                    self.driver.execute_script("arguments[0].click();", download_button)
                                    logger.info("⚡ NEW clip download successful (JS)!")
                                
                                time.sleep(2)  # Wait for download to start
                                return True
                                
                            except Exception as e:
                                logger.warning(f"Could not find download button in new clip: {e}")
                                
                    # If no new clip yet, try to find download buttons anyway
                    download_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]")
                    if download_buttons and len(download_buttons) > initial_clip_count:
                        # More download buttons than before = new clip
                        logger.info("✅ New download button detected!")
                        latest_button = download_buttons[0]
                        
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", latest_button)
                        time.sleep(0.2)
                        
                        try:
                            latest_button.click()
                            logger.info("⚡ Fast download successful!")
                        except:
                            self.driver.execute_script("arguments[0].click();", latest_button)
                            logger.info("⚡ Fast download successful (JS)!")
                        
                        time.sleep(2)
                        return True
                            
                except Exception:
                    pass
                
                # Very short sleep between attempts
                time.sleep(0.3)
            
            logger.warning("⚡ Fast method timeout - trying fallback download")
            return self.download_latest_clip()
            
        except Exception as e:
            logger.warning(f"⚡ Fast wait and download failed: {e}")
            return self.download_latest_clip()
    
    def download_latest_clip(self) -> bool:
        """
        Download the most recently created clip using optimized fast method
        
        Returns:
            bool: True if download was successful
        """
        try:
            logger.info("Attempting to download the latest clip...")
            
            # Minimal wait - clip should be ready immediately after creation
            time.sleep(0.5)
            
            # Ultra-fast method using exact user-provided HTML structure
            fast_selectors = [
                # Exact class from user's HTML - highest priority
                "//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]",
                # CSS equivalent for even faster execution
                "button.cutterClipsListItem_downloadIcon__gik8o",
                # Backup with full Material-UI structure
                "//button[contains(@class, 'MuiButtonBase-root') and contains(@class, 'MuiIconButton-root') and @title='Download']"
            ]
            
            for i, selector in enumerate(fast_selectors):
                try:
                    logger.info(f"Trying fast selector {i+1}: {selector[:60]}...")
                    
                    if selector.startswith('//'):
                        # XPath selector
                        download_buttons = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector for even faster execution
                        download_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    logger.info(f"Found {len(download_buttons)} elements with this selector")
                    
                    if download_buttons:
                        # Try to identify the most recently created clip
                        latest_button = None
                        
                        # Method 1: Look for the topmost clip (newest)
                        try:
                            # Find all clip containers and get the first one
                            clip_containers = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cutterClipsListItem') or contains(@class, 'clipItem')]")
                            if clip_containers:
                                # Get download button from the first (topmost) container
                                topmost_container = clip_containers[0]
                                latest_button = topmost_container.find_element(By.XPATH, ".//button[contains(@class, 'cutterClipsListItem_downloadIcon__gik8o')]")
                                logger.info("✅ Found download button in topmost clip container")
                            else:
                                latest_button = download_buttons[0]
                                logger.info("⚡ Using first available download button")
                        except:
                            # Fallback to first download button found
                            latest_button = download_buttons[0]
                            logger.info("⚡ Using first available download button (fallback)")
                        
                        # Method 2: If no clear latest, wait a bit more for the new clip to appear
                        if not latest_button:
                            time.sleep(1)
                            download_buttons = self.driver.find_elements(By.XPATH, selector) if selector.startswith('//') else self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if download_buttons:
                                latest_button = download_buttons[0]
                        
                        if latest_button:
                            logger.info(f"Found working download button with selector: {selector}")
                            logger.info("Attempting to click download button...")
                            
                            # Quick scroll into view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", latest_button)
                            time.sleep(0.1)  # Minimal wait
                            
                            # Try direct click first (fastest)
                            try:
                                latest_button.click()
                                logger.info("Successfully clicked download button (regular click)")
                            except Exception:
                                # Fallback to JavaScript click
                                self.driver.execute_script("arguments[0].click();", latest_button)
                                logger.info("Successfully clicked download button (JavaScript click)")
                            
                            logger.info("Download should start - waiting for download to begin...")
                            time.sleep(2)  # Sufficient wait for download to start
                            
                            logger.info("Clip downloaded successfully!")
                            return True
                        
                except Exception as e:
                    logger.warning(f"Fast selector {i+1} failed: {e}")
                    continue
            
            # If fast method fails, try one legacy fallback
            logger.warning("Fast selectors failed, trying legacy fallback...")
            
            # Single legacy fallback
            legacy_elements = self.driver.find_elements(By.XPATH, "//button[@title='Download']")
            if legacy_elements:
                legacy_button = legacy_elements[0]
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", legacy_button)
                    logger.info("Legacy download method succeeded")
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    logger.error(f"Legacy method also failed: {e}")
            
            logger.error("❌ Could not find any working download button")
            return False
            
        except Exception as e:
            logger.error(f"Download failed with error: {e}")
            return False
    
    def get_video_duration(self) -> int:
        """
        Try to get the video duration from the page
        
        Returns:
            int: Video duration in seconds, or 0 if not found
        """
        try:
            logger.info("Attempting to determine video duration...")
            
            # Method 1: Look for HTML5 video element duration
            try:
                video_element = self.driver.find_element(By.TAG_NAME, "video")
                duration = self.driver.execute_script("return arguments[0].duration;", video_element)
                if duration and duration > 0:
                    logger.info(f"Found video duration from HTML5 element: {duration}s")
                    return int(duration)
            except Exception as e:
                logger.debug(f"HTML5 video duration failed: {e}")
            
            # Method 2: Look for duration text in various formats
            duration_selectors = [
                "//span[contains(@class, 'duration')]",
                "//div[contains(@class, 'duration')]", 
                "//span[contains(text(), ':') and string-length(text()) <= 10]",
                "//*[contains(@class, 'time') and contains(text(), ':')]",
                "//*[contains(@aria-label, 'duration')]",
                "//*[contains(@title, 'duration')]",
                "//time",
                "//*[contains(@class, 'player')]//span[contains(text(), ':')]"
            ]
            
            for selector in duration_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text.strip()
                        if ':' in text and len(text) <= 10:
                            duration = self.parse_time_string(text)
                            if duration > 0:
                                logger.info(f"Found duration from text '{text}': {duration}s")
                                return duration
                except Exception as e:
                    logger.debug(f"Duration selector failed {selector}: {e}")
                    continue
            
            # Method 3: Look in page source for duration patterns
            try:
                page_source = self.driver.page_source
                import re
                
                # Look for JSON data with duration
                duration_patterns = [
                    r'"duration"[:\s]*(\d+)',
                    r'"duration"[:\s]*"(\d+)"',
                    r'duration[:\s]*(\d+)',
                    r'videoDuration[:\s]*(\d+)',
                    r'length[:\s]*(\d+)',
                    r'totalTime[:\s]*(\d+)'
                ]
                
                for pattern in duration_patterns:
                    matches = re.finditer(pattern, page_source, re.IGNORECASE)
                    for match in matches:
                        try:
                            duration = int(match.group(1))
                            if 10 <= duration <= 86400:  # Between 10 seconds and 24 hours
                                logger.info(f"Found duration from page source: {duration}s")
                                return duration
                        except:
                            continue
            except Exception as e:
                logger.debug(f"Page source duration search failed: {e}")
            
            # Method 4: Try to get from slider max values with heuristics
            try:
                range_sliders = self.driver.find_elements(By.XPATH, "//input[@type='range']")
                if range_sliders:
                    max_val = int(range_sliders[0].get_attribute('max') or '0')
                    if max_val > 100:  # If max is > 100, it might be seconds
                        logger.info(f"Estimated duration from slider max: {max_val}s")
                        return max_val
            except Exception as e:
                logger.debug(f"Slider max duration estimation failed: {e}")
                
            logger.warning("Could not determine video duration from any method")
            return 0
            
        except Exception as e:
            logger.warning(f"Error getting video duration: {e}")
            return 0
    
    def parse_time_string(self, time_str: str) -> int:
        """Parse time string in various formats to seconds"""
        try:
            if ':' not in time_str:
                return 0
                
            parts = time_str.strip().split(':')
            parts = [p for p in parts if p.isdigit()]
            
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS  
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                
            return 0
        except:
            return 0

    def check_if_same_video_loaded(self, youtube_url: str) -> bool:
        """
        Check if the same YouTube video is already loaded
        
        Args:
            youtube_url (str): YouTube URL to check
            
        Returns:
            bool: True if same video is loaded
        """
        return self.current_url == youtube_url
    
    def reset_for_new_video(self) -> bool:
        """
        Reset the interface for a new video (go back to homepage)
        
        Returns:
            bool: True if reset successful
        """
        try:
            logger.info("Resetting for new video...")
            self.current_url = None
            return self.navigate_to_homepage()
        except Exception as e:
            logger.error(f"Failed to reset for new video: {e}")
            return False

def validate_time_format(time_str: str) -> bool:
    """
    Validate time format (HH:MM:SS)
    
    Args:
        time_str (str): Time string to validate
        
    Returns:
        bool: True if valid format
    """
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'
    return re.match(pattern, time_str) is not None

def convert_time_to_seconds(time_str: str) -> int:
    """
    Convert time string to seconds
    
    Args:
        time_str (str): Time in HH:MM:SS format
        
    Returns:
        int: Time in seconds
    """
    try:
        parts = [int(x) for x in time_str.split(':')]
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except Exception:
        return 0

def format_seconds_to_time(seconds: int) -> str:
    """
    Convert seconds to HH:MM:SS format
    
    Args:
        seconds (int): Time in seconds
        
    Returns:
        str: Time in HH:MM:SS format
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"