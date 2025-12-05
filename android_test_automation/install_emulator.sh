#!/bin/bash
# Quick script to install Android Studio and set up emulator

echo "=========================================="
echo "Android Emulator Setup"
echo "=========================================="
echo ""

# Check if Android Studio is installed
if [ -d "/Applications/Android Studio.app" ]; then
    echo "✓ Android Studio is already installed!"
    echo ""
    echo "Next steps:"
    echo "1. Open Android Studio"
    echo "2. Go to: More Actions → Virtual Device Manager"
    echo "3. Click 'Create Device'"
    echo "4. Select Pixel 6, Android 12"
    echo "5. Click Play button to start emulator"
else
    echo "Android Studio is not installed."
    echo ""
    echo "Installing Android Studio via Homebrew..."
    echo ""
    
    # Check if Homebrew is available
    if command -v brew &> /dev/null; then
        read -p "Install Android Studio now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Installing Android Studio (this may take 10-15 minutes)..."
            brew install --cask android-studio
            
            echo ""
            echo "✓ Android Studio installed!"
            echo ""
            echo "Next steps:"
            echo "1. Open Android Studio from Applications"
            echo "2. Complete the setup wizard (Standard installation)"
            echo "3. Go to: More Actions → Virtual Device Manager"
            echo "4. Create a new virtual device (Pixel 6, Android 12)"
            echo "5. Start the emulator"
        else
            echo ""
            echo "You can install Android Studio manually:"
            echo "1. Visit: https://developer.android.com/studio"
            echo "2. Download for macOS"
            echo "3. Install the .dmg file"
        fi
    else
        echo "Homebrew not found. Please install Android Studio manually:"
        echo "1. Visit: https://developer.android.com/studio"
        echo "2. Download for macOS"
        echo "3. Install the .dmg file"
    fi
fi

echo ""
echo "=========================================="
echo "After Emulator is Running:"
echo "=========================================="
echo ""
echo "1. Verify connection:"
echo "   adb devices"
echo ""
echo "2. Install app on emulator:"
echo "   - Open Play Store in emulator"
echo "   - Search 'AI Insect Bug Identifier'"
echo "   - Install it"
echo ""
echo "3. Update config:"
echo "   cd android_test_automation"
echo "   python auto_detect_device.py"
echo ""
echo "4. Run tests:"
echo "   python main.py"
echo ""




