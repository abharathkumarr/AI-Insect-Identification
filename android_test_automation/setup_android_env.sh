#!/bin/bash
# Setup Android environment variables for Appium

# Find Android SDK location
if [ -d "$HOME/Library/Android/sdk" ]; then
    ANDROID_SDK="$HOME/Library/Android/sdk"
elif [ -d "$HOME/Android/Sdk" ]; then
    ANDROID_SDK="$HOME/Android/Sdk"
else
    # For Homebrew installation, we can use a minimal setup
    ADB_PATH=$(which adb)
    if [ -n "$ADB_PATH" ]; then
        # Extract SDK path from adb location
        ANDROID_SDK=$(dirname $(dirname "$ADB_PATH"))
        echo "Using ADB location: $ANDROID_SDK"
    else
        echo "Error: Could not find Android SDK"
        echo "Please install Android Studio or set ANDROID_HOME manually"
        exit 1
    fi
fi

# Set environment variables
export ANDROID_HOME="$ANDROID_SDK"
export ANDROID_SDK_ROOT="$ANDROID_SDK"
export PATH="$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools"

echo "✓ ANDROID_HOME set to: $ANDROID_HOME"
echo "✓ ANDROID_SDK_ROOT set to: $ANDROID_SDK_ROOT"
echo ""
echo "To make this permanent, add to ~/.zshrc:"
echo "  export ANDROID_HOME=\"$ANDROID_HOME\""
echo "  export ANDROID_SDK_ROOT=\"$ANDROID_SDK_ROOT\""
echo "  export PATH=\"\$PATH:\$ANDROID_HOME/platform-tools:\$ANDROID_HOME/tools\""




