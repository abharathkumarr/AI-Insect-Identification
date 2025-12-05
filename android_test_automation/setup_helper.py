"""
Setup Helper Script
Helps configure the test automation environment
"""

import subprocess
import sys
from pathlib import Path


def check_adb():
    """Check if ADB is installed and device is connected"""
    print("Checking ADB...")
    try:
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ ADB found: {result.stdout.strip()}")
        else:
            print("✗ ADB not found. Please install Android SDK Platform Tools")
            return False
        
        # Check for connected devices
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        devices = [line for line in lines if line.strip() and 'device' in line]
        
        if devices:
            print(f"✓ Found {len(devices)} connected device(s):")
            for device in devices:
                print(f"  - {device.split()[0]}")
            return True
        else:
            print("✗ No devices connected. Please connect your Android device/emulator")
            return False
            
    except FileNotFoundError:
        print("✗ ADB not found. Please install Android SDK Platform Tools")
        return False
    except Exception as e:
        print(f"✗ Error checking ADB: {str(e)}")
        return False


def check_appium():
    """Check if Appium is installed"""
    print("\nChecking Appium...")
    try:
        result = subprocess.run(
            ["appium", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Appium found: {result.stdout.strip()}")
            return True
        else:
            print("✗ Appium not found. Install with: npm install -g appium")
            return False
    except FileNotFoundError:
        print("✗ Appium not found. Install with: npm install -g appium")
        print("  Also install UiAutomator2 driver: appium driver install uiautomator2")
        return False
    except Exception as e:
        print(f"✗ Error checking Appium: {str(e)}")
        return False


def check_python_packages():
    """Check if required Python packages are installed"""
    print("\nChecking Python packages...")
    required_packages = [
        "appium",
        "selenium",
        "opencv-python-headless",
        "pillow",
        "numpy",
        "albumentations",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - Install with: pip install {package}")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages. Install with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True


def get_device_info():
    """Get device information for configuration"""
    print("\nGetting device information...")
    try:
        # Get device model
        result = subprocess.run(
            ["adb", "shell", "getprop", "ro.product.model"],
            capture_output=True,
            text=True
        )
        device_name = result.stdout.strip() if result.returncode == 0 else "Unknown"
        
        # Get Android version
        result = subprocess.run(
            ["adb", "shell", "getprop", "ro.build.version.release"],
            capture_output=True,
            text=True
        )
        platform_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
        
        # Get UDID
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')[1:]
        udid = lines[0].split()[0] if lines else "Unknown"
        
        print(f"Device Name: {device_name}")
        print(f"Platform Version: {platform_version}")
        print(f"UDID: {udid}")
        
        return {
            "device_name": device_name,
            "platform_version": platform_version,
            "udid": udid
        }
        
    except Exception as e:
        print(f"Error getting device info: {str(e)}")
        return None


def check_app_installed(package_name="com.janogroupllc.pdfphotos"):
    """Check if the app is installed on device"""
    print(f"\nChecking if app is installed ({package_name})...")
    try:
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages", package_name],
            capture_output=True,
            text=True
        )
        if package_name in result.stdout:
            print(f"✓ App is installed")
            return True
        else:
            print(f"✗ App not found. Please install AI Insect Bug Identifier app")
            return False
    except Exception as e:
        print(f"Error checking app: {str(e)}")
        return False


def main():
    """Run all checks"""
    print("="*60)
    print("Android Test Automation Setup Check")
    print("="*60)
    
    checks = {
        "ADB": check_adb(),
        "Appium": check_appium(),
        "Python Packages": check_python_packages(),
        "App Installed": check_app_installed(),
    }
    
    device_info = get_device_info()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check_name}: {status}")
    
    if device_info:
        print("\nDevice Information (update config.py with these values):")
        print(f"  deviceName: \"{device_info['device_name']}\"")
        print(f"  platformVersion: \"{device_info['platform_version']}\"")
        print(f"  udid: \"{device_info['udid']}\"")
    
    if all_passed:
        print("\n✓ All checks passed! You're ready to run tests.")
        print("\nNext steps:")
        print("1. Update config.py with your device information (if needed)")
        print("2. Run: python main.py --list-images")
        print("3. Run: python main.py --generate-augmented-cases")
        print("4. Run: python main.py")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())




