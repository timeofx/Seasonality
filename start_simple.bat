@echo off
title Seasonality Tool - Simple Start

echo.
echo ================================================================
echo    🚀 SEASONALITY TOOL - SIMPLE START
echo ================================================================
echo.

cd /d "%~dp0"

echo 🔧 Stopping any existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo 📦 Installing requirements...
pip install -r requirements.txt >nul

echo 🔥 Adding firewall rule (requires admin)...
netsh advfirewall firewall delete rule name="Streamlit Port" >nul 2>&1
netsh advfirewall firewall add rule name="Streamlit Port" dir=in action=allow protocol=TCP localport=8501 >nul 2>&1

echo.
echo 🚀 Starting server...
echo.
echo ================================================================
echo 📱 LOCAL ACCESS (always works):
echo    http://localhost:8501
echo.
echo 🌐 REMOTE ACCESS (for other devices):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "192.168"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo    http://%%b:8501
    )
)
echo.
echo 🔑 Login required - contact admin for credentials
echo ================================================================
echo.

python -m streamlit run app/main.py

echo.
echo Server stopped.
pause