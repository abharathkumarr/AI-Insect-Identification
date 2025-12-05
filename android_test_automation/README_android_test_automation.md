# Android App Test Automation
## AI Insect Bug Identifier - Dragonfly Testing

This framework automates testing of the **AI Insect Bug Identifier** Android app (com.janogroupllc.pdfphotos) for dragonfly identification, with integrated image augmentation support.

## Features

- ✅ **Automated Android App Testing** using Appium
- ✅ **Image Augmentation Integration** - Test with weather-augmented images
- ✅ **Result Classification** - Categorizes results as:
  - `correct_species` - App correctly identified dragonfly
  - `incorrect_species` - App identified wrong species
  - `no_identification` - App couldn't identify
  - `uncertain` - App provided uncertain/low-confidence result
- ✅ **Test Data Management** - CSV-based test case management
- ✅ **Comprehensive Reporting** - JSON reports with detailed statistics
- ✅ **Screenshot Capture** - Before/after screenshots for each test

## Prerequisites

1. **Android Device/Emulator** connected via ADB
2. **Appium Server** running (default: http://127.0.0.1:4723)
3. **Python 3.8+**
4. **AI Insect Bug Identifier App** installed on device

## Installation

1. **Install Python dependencies:**
```bash
cd android_test_automation
pip install -r requirements.txt
```

2. **Install Appium Server:**
```bash
npm install -g appium
npm install -g appium-doctor
appium-doctor --android
```

3. **Install UiAutomator2 driver:**
```bash
appium driver install uiautomator2
```

4. **Start Appium Server:**
```bash
appium
```

## Configuration

Edit `config.py` with your device information:

```python
DEVICE_CONFIG = {
    "platformName": "Android",
    "platformVersion": "15",  # Your Android version
    "deviceName": "Pixel 9",  # Your device name
    "udid": "YOUR_DEVICE_UDID",  # Get via: adb devices
    "automationName": "UiAutomator2",
    "appPackage": "com.janogroupllc.pdfphotos",
    "appActivity": ".MainActivity",
}
```

**Get Device UDID:**
```bash
adb devices
```

## Usage

### 1. List Available Test Images
```bash
python main.py --list-images
```

### 2. Generate Augmented Test Cases
```bash
python main.py --generate-augmented-cases
```

This creates test cases for all augmented images (rain, snow, fog, night, sunny, autumn, motion_blur).

### 3. Run All Tests
```bash
python main.py
```

### 4. Run Specific Test Case
```bash
python main.py --test-id TC001
```

### 5. Run Without Augmentation
```bash
python main.py --use-augmentation False
```

## Test Data Structure

Test cases are stored in `test_data/dragonfly_test_cases.csv`:

| test_id | image_name | expected_species | image_type | augmentation |
|---------|------------|------------------|------------|--------------|
| TC001 | dragonfly_closeup_1.jpg | dragonfly | original | none |
| TC002_AUG01 | dragonfly_closeup_1_rain.png | dragonfly | augmented | rain |

## Test Results

Results are saved in:
- **JSON Reports:** `reports/test_report_YYYYMMDD_HHMMSS.json`
- **Screenshots:** `test_results/screenshot_before_*.png` and `screenshot_after_*.png`
- **Logs:** `logs/android_test_automation.log`

## Report Structure

```json
{
  "timestamp": "2025-11-29T...",
  "total_tests": 10,
  "summary": {
    "total": 10,
    "correct_species": 7,
    "incorrect_species": 1,
    "no_identification": 1,
    "uncertain": 1,
    "accuracy": 87.5
  },
  "test_results": [...],
  "detailed_summary": {...}
}
```

## Integration with Augmentation Framework

The test automation integrates with the existing `dragonfly_augmentation` framework:

1. **Original images** are tested first
2. **Augmented images** (rain, snow, fog, etc.) are tested to evaluate robustness
3. Results show how weather conditions affect app performance

## Troubleshooting

### Appium Connection Issues
- Ensure Appium server is running: `appium`
- Check device connection: `adb devices`
- Verify device UDID in `config.py`

### Element Not Found
- App UI may have changed - update selectors in `config.py`
- Use `adb shell uiautomator dump` to inspect app UI
- Check screenshots in `test_results/` folder

### Image Upload Issues
- Ensure images are copied to device: `adb push image.jpg /sdcard/Download/`
- Check app permissions (camera, storage)
- Try Intent method if gallery method fails

## Project Structure

```
android_test_automation/
├── config.py                 # Configuration settings
├── app_driver.py             # Appium driver management
├── app_interactions.py       # App-specific interactions
├── result_classifier.py      # Result classification logic
├── test_data_manager.py      # Test data management
├── test_runner.py            # Main test execution
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── test_data/                # Test cases CSV
├── test_results/             # Screenshots
├── reports/                  # JSON reports
└── logs/                     # Log files
```

## Next Steps

1. **Update Device Configuration** in `config.py`
2. **Create Test Cases** or use `--generate-augmented-cases`
3. **Run Tests** and review reports
4. **Update Selectors** if app UI changes (inspect with `adb shell uiautomator dump`)

## Support

For issues or questions:
- Check logs: `logs/android_test_automation.log`
- Review screenshots: `test_results/`
- Inspect app UI: `adb shell uiautomator dump /sdcard/ui_dump.xml`



