"""
Main Entry Point for Android App Test Automation
AI Insect Bug Identifier - Dragonfly Testing
"""

import argparse
import logging
import sys
from pathlib import Path

from test_runner import TestRunner
from test_data_manager import TestDataManager
from config import LOG_LEVEL, LOG_FILE

# Setup logging
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Android App Test Automation for AI Insect Bug Identifier"
    )
    parser.add_argument(
        "--use-augmentation",
        action="store_true",
        default=True,
        help="Use augmented images for testing (default: True)"
    )
    parser.add_argument(
        "--test-id",
        type=str,
        help="Run specific test case by ID"
    )
    parser.add_argument(
        "--generate-augmented-cases",
        action="store_true",
        help="Generate test cases for augmented images"
    )
    parser.add_argument(
        "--list-images",
        action="store_true",
        help="List available test images"
    )
    parser.add_argument(
        "--manual-mode",
        action="store_true",
        help="Manual mode: Automation launches app and handles permissions, you select image manually, then automation continues"
    )
    
    args = parser.parse_args()
    
    try:
        data_manager = TestDataManager()
        
        # List images if requested
        if args.list_images:
            print("\nAvailable Original Images:")
            for img in data_manager.list_available_images("original"):
                print(f"  - {img}")
            print("\nAvailable Augmented Images:")
            for img in data_manager.list_available_images("augmented"):
                print(f"  - {img}")
            return
        
        # Generate augmented test cases if requested
        if args.generate_augmented_cases:
            logger.info("Generating augmented test cases...")
            augmentation_effects = ["rain", "snow", "fog", "night", "sunny", "autumn", "motion_blur"]
            
            original_images = data_manager.list_available_images("original")
            for img in original_images:
                if "dragonfly" in img.lower():
                    data_manager.add_augmented_test_cases(img, augmentation_effects)
            
            logger.info("Augmented test cases generated!")
            return
        
        # Initialize test runner
        logger.info("Initializing test runner...")
        runner = TestRunner(use_augmentation=args.use_augmentation, manual_mode=args.manual_mode)
        
        # Setup
        if not runner.setup(skip_onboarding=args.manual_mode):
            logger.error("Failed to setup test environment")
            return 1
        
        try:
            # Load test cases
            test_cases = data_manager.load_test_cases()
            
            if not test_cases:
                logger.error("No test cases found! Create test cases first.")
                return 1
            
            # Filter by test ID if specified
            if args.test_id:
                test_cases = [tc for tc in test_cases if tc.get("test_id") == args.test_id]
                if not test_cases:
                    logger.error(f"Test case {args.test_id} not found!")
                    return 1
            
            # Run tests
            logger.info(f"Running {len(test_cases)} test case(s)...")
            results = runner.run_all_tests(test_cases)
            
            # Generate report (even if interrupted)
            if results:
                print("\n" + "=" * 60)
                print("📊 GENERATING FINAL REPORT...")
                print("=" * 60 + "\n")
                report = runner.generate_report(results)
                logger.info("Test execution completed!")
            else:
                print("\n⚠️  No test results to report.")
                logger.warning("No test results to generate report")
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("⚠️  INTERRUPTED BY USER (Ctrl+C)")
            print("=" * 60)
            print("Generating summary of completed tests...")
            print("=" * 60 + "\n")
            
            # Generate report for completed tests
            # Use test_results from runner which should have all completed tests
            if hasattr(runner, 'test_results') and runner.test_results:
                print(f"Found {len(runner.test_results)} completed test(s)")
                report = runner.generate_report(runner.test_results)
                logger.info(f"Summary generated for {len(runner.test_results)} completed tests")
            else:
                print("⚠️  No tests were completed yet.")
                logger.warning("No test results to generate report")
            
            return 0
            
        finally:
            # Teardown
            try:
                runner.teardown()
            except:
                pass
    except Exception as e:
        logger.error(f"Error during test execution: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())



