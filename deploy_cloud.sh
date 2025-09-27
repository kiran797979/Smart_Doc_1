#!/bin/bash
# Cloud deployment script for Smart Doc Checker

echo "🌐 Smart Doc Checker - Cloud Deployment Helper"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}This script will help you deploy to Render and Vercel${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "CLOUD_DEPLOYMENT_GUIDE.md" ]; then
    echo -e "${RED}❌ Please run this script from the Smart_Doc-master directory${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Prerequisites Check:${NC}"
echo "1. ✓ GitHub repository with code"
echo "2. ⚠️  Render account (create at render.com)"
echo "3. ⚠️  Vercel account (create at vercel.com)"
echo ""

read -p "Do you have both Render and Vercel accounts? (y/n): " accounts
if [ "$accounts" != "y" ]; then
    echo -e "${YELLOW}Please create accounts first, then run this script again${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Preparation Complete${NC}"
echo ""

echo -e "${BLUE}🚀 Deployment Steps:${NC}"
echo ""

echo -e "${YELLOW}STEP 1: Backend Deployment to Render${NC}"
echo "1. Go to https://render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Use these settings:"
echo "   - Name: smart-doc-checker-api"
echo "   - Environment: Docker"
echo "   - Root Directory: backend"
echo "   - Branch: main"
echo "5. Click 'Create Web Service'"
echo "6. Wait for deployment (5-10 minutes)"
echo ""

read -p "Press Enter when Render deployment is complete..."

echo -e "${YELLOW}What is your Render app URL? (e.g., https://smart-doc-checker-api.onrender.com):${NC}"
read render_url

if [ -z "$render_url" ]; then
    echo -e "${RED}❌ Render URL is required${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Render URL saved: $render_url${NC}"

# Update frontend environment
echo -e "${BLUE}🔧 Configuring frontend for production...${NC}"
cd frontend

# Create .env.local with production API URL
echo "VITE_API_URL=$render_url" > .env.local
echo -e "${GREEN}✅ Frontend configured with API URL${NC}"

echo ""
echo -e "${YELLOW}STEP 2: Frontend Deployment to Vercel${NC}"
echo ""

# Check if Vercel CLI is installed
if command -v vercel &> /dev/null; then
    echo -e "${GREEN}✅ Vercel CLI found${NC}"
    
    echo -e "${BLUE}Deploying to Vercel...${NC}"
    
    # Login to Vercel (if not already logged in)
    echo "Please make sure you're logged into Vercel CLI..."
    vercel whoami || vercel login
    
    # Deploy
    echo -e "${BLUE}Starting Vercel deployment...${NC}"
    vercel --prod
    
else
    echo -e "${YELLOW}⚠️  Vercel CLI not found${NC}"
    echo ""
    echo "Option 1: Install Vercel CLI and deploy"
    echo "  npm install -g vercel"
    echo "  vercel login"
    echo "  vercel --prod"
    echo ""
    echo "Option 2: Deploy via Vercel Dashboard"
    echo "1. Go to https://vercel.com"
    echo "2. Click 'New Project'"
    echo "3. Import your GitHub repository"
    echo "4. Set Root Directory to: frontend"
    echo "5. Add environment variable:"
    echo "   - VITE_API_URL = $render_url"
    echo "6. Click Deploy"
fi

cd ..

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}Your Smart Doc Checker is now live:${NC}"
echo -e "📱 Frontend: Check your Vercel dashboard for the URL"
echo -e "🔧 Backend:  $render_url"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the application by uploading a document"
echo "2. Share the frontend URL with users"
echo "3. Monitor both services in their respective dashboards"
echo ""
echo -e "${BLUE}For detailed troubleshooting, see CLOUD_DEPLOYMENT_GUIDE.md${NC}"