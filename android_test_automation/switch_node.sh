#!/bin/bash
# Script to switch to compatible Node.js version for Appium

echo "Switching to Node.js 22 (compatible with Appium)..."

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Check if Node 22 is installed
if ! nvm list | grep -q "v22"; then
    echo "Installing Node.js 22..."
    nvm install 22
fi

# Switch to Node 22
nvm use 22

# Verify version
echo ""
echo "Current Node version: $(node --version)"
echo "Current npm version: $(npm --version)"
echo ""
echo "✓ Node.js version is now compatible with Appium!"
echo ""
echo "You can now run: appium"




