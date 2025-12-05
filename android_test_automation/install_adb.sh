#!/bin/bash
# Quick ADB Installation Script for macOS

echo "=========================================="
echo "Installing Android Platform Tools (ADB)"
echo "=========================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Android Platform Tools
echo "Installing Android Platform Tools..."
brew install android-platform-tools

# Verify installation
echo ""
echo "Verifying installation..."
if command -v adb &> /dev/null; then
    echo "✓ ADB installed successfully!"
    adb version
    echo ""
    echo "Next steps:"
    echo "1. Connect your Android phone via USB"
    echo "2. Enable USB Debugging on your phone"
    echo "3. Run: adb devices"
    echo "4. Run: python auto_detect_device.py"
else
    echo "✗ Installation failed. Please install manually."
    echo "See INSTALL_ADB.md for manual installation instructions."
fi




