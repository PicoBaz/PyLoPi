#!/bin/bash

echo "===================================="
echo "     PyLoPi - Log Analyzer"
echo "===================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f "venv/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

echo ""
echo "Starting PyLoPi..."
echo "Access the dashboard at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py