#!/bin/bash
# Quick script to start screen mirroring

echo "=== Screen Mirroring Options ==="
echo ""
echo "1. scrcpy (Free, Open Source)"
echo "2. Vysor (Easy, Browser-based)"
echo ""

# Check if scrcpy is installed
if command -v scrcpy &> /dev/null; then
    echo "✓ scrcpy is installed"
    echo ""
    echo "Starting scrcpy..."
    scrcpy -s 47921b4c
else
    echo "scrcpy not installed."
    echo ""
    echo "To install scrcpy (free):"
    echo "  brew install scrcpy"
    echo ""
    echo "Or use Vysor (easiest):"
    echo "  Visit: https://www.vysor.io/"
    echo "  Click 'Try Vysor in your browser'"
    echo ""
    read -p "Install scrcpy now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install scrcpy
        echo "Starting scrcpy..."
        scrcpy -s 47921b4c
    fi
fi




