@echo off
REM Smart Doc Checker - Windows Production Deployment Script
REM This script deploys the application for production use on Windows

echo ==========================================
echo   Smart Doc Checker - Production Deploy   
echo ==========================================

echo [INFO] Starting Smart Doc Checker deployment...

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found. Please run from project root.
    exit /b 1
)

REM Check for Docker
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Docker found. Checking for Docker Compose...
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        goto :docker_deploy
    )
)

:manual_deploy
echo [WARN] Docker not available. Using manual deployment...

REM Create production directories
if not exist "production" mkdir production
if not exist "production\backend" mkdir production\backend
if not exist "production\frontend" mkdir production\frontend

REM Backend setup
echo [INFO] Setting up backend for production...
cd backend

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install production dependencies
echo [INFO] Installing backend dependencies...
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

REM Create uploads and database directories
if not exist "uploads" mkdir uploads
if not exist "database" mkdir database
if not exist "logs" mkdir logs

cd ..

REM Frontend production build (already done)
echo [INFO] Frontend production build ready...

REM Create startup scripts
echo [INFO] Creating startup scripts...

REM Backend startup script
echo @echo off > start_backend_production.bat
echo echo Starting Smart Doc Checker Backend (Production)... >> start_backend_production.bat
echo cd backend >> start_backend_production.bat
echo call venv\Scripts\activate.bat >> start_backend_production.bat
echo uvicorn api.api_server:app --host 0.0.0.0 --port 8000 --workers 1 >> start_backend_production.bat

REM Frontend startup script  
echo @echo off > start_frontend_production.bat
echo echo Starting Smart Doc Checker Frontend (Production)... >> start_frontend_production.bat
echo cd frontend >> start_frontend_production.bat
echo npx serve -s build -l 3000 >> start_frontend_production.bat

REM Combined startup script
echo @echo off > start_production.bat
echo echo ========================================== >> start_production.bat
echo echo   Smart Doc Checker - Production Mode >> start_production.bat
echo echo ========================================== >> start_production.bat
echo echo. >> start_production.bat
echo echo Starting backend server... >> start_production.bat
echo start "Backend" cmd /k "start_backend_production.bat" >> start_production.bat
echo timeout /t 5 /nobreak ^>nul >> start_production.bat
echo echo Starting frontend server... >> start_production.bat
echo start "Frontend" cmd /k "start_frontend_production.bat" >> start_production.bat
echo echo. >> start_production.bat
echo echo ✅ Smart Doc Checker is starting... >> start_production.bat
echo echo. >> start_production.bat
echo echo 🌐 Frontend: http://localhost:3000 >> start_production.bat
echo echo 🔗 Backend API: http://localhost:8000 >> start_production.bat
echo echo 📚 API Docs: http://localhost:8000/docs >> start_production.bat
echo echo. >> start_production.bat

goto :success

:docker_deploy
echo [INFO] Deploying with Docker Compose...

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose down

REM Build and start services
echo [INFO] Building and starting services...
docker-compose up --build -d

REM Wait for services to start
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | find "Up" >nul
if %errorlevel% equ 0 (
    echo [INFO] ✅ Docker deployment successful!
    echo.
    echo 🌐 Frontend: http://localhost:3000
    echo 🔗 Backend API: http://localhost:8000
    echo 📚 API Docs: http://localhost:8000/docs
    echo 🔍 DB Browser: http://localhost:8080 (dev profile)
    echo.
    echo To stop: docker-compose down
    echo To view logs: docker-compose logs -f
) else (
    echo [ERROR] Docker deployment failed. Check logs with: docker-compose logs
    exit /b 1
)

goto :success

:success
echo.
echo [INFO] ✅ Deployment completed successfully! 🎉
echo.
if exist "start_production.bat" (
    echo To start the application, run: start_production.bat
)
pause