#!/bin/bash
# Build script for creating standalone executables
# Run this on each target platform (Windows, Mac, Linux)

set -e  # Exit on error

echo "=========================================="
echo "  AI Rescheduling Agent - Build Script"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    SPEC_FILE="build_linux.spec"
    OUTPUT_NAME="AI_Rescheduling_Agent"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    SPEC_FILE="build_mac.spec"
    OUTPUT_NAME="AI_Rescheduling_Agent.app"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
    SPEC_FILE="build_windows.spec"
    OUTPUT_NAME="AI_Rescheduling_Agent.exe"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "🖥️  Detected OS: $OS"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"
echo ""

# Install PyInstaller if not installed
echo "📦 Installing/upgrading PyInstaller..."
python3 -m pip install --upgrade pyinstaller --user --quiet
echo "✅ PyInstaller ready"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt --user --quiet
echo "✅ Dependencies installed"
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist
echo "✅ Cleaned"
echo ""

# Build the executable
echo "🔨 Building executable for $OS..."
echo "   Using spec file: $SPEC_FILE"
echo ""

# Use python -m PyInstaller instead of pyinstaller command
python3 -m PyInstaller --clean --noconfirm $SPEC_FILE

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ BUILD SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "📦 Output location: dist/$OUTPUT_NAME"
    echo ""
    
    # Show size
    if [ "$OS" == "mac" ]; then
        SIZE=$(du -sh "dist/$OUTPUT_NAME" | cut -f1)
    else
        SIZE=$(du -sh "dist/$OUTPUT_NAME" | cut -f1)
    fi
    echo "📊 Size: $SIZE"
    echo ""
    
    echo "🚀 To distribute:"
    echo "   1. Copy dist/$OUTPUT_NAME to target machines"
    echo "   2. Create config.env file with API credentials"
    echo "   3. Run the executable"
    echo ""
    echo "🔒 HIPAA Compliance Notes:"
    echo "   ✅ Runs localhost only (127.0.0.1)"
    echo "   ✅ No external network access"
    echo "   ✅ All data stays on local machine"
    echo "   ✅ No telemetry or analytics"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ BUILD FAILED"
    echo "=========================================="
    echo ""
    echo "Check the error messages above for details."
    exit 1
fi