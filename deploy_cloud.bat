@echo off
REM Cloud deployment script for Smart Doc Checker (Windows)

echo 🌐 Smart Doc Checker - Cloud Deployment Helper
echo ==============================================
echo.

echo This script will help you deploy to Render and Vercel
echo.

REM Check if we're in the right directory
if not exist "CLOUD_DEPLOYMENT_GUIDE.md" (
    echo ❌ Please run this script from the Smart_Doc-master directory
    pause
    exit /b 1
)

echo 📋 Prerequisites Check:
echo 1. ✓ GitHub repository with code
echo 2. ⚠️  Render account ^(create at render.com^)
echo 3. ⚠️  Vercel account ^(create at vercel.com^)
echo.

set /p accounts="Do you have both Render and Vercel accounts? (y/n): "
if /i "%accounts%" neq "y" (
    echo Please create accounts first, then run this script again
    pause
    exit /b 0
)

echo ✅ Preparation Complete
echo.

echo 🚀 Deployment Steps:
echo.

echo STEP 1: Backend Deployment to Render
echo 1. Go to https://render.com
echo 2. Click 'New +' → 'Web Service'
echo 3. Connect your GitHub repository
echo 4. Use these settings:
echo    - Name: smart-doc-checker-api
echo    - Environment: Docker
echo    - Root Directory: backend
echo    - Branch: main
echo 5. Click 'Create Web Service'
echo 6. Wait for deployment ^(5-10 minutes^)
echo.

pause

set /p render_url="What is your Render app URL? (e.g., https://smart-doc-checker-api.onrender.com): "

if "%render_url%"=="" (
    echo ❌ Render URL is required
    pause
    exit /b 1
)

echo ✅ Render URL saved: %render_url%

REM Update frontend environment
echo 🔧 Configuring frontend for production...
cd frontend

REM Create .env.local with production API URL
echo VITE_API_URL=%render_url%> .env.local
echo ✅ Frontend configured with API URL

echo.
echo STEP 2: Frontend Deployment to Vercel
echo.

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Vercel CLI found
    
    echo Deploying to Vercel...
    
    REM Login to Vercel ^(if not already logged in^)
    echo Please make sure you're logged into Vercel CLI...
    vercel whoami || vercel login
    
    REM Deploy
    echo Starting Vercel deployment...
    vercel --prod
    
) else (
    echo ⚠️  Vercel CLI not found
    echo.
    echo Option 1: Install Vercel CLI and deploy
    echo   npm install -g vercel
    echo   vercel login
    echo   vercel --prod
    echo.
    echo Option 2: Deploy via Vercel Dashboard
    echo 1. Go to https://vercel.com
    echo 2. Click 'New Project'
    echo 3. Import your GitHub repository
    echo 4. Set Root Directory to: frontend
    echo 5. Add environment variable:
    echo    - VITE_API_URL = %render_url%
    echo 6. Click Deploy
)

cd ..

echo.
echo 🎉 Deployment Complete!
echo.
echo Your Smart Doc Checker is now live:
echo 📱 Frontend: Check your Vercel dashboard for the URL
echo 🔧 Backend:  %render_url%
echo.
echo Next steps:
echo 1. Test the application by uploading a document
echo 2. Share the frontend URL with users
echo 3. Monitor both services in their respective dashboards
echo.
echo For detailed troubleshooting, see CLOUD_DEPLOYMENT_GUIDE.md

pause