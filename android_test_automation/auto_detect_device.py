"""
Auto-detect Android device and update config.py
"""

import subprocess
import re
import sys
from pathlib import Path

def run_adb_command(command):
    """Run ADB command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def get_connected_devices():
    """Get list of connected devices"""
    output = run_adb_command("adb devices")
    if not output:
        return []
    
    devices = []
    lines = output.split('\n')[1:]  # Skip header
    for line in lines:
        if line.strip() and 'device' in line:
            parts = line.split()
            if len(parts) >= 2:
                devices.append({
                    'udid': parts[0],
                    'status': parts[1]
                })
    return devices

def get_device_info(udid):
    """Get device information"""
    info = {}
    
    # Get Android version
    version = run_adb_command(f"adb -s {udid} shell getprop ro.build.version.release")
    info['platform_version'] = version if version else "Unknown"
    
    # Get device model
    model = run_adb_command(f"adb -s {udid} shell getprop ro.product.model")
    info['device_name'] = model if model else "Unknown"
    
    # Get manufacturer
    manufacturer = run_adb_command(f"adb -s {udid} shell getprop ro.product.manufacturer")
    info['manufacturer'] = manufacturer if manufacturer else "Unknown"
    
    # Get Android SDK version
    sdk = run_adb_command(f"adb -s {udid} shell getprop ro.build.version.sdk")
    info['sdk_version'] = sdk if sdk else "Unknown"
    
    return info

def update_config_file(device_info, udid):
    """Update config.py with device information"""
    config_path = Path(__file__).parent / "config.py"
    
    if not config_path.exists():
        print(f"Error: config.py not found at {config_path}")
        return False
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update device configuration
        replacements = {
            r'"platformVersion":\s*"[^"]*"': f'"platformVersion": "{device_info["platform_version"]}"',
            r'"deviceName":\s*"[^"]*"': f'"deviceName": "{device_info["device_name"]}"',
            r'"udid":\s*"[^"]*"': f'"udid": "{udid}"',
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        # Write updated config
        with open(config_path, 'w') as f:
            f.write(content)
        
        print(f"\n✓ Updated config.py with device information!")
        return True
        
    except Exception as e:
        print(f"Error updating config.py: {e}")
        return False

def main():
    """Main function"""
    print("="*60)
    print("Android Device Auto-Detection")
    print("="*60)
    
    # Check if ADB is available
    adb_version = run_adb_command("adb version")
    if not adb_version:
        print("\n✗ ADB not found!")
        print("Please install Android SDK Platform Tools:")
        print("  Mac: brew install android-platform-tools")
        print("  Linux: sudo apt-get install android-tools-adb")
        print("  Windows: Download from https://developer.android.com/studio/releases/platform-tools")
        return 1
    
    print(f"\n✓ ADB found: {adb_version.split()[0] if adb_version else 'Unknown'}")
    
    # Get connected devices
    print("\nChecking for connected devices...")
    devices = get_connected_devices()
    
    if not devices:
        print("\n✗ No devices found!")
        print("\nPlease:")
        print("1. Connect your Android phone via USB")
        print("2. Enable USB Debugging in Developer Options")
        print("3. Accept USB debugging prompt on phone")
        print("4. Run: adb devices")
        return 1
    
    print(f"\n✓ Found {len(devices)} device(s):")
    
    # If multiple devices, let user choose
    if len(devices) > 1:
        print("\nMultiple devices detected:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device['udid']} ({device['status']})")
        
        choice = input("\nSelect device number (1-{}): ".format(len(devices)))
        try:
            selected_device = devices[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice, using first device")
            selected_device = devices[0]
    else:
        selected_device = devices[0]
    
    udid = selected_device['udid']
    print(f"\nUsing device: {udid}")
    
    # Get device information
    print("\nGetting device information...")
    device_info = get_device_info(udid)
    
    print("\nDevice Information:")
    print(f"  UDID: {udid}")
    print(f"  Device Name: {device_info['device_name']}")
    print(f"  Manufacturer: {device_info['manufacturer']}")
    print(f"  Android Version: {device_info['platform_version']}")
    print(f"  SDK Version: {device_info['sdk_version']}")
    
    # Check if app is installed
    print("\nChecking if app is installed...")
    app_package = "com.janogroupllc.pdfphotos"
    app_check = run_adb_command(f"adb -s {udid} shell pm list packages {app_package}")
    if app_check and app_package in app_check:
        print(f"✓ App '{app_package}' is installed")
    else:
        print(f"✗ App '{app_package}' not found")
        print("Please install 'AI Insect Bug Identifier' from Play Store")
    
    # Update config file
    print("\n" + "="*60)
    update_choice = input("Update config.py with this device information? (y/n): ").lower()
    
    if update_choice == 'y':
        if update_config_file(device_info, udid):
            print("\n✓ Configuration updated successfully!")
            print("\nNext steps:")
            print("1. Start Appium server: appium")
            print("2. Run tests: python main.py")
        else:
            print("\n✗ Failed to update config.py")
            print("Please manually update config.py with the information above")
    else:
        print("\nPlease manually update config.py with:")
        print(f'  "platformVersion": "{device_info["platform_version"]}"')
        print(f'  "deviceName": "{device_info["device_name"]}"')
        print(f'  "udid": "{udid}"')
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




