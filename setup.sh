#!/bin/bash

# PLC SCADA Lab Setup Script for CPython
echo "🏭 Setting up PLC SCADA Lab with CPython..."

# Check if we're using CPython
python3 -c "import sys; print(f'Python: {sys.executable}'); print(f'Version: {sys.version}')"

# Check for required system dependencies
echo "📋 Checking system dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3 first:"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    echo "   macOS: brew install python"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "🌐 The application will be available at: http://localhost:8000"