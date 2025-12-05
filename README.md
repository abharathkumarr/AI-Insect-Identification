# AI-Insect-Identification

A comprehensive test automation framework for AI-powered insect identification applications, featuring Android app testing and weather-based image augmentation capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Components](#components)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [Contributing](#contributing)

## 🎯 Overview

This project provides an end-to-end testing solution for AI insect identification systems, with two main components:

1. **Android Test Automation** - Automated testing framework for the AI Insect Bug Identifier Android app using Appium
2. **Dragonfly Augmentation** - Weather-based image augmentation framework for testing model robustness under various environmental conditions

The framework enables comprehensive testing of computer vision applications by generating realistic test scenarios and automating the entire testing workflow.

## 📁 Project Structure

```
AI-Insect-Identification/
├── android_test_automation/          # Android app test automation
│   ├── config.py                    # Configuration settings
│   ├── app_driver.py                # Appium driver management
│   ├── app_interactions.py          # App-specific interactions
│   ├── test_runner.py               # Main test execution
│   ├── result_classifier.py         # Result classification logic
│   ├── test_data_manager.py         # Test data management
│   ├── main.py                      # Entry point
│   ├── test_data/                   # Test cases CSV
│   ├── test_results/                # Screenshots and page sources
│   ├── reports/                     # JSON test reports
│   └── logs/                        # Log files
│
├── dragonfly_augmentation/           # Image augmentation framework
│   ├── weather_aug/                 # Core augmentation modules
│   │   ├── augmentor.py             # Weather augmentation engine
│   │   └── classifier.py            # Weather classification model
│   ├── demo.py                      # Streamlit interactive demo
│   ├── generate_samples.py          # Batch augmentation script
│   ├── samples/                     # Original and augmented images
│   │   ├── original/                # Source images
│   │   └── augmented/               # Generated augmented images
│   └── logs/                        # Augmentation logs
│
└── README.md                        # This file
```

## 🔧 Components

### 1. Android Test Automation

Automated testing framework for the **AI Insect Bug Identifier** Android app (`com.janogroupllc.pdfphotos`). Features include:

- **Automated UI Testing** using Appium and UiAutomator2
- **Image Augmentation Integration** - Test with weather-augmented images
- **Result Classification** - Categorizes test results automatically
- **Comprehensive Reporting** - JSON reports with detailed statistics
- **Screenshot Capture** - Before/after screenshots for each test case

**Key Features:**
- ✅ Automated test execution
- ✅ Support for original and augmented test images
- ✅ Result classification (correct/incorrect/no identification/uncertain)
- ✅ Detailed JSON reports with accuracy metrics
- ✅ Screenshot capture for debugging

### 2. Dragonfly Augmentation

AI-based weather image augmentation framework designed to test computer vision applications under varying environmental conditions.

**Augmentation Effects:**
- 🌧️ **Rain** - Simulates rainy conditions with water droplets
- ❄️ **Snow** - Adds snow particles and brightness effects
- 🌫️ **Fog** - Creates atmospheric scattering and reduced visibility
- 🌙 **Night** - Simulates low-light conditions with color temperature shifts
- ☀️ **Sunny** - Enhances brightness, contrast, and adds sun flare effects
- 🍂 **Autumn** - Applies warm seasonal color tones
- 📸 **Motion Blur** - Simulates camera/subject movement

**Key Features:**
- ✅ 7 weather augmentation effects with 3 intensity levels
- ✅ Weather classification model for prediction analysis
- ✅ Interactive Streamlit demo interface
- ✅ Batch processing capabilities
- ✅ Comprehensive logging system

## 🚀 Quick Start

### Android Test Automation

1. **Install dependencies:**
```bash
cd android_test_automation
pip install -r requirements.txt
```

2. **Install Appium:**
```bash
npm install -g appium
appium driver install uiautomator2
```

3. **Configure device settings in `config.py`**

4. **Start Appium server:**
```bash
appium
```

5. **Run tests:**
```bash
python main.py
```

### Dragonfly Augmentation

1. **Install dependencies:**
```bash
cd dragonfly_augmentation
pip install -r requirements.txt
```

2. **Run interactive demo:**
```bash
streamlit run demo.py
```

3. **Or generate batch samples:**
```bash
python generate_samples.py
```

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **Node.js and npm** (for Appium)
- **Android SDK** and ADB (for Android testing)
- **Android device/emulator** (for Android testing)

### Step-by-Step Installation

#### For Android Test Automation:

```bash
# 1. Install Python dependencies
cd android_test_automation
pip install -r requirements.txt

# 2. Install Appium globally
npm install -g appium
npm install -g appium-doctor

# 3. Install UiAutomator2 driver
appium driver install uiautomator2

# 4. Verify installation
appium-doctor --android

# 5. Connect Android device
adb devices

# 6. Update config.py with your device details
```

#### For Dragonfly Augmentation:

```bash
# 1. Install Python dependencies
cd dragonfly_augmentation
pip install -r requirements.txt

# 2. Verify installation
python -c "import streamlit, albumentations, cv2; print('All dependencies installed!')"
```

## 💻 Usage

### Android Test Automation

#### List Available Test Images
```bash
python main.py --list-images
```

#### Generate Augmented Test Cases
```bash
python main.py --generate-augmented-cases
```

#### Run All Tests
```bash
python main.py
```

#### Run Specific Test Case
```bash
python main.py --test-id TC001
```

#### Run Without Augmentation
```bash
python main.py --use-augmentation False
```

### Dragonfly Augmentation

#### Interactive Demo
```bash
streamlit run demo.py
```
Opens a web interface where you can:
- Upload images
- Apply weather effects in real-time
- View ML model predictions
- Download augmented images

#### Batch Processing
```bash
python generate_samples.py
```
Processes all images in `samples/original/` and generates augmented versions.

#### Programmatic Usage
```python
from weather_aug.augmentor import WeatherAugmentor
import cv2

# Initialize augmentor
augmentor = WeatherAugmentor(intensity="medium")

# Load image
image = cv2.imread("dragonfly.jpg")
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Apply effects
rainy_image = augmentor.apply_rain(image_rgb)
foggy_image = augmentor.apply_fog(image_rgb)
night_image = augmentor.apply_night(image_rgb)
```

## ✨ Features

### Android Test Automation Features

- ✅ **Automated Test Execution** - Run tests programmatically
- ✅ **Image Augmentation Support** - Test with weather-augmented images
- ✅ **Result Classification** - Automatic categorization of test results
- ✅ **Comprehensive Reporting** - JSON reports with statistics
- ✅ **Screenshot Capture** - Visual debugging support
- ✅ **Test Data Management** - CSV-based test case management
- ✅ **Device Auto-detection** - Automatic device discovery
- ✅ **Multiple Test Modes** - Original, augmented, or mixed testing

### Dragonfly Augmentation Features

- ✅ **7 Weather Effects** - Rain, Snow, Fog, Night, Sunny, Autumn, Motion Blur
- ✅ **3 Intensity Levels** - Low, Medium, High for each effect
- ✅ **Weather Classification** - ML model for prediction analysis
- ✅ **Interactive UI** - Streamlit-based demo interface
- ✅ **Batch Processing** - Process multiple images automatically
- ✅ **Comprehensive Logging** - Full audit trail of operations
- ✅ **Real-time Preview** - See effects before saving

## 📚 Documentation

### Detailed Documentation

- **[Android Test Automation README](android_test_automation/README_android_test_automation.md)** - Complete guide for Android testing framework
- **[Dragonfly Augmentation README](dragonfly_augmentation/README_dragonfly_augmentation.md)** - Detailed documentation for augmentation framework
- **[Project Report](dragonfly_augmentation/PROJECT_REPORT.md)** - Comprehensive technical report

### Configuration

#### Android Test Automation Configuration

Edit `android_test_automation/config.py`:

```python
DEVICE_CONFIG = {
    "platformName": "Android",
    "platformVersion": "15",
    "deviceName": "Pixel 9",
    "udid": "YOUR_DEVICE_UDID",  # Get via: adb devices
    "automationName": "UiAutomator2",
    "appPackage": "com.janogroupllc.pdfphotos",
    "appActivity": ".MainActivity",
}
```

#### Test Data Format

Test cases are stored in CSV format (`test_data/dragonfly_test_cases.csv`):

| test_id | image_name | expected_species | image_type | augmentation |
|---------|------------|------------------|------------|--------------|
| TC001 | dragonfly_closeup_1.jpg | dragonfly | original | none |
| TC002_AUG01 | dragonfly_closeup_1_rain.png | dragonfly | augmented | rain |

## 📋 Requirements

### Android Test Automation

```
appium>=2.0.0
selenium>=4.0.0
opencv-python>=4.7.0
pandas>=1.5.0
pillow>=9.4.0
```

### Dragonfly Augmentation

```
streamlit>=1.20.0
albumentations>=1.3.0
opencv-python-headless>=4.7.0
pillow>=9.4.0
numpy>=1.23.0
```

## 🧪 Test Results

### Android Test Automation

Test results are saved in:
- **JSON Reports:** `android_test_automation/reports/test_report_YYYYMMDD_HHMMSS.json`
- **Screenshots:** `android_test_automation/test_results/screenshot_*.png`
- **Logs:** `android_test_automation/logs/android_test_automation.log`

### Dragonfly Augmentation

Augmented images are saved in:
- **Augmented Images:** `dragonfly_augmentation/samples/augmented/`
- **Logs:** `dragonfly_augmentation/logs/augmentations.log`

## 🔍 Troubleshooting

### Android Test Automation Issues

**Appium Connection Issues:**
- Ensure Appium server is running: `appium`
- Check device connection: `adb devices`
- Verify device UDID in `config.py`

**Element Not Found:**
- App UI may have changed - update selectors in `config.py`
- Use `adb shell uiautomator dump` to inspect app UI
- Check screenshots in `test_results/` folder

**Image Upload Issues:**
- Ensure images are copied to device: `adb push image.jpg /sdcard/Download/`
- Check app permissions (camera, storage)
- Try Intent method if gallery method fails

### Dragonfly Augmentation Issues

**Import Errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

**Streamlit Not Starting:**
- Verify Streamlit installation: `pip install streamlit`
- Check port availability (default: 8501)

## 🤝 Contributing

This is a research/educational project. For improvements or bug fixes:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational purposes as part of CMPE 287 - Software Testing course.

## 👤 Author

**CMPE 287 - Software Testing Project**

- Course: CMPE 287 - Software Testing
- Project: AI Insect Identification Test Automation Framework
- Date: December 2024

## 🙏 Acknowledgments

- **Albumentations** - Image augmentation library
- **Appium** - Mobile app automation framework
- **Streamlit** - Interactive web app framework
- **OpenCV** - Computer vision library

---

For detailed documentation, please refer to the component-specific README files:
- [Android Test Automation Documentation](android_test_automation/README_android_test_automation.md)
- [Dragonfly Augmentation Documentation](dragonfly_augmentation/README_dragonfly_augmentation.md)
