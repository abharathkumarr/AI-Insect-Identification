#!/bin/bash
# Complete test setup and execution script

echo "=========================================="
echo "Android Test Automation - Setup Check"
echo "=========================================="
echo ""

# Check device connection
echo "1. Checking device connection..."
if adb devices | grep -q "device$"; then
    DEVICE=$(adb devices | grep "device$" | head -1 | awk '{print $1}')
    echo "   ✓ Device connected: $DEVICE"
else
    echo "   ✗ No device connected!"
    echo "   Please connect your phone via USB and enable USB Debugging"
    exit 1
fi

# Check Node version
echo ""
echo "2. Checking Node.js version..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 20 ] || ([ "$NODE_VERSION" -ge 23 ] && [ "$NODE_VERSION" -lt 24 ]); then
    echo "   ⚠ Node.js version incompatible with Appium"
    echo "   Switching to Node.js 22..."
    nvm install 22 2>/dev/null
    nvm use 22
    echo "   ✓ Using Node.js $(node --version)"
else
    echo "   ✓ Node.js version OK: $(node --version)"
fi

# Check if Appium is running
echo ""
echo "3. Checking Appium server..."
if curl -s http://127.0.0.1:4723/status > /dev/null 2>&1; then
    echo "   ✓ Appium is running"
    APPIUM_RUNNING=true
else
    echo "   ⚠ Appium is not running"
    APPIUM_RUNNING=false
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo "✓ Device: Connected"
echo "✓ Node.js: $(node --version)"
if [ "$APPIUM_RUNNING" = true ]; then
    echo "✓ Appium: Running"
    echo ""
    echo "Ready to run tests!"
    echo ""
    echo "Run tests with:"
    echo "  python main.py"
    echo ""
    echo "Or test single image:"
    echo "  python main.py --test-id TC001"
else
    echo "✗ Appium: Not running"
    echo ""
    echo "Next steps:"
    echo "1. Open a NEW terminal window"
    echo "2. Run: appium"
    echo "3. Come back here and run: python main.py"
fi

echo ""
echo "=========================================="




