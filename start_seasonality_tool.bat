@echo off
echo ========================================
echo    Seasonality Trading Tool Starter
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.12+ and try again.
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version

REM Install requirements if needed
echo.
echo [2/4] Installing/updating requirements...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install requirements!
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Starting Seasonality Trading Tool...
echo Application will be available at: http://localhost:8501
echo.
echo The browser will open automatically in 5 seconds...
echo Press Ctrl+C to stop the application when done.
echo.

REM Start Streamlit without auto-opening browser to prevent duplicates
python -m streamlit run app/main.py --server.headless=false --server.port=8501 --browser.gatherUsageStats=false

REM Open browser manually after a short delay
timeout /t 3 /nobreak >nul
start "" "http://localhost:8501"

echo.
echo Application has been stopped.
pause