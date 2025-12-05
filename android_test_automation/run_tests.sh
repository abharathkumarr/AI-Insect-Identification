#!/bin/bash
# Complete test runner with proper environment setup

cd "$(dirname "$0")"

echo "=========================================="
echo "Setting up Android Test Environment"
echo "=========================================="

# Set Android SDK environment
export ANDROID_HOME="/opt/homebrew/Caskroom/android-platform-tools/36.0.0"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$PATH:$ANDROID_HOME/platform-tools"

# Set Node.js version
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 22 > /dev/null 2>&1

echo "✓ ANDROID_HOME: $ANDROID_HOME"
echo "✓ Node.js: $(node --version)"
echo ""

# Check if Appium is running
if ! curl -s http://127.0.0.1:4723/status > /dev/null 2>&1; then
    echo "Starting Appium server..."
    # Start Appium with environment variables
    ANDROID_HOME="$ANDROID_HOME" ANDROID_SDK_ROOT="$ANDROID_SDK_ROOT" appium > /tmp/appium.log 2>&1 &
    APPIUM_PID=$!
    echo "Appium starting (PID: $APPIUM_PID)..."
    sleep 8
    
    # Verify Appium started
    if curl -s http://127.0.0.1:4723/status > /dev/null 2>&1; then
        echo "✓ Appium is running"
    else
        echo "✗ Appium failed to start. Check /tmp/appium.log"
        exit 1
    fi
else
    echo "✓ Appium is already running"
fi

echo ""
echo "=========================================="
echo "Running Tests"
echo "=========================================="
echo ""

# Export environment for Python
export ANDROID_HOME
export ANDROID_SDK_ROOT

# Run tests
python3 main.py "$@"




