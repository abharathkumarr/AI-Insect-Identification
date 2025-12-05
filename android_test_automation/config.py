"""
Configuration file for Android App Test Automation
AI Insect Bug Identifier App Testing
"""

# App Configuration
APP_PACKAGE = "com.janogroupllc.pdfphotos"  # AI Insect Bug Identifier
# Launcher activity resolved via:
# adb shell cmd package resolve-activity -a android.intent.action.MAIN \
#   -c android.intent.category.LAUNCHER com.janogroupllc.pdfphotos
APP_ACTIVITY = "com.janogroupllc.PdfPhotos.MainActivity"

# Appium Server Configuration
APPIUM_SERVER_URL = "http://127.0.0.1:4723"

# Device Configuration (Update these based on your device)
DEVICE_CONFIG = {
    "platformName": "Android",
    "platformVersion": "16",  # Detected: Android 12
    "deviceName": "sdk_gphone64_arm64",  # Detected: OnePlus EB2101
    "udid": "emulator-5554",  # Detected device UDID
    "automationName": "UiAutomator2",
    "appPackage": APP_PACKAGE,
    "appActivity": APP_ACTIVITY,
    "noReset": False,  # Set to True to keep app data between runs
    "fullReset": False,  # Set to True to uninstall app before each run
    "skipServerInstallation": True,  # Skip server installation if already installed
    "skipUnlock": True,  # Skip unlock if device is already unlocked
    "autoGrantPermissions": True,  # Automatically grant permissions
    "disableWindowAnimation": False,  # Don't disable animations (can cause permission issues)
}

# Timeouts (in seconds) - ULTRA FAST
IMPLICIT_WAIT = 5   # Minimal implicit wait
EXPLICIT_WAIT = 2   # Fast explicit wait
ELEMENT_WAIT = 1   # Fail fast - 1 second max per element

# Test Data Paths
TEST_DATA_DIR = "test_data"
ORIGINAL_IMAGES_DIR = "../dragonfly_augmentation/samples/original"
AUGMENTED_IMAGES_DIR = "../dragonfly_augmentation/samples/augmented"
TEST_RESULTS_DIR = "test_results"
TEST_REPORTS_DIR = "reports"

# Test Data File
TEST_CASES_CSV = f"{TEST_DATA_DIR}/dragonfly_test_cases.csv"

# Expected Dragonfly Species (for validation)
# Update this list based on what the app should identify
EXPECTED_DRAGONFLY_SPECIES = [
    "darner",
    "skimmer",
    "dragonfly",  # Keep as fallback
    "dragon fly",
    "aeshnidae",  # Darner family
    "libellulidae",  # Skimmer family
    "aeshna",  # Darner genus
    "libellula",  # Skimmer genus
    "odonata",  # Order
]

# Result Classification Keywords
UNCERTAIN_KEYWORDS = [
    "uncertain",
    "maybe",
    "possibly",
    "likely",
    "probably",
    "could be",
    "might be",
    "similar to",
]

NO_IDENTIFICATION_KEYWORDS = [
    "not found",
    "no match",
    "unable to identify",
    "cannot identify",
    "no result",
    "try again",
    "no insect detected",
    "invalid",
]

# XPath Selectors (These may need to be updated based on actual app UI)
# You'll need to inspect the app UI to get correct selectors
SELECTORS = {
    "camera_button": "//android.widget.Button[@content-desc='Camera']",
    "gallery_button": "//android.widget.Button[@content-desc='Gallery']",
    "photo_icon": "//android.widget.ImageView[contains(@content-desc, 'photo') or contains(@content-desc, 'image')]",
    "result_text": "//android.widget.TextView[contains(@resource-id, 'result') or contains(@resource-id, 'species')]",
    "species_name": "//android.widget.TextView[contains(@resource-id, 'species')]",
    "confidence_text": "//android.widget.TextView[contains(@resource-id, 'confidence')]",
    "back_button": "//android.widget.Button[@content-desc='Back']",
    "retry_button": "//android.widget.Button[@text='Retry' or @content-desc='Retry']",
}

# Image Upload Methods
IMAGE_UPLOAD_METHOD = "gallery"  # Options: "gallery" or "camera"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/android_test_automation.log"

