#!/bin/bash

echo "========================================"
echo "AI 3D Model Generator"
echo "One-Click Setup and Run"
echo "========================================"
echo ""

# Detect if running in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "[1/6] Already in virtual environment: $VIRTUAL_ENV"
else
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "[1/5] Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to create virtual environment"
            exit 1
        fi
        echo "Virtual environment created successfully"
    else
        echo "[1/5] Virtual environment already exists"
    fi
    
    # Activate virtual environment
    echo "[2/5] Activating virtual environment..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to activate virtual environment"
        exit 1
    fi
fi

# Upgrade pip
echo "[2/5] Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "[WARN] .env file created from .env.example"
    echo "[INFO] Please edit .env and add your API keys if needed"
    echo "[INFO] Local LLM is enabled by default - no API keys required!"
    echo ""
fi

# Download models if enabled
echo "[4/5] Checking if auto-download is enabled..."
if grep -q "AUTO_DOWNLOAD_MODELS=true" .env 2>/dev/null; then
    echo ""
    echo "Auto-download enabled - models will be downloaded on first run"
else
    echo "Auto-download disabled"
fi

# Create required directories
mkdir -p output
mkdir -p models/3d
mkdir -p models/llm
mkdir -p models/image
mkdir -p logs

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Starting AI 3D Model Generator..."
echo "Choose your preferred mode:"
echo ""
echo "1. Desktop GUI (PyQt6) - Recommended"
echo "2. Web Interface (Browser-based)"
echo "3. API Server Only (For developers)"
echo ""

# Default to GUI if no argument
MODE="gui"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --gui|-g)
            MODE="gui"
            shift
            ;;
        --web|-w)
            MODE="web"
            shift
            ;;
        --api|-a)
            MODE="api"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--gui|--web|--api]"
            exit 1
            ;;
    esac
done

# Prompt for mode if not specified via command line
if [[ "$MODE" == "gui" && $# -eq 0 ]]; then
    echo -n "Select mode [1-3] (default: 1): "
    read -r choice
    case "$choice" in
        2)
            MODE="web"
            ;;
        3)
            MODE="api"
            ;;
        *)
            MODE="gui"
            ;;
    esac
fi

case "$MODE" in
    web)
        echo "Starting Web Interface..."
        echo "Opening browser at http://localhost:5000/"
        
        # Try to open browser automatically
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open http://localhost:5000/ &
        elif command -v open >/dev/null 2>&1; then
            open http://localhost:5000/ &
        elif command -v start >/dev/null 2>&1; then
            start http://localhost:5000/ &
        else
            echo "Please open http://localhost:5000/ in your browser"
        fi
        
        python main.py --mode web
        ;;
    
    api)
        echo "Starting API Server..."
        python main.py --mode api
        ;;
    
    *)
        echo "Starting Desktop GUI (default)..."
        python main.py --mode gui
        ;;
esac

echo ""
echo "========================================"
echo "Application stopped."
echo "========================================"
