#!/bin/bash
# Smart Doc Checker - Production Deployment Script
# This script deploys the application for production use

echo "=========================================="
echo "  Smart Doc Checker - Production Deploy   "
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run from project root."
    exit 1
fi

print_status "Starting Smart Doc Checker deployment..."

# Option 1: Docker Deployment (if Docker is available)
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    print_status "Docker found. Deploying with Docker Compose..."
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down
    
    # Build and start services
    print_status "Building and starting services..."
    docker-compose up --build -d
    
    # Check if services are running
    sleep 10
    if docker-compose ps | grep -q "Up"; then
        print_status "✅ Docker deployment successful!"
        echo ""
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔗 Backend API: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo "🔍 DB Browser: http://localhost:8080 (dev profile)"
        echo ""
        echo "To stop: docker-compose down"
        echo "To view logs: docker-compose logs -f"
    else
        print_error "Docker deployment failed. Check logs with: docker-compose logs"
        exit 1
    fi
else
    # Option 2: Manual deployment
    print_warning "Docker not found. Using manual deployment..."
    
    # Create production directories
    mkdir -p production/{backend,frontend,nginx}
    
    # Backend setup
    print_status "Setting up backend..."
    cd backend
    
    # Install dependencies
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        python -m venv venv
        source venv/bin/activate
    fi
    
    pip install -r requirements.txt
    pip install gunicorn
    
    # Create production config
    cat > production_config.py << 'EOF'
import os
from pathlib import Path

# Production configuration
DEBUG = False
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 4
UPLOAD_DIR = Path("uploads")
DATABASE_PATH = "database/smart_doc_checker.db"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
Path("database").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
EOF
    
    cd ..
    
    # Frontend setup
    print_status "Building frontend for production..."
    cd frontend
    
    # Build production version
    npm run build
    
    cd ..
    
    print_status "✅ Manual deployment setup complete!"
    echo ""
    echo "To start the application:"
    echo "1. Backend: cd backend && source venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:8000 api.api_server:app"
    echo "2. Frontend: cd frontend && npx serve -s build -l 3000"
    echo ""
fi

print_status "Deployment completed successfully! 🎉"