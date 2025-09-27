#!/bin/bash
# Render.com build script for Smart Doc Checker Backend

echo "🚀 Starting Smart Doc Checker Backend Build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up backend environment
echo "⚙️ Setting up backend environment..."
cd backend

# Create necessary directories
mkdir -p uploads database logs

# Set proper permissions
chmod 755 uploads database logs

# Initialize database if it doesn't exist
if [ ! -f "database/smart_doc_checker.db" ]; then
    echo "🗄️ Initializing database..."
    python -c "
from database.db_manager import DatabaseManager
db = DatabaseManager()
db.initialize_database()
print('✅ Database initialized successfully')
"
fi

echo "✅ Build completed successfully!"
echo "🌐 Backend will be available at the provided Render URL"