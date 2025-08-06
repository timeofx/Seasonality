@echo off
title Network Diagnosis for Seasonality Tool

echo.
echo ================================================================
echo    🔍 NETWORK DIAGNOSIS FOR SEASONALITY TOOL
echo ================================================================
echo.

echo 📊 Current Network Configuration:
echo ----------------------------------------------------------------
ipconfig | findstr "IPv4"
echo.

echo 📊 Active Network Connections on Port 8501:
echo ----------------------------------------------------------------
netstat -an | findstr ":8501"
echo.

echo 📊 Windows Firewall Rules for Port 8501:
echo ----------------------------------------------------------------
netsh advfirewall firewall show rule name=all | findstr -i "8501"
netsh advfirewall firewall show rule name="Streamlit"
echo.

echo 📊 Testing Connectivity:
echo ----------------------------------------------------------------
echo Testing localhost...
ping -n 2 localhost
echo.

echo Testing your local IP...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4" ^| findstr "192.168"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo Testing %%b...
        ping -n 2 %%b
    )
)
echo.

echo 📊 Current Processes using Python:
echo ----------------------------------------------------------------
tasklist | findstr python
echo.

echo 📊 Current Processes using Streamlit:
echo ----------------------------------------------------------------
tasklist | findstr streamlit
echo.

echo ================================================================
echo    🔧 TROUBLESHOOTING STEPS:
echo ================================================================
echo 1. Make sure Windows Firewall allows port 8501
echo 2. Check if your router has port forwarding enabled
echo 3. Verify your device is on the same network
echo 4. Try accessing from another device: http://[YOUR_IP]:8501
echo 5. Check if antivirus is blocking the connection
echo ================================================================
echo.
pause