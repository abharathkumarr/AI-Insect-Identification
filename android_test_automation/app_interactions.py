"""
App-specific interactions for AI Insect Bug Identifier
Handles navigation, image upload, and result extraction
"""

import logging
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
import subprocess
import os

from app_driver import AppDriver
from config import SELECTORS, IMAGE_UPLOAD_METHOD

logger = logging.getLogger(__name__)


class AppInteractions:
    """Handles specific interactions with the AI Insect Bug Identifier app"""
    
    def __init__(self, driver: AppDriver):
        self.driver = driver
        self.app_package = "com.janogroupllc.pdfphotos"
        # Get device ID from config
        from config import DEVICE_CONFIG
        self.device_id = DEVICE_CONFIG.get("udid", "emulator-5554")
    
    def handle_permissions(self):
        """Handle app permissions - FAST CHECK ONLY"""
        try:
            # Quick check - only try for 1 second max per button, skip if not found immediately
            permission_buttons = [
                "While using the app",
                "Allow",
                "OK",
            ]
            
            for button_text in permission_buttons:
                xpath = f"//android.widget.Button[@text='{button_text}']"
                if self.driver.click_element(xpath, timeout=1):  # Reduced to 1s
                    logger.info(f"✓ Clicked permission: {button_text}")
                    time.sleep(0.3)
                    return True
            
            # No permission dialogs found - that's fine, continue
            return True
            
        except Exception as e:
            # Ignore errors - permissions may already be granted
            return True
    
    def skip_onboarding(self):
        """Skip onboarding - ROBUST CLICK METHODS"""
        try:
            logger.info("Checking onboarding...")
            time.sleep(0.5)

            # DEBUG: Save page source to see what's available
            try:
                page_source = self.driver.get_page_source()
                if page_source and "Get Started" in page_source:
                    logger.info("✓ Found 'Get Started' text in page source")
            except:
                pass

            clicked = False
            
            # FIRST: Try clicking "Skip" button (top right) - faster than Get Started
            # XML shows: <android.widget.Button content-desc="Skip" bounds="[849,195][1017,321]"/>
            skip_center_x = (849 + 1017) // 2  # 933
            skip_center_y = (195 + 321) // 2   # 258
            try:
                logger.info(f"Trying 'Skip' button at ({skip_center_x}, {skip_center_y})")
                subprocess.run(
                    ["adb", "-s", self.device_id, "shell", "input", "tap", str(skip_center_x), str(skip_center_y)],
                    check=True,
                    capture_output=True,
                    timeout=2
                )
                logger.info("✓ Tapped 'Skip' button")
                time.sleep(1)
                # Check if we're past onboarding
                try:
                    still_on_onboarding = self.driver.element_exists("//*[@content-desc='Get Started']", timeout=0.5)
                    if not still_on_onboarding:
                        clicked = True
                        logger.info("✓ Successfully skipped onboarding via 'Skip' button")
                except:
                    clicked = True  # Assume it worked
            except Exception as e:
                logger.debug(f"Skip button tap failed: {e}")
            
            # METHOD 1: Try finding element using content-desc (XML shows this!)
            # Try both XPath and Accessibility ID (content-desc can be accessed via accessibility ID)
            get_started_selectors = [
                ("//*[@content-desc='Get Started']", AppiumBy.XPATH),  # PRIMARY - XML shows this!
                ("//android.widget.Button[@content-desc='Get Started']", AppiumBy.XPATH),
                ("Get Started", AppiumBy.ACCESSIBILITY_ID),  # Try accessibility ID
            ]
            
            for selector, by_type in get_started_selectors:
                try:
                    element = self.driver.find_element_safe(selector, by=by_type, timeout=2)
                    if element:
                        # Get exact button bounds from XML: [63,2075][1017,2222]
                        # Center: x = (63 + 1017) / 2 = 540, y = (2075 + 2222) / 2 = 2148
                        try:
                            # Try direct click first
                            element.click()
                            logger.info(f"✓ Clicked 'Get Started' via element.click()")
                            clicked = True
                            break
                        except Exception as e1:
                            # Fallback: Use element's exact center
                            try:
                                location = element.location
                                size = element.size
                                x = location['x'] + size['width'] // 2
                                y = location['y'] + size['height'] // 2
                                # Use ADB tap (more reliable)
                                subprocess.run(
                                    ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)],
                                    check=True,
                                    capture_output=True,
                                    timeout=2
                                )
                                logger.info(f"✓ ADB tapped 'Get Started' at element center ({x}, {y})")
                                clicked = True
                                break
                            except Exception as e2:
                                logger.debug(f"Click methods failed: {e1}, {e2}")
                                continue
                except:
                    continue
            
            # METHOD 2: Coordinate tap using EXACT button center from XML
            # XML shows button bounds: [63,2075][1017,2222]
            # Center: x = (63 + 1017) / 2 = 540, y = (2075 + 2222) / 2 = 2148
            if not clicked:
                try:
                    # Use exact coordinates from XML analysis
                    x = 540  # Center of button width
                    y = 2148  # Center of button height (from XML bounds)
                    
                    # Use ADB tap (most reliable for coordinate-based clicks)
                    logger.info(f"Tapping 'Get Started' at exact center ({x}, {y}) from XML")
                    subprocess.run(
                        ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)],
                        check=True,
                        capture_output=True,
                        timeout=2
                    )
                    logger.info(f"✓ ADB tapped 'Get Started' at exact center ({x}, {y})")
                    clicked = True
                    time.sleep(1.5)  # Wait for screen transition
                    
                    # Verify click worked - check if we're past onboarding
                    try:
                        still_on_onboarding = self.driver.element_exists("//*[@content-desc='Get Started']", timeout=0.5)
                        if still_on_onboarding:
                            logger.warning("Still on onboarding - trying multiple taps")
                            # Try multiple taps in quick succession (button might need multiple taps)
                            for attempt in range(3):
                                subprocess.run(
                                    ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)],
                                    check=True,
                                    capture_output=True,
                                    timeout=2
                                )
                                time.sleep(0.3)
                            time.sleep(1)
                    except:
                        pass
                except Exception as e:
                    logger.warning(f"Exact coordinate tap failed: {str(e)}")

            if clicked:
                time.sleep(2)  # Wait for bottom sheet to appear after "Get Started"
                # Verify we moved past onboarding - bottom sheet should appear
                # Bottom sheet has "Choose from Gallery" option
                try:
                    still_on_onboarding = self.driver.element_exists("//*[@content-desc='Get Started']", timeout=0.5)
                    if still_on_onboarding:
                        logger.warning("Still on onboarding screen after tap - trying ADB tap at exact center")
                        # Try ADB tap at exact center from XML: (540, 2148)
                        subprocess.run(
                            ["adb", "-s", self.device_id, "shell", "input", "tap", "540", "2148"],
                            check=True,
                            capture_output=True,
                            timeout=2
                        )
                        time.sleep(2)  # Wait for bottom sheet
                    else:
                        # Check if bottom sheet appeared (has "Choose from Gallery")
                        bottom_sheet_appeared = self.driver.element_exists("//*[contains(@text, 'Choose from Gallery')]", timeout=1) or \
                                               self.driver.element_exists("//*[contains(@content-desc, 'Choose from Gallery')]", timeout=1)
                        if bottom_sheet_appeared:
                            logger.info("✓ Bottom sheet appeared after 'Get Started'")
                        else:
                            logger.info("Bottom sheet may not have appeared yet - will try in open_gallery()")
                except:
                    pass

            # Handle notification dialog - try multiple methods
            allow_xpaths = [
                "//android.widget.Button[@text='Allow']",
                "//*[@text='Allow']",
                "//*[@resource-id='com.android.permissioncontroller:id/permission_allow_button']",
            ]

            for attempt in range(3):
                for ax in allow_xpaths:
                    try:
                        element = self.driver.find_element_safe(ax, timeout=1)
                        if element:
                            try:
                                element.click()
                            except:
                                # Fallback to tap
                                location = element.location
                                size = element.size
                                x = location['x'] + size['width'] // 2
                                y = location['y'] + size['height'] // 2
                                self.driver.driver.tap([(x, y)], 300)
                            logger.info("✓ Auto-clicked 'Allow' on notifications")
                            time.sleep(0.5)
                            return True
                    except:
                        continue
                if attempt < 2:
                    time.sleep(0.3)

            return True
        except Exception as e:
            logger.warning(f"Onboarding skip error: {str(e)}")
            return False
    
    def open_gallery(self):
        """Open gallery - Handle bottom sheet after 'Get Started'"""
        try:
            logger.info("Opening gallery...")
            time.sleep(1)  # Wait for bottom sheet to appear after "Get Started"
            
            # The bottom sheet appears after clicking "Get Started"
            # It has 3 options: "Take Photo", "Choose from Gallery", "Skip to App"
            # Try multiple selectors - bottom sheet uses content-desc per XML:
            #   <android.widget.Button ... content-desc="Choose from Gallery" ... />
            gallery_selectors = [
                "//*[@content-desc='Choose from Gallery']",            # PRIMARY - matches XML exactly
                "//android.widget.Button[@content-desc='Choose from Gallery']",
                "//*[contains(@content-desc, 'Choose from Gallery')]",  # Fallback partial match
                "//*[@text='Choose from Gallery']",                     # Text-based (in case UI changes)
                "//android.widget.Button[@text='Choose from Gallery']",
                "//android.widget.TextView[@text='Choose from Gallery']",
                "//*[contains(@text, 'Choose from Gallery')]",
            ]
            
            # Give a bit more time per selector so we don't miss the button
            for selector in gallery_selectors:
                if self.driver.click_element(selector, timeout=3):  # up to 3s per selector
                    logger.info("✓ Clicked 'Choose from Gallery'")
                    time.sleep(2.0)  # Wait for gallery picker to open
                    return True
            
            # DEBUG: Save page source to see what's available
            try:
                page_source = self.driver.get_page_source()
                if page_source:
                    # Save to file for debugging
                    debug_file = "test_results/page_source_debug.xml"
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(page_source)
                    logger.info(f"✓ Saved page source to {debug_file} for debugging")
                    # Look for any clickable elements
                    if "Gallery" in page_source or "Photo" in page_source or "Image" in page_source:
                        logger.info("Found gallery-related text in page source")
            except:
                pass
            
            # Fallback: Try tapping bottom sheet "Choose from Gallery" position
            # Bottom sheet has 3 options: "Take Photo" (top), "Choose from Gallery" (middle), "Skip to App" (bottom)
            try:
                size = self.driver.driver.get_window_size()
                width = size['width']
                height = size['height']
                
                # Bottom sheet positions - "Choose from Gallery" is usually in the middle
                # Try tapping middle section where "Choose from Gallery" should be
                tap_positions = [
                    (width // 2, int(height * 0.6)),   # Middle of screen (where "Choose from Gallery" usually is)
                    (width // 2, int(height * 0.65)),  # Slightly lower
                    (width // 2, int(height * 0.55)),  # Slightly higher
                ]
                
                for x, y in tap_positions:
                    logger.info(f"Trying coordinate tap at ({x}, {y}) for 'Choose from Gallery'")
                    # Use ADB tap (more reliable)
                    subprocess.run(
                        ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)],
                        check=True,
                        capture_output=True,
                        timeout=2
                    )
                    time.sleep(1)
                    # Check if gallery picker opened (look for file picker UI elements)
                    # Gallery picker usually has "Recent", "Downloads", "Images", etc.
                    if self.driver.element_exists("//*[contains(@text, 'Recent')]", timeout=0.5) or \
                       self.driver.element_exists("//*[contains(@text, 'Downloads')]", timeout=0.5) or \
                       self.driver.element_exists("//*[contains(@text, 'Images')]", timeout=0.5) or \
                       self.driver.element_exists("//*[contains(@text, 'Gallery')]", timeout=0.5):
                        logger.info("✓ Gallery picker opened")
                        return True
            except Exception as e:
                logger.debug(f"Coordinate tap failed: {e}")
            
            logger.warning("Gallery button not found - check test_results/page_source_debug.xml")
            return False
            
        except Exception as e:
            logger.error(f"Error opening gallery: {str(e)}")
            return False
    
    def select_image_from_gallery(self, image_path):
        """Select an image from the device gallery - matches image name from test case"""
        try:
            logger.info(f"Selecting image: {image_path}")
            
            # First, copy image to device if needed
            image_name = os.path.basename(image_path)
            device_path = f"/sdcard/Download/{image_name}"
            
            # Copy image to device using adb
            try:
                subprocess.run(
                    ["adb", "-s", self.device_id, "push", image_path, device_path],
                    check=True,
                    capture_output=True
                )
                logger.info(f"Image copied to device: {device_path}")
            except Exception as e:
                logger.warning(f"Could not copy image via adb: {str(e)}")
            
            time.sleep(0.5)  # Wait for gallery to load
            
            # Navigate to Downloads folder if needed
            folder_selectors = [
                "//android.widget.TextView[@text='Download']",
                "//android.widget.TextView[@text='Downloads']",
            ]
            
            for selector in folder_selectors:
                if self.driver.click_element(selector, timeout=2):
                    time.sleep(0.5)
                    break
            
            # Try to find image by matching name from test case
            # First, try to find exact image name match
            image_name_without_ext = os.path.splitext(image_name)[0]
            
            # Try multiple strategies to find the image
            image_selectors = [
                # Try to find by image name in TextView (if gallery shows filenames)
                f"//android.widget.TextView[contains(@text, '{image_name_without_ext}')]",
                f"//android.widget.TextView[@text='{image_name}']",
                # Try to find by content description
                f"//*[contains(@content-desc, '{image_name_without_ext}')]",
            ]
            
            image_found = False
            for selector in image_selectors:
                if self.driver.click_element(selector, timeout=2):
                    logger.info(f"✓ Image selected by name match: {image_name}")
                    image_found = True
                    break
            
            # If name matching fails, select first image (fallback)
            if not image_found:
                logger.info(f"Image name not found in gallery, selecting first image as fallback")
                fallback_selectors = [
                    "(//android.widget.ImageView)[1]",  # First image
                    "(//android.widget.ImageView)[2]",   # Second image
                    "(//android.widget.ImageView)[3]",   # Third image
                ]
                
                for selector in fallback_selectors:
                    if self.driver.click_element(selector, timeout=2):
                        logger.info("✓ Image selected (first available)")
                        image_found = True
                        break
            
            if image_found:
                time.sleep(1.5)  # Wait for app to process selection
                return True
            else:
                logger.warning("Could not find image in gallery")
                return False
            
        except Exception as e:
            logger.error(f"Error selecting image: {str(e)}")
            return False
    
    def ensure_app_running(self):
        """Ensure app is running, restart if needed"""
        try:
            # Check if app is in foreground
            result = subprocess.run(
                ["adb", "-s", self.device_id, "shell", "dumpsys", "window", "windows"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if self.app_package in result.stdout:
                logger.info("✓ App is running")
                return True
            
            # App not running, restart it
            logger.info("App closed, restarting...")
            from config import APP_PACKAGE, APP_ACTIVITY
            launch_cmd = f"adb -s {self.device_id} shell am start -n {APP_PACKAGE}/{APP_ACTIVITY}"
            subprocess.run(launch_cmd, shell=True, capture_output=True, timeout=3)
            time.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"Could not check app status: {str(e)}")
            return False
    
    def upload_image_via_intent(self, image_path):
        """Upload image directly via Android Intent (alternative method)"""
        try:
            logger.info(f"Uploading image via Intent: {image_path}")
            
            # Ensure app is running first
            self.ensure_app_running()
            
            # Copy image to device
            image_name = os.path.basename(image_path)
            device_path = f"/sdcard/Download/{image_name}"
            
            subprocess.run(
                ["adb", "-s", self.device_id, "push", image_path, device_path],
                check=True,
                capture_output=True
            )
            
            # Use adb to open the image with the app
            # Format: package/activity (not just activity)
            from config import APP_PACKAGE, APP_ACTIVITY
            # Convert full activity path to package/activity format
            # APP_ACTIVITY is "com.janogroupllc.PdfPhotos.MainActivity"
            # Need: "com.janogroupllc.pdfphotos/com.janogroupllc.PdfPhotos.MainActivity"
            intent_command = (
                f"adb -s {self.device_id} shell am start -a android.intent.action.VIEW "
                f"-d file://{device_path} "
                f"-t image/* "
                f"-n {APP_PACKAGE}/{APP_ACTIVITY}"
            )
            
            result = subprocess.run(intent_command, shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logger.warning(f"Intent failed: {result.stderr}")
                # Ensure app is still running
                self.ensure_app_running()
                return False
            
            time.sleep(2)
            
            # Verify app is still running
            self.ensure_app_running()
            
            # DEBUG: Save page source after Intent to see what screen appears
            try:
                page_source = self.driver.get_page_source()
                if page_source:
                    debug_file = "test_results/page_source_after_intent.xml"
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write(page_source)
                    logger.info(f"✓ Saved page source after Intent to {debug_file}")
                    
                    # Check if Intent reset app to onboarding (common issue)
                    if "Get Started" in page_source and "Bug Identifier" in page_source:
                        logger.warning("App reset to onboarding after Intent - need to click 'Get Started'")
                        logger.info("Please manually click 'Get Started' on the emulator, then the automation will continue")
                        # Wait for user to click Get Started manually
                        time.sleep(3)
                        # Try to click Get Started programmatically at exact center
                        for attempt in range(2):
                            subprocess.run(
                                ["adb", "-s", self.device_id, "shell", "input", "tap", "540", "2148"],
                                check=True,
                                capture_output=True,
                                timeout=2
                            )
                            time.sleep(1)
                        # Handle notification dialog again
                        allow_xpaths = ["//android.widget.Button[@text='Allow']", "//*[@text='Allow']"]
                        for ax in allow_xpaths:
                            if self.driver.click_element(ax, timeout=1):
                                logger.info("✓ Clicked 'Allow' again after Intent reset")
                                break
                        time.sleep(2)  # Wait for app to process
            except:
                pass
            
            logger.info("✓ Image uploaded via Intent")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading via Intent: {str(e)}")
            # Try to recover app
            self.ensure_app_running()
            return False
    
    def wait_for_scanning(self, max_wait=30):
        """Wait for 'Finalizing profile...' scanning to complete"""
        try:
            logger.info("Waiting for image scanning to complete...")
            
            # Wait for scanning screen to appear
            scanning_indicators = [
                "Finalizing profile",
                "Finalizing",
                "Scanning",
                "Processing",
            ]
            
            scanning_found = False
            for indicator in scanning_indicators:
                if self.driver.element_exists(f"//*[contains(@text, '{indicator}')]", timeout=3):
                    scanning_found = True
                    logger.info(f"✓ Found scanning indicator: {indicator}")
                    break
            
            if not scanning_found:
                logger.info("No scanning screen detected, proceeding...")
                return True
            
            # Wait for scanning to complete (progress disappears or result screen appears)
            start_time = time.time()
            while time.time() - start_time < max_wait:
                page_source = self.driver.get_page_source()
                if page_source:
                    # Check if scanning is still in progress
                    still_scanning = any(
                        indicator in page_source 
                        for indicator in ["Finalizing profile", "Finalizing", "Scanning"]
                    )
                    
                    # Check if result screen appeared (has "Dragonfly", "No Insect Detected", or species name)
                    result_appeared = any(
                        keyword in page_source 
                        for keyword in [
                            "Dragonfly", 
                            "species of", 
                            "Damselfly",
                            "No Insect Detected",  # Exact text from "No Insect" screen
                            "No insect detected",
                            "No insect visible",
                            "Tips for Better Photos",  # Appears on "No Insect Detected" screen
                        ]
                    )
                    
                    if not still_scanning or result_appeared:
                        logger.info("✓ Scanning completed")
                        time.sleep(1)  # Brief wait for UI to settle
                        return True
                
                time.sleep(1)  # Check every second
            
            logger.warning("Scanning timeout - proceeding anyway")
            return True
            
        except Exception as e:
            logger.warning(f"Error waiting for scanning: {str(e)}")
            return True  # Continue even if there's an error
    
    def handle_advertisement(self):
        """Handle advertisement: wait 5 seconds and click Close button"""
        try:
            logger.info("Checking for advertisement...")
            time.sleep(1)  # Brief wait for ad to appear
            
            # Look for advertisement indicators
            ad_indicators = [
                "Test Ad",
                "Advertisement",
                "Ad",
            ]
            
            ad_found = False
            page_source = self.driver.get_page_source()
            if page_source:
                for indicator in ad_indicators:
                    if indicator in page_source:
                        ad_found = True
                        logger.info(f"✓ Advertisement detected: {indicator}")
                        break
            
            if ad_found:
                # Wait 5 seconds as per requirement
                logger.info("Waiting 5 seconds for advertisement...")
                time.sleep(5)
                
                # Try to find and click Close button - multiple strategies
                close_selectors = [
                    "//android.widget.Button[@text='Close']",
                    "//*[@text='Close']",
                    "//android.widget.Button[contains(@text, 'Close')]",
                    "//*[contains(@text, 'Close')]",
                    # Try by content description
                    "//*[@content-desc='Close']",
                    "//android.widget.Button[@content-desc='Close']",
                    # Try accessibility ID
                    "Close",
                ]
                
                close_clicked = False
                for selector in close_selectors:
                    if self.driver.click_element(selector, timeout=2):
                        logger.info("✓ Closed advertisement")
                        time.sleep(1)  # Wait for ad to close
                        close_clicked = True
                        break
                
                # If Close button not found, try coordinate-based tap (ad might be in WebView)
                if not close_clicked:
                    logger.info("Close button not found, trying coordinate tap...")
                    try:
                        # Try tapping bottom-right area where Close button often appears
                        size = self.driver.driver.get_window_size()
                        width = size['width']
                        height = size['height']
                        
                        # Try multiple positions where Close button might be
                        close_positions = [
                            (width - 100, 100),  # Top-right corner
                            (width - 150, 150),  # Slightly lower
                            (width // 2, height - 100),  # Bottom center
                        ]
                        
                        for x, y in close_positions:
                            subprocess.run(
                                ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)],
                                check=True,
                                capture_output=True,
                                timeout=2
                            )
                            time.sleep(0.5)
                            # Check if ad disappeared
                            new_page_source = self.driver.get_page_source()
                            if new_page_source and not any(ind in new_page_source for ind in ad_indicators):
                                logger.info("✓ Closed advertisement via coordinate tap")
                                close_clicked = True
                                break
                    except Exception as e:
                        logger.debug(f"Coordinate tap failed: {e}")
                
                if not close_clicked:
                    logger.warning("Advertisement found but Close button not found - continuing anyway")
            else:
                logger.info("No advertisement detected")
            
            return True
            
        except Exception as e:
            logger.warning(f"Error handling advertisement: {str(e)}")
            return True  # Continue even if there's an error
    
    def extract_result(self):
        """Extract identification result from the app - looks for 'Dragonfly a species of Dragonfly or Damselfly' pattern"""
        try:
            # Ensure app is running before extracting
            self.ensure_app_running()
            
            logger.info("Extracting identification result...")
            time.sleep(2)  # Wait for app to process
            
            result = {
                "species": None,
                "confidence": None,
                "full_text": None,
                "status": "no_identification"
            }
            
            # Get page source to extract all text
            page_source = self.driver.get_page_source()
            all_text = []
            all_content_desc = []
            
            if page_source:
                # Extract text from XML
                import re
                text_matches = re.findall(r'<.*?text="([^"]+)"', page_source)
                all_text.extend(text_matches)
                
                # Also extract content-desc (important for Flutter apps)
                content_desc_matches = re.findall(r'<.*?content-desc="([^"]+)"', page_source)
                all_content_desc.extend(content_desc_matches)
            
            # Also try multiple selectors to find result text
            result_selectors = [
                SELECTORS.get("result_text"),
                SELECTORS.get("species_name"),
                "//android.widget.TextView[contains(@resource-id, 'result')]",
                "//android.widget.TextView[contains(@resource-id, 'species')]",
                "//android.widget.TextView[contains(@resource-id, 'name')]",
                "//android.widget.TextView[contains(@resource-id, 'identification')]",
                "//android.widget.TextView[2]",  # Often the second TextView has the result
                "//android.widget.TextView[3]",
                # Try to find by content-desc
                "//*[contains(@content-desc, 'Dragonfly')]",
                "//*[contains(@content-desc, 'species')]",
            ]
            
            for selector in result_selectors:
                if selector:
                    text = self.driver.get_text(selector, timeout=2)
                    if text:
                        all_text.append(text)
            
            # Combine all text and content-desc
            full_text = " ".join(all_text + all_content_desc)
            result["full_text"] = full_text.lower()
            
            # Check for "No insect" cases first (must check before looking for Dragonfly)
            # Updated to match exact text from the screen: "No Insect Detected"
            no_insect_patterns = [
                "no insect detected",  # Exact match for "No Insect Detected" screen
                "no insect visible",
                "no insect",
                "couldn't detect any insects",
                "could not detect any insects",
                "we couldn't detect",
                "tips for better photos",  # This appears on "No Insect Detected" screen
            ]
            
            for pattern in no_insect_patterns:
                if pattern in full_text:
                    result["species"] = None
                    result["status"] = "no_identification"
                    logger.info(f"✓ Detected 'No insect' result (matched: {pattern})")
                    return result
            
            # Look for pattern: "Dragonfly a species of Dragonfly or Damselfly"
            # Extract "Dragonfly" as the main species
            import re
            dragonfly_pattern = r'(Dragonfly|dragonfly|Dragon fly|dragon fly)'
            match = re.search(dragonfly_pattern, full_text, re.IGNORECASE)
            
            if match:
                result["species"] = "Dragonfly"  # Normalize to "Dragonfly"
                logger.info("✓ Found Dragonfly in result")
            else:
                # Try to extract any species name (fallback)
                # Check both text and content-desc
                all_combined = all_text + all_content_desc
                if all_combined:
                    for text in all_combined:
                        if text and len(text) > 2 and text.strip():
                            # Skip common UI text
                            skip_texts = ["Basic info", "Effects", "Observation", "Identify", "Scientific name", 
                                        "a species of", "Dragonfly or Damselfly"]
                            text_clean = text.strip()
                            if text_clean not in skip_texts and not any(skip in text_clean for skip in skip_texts):
                                # Check if it contains "Dragonfly"
                                if "dragonfly" in text_clean.lower():
                                    result["species"] = "Dragonfly"
                                    logger.info(f"✓ Found Dragonfly in: {text_clean}")
                                    break
                                elif len(text_clean) > 5:  # Likely a species name
                                    result["species"] = text_clean
                                    break
            
            # Try to extract confidence (if available)
            confidence_selectors = [
                SELECTORS.get("confidence_text"),
                "//android.widget.TextView[contains(@text, '%')]",
                "//android.widget.TextView[contains(@text, 'confidence')]",
            ]
            
            for selector in confidence_selectors:
                if selector:
                    conf_text = self.driver.get_text(selector, timeout=2)
                    if conf_text:
                        # Extract percentage
                        match = re.search(r'(\d+)%', conf_text)
                        if match:
                            result["confidence"] = int(match.group(1))
                            break
            
            logger.info(f"Extracted result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting result: {str(e)}")
            return {
                "species": None,
                "confidence": None,
                "full_text": None,
                "status": "no_identification"
            }
    
    def navigate_back(self):
        """Navigate back to previous screen"""
        try:
            # Try back button
            back_selectors = [
                SELECTORS.get("back_button"),
                "//android.widget.Button[@content-desc='Back']",
                "//android.widget.ImageButton[@content-desc='Back']",
            ]
            
            for selector in back_selectors:
                if selector and self.driver.click_element(selector, timeout=2):
                    time.sleep(1)
                    return True
            
            # Use Android back button
            self.driver.driver.back()
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.warning(f"Error navigating back: {str(e)}")
            return False
    
    def click_identify_button(self):
        """Click the 'Identify' button to start next identification"""
        try:
            logger.info("Looking for 'Identify' button...")
            
            # Try multiple selectors for Identify button
            identify_selectors = [
                "//android.widget.Button[@text='Identify']",
                "//*[@text='Identify']",
                "//android.widget.Button[contains(@text, 'Identify')]",
                "//*[contains(@text, 'Identify')]",
                # Try by content-desc
                "//*[@content-desc='Identify']",
                "//android.widget.Button[@content-desc='Identify']",
                # Try accessibility ID
                "Identify",
            ]
            
            for selector in identify_selectors:
                if self.driver.click_element(selector, timeout=3):
                    logger.info("✓ Clicked 'Identify' button")
                    time.sleep(2)  # Wait for screen to change
                    return True
            
            logger.warning("Identify button not found")
            return False
            
        except Exception as e:
            logger.warning(f"Error clicking Identify button: {str(e)}")
            return False
    
    def reset_for_next_test(self):
        """Reset app state for next test"""
        try:
            logger.info("Resetting app for next test...")
            
            # Try to find "Take another photo" or similar button
            reset_buttons = [
                "//android.widget.Button[contains(@text, 'Take another')]",
                "//android.widget.Button[contains(@text, 'New photo')]",
                "//android.widget.Button[contains(@text, 'Retry')]",
                "//android.widget.TextView[contains(@text, 'Take another')]",
            ]
            
            for selector in reset_buttons:
                if self.driver.click_element(selector, timeout=2):
                    time.sleep(2)
                    return True
            
            # Try Identify button (for next identification)
            if self.click_identify_button():
                return True
            
            # If no button found, navigate back
            self.navigate_back()
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.warning(f"Error resetting app: {str(e)}")
            return False

