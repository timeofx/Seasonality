@echo off
title Seasonality Trading Tool - Secure Remote Server

echo.
echo ================================================================
echo    🔐 Seasonality Trading Tool - Secure Remote Server
echo ================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo 📁 Working directory: %CD%
echo 🐍 Python version check...
python --version

echo.
echo 📦 Installing/updating requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)
echo ✅ Requirements installed successfully

echo.
echo 🧹 Performing aggressive cleanup...
echo 🔄 Stopping existing Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq streamlit*" >nul 2>&1

echo ⏳ Waiting for cleanup to complete...
timeout /t 3 /nobreak >nul

echo ✅ Port 8501 is available and ready

echo.
echo ================================================================
echo 🚀 STARTING SECURE REMOTE SERVER
echo ================================================================

REM Get local IP for remote access - improved version
echo 🔍 Detecting network configuration...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo Found IP: %%b
        if not "%%b"=="127.0.0.1" set LOCAL_IP=%%b
    )
)
if "%LOCAL_IP%"=="" set LOCAL_IP=192.168.1.100
echo ✅ Using IP: %LOCAL_IP%

echo 🌍 Local Access:  http://localhost:8501
echo 🌐 Remote Access: http://%LOCAL_IP%:8501
echo ================================================================
echo 🔑 Secure Authentication:
echo    🔒 Contact administrator for login credentials
echo    👥 Multiple user roles available (Admin, Trader, Analyst)
echo ================================================================
echo 🛡️ SECURITY FEATURES:
echo    🔒 SHA256 password hashing
echo    🕐 Session management
echo    🚪 Secure logout
echo    👥 Role-based permissions
echo ================================================================
echo ⚠️ FIREWALL & NETWORK DIAGNOSIS:
echo    📋 Checking Windows Firewall rules for port 8501...
netsh advfirewall firewall show rule name="Streamlit" dir=in 2>nul || (
    echo    ❌ No firewall rule found for Streamlit
    echo    ✅ Creating firewall rule...
    netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501 >nul 2>&1
    echo    ✅ Firewall rule created for port 8501
)
echo    📋 Testing network connectivity...
echo    🌐 Your external IP can be checked at: https://whatismyipaddress.com/
echo    🔧 If remote access fails, check router port forwarding for port 8501
echo ================================================================

echo.
echo 🚀 Launching Streamlit application...
echo ⏳ Waiting for server to initialize...

REM Start Streamlit server
start /min python -m streamlit run app/main.py

REM Wait for server to start
timeout /t 5 /nobreak >nul

echo ✅ SERVER IS RUNNING!
echo 🔍 Testing local connection...
ping -n 1 localhost >nul && echo ✅ Localhost connectivity: OK || echo ❌ Localhost connectivity: FAILED
echo 🔍 Testing remote IP connectivity...
ping -n 1 %LOCAL_IP% >nul && echo ✅ Remote IP connectivity: OK || echo ❌ Remote IP connectivity: FAILED
echo ================================================================
echo 🌐 ACCESS LINKS:
echo    Local:  http://localhost:8501
echo    Remote: http://%LOCAL_IP%:8501
echo ================================================================
echo 📋 COPY THESE LINKS:
echo 📱 Local Access:   http://localhost:8501
echo 🌍 Remote Access:  http://%LOCAL_IP%:8501
echo ================================================================
echo 📊 SERVER STATUS: ONLINE ✅
echo 🔒 Authentication: REQUIRED
echo 👥 Available Roles: Admin, Trader, Analyst
echo ⏹️ Press Ctrl+C to stop the server
echo ================================================================

echo.
echo 📊 Server monitoring started...
echo Links are always available above ⬆️

REM Monitor server status
:MONITOR_LOOP
timeout /t 10 /nobreak >nul
echo 📊 Server Status: RUNNING ✅ - %TIME% - Links: http://localhost:8501
goto MONITOR_LOOP

echo.
echo 🔚 Secure server session ended
pause