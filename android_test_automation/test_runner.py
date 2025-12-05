"""
Main Test Runner for Android App Automation
Integrates augmentation framework with app testing
"""

import logging
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from app_driver import AppDriver
from app_interactions import AppInteractions
from result_classifier import ResultClassifier
from test_data_manager import TestDataManager
from config import TEST_RESULTS_DIR, TEST_REPORTS_DIR

# Import augmentation framework
import sys
from pathlib import Path
augmentation_path = Path(__file__).parent.parent / "dragonfly_augmentation"
sys.path.insert(0, str(augmentation_path))
try:
    from weather_aug.augmentor import WeatherAugmentor
except ImportError:
    WeatherAugmentor = None
    logger.warning("Could not import WeatherAugmentor. Augmentation features disabled.")

logger = logging.getLogger(__name__)


class TestRunner:
    """Main test runner that orchestrates the entire testing process"""
    
    def __init__(self, use_augmentation: bool = True, manual_mode: bool = False):
        """
        Initialize test runner
        
        Args:
            use_augmentation: Whether to use augmented images for testing
            manual_mode: If True, user handles onboarding and image selection manually
        """
        self.driver = AppDriver()
        self.app_interactions = None
        self.classifier = ResultClassifier()
        self.data_manager = TestDataManager()
        self.use_augmentation = use_augmentation
        self.manual_mode = manual_mode
        self.augmentor = WeatherAugmentor(intensity="medium") if (use_augmentation and WeatherAugmentor) else None
        
        # Create results directories
        Path(TEST_RESULTS_DIR).mkdir(exist_ok=True)
        Path(TEST_REPORTS_DIR).mkdir(exist_ok=True)
        
        self.test_results = []
    
    def setup(self, skip_onboarding: bool = False):
        """Setup test environment"""
        try:
            logger.info("Setting up test environment...")
            
            # Start Appium driver
            self.driver.start_driver()
            
            # Initialize app interactions
            self.app_interactions = AppInteractions(self.driver)
            
            if not skip_onboarding:
                # Handle permissions and onboarding - ULTRA FAST
                time.sleep(0.5)  # Minimal wait for app to load
                self.app_interactions.skip_onboarding()
                self.app_interactions.handle_permissions()  # Fast check only
            else:
                # Manual mode: Just launch app and handle permissions
                logger.info("=" * 60)
                logger.info("MANUAL MODE ENABLED")
                logger.info("=" * 60)
                logger.info("1. App will be launched")
                logger.info("2. Permissions will be handled automatically")
                logger.info("3. YOU need to:")
                logger.info("   - Click 'Get Started' button")
                logger.info("   - Choose an image from gallery")
                logger.info("4. Automation will continue after image is selected")
                logger.info("=" * 60)
                time.sleep(2)  # Give user time to read
                
                # Just handle permissions
                self.app_interactions.handle_permissions()
                logger.info("✓ Permissions handled")
                logger.info("⏳ Waiting for you to click 'Get Started' and select an image...")
            
            logger.info("Test environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error during setup: {str(e)}")
            return False
    
    def teardown(self):
        """Cleanup after tests"""
        try:
            logger.info("Tearing down test environment...")
            if self.driver:
                self.driver.stop_driver()
            logger.info("Test environment torn down")
        except Exception as e:
            logger.error(f"Error during teardown: {str(e)}")
    
    def run_single_test(self, test_case: Dict) -> Dict:
        """
        Run a single test case
        
        Args:
            test_case: Dict with test case information
            
        Returns:
            Dict with test result
        """
        test_id = test_case.get("test_id", "UNKNOWN")
        image_name = test_case.get("image_name", "")
        expected_species = test_case.get("expected_species", "dragonfly")
        image_type = test_case.get("image_type", "original")
        augmentation = test_case.get("augmentation", "none")
        
        logger.info(f"Running test case: {test_id} - {image_name}")
        
        result = {
            "test_id": test_id,
            "image_name": image_name,
            "image_type": image_type,
            "augmentation": augmentation,
            "expected_species": expected_species,
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "app_result": None,
            "classification": None,
            "error": None,
        }
        
        try:
            # Get image path
            image_path = self.data_manager.get_image_path(image_name, image_type)
            
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Take screenshot before test
            screenshot_before = f"{TEST_RESULTS_DIR}/screenshot_before_{test_id}.png"
            self.driver.take_screenshot(screenshot_before)
            
            if self.manual_mode:
                # Manual mode: Wait for user to select image, then process
                print("\n" + "=" * 60)
                print("📸 PROCESSING TEST IMAGE...")
                print("=" * 60)
                print(f"Test Case: {test_id}")
                print(f"Expected Species: {expected_species}")
                print(f"Image: {image_name}")
                print("=" * 60)
                print("Taking image as input...")
                print("Automation will detect when image is processed and extract results.")
                print("=" * 60 + "\n")
                
                # Wait for user to select image - detect when scanning starts or result appears
                self._wait_for_image_selection()
                
                # Wait for scanning/progress to complete
                self.app_interactions.wait_for_scanning()
            else:
                # Automated mode: Upload image to app
                logger.info(f"Uploading image: {image_path}")
                
                # Try gallery method first
                if self.app_interactions.open_gallery():
                    if self.app_interactions.select_image_from_gallery(str(image_path)):
                        logger.info("Image uploaded via gallery")
                    else:
                        # Fallback to Intent method
                        logger.info("Trying Intent method...")
                        self.app_interactions.upload_image_via_intent(str(image_path))
                else:
                    # Use Intent method directly
                    self.app_interactions.upload_image_via_intent(str(image_path))
                
                # Wait for scanning/progress to complete
                self.app_interactions.wait_for_scanning()
            
            # Handle advertisement if present
            self.app_interactions.handle_advertisement()
            
            # Extract result
            print("\n" + "=" * 60)
            print("📊 EXTRACTING RESULT...")
            print("=" * 60)
            app_result = self.app_interactions.extract_result()
            result["app_result"] = app_result
            
            # Classify result
            classification = self.classifier.classify_result(app_result, expected_species)
            result["classification"] = classification
            result["status"] = "passed" if classification["category"] == "correct_species" else "failed"
            
            # Take screenshot after test
            screenshot_after = f"{TEST_RESULTS_DIR}/screenshot_after_{test_id}.png"
            self.driver.take_screenshot(screenshot_after)
            
            # Print result to terminal
            print("\n" + "=" * 60)
            print("✅ TEST RESULT")
            print("=" * 60)
            print(f"Test ID: {test_id}")
            print(f"Image: {image_name}")
            print(f"Expected Species: {expected_species}")
            print("-" * 60)
            app_species = app_result.get('species', 'Not found')
            if app_species is None:
                app_species = "No Insect Visible"
            print(f"App Result: {app_species}")
            full_text_preview = app_result.get('full_text', 'N/A')
            if len(full_text_preview) > 100:
                full_text_preview = full_text_preview[:100] + "..."
            print(f"Full Text: {full_text_preview}")
            print("-" * 60)
            print(f"Classification: {classification['category']}")
            print(f"Output: {classification['app_species']}")
            print(f"Reason: {classification['reason']}")
            print("=" * 60 + "\n")
            
            logger.info(f"Test {test_id} completed: {classification['category']}")
            
            # Save result immediately to self.test_results (so it's available even if interrupted)
            # This ensures the result is saved even if Ctrl+C is pressed right after
            if result not in self.test_results:
                self.test_results.append(result)
            
            # In manual mode, click Identify button for next test (but don't wait for next image yet)
            if self.manual_mode:
                print("\n" + "=" * 60)
                print("🔄 PREPARING FOR NEXT TEST...")
                print("=" * 60)
                print("Selecting next test image...")
                print("=" * 60 + "\n")
                
                if self.app_interactions.click_identify_button():
                    time.sleep(2)  # Wait for screen to change
                    logger.info("✓ Identify button clicked - ready for next test")
                else:
                    logger.warning("Could not click Identify button - you may need to click it manually")
            else:
                # Reset for next test (automated mode)
                self.app_interactions.reset_for_next_test()
                time.sleep(2)
            
        except KeyboardInterrupt:
            # If interrupted during test, save what we have
            logger.info(f"Test {test_id} interrupted by user")
            result["status"] = "interrupted"
            result["error"] = "Test interrupted by user"
            # Save partial result
            if result not in self.test_results:
                self.test_results.append(result)
            raise  # Re-raise to be caught by outer handler
            
        except Exception as e:
            logger.error(f"Error in test {test_id}: {str(e)}")
            result["error"] = str(e)
            result["status"] = "error"
            # Save error result
            if result not in self.test_results:
                self.test_results.append(result)
        
        return result
    
    def run_all_tests(self, test_cases: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Run all test cases
        
        Args:
            test_cases: Optional list of test cases (loads from file if not provided)
            
        Returns:
            List of test results
        """
        if test_cases is None:
            test_cases = self.data_manager.load_test_cases()
        
        if not test_cases:
            logger.error("No test cases found!")
            return []
        
        logger.info(f"Running {len(test_cases)} test cases...")
        print("\n" + "=" * 60)
        print("ℹ️  TIP: Press Ctrl+C at any time to stop and see summary")
        print("=" * 60 + "\n")
        
        results = []
        try:
            for i, test_case in enumerate(test_cases, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"Test {i}/{len(test_cases)}: {test_case.get('test_id')}")
                logger.info(f"{'='*60}")
                
                # In manual mode, for first test, user needs to select image
                # For subsequent tests, we click Identify button after previous test
                # So we wait for image selection before processing
                if self.manual_mode and i == 1:
                    print("\n" + "=" * 60)
                    print("📸 STARTING TEST AUTOMATION")
                    print("=" * 60)
                    print("Initializing app and preparing for image processing...")
                    print("=" * 60 + "\n")
                
                result = self.run_single_test(test_case)
                # Add to results list (result is already saved to self.test_results in run_single_test)
                if result:
                    results.append(result)
                
                # In manual mode, don't pause - the Identify button click and wait_for_image_selection
                # in run_single_test handles the timing
                if not self.manual_mode:
                    # Brief pause between tests (automated mode)
                    time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("⚠️  TEST EXECUTION INTERRUPTED BY USER")
            print("=" * 60)
            # Use self.test_results which has all completed tests
            completed_count = len(self.test_results)
            print(f"Tests completed so far: {completed_count}/{len(test_cases)}")
            print("=" * 60 + "\n")
            logger.info(f"Test execution interrupted. Completed {completed_count}/{len(test_cases)} tests")
            # Return all completed results
            return self.test_results
        
        return results
    
    def generate_report(self, results: Optional[List[Dict]] = None) -> Dict:
        """
        Generate test report
        
        Args:
            results: Optional list of results (uses self.test_results if not provided)
            
        Returns:
            Dict with report data
        """
        if results is None:
            results = self.test_results
        
        if not results:
            logger.warning("No test results to generate report")
            return {}
        
        # Get classifications (filter out None values)
        classifications = [r["classification"] for r in results if r.get("classification") is not None]
        
        # Get summary
        summary = self.classifier.get_category_summary(classifications)
        
        # Generate report (safely handle None classifications)
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "summary": summary,
            "test_results": results,
            "detailed_summary": {
                "correct_species": [r for r in results if r.get("classification") and r.get("classification", {}).get("category") == "correct_species"],
                "incorrect_species": [r for r in results if r.get("classification") and r.get("classification", {}).get("category") == "incorrect_species"],
                # Combine uncertain and no_identification
                "no_identification": [r for r in results if r.get("classification") and r.get("classification", {}).get("category") in ["no_identification", "uncertain"]],
                "uncertain": [],  # Keep for backward compatibility but empty
                "errors": [r for r in results if r.get("status") == "error"],
            }
        }
        
        # Save report to file
        report_file = Path(TEST_REPORTS_DIR) / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to: {report_file}")
        
        # Print summary
        self._print_summary(summary, report)
        
        return report
    
    def _wait_for_image_selection(self, max_wait=300):
        """
        Wait for user to select an image in manual mode
        Detects when image selection is complete by looking for:
        - Scanning screen ("Finalizing profile...")
        - Result screen (has "Dragonfly" or "No Insect Detected")
        """
        try:
            logger.info("Waiting for image to be processed...")
            print("⏳ Processing image...")
            print("   (Waiting for app to process the image)")
            start_time = time.time()
            check_count = 0
            consecutive_errors = 0
            max_consecutive_errors = 5  # If we can't get page source 5 times in a row, proceed
            
            while time.time() - start_time < max_wait:
                check_count += 1
                page_source = None
                
                try:
                    page_source = self.driver.get_page_source()
                    consecutive_errors = 0  # Reset error count on success
                except Exception as e:
                    consecutive_errors += 1
                    # If instrumentation keeps failing, the app might be on result screen already
                    if consecutive_errors >= max_consecutive_errors:
                        logger.warning(f"Instrumentation failed {consecutive_errors} times - app may be on result screen")
                        print("⚠️  App instrumentation unavailable - assuming result screen is ready")
                        # Try to extract result anyway - it might work
                        time.sleep(2)  # Give app a moment
                        return True
                    # Wait a bit longer before retrying
                    time.sleep(3)
                    continue
                
                if page_source:
                    # Check if scanning has started (image was selected)
                    scanning_indicators = [
                        "Finalizing profile",
                        "Finalizing",
                        "Scanning",
                        "Processing",
                    ]
                    
                    # Check if result screen appeared (image was already processed)
                    # Updated to include "No Insect Detected" (exact text from the screen)
                    result_indicators = [
                        "Dragonfly",
                        "No Insect Detected",  # Exact text from the screen
                        "No Insect",
                        "No insect visible",
                        "No insect detected",
                        "species of",
                        "Damselfly",
                        "Tips for Better Photos",  # This appears on "No Insect Detected" screen
                    ]
                    
                    # Check if we're on a screen that suggests image was selected
                    if any(ind in page_source for ind in scanning_indicators):
                        logger.info("✓ Image selection detected - scanning started")
                        print("✓ Image detected! Processing...")
                        return True
                    
                    if any(ind in page_source for ind in result_indicators):
                        logger.info("✓ Image selection detected - result screen appeared")
                        print("✓ Image detected! Result screen found.")
                        return True
                
                # Show progress every 10 seconds
                if check_count % 5 == 0:
                    elapsed = int(time.time() - start_time)
                    print(f"   Still waiting... ({elapsed}s elapsed)")
                
                # Check every 2 seconds
                time.sleep(2)
            
            logger.warning("Timeout waiting for image selection - proceeding anyway")
            print("⚠️  Timeout waiting for image - proceeding anyway")
            return True
            
        except Exception as e:
            logger.warning(f"Error waiting for image selection: {str(e)}")
            print(f"⚠️  Error waiting for image: {str(e)}")
            # Proceed anyway - user may have selected image
            return True
    
    def _print_summary(self, summary: Dict, report: Dict):
        """Print test summary to console"""
        print("\n" + "="*60)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Tests Executed: {summary['total']}")
        print(f"✓ Correct Species: {summary['correct_species']}")
        print(f"✗ Incorrect Species: {summary['incorrect_species']}")
        print(f"✗ No Identification: {summary['no_identification']}")
        
        # Show accuracy (calculated as correct / total)
        if summary['total'] > 0:
            print(f"📈 Accuracy: {summary['accuracy']}% (Correct: {summary['correct_species']}/{summary['total']})")
        else:
            print(f"📈 Accuracy: N/A (no tests executed)")
        
        print("="*60)
        
        # Print detailed breakdown
        print("\n📋 DETAILED BREAKDOWN:")
        print("-" * 60)
        
        if summary['correct_species'] > 0:
            print(f"\n✓ Correct Species ({summary['correct_species']}):")
            for result in report['detailed_summary']['correct_species']:
                classification = result.get('classification', {})
                expected = classification.get('expected_species', 'unknown')
                app_species = classification.get('app_species', 'unknown')
                print(f"   • {result['test_id']}: {expected} → {app_species}")
        
        if summary['incorrect_species'] > 0:
            print(f"\n✗ Incorrect Species ({summary['incorrect_species']}):")
            for result in report['detailed_summary']['incorrect_species']:
                classification = result.get('classification', {})
                print(f"   • {result['test_id']}: Expected '{classification.get('expected_species')}', "
                      f"Got '{classification.get('app_species')}'")
        
        # Combine uncertain and no_identification (they're the same)
        no_id_count = summary['no_identification']
        uncertain_results = report['detailed_summary'].get('uncertain', [])
        no_id_results = report['detailed_summary'].get('no_identification', [])
        all_no_id_results = uncertain_results + no_id_results
        
        if no_id_count > 0:
            print(f"\n✗ No Identification ({no_id_count}):")
            for result in all_no_id_results:
                classification = result.get('classification', {})
                app_species = classification.get('app_species', 'no_insect_visible') if classification else 'no_insect_visible'
                print(f"   • {result['test_id']}: {app_species}")
        
        if len(report.get('detailed_summary', {}).get('errors', [])) > 0:
            print(f"\n⚠️  Errors ({len(report['detailed_summary']['errors'])}):")
            for result in report['detailed_summary']['errors']:
                print(f"   • {result['test_id']}: {result.get('error', 'Unknown error')}")
        
        print("=" * 60)

