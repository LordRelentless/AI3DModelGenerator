@echo off
chcp 65001 >nul
echo ========================================
echo AI 3D Model Generator
echo One-Click Setup and Run
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo [1/5] Virtual environment already exists
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo [WARN] .env file created from .env.example
    echo [INFO] Please edit .env and add your API keys if needed
    echo [INFO] Local LLM is enabled by default - no API keys required!
    echo.
)

REM Download models if enabled
echo [5/5] Checking if auto-download is enabled...
findstr /C:"AUTO_DOWNLOAD_MODELS=true" .env >nul
if errorlevel 1 (
    echo.
    echo Auto-download enabled - models will be downloaded on first run
) else (
    echo Auto-download disabled
)

REM Create required directories
if not exist "output\" mkdir output
if not exist "models\3d\" mkdir models\3d
if not exist "models\llm\" mkdir models\llm
if not exist "models\image\" mkdir models\image
if not exist "logs\" mkdir logs

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Starting AI 3D Model Generator...
echo Choose your preferred mode:
echo.
echo 1. Desktop GUI (PyQt6) - Recommended
echo 2. Web Interface (Browser-based)
echo 3. API Server Only (For developers)
echo.
set /p choice=Select mode (1-3): 
if "%choice%"=="1" goto gui
if "%choice%"=="2" goto web
if "%choice%"=="3" goto api
goto :default

:gui
echo Starting Desktop GUI...
python main.py --mode gui
goto :end

:web
echo Starting Web Interface...
echo Opening browser at http://localhost:5000/
start http://localhost:5000/
timeout /t 2 >nul
python main.py --mode web
goto :end

:api
echo Starting API Server...
python main.py --mode api
goto :end

:default
echo Starting Desktop GUI (default)...
python main.py --mode gui
goto :end

:end
echo.
echo Application stopped. Press any key to exit...
pause >nul
