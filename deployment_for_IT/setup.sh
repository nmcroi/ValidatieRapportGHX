#!/bin/bash

# GHX Prijslijst Validatie Tool v2.0 - Setup Script
# ====================================================

echo "====================================="
echo "GHX Validatie Tool v2.0 Setup"
echo "====================================="

# Check Python version
echo "Checking Python installation..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure server paths
echo ""
echo "====================================="
echo "IMPORTANT: Configure Server Paths"
echo "====================================="
echo "1. Copy config/server_paths_template.json to config/server_paths.json"
echo "2. Update paths in server_paths.json for your server environment"
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p /tmp/validation_reports

# Set permissions
echo "Setting permissions..."
chmod +x app/cli_validate.py

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "To run the validator:"
echo "  python app/cli_validate.py <price_file> <default_template_file>"
echo ""
echo "For Lucy integration:"
echo "  Use the full path to cli_validate.py in Lucy configuration"
echo ""