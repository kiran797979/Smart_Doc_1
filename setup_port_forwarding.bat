@echo off
REM Smart Doc Checker - Port Forwarding Setup Script
REM This script helps set up port forwarding for external access

echo 🌐 Smart Doc Checker - Port Forwarding Setup
echo ===========================================
echo.

echo Current application status:
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.

echo 📋 Port Forwarding Options:
echo.
echo 1. Windows Firewall Configuration
echo 2. Router Port Forwarding Guide  
echo 3. SSH Tunnel Setup
echo 4. ngrok Tunnel (Recommended for testing)
echo 5. Check current network configuration
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" goto :firewall
if "%choice%"=="2" goto :router
if "%choice%"=="3" goto :ssh
if "%choice%"=="4" goto :ngrok
if "%choice%"=="5" goto :network
echo Invalid choice. Exiting...
pause
exit /b 1

:firewall
echo.
echo 🔥 Windows Firewall Configuration
echo ================================
echo.
echo Adding firewall rules for Smart Doc Checker...

REM Add firewall rules for inbound connections
netsh advfirewall firewall add rule name="Smart Doc Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="Smart Doc Backend" dir=in action=allow protocol=TCP localport=8000

echo.
echo ✅ Firewall rules added successfully!
echo.
echo Your application should now be accessible from:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4"') do (
    set ip=%%a
    set ip=!ip: =!
    if not "!ip!"=="" (
        echo Frontend: http://!ip!:3000
        echo Backend:  http://!ip!:8000
    )
)
echo.
goto :end

:router
echo.
echo 🏠 Router Port Forwarding Guide
echo ==============================
echo.
echo To access your Smart Doc Checker from the internet:
echo.
echo 1. Find your router's admin interface:
echo    - Usually: http://192.168.1.1 or http://192.168.0.1
echo    - Login with admin credentials
echo.
echo 2. Navigate to Port Forwarding section:
echo    - Look for "Port Forwarding", "Virtual Server", or "NAT"
echo.
echo 3. Add these rules:
echo    Rule 1: Frontend Access
echo    - External Port: 3000
echo    - Internal Port: 3000  
echo    - Internal IP: [Your PC's local IP]
echo    - Protocol: TCP
echo.
echo    Rule 2: Backend API Access
echo    - External Port: 8000
echo    - Internal Port: 8000
echo    - Internal IP: [Your PC's local IP] 
echo    - Protocol: TCP
echo.
echo 4. Save settings and restart router if needed
echo.
echo 5. Access via your public IP:
echo    - Find public IP: https://whatismyipaddress.com
echo    - Frontend: http://[PUBLIC_IP]:3000
echo    - Backend: http://[PUBLIC_IP]:8000
echo.
goto :end

:ssh
echo.
echo 🔐 SSH Tunnel Setup
echo ==================
echo.
echo If you have SSH access to a server, you can create tunnels:
echo.
echo For Frontend (port 3000):
echo ssh -L 3000:localhost:3000 user@your-server.com
echo.
echo For Backend (port 8000):  
echo ssh -L 8000:localhost:8000 user@your-server.com
echo.
echo Then access via: http://your-server.com:3000
echo.
goto :end

:ngrok
echo.
echo 🚇 ngrok Tunnel Setup (Recommended)
echo ==================================
echo.
echo ngrok provides secure tunnels to your local server
echo.
echo 1. Download ngrok: https://ngrok.com/download
echo 2. Install and authenticate with ngrok
echo 3. Run these commands in separate terminals:
echo.
echo    Frontend tunnel:
echo    ngrok http 3000
echo.
echo    Backend tunnel:  
echo    ngrok http 8000
echo.
echo 4. ngrok will provide public URLs like:
echo    - https://abc123.ngrok.io (Frontend)
echo    - https://def456.ngrok.io (Backend)
echo.
echo 5. Update your frontend API URL to use the backend ngrok URL
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if %errorlevel%==0 (
    echo.
    echo ✅ ngrok is installed! 
    echo.
    set /p start_ngrok="Start ngrok tunnels now? (y/n): "
    if /i "!start_ngrok!"=="y" (
        echo.
        echo Starting ngrok tunnels...
        start "Frontend Tunnel" ngrok http 3000
        timeout /t 3 >nul
        start "Backend Tunnel" ngrok http 8000
        echo.
        echo ✅ Tunnels started! Check the ngrok windows for public URLs.
    )
) else (
    echo.
    echo ⚠️  ngrok not found. Please install from: https://ngrok.com/download
)
goto :end

:network
echo.
echo 🔍 Network Configuration Check
echo =============================
echo.
echo Your local IP addresses:
ipconfig | findstr /R /C:"IPv4 Address"
echo.
echo Current listening ports:
netstat -an | findstr ":3000\|:8000" | findstr LISTENING
echo.
echo Local access URLs:
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo LAN access URLs (use your IPv4 address):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4"') do (
    set ip=%%a
    set ip=!ip: =!
    if not "!ip!"=="" (
        echo Frontend: http://!ip!:3000
        echo Backend:  http://!ip!:8000
    )
)
echo.
goto :end

:end
echo.
echo 🎯 Quick Test:
echo =============
echo 1. Test local access: http://localhost:3000
echo 2. Test LAN access from another device on same network
echo 3. Test external access if port forwarding is configured
echo.
echo ⚠️  Security Note:
echo Make sure to secure your application before exposing it to the internet!
echo.
pause