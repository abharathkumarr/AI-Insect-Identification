"""
Appium Driver Setup and Management for Android App Testing
"""

import logging
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from config import (
    APPIUM_SERVER_URL,
    DEVICE_CONFIG,
    IMPLICIT_WAIT,
    EXPLICIT_WAIT,
    ELEMENT_WAIT,
    LOG_LEVEL,
    LOG_FILE,
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AppDriver:
    """Manages Appium driver connection and basic app interactions"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def start_driver(self):
        """Initialize and start the Appium driver"""
        try:
            logger.info("Initializing Appium driver...")
            
            # Create UiAutomator2Options
            options = UiAutomator2Options()
            options.platform_name = DEVICE_CONFIG["platformName"]
            options.platform_version = DEVICE_CONFIG["platformVersion"]
            options.device_name = DEVICE_CONFIG["deviceName"]
            options.udid = DEVICE_CONFIG["udid"]
            options.automation_name = DEVICE_CONFIG["automationName"]
            options.app_package = DEVICE_CONFIG["appPackage"]
            options.app_activity = DEVICE_CONFIG["appActivity"]
            options.no_reset = DEVICE_CONFIG["noReset"]
            options.full_reset = DEVICE_CONFIG["fullReset"]
            
            # Create driver
            self.driver = webdriver.Remote(
                command_executor=APPIUM_SERVER_URL,
                options=options
            )
            
            # Set implicit wait
            self.driver.implicitly_wait(IMPLICIT_WAIT)
            
            # Create explicit wait
            self.wait = WebDriverWait(self.driver, EXPLICIT_WAIT)
            
            logger.info("Appium driver initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Appium driver: {str(e)}")
            raise
    
    def stop_driver(self):
        """Stop and close the Appium driver"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Appium driver closed successfully")
        except Exception as e:
            logger.error(f"Error closing driver: {str(e)}")
    
    def find_element_safe(self, locator, by=AppiumBy.XPATH, timeout=ELEMENT_WAIT):
        """Safely find an element with timeout"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, locator)))
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {locator}")
            return None
    
    def click_element(self, locator, by=AppiumBy.XPATH, timeout=ELEMENT_WAIT):
        """Click an element safely - FAST with minimal logging"""
        try:
            element = self.find_element_safe(locator, by, timeout)
            if element:
                element.click()
                return True
            return False
        except Exception:
            # Don't log errors for missing elements (expected)
            return False
    
    def element_exists(self, locator, by=AppiumBy.XPATH, timeout=0.5):
        """Quick check if element exists without waiting long"""
        try:
            element = self.find_element_safe(locator, by, timeout)
            return element is not None
        except:
            return False
    
    def get_text(self, locator, by=AppiumBy.XPATH, timeout=ELEMENT_WAIT):
        """Get text from an element safely"""
        try:
            element = self.find_element_safe(locator, by, timeout)
            if element:
                text = element.text
                logger.info(f"Got text from {locator}: {text}")
                return text
            return None
        except Exception as e:
            logger.error(f"Failed to get text from {locator}: {str(e)}")
            return None
    
    def wait_for_element(self, locator, by=AppiumBy.XPATH, timeout=EXPLICIT_WAIT):
        """Wait for element to be visible"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located((by, locator)))
            return element
        except TimeoutException:
            logger.warning(f"Element not visible within {timeout}s: {locator}")
            return None
    
    def take_screenshot(self, filename):
        """Take a screenshot"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return False
    
    def get_page_source(self):
        """Get the current page source (XML)"""
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page source: {str(e)}")
            return None



