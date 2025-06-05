#!/bin/bash

# Claude Cost Analyzer Setup Script

echo "Setting up Claude Cost Analyzer..."

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Please install Python 3 and pip first."
    exit 1
fi

# Install requirements
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  Text analysis:        python3 claude_cost_analyzer.py"
echo "  Visual analysis:      python3 claude_cost_visualizer.py"
echo "  Save charts:          python3 claude_cost_visualizer.py --save-dir ./charts"
echo ""
echo "For help:"
echo "  python3 claude_cost_analyzer.py --help"
echo "  python3 claude_cost_visualizer.py --help"